"""Валидация серий: FDR, формула, форма/персистентность, конфликты, статусы.

Все проверки — **опциональные**: каждая добавляет колонку и может быть
использована как фильтр. Модуль не пересчитывает серии, а обогащает уже
найденные результаты (минимум лишних вычислений).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.core.spectrum._conflicts import mark_conflicts
from src.core.spectrum._decoy import fdr_table, q_values
from src.core.spectrum._formula_check import check_series_formula


def attach_fdr(
    df: pd.DataFrame, decoy_frames: list[pd.DataFrame], alpha: float = 0.05
) -> pd.DataFrame:
    """Добавить q-value по ансамблю decoy-серий и флаг ``fdr_significant``."""
    out = df.copy()
    if out.empty:
        out["q_value"] = []
        out["fdr_significant"] = []
        return out
    decoy_lengths = [
        frame["n_groups"].astype(int).tolist()
        for frame in decoy_frames
        if frame is not None
    ]
    table = fdr_table(
        out["n_groups"].astype(int).tolist(),
        decoy_lengths,
        min_length=1,
        max_length=int(out["n_groups"].max()),
    )
    out["q_value"] = q_values(out["n_groups"].astype(int).tolist(), table)
    out["fdr_significant"] = out["q_value"] <= alpha
    return out


def attach_formula_check(
    df: pd.DataFrame, group: str, counts_by_brutto: dict[str, dict]
) -> pd.DataFrame:
    """Проверить химическую допустимость продукта для каждой серии."""
    out = df.copy()
    ok_flags, reasons = [], []
    for _, row in out.iterrows():
        counts = counts_by_brutto.get(str(row.get("brutto", "")))
        if not counts:
            ok_flags.append(False)
            reasons.append("нет состава")
            continue
        res = check_series_formula(counts, int(row["n_groups"]), group)
        ok_flags.append(bool(res["ok"]))
        reasons.append(res["reason"])
    out["formula_ok"] = ok_flags
    out["formula_reason"] = reasons
    return out


def attach_profile(
    df: pd.DataFrame,
    raw_path: str,
    *,
    ppm: float = 2.0,
    max_scans: int | None = 16,
    shape_scans: int = 3,
    min_snr: float = 3.0,
) -> pd.DataFrame:
    """Проверить шаги серий по сырому RAW: персистентность, S/N, форма.

    Профиль читается один раз на скан; проверяются только уникальные m/z шагов.
    """
    from src.core.io.raw_profile import validate_masses

    out = df.copy()
    masses = sorted(
        {float(m) for lst in out["series_mz"] for m in lst if m is not None}
    )
    if not masses:
        out["persistence"] = 0.0
        out["shape_ok"] = False
        out["snr"] = np.nan
        return out

    met = validate_masses(
        raw_path,
        masses,
        ppm=ppm,
        max_scans=max_scans,
        shape_scans=shape_scans,
        min_snr=min_snr,
    ).set_index("mass")

    pers, shape, snr_min = [], [], []
    for lst in out["series_mz"]:
        idx = [float(m) for m in lst if m is not None and float(m) in met.index]
        if not idx:
            pers.append(0.0)
            shape.append(False)
            snr_min.append(np.nan)
            continue
        sub = met.loc[idx]
        pers.append(float(sub["persistence"].min()))
        shape.append(bool(sub["shape_ok"].all()))
        snr_min.append(float(sub["snr"].min()))
    out["persistence"] = pers
    out["shape_ok"] = shape
    out["snr"] = snr_min
    return out


def attach_conflicts(df: pd.DataFrame) -> pd.DataFrame:
    """Пометить серии со спорными шагами (P3)."""
    return mark_conflicts(df)


def add_status(df: pd.DataFrame) -> pd.DataFrame:
    """Итоговый статус серии по всем доступным проверкам.

    Приоритет: rejected_noise → ambiguous → possible_random_match → supported.
    """
    out = df.copy()
    statuses = []
    for _, row in out.iterrows():
        if "shape_ok" in out.columns and not bool(row.get("shape_ok", True)):
            statuses.append("rejected_noise")
        elif "ambiguous" in out.columns and bool(row.get("ambiguous", False)):
            statuses.append("ambiguous")
        elif not bool(row.get("significant", True)):
            statuses.append("possible_random_match")
        elif "fdr_significant" in out.columns and not bool(
            row.get("fdr_significant", True)
        ):
            statuses.append("possible_random_match")
        elif "formula_ok" in out.columns and not bool(row.get("formula_ok", True)):
            statuses.append("real_peak_unrelated")
        elif "persistence" in out.columns and float(row.get("persistence", 1.0)) < 0.5:
            statuses.append("possible_random_match")
        else:
            statuses.append("supported")
    out["status"] = statuses
    return out


def summarize(df: pd.DataFrame) -> dict:
    """Сводка по сериям: число, среднее, значимые, статусы."""
    if df is None or df.empty:
        return {"n": 0, "mean": 0.0, "sig_n": 0, "statuses": {}}
    n_groups = df["n_groups"].astype(int)
    sig = df["significant"].astype(bool) if "significant" in df else None
    return {
        "n": int(len(df)),
        "mean": round(float(n_groups.mean()), 3),
        "median": float(n_groups.median()),
        "sig_n": int(sig.sum()) if sig is not None else 0,
        "sig_mean": (
            round(float(n_groups[sig].mean()), 3)
            if sig is not None and sig.any()
            else 0.0
        ),
        "statuses": (
            df["status"].value_counts().to_dict() if "status" in df.columns else {}
        ),
    }


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
    предпоследнему (проверка «куда откатиться»). Поэтому считать метрики для
    всех шагов не нужно.
    """
    from src.core.io.raw_profile import validate_masses

    out = df.copy()
    if out.empty:
        for col in ("last_persistence", "last_shape_ok", "last_multi", "prev_ok"):
            out[col] = []
        return out

    # Для каждой серии — последний и (если есть) предыдущий найденный шаг.
    masses: set[float] = set()
    picks: list[list[float]] = []
    for _, row in out.iterrows():
        steps = list(row["steps_found"])
        mz = list(row["series_mz"])
        cand = [float(mz[list(range(len(mz))).index(s)]) for s in steps[-depth:]]
        picks.append(cand)
        masses.update(cand)

    met = validate_masses(
        raw_path, sorted(masses), ppm=ppm, max_scans=max_scans, shape_scans=shape_scans
    ).set_index("mass")

    last_p, last_ok, last_multi, prev_ok = [], [], [], []
    for cand in picks:
        last = met.loc[cand[-1]] if cand[-1] in met.index else None
        prev = met.loc[cand[-2]] if len(cand) > 1 and cand[-2] in met.index else None
        last_p.append(float(last["persistence"]) if last is not None else 0.0)
        last_ok.append(bool(last["shape_ok"]) if last is not None else False)
        last_multi.append(bool(last["multi"]) if last is not None else False)
        prev_ok.append(bool(prev["shape_ok"]) if prev is not None else False)
    out["last_persistence"] = last_p
    out["last_shape_ok"] = last_ok
    out["last_multi"] = last_multi
    out["prev_ok"] = prev_ok
    return out


def trim_to_confirmed_last(
    df: pd.DataFrame,
    *,
    persistence_min: float = 0.5,
    min_length: int = 1,
) -> pd.DataFrame:
    """Откатить серию к последней подтверждённой ступени.

    Последняя ступень считается подтверждённой, если ``last_persistence`` ≥ порога
    и ``last_shape_ok``. Иначе — проверяется предпоследняя (``prev_ok`` +
    «у неё была нормальная персистентность» неизвестна, поэтому требуется
    ``prev_ok`` иначе серия отбрасывается). Результат: новая длина ``n_groups``
    и ``trimmed_steps``.
    """
    out = df.copy()
    new_n, trimmed = [], []
    for _, row in out.iterrows():
        n = int(row["n_groups"])
        last_ok = float(row["last_persistence"]) >= persistence_min and bool(
            row["last_shape_ok"]
        )
        if last_ok:
            new_n.append(n)
            trimmed.append(0)
        elif n - 1 >= max(1, min_length) and bool(row.get("prev_ok", False)):
            new_n.append(n - 1)
            trimmed.append(1)
        else:
            new_n.append(0)
            trimmed.append(n)
    out["trimmed_steps"] = trimmed
    out["n_groups"] = new_n
    out = out[out["n_groups"] >= max(1, min_length)].reset_index(drop=True)
    return out
