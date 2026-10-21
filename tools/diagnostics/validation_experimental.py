"""Экспериментальные проверки последних ступеней (persistence/profile).

Не входят в рабочий пайплайн: используются только ablation-диагностикой и
тестами. В `src` оставлены только проверки, которые реально применяются
программой.
"""

from __future__ import annotations

import pandas as pd


def attach_last_steps(
    df: pd.DataFrame,
    raw_path: str,
    *,
    ppm: float = 2.0,
    max_scans: int | None = 16,
    shape_scans: int = 3,
    depth: int = 2,
) -> pd.DataFrame:
    """Метрики profile/персистентности только для последних ``depth`` ступеней.

    Профиль применяется к последнему пику серии; если он сомнителен — к
    предпоследнему (проверка «куда откатиться»). Пропуски (``None``) и
    ступени вне ``series_mz`` игнорируются; для серии без валидных ступеней
    метрики нулевые.
    """
    from src.core.io.raw_profile import validate_masses

    out = df.copy()
    if out.empty:
        for col in (
            "last_persistence",
            "last_shape_ok",
            "last_multi",
            "prev_persistence",
            "prev_ok",
        ):
            out[col] = []
        return out

    # ``steps_found`` — 1-based номера ступеней, ``series_mz`` — позиционный
    # список m/z (позиция ``i`` — ступень ``i + 1``, ``None`` — пропуск).
    masses: set[float] = set()
    picks: list[list[float]] = []
    for _, row in out.iterrows():
        steps = [int(s) for s in row["steps_found"]]
        mz = list(row["series_mz"])
        cand: list[float] = []
        for step in steps[-depth:]:
            pos = step - 1
            if 0 <= pos < len(mz) and mz[pos] is not None:
                cand.append(float(mz[pos]))
        picks.append(cand)
        masses.update(cand)

    met = (
        validate_masses(
            raw_path,
            sorted(masses),
            ppm=ppm,
            max_scans=max_scans,
            shape_scans=shape_scans,
        ).set_index("mass")
        if masses
        else pd.DataFrame()
    )

    def _metric(mass: float | None, column: str, default):
        if mass is None or mass not in met.index:
            return default
        return met.loc[mass][column]

    last_p, last_ok, last_multi, prev_p, prev_ok = [], [], [], [], []
    for cand in picks:
        last = cand[-1] if cand else None
        prev = cand[-2] if len(cand) > 1 else None
        last_p.append(float(_metric(last, "persistence", 0.0)))
        last_ok.append(bool(_metric(last, "shape_ok", False)))
        last_multi.append(bool(_metric(last, "multi", False)))
        prev_p.append(float(_metric(prev, "persistence", 0.0)))
        prev_ok.append(bool(_metric(prev, "shape_ok", False)))
    out["last_persistence"] = last_p
    out["last_shape_ok"] = last_ok
    out["last_multi"] = last_multi
    out["prev_persistence"] = prev_p
    out["prev_ok"] = prev_ok
    return out
