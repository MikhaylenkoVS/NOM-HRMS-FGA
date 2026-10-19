"""Разрешение конфликтов: один наблюдаемый пик — несколько серий (P3).

В плотном NOM-спектре один и тот же пик дериватизата может оказаться шагом у
нескольких исходных соединений (и на разных ступенях). Раньше каждый пик
исходника искался независимо, поэтому такие «пики на все руки» порождали
ложные серии.

Правило (уточнено): конфликт важен только для **последнего наблюдаемого пика
серии**. Если спорный шаг не последний, а следующая ступень найдена и
бесспорна, серия не считается неоднозначной: цепочка продолжается уникальным
пиком. Поэтому ``ambiguous = contested[last_step]``.

ВАЖНО: сравнивать нужно только шаги **одной и той же** производной
(дейтерометилирование с дейтерометилированием, дейтероацилирование с
дейтероацилированием). Функция принимает один DataFrame — по одному на
производную, — поэтому смешивание невозможно по построению.
"""

from __future__ import annotations

import pandas as pd


def mark_conflicts(df: pd.DataFrame, tolerance: float = 0.001) -> pd.DataFrame:
    """Пометить серии, у которых есть шаги, используемые другими сериями.

    Parameters
    ----------
    df : DataFrame
        Результат ``find_series`` с колонкой ``series_mz`` (список m/z).
    tolerance : float
        Окно группировки шагов, Да (по умолчанию 1 мДа).

    Returns
    -------
    DataFrame
        Копия с колонками ``contested_steps`` (int) и ``ambiguous`` (bool).
    """
    if df is None or df.empty:
        out = df.copy() if df is not None else pd.DataFrame()
        out["contested_steps"] = 0
        out["ambiguous"] = False
        return out

    # Все шаги всех серий → сортировка → кластеры single-linkage по tolerance.
    # (mz, строка, номер ступени) — номер нужен для правила «есть предыдущая ступень»
    steps_lists = (
        list(df["steps_found"])
        if "steps_found" in df.columns
        else [
            [i + 1 for i, mz in enumerate(_lst) if mz is not None]
            for _lst in df["series_mz"]
        ]
    )
    pairs: list[tuple[float, int, int]] = []
    for idx, mz_list in enumerate(df["series_mz"]):
        steps = list(steps_lists[idx])
        for pos, mz in enumerate(mz_list):
            if mz is not None:
                pairs.append(
                    (float(mz), idx, int(steps[pos]) if pos < len(steps) else pos + 1)
                )
    pairs.sort()

    clusters: list[tuple[float, set[int]]] = []
    cur_start = None
    cur_members: set[int] = set()
    prev_mz = None
    for mz, idx, _st in pairs:
        if cur_start is None:
            cur_start = mz
            cur_members = set()
        elif mz - prev_mz > tolerance + 1e-9:
            clusters.append((cur_start, cur_members))
            cur_start = mz
            cur_members = set()
        cur_members.add(idx)
        prev_mz = mz
    if cur_start is not None:
        clusters.append((cur_start, cur_members))

    size_by_start = {start: len(members) for start, members in clusters}

    # Каждой массе — начало её кластера.
    cluster_of: dict[float, float] = {}
    cur_start = None
    prev_mz = None
    for mz, _idx, _st in pairs:
        if cur_start is None or mz - prev_mz > tolerance + 1e-9:
            cur_start = mz
        cluster_of[mz] = cur_start
        prev_mz = mz

    if "steps_found" in df.columns:
        steps_lists = list(df["steps_found"])
    else:
        steps_lists = [
            [i + 1 for i, mz in enumerate(lst) if mz is not None]
            for lst in df["series_mz"]
        ]

    # Правило цепочки: если из претендентов ровно один имеет предыдущую ступень,
    # пик принадлежит ему (остальные претенденты на этот шаг не проходят).
    chain_ok: dict[int, set[float]] = {}
    for start, members in clusters:
        if len(members) < 2:
            continue
        supported = set()
        for mz, row, step in pairs:
            if cluster_of.get(mz) != start:
                continue
            steps = list(steps_lists[row])
            if step - 1 in steps:
                supported.add(row)
        if len(supported) == 1:
            chain_ok[start] = supported

    contested = []
    ambiguous = []
    for row_index, (mz_list, steps) in enumerate(zip(df["series_mz"], steps_lists)):
        flags = []
        for mz in mz_list:
            if mz is None:
                flags.append(False)
                continue
            start = cluster_of.get(float(mz))
            shared = start is not None and size_by_start.get(start, 0) > 1
            if shared and start in chain_ok and row_index not in chain_ok[start]:
                shared = False  # пик принадлежит претенденту с предыдущей ступенью
            flags.append(shared)
        contested.append(int(sum(flags)))
        # важен только последний наблюдаемый пик серии
        last_step = max(steps) if len(steps) else None
        if last_step is None:
            ambiguous.append(False)
            continue
        pos = list(steps).index(last_step)
        ambiguous.append(bool(flags[pos]) if pos < len(flags) else False)

    out = df.copy()
    out["contested_steps"] = contested
    out["ambiguous"] = ambiguous
    return out


def apply_conflicts(df: pd.DataFrame, drop_ambiguous: bool = False) -> pd.DataFrame:
    """Пометить конфликты и (опционально) убрать неоднозначные серии."""
    marked = mark_conflicts(df)
    if drop_ambiguous and not marked.empty:
        marked = marked[~marked["ambiguous"]].reset_index(drop=True)
    return marked
