"""Runtime formula DB reader — CNOSP uint32 + byte shuffle + Zstd + LRU."""

from __future__ import annotations

import collections
import hashlib
import json
import logging
import struct
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import zstandard as zstd

from ._packed import (
    MASSES,
    MASS_U,
    MASS_SCALE,
    BIN_WIDTH_U,
    RECORD_SIZE,
    unpack_c_n_o_s_p,
    byte_unshuffle_uint32_le,
    restore_h,
    decode_block,
    formula_to_string,
    calculate_exact_mass,
    dbe_from_counts,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SearchResult:
    formula_str: str
    counts: dict[str, int]
    exact_mass: float
    error_ppm: float
    dbe: float


class LRUBlockCache:
    def __init__(self, max_blocks=8):
        self._max = max_blocks
        self._cache: collections.OrderedDict[tuple, list[dict]] = (
            collections.OrderedDict()
        )

    def get(self, key) -> Optional[list[dict]]:
        if key in self._cache:
            self._cache.move_to_end(key)
            return self._cache[key]
        return None

    def put(self, key, value):
        if key in self._cache:
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._max:
                self._cache.popitem(last=False)
        self._cache[key] = value

    def clear(self):
        self._cache.clear()


class FormulaDatabaseReader:
    def __init__(self, manifest_path: str | Path, cache_size=8, verify=True):
        self._mp = Path(manifest_path)
        name = self._mp.name
        fdb_name = (
            name[: -len(".manifest.json")] + ".fdb"
            if name.endswith(".manifest.json")
            else self._mp.stem + ".fdb"
        )
        self._fdb = self._mp.with_name(fdb_name)
        self._verify = verify
        self._cache = LRUBlockCache(cache_size)
        self._file = None

        with open(self._mp, encoding="utf-8") as mf:
            m = json.load(mf)
        self._manifest = m
        self._max_mass_u = m["max_mass_u"]
        self._blocks = {b["bin_id"]: b for b in m["blocks"]}

    @property
    def total_formulas(self):
        return self._manifest["formula_count"]

    @property
    def max_mass(self):
        return self._max_mass_u / MASS_SCALE

    def _open(self):
        if self._file is None:
            self._file = open(self._fdb, "rb")

    def _load_block(self, bin_id: int) -> list[dict]:
        bm = self._blocks[bin_id]
        self._open()
        self._file.seek(bm["file_offset"])
        compressed = self._file.read(bm["compressed_size"])

        if self._verify:
            actual = hashlib.sha256(compressed).hexdigest()
            if actual != bm["compressed_sha256"]:
                raise RuntimeError(f"Block {bin_id} SHA-256 mismatch")

        dctx = zstd.ZstdDecompressor()
        shuffled = dctx.decompress(compressed, max_output_size=bm["raw_size"])
        if len(shuffled) != bm["raw_size"]:
            raise RuntimeError(
                f"Block {bin_id}: expected {bm['raw_size']} raw, got {len(shuffled)}"
            )

        raw = byte_unshuffle_uint32_le(shuffled)
        return decode_block(raw, bm["mass_low_u"], bm["mass_high_u"], self._max_mass_u)

    def _bin_range(self, mass_u: int, ppm: float) -> range:
        delta_u = int(mass_u * ppm * 1e-6)
        lo = max(0, mass_u - delta_u)
        return range(lo // BIN_WIDTH_U, (mass_u + delta_u) // BIN_WIDTH_U + 1)

    def search(
        self,
        target_mass: float,
        ppm=1.0,
        element_filter: dict[str, tuple[int, int]] | None = None,
        max_results=100,
    ) -> list[SearchResult]:
        target_u = int(round(target_mass * MASS_SCALE))
        bin_range = self._bin_range(target_u, ppm)
        delta_u = int(target_u * ppm * 1e-6)
        results: list[SearchResult] = []
        seen = set()

        for bi in bin_range:
            if bi not in self._blocks:
                continue
            key = (self._manifest.get("database_version", ""), bi)
            formulas = self._cache.get(key)
            if formulas is None:
                formulas = self._load_block(bi)
                self._cache.put(key, formulas)

            for cts in formulas:
                fstr = formula_to_string(cts)
                if fstr in seen:
                    continue
                mass_u = cts["mass_u"]
                err = abs(mass_u - target_u)
                if err > delta_u:
                    continue
                err_ppm = (err / target_u) * 1e6

                if element_filter:
                    if any(
                        cts.get(el, 0) < lo or cts.get(el, 0) > hi
                        for el, (lo, hi) in element_filter.items()
                    ):
                        continue

                results.append(
                    SearchResult(
                        fstr,
                        dict(cts),
                        mass_u / MASS_SCALE,
                        err_ppm,
                        dbe_from_counts(cts),
                    )
                )
                seen.add(fstr)

        results.sort(key=lambda r: (abs(r.error_ppm), r.formula_str))
        return results[:max_results]

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
