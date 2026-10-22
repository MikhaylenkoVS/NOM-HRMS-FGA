"""Референс: длина серий без фильтров (F16).

Шаг считается подтверждённым, если в окне ожидаемой m/z есть хотя бы один
пик дериватизата. Ни profile, ни вычитание исходника, ни FDR, ни
reliability-политика не применяются. Серия обрывается на первом пропуске.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ablation_f16 import REAL

from src.configs import CHEM, PIPELINE
from src.core.domain.molecule import parse_formula
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.spectrum._series import _theor_ion_mass_cached

WINDOWS = (
    ("abs_0.0003", "abs", 0.00030),
    ("abs_0.0005", "abs", 0.00050),
    ("ppm_0.5", "ppm", 0.5),
    ("ppm_1.0", "ppm", 1.0),
    ("ppm_3.0", "ppm", 3.0),
    ("ppm_5.0", "ppm", 5.0),
)


def build_anchors(src):
    t = src.table
    a = t.loc[t["assign"].astype(bool) & t["brutto"].notna()].copy()
    ion_mode = _ion_mode_from_sign(PIPELINE.run_pipeline_defaults["sign"])
    m0 = []
    for mass, brutto in zip(a["mass"].to_numpy(float), a["brutto"].astype(str)):
        try:
            m = _theor_ion_mass_cached(brutto, ion_mode)
            if abs(m - mass) / mass > 0.001:
                m = mass
        except Exception:
            m = mass
        m0.append(float(m))
    a["m0"] = m0
    a["O"] = [int(parse_formula(str(b)).get("O", 0)) for b in a["brutto"].astype(str)]
    a = a[a["O"] >= 1].reset_index(drop=True)
    a["anchor_idx"] = np.arange(len(a))
    return a


def count_window(sorted_mz, mu, h):
    lo = np.searchsorted(sorted_mz, mu - h, side="left")
    hi = np.searchsorted(sorted_mz, mu + h, side="right")
    return int(hi - lo)


def main() -> None:
    cache = pd.read_pickle("D:/Temp/User/nom_restrict_cache/restricted.pkl")
    src, dmet, dacet = cache["src"], cache["dmet"], cache["dacet"]
    anchors = build_anchors(src)
    print("anchors", len(anchors), flush=True)

    report = {
        "dataset": "Fulvagra F16",
        "anchors": int(len(anchors)),
        "max_deg": 10,
        "source": "restricted assign, O>=1",
        "filters": "none: no profile, no source subtraction, no FDR, no reliability",
        "windows": [],
    }
    for deriv, spec, delta in (
        ("cd3", dmet, CHEM.derivatization_shifts["delta_cd3"]),
        ("cd3co", dacet, CHEM.derivatization_shifts["delta_cd3co"]),
    ):
        dmz = np.sort(spec.table["mass"].to_numpy(float))
        for name, kind, value in WINDOWS:
            lengths = []
            max_deg_seen = 0
            for a in anchors.itertuples(index=False):
                length = 0
                for n in range(1, min(10, int(a.O)) + 1):
                    mu = float(a.m0) + n * delta
                    h = value if kind == "abs" else mu * value * 1e-6
                    if count_window(dmz, mu, h) >= 1:
                        length = n
                    else:
                        break
                lengths.append(length)
                max_deg_seen = max(max_deg_seen, length)
            arr = np.asarray(lengths)
            pos = arr[arr > 0]
            report["windows"].append(
                {
                    "deriv": deriv,
                    "window": name,
                    "mean_all": round(float(arr.mean()), 3),
                    "mean_positive": round(float(pos.mean()), 3) if pos.size else 0.0,
                    "median_all": float(np.median(arr)),
                    "median_positive": float(np.median(pos)) if pos.size else 0.0,
                    "share_zero": round(float((arr == 0).mean()), 4),
                    "share_ge2": round(float((arr >= 2).mean()), 4),
                    "share_ge4": round(float((arr >= 4).mean()), 4),
                    "max": int(arr.max()),
                    "n_positive": int(pos.size),
                    "hist": {str(k): int((arr == k).sum()) for k in range(0, 11)},
                }
            )
            print(
                deriv,
                name,
                "mean_all",
                round(float(arr.mean()), 3),
                "mean_pos",
                round(float(pos.mean()), 3) if pos.size else 0.0,
                "zero",
                round(float((arr == 0).mean()), 4),
                "max",
                int(arr.max()),
                flush=True,
            )
    Path("D:/Temp/User/reference_length_no_filters.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("saved")


if __name__ == "__main__":
    main()
