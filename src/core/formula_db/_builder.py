"""Offline formula database builder — CNOSP uint32 + byte shuffle + Zstd."""

from __future__ import annotations

import hashlib
import json
import logging
import os
import struct
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import zstandard as zstd

from ._packed import (
    MASS_U,
    MASSES,
    MASS_SCALE,
    BIN_WIDTH_U,
    RECORD_SIZE,
    pack_c_n_o_s_p,
    unpack_c_n_o_s_p,
    ceil_div,
    restore_h,
    byte_shuffle_uint32_le,
    formula_to_string,
    calculate_exact_mass,
    dbe_from_counts,
)

logger = logging.getLogger(__name__)

COMPRESSION_LEVEL: int = 9
FORMAT_VERSION: int = 2  # bumped: CNOSP uint32 + byte_shuffle
DB_VERSION: int = 1
PROFILE_VERSION: str = "dbe_nonnegative_even_p3_s2"


@dataclass(slots=True)
class BuildConfig:
    output: Path
    max_mass: float = 1000.0
    elements: tuple[str, ...] = ("C", "H", "N", "O", "S", "P")
    profile: str = PROFILE_VERSION
    bin_width: float = 0.1
    compression_level: int = COMPRESSION_LEVEL


def _progress_bar(current, total, width=40, label=""):
    pct = current / max(total, 1)
    filled = int(width * pct)
    bar = chr(0x2588) * filled + chr(0x2591) * (width - filled)
    label_str = f"{label}  " if label else ""
    sys.stderr.write(
        chr(13) + label_str + bar + f"  {pct*100:5.1f}%  {current:,}/{total:,}"
    )
    sys.stderr.flush()
    if current >= total:
        sys.stderr.write(chr(10))


def _enum_valid_cnosp(
    max_mass_u: int,
    progress_cb=None,
    est_total=82_091_308,
    update_interval=0.1,
) -> tuple[list[tuple[int, int, int, int, int, int, int]], int]:
    """Enumerate all valid (c,h,n,o,s,p,mass_u) with integer arithmetic."""
    result: list[tuple[int, int, int, int, int, int, int]] = []
    count = 0
    last_report = 0.0
    c_max = max_mass_u // MASS_U["C"]

    for c in range(1, c_max + 1):
        m_c = c * MASS_U["C"]
        if m_c > max_mass_u:
            break
        n_limit = min(127, (max_mass_u - m_c) // MASS_U["N"])
        for nv in range(n_limit + 1):
            m_cn = m_c + nv * MASS_U["N"]
            o_limit = min(63, (max_mass_u - m_cn) // MASS_U["O"])
            for o in range(o_limit + 1):
                m_cno = m_cn + o * MASS_U["O"]
                p_limit = min(63, (max_mass_u - m_cno) // MASS_U["P"])
                for pv in range(p_limit + 1):
                    m_cnop = m_cno + pv * MASS_U["P"]
                    s_limit = min(31, (max_mass_u - m_cnop) // MASS_U["S"])
                    for sv in range(s_limit + 1):
                        base_u = m_cnop + sv * MASS_U["S"]
                        if base_u > max_mass_u:
                            break
                        h_max_v = 2 * c + nv + pv + 2
                        h_max_m = (max_mass_u - base_u) // MASS_U["H"]
                        h_max = min(255, h_max_v, h_max_m)
                        parity = (nv + pv) & 1
                        for h in range(parity, h_max + 1, 2):
                            dbe_num = 2 * c + 2 + nv + pv - h
                            if dbe_num >= 0 and dbe_num % 2 == 0:
                                mass_u = base_u + h * MASS_U["H"]
                                if mass_u <= max_mass_u:
                                    result.append((c, h, nv, o, sv, pv, mass_u))
                                    count += 1
                                    if progress_cb:
                                        now = time.perf_counter()
                                        if now - last_report >= update_interval:
                                            progress_cb(count, est_total)
                                            last_report = now
    if progress_cb:
        progress_cb(count, count)
    result.sort(key=lambda x: x[6])
    return result, count


def build_database(config: BuildConfig) -> None:
    t0 = time.perf_counter()
    max_mass_u = int(config.max_mass * MASS_SCALE)

    # ── Step 1 ──
    ESTIMATED = 82_091_308
    logger.info(f"Phase 1/2: enumerating (~{ESTIMATED:,} estimated)...")

    def _cb(c, t):
        _progress_bar(c, t, label="Phase 1/2: enum")

    formulas, total = _enum_valid_cnosp(max_mass_u, _cb, ESTIMATED)
    logger.info(f"  {total:,} valid formulas in {time.perf_counter() - t0:.1f}s")

    # ── Step 2: bin by mass_u ──
    n_bins = max_mass_u // BIN_WIDTH_U + 1
    bins: list[list[int]] = [[] for _ in range(n_bins)]
    for c, h, nv, o, sv, pv, mass_u in formulas:
        bi = mass_u // BIN_WIDTH_U
        # Store CNOSP uint32 only (H + mass derived at runtime)
        code = pack_c_n_o_s_p(c, nv, o, sv, pv)
        bins[bi].append(code)

    # ── Step 3: Sort, shuffle, compress ──
    cctx = zstd.ZstdCompressor(level=config.compression_level)
    fdb_path = config.output.with_suffix(".fdb")
    manifest_path = config.output.with_suffix(".manifest.json")
    fdb_path.parent.mkdir(parents=True, exist_ok=True)

    block_list = []
    fdb_hasher = hashlib.sha256()
    non_empty = sum(1 for b in bins if b)
    written = 0
    total_f = 0

    with open(fdb_path, "wb") as f:
        for bi in range(n_bins):
            if not bins[bi]:
                continue
            written += 1
            _progress_bar(written, non_empty, label="Phase 2/2: pack")

            codes = sorted(bins[bi])
            raw = struct.pack(f"<{len(codes)}I", *codes)
            raw_size = len(raw)
            shuffled = byte_shuffle_uint32_le(raw)
            compressed = cctx.compress(shuffled)

            offset = f.tell()
            f.write(compressed)
            fdb_hasher.update(compressed)

            mass_low_u = bi * BIN_WIDTH_U
            mass_high_u = mass_low_u + BIN_WIDTH_U

            block_list.append(
                {
                    "bin_id": bi,
                    "mass_low_u": mass_low_u,
                    "mass_high_u": mass_high_u,
                    "file_offset": offset,
                    "compressed_size": len(compressed),
                    "raw_size": raw_size,
                    "formula_count": len(codes),
                    "compressed_sha256": hashlib.sha256(compressed).hexdigest(),
                }
            )
            total_f += len(codes)

    fdb_sha256 = fdb_hasher.hexdigest()

    # ── Step 4: Manifest ──
    manifest = {
        "format_version": FORMAT_VERSION,
        "database_version": str(DB_VERSION),
        "chemical_profile_version": config.profile,
        "profile_description": (
            "Closed-shell: DBE = (2*C+2+N+P-H)/2 >= 0, numerator even. "
            "P trivalent, S divalent."
        ),
        "atomic_mass_scale": MASS_SCALE,
        "atomic_masses_u": MASS_U,
        "max_mass_u": max_mass_u,
        "bin_width_u": BIN_WIDTH_U,
        "record_encoding": "uint32_c_n_o_s_p_h_derived_from_block",
        "record_endianness": "little",
        "record_size_before_transform": RECORD_SIZE,
        "sort_order": "uint32_ascending",
        "transform": "byte_shuffle_v1",
        "compression": {
            "algorithm": "zstd",
            "level": config.compression_level,
            "dictionary_file": None,
            "dictionary_sha256": None,
        },
        "database_file": fdb_path.name,
        "database_sha256": fdb_sha256,
        "formula_count": total_f,
        "blocks": block_list,
    }

    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest, mf, indent=2)

    elapsed = time.perf_counter() - t0
    fdb_size = fdb_path.stat().st_size
    logger.info(f"  {total_f:,} formulas in {len(block_list)} blocks")
    logger.info(f"  .fdb: {fdb_size / 1024**2:.1f} MB (SHA-256: {fdb_sha256[:16]}...)")
    logger.info(f"  Total: {elapsed:.1f}s")


def generate_formulas(max_mass: float, **kw) -> list:
    """Backward-compat wrapper: returns (c,h,n,o,s,p,mass) float tuples."""
    max_mass_u = int(max_mass * MASS_SCALE)
    raw, _ = _enum_valid_cnosp(max_mass_u)
    return [(c, h, n, o, s, p, mass_u / MASS_SCALE) for c, h, n, o, s, p, mass_u in raw]
