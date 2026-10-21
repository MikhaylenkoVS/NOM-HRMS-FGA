"""Варианты жёсткого вычитания по profile-статусам (F16, restricted assign)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from ablation_f16 import DECOYS, REAL

from src.configs import CHEM, PIPELINE
from src.core.spectrum import Spectrum, find_series
from src.core.spectrum._decoy import DECOY_SEED, decoy_shifts
from src.core.spectrum._validate import attach_fdr

H = 0.00030
TAG = "00030"


def main() -> None:
    cache = pd.read_pickle("D:/Temp/User/nom_restrict_cache/restricted.pkl")
    src, dmet, dacet = cache["src"], cache["dmet"], cache["dacet"]
    pos = pd.read_pickle("D:/Temp/User/restricted_profile_positions.pkl")
    src_tab = src.table
    sm = np.sort(src_tab.loc[src_tab["assign"].astype(bool), "mass"].to_numpy(float))

    defaults = PIPELINE.run_pipeline_defaults
    kw = dict(
        ppm_tol=defaults["ppm_tol"],
        max_groups=10,
        max_gaps=0,
        require_first_step=True,
        significance_level=defaults["significance_level"],
    )

    out = {}
    for deriv, spec, delta in (
        ("cd3", dmet, CHEM.derivatization_shifts["delta_cd3"]),
        ("cd3co", dacet, CHEM.derivatization_shifts["delta_cd3co"]),
    ):
        sub = pos[pos["deriv"] == deriv].copy()
        st = f"status_{TAG}"
        pm = f"peak_mz_{TAG}"
        # расстояние до ближайшего исходного пика
        d_b = np.full(len(sub), np.nan)
        for i, p in enumerate(sub[pm].to_numpy(float)):
            if p != p:
                continue
            j = int(np.searchsorted(sm, p))
            cand = [k for k in (j - 1, j, j + 1) if 0 <= k < len(sm)]
            if cand:
                k = min(cand, key=lambda z: abs(sm[z] - p))
                d_b[i] = abs(sm[k] - p)
        sub["d_mu"] = np.abs(sub[pm].to_numpy(float) - sub["mu"].to_numpy(float))
        sub["d_b"] = d_b

        masses = spec.table["mass"].to_numpy(float)
        masks = {
            "unconf+unrel": sub[st].isin(["unconfirmed", "unreliable"]).to_numpy(),
            "unconf_only": (sub[st] == "unconfirmed").to_numpy(),
            "closer_B": (
                sub[st].isin(["unconfirmed", "unreliable"]) & (sub["d_b"] < sub["d_mu"])
            ).to_numpy(),
            "closer_B_margin": (
                sub[st].isin(["unconfirmed", "unreliable"])
                & (sub["d_b"] + 0.0001 < sub["d_mu"])
            ).to_numpy(),
        }
        out[deriv] = {}
        for name, mask in masks.items():
            drop = np.zeros(len(masses), dtype=bool)
            for p in sub.loc[mask, pm].to_numpy(float):
                if p != p:
                    continue
                j = int(np.searchsorted(masses, p))
                cand = [k for k in (j - 1, j, j + 1) if 0 <= k < len(masses)]
                if cand:
                    k = min(cand, key=lambda z: abs(masses[z] - p))
                    if abs(masses[k] - p) <= 0.01:
                        drop[k] = True
            filtered = Spectrum(table=spec.table.loc[~drop].reset_index(drop=True))
            target = find_series(src, filtered, delta, **kw)
            shifts = decoy_shifts(delta, k=DECOYS, seed=DECOY_SEED)
            decoys = [find_series(src, filtered, delta + sh, **kw) for sh in shifts]
            scored = attach_fdr(target, decoys)
            keep = scored[scored["fdr_significant"]]
            out[deriv][name] = {
                "removed": int(drop.sum()),
                "retained": int(len(keep)),
                "mean_len_retained": (
                    round(float(keep["steps_found"].map(len).mean()), 3)
                    if len(keep)
                    else 0.0
                ),
                "median_len_retained": (
                    float(keep["steps_found"].map(len).median()) if len(keep) else 0.0
                ),
            }
            print(deriv, name, out[deriv][name], flush=True)
    Path("D:/Temp/User/hard_variants_f16.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
