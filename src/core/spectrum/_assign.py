"""Auto-generated."""

import logging
import math
import numpy as np
from src.core.domain.spectrum import Spectrum
from ._denoise import compute_noise_threshold
from ._generate import _generate_candidate_formulas, _ion_shift, _neutral_to_ion_mass
from ._constants import (
    FormulaSearchConfig,
    ATOMIC_MASS,
    _FS_RANGES,
    _FS_ELEMENTS,
    _FORMULA_SEARCH,
)
from ._chem import (
    _beynon_m1_ratio_cached,
    _counts_to_str,
    _NOM_REGION_CENTERS,
    _measure_m1_ratio,
    _ISOTOPE_TOLERANCE,
    _ISOTOPE_PENALTY,
)
from src.configs import CHEM, PIPELINE

logger = logging.getLogger(__name__)


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
    sign: str | None = None,
    progress_callback=None,
):
    """Assign brutto formulas by brute-force CHON enumeration.

    Generates candidate CHON formulas over the mass window, converts them to
    m/z according to ``ion_mode``, and picks the most NOM-plausible formula
    among all candidates within ``rel_error_ppm``.

    Parameters
    ----------
    src : Spectrum
        Spectrum whose ``table`` (with a ``mass`` column) is annotated.
    rel_error_ppm : float, optional
        Maximum allowed mass error (ppm) for a match. Default 1.0.
    mass_min, mass_max : float or None, optional
        Neutral-mass window bounds; if None, taken from the observed masses.
    search_config : FormulaSearchConfig or None, optional
        Formula-generation configuration. A default config is used if None.
    brutto_generation_mode : {"nom_like", "soft"}, optional
        Passed to the candidate generator. Default ``"nom_like"``.
    ion_mode : str, optional
        Ionization mode for the neutral-to-ion conversion. Default ``"[M-H]-"``.
    nom_weight : float, optional
        Weight for the NOM-distance term in the composite score:
        ``score = nom_weight * nom_distance + penalties``. Default 1.0.

    Returns
    -------
    Spectrum
        The same spectrum with ``table["brutto"]`` (formula str or None),
        ``table["assign"]`` (bool), and ``table["all_candidates"]`` (list of str).

    Notes
    -----
    Ppm deviation is used ONLY to define the candidate set (admission window);
    within the window, ranking is by NOM chemical plausibility, not by |ppm|.
    """
    if search_config is None:
        search_config = FormulaSearchConfig()

    table = src.table
    mass_series = table["mass"]

    if mass_min is None:
        mass_min_local = float(mass_series.min())
    else:
        mass_min_local = float(mass_min)

    if mass_max is None:
        mass_max_local = float(mass_series.max())
    else:
        mass_max_local = float(mass_max)

    # Корректируем массовое окно для генерации нейтральных кандидатов
    # На входе — m/z наблюдаемых пиков (ионные массы), а генератор
    # работает в нейтральных массах. Сдвигаем окно на массу носителя заряда.
    ion_mode_lower = ion_mode.lower() if ion_mode else ""
    if ion_mode_lower in ("[m-h]-", "m-h", "mh-"):
        gen_min = mass_min_local + CHEM.proton_mass
        gen_max = mass_max_local + CHEM.proton_mass
    elif ion_mode_lower in ("[m]+", "m+", "[m+]"):
        gen_min = mass_min_local + CHEM.electron_mass
        gen_max = mass_max_local + CHEM.electron_mass
    elif ion_mode_lower in ("[m+h]+", "m+h", "mh+"):
        gen_min = mass_min_local - CHEM.proton_mass
        gen_max = mass_max_local - CHEM.proton_mass
    else:
        gen_min, gen_max = mass_min_local, mass_max_local

    # Генерируем кандидатов (нейтральные массы)
    candidates = _generate_candidate_formulas(
        mass_min=gen_min,
        mass_max=gen_max,
        cfg=search_config,
        mode=brutto_generation_mode,
    )

    if not candidates:
        table["brutto"] = None
        table["assign"] = False
        return src

    # Разделим counts и нейтральные массы (один проход)
    counts_list = []
    masses_list = []
    for c, h, o, n, mass in candidates:
        counts_list.append((c, h, o, n))
        masses_list.append(mass)
    cand_counts = np.array(counts_list, dtype=np.int32)
    cand_masses_neutral = np.array(masses_list, dtype=float)
    del counts_list, masses_list

    # Переводим нейтральные массы в m/z — векторизовано
    _shift = _ion_shift(ion_mode)
    cand_masses_ion = cand_masses_neutral + _shift

    # ── Предвычисление метрик кандидатов (OPT-07 / OPT-08) ─────────────────────
    c_arr = cand_counts[:, 0].astype(float)
    h_arr = cand_counts[:, 1].astype(float)
    o_arr = cand_counts[:, 2].astype(float)
    n_arr = cand_counts[:, 3].astype(float)

    valid = c_arr > 0
    safe_c = np.where(valid, c_arr, 1.0)
    hc_arr = np.where(valid, h_arr / safe_c, 0.0)
    oc_arr = np.where(valid, o_arr / safe_c, 0.0)
    nc_arr = np.where(valid, n_arr / safe_c, 0.0)

    cand_dbe = 1.0 + c_arr - h_arr / 2.0 + o_arr / 2.0

    centers = np.asarray(_NOM_REGION_CENTERS, dtype=float)
    ndist_arr = np.min(
        np.hypot(
            oc_arr[:, None] - centers[None, :, 0],
            hc_arr[:, None] - centers[None, :, 1],
        ),
        axis=1,
    )
    ndist_arr = np.where(hc_arr <= 0, 10.0, ndist_arr)

    dbe_pen_arr = np.where(cand_dbe > 20, (cand_dbe - 20) * 0.5, 0.0)
    nc_pen_arr = np.where(nc_arr > 0.3, nc_arr * 2.0, 0.0)
    n_abs_pen_arr = np.where(
        (n_arr > 3) & ((o_arr == 0) | (o_arr / np.where(n_arr > 0, n_arr, 1.0) < 0.5)),
        (n_arr - 3) * 2.0,
        0.0,
    )

    base_score = nom_weight * ndist_arr + dbe_pen_arr + nc_pen_arr + n_abs_pen_arr
    base_score = np.where(valid, base_score, np.inf)

    cand_m1_theor = None
    if isotope_filter and original is not None:
        cand_m1_theor = np.array(
            [
                _beynon_m1_ratio_cached(int(ci), int(hi), int(oi), int(ni))
                for ci, hi, oi, ni in cand_counts
            ],
            dtype=float,
        )

    brutto_col = [None] * len(table)
    assign_col = [False] * len(table)
    candidates_col = [None] * len(table)

    n_peaks = len(table)
    for idx, (mass_obs,) in enumerate(zip(table["mass"])):
        if progress_callback:
            progress_callback(idx + 1, n_peaks)
        mass_obs = float(mass_obs)

        abs_ppm = np.abs((cand_masses_ion - mass_obs) / mass_obs * 1e6)
        mask = abs_ppm <= rel_error_ppm
        if not mask.any():
            candidates_col[idx] = []
            continue

        global_indices = np.where(mask)[0]

        if cand_m1_theor is not None:
            m1_real = None
            try:
                m1_real = _measure_m1_ratio(mass_obs, original)
            except Exception:
                m1_real = None
            if m1_real is not None and m1_real > 0:
                safe_theor = np.where(cand_m1_theor > 0, cand_m1_theor, 1.0)
                dev = np.abs(m1_real - cand_m1_theor) / safe_theor
                iso_pen_arr = np.where(
                    (cand_m1_theor > 0) & (dev > _ISOTOPE_TOLERANCE),
                    _ISOTOPE_PENALTY,
                    0.0,
                )
                scores = base_score + iso_pen_arr
            else:
                scores = base_score
        else:
            scores = base_score

        masked_scores = scores[global_indices]
        if np.isfinite(masked_scores).any():
            chosen_global = int(global_indices[int(np.argmin(masked_scores))])
        else:
            sorted_order = np.argsort(abs_ppm[global_indices])
            chosen_global = int(global_indices[sorted_order[0]])

        sorted_order = np.argsort(abs_ppm[global_indices])
        sorted_global = global_indices[sorted_order]
        all_candidates_list = [_counts_to_str(*cand_counts[i]) for i in sorted_global]
        candidates_col[idx] = all_candidates_list
        assign_col[idx] = True
        brutto_col[idx] = _counts_to_str(*cand_counts[chosen_global])

    table["brutto"] = brutto_col
    table["assign"] = assign_col
    table["all_candidates"] = candidates_col
    return src
