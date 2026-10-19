"""Homologous-series detection for isotope-labelled (CD3 / CD3CO) spectra."""

import logging
from functools import lru_cache

import numpy as np
import pandas as pd
from src.configs import CHEM
from ._chem import exact_mass_from_counts
from ._generate import _neutral_to_ion_mass
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
    mz = (
        mz_array.astype(float, copy=False)
        if isinstance(mz_array, np.ndarray)
        else np.asarray(mz_array, dtype=float)
    )
    diffs_ppm = np.abs(mz - target_mz) / target_mz * 1e6
    mask = diffs_ppm <= ppm_tol
    if not mask.any():
        return None
    # Find the closest peak among those within tolerance
    valid = np.where(mask, diffs_ppm, np.inf)
    return int(np.argmin(valid))


def _find_peak_sorted(mz_sorted: np.ndarray, target_mz: float, ppm_tol: float):
    """Бинарный поиск ближайшего пика в ОТСОРТИРОВАННОМ массиве, O(log M).

    Возвращает позицию в ``mz_sorted`` или ``None``.
    """
    if mz_sorted.size == 0:
        return None
    pos = int(np.searchsorted(mz_sorted, target_mz))
    best = None
    best_dev = None
    for j in (pos - 1, pos):
        if 0 <= j < mz_sorted.size:
            dev = abs(mz_sorted[j] - target_mz) / target_mz * 1e6
            if dev <= ppm_tol and (best_dev is None or dev < best_dev):
                best, best_dev = j, dev
    return best


@lru_cache(maxsize=200_000)
def _theor_ion_mass_cached(brutto_str: str, ion_mode: str) -> float:
    """Теоретическая m/z по брутто-формуле (кэш между вызовами и прогонами)."""
    counts = parse_formula(brutto_str)
    return _neutral_to_ion_mass(exact_mass_from_counts(counts), ion_mode)


def find_series(
    src,
    deriv,
    delta,
    ppm_tol=5.0,
    max_groups=20,
    max_gaps=1,
    require_first_step: bool = True,
    significance_level: float = 0.95,
    anchor_column: str | None = None,
    profile_check: bool = False,
    profile_max_jump: float | None = 10.0,
    profile_max_corr: float | None = 0.5,
    allow_gaps: bool | None = None,
    min_series_length=1,
    max_consecutive_misses=3,
    ion_mode: str | None = None,
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
    max_gaps : int, optional
        Максимальное число пропущенных ступеней внутри серии (правило по
        умолчанию — **не более 1**). ``0`` — серия обрывается на первом
        пропуске (пропуски запрещены). При исчерпании бюджета серия
        обрывается на последней найденной ступени, поэтому в результате
        всегда ``len(missing) <= max_gaps``. Должно быть >= 0. Default 1.
    allow_gaps : bool or None, optional
        Устаревший синоним: ``False`` эквивалентно ``max_gaps=0``, ``True``
        и ``None`` — используется ``max_gaps`` (число пропусков ограничено).
        Оставлен для совместимости. Default ``None``.
    profile_check : bool, optional
        Включить проверку профиля интенсивностей продуктов (по умолчанию
        выключено — сначала сравниваем на данных). Default ``False``.
    profile_max_jump : float or None, optional
        Максимально допустимое отношение I(n+1)/I(n) между соседними
        ступенями. ``None`` — проверка отключена. Default 10.0.
    profile_max_corr : float or None, optional
        Максимально допустимая корреляция Спирмена «номер ступени —
        интенсивность». ``None`` — отключена. Default 0.5.
    anchor_column : str or None, optional
        Колонка исходного спектра с наблюдаемой m/z того же соединения в
        производном спектре (``anchor_mz_dmet`` / ``anchor_mz_dacet``).
        Если задана и значение не пустое, шаг считается от неё, а не от
        теоретической массы (компенсация дрейфа калибровки).
        Default ``None`` (теоретическая масса).
    significance_level : float, optional
        Уровень доверия для длины серии (0.95 → порог p < 0.05).
        Значимость считается по локальной плотности пиков (ADR-0009).
        Должно быть в (0, 1). Default 0.95.
    require_first_step : bool, optional
        Требовать подтверждения первой ступени (n=1). Приоритет проекта —
        точность: без монодериватизированного продукта нет доказательства
        дериватизации, а «ступени» 2..n могут быть случайными совпадениями,
        из-за которых N_COOH/N_OH завышается. Default ``True``.
    min_series_length : int, optional
        Minimum series length required to emit a record. Default 1.
    max_consecutive_misses : int, optional
        Stop probing the series after this many consecutive missed (gap)
        steps.  Avoids wasteful loops for molecules with few functional
        groups.  Must be >= 1.  Default 3.  При ``max_gaps <= 2`` бюджет
        пропусков срабатывает раньше.
    ion_mode : str or None, optional
        Ionization mode used to convert the assigned neutral mass to the
        theoretical m/z of the source peak.  ``None`` falls back to
        ``CHEM.default_ion_mode``.  Default ``None``.

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
    # Совместимость: allow_gaps=False — это max_gaps=0 (без пропусков).
    # allow_gaps=True больше не означает «пропусков сколько угодно»: их число
    # ограничено max_gaps (правило по умолчанию — не более 1).
    if allow_gaps is False:
        max_gaps = 0
    if max_gaps < 0:
        raise ValueError(f"max_gaps должно быть >= 0, получено {max_gaps}")
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
    int_deriv = (
        np.asarray(deriv.table["intensity"].values, dtype=float)
        if "intensity" in deriv.table.columns
        else np.ones(len(mz_deriv), dtype=float)
    )
    records = []

    # Вероятность случайного попадания в окно на одном шаге: отношение
    # ширины окна к среднему шагу между пиками производного спектра.
    _mz_sorted = np.sort(np.asarray(mz_deriv, dtype=float))
    _span = float(_mz_sorted[-1] - _mz_sorted[0]) if _mz_sorted.size > 1 else 0.0
    _spacing = _span / max(1, _mz_sorted.size - 1) if _span > 0 else 0.0
    if not 0.0 < float(significance_level) < 1.0:
        raise ValueError(
            f"significance_level должно быть в (0, 1), получено {significance_level}"
        )
    p_threshold = 1.0 - float(significance_level)

    n_total = len(src.table)
    for i, row in enumerate(src.table.itertuples(index=False), start=1):
        if progress_callback:
            progress_callback(i, n_total)
        if not getattr(row, "assign", False):
            continue
        # Изотопный сателлит — не самостоятельное соединение: он прикреплён
        # к материнскому пику и не должен искать собственную серию
        # дериватизации (иначе один и тот же продукт засчитывается дважды).
        satellite_of = getattr(row, "iso_satellite_of", None)
        if satellite_of is not None and not pd.isna(satellite_of):
            continue

        m0_obs = row.mass
        brutto = getattr(row, "brutto", "") or ""
        # Compute theoretical m/z from assigned brutto formula
        try:
            brutto_str = str(brutto)
            m0_theor = _theor_ion_mass_cached(
                brutto_str, str(ion_mode or CHEM.default_ion_mode)
            )
            if abs(m0_theor - m0_obs) / m0_obs > 0.001:
                m0_theor = m0_obs
        except Exception:
            m0_theor = m0_obs

        m0_ref = m0_theor
        if anchor_column:
            anchor_val = getattr(row, anchor_column, None)
            if anchor_val is not None and not pd.isna(anchor_val):
                m0_ref = float(anchor_val)
        found_steps = []
        series_mz = []
        found_intensities = []
        consecutive_misses = 0
        gaps = 0

        for step in range(1, max_groups + 1):
            target = m0_ref + step * delta
            idx = _find_peak_sorted(_mz_sorted, target, ppm_tol)

            if idx is not None:
                found_steps.append(step)
                series_mz.append(float(_mz_sorted[idx]))
                found_intensities.append(float(int_deriv[idx]))
                consecutive_misses = 0
            else:
                series_mz.append(None)
                consecutive_misses += 1
                gaps += 1
                # Правило по умолчанию: в серии допускается не более max_gaps
                # пропусков (0 — без пропусков). Бюджет исчерпан — серия
                # обрывается на последней найденной ступени, поэтому
                # len(missing) <= max_gaps всегда.
                if gaps > max_gaps:
                    break
                if consecutive_misses >= max_consecutive_misses:
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

        if require_first_step and 1 not in found_steps:
            # Первая ступень не подтверждена — серия не считается
            # (точность важнее полноты: см. ADR-0008/0009).
            continue

        # Статистическая значимость длины: сколько шагов подтверждено и
        # насколько это выше случайного фона (см. ADR-0009).
        if _spacing > 0:
            p_step = min(1.0, 2.0 * float(m0_obs) * float(ppm_tol) * 1e-6 / _spacing)
            n_confirmed = len(found_steps)
            p_value = min(1.0, float(max_groups) * p_step ** max(1, n_confirmed))
        else:
            p_step = 1.0
            p_value = 1.0
        significant = bool(p_value < p_threshold)

        # Профиль интенсивностей: у реальной молекулы продукты 1..k образуют
        # согласованную смесь; случайные наборы пиков такого профиля не дают.
        max_jump = float("nan")
        int_corr = float("nan")
        profile_ok = True
        if profile_check and len(found_steps) >= 2:
            ints = np.asarray(found_intensities, dtype=float)
            steps_arr = np.asarray(found_steps, dtype=float)
            if np.all(ints > 0):
                max_jump = float(np.max(ints[1:] / ints[:-1]))
                ranks_i = np.argsort(np.argsort(ints)).astype(float)
                ranks_s = np.argsort(np.argsort(steps_arr)).astype(float)
                if ranks_i.std() > 0 and ranks_s.std() > 0:
                    int_corr = float(np.corrcoef(ranks_s, ranks_i)[0, 1])
            if profile_max_jump is not None and np.isfinite(max_jump):
                profile_ok = profile_ok and bool(max_jump <= profile_max_jump)
            if profile_max_corr is not None and np.isfinite(int_corr):
                profile_ok = profile_ok and bool(int_corr <= profile_max_corr)
            if not profile_ok:
                # Точность прежде полноты: серия с несогласованным профилем
                # не засчитывается (ADR-0009), но только при явном включении.
                continue

        if n_groups >= min_series_length:
            records.append(
                {
                    "mass_src": m0_obs,
                    "brutto": brutto,
                    "n_groups": n_groups,
                    "steps_found": found_steps,
                    "missing": missing_steps,
                    "series_mz": trimmed,
                    "p_value": p_value,
                    "significant": significant,
                    "profile_ok": profile_ok,
                    "max_jump": max_jump,
                    "int_corr": int_corr,
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
            "p_value",
            "significant",
            "profile_ok",
            "max_jump",
            "int_corr",
        ],
    )


# ===========================================================================
# Сборка итоговой таблицы
# ===========================================================================
