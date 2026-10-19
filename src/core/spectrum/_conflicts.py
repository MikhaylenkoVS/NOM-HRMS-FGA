"""Разрешение конфликтов: один наблюдаемый пик — несколько серий (P3).

В плотном NOM-спектре один и тот же пик дериватизата может оказаться шагом у
нескольких исходных соединений (и на разных ступенях). Раньше каждый пик
исходника искался независимо, поэтому такие «пики на все руки» порождали
ложные серии.

Правило (уточнено): конфликт важен только для **последнего наблюдаемого пика
серии**. Если спорный шаг не последний, а следующая ступень найдена и
бесспорна, серия не считается неоднозначной: цепочка продолжается уникальным
пиком. Поэтому ``ambiguous = contested[last_step]``.

Правило цепочки: если в кластере ровно один претендент имеет предыдущую
ступень, пик принадлежит ему; для остальных претендентов шаг спорный.

Химическая правдоподобность: по умолчанию в конфликтах участвуют только
серии с правдоподобной NOM-формулой (CHNOPS, отношения элементов, DBE; см.
``_formula_check.is_plausible_brutto``). Неправдоподобная серия не может
претендовать на пик и не делает другие серии ``ambiguous``, но остаётся в
выдаче — её отсекают другие проверки (формула/FDR).

ВАЖНО: сравнивать нужно только шаги **одной и той же** производной
(дейтерометилирование с дейтерометилированием, дейтероацилирование с
дейтероацилированием). Функция принимает один DataFrame — по одному на
производную, — поэтому смешивание невозможно по построению.
"""

from __future__ import annotations

import pandas as pd


def _valid_flags(df: pd.DataFrame, valid) -> list[bool]:
    """Маска серий, участвующих в конфликтах.

    ``valid=None`` — считаем правдоподобность по колонке ``brutto`` (если она
    есть), иначе все серии считаются правдоподобными.
    """
    n = len(df)
    if valid is None:
        if "brutto" not in df.columns:
            return [True] * n
        from ._formula_check import is_plausible_brutto

        return [bool(is_plausible_brutto(str(b))[0]) for b in df["brutto"]]
    flags = [bool(v) for v in valid]
    if len(flags) != n:
        raise ValueError(f"valid: ожидалось {n} значений, получено {len(flags)}")
    return flags


def analyze_conflicts(
    df: pd.DataFrame, tolerance: float = 0.001, valid=None
) -> list[dict]:
    """Собрать кластеры пиков, которые делят две и более серии.

    Parameters
    ----------
    df : DataFrame
        Результат ``find_series`` с колонкой ``series_mz``.
    tolerance : float
        Окно группировки шагов, Да (по умолчанию 1 мДа).
    valid : sequence of bool, optional
        Маска серий, участвующих в конфликтах. ``None`` — только серии с
        правдоподобной формулой (по колонке ``brutto``), иначе все.

    Returns
    -------
    list of dict
        Каждый кластер: ``start`` (минимальный m/z), ``end`` (максимальный),
        ``members`` (список ``{"row", "step", "mz"}``), ``supported`` (строки
        с предыдущей ступенью) и ``owner`` (строка-владелец или ``None``).
    """
    if df is None or len(df) == 0:
        return []
    flags = _valid_flags(df, valid)

    # ``series_mz`` — позиционный список: позиция ``i`` соответствует ступени
    # ``i + 1``, ``None`` — пропуск. Номер ступени берём из позиции, а не из
    # ``steps_found``: списки могут иметь разную длину при пропусках.
    pairs: list[tuple[float, int, int]] = []  # (mz, строка, номер ступени)
    steps_by_row: list[list[int]] = []
    for idx, mz_list in enumerate(df["series_mz"]):
        steps: list[int] = []
        if flags[idx]:
            for pos, mz in enumerate(mz_list):
                if mz is not None:
                    step = pos + 1
                    pairs.append((float(mz), idx, step))
                    steps.append(step)
        steps_by_row.append(steps)
    pairs.sort()

    clusters: list[dict] = []
    cur: dict | None = None
    prev_mz = None
    for mz, row, step in pairs:
        if cur is None or mz - prev_mz > tolerance + 1e-9:
            cur = {"start": mz, "end": mz, "members": []}
            clusters.append(cur)
        cur["end"] = mz
        cur["members"].append({"row": row, "step": step, "mz": mz})
        prev_mz = mz

    result: list[dict] = []
    for cluster in clusters:
        rows = {m["row"] for m in cluster["members"]}
        if len(rows) < 2:
            continue
        shared_steps: dict[int, list[int]] = {}
        for m in cluster["members"]:
            shared_steps.setdefault(m["row"], []).append(m["step"])
        supported = sorted(
            row
            for row, steps in shared_steps.items()
            if any(step - 1 in steps_by_row[row] for step in steps)
        )
        cluster["supported"] = supported
        cluster["owner"] = supported[0] if len(supported) == 1 else None
        result.append(cluster)
    return result


def mark_conflicts(
    df: pd.DataFrame, tolerance: float = 0.001, valid=None
) -> pd.DataFrame:
    """Пометить серии, у которых есть шаги, используемые другими сериями.

    Parameters
    ----------
    df : DataFrame
        Результат ``find_series`` с колонкой ``series_mz`` (список m/z).
    tolerance : float
        Окно группировки шагов, Да (по умолчанию 1 мДа).
    valid : sequence of bool, optional
        Маска серий, участвующих в конфликтах. ``None`` — только серии с
        правдоподобной NOM-формулой (колонка ``brutto``), иначе все.

    Returns
    -------
    DataFrame
        Копия с колонками ``contested_steps`` (int) и ``ambiguous`` (bool).
        ``contested_steps`` — число шагов, которые серия проиграла владельцу
        пика; ``ambiguous`` — проигран именно последний наблюдаемый шаг.
        Неправдоподобные серии не участвуют: у них обе колонки нулевые.
    """
    if df is None or df.empty:
        out = df.copy() if df is not None else pd.DataFrame()
        out["contested_steps"] = 0
        out["ambiguous"] = False
        return out
    valid_flags = _valid_flags(df, valid)

    clusters = analyze_conflicts(df, tolerance, valid=valid_flags)
    cluster_of: dict[float, float] = {}
    size_by_start: dict[float, int] = {}
    owner: dict[float, int] = {}
    for cluster in clusters:
        start = cluster["start"]
        size_by_start[start] = len({m["row"] for m in cluster["members"]})
        if cluster["owner"] is not None:
            owner[start] = cluster["owner"]
        for m in cluster["members"]:
            cluster_of[m["mz"]] = start

    contested: list[int] = []
    ambiguous: list[bool] = []
    for row_index, mz_list in enumerate(df["series_mz"]):
        if not valid_flags[row_index]:
            # неправдоподобная формула не участвует в конфликтах
            contested.append(0)
            ambiguous.append(False)
            continue
        flags: list[bool] = []
        for mz in mz_list:
            if mz is None:
                flags.append(False)
                continue
            start = cluster_of.get(float(mz))
            shared = start is not None and size_by_start.get(start, 0) > 1
            if shared and start in owner:
                # пик принадлежит владельцу; спорен только для остальных
                shared = row_index != owner[start]
            flags.append(shared)
        contested.append(int(sum(flags)))
        # важен только последний наблюдаемый пик серии: в ``series_mz`` он
        # последний не-None (серия обрезана по последней найденной ступени).
        last_pos = next(
            (pos for pos in range(len(flags) - 1, -1, -1) if mz_list[pos] is not None),
            None,
        )
        ambiguous.append(bool(flags[last_pos]) if last_pos is not None else False)
    out = df.copy()
    out["contested_steps"] = contested
    out["ambiguous"] = ambiguous
    return out


def apply_conflicts(
    df: pd.DataFrame, drop_ambiguous: bool = False, valid=None
) -> pd.DataFrame:
    """Пометить конфликты и (опционально) убрать неоднозначные серии."""
    marked = mark_conflicts(df, valid=valid)
    if drop_ambiguous and not marked.empty:
        marked = marked[~marked["ambiguous"]].reset_index(drop=True)
    return marked
