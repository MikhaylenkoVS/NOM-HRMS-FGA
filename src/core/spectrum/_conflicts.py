"""Разрешение конфликтов: один наблюдаемый пик — несколько серий (P3).

В плотном NOM-спектре один и тот же пик дериватизата может оказаться шагом у
нескольких исходных соединений (и на разных ступенях). Раньше каждый пик
исходника искался независимо, поэтому такие «пики на все руки» порождали
ложные серии.

Здесь конфликт только **помечается** (и, по желанию, серии отбрасываются):
шаги всех серий группируются в кластеры по m/z (single-linkage в пределах
окна), и если кластер используется более чем одной серией, шаг считается
спорным. Ничего не удаляется «молча» — неоднозначность остаётся в колонках
``contested_steps`` и ``ambiguous``.
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
    pairs: list[tuple[float, int]] = []
    for idx, mz_list in enumerate(df["series_mz"]):
        for mz in mz_list:
            if mz is not None:
                pairs.append((float(mz), idx))
    pairs.sort()

    clusters: list[tuple[float, set[int]]] = []
    cur_start = None
    cur_members: set[int] = set()
    prev_mz = None
    for mz, idx in pairs:
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
    for mz, _idx in pairs:
        if cur_start is None or mz - prev_mz > tolerance + 1e-9:
            cur_start = mz
        cluster_of[mz] = cur_start
        prev_mz = mz

    contested = []
    for mz_list in df["series_mz"]:
        n = 0
        for mz in mz_list:
            if mz is None:
                continue
            start = cluster_of.get(float(mz))
            if start is not None and size_by_start.get(start, 0) > 1:
                n += 1
        contested.append(n)

    out = df.copy()
    out["contested_steps"] = contested
    out["ambiguous"] = [c > 0 for c in contested]
    return out


def apply_conflicts(df: pd.DataFrame, drop_ambiguous: bool = False) -> pd.DataFrame:
    """Пометить конфликты и (опционально) убрать неоднозначные серии."""
    marked = mark_conflicts(df)
    if drop_ambiguous and not marked.empty:
        marked = marked[~marked["ambiguous"]].reset_index(drop=True)
    return marked
