"""Auto-generated."""
import logging
import math
import numpy as np
from src.core.domain.spectrum import Spectrum
from ._denoise import compute_noise_threshold
from ._generate import _generate_candidate_formulas, _ion_shift, _neutral_to_ion_mass
from ._constants import FormulaSearchConfig, ATOMIC_MASS, _FS_RANGES, _FS_ELEMENTS, _FORMULA_SEARCH
from ._chem import _beynon_m1_ratio_cached, _counts_to_str, _nom_distance
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

    table = src.table.copy()
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
        src.table = table
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

    # Предвычисляем DBE для всех кандидатов
    cand_dbe = 1.0 + cand_counts[:, 0].astype(float) - cand_counts[:, 1].astype(float) / 2.0 + cand_counts[:, 2].astype(float) / 2.0

    brutto_col = [None] * len(table)
    assign_col = [False] * len(table)
    candidates_col = [None] * len(table)

    for idx, (mass_obs,) in enumerate(zip(table["mass"])):
        mass_obs = float(mass_obs)

        abs_ppm = np.abs((cand_masses_ion - mass_obs) / mass_obs * 1e6)
        mask = abs_ppm <= rel_error_ppm
        if not mask.any():
            candidates_col[idx] = []
            continue

        global_indices = np.where(mask)[0]

        best_local: int | None = None
        best_score = float("inf")

        m1_real: float | None = None
        if isotope_filter and original is not None:
            try:
                m1_real = _measure_m1_ratio(mass_obs, original)
            except Exception:
                m1_real = None

        for li in global_indices:
            c_val = int(cand_counts[li, 0])
            h_val = int(cand_counts[li, 1])
            o_val = int(cand_counts[li, 2])
            n_val = int(cand_counts[li, 3])
            if c_val <= 0:
                continue
            hc = h_val / c_val
            oc = o_val / c_val
            nc = n_val / c_val
            ndist = _nom_distance(hc, oc)
            dbe = float(cand_dbe[li])
            dbe_pen = (dbe - 20) * 0.5 if dbe > 20 else 0.0
            nc_pen = nc * 2.0 if nc > 0.3 else 0.0
            if n_val > 3 and (o_val == 0 or o_val / n_val < 0.5):
                n_abs_pen = (n_val - 3) * 2.0
            else:
                n_abs_pen = 0.0
            iso_pen = 0.0
            if m1_real is not None and m1_real > 0:
                m1_theor = _beynon_m1_ratio_cached(c_val, h_val, o_val, n_val)
                if m1_theor > 0:
                    dev = abs(m1_real - m1_theor) / m1_theor
                    if dev > _ISOTOPE_TOLERANCE:
                        iso_pen = _ISOTOPE_PENALTY
            score = nom_weight * ndist + dbe_pen + nc_pen + n_abs_pen + iso_pen
            if score < best_score:
                best_score = score
                best_local = li

        if best_local is None:
            sorted_order = np.argsort(abs_ppm[mask])
            chosen_global = int(global_indices[sorted_order[0]])
        else:
            chosen_global = int(best_local)

        sorted_order = np.argsort(abs_ppm[mask])
        sorted_global = global_indices[sorted_order]
        all_candidates_list = [_counts_to_str(*cand_counts[i]) for i in sorted_global]
        candidates_col[idx] = all_candidates_list
        assign_col[idx] = True
        brutto_col[idx] = _counts_to_str(*cand_counts[chosen_global])

    table["brutto"] = brutto_col
    table["assign"] = assign_col
    table["all_candidates"] = candidates_col
    src.table = table
    return src

