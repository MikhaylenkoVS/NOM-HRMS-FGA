"""Auto-generated."""
import logging
import numpy as np
import pandas as pd
from src.core.domain.spectrum import Spectrum
from src.configs import CHEM
from ._chem import _counts_to_str, exact_mass_from_counts
from ._constants import FormulaSearchConfig
from ._generate import _neutral_to_ion_mass, _ion_shift
from src.core.domain.molecule import parse_formula

logger = logging.getLogger(__name__)


def _find_peak(mz_array, target_mz, ppm_tol):
    """Find the peak in ``mz_array`` closest to ``target_mz`` within tolerance.

    Parameters
    ----------
    mz_array : array-like of float
        Candidate m/z values to search.
    target_mz : float
        Target m/z to match.
    ppm_tol : float
        Maximum allowed deviation (ppm).

    Returns
    -------
    int or None
        Index of the closest peak within ``ppm_tol``, or ``None`` if none
        falls within tolerance.
    """
    mz = mz_array.astype(float, copy=False) if isinstance(mz_array, np.ndarray) else np.asarray(mz_array, dtype=float)
    diffs_ppm = np.abs(mz - target_mz) / target_mz * 1e6
    mask = diffs_ppm <= ppm_tol
    if not mask.any():
        return None
    # Find the closest peak among those within tolerance
    valid = np.where(mask, diffs_ppm, np.inf)
    return int(np.argmin(valid))

def find_series(
    src,
    deriv,
    delta,
    ppm_tol=5.0,
    max_groups=20,
    allow_gaps=True,
    min_series_length=1,
    max_consecutive_misses=3,
    progress_callback=None,
):
    """Detect homologous derivatization series in a labelled spectrum.

    For each assigned source peak ``m_0``, searches the derivatized spectrum
    for the chain ``m_0 + 1*delta, m_0 + 2*delta, ..., m_0 + n*delta``. The
    number of steps found equals the number of reactive functional groups
    (-COOH for ``DELTA_CD3``, -OH for ``DELTA_CD3CO``).

    Parameters
    ----------
    src : Spectrum
        Source spectrum with assigned formulas (needs ``brutto``, ``mass``,
        ``assign`` columns).
    deriv : Spectrum
        Derivatized-sample spectrum (needs ``mass``, ``intensity`` columns).
    delta : float
        Expected m/z shift per functional group (Da), e.g. ``DELTA_CD3``.
    ppm_tol : float, optional
        Mass-match tolerance (ppm). Must be > 0. Default 5.0.
    max_groups : int, optional
        Maximum number of functional groups (series steps) to probe.
        Default 20.
    allow_gaps : bool, optional
        If ``True`` (recommended), keep searching past a missing step;
        if ``False``, stop the series at the first gap. Default ``True``.
    min_series_length : int, optional
        Minimum series length required to emit a record. Default 1.
    max_consecutive_misses : int, optional
        Stop probing the series after this many consecutive missed (gap)
        steps.  Avoids wasteful loops for molecules with few functional
        groups when ``allow_gaps=True``.  Must be >= 1.  Default 3.

    Returns
    -------
    pandas.DataFrame
        One row per detected series with columns: ``mass_src``, ``brutto``,
        ``n_groups`` (length by last found step), ``steps_found`` (1-based
        list), ``missing`` (skipped steps inside the series), ``series_mz``
        (m/z per step 1..n_groups, ``None`` for a gap).

    Raises
    ------
    ValueError
        If ``ppm_tol <= 0``, if ``max_groups``/``min_series_length``/
        ``max_consecutive_misses`` are below 1, or if required columns
        are missing from ``src``/``deriv``.

    Notes
    -----
    The series length is the last *found* step (1-based): observing steps
    1, 2, 3, 5 yields ``n_groups = 4`` recorded as length 5 with step 4
    listed under ``missing``.
    """

    if ppm_tol <= 0:
        raise ValueError(f"ppm_tol должно быть > 0, получено {ppm_tol}")
    if max_groups < 1 or min_series_length < 1 or max_consecutive_misses < 1:
        raise ValueError(
            f"max_groups ({max_groups}), min_series_length ({min_series_length}) "
            f"и max_consecutive_misses ({max_consecutive_misses}) "
            "должны быть >= 1"
        )
    required_src = ["brutto", "mass", "assign"]
    missing_src = [c for c in required_src if c not in src.table.columns]
    if missing_src:
        raise ValueError(f"В src не хватает столбца {missing_src}")
    required_deriv = ["mass", "intensity"]
    missing_deriv = [c for c in required_deriv if c not in deriv.table.columns]
    if missing_deriv:
        raise ValueError(
            f"В deriv.table отсутствуют колонки {missing_deriv}. "
            "Файл дериватизированного спектра некорректен."
        )

    mz_deriv = deriv.table["mass"].values
    records = []

    # Кэш parse_formula — одни и те же формулы повторяются между пиками
    _formula_cache: dict[str, dict] = {}

    n_total = len(src.table)
    for i, row in enumerate(src.table.itertuples(index=False), start=1):
        if progress_callback:
            progress_callback(i, n_total)
        if not getattr(row, "assign", False):
            continue

        m0_obs = row.mass
        brutto = getattr(row, "brutto", "") or ""
        # Compute theoretical m/z from assigned brutto formula
        try:
            brutto_str = str(brutto)
            counts = _formula_cache.get(brutto_str)
            if counts is None:
                counts = parse_formula(brutto_str)
                _formula_cache[brutto_str] = counts
            exact_neutral = exact_mass_from_counts(counts)
            m0_theor = _neutral_to_ion_mass(exact_neutral, CHEM.default_ion_mode)
            if abs(m0_theor - m0_obs) / m0_obs > 0.001:
                m0_theor = m0_obs
        except Exception:
            m0_theor = m0_obs
        found_steps = []
        series_mz = []
        consecutive_misses = 0

        for step in range(1, max_groups + 1):
            target = m0_theor + step * delta
            idx = _find_peak(mz_deriv, target, ppm_tol)

            if idx is not None:
                found_steps.append(step)
                series_mz.append(float(mz_deriv[idx]))
                consecutive_misses = 0
            else:
                series_mz.append(None)
                consecutive_misses += 1
                if consecutive_misses >= max_consecutive_misses:
                    break
                if not allow_gaps and found_steps:
                    break

        if not found_steps:
            n_groups = 0
            missing_steps = []
            trimmed = []
        else:
            n_groups = max(found_steps)
            all_steps = set(range(1, n_groups + 1))
            missing_steps = sorted(all_steps - set(found_steps))
            trimmed = series_mz[:n_groups]

        if n_groups >= min_series_length:
            records.append(
                {
                    "mass_src": m0_obs,
                    "brutto": brutto,
                    "n_groups": n_groups,
                    "steps_found": found_steps,
                    "missing": missing_steps,
                    "series_mz": trimmed,
                }
            )

        if not found_steps:
            continue

    return pd.DataFrame(
        records,
        columns=[
            "mass_src",
            "brutto",
            "n_groups",
            "steps_found",
            "missing",
            "series_mz",
        ],
    )

# ===========================================================================
# Сборка итоговой таблицы
# ===========================================================================

