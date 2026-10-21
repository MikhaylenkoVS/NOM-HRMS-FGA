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
