"""Formula database — CNOSP uint32 + byte shuffle + Zstd.

Provides:
- FormulaDatabaseReader — runtime search with LRU block cache
- DatabaseManager — download/verify/update
- pack_c_n_o_s_p / unpack_c_n_o_s_p — uint32 encoding
- CLI: python -m src.core.formula_db build
"""

from ._packed import (
    MASSES,
    MASS_U,
    MASS_SCALE,
    BIN_WIDTH_U,
    pack_c_n_o_s_p,
    unpack_c_n_o_s_p,
    pack_formula,
    unpack_formula,
    ceil_div,
    restore_h,
    byte_shuffle_uint32_le,
    byte_unshuffle_uint32_le,
    formula_to_string,
    calculate_exact_mass,
    dbe_from_counts,
    is_valid_closed_shell,
)
from ._reader import FormulaDatabaseReader, SearchResult
from ._manager import DatabaseManager

__all__ = [
    "FormulaDatabaseReader",
    "DatabaseManager",
    "SearchResult",
    "pack_c_n_o_s_p",
    "unpack_c_n_o_s_p",
    "pack_formula",
    "unpack_formula",
    "calculate_exact_mass",
    "dbe_from_counts",
    "formula_to_string",
    "is_valid_closed_shell",
    "MASSES",
    "MASS_U",
    "MASS_SCALE",
]
