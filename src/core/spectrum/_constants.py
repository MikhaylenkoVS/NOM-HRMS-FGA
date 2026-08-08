"""Auto-generated."""

import logging
import math
import numpy as np
from typing import Literal, Optional, Sequence
from dataclasses import dataclass
from src.configs import CHEM, PIPELINE
from src.configs.loader import ISOTOPE_CFG

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

# Formula-search defaults (single source of truth: pipeline.json -> formula_search).
# JSON stores ranges as [min, max] lists; convert to tuples to preserve the
# exact original types expected downstream.
_FORMULA_SEARCH = PIPELINE.formula_search
_FS_ELEMENTS: tuple[str, ...] = tuple(_FORMULA_SEARCH["elements"])
_FS_RANGES: dict[str, tuple[int, int]] = {
    el: tuple(rng) for el, rng in _FORMULA_SEARCH["ranges"].items()
}


@dataclass(slots=True)
class FormulaSearchConfig:
    """Configuration for brute-force CHON formula generation.

    Defines which elements to enumerate, their per-element count ranges, and
    the chemical plausibility filters used to keep only NOM-like formulas.

    Attributes
    ----------
    elements : tuple of str
        Elements to enumerate, in output order. Default ``("C", "H", "O", "N")``.
    ranges : dict of {str: tuple of (int, int)}, optional
        Inclusive ``(min, max)`` count range per element. If ``None``,
        NOM-oriented defaults are filled in by ``__post_init__``.
    max_hc : float
        Maximum allowed H/C atomic ratio. Default 3.0.
    max_oc : float
        Maximum allowed O/C atomic ratio. Default 1.2.
    max_nc : float
        Maximum allowed N/C atomic ratio. Default 1.0.
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
    # Plausibility filters (defaults from pipeline.json -> formula_search).
    max_hc: float = _FORMULA_SEARCH["max_hc"]  # H/C <= 3
    max_oc: float = _FORMULA_SEARCH["max_oc"]  # O/C <= 1.2
    max_nc: float = _FORMULA_SEARCH["max_nc"]  # N/C <= 1.0
    max_dbe: float = _FORMULA_SEARCH["max_dbe"]  # DBE <= 30
    min_c: int = _FORMULA_SEARCH["min_c"]  # minimum carbons

    def __post_init__(self):
        if self.ranges is None:
            # Default per-element count ranges (see pipeline.json).
            self.ranges = dict(_FS_RANGES)
        for el in self.elements:
            if el not in self.ranges:
                raise ValueError(f"Для элемента {el!r} не задан диапазон в ranges")
