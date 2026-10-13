"""Assignment of brute formulas (CHNOSP + halogens) to observed m/z values."""

import logging
import math

import numpy as np

from ._generate import _generate_cached, _ion_shift, limits_key, ranges_key
from ._constants import HALOGENS, FormulaSearchConfig
from ._chem import _counts_to_str, _NOM_REGION_CENTERS
from ._isotopes import (
    ISOTOPE_TABLE,
    find_isotope_variants,
    nominal_shift,
    variants,
)
from ._formula_source import DEFAULT_HALOGEN_ATOMS, db_candidates
from src.configs import CHEM
from src.configs.loader import ISOTOPE_CFG

logger = logging.getLogger(__name__)

_ISOTOPE_TOLERANCE = float(ISOTOPE_CFG.tolerance)
_ISOTOPE_PENALTY = float(ISOTOPE_CFG.penalty)
_M2_TOLERANCE = float(getattr(ISOTOPE_CFG, "m2_tolerance", 0.35))
#: Допуск на отношение интенсивностей при атрибуции изотопных сателлитов.
_SATELLITE_TOLERANCE = float(getattr(ISOTOPE_CFG, "satellite_tolerance", 0.35))
#: ppm-допуск поиска изотопных вариантов и сателлитов в спектре (шире, чем
#: поиск самих формул: сателлит может быть смещён и по массе, и по профилю).
_SATELLITE_PPM_TOL = float(getattr(ISOTOPE_CFG, "variant_ppm_tol", 5.0))
#: Порог M+2/M, при котором слой галогенных подстановок включается:
#: Cl даёт ≈32 %, Br ≈97 %, поэтому 5 % надёжно отделяет их от 13C-фона.
_HALOGEN_M2_EVIDENCE = float(getattr(ISOTOPE_CFG, "halogen_m2_evidence", 0.05))

#: Сдвиг M+2, по которому ищется наблюдаемый пик (34S/37Cl/81Br ≈ 1.996 Да).
_M2_MASS_SHIFT = 1.9958

#: Шаг сетки кэша массовых окон (0.001 Да).
_WINDOW_GRID = 1000.0
#: Максимум окон в кэше генератора на один вызов assign_formulas.
_MAX_WINDOW_CACHE = 4096


def _isotope_coefficients(elements: tuple[str, ...]) -> tuple[np.ndarray, np.ndarray]:
    """Векторные коэффициенты M+1 и M+2 для оценки изотопного паттерна.

    Возвращает ``(q1, q2)`` в порядке ``elements``: вклад одного атома
    элемента в отношения M+1/M и M+2/M. Это линейное приближение (как в
    формуле Бейнона, но по всей изотопной таблице, включая S/P/галогены);
    точный паттерн считается отдельно в :mod:`src.core.spectrum._isotopes`.
    """
    q1 = np.zeros(len(elements), dtype=float)
    q2 = np.zeros(len(elements), dtype=float)
    for i, el in enumerate(elements):
        pairs = ISOTOPE_TABLE.get(el)
        if not pairs:
            continue
        p0 = pairs[0][1]
        for k in range(1, len(pairs)):
            shift = nominal_shift(el, k)
            ratio = pairs[k][1] / p0
            if shift == 1:
                q1[i] += ratio
            elif shift == 2:
                q2[i] += ratio
    return q1, q2


def _sorted_mass_index(table) -> tuple[np.ndarray, np.ndarray]:
    """Массы и интенсивности спектра, отсортированные по массе."""
    masses = np.asarray(table["mass"], dtype=float)
    intensities = np.asarray(table["intensity"], dtype=float)
    order = np.argsort(masses, kind="stable")
    return masses[order], intensities[order]


def _peak_intensity_near(
    masses_sorted: np.ndarray,
    intensities_sorted: np.ndarray,
    target: float,
    ppm_tol: float,
) -> float | None:
    """Максимальная интенсивность в ppm-окне вокруг ``target`` (или None)."""
    tol = max(abs(target) * ppm_tol * 1e-6, 1e-12)
    lo = int(np.searchsorted(masses_sorted, target - tol, side="left"))
    hi = int(np.searchsorted(masses_sorted, target + tol, side="right"))
    if hi <= lo:
        return None
    return float(np.max(intensities_sorted[lo:hi]))


def _candidate_scores(
    counts: np.ndarray,
    elements: tuple[str, ...],
    idx: dict[str, int],
    nom_weight: float,
    cfg: FormulaSearchConfig,
) -> np.ndarray:
    """Композитный скор кандидатов: NOM-подобие + штрафы за экзотику.

    ``score = nom_weight * NOM_distance(O/C, H/C) + DBE/N штрафы +
    penalty_s * S + penalty_p * P + penalty_halogen * X``.
    Чем меньше — тем правдоподобнее формула.
    """
    penalty_s = cfg.penalty_s
    penalty_p = cfg.penalty_p
    penalty_halogen = cfg.penalty_halogen

    def col(el: str) -> np.ndarray:
        i = idx.get(el)
        if i is None:
            return np.zeros(len(counts), dtype=float)
        return counts[:, i].astype(float)

    c_arr = col("C")
    h_arr = col("H")
    o_arr = col("O")
    n_arr = col("N")
    p_arr = col("P")
    s_arr = col("S")
    x_arr = sum(col(el) for el in HALOGENS)

    valid = c_arr > 0
    safe_c = np.where(valid, c_arr, 1.0)
    hc_arr = np.where(valid, h_arr / safe_c, 0.0)
    oc_arr = np.where(valid, o_arr / safe_c, 0.0)
    nc_arr = np.where(valid, n_arr / safe_c, 0.0)

    # DBE = (2C + 2 + N + P - H - X) / 2.
    # (Раньше здесь вместо N использовался O — исправлено вместе с
    # расширением набора элементов.)
    dbe = (2.0 * c_arr + 2.0 + n_arr + p_arr - h_arr - x_arr) / 2.0

    centers = np.asarray(_NOM_REGION_CENTERS, dtype=float)
    ndist = np.min(
        np.hypot(
            oc_arr[:, None] - centers[None, :, 0],
            hc_arr[:, None] - centers[None, :, 1],
        ),
        axis=1,
    )
    ndist = np.where(hc_arr <= 0, 10.0, ndist)

    score = (
        nom_weight * ndist
        + np.where(dbe > 20, (dbe - 20) * 0.5, 0.0)
        + np.where(nc_arr > 0.3, nc_arr * 2.0, 0.0)
        + np.where(
            (n_arr > 3)
            & ((o_arr == 0) | (o_arr / np.where(n_arr > 0, n_arr, 1.0) < 0.5)),
            (n_arr - 3) * 2.0,
            0.0,
        )
        # Экзотические гетероатомы и галогены штрафуются ПО АТОМАМ: без
        # изотопного подтверждения (совпадение M+2) S/P/галоген-формула
        # должна проигрывать CHNO-варианту в пределах того же ppm-окна.
        + s_arr * penalty_s
        + p_arr * penalty_p
        + x_arr * penalty_halogen
    )
    return np.where(valid, score, np.inf)


def assign_formulas(
    src,
    rel_error_ppm: float = 1.0,
    mass_min: float | None = None,
    mass_max: float | None = None,
    search_config: FormulaSearchConfig | None = None,
    brutto_generation_mode: str = "nom_like",
    ion_mode: str = CHEM.default_ion_mode,
    nom_weight: float = 1.0,
    isotope_filter: bool = False,
    original=None,
    rel_error: float | None = None,
    progress_callback=None,
    isotope_variants: bool = False,
    isotope_satellites: bool = True,
    formula_db=None,
    db_halogen_atoms: int = DEFAULT_HALOGEN_ATOMS,
):
    """Assign brutto formulas by mass-local enumeration over the element set.

    Формулы ищутся **под каждый пик отдельно**: генератор запускается на
    узком окне ``m/z ± rel_error_ppm`` (с кэшем по сетке 0.001 Да), поэтому
    расширенный набор элементов (C, H, O, N, S, P, F, Cl, Br, I) не приводит
    к перебору «всех формул до 1000 Да».

    Parameters
    ----------
    src : Spectrum
        Spectrum whose ``table`` (with a ``mass`` column) is annotated.
    rel_error_ppm : float, optional
        Maximum allowed mass error (ppm) for a match. Default 1.0.
    mass_min, mass_max : float or None, optional
        Окно поиска по наблюдаемым m/z; пики вне окна остаются без формулы.
    search_config : FormulaSearchConfig or None, optional
        Formula-generation configuration (elements, ranges, ratio limits).
    brutto_generation_mode : str, optional
        Kept for API compatibility (``"nom_like"``/``"soft"``).
    ion_mode : str, optional
        Ionization mode for the neutral-to-ion conversion. Default ``"[M-H]-"``.
    nom_weight : float, optional
        Weight for the NOM-distance term in the composite score.
    isotope_filter : bool, optional
        Учитывать изотопный паттерн M+1/M+2 при ранжировании кандидатов.
    original : Spectrum or None, optional
        Исходный спектр до шумоподавления — источник M+1/M+2.
    isotope_variants : bool, optional
        Дополнительно искать изотопные варианты выбранной формулы
        (колонка ``iso_variants``).

    Returns
    -------
    Spectrum
        The same spectrum with ``table["brutto"]``, ``table["assign"]``,
        ``table["all_candidates"]`` и (при ``isotope_variants=True``)
        ``table["iso_variants"]``.

    Notes
    -----
    Ppm deviation is used ONLY to define the candidate set (admission window);
    within the window, ranking is by chemical plausibility, not by |ppm|.
    """
    if search_config is None:
        search_config = FormulaSearchConfig()

    table = src.table
    mass_values = np.asarray(table["mass"], dtype=float)
    n_rows = len(table)

    # Краевые случаи: пустой спектр и нечисловые/неположительные массы.
    valid_mass = np.isfinite(mass_values) & (mass_values > 0)
    if mass_min is not None:
        valid_mass &= mass_values >= float(mass_min)
    if mass_max is not None:
        valid_mass &= mass_values <= float(mass_max)

    if not valid_mass.any():
        table["brutto"] = [None] * n_rows
        table["assign"] = [False] * n_rows
        table["all_candidates"] = [[] for _ in range(n_rows)]
        return src

    elements = tuple(search_config.elements)
    idx = {el: i for i, el in enumerate(elements)}
    rk = ranges_key(search_config)
    lk = limits_key(search_config)
    shift = _ion_shift(ion_mode)

    # ── Изотопная проверка (подготовка) ──────────────────────────────────────
    # Индекс исходного спектра нужен и фильтру, и поиску вариантов, и оценке
    # изотопного свидетельства для слоя галогенов.
    q1 = q2 = m_sorted = i_sorted = None
    if original is not None:
        try:
            m_sorted, i_sorted = _sorted_mass_index(original.table)
            if not len(m_sorted):
                m_sorted = i_sorted = None
        except Exception:  # pragma: no cover - защита от неожиданного формата
            m_sorted = i_sorted = None
    if isotope_filter and m_sorted is not None:
        q1, q2 = _isotope_coefficients(elements)
    m2_el_idx = [idx[el] for el in ("S", "Cl", "Br") if el in idx]

    brutto_col = [None] * n_rows
    assign_col = [False] * n_rows
    candidates_col = [None] * n_rows
    variants_col = [None] * n_rows if isotope_variants else None

    window_cache: dict[tuple[float, float], tuple] = {}

    for row_i, mass_obs in enumerate(mass_values):
        if progress_callback:
            progress_callback(row_i + 1, n_rows)
        if not valid_mass[row_i]:
            candidates_col[row_i] = []
            continue
        mass_obs = float(mass_obs)

        tol = max(abs(mass_obs) * rel_error_ppm * 1e-6, 1e-12)
        neutral = mass_obs - shift
        key = (
            math.floor((neutral - tol) * _WINDOW_GRID) / _WINDOW_GRID,
            math.ceil((neutral + tol) * _WINDOW_GRID) / _WINDOW_GRID,
        )

        def _window(win_key: tuple[float, float], with_halogens: bool):
            """Кандидаты для окна: сжатая база (при наличии) или перебор."""
            cache_key = (win_key, bool(with_halogens))
            cached = window_cache.get(cache_key)
            if cached is not None:
                return cached
            if formula_db is not None:
                center = 0.5 * (win_key[0] + win_key[1])
                half = max(0.5 * (win_key[1] - win_key[0]), 1e-9)
                counts_arr, masses_arr = db_candidates(
                    formula_db,
                    search_config,
                    center,
                    half,
                    include_halogens=with_halogens,
                    max_halogen_atoms=db_halogen_atoms,
                )
                result = (counts_arr, masses_arr)
            else:
                result = _generate_cached(
                    win_key[0],
                    win_key[1],
                    rk,
                    lk,
                    search_config.min_c,
                    search_config.max_dbe,
                    brutto_generation_mode,
                    0.0,
                )
            if len(window_cache) >= _MAX_WINDOW_CACHE:
                window_cache.clear()
            window_cache[cache_key] = result
            return result

        # Слой галогенов включаем по изотопному свидетельству: сильный M+2
        # (Cl/Br дают десятки процентов) или отсутствие CHNOSP-кандидатов.
        need_hal = db_halogen_atoms > 0
        if need_hal and formula_db is not None and m_sorted is not None:
            base_int = _peak_intensity_near(m_sorted, i_sorted, mass_obs, rel_error_ppm)
            if base_int:
                m2_int = _peak_intensity_near(
                    m_sorted, i_sorted, mass_obs + _M2_MASS_SHIFT, rel_error_ppm
                )
                need_hal = bool(
                    m2_int is not None and (m2_int / base_int) >= _HALOGEN_M2_EVIDENCE
                )

        rows_c, masses_neutral = _window(key, need_hal)
        if not len(rows_c) and db_halogen_atoms > 0 and not need_hal:
            # CHNOSP не дал вариантов — пробуем с галогенами.
            rows_c, masses_neutral = _window(key, True)
        if not len(rows_c):
            candidates_col[row_i] = []
            continue

        counts = np.asarray(rows_c, dtype=np.int32)
        ion = np.asarray(masses_neutral, dtype=float) + shift
        abs_ppm = np.abs((ion - mass_obs) / mass_obs * 1e6)
        mask = abs_ppm <= rel_error_ppm
        if not mask.any():
            candidates_col[row_i] = []
            continue

        counts_win = counts[mask]
        abs_ppm_win = abs_ppm[mask]
        scores_win = _candidate_scores(
            counts_win, elements, idx, nom_weight, search_config
        )

        # ── Изотопные штрафы ────────────────────────────────────────────────
        if q1 is not None and m_sorted is not None:
            base_intensity = _peak_intensity_near(
                m_sorted, i_sorted, mass_obs, rel_error_ppm
            )
            if base_intensity and base_intensity > 0:
                counts_f = counts_win.astype(float)
                m1_theor = counts_f @ q1
                m1_meas = _peak_intensity_near(
                    m_sorted, i_sorted, mass_obs + 1.00335, rel_error_ppm
                )
                if m1_meas is not None:
                    m1_ratio = m1_meas / base_intensity
                    denom = np.where(m1_theor > 0, m1_theor, 1.0)
                    dev = np.abs(m1_ratio - m1_theor) / denom
                    scores_win = scores_win + np.where(
                        (m1_theor > 0) & (dev > _ISOTOPE_TOLERANCE),
                        _ISOTOPE_PENALTY,
                        0.0,
                    )
                # M+2 информативен для S/Cl/Br-содержащих кандидатов.
                if m2_el_idx:
                    has_m2 = (counts_win[:, m2_el_idx] > 0).any(axis=1)
                    if has_m2.any():
                        m2_meas = _peak_intensity_near(
                            m_sorted,
                            i_sorted,
                            mass_obs + _M2_MASS_SHIFT,
                            rel_error_ppm,
                        )
                        if m2_meas is not None:
                            m2_theor = counts_f @ q2 + 0.5 * m1_theor**2
                            m2_ratio = m2_meas / base_intensity
                            denom2 = np.where(m2_theor > 0, m2_theor, 1.0)
                            dev2 = np.abs(m2_ratio - m2_theor) / denom2
                            scores_win = scores_win + np.where(
                                has_m2 & (m2_theor > 0) & (dev2 > _M2_TOLERANCE),
                                _ISOTOPE_PENALTY,
                                0.0,
                            )
                            # Изотопное подтверждение: если M+2 сходится,
                            # S/Cl/Br-формула получает бонус и может
                            # выиграть у CHNO-варианта — это и есть проверка
                            # "нестандартного изотопа" по паттерну.
                            n_m2_atoms = (
                                counts_win[:, m2_el_idx].sum(axis=1).astype(float)
                            )
                            scores_win = scores_win - np.where(
                                has_m2 & (m2_theor > 0) & (dev2 <= _M2_TOLERANCE),
                                search_config.bonus_isotope_m2 * n_m2_atoms,
                                0.0,
                            )

        if np.isfinite(scores_win).any():
            best_local = int(np.argmin(scores_win))
        else:
            best_local = int(np.argmin(abs_ppm_win))

        order_ppm = np.argsort(abs_ppm_win)
        candidates_col[row_i] = [
            _counts_to_str(*counts_win[i].tolist(), element_order=elements)
            for i in order_ppm
        ]
        assign_col[row_i] = True
        chosen = counts_win[best_local]
        brutto_col[row_i] = _counts_to_str(*chosen.tolist(), element_order=elements)

        if variants_col is not None and original is not None:
            counts_dict = {el: int(chosen[idx[el]]) for el in elements}
            try:
                variants_col[row_i] = find_isotope_variants(
                    mass_obs,
                    counts_dict,
                    original.table,
                    ppm_tol=_SATELLITE_PPM_TOL,
                )
            except Exception:  # pragma: no cover - диагностика не ломает прогон
                variants_col[row_i] = []

    table["brutto"] = brutto_col
    table["assign"] = assign_col
    table["all_candidates"] = candidates_col
    if variants_col is not None:
        table["iso_variants"] = variants_col

    # ── Атрибуция изотопных сателлитов ──────────────────────────────────────
    # Пик, который на Δ (13C, 34S, 37Cl, 81Br, …) тяжелее другого пика и чьё
    # отношение интенсивностей совпадает с теоретическим, помечается как
    # изотопный сателлит этого (родительского) пика, чтобы в отчёте он не
    # выглядел самостоятельным соединением.
    if isotope_satellites:
        sat_of, sat_label = _mark_isotope_satellites(
            table,
            mass_values,
            brutto_col,
            assign_col,
            elements,
            _SATELLITE_PPM_TOL,
            _SATELLITE_TOLERANCE,
        )
        table["iso_satellite_of"] = sat_of
        table["iso_satellite_label"] = sat_label
    return src


def _mark_isotope_satellites(
    table,
    mass_values: np.ndarray,
    brutto_col: list,
    assign_col: list,
    elements: tuple[str, ...],
    ppm_tol: float,
    tolerance: float,
) -> tuple[list, list]:
    """Пометить пики-изотопные сателлиты: ``(родительская масса, метка)``.

    Для каждого назначенного пика строятся теоретические изотопные варианты
    его формулы; если в спектре есть пик на ожидаемой m/z и отношение
    интенсивностей совпадает с теоретическим в пределах ``tolerance``, этот
    пик помечается как сателлит (метка вида ``13C``, ``37Cl``).

    Пик может быть сателлитом только одного родителя: первое найденное
    совпадение фиксируется, повторные не перезаписывают пометку.
    """
    from src.core.domain.molecule import parse_formula

    n = len(mass_values)
    sat_of: list = [None] * n
    sat_label: list = [None] * n
    if not len(table):
        return sat_of, sat_label

    intensities = np.asarray(table["intensity"], dtype=float)
    assigned = [
        i for i in range(min(n, len(brutto_col))) if assign_col[i] and brutto_col[i]
    ]
    if not assigned:
        return sat_of, sat_label

    # Сателлит ищем среди ВСЕХ пиков (а не только назначенных): обычно
    # сателлитный пик своей формулы не получает, и его нужно пометить как
    # изотопный вариант родителя, а не оставлять «самостоятельным».
    finite = np.isfinite(mass_values) & (mass_values > 0)
    all_idx = np.where(finite)[0]
    order = np.argsort(mass_values[all_idx], kind="stable")
    masses_sorted = mass_values[all_idx][order]
    idx_sorted = [int(all_idx[i]) for i in order]

    for pos, parent_i in enumerate(assigned):
        parent_mass = float(mass_values[parent_i])
        if not np.isfinite(parent_mass) or parent_mass <= 0:
            continue
        try:
            counts = parse_formula(str(brutto_col[parent_i]))
        except Exception:  # pragma: no cover - защита от разбора
            continue
        counts = {el: int(cnt) for el, cnt in counts.items() if el in elements}
        if not counts:
            continue
        parent_intensity = float(intensities[parent_i])
        if parent_intensity <= 0:
            continue

        for var in variants(counts, max_substitutions=1):
            target = parent_mass + var["delta_mass"]
            tol = max(abs(target) * ppm_tol * 1e-6, 1e-12)
            lo = int(np.searchsorted(masses_sorted, target - tol, side="left"))
            hi = int(np.searchsorted(masses_sorted, target + tol, side="right"))
            if hi <= lo:
                continue
            for j_pos in range(lo, hi):
                sat_i = idx_sorted[j_pos]
                if sat_i == parent_i or sat_of[sat_i] is not None:
                    continue
                ratio = float(intensities[sat_i]) / parent_intensity
                theor = float(var["ratio"])
                if theor <= 0:
                    continue
                if abs(ratio - theor) / theor <= tolerance:
                    sat_of[sat_i] = parent_mass
                    sat_label[sat_i] = var["label"]
                    break
    return sat_of, sat_label
