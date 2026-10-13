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
import sys
from pathlib import Path

import numpy as np

from ._constants import ATOMIC_MASS, HALOGENS, FormulaSearchConfig

logger = logging.getLogger(__name__)

#: Сколько галогенов максимум добавлять слоем подстановок (1 = F/Cl/Br/I).
DEFAULT_HALOGEN_ATOMS = 1

#: Сколько кандидатов запрашивать у базы на один поиск.
_MAX_DB_RESULTS = 200_000


def find_manifest() -> Path | None:
    """Найти манифест сжатой базы формул (проект или PyInstaller-бандл)."""
    dirs: list[Path] = []
    # Проектный путь: <repo>/data/formula_db
    dirs.append(Path(__file__).resolve().parents[3] / "data" / "formula_db")
    # PyInstaller onefile распаковывает данные в sys._MEIPASS
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        dirs.append(Path(meipass) / "data" / "formula_db")
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
        from src.core.formula_db._reader import FormulaDatabaseReader

        reader = FormulaDatabaseReader(path, cache_size=64)
        logger.info(
            "Сжатая база формул подключена: %s (%s формул)",
            Path(path).name,
            f"{reader.total_formulas:,}",
        )
        return reader
    except Exception as exc:  # pragma: no cover - нет zstandard и т.п.
        logger.warning("Не удалось открыть базу формул (%s): %s", path, exc)
        return None


def halogen_combos(max_atoms: int = DEFAULT_HALOGEN_ATOMS) -> list[tuple[str, int]]:
    """Комбинации галогенов до ``max_atoms`` атомов: ``[("Cl", 1), ("Cl", 2), …]``."""
    if max_atoms <= 0:
        return []
    out: list[tuple[str, int]] = []
    for n in range(1, max_atoms + 1):
        for combo in itertools.combinations_with_replacement(HALOGENS, n):
            # Сворачиваем в (элемент, количество), сохраняя порядок HALOGENS
            collapsed = tuple(
                (el, combo.count(el)) for el in HALOGENS if combo.count(el)
            )
            if collapsed not in out:
                out.append(collapsed)
    return out


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
    if x_at > cfg.max_xc * c:
        return False

    dbe_num = 2 * c + 2 + n_at + p_at - h - x_at
    if dbe_num < 0 or dbe_num % 2:
        return False
    return (dbe_num / 2.0) <= cfg.max_dbe


def db_candidates(
    reader,
    cfg: FormulaSearchConfig,
    center: float,
    half_width: float,
    include_halogens: bool = False,
    max_halogen_atoms: int = DEFAULT_HALOGEN_ATOMS,
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
        Добавлять ли слой галогенных подстановок.
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

    def _collect(target_mass: float, extra_counts: dict[str, int]) -> None:
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
            if not _passes_filters(counts, cfg):
                continue
            row = tuple(counts[el] for el in elements)
            if row in seen:
                continue
            seen.add(row)
            rows.append(row)
            masses.append(float(res.exact_mass) + _extra_mass(extra_counts))

    _collect(center, {})

    if include_halogens and max_halogen_atoms > 0:
        for combo in halogen_combos(max_halogen_atoms):
            extra = {el: n for el, n in combo}
            delta = _extra_mass(extra)
            if delta >= center:
                continue
            _collect(center - delta, extra)

    if not rows:
        return np.zeros((0, len(elements)), dtype=np.int32), np.zeros(0, dtype=float)
    return np.asarray(rows, dtype=np.int32), np.asarray(masses, dtype=float)


def _extra_mass(extra_counts: dict[str, int]) -> float:
    """Масса добавленных атомов (галогены и т.п.)."""
    return sum(ATOMIC_MASS[el] * n for el, n in extra_counts.items() if n)


def mass_to_counts(cfg: FormulaSearchConfig) -> dict[str, float]:
    """Массы элементов в порядке ``cfg.elements`` (удобно для векторизации)."""
    return {el: ATOMIC_MASS[el] for el in cfg.elements if el in ATOMIC_MASS}
