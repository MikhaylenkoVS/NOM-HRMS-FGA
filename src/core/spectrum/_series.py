"""Homologous-series detection for isotope-labelled (CD3 / CD3CO) spectra."""

import logging
from functools import lru_cache

import numpy as np
import pandas as pd
from src.configs import CHEM
from ._chem import exact_mass_from_counts
from ._penalty import PenaltyWeights
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


def _count_in_window(sorted_mz: np.ndarray, target_mz: float, ppm_tol: float) -> int:
    """Сколько пиков попадает в ppm-окно вокруг target."""
    if sorted_mz.size == 0:
        return 0
    tol = abs(target_mz) * float(ppm_tol) * 1e-6
    lo = int(np.searchsorted(sorted_mz, target_mz - tol, side="left"))
    hi = int(np.searchsorted(sorted_mz, target_mz + tol, side="right"))
    return max(0, hi - lo)


def _peaks_in_window(
    sorted_mz: np.ndarray, target_mz: float, ppm_tol: float
) -> list[float]:
    """Список пиков в ppm-окне вокруг target."""
    if sorted_mz.size == 0:
        return []
    tol = abs(target_mz) * float(ppm_tol) * 1e-6
    lo = int(np.searchsorted(sorted_mz, target_mz - tol, side="left"))
    hi = int(np.searchsorted(sorted_mz, target_mz + tol, side="right"))
    return [float(v) for v in sorted_mz[lo:hi]]


def _series_o_limit(brutto: str, delta: float, max_groups: int) -> int:
    """Предел длины по кислороду: CD3 — O//2, CD3CO — O."""
    try:
        counts = parse_formula(str(brutto))
    except Exception:
        return int(max_groups)
    o = int(counts.get("O", 0))
    d = float(delta)
    if abs(d - float(CHEM.derivatization_shifts["delta_cd3"])) < 0.01:
        return min(int(max_groups), o // 2)
    if abs(d - float(CHEM.derivatization_shifts["delta_cd3co"])) < 0.01:
        return min(int(max_groups), o)
    return int(max_groups)


def _add_penalty(detail: dict, key: str, value: float, reason: str) -> None:
    """Добавить/усилить штраф и причину, не дублируя текст."""
    if value <= 0:
        return
    penalties = detail.setdefault("penalties", {})
    penalties[key] = max(float(penalties.get(key, 0.0)), float(value))
    reasons = detail.setdefault("reasons", [])
    if reason not in reasons:
        reasons.append(reason)


def _finalize_policy(
    details: list[dict], *, confirmation_mode: str = "overlap_only"
) -> dict:
    """Пересчитать confidence/confirmed/ambiguous.

    По умолчанию (``overlap_only``) ступень считается reliable, если у неё
    нет только двух блокирующих штрафов — ``source_overlap`` и
    ``conflict_overlap``. Остальные штрафы (изотоп, O-лимит, профиль и т.п.)
    сохраняются в confidence/reasons, но не отсекают ступень: их шкала ещё
    не валидирована. Режим ``all_penalties`` оставлен для экспериментов.
    """
    if confirmation_mode not in ("overlap_only", "all_penalties"):
        raise ValueError(f"неизвестный confirmation_mode: {confirmation_mode}")
    for d in details:
        penalties = d.get("penalties", {})
        total = min(100.0, float(sum(penalties.values())))
        d["confidence"] = round(100.0 - total, 1)
        if d.get("status") == "gap":
            continue
        if confirmation_mode == "overlap_only":
            blocked = "source_overlap" in penalties or "conflict_overlap" in penalties
            d["status"] = "ambiguous" if blocked else "reliable"
        else:
            d["status"] = "reliable" if total == 0.0 else "ambiguous"

    reliable_ns = [d["n"] for d in details if d.get("status") == "reliable"]
    confirmed = max(reliable_ns, default=0)
    ambiguous_ns = [
        d["n"] for d in details if d.get("status") != "reliable" and d["n"] > confirmed
    ]
    ambiguous = max(ambiguous_ns, default=confirmed)
    amb_confs = [
        d["confidence"]
        for d in details
        if d.get("status") != "reliable" and d["n"] > confirmed
    ]
    confidence = min(amb_confs, default=100.0)
    display = f"{confirmed}({ambiguous})" if ambiguous > confirmed else str(confirmed)
    return {
        "confirmed_length": int(confirmed),
        "ambiguous_length": int(ambiguous),
        "confidence": float(confidence),
        "display_length": display,
    }


@lru_cache(maxsize=200_000)
def _theor_ion_mass_cached(brutto_str: str, ion_mode: str) -> float:
    """Теоретическая m/z по брутто-формуле (кэш между вызовами и прогонами)."""
    counts = parse_formula(brutto_str)
    return _neutral_to_ion_mass(exact_mass_from_counts(counts), ion_mode)


def _apply_hard_snr_filter(
    result: pd.DataFrame,
    snr_min: float,
    confirmation_mode: str = "overlap_only",
) -> pd.DataFrame:
    """Жёстко обрезать серию перед первым шагом с S/N < ``snr_min``.

    Критерий применяется только к шагам, для которых RAW-профиль дал
    конечное значение ``snr``. Шаг с низким S/N считается отсутствующим:
    серия обрывается перед ним (для ``max_gaps=0`` это эквивалентно
    удалению пика и разрыву цепочки).
    """
    if snr_min <= 0 or result.empty:
        return result
    keep_rows = []
    for _, row in result.iterrows():
        details = list(row["step_details"])
        low_n = None
        for detail in details:
            value = detail.get("snr")
            if value is None:
                continue
            value = float(value)
            if np.isfinite(value) and value < float(snr_min):
                low_n = int(detail["n"])
                break
        if low_n is None:
            keep_rows.append(row)
            continue
        if low_n <= 1:
            continue
        kept = [d for d in details if int(d.get("n", 0)) < low_n]
        if not any(d.get("status") != "gap" for d in kept):
            continue
        row = row.copy()
        row["step_details"] = kept
        row["steps_found"] = [int(d["n"]) for d in kept if d.get("status") != "gap"]
        row["missing"] = [int(d["n"]) for d in kept if d.get("status") == "gap"]
        row["series_mz"] = [
            None if d.get("status") == "gap" else d.get("mz") for d in kept
        ]
        row["n_groups"] = int(kept[-1]["n"]) if kept else 0
        policy = _finalize_policy(kept, confirmation_mode=confirmation_mode)
        row["confirmed_length"] = int(policy["confirmed_length"])
        row["ambiguous_length"] = int(policy["ambiguous_length"])
        row["confidence"] = float(policy["confidence"])
        row["display_length"] = policy["display_length"]
        row["ambiguous"] = bool(policy["ambiguous_length"] > policy["confirmed_length"])
        keep_rows.append(row)
    if not keep_rows:
        return result.iloc[0:0].copy()
    return pd.DataFrame(keep_rows, columns=result.columns).reset_index(drop=True)


def find_series(
    src,
    deriv,
    delta,
    ppm_tol=5.0,
    max_groups=20,
    max_gaps=0,
    confirmation_mode: str = "overlap_only",
    require_first_step: bool = False,
    significance_level: float = 0.95,
    anchor_column: str | None = None,
    profile_check: bool = False,
    formula_check: bool = False,
    profile_max_jump: float | None = 10.0,
    profile_max_corr: float | None = 0.5,
    raw_path: str | None = None,
    profile_scans: int = 16,
    resolution_scans: int | None = None,
    profile_min_persistence: float = 0.8,
    snr_min: float = 3.0,
    weights: PenaltyWeights | None = None,
    allow_gaps: bool | None = None,
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

    weights = weights or PenaltyWeights()
    if ppm_tol <= 0:
        raise ValueError(f"ppm_tol должно быть > 0, получено {ppm_tol}")
    if max_groups < 1 or max_consecutive_misses < 1:
        raise ValueError(
            f"max_groups ({max_groups}) и max_consecutive_misses "
            f"({max_consecutive_misses}) должны быть >= 1"
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
    _src_mz_sorted = np.sort(np.asarray(src.table["mass"], dtype=float))
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

        # Первые три ступени отсутствуют — серия не считается, даже если
        # пользователь отключил require_first_step (защита от случайных
        # совпадений на высоких степенях).
        if not any(step in found_steps for step in (1, 2, 3)):
            continue
        if require_first_step and 1 not in found_steps:
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

        if found_steps:
            o_limit = _series_o_limit(brutto, delta, max_groups)
            found_mz = {
                int(step): series_mz[int(step) - 1]
                for step in found_steps
                if 0 <= int(step) - 1 < len(series_mz)
            }
            iso_status = str(getattr(row, "iso_status", "") or "")
            try:
                iso_dev = float(getattr(row, "iso_dev", float("nan")))
            except (TypeError, ValueError):
                iso_dev = float("nan")
            details = []
            for n in range(1, n_groups + 1):
                if n not in found_mz:
                    details.append(
                        {
                            "n": n,
                            "status": "gap",
                            "confidence": 100.0 - weights.gap(1),
                            "penalties": {"gap": weights.gap(1)},
                            "reasons": ["пропуск шага"],
                        }
                    )
                    continue
                target = m0_ref + n * delta
                src_hits = _peaks_in_window(_src_mz_sorted, target, ppm_tol)
                n_src = len(src_hits)
                n_deriv = _count_in_window(_mz_sorted, target, ppm_tol)
                penalties = {}
                reasons = []
                if n_src > 0:
                    penalties["source_overlap"] = weights.source_overlap(n_src)
                    reasons.append("наложение на пик исходного спектра")
                if n > o_limit:
                    penalties["o_excess"] = weights.o_excess(n - o_limit)
                    reasons.append(
                        "превышение допустимой длины по количеству атомов кислорода"
                    )
                if iso_status == "inconsistent":
                    if np.isfinite(iso_dev):
                        iso_pen = weights.isotope(iso_dev)
                    else:
                        iso_pen = weights.isotope(float("nan"))
                    penalties["isotope"] = iso_pen
                    reasons.append("изотопный паттерн не подтверждён")
                total = min(100.0, float(sum(penalties.values())))
                details.append(
                    {
                        "n": n,
                        "mz": float(found_mz[n]),
                        "n_deriv": int(n_deriv),
                        "n_src": int(n_src),
                        "src_mz": src_hits,
                        "o_excess": bool(n > o_limit),
                        "iso_status": iso_status,
                        "iso_dev": float(iso_dev),
                        "status": "reliable" if total == 0.0 else "ambiguous",
                        "confidence": round(100.0 - total, 1),
                        "penalties": penalties,
                        "reasons": reasons,
                    }
                )
            # Профиль интенсивностей: штрафуем конкретный скачок/корреляцию.
            if profile_check and len(found_intensities) >= 2:
                ints = np.asarray(found_intensities, dtype=float)
                if np.all(ints > 0):
                    ratios = ints[1:] / ints[:-1]
                    worst = int(np.argmax(ratios))
                    jump = float(ratios[worst])
                    jump_step = int(found_steps[worst + 1])
                    detail = next(
                        (d for d in details if int(d["n"]) == jump_step), None
                    )
                    if detail is not None:
                        detail["intensity_jump"] = jump
                    if (
                        detail is not None
                        and detail.get("status") != "reliable"
                        and profile_max_jump is not None
                        and jump > float(profile_max_jump)
                    ):
                        _add_penalty(
                            detail,
                            "intensity_profile",
                            weights.intensity(
                                5.0 * (jump / float(profile_max_jump) - 1.0)
                            ),
                            "скачок интенсивности между ступенями",
                        )
                    if (
                        profile_max_corr is not None
                        and np.isfinite(int_corr)
                        and int_corr > float(profile_max_corr)
                    ):
                        last_detail = details[-1]
                        last_detail["int_corr"] = float(int_corr)
                        if last_detail.get("status") == "reliable":
                            continue
                        _add_penalty(
                            last_detail,
                            "intensity_profile",
                            weights.intensity(
                                5.0 * (float(int_corr) - float(profile_max_corr)) / 0.5
                            ),
                            "несогласованный профиль интенсивностей",
                        )

            policy = _finalize_policy(details, confirmation_mode=confirmation_mode)
            confirmed_length = policy["confirmed_length"]
            ambiguous_length = policy["ambiguous_length"]
            series_confidence = policy["confidence"]
            display_length = policy["display_length"]
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
                    "o_limit": int(o_limit),
                    "confirmed_length": int(confirmed_length),
                    "ambiguous_length": int(ambiguous_length),
                    "ambiguous": bool(ambiguous_length > confirmed_length),
                    "confidence": float(series_confidence),
                    "display_length": display_length,
                    "step_details": details,
                }
            )

        if not found_steps:
            continue

    result = pd.DataFrame(
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
            "o_limit",
            "confirmed_length",
            "ambiguous_length",
            "ambiguous",
            "confidence",
            "display_length",
            "step_details",
        ],
    )

    # Profile-разрешение наложений source/derivative. Если в объединённом
    # окне видно >= 1 + n_src пиков, наложение разрешено: source-штраф
    # снимается, и шаг может стать reliable.
    if raw_path and not result.empty:
        try:
            from ._profile_resolve import ProfileResolver

            resolver = ProfileResolver(raw_path, scans=resolution_scans)
            for idx in range(len(result)):
                for detail in result.at[idx, "step_details"]:
                    src_mz = detail.get("src_mz") or []
                    penalties = detail.get("penalties", {})
                    if not src_mz or "source_overlap" not in penalties:
                        continue
                    center = float(detail["mz"])
                    tol = abs(center) * float(ppm_tol) * 1e-6
                    lo = min([center] + [float(v) for v in src_mz]) - tol
                    hi = max([center] + [float(v) for v in src_mz]) + tol
                    resolved = resolver.resolve(lo, hi)
                    expected = 1 + len(src_mz)
                    detail["profile_peaks"] = int(resolved["n_peaks"])
                    detail["profile_expected"] = int(expected)
                    if int(resolved["n_peaks"]) >= expected:
                        penalties.pop("source_overlap", None)
                        detail["reasons"] = [
                            r for r in detail.get("reasons", []) if "исходного" not in r
                        ]
                        detail["profile_resolved"] = True
                    else:
                        deficit = (expected - int(resolved["n_peaks"])) / expected
                        _add_penalty(
                            detail,
                            "poor_resolution",
                            min(
                                weights.poor_resolution_max,
                                weights.poor_resolution_max * deficit,
                            ),
                            "плохое разрешение пиков",
                        )
        except Exception as exc:  # RAW может быть недоступен
            logger.debug("profile resolution skipped: %s", exc)

    # Per-step RAW-профиль: считаем метрики один раз на все уникальные
    # m/z шагов, затем раздаём штрафы. Это не удаляет шаги.
    if raw_path and not result.empty:
        try:
            from src.core.io.raw_profile import validate_masses

            unique_masses = sorted(
                {
                    float(d["mz"])
                    for details in result["step_details"]
                    for d in details
                    if "mz" in d
                }
            )
            if unique_masses:
                metrics = validate_masses(
                    raw_path,
                    unique_masses,
                    ppm=ppm_tol,
                    max_scans=profile_scans,
                    min_snr=snr_min,
                ).set_index("mass")
                for idx in range(len(result)):
                    for detail in result.at[idx, "step_details"]:
                        mz = detail.get("mz")
                        if mz is None or float(mz) not in metrics.index:
                            continue
                        met = metrics.loc[float(mz)]
                        persistence = float(met["persistence"])
                        detail["persistence"] = persistence
                        detail["shape_ok"] = bool(met["shape_ok"])
                        detail["multi"] = bool(met.get("multi", False))
                        detail["snr"] = float(met["snr"])
                        if detail.get("status") == "reliable":
                            continue
                        if persistence < profile_min_persistence:
                            _add_penalty(
                                detail,
                                "persistence",
                                weights.persistence(
                                    persistence, profile_min_persistence
                                ),
                                f"низкая персистентность ({persistence:.0%})",
                            )
                        if not bool(met["shape_ok"]):
                            _add_penalty(
                                detail,
                                "peak_profile",
                                weights.peak_profile,
                                "неудовлетворительная форма пика",
                            )
                        if bool(met.get("multi", False)):
                            _add_penalty(
                                detail,
                                "poor_resolution",
                                weights.multi_resolution,
                                "несколько пиков в окне",
                            )
        except Exception as exc:  # профиль не должен ломать поиск
            logger.debug("profile penalties skipped: %s", exc)

    # Жёсткий критерий: шаг с S/N < snr_min считается отсутствующим.
    if raw_path and not result.empty:
        result = _apply_hard_snr_filter(
            result,
            snr_min=snr_min,
            confirmation_mode=confirmation_mode,
        )

    # Штрафы за конфликты: наложение пиков разных серий. Дополнительный
    # штраф «без предыдущей ступени» — только когда пропуски разрешены.
    if not result.empty:
        from ._conflicts import analyze_conflicts

        for cluster in analyze_conflicts(result, tolerance=0.001):
            members = cluster.get("members", [])
            if len(members) < 2:
                continue
            supported = set(cluster.get("supported", []))
            mixed = bool(supported) and any(
                int(m["row"]) not in supported for m in members
            )
            for member in members:
                ridx = int(member["row"])
                step = int(member["step"])
                details = result.at[ridx, "step_details"]
                detail = next((d for d in details if int(d["n"]) == step), None)
                if detail is None:
                    continue
                detail["conflict_overlap"] = True
                _add_penalty(
                    detail,
                    "conflict_overlap",
                    weights.conflict_overlap,
                    "наложение пика другой серии",
                )
                if max_gaps > 0 and mixed and ridx not in supported:
                    detail["conflict_no_prev"] = True
                    _add_penalty(
                        detail,
                        "conflict_no_prev",
                        weights.conflict_no_prev,
                        "конфликт без предыдущей ступени",
                    )
        for ridx in range(len(result)):
            details = result.at[ridx, "step_details"]
            policy = _finalize_policy(details, confirmation_mode=confirmation_mode)
            result.at[ridx, "confirmed_length"] = policy["confirmed_length"]
            result.at[ridx, "ambiguous_length"] = policy["ambiguous_length"]
            result.at[ridx, "confidence"] = policy["confidence"]
            result.at[ridx, "display_length"] = policy["display_length"]
            result.at[ridx, "ambiguous"] = bool(
                policy["ambiguous_length"] > policy["confirmed_length"]
            )

    # P2/P3: химическая проверка продукта и пометка конфликтов (опционально).
    if formula_check and not result.empty:
        from ._validate import attach_formula_check

        if formula_check:
            group = None
            if (
                abs(float(delta) - float(CHEM.derivatization_shifts["delta_cd3"]))
                < 0.01
            ):
                group = "cd3"
            elif (
                abs(float(delta) - float(CHEM.derivatization_shifts["delta_cd3co"]))
                < 0.01
            ):
                group = "cd3co"
            if group:
                counts_by_brutto = {}
                for brutto in result["brutto"].unique():
                    try:
                        counts_by_brutto[str(brutto)] = parse_formula(str(brutto))
                    except Exception:
                        continue
                result = attach_formula_check(result, group, counts_by_brutto)

    return result


# ===========================================================================
# Сборка итоговой таблицы
# ===========================================================================
