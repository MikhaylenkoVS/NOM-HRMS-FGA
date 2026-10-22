"""Источник формул-кандидатов: сжатая база формул или перебор.

Назначение формул может получать кандидатов двумя способами:

* **сжатая база формул** (``data/formula_db/*.fdb`` + манифест) — поиск по
  массовому окну за миллисекунды на пик (рекомендуется, используется
  автоматически, если файл базы доступен);
* **перебор** (:mod:`src.core.spectrum._generate`) — запасной вариант, если
  база недоступна.

База содержит CHNOSP-формулы (C, N, O, S, P; водород восстанавливается).
Галогены добавляются «слоем подстановок»: для каждой комбинации галогенов
(F, Cl, Br, I) выполняется дополнительный запрос к базе по массе
``m − Δ(галогены)``, а найденные формулы дополняются этой комбинацией.
Такой слой включается только при изотопном свидетельстве (сильный M+2) или
когда CHNOSP-кандидатов в окне нет, поэтому обычный прогон остаётся быстрым.
"""

from __future__ import annotations

import itertools
import logging
import os
import sys
from pathlib import Path

import numpy as np

from ._constants import ATOMIC_MASS, HALOGENS, FormulaSearchConfig
from ._isotopes import ISOTOPE_TABLE

logger = logging.getLogger(__name__)

#: Целочисленная шкала масс (1e-11 Да), как в базе формул.
MASS_SCALE_INT = 100_000_000_000
BIN_WIDTH_U_INT = 10_000_000_000
_MASS_H_U = int(round(ATOMIC_MASS["H"] * MASS_SCALE_INT))

#: Предельное число атомов галогенов в брутто-формуле по умолчанию.
#: Значение — пользовательская настройка (GUI/CLI); здесь только дефолт.
DEFAULT_HALOGEN_ATOMS = 5

#: Сколько галогенных подстановок разрешено перебирать за один запрос к базе.
#: Их число растёт комбинаторно (до 5 атомов — 126 комбинаций), а каждая
#: комбинация — отдельный запрос. Пока галогены не встроены в саму базу
#: (uint64-формат), перебор ограничиваем и предупреждаем в логе.
_MAX_HALOGEN_COMBOS = 16

#: Сколько кандидатов запрашивать у базы на один поиск.
_MAX_DB_RESULTS = 200_000

#: Масса атома водорода — для модели замещения H -> X.
MASS_H = float(ATOMIC_MASS["H"])


def find_manifest() -> Path | None:
    """Найти манифест сжатой базы формул (проект или PyInstaller-бандл).

    Выбор делается реестром вариантов (``src/core/formula_db/_variants.py``):
    если установлено несколько баз, берётся самая приоритетная (с галогенами).
    Переменная окружения ``NOM_FORMULA_DB=chnosp|chorsphal|none`` позволяет
    переопределить выбор.
    """
    # Проект, PyInstaller-бандл и user data (скачанная отдельно база).
    try:
        from src.core.formula_db._variants import search_dirs

        dirs = search_dirs()
    except Exception:
        dirs = [Path(__file__).resolve().parents[3] / "data" / "formula_db"]
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            dirs.append(Path(meipass) / "data" / "formula_db")
    try:
        from src.core.formula_db._variants import active_variant

        chosen = active_variant(dirs)
        if chosen is not None:
            from src.core.formula_db._variants import find_variant_path

            return find_variant_path(chosen, dirs)
        if (os.environ.get("NOM_FORMULA_DB") or "").strip().lower() in (
            "none",
            "off",
            "0",
        ):
            return None  # явный отказ от базы
    except Exception:  # pragma: no cover - реестр не должен ломать запуск
        pass
    for d in dirs:
        try:
            if d.is_dir():
                manifests = sorted(d.glob("*.manifest.json"))
                if manifests:
                    return manifests[-1]
        except OSError:  # pragma: no cover - защита от прав доступа
            continue
    return None


def open_formula_db(manifest_path: str | Path | None = None):
    """Открыть базу формул; ``None``, если файла или зависимости нет.

    Parameters
    ----------
    manifest_path : str or Path or None
        Путь к манифесту. Если не задан — ищется автоматически
        (:func:`find_manifest`).
    """
    path = Path(manifest_path) if manifest_path else find_manifest()
    if path is None or not Path(path).is_file():
        logger.info("Сжатая база формул не найдена — используется перебор.")
        return None
    try:
        reader = _open_reader_for_manifest(path)
        logger.info(
            "Сжатая база формул подключена: %s (формат v%s, %s формул%s)",
            Path(path).name,
            getattr(reader, "format_version", 2),
            f"{reader.total_formulas:,}",
            ", галогены в базе" if getattr(reader, "has_halogens", False) else "",
        )
        return reader
    except Exception as exc:  # pragma: no cover - нет zstandard и т.п.
        logger.warning("Не удалось открыть базу формул (%s): %s", path, exc)
        return None


def _open_reader_for_manifest(path: str | Path):
    """Выбрать читателя по версии формата манифеста.

    * ``format_version = 3`` — CHNOSPHal (галогены уже в базе);
    * иначе — прежний формат v2 (CHNOSP + слой подстановок).
    """
    import json

    try:
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        manifest = {}
    if int(manifest.get("format_version", 0) or 0) == 3:
        from src.core.formula_db._reader_v3 import FormulaDatabaseReaderV3

        return FormulaDatabaseReaderV3(path, cache_size=64)
    from src.core.formula_db._reader import FormulaDatabaseReader

    return FormulaDatabaseReader(path, cache_size=64)


def halogen_combos(
    max_atoms: int = DEFAULT_HALOGEN_ATOMS,
) -> list[tuple[tuple[str, int], ...]]:
    """Комбинации галогенов до ``max_atoms`` атомов.

    Каждая комбинация — кортеж пар ``(элемент, количество)``:
    ``[(("F", 1),), (("Cl", 1),), …, (("Cl", 2),), (("Cl", 1), ("Br", 1)), …]``.
    """
    if max_atoms <= 0:
        return []
    out: list[tuple[tuple[str, int], ...]] = []
    for n in range(1, max_atoms + 1):
        for combo in itertools.combinations_with_replacement(HALOGENS, n):
            # Сворачиваем в (элемент, количество), сохраняя порядок HALOGENS
            collapsed = tuple(
                (el, combo.count(el)) for el in HALOGENS if combo.count(el)
            )
            if collapsed not in out:
                out.append(collapsed)
    return out


def _halogen_cfg() -> dict:
    """Секция ``halogen_search`` из formula_search.json."""
    from src.configs import FORMULA_SEARCH_CFG

    section = getattr(FORMULA_SEARCH_CFG, "halogen_search", None)
    if section is None:
        return {}
    return dict(section) if hasattr(section, "keys") else {}


def slowdown_factor(n_combos: int) -> float:
    """Ориентировочное замедление назначения формул (база 16 комбинаций = 1.0).

    Значения — измеренная таблица ``halogen_search.slowdown_table``
    (см. tools/measure_halogen_slowdown.py).
    """
    table = _halogen_cfg().get("slowdown_table")
    if not table:
        table = [[16, 1.0], [1000, 1.8]]
    factor = 1.0
    for limit, value in table:
        if n_combos <= limit:
            return float(value)
        factor = float(value)
    return factor


def halogen_search_plan(
    cfg: FormulaSearchConfig,
    max_combinations: int = 16,
    exhaustive: bool = True,
    max_atoms_total: int | None = None,
) -> dict:
    """Что именно будет проверяться и чего это стоит.

    Возвращает: сколько комбинаций выбрано, сколько допустимо в окнах,
    коэффициент замедления и нужен ли предупреждающий баннер (число комбинаций
    существенно больше базовых 16).
    """
    combos, allowed = select_halogen_combos(
        cfg, max_combinations, exhaustive, max_atoms_total
    )
    warn_from = int(_halogen_cfg().get("warn_from", 21))
    show_warning = bool(_halogen_cfg().get("show_warning", False))
    n = len(combos)
    return {
        "selected": n,
        "allowed": allowed,
        "exhaustive": bool(exhaustive),
        "slowdown": slowdown_factor(n),
        "warn": n >= warn_from,
        #: Показывать ли предупреждение пользователю (флаг конфига).
        "warn_enabled": show_warning,
        "limits": halogen_limits(cfg),
    }


def halogen_limits(cfg: FormulaSearchConfig) -> dict[str, int]:
    """Максимумы атомов по галогенам из пользовательских диапазонов.

    Именно эти значения определяют, какие комбинации вообще разрешены
    (например, Cl <= 5, Br <= 3 при соответствующих окнах).
    """
    limits: dict[str, int] = {}
    for el in HALOGENS:
        rng = cfg.ranges.get(el) if cfg.ranges else None
        limits[el] = int(rng[1]) if rng else 0
    return limits


def combo_priority(combo: tuple[tuple[str, int], ...]) -> tuple:
    """Ключ сортировки комбинаций (сортировка — по убыванию ключа).

    Порядок правил (уточнён заказчиком):
      1. МЕНЬШЕ суммарное число атомов галогенов — перебор начинается с
         наименьших количеств каждого отдельного галогена
         (F1, Cl1, Br1, I1, затем двух-атомные и т. д.);
      2. при равном числе атомов — «концентрированные» варианты
         (F5 и Cl4F важнее, чем F2ClBrI): больше атомов одного галогена;
      3. меньше разных галогенов в комбинации;
      4. выше вероятность изотопного паттерна (устойчивость порядка).

    Возвращаются обратные знаки для сортировки ``reverse=True``.
    """
    counts = [n for _, n in combo]
    if not counts:
        # Пустая подстановка — это «без галогенов»: она обрабатывается вне
        # списка комбинаций и в приоритете должна идти последней.
        return (-1e9, 0, 0, 1.0)
    probability = 1.0
    for el, n in combo:
        isotopes = ISOTOPE_TABLE.get(el) or []
        if len(isotopes) < 2:
            continue  # моноизотопный элемент на паттерн не влияет
        probability *= isotopes[1][1] ** n
    return (-sum(counts), max(counts), -len(counts), probability)


def halogen_combos_within(
    limits: dict[str, int],
    max_atoms_total: int | None = None,
) -> list[tuple[tuple[str, int], ...]]:
    """Все допустимые комбинации галогенов по пределам пользователя.

    Учитываются и персональные пределы (F <= 2, Br <= 3, ...), и общий предел
    числа атомов галогенов (``max_atoms_total``).
    """
    caps = {el: max(0, int(limits.get(el, 0))) for el in HALOGENS}
    total_cap = sum(caps.values()) if max_atoms_total is None else int(max_atoms_total)
    total_cap = max(0, min(total_cap, sum(caps.values())))
    out: list[tuple[tuple[str, int], ...]] = []

    def _walk(idx: int, acc: list[tuple[str, int]], used: int) -> None:
        if idx == len(HALOGENS):
            if used > 0:
                out.append(tuple(acc))
            return
        el = HALOGENS[idx]
        for n in range(0, min(caps[el], total_cap - used) + 1):
            if n:
                acc.append((el, n))
            _walk(idx + 1, acc, used + n)
            if n:
                acc.pop()

    _walk(0, [], 0)
    out.sort(key=combo_priority, reverse=True)
    return out


def select_halogen_combos(
    cfg: FormulaSearchConfig,
    max_combinations: int,
    exhaustive: bool = False,
    max_atoms_total: int | None = None,
) -> tuple[list[tuple[tuple[str, int], ...]], int]:
    """Выбранные комбинации и их общее число в разрешённом пространстве.

    По умолчанию берётся не более ``max_combinations`` самых приоритетных
    комбинаций; при ``exhaustive=True`` — все. Если разрешённых комбинаций
    меньше лимита, берутся все (лимит не «добивается» искусственно).
    """
    limits = halogen_limits(cfg)
    allowed = halogen_combos_within(limits, max_atoms_total)
    limit = max(1, int(max_combinations))
    if exhaustive:
        return allowed, len(allowed)
    # ``allowed`` уже отсортирован по приоритету (см. combo_priority): сначала
    # комбинации с наименьшим числом атомов, внутри равных — концентрированные.
    # Одиночные подстановки F1/Cl1/Br1/I1 попадают в набор автоматически.
    return allowed[:limit], len(allowed)


def _most_probable_combos(
    combos: list[tuple[tuple[str, int], ...]],
    limit: int,
) -> list[tuple[tuple[str, int], ...]]:
    """Оставить ``limit`` наиболее значимых галогенных комбинаций.

    Приоритет: сначала комбинации, которые вообще способны объяснить
    наблюдаемый M+2 (Cl, Br), затем — по вероятности появления изотопного
    паттерна (произведение природных распространённостей). F и I своего
    M+2 не дают, поэтому идут последними.
    """
    #: Элементы, у которых есть природный изотоп +2 (объясняют M+2).
    m2_elements = ("Cl", "Br")

    def priority(combo: tuple[tuple[str, int], ...]) -> tuple[bool, int, float]:
        explains_m2 = any(el in m2_elements and cnt > 0 for el, cnt in combo)
        total = sum(cnt for _, cnt in combo)
        probability = 1.0
        for element, count in combo:
            isotopes = ISOTOPE_TABLE.get(element) or []
            if len(isotopes) < 2:
                continue  # моноизотопный элемент на паттерн не влияет
            probability *= isotopes[1][1] ** count
        # Простые формулы (меньше атомов) вперёд: комбинации с моноизотопными
        # F/I иначе набирали бы «вероятность» 1.0 и вытесняли Cl/Br.
        return (explains_m2, -total, probability)

    return sorted(combos, key=priority, reverse=True)[:limit]


def _passes_filters(counts: dict[str, int], cfg: FormulaSearchConfig) -> bool:
    """Те же жёсткие правила, что и в переборе: диапазоны, отношения, DBE.

    Нужно, чтобы результаты поиска по базе и по перебору совпадали.
    """
    c = counts.get("C", 0)
    if c < max(1, int(cfg.min_c)):
        return False
    for el in cfg.elements:
        lo, hi = cfg.ranges[el]
        n = counts.get(el, 0)
        if n < lo or n > hi:
            return False

    h = counts.get("H", 0)
    n_at = counts.get("N", 0)
    o_at = counts.get("O", 0)
    p_at = counts.get("P", 0)
    s_at = counts.get("S", 0)
    x_at = sum(counts.get(el, 0) for el in HALOGENS)

    if cfg.ratios_enabled:
        if h > cfg.max_hc * c:
            return False
        if o_at > cfg.max_oc * c:
            return False
        if n_at > cfg.max_nc * c:
            return False
        if s_at > cfg.max_sc * c:
            return False
        if p_at > cfg.max_pc * c:
            return False
        if cfg.max_xc is not None and x_at > cfg.max_xc * c:
            return False

    dbe_num = 2 * c + 2 + n_at + p_at - h - x_at
    if dbe_num < 0 or dbe_num % 2:
        return False
    if cfg.nom_dbe_enabled and (dbe_num / 2.0) > cfg.max_dbe:
        return False
    return True


def _combo_delta_u(combo: tuple[tuple[str, int], ...]) -> int:
    """Сдвиг подстановки H -> X в целочисленной шкале (1e-11 Да)."""
    total = 0
    for el, n in combo:
        total += n * (int(round(ATOMIC_MASS[el] * MASS_SCALE_INT)) - _MASS_H_U)
    return total


def halogen_candidates_batched(
    reader,
    cfg: FormulaSearchConfig,
    center: float,
    half_width: float,
    combos: list[tuple[tuple[str, int], ...]] | None = None,
    max_halogen_atoms: int = DEFAULT_HALOGEN_ATOMS,
) -> tuple[np.ndarray, np.ndarray, int]:
    """ПОЛНЫЙ перебор галогенных подстановок (все 126 при капе 5).

    Для подстановки Δ масса родителя должна лежать в
    ``[center − Δ − ε, center − Δ + ε]``. Все такие узкие окна покрываются
    небольшим набором бинов 0.1 Да: бины читаются один раз (пакетно), затем Δ
    подбирается векторно (``searchsorted``). Возвращает
    ``(counts, masses, n_combos)``.
    """
    elements = tuple(cfg.elements)
    if center <= 0 or half_width <= 0:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0), 0

    if combos is None:
        combos = [()]
        for size in range(1, max_halogen_atoms + 1):
            for combo in halogen_combos(size):
                if combo not in combos:
                    combos.append(combo)
    else:
        combos = [()] + [c for c in combos if c]

    deltas = np.array([_combo_delta_u(c) for c in combos], dtype=np.int64)
    order = np.argsort(deltas)
    deltas_sorted = deltas[order]

    center_u = int(round(center * MASS_SCALE_INT))
    eps_u = int(half_width * MASS_SCALE_INT) + 1

    bin_ids: set[int] = set()
    for d_u in deltas_sorted:
        lo = max(0, center_u - int(d_u) - eps_u)
        hi = center_u - int(d_u) + eps_u
        if hi <= 0:
            continue
        bin_ids.update(range(lo // BIN_WIDTH_U_INT, hi // BIN_WIDTH_U_INT + 1))
    if not bin_ids:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0), len(combos)

    mass_u, counts_db, h_db = reader.arrays_for_bins(sorted(bin_ids))
    if len(mass_u) == 0:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0), len(combos)

    # Векторный подбор Δ: для каждой записи базы проверяем, попадает ли
    # родитель (та же запись) в окно пика при какой-либо подстановке.
    diff = center_u - mass_u
    pos = np.searchsorted(deltas_sorted, diff)
    pairs: list[tuple[int, int]] = []
    for shift in (-1, 0):
        idx = pos + shift
        valid = (idx >= 0) & (idx < len(deltas_sorted))
        if not valid.any():
            continue
        rec_idx = np.nonzero(valid)[0]
        combo_idx = order[idx[rec_idx]]
        ok = np.abs(diff[rec_idx] - deltas[combo_idx]) <= eps_u
        pairs.extend(zip(rec_idx[ok].tolist(), combo_idx[ok].tolist()))

    rows: list[tuple[int, ...]] = []
    masses: list[float] = []
    seen_rows: set[tuple[int, ...]] = set()
    for rec, ci in pairs:
        combo = combos[int(ci)]
        n_x = sum(n for _, n in combo)
        h_final = int(h_db[rec]) - n_x
        if h_final < 0:
            continue
        counts = {el: 0 for el in elements}
        for j, el in enumerate(("C", "N", "O", "S", "P")):
            if el in counts:
                counts[el] = int(counts_db[rec, j])
        counts["H"] = h_final
        for el, n in combo:
            counts[el] = counts.get(el, 0) + n
        if not _passes_filters(counts, cfg):
            continue
        row = tuple(counts[el] for el in elements)
        if row in seen_rows:
            continue
        seen_rows.add(row)
        rows.append(row)
        masses.append((int(mass_u[rec]) + int(deltas[int(ci)])) / MASS_SCALE_INT)

    if not rows:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0), len(combos)
    return (
        np.asarray(rows, dtype=np.int32),
        np.asarray(masses, dtype=float),
        len(combos),
    )


def db_candidates(
    reader,
    cfg: FormulaSearchConfig,
    center: float,
    half_width: float,
    include_halogens: bool = False,
    max_halogen_atoms: int = DEFAULT_HALOGEN_ATOMS,
    halogen_exhaustive: bool = False,
    halogen_max_combinations: int = _MAX_HALOGEN_COMBOS,
) -> tuple[np.ndarray, np.ndarray]:
    """Кандидаты из сжатой базы в окне ``center ± half_width`` (в нейтральных массах).

    Parameters
    ----------
    reader : FormulaDatabaseReader
        Открытая база.
    cfg : FormulaSearchConfig
        Ограничения (диапазоны элементов, отношения, DBE).
    center, half_width : float
        Центр и полуширина окна в Да.
    include_halogens : bool
        Добавлять ли слой галогенных подстановок. Для баз, которые уже содержат
        галогены (``reader.has_halogens``, формат v3 — CHNOSPHal), параметр
        игнорируется: галогены приходят из самой базы и доступны всегда.
    max_halogen_atoms : int
        Максимум атомов галогенов в подстановке.

    Returns
    -------
    numpy.ndarray
        Количества атомов (int32), столбцы — в порядке ``cfg.elements``.
    numpy.ndarray
        Нейтральные моноизотопные массы, параллельные строкам.
    """
    elements = tuple(cfg.elements)
    if center <= 0 or half_width <= 0:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0, dtype=float)

    ppm = (half_width / center) * 1e6
    # Небольшой запас: база возвращает результаты по своему ppm-фильтру.
    ppm = max(ppm * 1.05, ppm + 1e-3)

    element_filter = {
        el: (int(cfg.ranges[el][0]), int(cfg.ranges[el][1]))
        for el in elements
        if el in cfg.ranges
    }

    rows: list[tuple[int, ...]] = []
    masses: list[float] = []
    seen: set[tuple[int, ...]] = set()

    def _collect(
        target_mass: float,
        extra_counts: dict[str, int],
        h_shift: int = 0,
    ) -> None:
        try:
            results = reader.search(
                target_mass,
                ppm=ppm,
                element_filter=element_filter,
                max_results=_MAX_DB_RESULTS,
            )
        except Exception as exc:  # pragma: no cover - защита от базы
            logger.debug("Ошибка поиска в базе формул: %s", exc)
            return
        for res in results:
            counts = {el: int(res.counts.get(el, 0)) for el in elements}
            for el, n in extra_counts.items():
                counts[el] = counts.get(el, 0) + n
            if h_shift:
                counts["H"] = counts.get("H", 0) + h_shift
                if counts["H"] < 0:
                    continue
            if not _passes_filters(counts, cfg):
                continue
            row = tuple(counts[el] for el in elements)
            if row in seen:
                continue
            seen.add(row)
            rows.append(row)
            masses.append(
                float(res.exact_mass) + _extra_mass(extra_counts) + h_shift * MASS_H
            )

    _collect(center, {})

    # База формата v3 (CHNOSPHal) уже содержит галогены: слой подстановок не
    # нужен и привёл бы к двойному учёту.
    halogens_in_base = bool(getattr(reader, "has_halogens", False))
    if include_halogens and max_halogen_atoms > 0 and not halogens_in_base:
        # Полный перебор: если читатель умеет пакетный доступ к бинам, все
        # подстановки разрешённого капа проверяются за один проход (см.
        # exhaustive_halogen_candidates). Ограничение «16 наиболее вероятных»
        # остаётся только как аварийный путь для читателей без пакетного API.
        exhaustive_ok = False
        if hasattr(reader, "arrays_for_bins"):
            try:
                selected, n_allowed = select_halogen_combos(
                    cfg,
                    max_combinations=halogen_max_combinations,
                    exhaustive=halogen_exhaustive,
                    max_atoms_total=max_halogen_atoms,
                )
                h_counts, h_masses, n_combos = halogen_candidates_batched(
                    reader,
                    cfg,
                    center,
                    half_width,
                    selected,
                    max_halogen_atoms=max_halogen_atoms,
                )
                logger.debug(
                    "Галогенные комбинации: выбрано %d из %d допустимых "
                    "(полный режим: %s)",
                    n_combos,
                    n_allowed,
                    halogen_exhaustive,
                )
                exhaustive_ok = True
                for row, mass in zip(h_counts, h_masses):
                    t = tuple(int(v) for v in row)
                    if t in seen:
                        continue
                    seen.add(t)
                    rows.append(t)
                    masses.append(float(mass))
                logger.debug(
                    "Полный перебор подстановок: %d комбинаций, кандидатов %d",
                    n_combos,
                    len(h_counts),
                )
            except Exception as exc:  # pragma: no cover - запасной путь
                logger.warning(
                    "Полный перебор подстановок недоступен (%s), "
                    "используется ограниченный список",
                    exc,
                )
                exhaustive_ok = False
        if exhaustive_ok:
            combos = []
        else:
            combos = halogen_combos(max_halogen_atoms)
        if combos and len(combos) > _MAX_HALOGEN_COMBOS:
            logger.warning(
                "Галогенных подстановок %d (предел %d атомов) — за один запрос "
                "перебираются только %d наиболее вероятных; полный перебор "
                "требует базы с галогенами",
                len(combos),
                max_halogen_atoms,
                _MAX_HALOGEN_COMBOS,
            )
            combos = _most_probable_combos(combos, _MAX_HALOGEN_COMBOS)
        for combo in combos:
            extra = {el: n for el, n in combo}
            n_x = sum(extra.values())
            # Модель замещения H -> X: база содержит на `n_x` больше водородов,
            # а галогены её заменяют. Чистое прибавление X дало бы базу с другой
            # чётностью DBE (для нечётного числа галогенов такая формула вообще
            # не закрыто-оболочечная), поэтому в базе её не оказалось бы.
            delta = _extra_mass(extra) - n_x * MASS_H
            if delta >= center:
                continue
            _collect(center - delta, extra, h_shift=-n_x)

    if not rows:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0, dtype=float)
    return np.asarray(rows, dtype=np.int32), np.asarray(masses, dtype=float)


def _extra_mass(extra_counts: dict[str, int]) -> float:
    """Масса добавленных атомов (галогены и т.п.)."""
    return sum(ATOMIC_MASS[el] * n for el, n in extra_counts.items() if n)


def mass_to_counts(cfg: FormulaSearchConfig) -> dict[str, float]:
    """Массы элементов в порядке ``cfg.elements`` (удобно для векторизации)."""
    return {el: ATOMIC_MASS[el] for el in cfg.elements if el in ATOMIC_MASS}
