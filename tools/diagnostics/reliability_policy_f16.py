"""Политика reliability v2 (F16): без FDR, без prefix.

reliable:
  * n_deriv >= 1 и n_src == 0; или
  * n_deriv >= 1, n_src >= 1 и profile в объединённой области разрешает
    >= 1 + n_src пиков.

ambiguous:
  * n_deriv >= 1, n_src >= 1, profile разрешает < 1 + n_src пиков.

absent:
  * n_deriv == 0.

Подтверждённая длина: максимальный n в непрерывном префиксе (до первого
absent), для которого шаг reliable; ambiguous на промежуточных шагах
допустимы. Неподтверждённая длина: максимальный ambiguous n, если он больше
подтверждённой.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ablation_f16 import REAL

from src.configs import CHEM, PIPELINE
from src.core.domain.molecule import parse_formula
from src.core.io.raw_profile import _open_raw, scan_numbers, scan_profile
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.spectrum._series import _theor_ion_mass_cached

from profile_resolve import profile_peaks

WINDOWS = (
    0.00010,
    0.00015,
    0.00020,
    0.00025,
    0.00030,
    0.00035,
    0.00040,
    0.00045,
    0.00050,
    0.00060,
    0.00070,
    0.00080,
    0.00100,
)
MAX_H = max(WINDOWS)


def htag(h: float) -> str:
    return f"{int(round(h * 1e5)):05d}"


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


def load_profiles(raw_path: str):
    raw = _open_raw(raw_path)
    try:
        scans = scan_numbers(raw)
        pick = [
            scans[i]
            for i in np.linspace(0, len(scans) - 1, min(3, len(scans)))
            .round()
            .astype(int)
        ]
        out = []
        for s in pick:
            mz, inten = scan_profile(raw, s)
            if mz.size:
                out.append((mz, inten))
    finally:
        raw.Dispose()
    return out


def count_window(sorted_mz, mu, h):
    lo = np.searchsorted(sorted_mz, mu - h, side="left")
    hi = np.searchsorted(sorted_mz, mu + h, side="right")
    return int(hi - lo)


def classify(anchors, spec, profiles, delta, deriv, src_all):
    dmz = np.sort(spec.table["mass"].to_numpy(float))
    rows = []
    for a in anchors.itertuples(index=False):
        for n in range(1, min(10, int(a.O)) + 1):
            mu = float(a.m0) + n * delta
            if mu < dmz[0] or mu > dmz[-1]:
                continue
            rec = {"deriv": deriv, "anchor_idx": int(a.anchor_idx), "n": n, "mu": mu}
            for h in WINDOWS:
                nd = count_window(dmz, mu, h)
                ns = count_window(src_all, mu, h)
                status = "absent"
                k_obs = 0
                if nd >= 1:
                    if ns == 0:
                        status = "reliable"
                        k_obs = nd
                    else:
                        lo = int(np.searchsorted(src_all, mu - h, side="left"))
                        hi = int(np.searchsorted(src_all, mu + h, side="right"))
                        inter = src_all[lo:hi]
                        u_lo = min(mu, float(inter.min())) - h
                        u_hi = max(mu, float(inter.max())) + h
                        ks = [
                            len(profile_peaks(mz, inten, u_lo, u_hi, min_snr=3.0))
                            for mz, inten in profiles
                        ]
                        k_obs = max(ks) if ks else 0
                        votes = ["reliable" if k >= 1 + ns else "ambiguous" for k in ks]
                        if votes.count("reliable") >= 2:
                            status = "reliable"
                        else:
                            status = "ambiguous"
                rec[f"nd_{htag(h)}"] = nd
                rec[f"ns_{htag(h)}"] = ns
                rec[f"kobs_{htag(h)}"] = k_obs
                rec[f"st_{htag(h)}"] = status
            rows.append(rec)
    return pd.DataFrame(rows)


def main() -> None:
    t0 = time.perf_counter()
    cache = pd.read_pickle("D:/Temp/User/nom_restrict_cache/restricted.pkl")
    src, dmet, dacet = cache["src"], cache["dmet"], cache["dacet"]
    anchors = build_anchors(src)
    src_all = np.sort(src.table["mass"].to_numpy(float))
    print(f"anchors={len(anchors)}", flush=True)

    base = Path("data/real_sets") / "Fulvagra F16"
    _, m_raw, d_raw = REAL["Fulvagra F16"]
    frames = []
    for deriv, spec, raw_name, delta in (
        ("cd3", dmet, m_raw, CHEM.derivatization_shifts["delta_cd3"]),
        ("cd3co", dacet, d_raw, CHEM.derivatization_shifts["delta_cd3co"]),
    ):
        profiles = load_profiles(str((base / raw_name).resolve()))
        df = classify(anchors, spec, profiles, delta, deriv, src_all)
        frames.append(df)
        print(
            f"{deriv}: positions={len(df)}, "
            f"profile_cases={int((df[[f'ns_{htag(h)}' for h in WINDOWS]].max(axis=1) > 0).sum())}",
            flush=True,
        )
    pos = pd.concat(frames, ignore_index=True)

    report = {"anchors": len(anchors), "windows": list(WINDOWS), "by_h": []}
    for h in WINDOWS:
        st = f"st_{htag(h)}"
        nd = f"nd_{htag(h)}"
        ns = f"ns_{htag(h)}"
        for deriv in ("cd3", "cd3co"):
            sub = pos[pos["deriv"] == deriv]
            counts = sub[st].value_counts()
            # политика длины по непрерывному префиксу (до первого absent)
            sub = sub.sort_values(["anchor_idx", "n"])
            a_arr = sub["anchor_idx"].to_numpy()
            statuses = sub[st].to_numpy()
            conf, unc = [], []
            start = 0
            for i in range(1, len(sub) + 1):
                if i == len(sub) or a_arr[i] != a_arr[start]:
                    last_rel = 0
                    last_amb = 0
                    for j in range(start, i):
                        s = statuses[j]
                        if s == "absent":
                            break
                        if s == "reliable":
                            last_rel = j - start + 1
                        else:
                            last_amb = j - start + 1
                    conf.append(last_rel)
                    unc.append(last_amb if last_amb > last_rel else 0)
                    start = i
            conf = np.asarray(conf)
            unc = np.asarray(unc)
            report["by_h"].append(
                {
                    "deriv": deriv,
                    "h_da": h,
                    "n_positions": int(len(sub)),
                    "reliable": int(counts.get("reliable", 0)),
                    "ambiguous": int(counts.get("ambiguous", 0)),
                    "absent": int(counts.get("absent", 0)),
                    "mean_nd": round(float(sub[nd].mean()), 3),
                    "mean_ns": round(float(sub[ns].mean()), 3),
                    "mean_sum": round(float((sub[nd] + sub[ns]).mean()), 3),
                    "mean_confirmed": round(float(conf.mean()), 3),
                    "mean_unconfirmed_tail": round(float(unc.mean()), 3),
                    "share_confirmed_0": round(float((conf == 0).mean()), 4),
                    "share_confirmed_ge2": round(float((conf >= 2).mean()), 4),
                    "share_confirmed_ge4": round(float((conf >= 4).mean()), 4),
                    "conf_hist": {str(k): int((conf == k).sum()) for k in range(1, 11)},
                }
            )
    report["seconds"] = round(time.perf_counter() - t0, 1)
    Path("D:/Temp/User/reliability_policy_v2_f16.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    pos.to_pickle("D:/Temp/User/reliability_policy_v2_positions.pkl")
    for r in report["by_h"]:
        print(r)
    print("seconds", report["seconds"])


if __name__ == "__main__":
    main()
