"""Spectrum-package constants loaded from ``src/configs``."""

import logging
from dataclasses import dataclass
from src.configs import CHEM, FORMULA_SEARCH_CFG

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
DELTA_CD3 = CHEM.derivatization_shifts[
    "delta_cd3"
]  # Da: сдвиг m/z при замене COOH -> COOCD3
DELTA_CD3CO = CHEM.derivatization_shifts[
    "delta_cd3co"
]  # Da: сдвиг m/z при замене OH  -> OCOCD3

# ===========================================================================
# Загрузка спектров
# ===========================================================================

logger = logging.getLogger(__name__)
# Monoisotopic masses of the elements handled by the [M-H]- assignment
# (single source of truth: chemistry.json -> monoisotopic_masses).
ATOMIC_MASS = {el: CHEM.monoisotopic_masses[el] for el in CHEM.atomic_mass_elements}

#: Галогены: в DBE и правилах валентности ведут себя как одновалентный X.
HALOGENS: tuple[str, ...] = ("F", "Cl", "Br", "I")

#: Формальные валентности для правила чётности (Льюис).
#: S и P взяты в обычной для природного органического вещества форме
#: (S двухвалентна, P трёхвалентна) — это согласовано с профилем
#: сжатой базы формул `dbe_nonnegative_even_p3_s2`.
ELEMENT_VALENCES: dict[str, int] = {
    "C": 4,
    "H": 1,
    "N": 3,
    "O": 2,
    "S": 2,
    "P": 3,
    "F": 1,
    "Cl": 1,
    "Br": 1,
    "I": 1,
}

# Formula-search defaults
# (single source of truth: configs/constants/formula_search.json).
# JSON stores ranges as [min, max] lists; convert to tuples to preserve the
# exact original types expected downstream.
_FORMULA_SEARCH = FORMULA_SEARCH_CFG
_FS_ELEMENTS: tuple[str, ...] = tuple(_FORMULA_SEARCH["elements"])
_FS_RANGES: dict[str, tuple[int, int]] = {
    el: tuple(rng) for el, rng in _FORMULA_SEARCH["ranges"].items()
}


def _fs_get(key: str, default: float) -> float:
    """Значение из конфига формул с запасным вариантом (конфиг может быть старым)."""
    return float(_FORMULA_SEARCH[key]) if key in _FORMULA_SEARCH else float(default)


@dataclass(slots=True)
class FormulaSearchConfig:
    """Configuration for brute-force formula generation (CHNOSP + halogens).

    Defines which elements to enumerate, their per-element count ranges, and
    the chemical plausibility filters used to keep only NOM-like formulas.

    Attributes
    ----------
    elements : tuple of str
        Elements to enumerate, in output order.
        Default from ``formula_search.json``: ``("C", "H", "O", "N", "S",
        "P", "F", "Cl", "Br", "I")``.
    ranges : dict of {str: tuple of (int, int)}, optional
        Inclusive ``(min, max)`` count range per element. If ``None``, the
        configured defaults are filled in by ``__post_init__``.
    max_hc, max_oc, max_nc, max_sc, max_pc, max_xc : float
        Maximum allowed heteroatom/carbon ratios (H/C, O/C, N/C, S/C, P/C,
        halogen/C). Defaults from ``formula_search.json``.
    max_dbe : float
        Maximum allowed double-bond equivalent (DBE). Default 30.0.
    min_c : int
        Minimum number of carbon atoms. Default 1.

    Raises
    ------
    ValueError
        If any element in ``elements`` lacks a range in ``ranges``.
    """

    elements: tuple[str, ...] = _FS_ELEMENTS
    ranges: dict[str, tuple[int, int]] | None = None
    # Plausibility filters (defaults from constants/formula_search.json).
    max_hc: float = _FORMULA_SEARCH["max_hc"]  # H/C <= 3
    max_oc: float = _FORMULA_SEARCH["max_oc"]  # O/C <= 1.2
    max_nc: float = _FORMULA_SEARCH["max_nc"]  # N/C <= 1.0
    max_sc: float = _fs_get("max_sc", 0.5)  # S/C
    max_pc: float = _fs_get("max_pc", 0.5)  # P/C
    max_xc: float = _fs_get("max_xc", 0.5)  # (F+Cl+Br+I)/C
    max_dbe: float = _FORMULA_SEARCH["max_dbe"]  # DBE <= 30
    min_c: int = _FORMULA_SEARCH["min_c"]  # minimum carbons
    # Штрафы за экзотические гетероатомы (на атом) и бонус за изотопное
    # подтверждение M+2 — см. _penalty_note в formula_search.json.
    penalty_s: float = _fs_get("penalty_s", 1.0)
    penalty_p: float = _fs_get("penalty_p", 1.5)
    penalty_halogen: float = _fs_get("penalty_halogen", 1.5)
    bonus_isotope_m2: float = _fs_get("bonus_isotope_m2", 2.5)

    def __post_init__(self):
        if self.ranges is None:
            # Default per-element count ranges (constants/formula_search.json).
            self.ranges = dict(_FS_RANGES)
        else:
            # Частично заданные диапазоны дополняются значениями из конфига:
            # набор элементов расширен (S, P, F, Cl, Br, I), а вызывающий код
            # (GUI, CLI --element-ranges, сегментный режим) исторически
            # передаёт только C/H/O/N.
            self.ranges = dict(self.ranges)
            for el in self.elements:
                if el not in self.ranges:
                    self.ranges[el] = tuple(_FS_RANGES.get(el, (0, 0)))

    # ── удобные представления для векторизованных вычислений ────────────────
    @property
    def element_order(self) -> tuple[str, ...]:
        """Порядок элементов для массивов counts (по умолчанию — C, H, O, N, …)."""
        return self.elements

    def ratio_limits(self) -> dict[str, float]:
        """Предельные отношения элемент/C в виде ``{элемент: лимит}``."""
        return {
            "H": self.max_hc,
            "O": self.max_oc,
            "N": self.max_nc,
            "S": self.max_sc,
            "P": self.max_pc,
            "F": self.max_xc,
            "Cl": self.max_xc,
            "Br": self.max_xc,
            "I": self.max_xc,
        }
