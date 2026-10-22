"""Enumeration of candidate formulas (CHNOSP + halogens) within a mass window.

Генератор перебирает формулы по элементам из
``configs/constants/formula_search.json`` (по умолчанию C, H, O, N, S, P, F,
Cl, Br, I) с учётом:

* диапазонов количеств по каждому элементу;
* предельных отношений элемент/C (H/C, O/C, N/C, S/C, P/C, X/C, где X —
  сумма галогенов);
* правила чётности Льюиса (сумма валентностей чётна);
* условия существования связного графа (DBE >= 0) и потолка DBE.

Реализация: цикл по углероду, затем DFS по «тяжёлым» элементам в порядке
убывания массы с отсечением по достижимой массе; диапазон водорода
разворачивается в конце (его вклад считаем последним — шаг по H мал,
а ограничения по DBE и чётности задают точный интервал).

Количества в результате идут в порядке ``cfg.elements`` (для конфига по
умолчанию — C, H, O, N, S, P, F, Cl, Br, I).
"""

import logging
import math
from functools import lru_cache

import numpy as np

from src.configs import CHEM, FORMULA_SEARCH_CFG
from ._constants import ATOMIC_MASS, HALOGENS, FormulaSearchConfig

logger = logging.getLogger(__name__)

# Default per-element count ranges for brutto assignment
# (single source of truth: configs/constants/formula_search.json).
# convert to tuples to preserve the exact original types.
DEFAULT_BRUTTO_DICT = {
    el: tuple(rng) for el, rng in FORMULA_SEARCH_CFG["default_brutto_dict"].items()
}

_INF = float("inf")
_EPS = 1e-9


def ranges_key(cfg: FormulaSearchConfig) -> tuple[tuple[str, int, int], ...]:
    """Хэшируемое представление диапазонов: ``((элемент, min, max), …)``."""
    return tuple(
        (el, int(cfg.ranges[el][0]), int(cfg.ranges[el][1])) for el in cfg.elements
    )


def limits_key(cfg: FormulaSearchConfig) -> tuple[tuple[str, float], ...]:
    """Хэшируемое представление предельных отношений элемент/C."""
    if cfg.ratios_enabled:
        limits = {
            "H": float(cfg.max_hc),
            "O": float(cfg.max_oc),
            "N": float(cfg.max_nc),
            "S": float(cfg.max_sc),
            "P": float(cfg.max_pc),
        }
        x_limit = float("inf") if cfg.max_xc is None else float(cfg.max_xc)
    else:
        limits = {el: _INF for el in ("H", "O", "N", "S", "P")}
        x_limit = _INF
    for el in HALOGENS:
        limits[el] = x_limit
    return tuple(sorted(limits.items()))


@lru_cache(maxsize=16)
def _generate_cached(
    mass_min: float,
    mass_max: float,
    ranges: tuple[tuple[str, int, int], ...],
    limits: tuple[tuple[str, float], ...],
    min_c: int,
    max_dbe: float,
    mode: str = "soft",
    slack: float = 0.01,
) -> tuple[tuple[tuple[int, ...], ...], tuple[float, ...]]:
    """Enumerate candidate formulas (memoized on hashable parameters).

    Parameters
    ----------
    mass_min, mass_max : float
        Neutral-mass window. ``slack`` задаёт относительный запас по краям
        (по умолчанию ±1 %, чтобы не терять формулы на границах окна); при
        поиске по отдельному пику запас можно поставить 0.
    ranges : tuple of (str, int, int)
        ``(элемент, минимум, максимум)`` в каноническом порядке элементов.
    limits : tuple of (str, float)
        Предельные отношения элемент/C. ``inf`` отключает ограничение.
    min_c : int
        Минимальное число атомов углерода.
    max_dbe : float
        Потолок DBE.
    mode : str
        Оставлен для совместимости API (``"soft"``/``"nom_like"``); химические
        правила применяются всегда, поэтому значение не влияет на результат.
    slack : float
        Относительный запас массового окна (0.01 = ±1 %).

    Returns
    -------
    tuple of tuple of int
        Строки количеств в порядке ``ranges``.
    tuple of float
        Нейтральные моноизотопные массы, параллельные строкам количеств.
    """
    del mode  # правила применяются всегда

    elements = tuple(el for el, _, _ in ranges)
    rng = {el: (int(lo), int(hi)) for el, lo, hi in ranges}
    lim = {el: float(v) for el, v in limits}
    mass = {el: ATOMIC_MASS[el] for el in elements}

    lo = mass_min * (1.0 - slack)
    hi = mass_max * (1.0 + slack)

    m_c = mass.get("C", 0.0)
    m_h = mass.get("H", 0.0)
    c_rng = rng.get("C", (1, 1))
    h_rng = rng.get("H", (0, 0))

    c_lo = max(int(min_c), int(c_rng[0]))
    c_hi = int(c_rng[1])
    if m_c > 0:
        c_hi = min(c_hi, int(math.floor(hi / m_c + _EPS)))
    if c_hi < c_lo:
        return (), ()

    heavy = [el for el in elements if el not in ("C", "H")]
    # Тяжёлые — по убыванию массы: отсечение по массе срабатывает раньше.
    heavy.sort(key=lambda el: -mass[el])
    halogens = [el for el in HALOGENS if el in rng]
    max_xc = lim.get("F", _INF)
    max_hc = lim.get("H", _INF)

    rows: list[tuple[int, ...]] = []
    masses: list[float] = []
    counts: dict[str, int] = {}

    def _append(c: int, mass_fixed: float, x_total: int) -> None:
        """Развернуть диапазон H и применить правила валентности/DBE."""
        n_at = counts.get("N", 0)
        p_at = counts.get("P", 0)

        h_lo = int(h_rng[0])
        h_hi = int(h_rng[1])
        if max_hc != _INF:
            h_hi = min(h_hi, int(math.floor(max_hc * c + _EPS)))
        if m_h > 0:
            h_lo = max(h_lo, int(math.ceil((lo - mass_fixed) / m_h - _EPS)))
            h_hi = min(h_hi, int(math.floor((hi - mass_fixed) / m_h + _EPS)))

        # DBE = (2C + 2 + N + P - H - X) / 2; H ограничен сверху условием
        # DBE >= 0, снизу — потолком max_dbe и балансом валентностей.
        h_dbe_max = 2 * c + 2 + n_at + p_at - x_total
        h_hi = min(h_hi, h_dbe_max)
        if max_dbe != _INF:
            h_lo = max(h_lo, h_dbe_max - 2 * int(max_dbe))
        if h_lo > h_hi:
            return

        # Чётность числителя DBE (правило Льюиса).
        parity = (n_at + p_at - x_total) % 2
        start = h_hi - ((h_hi - parity) % 2)
        if start < h_lo:
            return

        base_mass = mass_fixed
        for h in range(start, h_lo - 1, -2):
            m_total = base_mass + h * m_h
            if m_total < lo or m_total > hi:
                continue
            rows.append(
                tuple(
                    c if el == "C" else (h if el == "H" else counts.get(el, 0))
                    for el in elements
                )
            )
            masses.append(m_total)

    def rec(
        k: int,
        c: int,
        mass_fixed: float,
        x_total: int,
        cap: dict[str, int],
        x_cap: int | None,
        suf_max: list[float],
        suf_min: list[float],
    ) -> None:
        # Отсечение по достижимой массе: до lo не дотянуть / в hi уже не влезть.
        if mass_fixed + suf_max[k] < lo or mass_fixed + suf_min[k] > hi:
            return
        if k == len(heavy):
            _append(c, mass_fixed, x_total)
            return

        el = heavy[k]
        m_el = mass[el]
        cnt_lo = int(rng[el][0])
        cnt_hi = cap[el]
        if el in halogens and x_cap is not None:
            # Лимит X/C общий для всех галогенов: вычитаем уже набранное.
            cnt_hi = min(cnt_hi, x_cap - x_total)

        # Нижняя граница: сколько атомов нужно, чтобы дотянуть массу до lo.
        need = lo - mass_fixed - suf_max[k + 1]
        if need > 0 and m_el > 0:
            cnt_lo = max(cnt_lo, int(math.ceil(need / m_el - _EPS)))
        # Верхняя граница: больше не влезет в hi с минимальными остальными.
        room = hi - mass_fixed - suf_min[k + 1]
        if m_el > 0:
            cnt_hi = min(cnt_hi, int(math.floor(room / m_el + _EPS)))

        for cnt in range(cnt_lo, cnt_hi + 1):
            counts[el] = cnt
            rec(
                k + 1,
                c,
                mass_fixed + cnt * m_el,
                x_total + cnt if el in halogens else x_total,
                cap,
                x_cap,
                suf_max,
                suf_min,
            )
        counts[el] = 0

    h_min_mass = int(h_rng[0]) * m_h
    n_heavy = len(heavy)
    for c in range(c_lo, c_hi + 1):
        # Максимумы по элементам с учётом лимитов элемент/C для этого C.
        cap: dict[str, int] = {}
        for el in heavy:
            hi_cnt = int(rng[el][1])
            ratio = lim.get(el, _INF)
            if ratio != _INF:
                hi_cnt = min(hi_cnt, int(math.floor(ratio * c + _EPS)))
            cap[el] = hi_cnt
        x_cap = int(math.floor(max_xc * c + _EPS)) if max_xc != _INF else None
        h_max_cnt = int(h_rng[1])
        if max_hc != _INF:
            h_max_cnt = min(h_max_cnt, int(math.floor(max_hc * c + _EPS)))

        # Суффиксные суммы достижимой массы: max — для отсечения снизу,
        # min — для отсечения сверху (включая вклад водорода).
        suf_max = [0.0] * (n_heavy + 1)
        suf_min = [0.0] * (n_heavy + 1)
        suf_max[n_heavy] = h_max_cnt * m_h
        suf_min[n_heavy] = h_min_mass
        for k in range(n_heavy - 1, -1, -1):
            el = heavy[k]
            suf_max[k] = suf_max[k + 1] + cap[el] * mass[el]
            suf_min[k] = suf_min[k + 1] + int(rng[el][0]) * mass[el]

        c_mass = c * m_c
        if c_mass + suf_max[0] < lo or c_mass + suf_min[0] > hi:
            continue
        rec(0, c, c_mass, 0, cap, x_cap, suf_max, suf_min)

    return tuple(rows), tuple(masses)


def _generate_candidate_formulas(
    mass_min: float,
    mass_max: float,
    cfg: FormulaSearchConfig,
    mode: str = "soft",
) -> list[tuple[int, ...]]:
    """Enumerate candidate formulas; последний элемент кортежа — масса.

    Возвращает кортежи ``(count_C, count_H, …, neutral_mass)`` в порядке
    ``cfg.elements``. Результат мемоизируется по хэшируемым параметрам
    (массовое окно + диапазоны + лимиты).
    """
    rows, masses = _generate_cached(
        mass_min,
        mass_max,
        ranges_key(cfg),
        limits_key(cfg),
        cfg.min_c,
        float("inf") if not cfg.nom_dbe_enabled else cfg.max_dbe,
        mode,
    )
    return [tuple(row) + (m,) for row, m in zip(rows, masses)]


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


#: Алиасы режимов ионизации (как их могут писать GUI/CLI/конфиги).
_ION_MODE_ALIASES = {
    "m-h": "[m-h]-",
    "mh-": "[m-h]-",
    "m+": "[m]+",
    "[m+]": "[m]+",
    "m+h": "[m+h]+",
    "mh+": "[m+h]+",
}


def _adduct_table() -> dict:
    """Таблица аддуктов из chemistry.json (пустая, если её нет)."""
    return dict(getattr(CHEM, "adducts", {}) or {})


def _adduct_entry(ion_mode: str):
    """Найти запись аддукта по имени режима (с учётом алиасов)."""
    key = (ion_mode or "").strip().lower()
    if key in ("neutral", ""):
        return None
    key = _ION_MODE_ALIASES.get(key, key)
    table = {name.lower(): entry for name, entry in _adduct_table().items()}
    return table.get(key)


def _ion_shift(ion_mode: str) -> float:
    """Постоянный сдвиг (Да) для перевода нейтральной массы в m/z.

    ``neutral_mass + _ion_shift(mode) == observed m/z``.
    Значения берутся из таблицы аддуктов (chemistry.json): для [M-H]-
    это −m(протона), что эквивалентно −m(H) + m(e).

    Режимы со ``status="future"`` ещё не подключены к научным стадиям и
    вызывают явную ошибку, чтобы их нельзя было использовать «вслепую».
    """
    key = (ion_mode or "").strip().lower()
    if key in ("neutral", "") or ion_mode is None:
        return 0.0
    entry = _adduct_entry(key)
    if entry is None:
        raise ValueError(f"Unknown ion_mode: {ion_mode}")
    status = str(entry.get("status", "supported")).lower()
    if status != "supported":
        raise ValueError(
            f"Режим ионизации {ion_mode!r} помечен как '{status}': "
            "он зарезервирован на будущее и пока не подключён. "
            "Используйте [M-H]-."
        )
    return float(entry["mass_shift"])


def neutral_masses(mz_values, ion_mode: str):
    """Перевести массив m/z в нейтральные массы (векторно, один раз).

    Пункт 3: все пики спектра заранее переводятся в нейтральные массы,
    и только после этого ищутся по базе формул.
    """
    shift = _ion_shift(ion_mode)
    array = np.asarray(mz_values, dtype=float)
    return array - shift
