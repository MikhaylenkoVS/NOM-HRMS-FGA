"""Auto-generated."""

import logging
import math
from functools import lru_cache

import numpy as np
from src.configs import CHEM, PIPELINE
from src.core.van_krevelen import NOM_REGIONS
from src.core.domain.molecule import parse_formula
from ._constants import ATOMIC_MASS, DELTA_CD3, DELTA_CD3CO, FormulaSearchConfig

logger = logging.getLogger(__name__)

# convert to tuples to preserve the exact original types.
DEFAULT_BRUTTO_DICT = {
    el: tuple(rng) for el, rng in PIPELINE.default_brutto_dict.items()
}


@lru_cache(maxsize=16)
def _generate_cached(
    mass_min: float,
    mass_max: float,
    c_range: tuple[int, int],
    h_range: tuple[int, int],
    o_range: tuple[int, int],
    n_range: tuple[int, int],
) -> tuple[tuple[int, int, int, int, float], ...]:
    """Enumerate candidate CHON formulas (memoized on hashable parameters)."""
    eps = 1e-9  # защита от округления в ceil/floor
    mass_min_abs = mass_min * 0.99
    mass_max_abs = mass_max * 1.01

    c_min, c_max = c_range
    h_min, h_max = h_range
    o_min, o_max = o_range
    n_min, n_max = n_range

    M_C = ATOMIC_MASS["C"]
    M_H = ATOMIC_MASS.get("H", 0.0)
    M_O = ATOMIC_MASS.get("O", 0.0)
    M_N = ATOMIC_MASS.get("N", 0.0)
    M_O_max = o_max * M_O
    M_N_max = n_max * M_N
    M_extra = M_O_max + M_N_max  # макс. добавка гетероатомов

    result: list[tuple[int, int, int, int, float]] = []

    for c in range(c_min, c_max + 1):
        base_C = c * M_C
        if base_C > mass_max_abs:
            break

        # ---------- допустимый диапазон H для этого C ----------
        # Даже с макс. O+N масса должна достичь mass_min_abs
        h_lo = max(
            h_min,
            math.ceil((mass_min_abs - base_C - M_extra) / M_H - eps),
        )
        # Без O+N масса не должна превысить mass_max_abs
        h_hi = min(
            h_max,
            math.floor((mass_max_abs - base_C) / M_H + eps),
        )
        if h_lo > h_hi:
            continue

        for h in range(h_lo, h_hi + 1):
            base_CH = base_C + h * M_H

            # ---------- допустимый диапазон O ----------
            o_lo = max(
                o_min,
                (
                    math.ceil((mass_min_abs - base_CH - M_N_max) / M_O - eps)
                    if M_O > 0
                    else 0
                ),
            )
            o_hi = min(
                o_max,
                math.floor((mass_max_abs - base_CH) / M_O + eps) if M_O > 0 else 0,
            )
            if o_lo > o_hi:
                continue

            for o in range(o_lo, o_hi + 1):
                base_CHO = base_CH + o * M_O

                # ---------- допустимый диапазон N ----------
                n_lo = max(
                    n_min,
                    math.ceil((mass_min_abs - base_CHO) / M_N - eps) if M_N > 0 else 0,
                )
                n_hi = min(
                    n_max,
                    math.floor((mass_max_abs - base_CHO) / M_N + eps) if M_N > 0 else 0,
                )
                for n in range(n_lo, n_hi + 1):
                    mass = base_CHO + n * M_N

                    # ── Классические химические правила (жёсткие) ──────
                    # LEWIS: сумма валентностей должна быть чётной
                    #   4C + H + 3N + 2O ≡ H + N (mod 2)
                    if (h + n) % 2 != 0:
                        continue
                    # SENIOR: необходимое условие существования связного графа
                    #   H ≤ 2C + N + 2  (эквивалентно DBE ≥ 0)
                    if h > 2 * c + n + 2:
                        continue

                    result.append((c, h, o, n, mass))

    return tuple(result)


def _generate_candidate_formulas(
    mass_min: float,
    mass_max: float,
    cfg: FormulaSearchConfig,
    mode: str = "soft",
) -> list[tuple[int, int, int, int, float]]:
    """Enumerate candidate CHON formulas within a neutral-mass window.

    Returns (c, h, o, n, mass) tuples — string building is deferred. The
    result is memoized on the hashable parameters (mass window + count ranges).
    """
    c_range = tuple(cfg.ranges["C"])
    h_range = tuple(cfg.ranges["H"])
    o_range = tuple(cfg.ranges.get("O", (0, 0)))
    n_range = tuple(cfg.ranges.get("N", (0, 0)))
    return list(
        _generate_cached(mass_min, mass_max, c_range, h_range, o_range, n_range)
    )


def _neutral_to_ion_mass(neutral_mass: float, ion_mode: str) -> float:
    """Convert a neutral mass to observed m/z for a given ion type.

    Parameters
    ----------
    neutral_mass : float
        Neutral monoisotopic mass (Da).
    ion_mode : str
        Ionization mode. Recognised (case-insensitive): ``"neutral"``/empty
        (no shift), ``"[M-H]-"`` (subtract one proton mass), ``"[M+H]+"``
        (add one proton mass).

    Returns
    -------
    float
        The corresponding m/z value.

    Raises
    ------
    ValueError
        If ``ion_mode`` is not recognised.
    """
    ion_mode = ion_mode.lower()

    if ion_mode in ("neutral", None, ""):
        return neutral_mass

    # отрицательный режим [M-H]- : вычитаем массу протона (не атома H)
    if ion_mode in ("[m-h]-", "m-h", "mh-"):
        return neutral_mass - CHEM.proton_mass

    # положительный режим [M]+ : вычитаем только массу электрона
    if ion_mode in ("[m]+", "m+", "[m+]"):
        return neutral_mass - CHEM.electron_mass

    # положительный режим [M+H]+ : добавляем массу протона
    if ion_mode in ("[m+h]+", "m+h", "mh+"):
        return neutral_mass + CHEM.proton_mass

    # можно добавить другие аддукты позже
    raise ValueError(f"Unknown ion_mode: {ion_mode}")


def _ion_shift(ion_mode: str) -> float:
    """Return the constant mass shift (Da) for vectorised ion conversion.

    ``neutral_mass + _ion_shift(mode) == observed m/z``.
    """
    ion_mode = ion_mode.lower() if ion_mode else ""
    if ion_mode in ("neutral", None, ""):
        return 0.0
    if ion_mode in ("[m-h]-", "m-h", "mh-"):
        return -CHEM.proton_mass
    if ion_mode in ("[m]+", "m+", "[m+]"):
        return -CHEM.electron_mass
    if ion_mode in ("[m+h]+", "m+h", "mh+"):
        return +CHEM.proton_mass
    raise ValueError(f"Unknown ion_mode: {ion_mode}")


# ── NOM-приоритизация ────────────────────────────────────────────────────────

# Центры NOM-областей (усреднённые вершины) для расчёта расстояния
_NOM_REGION_CENTERS: list[tuple[float, float]] = [
    (
        sum(v[0] for v in r["vertices"]) / len(r["vertices"]),
        sum(v[1] for v in r["vertices"]) / len(r["vertices"]),
    )
    for r in NOM_REGIONS
]

# ── Изотопный фильтр ¹³C (опциональный, формула Бейнона) ──────────────────

# Относительные распространённости тяжёлых изотопов (в %):
