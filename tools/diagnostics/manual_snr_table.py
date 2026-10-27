"""Таблица I(mu)/локальный шум для якорей из работы Тарабрина.

Строки — 22 ручных якоря F14/F16 (11+11), столбцы — степени 1..10.
Для каждого mu = m0(брутто) + n*delta берётся интенсивность пика из
усреднённого спектра дериватизата. Основной локальный шум — MAD
центроидных интенсивностей в ±0.2 Да (без ±0.02 Да вокруг mu);
дополнительно в CSV сохраняется шум RAW-профиля и ratio_raw.

Запуск требует python-docx (глобальный Python):
  python tools/diagnostics/manual_snr_table.py
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from docx import Document

from src.core.io.raw_profile import (
    _open_raw,
    _shape_metrics,
    scan_numbers,
    scan_profile,
)
from src.core.spectrum import load_spectrum
from src.core.spectrum._local_noise import local_noise_mad_sorted
from src.core.spectrum._series import _theor_ion_mass_cached
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.configs import PIPELINE

DOCX = Path(
    "C:/Users/mvs/Work/Лаборатория/Аналитика/Тарабрин аналитика альфа-версия.docx"
)
SETS = {
    "Fulvagra F14": {
        "src": "data/real_sets/Fulvagra F14/Fulvagra_prep HPLC_Fr14_ESI_1e6_480k_128_m-s_averaged.json",
        "dmet_raw": "data/real_sets/Fulvagra F14/Fulvagra_prep HPLC_FR14_CD3OD mod_ESI_1e6_480k_128_m-s.raw",
        "dmet_avg": "data/real_sets/Fulvagra F14/Fulvagra_prep HPLC_FR14_CD3OD mod_ESI_1e6_480k_128_m-s_averaged.json",
        "dacet_raw": "data/real_sets/Fulvagra F14/Fulvagra_prep HPLC_FR14_AC-D4_ESI_1e6_480k_128_m-s.raw",
        "dacet_avg": "data/real_sets/Fulvagra F14/Fulvagra_prep HPLC_FR14_AC-D4_ESI_1e6_480k_128_m-s_averaged.json",
        "mass_table": 0,
    },
    "Fulvagra F16": {
        "src": "data/real_sets/Fulvagra F16/Fulvagra_prep HPLC_Fr16_ESI_1e6_480k_128_m-s_averaged.json",
        "dmet_raw": "data/real_sets/Fulvagra F16/Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s_.raw",
        "dmet_avg": "data/real_sets/Fulvagra F16/Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s__averaged.json",
        "dacet_raw": "data/real_sets/Fulvagra F16/Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s.raw",
        "dacet_avg": "data/real_sets/Fulvagra F16/Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s_averaged.json",
        "mass_table": 1,
    },
}
DELTAS = {"CD3": 17.03448, "CD3CO": 45.02939}
MAX_N = 10
PPM = 2.0
SNR_MIN = 3.0


def _clean(value: str) -> str:
    return " ".join(value.replace("\xa0", " ").split())


def _manual_anchors(doc: Document, table_index: int) -> list[dict]:
    out = []
    for row in doc.tables[table_index].rows[2:]:
        c = [_clean(x.text) for x in row.cells]
        if len(c) >= 3 and c[0]:
            out.append({"number": c[0], "mass": float(c[1]), "formula": c[2]})
    return out


def _nearest_peak(table, mass: float, ppm=PPM):
    m = np.asarray(table["mass"], dtype=float)
    i = np.asarray(table["intensity"], dtype=float)
    order = np.argsort(m)
    m, i = m[order], i[order]
    tol = abs(mass) * ppm * 1e-6
    lo = int(np.searchsorted(m, mass - tol, side="left"))
    hi = int(np.searchsorted(m, mass + tol, side="right"))
    if hi <= lo:
        return None
    k = lo + int(np.argmax(i[lo:hi]))
    return float(m[k]), float(i[k])


def _local_noise_from_averaged(table, mass: float) -> float:
    """Локальный шум: MAD в ±0.2 Да, исключая ±0.02 Да вокруг mass."""
    m = np.asarray(table["mass"], dtype=float)
    i = np.asarray(table["intensity"], dtype=float)
    order = np.argsort(m)
    return local_noise_mad_sorted(m[order], i[order], mass)


def _raw_noise(raw_path: str, masses: list[float], shape_scans: int = 3) -> dict:
    """Локальный шум по RAW-профилям: медиана sigma по нескольким сканам."""
    raw = _open_raw(raw_path)
    try:
        scans = scan_numbers(raw, max_scans=shape_scans)
        sigmas = {m: [] for m in masses}
        apexes = {m: [] for m in masses}
        for scan in scans:
            mz, inten = scan_profile(raw, scan)
            if mz.size == 0:
                continue
            for mass in masses:
                met = _shape_metrics(mz, inten, float(mass), 0.02)
                if met.get("present"):
                    sig = float(met.get("noise_sigma") or 0.0)
                    if sig > 0:
                        sigmas[mass].append(sig)
                    apexes[mass].append(float(met.get("apex") or 0.0))
        return {
            m: {
                "noise": float(np.median(sigmas[m])) if sigmas[m] else 0.0,
                "apex": float(np.max(apexes[m])) if apexes[m] else 0.0,
            }
            for m in masses
        }
    finally:
        raw.Dispose()


def _tables(rows: pd.DataFrame) -> str:
    lines = []
    for deriv in ("CD3", "CD3CO"):
        sub = rows[rows["derivative"] == deriv]
        if sub.empty:
            continue
        pivot = sub.pivot_table(
            index=["dataset", "number", "manual_mass", "formula"],
            columns="n",
            values="ratio",
            aggfunc="first",
        )

        # Естественный порядок 14-1, 14-2, ..., 16-10.
        def _anchor_key(item):
            dataset, number = item[0], item[1]
            m = re.search(r"(\d+)$", str(number))
            return (dataset, int(m.group(1)) if m else 0)

        pivot = pivot.reindex(sorted(pivot.index, key=_anchor_key))
        lines += [f"## {deriv}", ""]
        lines.append(
            "| Сет | № | m/z | Формула | "
            + " | ".join(str(n) for n in range(1, MAX_N + 1))
            + " |"
        )
        lines.append(
            "|---|---|---:|---|" + "|".join("---:" for _ in range(MAX_N)) + "|"
        )
        for idx, row in pivot.iterrows():
            dataset, number, mass, formula = idx
            vals = []
            for n in range(1, MAX_N + 1):
                value = row.get(n, np.nan)
                vals.append(
                    "—"
                    if pd.isna(value) or float(value) < SNR_MIN
                    else f"{float(value):.1f}"
                )
            lines.append(
                f"| {dataset} | {number} | {mass:.5f} | {formula} | "
                + " | ".join(vals)
                + " |"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docx", default=str(DOCX))
    ap.add_argument("--out", default="output/manual_snr_table")
    args = ap.parse_args()
    doc = Document(args.docx)
    ion_mode = _ion_mode_from_sign(PIPELINE.run_pipeline_defaults["sign"])
    records = []
    for dataset, cfg in SETS.items():
        anchors = _manual_anchors(doc, cfg["mass_table"])
        specs = {
            "CD3": load_spectrum(cfg["dmet_avg"]),
            "CD3CO": load_spectrum(cfg["dacet_avg"]),
        }
        raw_paths = {"CD3": cfg["dmet_raw"], "CD3CO": cfg["dacet_raw"]}
        for deriv, delta in DELTAS.items():
            masses = []
            for a in anchors:
                try:
                    m0 = _theor_ion_mass_cached(a["formula"], ion_mode)
                except Exception:
                    m0 = a["mass"]
                for n in range(1, MAX_N + 1):
                    masses.append(m0 + n * delta)
            noise = _raw_noise(raw_paths[deriv], masses)
            for a in anchors:
                try:
                    m0 = _theor_ion_mass_cached(a["formula"], ion_mode)
                except Exception:
                    m0 = a["mass"]
                for n in range(1, MAX_N + 1):
                    mu = m0 + n * delta
                    peak = _nearest_peak(specs[deriv].table, mu)
                    # Основная оценка: локальный шум по усреднённому
                    # центроидному спектру (MAD в ±0.2 Да, без ±0.02 Да).
                    sigma = _local_noise_from_averaged(specs[deriv].table, mu)
                    sigma_raw = float(noise[mu]["noise"])
                    intensity = peak[1] if peak is not None else None
                    ratio = (
                        float(intensity) / sigma
                        if intensity is not None and sigma > 0
                        else np.nan
                    )
                    passed = bool(np.isfinite(ratio) and ratio >= SNR_MIN)
                    ratio_raw = (
                        float(intensity) / sigma_raw
                        if intensity is not None and sigma_raw > 0
                        else np.nan
                    )
                    records.append(
                        {
                            "dataset": dataset,
                            "number": a["number"],
                            "manual_mass": a["mass"],
                            "formula": a["formula"],
                            "derivative": deriv,
                            "n": n,
                            "mu": mu,
                            "peak_mz": peak[0] if peak is not None else None,
                            "intensity": intensity,
                            "local_noise": sigma,
                            "ratio": ratio,
                            "passed": passed,
                            "local_noise_raw": sigma_raw,
                            "ratio_raw": ratio_raw,
                        }
                    )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(records)
    df.to_csv(out / "manual_snr_table.csv", index=False)
    (out / "manual_snr_table.json").write_text(
        json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    md = [
        "# I(mu)/локальный шум для якорей Тарабрина",
        "",
        "`n` — степень дериватизации; `mu = m0(брутто) + n·Δ`.",
        "`mu` — теоретическая масса; интенсивность — пик в усреднённом",
        "спектре дериватизата в окне 2 ppm; локальный шум — MAD",
        "центроидных интенсивностей в ±0.2 Да, без ±0.02 Да вокруг `mu`.",
        "`—` — пик не найден или `I/шум < 3` (жёсткий критерий S/N).",
        "В CSV остаются исходные `ratio`, `ratio_raw` и флаг `passed`.",
        "",
        _tables(df),
    ]
    (out / "manual_snr_table.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"written: {out}")


if __name__ == "__main__":
    main()
