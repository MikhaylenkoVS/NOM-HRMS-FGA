"""Isotope arithmetic: theoretical isotope patterns and isotope variants.

Единый источник изотопных данных — ``configs/constants/isotope.json``
(``isotope_table``), поэтому поддержка новых элементов (S, P, галогены)
добавляется правкой JSON, а не кода.

Модуль даёт три вещи:

* :func:`pattern` — теоретический изотопный паттерн (M, M+1, M+2, …)
  как отношения интенсивностей к моноизотопному пику. Считается свёрткой
  полиномов по номинальному сдвигу массы, поэтому корректно учитывает
  Cl/Br (вклад сразу в M+2), S (M+1 и M+2) и мультиномиальность.
* :func:`variants` — список изотопных вариантов формулы (замена одного
  атома на тяжёлый изотоп): точный сдвиг массы, вероятность, метка
  (``13C``, ``34S``, ``37Cl`` …).
* :func:`find_isotope_variants` — поиск этих вариантов в наблюдаемом
  спектре: для каждого варианта ищется пик в ppm-окне и сравнивается
  измеренное отношение интенсивностей с теоретическим.

Оценки — по природным распространённостям изотопов (IUPAC/NIST), значения
округлены так, как их принято приводить в таблицах.
"""

from __future__ import annotations

import logging
from typing import Iterable, Mapping

import numpy as np

from src.configs.loader import ISOTOPE_CFG

logger = logging.getLogger(__name__)

#: element -> tuple of (exact isotope mass, natural abundance)
ISOTOPE_TABLE: dict[str, tuple[tuple[float, float], ...]] = {
    el: tuple((float(m), float(p)) for m, p in pairs)
    for el, pairs in dict(ISOTOPE_CFG.isotope_table).items()
}

#: Максимальный номинальный сдвиг, до которого считаем паттерн.
DEFAULT_MAX_SHIFT: int = int(getattr(ISOTOPE_CFG, "pattern_max_shift", 3))

#: Минимальная вероятность варианта, чтобы его вообще рассматривать.
VARIANT_MIN_PROBABILITY: float = float(
    getattr(ISOTOPE_CFG, "variant_min_probability", 0.002)
)

#: Порог расхождения измеренного M+2 с теоретическим (доля).
M2_TOLERANCE: float = float(getattr(ISOTOPE_CFG, "m2_tolerance", 0.35))


def isotopes(element: str) -> tuple[tuple[float, float], ...]:
    """Изотопы элемента как ``((масса, распространённость), …)``."""
    try:
        return ISOTOPE_TABLE[element]
    except KeyError as exc:  # pragma: no cover - защита от опечаток в конфиге
        raise KeyError(
            f"Нет изотопных данных для {element!r}. "
            f"Добавьте элемент в isotope.json -> isotope_table."
        ) from exc


def isotope_label(element: str, mass_index: int) -> str:
    """Метка изотопа, например ``13C`` или ``81Br``."""
    mass = ISOTOPE_TABLE[element][mass_index][0]
    return f"{int(round(mass))}{element}"


def nominal_shift(element: str, mass_index: int) -> int:
    """Номинальный сдвиг массы изотопа относительно самого лёгкого (0, 1, 2, …)."""
    base = ISOTOPE_TABLE[element][0][0]
    return int(round(ISOTOPE_TABLE[element][mass_index][0] - base))


def _convolve(a: list[float], b: list[float], max_shift: int) -> list[float]:
    """Свёртка двух срезанных полиномов по номинальному сдвигу."""
    out = [0.0] * (max_shift + 1)
    for i, ai in enumerate(a):
        if ai == 0.0:
            continue
        limit = min(len(b), max_shift - i + 1)
        for j in range(limit):
            if b[j]:
                out[i + j] += ai * b[j]
    return out


def _element_poly(element: str, count: int, max_shift: int) -> list[float]:
    """Полином ``(Σ (p_i/p_0) x^{s_i})^count``, срезанный по ``max_shift``.

    Коэффициент при ``x^0`` равен 1.0 — это нормировка на чисто
    моноизотопный состав, поэтому результат сразу даёт отношения
    интенсивностей к пику M.
    """
    pairs = ISOTOPE_TABLE.get(element)
    if not pairs or count <= 0:
        return [1.0] + [0.0] * max_shift
    p0 = pairs[0][1]
    if p0 <= 0:  # pragma: no cover - некорректный конфиг
        return [1.0] + [0.0] * max_shift

    base = [0.0] * (max_shift + 1)
    for idx, (_mass, abundance) in enumerate(pairs):
        shift = nominal_shift(element, idx)
        if shift <= max_shift:
            base[shift] += abundance / p0
    if base[0] == 0.0:
        base[0] = 1.0

    # Быстрое возведение в степень повторным перемножением срезанных полиномов.
    result = [1.0] + [0.0] * max_shift
    factor = base
    n = count
    while n > 0:
        if n & 1:
            result = _convolve(result, factor, max_shift)
        n >>= 1
        if n:
            factor = _convolve(factor, factor, max_shift)
    return result


def pattern(
    counts: Mapping[str, int],
    max_shift: int = DEFAULT_MAX_SHIFT,
) -> list[float]:
    """Теоретический изотопный паттерн как отношения к моноизотопному пику.

    Parameters
    ----------
    counts : mapping of {str: int}
        Атомные количества, например ``{"C": 7, "H": 6, "O": 2, "Cl": 1}``.
    max_shift : int, optional
        До какого номинального сдвига считать (по умолчанию из конфига).

    Returns
    -------
    list of float
        ``[1.0, M+1/M, M+2/M, …]``. Для чисто моноизотопного состава —
        ``[1.0, 0.0, …]``.
    """
    poly = [1.0] + [0.0] * max_shift
    for element, n in counts.items():
        if not n or n <= 0:
            continue
        poly = _convolve(poly, _element_poly(element, int(n), max_shift), max_shift)
    poly[0] = 1.0
    return poly


def m1_ratio(counts: Mapping[str, int]) -> float:
    """Теоретическое отношение M+1/M (доля, не проценты)."""
    return pattern(counts, max_shift=1)[1]


def m2_ratio(counts: Mapping[str, int]) -> float:
    """Теоретическое отношение M+2/M."""
    return pattern(counts, max_shift=2)[2]


def variants(
    counts: Mapping[str, int],
    max_substitutions: int = 1,
    min_probability: float = VARIANT_MIN_PROBABILITY,
) -> list[dict]:
    """Изотопные варианты формулы, отсортированные по убыванию вероятности.

    Parameters
    ----------
    counts : mapping of {str: int}
        Атомные количества.
    max_substitutions : int, optional
        Сколько атомов заменяем на тяжёлые (1 — только однократные замены).
    min_probability : float, optional
        Отбрасывать варианты с отношением к M ниже этого порога.

    Returns
    -------
    list of dict
        Элементы вида ``{"label": "37Cl", "delta_mass": 1.997, "shift": 2,
        "ratio": 0.32, "element": "Cl", "count": 1}``; ``ratio`` — ожидаемая
        интенсивность относительно моноизотопного пика.
    """
    pairs_all: list[tuple[str, int, float, float]] = []  # el, count, delta, ratio
    for element, n in counts.items():
        if not n or n <= 0:
            continue
        iso = ISOTOPE_TABLE.get(element)
        if not iso or len(iso) == 1:
            continue
        p0 = iso[0][1]
        for idx in range(1, len(iso)):
            delta = iso[idx][0] - iso[0][0]
            ratio = int(n) * iso[idx][1] / p0
            pairs_all.append((element, int(n), delta, ratio))

    out: list[dict] = []
    for element, n, delta, ratio in pairs_all:
        if ratio < min_probability:
            continue
        # Индекс изотопа по точному сдвигу (в таблице их не больше четырёх).
        idx = next(
            i
            for i in range(1, len(ISOTOPE_TABLE[element]))
            if abs(ISOTOPE_TABLE[element][i][0] - ISOTOPE_TABLE[element][0][0] - delta)
            < 1e-9
        )
        out.append(
            {
                "label": isotope_label(element, idx),
                "delta_mass": delta,
                "shift": nominal_shift(element, idx),
                "ratio": ratio,
                "element": element,
                "count": 1,
            }
        )

    if max_substitutions >= 2:
        # Двукратные замены одного и того же элемента: 2×13C, 2×37Cl и т.п.
        for element, n, delta, ratio in pairs_all:
            if n < 2:
                continue
            iso = ISOTOPE_TABLE[element]
            for i in range(1, len(iso)):
                p_i = iso[i][1]
                p0 = iso[0][1]
                combo_ratio = n * (n - 1) / 2.0 * (p_i / p0) ** 2
                if combo_ratio >= min_probability:
                    out.append(
                        {
                            "label": f"2×{isotope_label(element, i)}",
                            "delta_mass": 2 * (iso[i][0] - iso[0][0]),
                            "shift": 2 * nominal_shift(element, i),
                            "ratio": combo_ratio,
                            "element": element,
                            "count": 2,
                        }
                    )

    out.sort(key=lambda v: -v["ratio"])
    return out


def _lookup_peak(
    masses: np.ndarray,
    intensities: np.ndarray,
    target: float,
    ppm_tol: float,
) -> tuple[float, float] | None:
    """Найти ближайший пик к ``target`` в ppm-окне; вернуть (масса, интенсивность)."""
    tol = max(abs(target) * ppm_tol * 1e-6, 1e-9)
    diffs = np.abs(masses - target)
    mask = diffs <= tol
    if not mask.any():
        return None
    idx = np.where(mask)[0]
    best = idx[int(np.argmin(diffs[idx]))]
    return float(masses[best]), float(intensities[best])


def measure_pattern(
    mass: float,
    spectrum_table,
    ppm_tol: float = 5.0,
    max_shift: int = 2,
) -> dict[int, float]:
    """Измерить отношения M+k/M в спектре (по номинальным сдвигам).

    Для каждого сдвига берётся самый вероятный точный сдвиг массы
    (13C для M+1; 34S/37Cl/81Br для M+2 — ищется по каждому кандидату).
    """
    masses = np.asarray(spectrum_table["mass"], dtype=float)
    intensities = np.asarray(spectrum_table["intensity"], dtype=float)
    m0 = _lookup_peak(masses, intensities, mass, ppm_tol)
    if m0 is None or m0[1] <= 0:
        return {}
    base_intensity = m0[1]

    measured: dict[int, float] = {}
    for shift in range(1, max_shift + 1):
        # Массовые сдвиги, которые дают такой номинальный сдвиг:
        candidates: list[float] = []
        for element, iso in ISOTOPE_TABLE.items():
            for i in range(1, len(iso)):
                if nominal_shift(element, i) == shift:
                    candidates.append(iso[i][0] - iso[0][0])
        best: tuple[float, float] | None = None
        for delta in candidates:
            hit = _lookup_peak(masses, intensities, mass + delta, ppm_tol)
            if hit and (best is None or hit[1] > best[1]):
                best = hit
        if best is not None:
            measured[shift] = best[1] / base_intensity
    return measured


def find_isotope_variants(
    mass: float,
    counts: Mapping[str, int],
    spectrum_table,
    ppm_tol: float = 5.0,
    max_substitutions: int = 1,
    tolerance: float = float(ISOTOPE_CFG.tolerance),
) -> list[dict]:
    """Сопоставить изотопные варианты формулы с наблюдаемыми пиками.

    Для каждого варианта (например, ``13C`` или ``37Cl``) считается ожидаемая
    m/z, ищется пик в ppm-окне и сравнивается измеренное отношение
    интенсивностей с теоретическим.

    Returns
    -------
    list of dict
        ``{"label", "expected_mz", "ratio_theor", "found_mz", "ratio_measured",
        "deviation", "ok"}`` — ``ok`` True, если пик найден и расхождение
        в пределах ``tolerance``.
    """
    results: list[dict] = []
    for var in variants(counts, max_substitutions=max_substitutions):
        expected_mz = mass + var["delta_mass"]
        hit = _lookup_peak(
            np.asarray(spectrum_table["mass"], dtype=float),
            np.asarray(spectrum_table["intensity"], dtype=float),
            expected_mz,
            ppm_tol,
        )
        row = {
            "label": var["label"],
            "expected_mz": expected_mz,
            "ratio_theor": var["ratio"],
            "found_mz": hit[0] if hit else None,
            "intensity": hit[1] if hit else None,
            "ratio_measured": None,
            "deviation": None,
            "ok": False,
        }
        if hit:
            base = _lookup_peak(
                np.asarray(spectrum_table["mass"], dtype=float),
                np.asarray(spectrum_table["intensity"], dtype=float),
                mass,
                ppm_tol,
            )
            if base and base[1] > 0:
                ratio_measured = hit[1] / base[1]
                row["ratio_measured"] = ratio_measured
                denom = max(var["ratio"], 1e-12)
                row["deviation"] = abs(ratio_measured - var["ratio"]) / denom
                row["ok"] = row["deviation"] <= tolerance
        results.append(row)
    return results


def isotope_variant_masses(
    mass: float,
    counts: Mapping[str, int],
    max_substitutions: int = 1,
) -> list[tuple[float, str, float]]:
    """Ожидаемые m/z изотопных вариантов: ``[(mz, label, ratio), …]``."""
    return [
        (mass + v["delta_mass"], v["label"], v["ratio"])
        for v in variants(counts, max_substitutions=max_substitutions)
    ]


def element_counts_from_iterable(elements: Iterable[str]) -> dict[str, int]:
    """Свернуть последовательность символов элементов в словарь количеств."""
    counts: dict[str, int] = {}
    for el in elements:
        counts[el] = counts.get(el, 0) + 1
    return counts
