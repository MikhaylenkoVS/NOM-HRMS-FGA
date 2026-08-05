"""Pipeline helpers."""
import logging
from pathlib import Path
import pandas as pd
from typing import Optional, Any
from src.core.domain.molecule import parse_formula
logger = logging.getLogger(__name__)

def _debug(msg: str) -> None:
    logger.debug(msg)


def _ppm_error(observed: float, theoretical: float) -> float:
    """Return the absolute mass error between two masses in ppm.

    Parameters
    ----------
    observed : float
        Observed mass (Da).
    theoretical : float
        Theoretical/reference mass (Da).

    Returns
    -------
    float
        ``|observed - theoretical| / theoretical * 1e6``; ``inf`` if the
        theoretical mass is zero.
    """
    if theoretical == 0:
        return float("inf")
    return abs(observed - theoretical) / theoretical * 1e6


def _normalize_brutto(value) -> Optional[str]:
    """Canonicalize a brutto-formula string to Hill-ordered element counts.

    Parameters
    ----------
    value : str or NaN
        Raw formula string (any element order, possibly with whitespace).

    Returns
    -------
    str or None
        Formula in canonical order (C, H, then others alphabetically),
        e.g. ``"C7H6O2"``; ``None`` for missing/empty input.
    """
    import re

    if pd.isna(value):
        return None
    s = str(value).strip()
    if not s:
        return None
    # Канонический порядок: C H O N S P ... (совпадает с генератором формул)
    try:
        tokens = re.findall(r"([A-Z][a-z]?)(\d*)", s)
        counts: dict[str, int] = {}
        for elem, numstr in tokens:
            if not elem:
                continue
            n = int(numstr) if numstr else 1
            counts[elem] = counts.get(elem, 0) + n
        # Убираем нули
        counts = {k: v for k, v in counts.items() if v > 0}

        # Сортировка: C, H, O, N, S, P, затем остальные по алфавиту
        def sort_key(e: str) -> tuple:
            order = {"C": 0, "H": 1, "O": 2, "N": 3, "S": 4, "P": 5}
            return (order.get(e, 99), e)

        parts = []
        for elem in sorted(counts.keys(), key=sort_key):
            cnt = counts[elem]
            parts.append(elem if cnt == 1 else f"{elem}{cnt}")
        return "".join(parts)
    except Exception:
        return s.upper()


def _match_row_by_mass(
    table: pd.DataFrame,
    mass_obs: float,
    ppm_tol: float,
    mass_col: str = "mass",
    require_assigned: bool = False,
) -> Optional[pd.Series]:
    """Find the table row whose mass best matches an observed mass.

    Parameters
    ----------
    table : pandas.DataFrame
        Table to search; must contain ``mass_col``.
    mass_obs : float
        Observed mass (Da) to match.
    ppm_tol : float
        Maximum allowed mass error (ppm).
    mass_col : str, optional
        Name of the mass column. Default ``"mass"``.
    require_assigned : bool, optional
        If ``True``, keep only rows where ``assign`` is truthy. Default False.

    Returns
    -------
    pandas.Series or None
        The closest matching row within tolerance, or ``None`` if no row
        qualifies.
    """
    if table is None or table.empty:
        return None
    if mass_col not in table.columns:
        _debug(
            f"  _match_row_by_mass: колонка '{mass_col}' не найдена, доступны {list(table.columns)}"
        )
        return None
    work = table.copy()
    work["_ppm"] = (
        work[mass_col]
        .astype(float)
        .apply(lambda x: _ppm_error(float(x), float(mass_obs)))
    )
    work = work.loc[work["_ppm"] <= ppm_tol].copy()
    if require_assigned:
        if "assign" not in work.columns:
            _debug(
                "  _match_row_by_mass: require_assigned=True, но колонки 'assign' нет"
            )
            return None
        work = work.loc[work["assign"] == True].copy()  # noqa: E712
    if work.empty:
        return None
    return work.sort_values("_ppm").iloc[0]


# ---------------------------------------------------------------------------
# Датаклассы статистики
# ---------------------------------------------------------------------------


