"""CNOSP formula packing — uint32 without H, integer arithmetic, byte shuffle.

H is NOT stored. It is deterministically restored from CNOSP + block bounds.
"""

from __future__ import annotations

import struct
from typing import Final

# ── Integer mass scale ──────────────────────────────────────────────────────
MASS_SCALE: Final[int] = 100_000_000_000
BIN_WIDTH_U: Final[int] = 10_000_000_000

MASS_U: Final[dict[str, int]] = {
    "C": 1_200_000_000_000,
    "H":   100_782_503_223,
    "N": 1_400_307_400_443,
    "O": 1_599_491_461_957,
    "S": 3_197_207_117_440,
    "P": 3_097_376_199_842,
}

MASSES: Final[dict[str, float]] = {el: v / MASS_SCALE for el, v in MASS_U.items()}
ELEMENTS: Final[tuple[str, ...]] = ("C", "N", "O", "S", "P")
RECORD_SIZE: Final[int] = 4

_ELEMENT_BITS: Final = {
    "C": (0,  7, 0x7F), "N": (7,  7, 0x7F), "O": (14, 6, 0x3F),
    "S": (20, 5, 0x1F), "P": (25, 6, 0x3F),
}


def pack_c_n_o_s_p(c=0, n=0, o=0, s=0, p=0) -> int:
    """Pack C/N/O/S/P counts → uint32."""
    vals = {"C": c, "N": n, "O": o, "S": s, "P": p}
    result = 0
    for el, (shift, bits, mask) in _ELEMENT_BITS.items():
        val = vals[el]
        if val < 0: raise ValueError(f"Negative {el}: {val}")
        if val > mask: raise ValueError(f"{el}={val} exceeds {bits}-bit limit (max {mask})")
        result |= (val & mask) << shift
    return result


def unpack_c_n_o_s_p(code: int) -> tuple[int, int, int, int, int]:
    """Unpack uint32 → (C, N, O, S, P)."""
    return ((code >> 0) & 0x7F, (code >> 7) & 0x7F, (code >> 14) & 0x3F,
            (code >> 20) & 0x1F, (code >> 25) & 0x3F)


def pack_formula(counts: dict[str, int]) -> int:
    """Pack dict → uint32."""
    return pack_c_n_o_s_p(counts.get("C", 0), counts.get("N", 0),
                          counts.get("O", 0), counts.get("S", 0), counts.get("P", 0))


def unpack_formula(code: int) -> dict[str, int]:
    c, n, o, s, p = unpack_c_n_o_s_p(code)
    return {"C": c, "N": n, "O": o, "S": s, "P": p}


# ── Integer ceil_div ─────────────────────────────────────────────────────────

def ceil_div(a: int, b: int) -> int:
    """Integer ceil division. Works for negative a."""
    return -(a // -b) if b > 0 else -(a // -b)


# ── Deterministic H restoration ─────────────────────────────────────────────

def restore_h(c: int, n: int, o: int, s: int, p: int,
              block_low_u: int, block_high_u: int, max_mass_u: int,
              ) -> tuple[int, int] | None:
    """Recover H from CNOSP + block bounds. Returns (h, mass_u) or None."""
    base_u = (c * MASS_U["C"] + n * MASS_U["N"] + o * MASS_U["O"]
              + s * MASS_U["S"] + p * MASS_U["P"])
    parity = (n + p) & 1
    h_m = MASS_U["H"]
    parity_mass = parity * h_m
    k = max(0, ceil_div(block_low_u - base_u - parity_mass, 2 * h_m))
    h = parity + 2 * k
    mass_u = base_u + h * h_m

    if not (block_low_u <= mass_u < block_high_u): return None
    if mass_u > max_mass_u: return None
    dbe_num = 2 * c + 2 + n + p - h
    if dbe_num < 0 or dbe_num % 2 != 0: return None
    return h, mass_u


# ── Byte shuffle ─────────────────────────────────────────────────────────────

def byte_shuffle_uint32_le(data: bytes) -> bytes:
    """Transpose: [b0b1b2b3]*N → [all-b0][all-b1][all-b2][all-b3]."""
    if len(data) % 4: raise ValueError(f"len must be multiple of 4, got {len(data)}")
    n = len(data) // 4
    r = bytearray(len(data))
    for i in range(n):
        off = i * 4
        r[i], r[n + i], r[2 * n + i], r[3 * n + i] = data[off:off + 4]
    return bytes(r)


def byte_unshuffle_uint32_le(data: bytes) -> bytes:
    """Inverse of byte_shuffle_uint32_le."""
    if len(data) % 4: raise ValueError(f"len must be multiple of 4, got {len(data)}")
    n = len(data) // 4
    r = bytearray(len(data))
    for i in range(n):
        off = i * 4
        r[off:off + 4] = bytes([data[i], data[n + i], data[2 * n + i], data[3 * n + i]])
    return bytes(r)


# ── Block payload decoder ────────────────────────────────────────────────────

def decode_block(raw: bytes, block_low_u: int, block_high_u: int, max_mass_u: int,
                 elem_filter: dict[str, tuple[int, int]] | None = None,
                 ) -> list[dict]:
    """Unshuffle → unpack uint32 → restore H. Returns [{element: count, mass_u}, ...]."""
    if len(raw) % RECORD_SIZE: raise ValueError(f"Unaligned: {len(raw)}")
    n = len(raw) // RECORD_SIZE
    results = []
    for i in range(n):
        code = struct.unpack_from("<I", raw, i * RECORD_SIZE)[0]
        c, nv, o, sv, pv = unpack_c_n_o_s_p(code)
        if elem_filter:
            actual = {"C": c, "N": nv, "O": o, "S": sv, "P": pv}
            if any(actual.get(el, 0) < lo or actual.get(el, 0) > hi
                   for el, (lo, hi) in (elem_filter or {}).items()):
                continue
        r = restore_h(c, nv, o, sv, pv, block_low_u, block_high_u, max_mass_u)
        if r is None: continue
        h, mass_u = r
        results.append({"C": c, "N": nv, "O": o, "S": sv, "P": pv, "H": h, "mass_u": mass_u})
    return results


# ── String / DBE / mass helpers ──────────────────────────────────────────────

def formula_to_string(counts: dict[str, int]) -> str:
    parts = []
    for el in ["C", "H"]:
        n = counts.get(el, 0)
        if n > 0: parts.append(el if n == 1 else f"{el}{n}")
    for el in sorted(set(counts) - {"C", "H"}):
        n = counts.get(el, 0)
        if n > 0: parts.append(el if n == 1 else f"{el}{n}")
    return "".join(parts) if parts else ""


def calculate_exact_mass(counts: dict[str, int]) -> float:
    return sum(MASSES[el] * n for el, n in counts.items() if n > 0 and el in MASSES)


def dbe_from_counts(counts: dict[str, int]) -> float:
    return max(0.0, (2 * counts.get("C", 0) + 2 + counts.get("N", 0)
                     + counts.get("P", 0) - counts.get("H", 0)) / 2.0)


def is_valid_closed_shell(counts: dict[str, int]) -> bool:
    c = counts.get("C", 0)
    if c <= 0: return False
    num = 2 * c + 2 + counts.get("N", 0) + counts.get("P", 0) - counts.get("H", 0)
    return num >= 0 and num % 2 == 0
