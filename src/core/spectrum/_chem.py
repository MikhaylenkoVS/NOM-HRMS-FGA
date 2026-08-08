"""Auto-generated."""

import logging
import math
import pandas as pd
import numpy as np
from typing import List, Tuple
from src.core.domain.molecule import parse_formula
from src.core.van_krevelen import NOM_REGIONS
from src.configs.loader import ISOTOPE_CFG
from ._constants import ATOMIC_MASS, DELTA_CD3, DELTA_CD3CO

logger = logging.getLogger(__name__)


def exact_mass_from_counts(counts: dict[str, int]) -> float:
    """Compute the exact (monoisotopic) neutral mass from element counts.

    Parameters
    ----------
    counts : dict of {str: int}
        Element counts, e.g. ``{'C': 7, 'H': 6, 'O': 2}``. Non-positive
        counts are ignored.

    Returns
    -------
    float
        Monoisotopic mass in daltons, summed from ``ATOMIC_MASS``.
    """
    mass = 0.0
    for elem, n in counts.items():
        if n <= 0:
            continue
        mass += ATOMIC_MASS[elem] * n
    return mass


def dbe_from_counts(counts: dict[str, int]) -> float:
    """Compute the double-bond equivalent (DBE) for a CHON formula.

    Parameters
    ----------
    counts : dict of {str: int}
        Element counts; keys ``"C"``, ``"H"``, ``"N"`` are used.

    Returns
    -------
    float
        DBE (rings plus pi-bonds), computed as ``max(0, 1 + C - H/2 + N/2)``.
        Negative values are clamped to zero (DBE < 0 is chemically meaningless).
    """
    c = counts.get("C", 0)
    h = counts.get("H", 0)
    n = counts.get("N", 0)
    return max(0.0, 1 + c - h / 2.0 + n / 2.0)


def _row_to_brutto(row, element_order=None):
    """Build a Hill-like brutto formula string from element columns of a row.

    Parameters
    ----------
    row : pandas.Series or mapping
        Row containing per-element integer counts under element-symbol keys.
    element_order : list of str, optional
        Elements to include, in output order. Defaults to
        ``["C", "H", "O", "N", "S", "P"]``.

    Returns
    -------
    str or None
        Concatenated formula (e.g. ``"C7H6O2"``), or ``None`` if no positive
        element counts are present.
    """
    if element_order is None:
        element_order = ["C", "H", "O", "N", "S", "P"]

    parts = []
    for el in element_order:
        if el in row and pd.notna(row[el]):
            val = row[el]
            try:
                val = int(val)
            except Exception:
                continue
            if val > 0:
                parts.append(el if val == 1 else f"{el}{val}")
    return "".join(parts) if parts else None


# -- CSV column name mapper (IMP-11) -------------------------------------------
# Единый маппинг имён колонок CSV → mass / intensity, используется


# NOM region centers (from spectrum_ops.py lines 488-498)
_NOM_REGION_CENTERS: list[tuple[float, float]] = [
    (
        sum(v[0] for v in r["vertices"]) / len(r["vertices"]),
        sum(v[1] for v in r["vertices"]) / len(r["vertices"]),
    )
    for r in NOM_REGIONS
]

# ── Изотопный фильтр ¹³C (опциональный, формула Бейнона) ──────────────────


# Isotope constants (from spectrum_ops.py lines 499-610)
# ¹³C: 1.1%, ²H: 0.015%, ¹⁷O: 0.04%, ¹⁵N: 0.37%
_BEYNON_COEFFS = ISOTOPE_CFG.beynon_coefficients

# Порог расхождения M+1/M для штрафа: если |реальное − теоретическое| / теоретическое > 20%
_ISOTOPE_TOLERANCE = ISOTOPE_CFG.tolerance

# Штраф к score при несовпадении изотопного паттерна (средний уровень)
_ISOTOPE_PENALTY = ISOTOPE_CFG.penalty

# Масса ¹³C − ¹²C (Da)
_DELTA_M1 = ISOTOPE_CFG.delta_m1


def _beynon_m1_ratio(counts: dict[str, int]) -> float:
    """Теоретическое соотношение (M+1)/M по формуле Бейнона.

    Parameters
    ----------
    counts : dict of {str: int}
        Атомные количества (C, H, O, N, ...).

    Returns
    -------
    float
        (M+1)/M как доля (не проценты), e.g. 0.078 для C₇H₆O₂.
    """
    total = 0.0
    for el, coeff in _BEYNON_COEFFS.items():
        total += counts.get(el, 0) * coeff
    return total / 100.0


def _beynon_m1_ratio_cached(c: int, h: int, o: int, n: int) -> float:
    """Теоретическое (M+1)/M для кортежа (C, H, O, N) — без dict-оверхеда."""
    return (c * 1.1 + h * 0.015 + o * 0.04 + n * 0.37) / 100.0


def _counts_to_str(c: int, h: int, o: int, n: int) -> str:
    """Build a Hill-order formula string from element counts."""
    parts = []
    if c > 0:
        parts.append(f"C{c}" if c > 1 else "C")
    if h > 0:
        parts.append(f"H{h}" if h > 1 else "H")
    if o > 0:
        parts.append(f"O{o}" if o > 1 else "O")
    if n > 0:
        parts.append(f"N{n}" if n > 1 else "N")
    return "".join(parts)


def _measure_m1_ratio(
    mass: float,
    original_spec,
    ppm_tol: float = 5.0,
) -> float | None:
    """Измерить реальное отношение M+1/M в исходном (pre-denoise) спектре.

    Ищет пик на массе mass + 1.00335 Да в пределах ppm_tol.
    Возвращает отношение интенсивностей или None, если пик не найден.

    Parameters
    ----------
    mass : float
        Масса моноизотопного пика (m/z).
    original_spec : Spectrum
        Исходный спектр до шумоподавления.
    ppm_tol : float
        Допуск поиска в ppm. По умолчанию 5.0.

    Returns
    -------
    float or None
        M1_intensity / M_intensity, или None если M+1 не найден.
    """
    mass_m1 = mass + _DELTA_M1
    tol_da = mass_m1 * ppm_tol * 1e-6

    masses = original_spec.table["mass"].values
    intensities = original_spec.table["intensity"].values

    diffs = np.abs(masses - mass_m1)
    mask = diffs <= tol_da
    if not mask.any():
        return None

    # Найти исходный пик — ближайший по массе
    diffs_orig = np.abs(masses - mass)
    mask_orig = diffs_orig <= (mass * ppm_tol * 1e-6)
    if not mask_orig.any():
        return None

    idx_orig = np.argmin(diffs_orig)
    idx_m1 = np.argmin(diffs[mask])
    m1_indices = np.where(mask)[0]
    idx_m1 = m1_indices[idx_m1]

    intensity_orig = float(intensities[idx_orig])
    intensity_m1 = float(intensities[idx_m1])

    if intensity_orig <= 0:
        return None

    return intensity_m1 / intensity_orig


def _nom_distance(hc: float, oc: float) -> float:
    """Минимальное евклидово расстояние от (O/C, H/C) до центра NOM-области."""
    if hc <= 0:
        return 10.0  # заведомо большой штраф для не-NOM
    best = min(math.hypot(oc - cx, hc - cy) for cx, cy in _NOM_REGION_CENTERS)
    return best
