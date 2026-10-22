"""PPD по определению пользователя + политика confirmed/unconfirmed длины.

PPD (deriv): число пиков дериватизата в окне +/-h вокруг ожидаемой mu.
PPD (src):   число пиков исходника в том же окне.
PPD (sum):   сумма.

Надёжный пик: ровно один пик дериватизата и ноль сигналов исходника
в окне. Иначе — ненадёжный (если пик дериватизата есть) или absent.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.configs import CHEM
from src.core.domain.molecule import parse_formula
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.spectrum._series import _theor_ion_mass_cached
from src.configs import PIPELINE

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


def counts_in_window(sorted_mz, mu, h):
    lo = np.searchsorted(sorted_mz, mu - h, side="left")
    hi = np.searchsorted(sorted_mz, mu + h, side="right")
    return (hi - lo).astype(int)


def main() -> None:
    cache = pd.read_pickle("D:/Temp/User/nom_restrict_cache/restricted.pkl")
    src, dmet, dacet = cache["src"], cache["dmet"], cache["dacet"]
    anchors = build_anchors(src)
    src_all = np.sort(src.table["mass"].to_numpy(float))
    src_assigned = np.sort(
        src.table.loc[src.table["assign"].astype(bool), "mass"].to_numpy(float)
    )
    print("anchors", len(anchors), "src peaks", len(src_all))

    rows = []
    for deriv, spec, delta in (
        ("cd3", dmet, CHEM.derivatization_shifts["delta_cd3"]),
        ("cd3co", dacet, CHEM.derivatization_shifts["delta_cd3co"]),
    ):
        dmz = np.sort(spec.table["mass"].to_numpy(float))
        for a in anchors.itertuples(index=False):
            for n in range(1, min(10, int(a.O)) + 1):
                mu = float(a.m0) + n * delta
                if mu < dmz[0] or mu > dmz[-1]:
                    continue
                rec = {
                    "deriv": deriv,
                    "anchor_idx": int(a.anchor_idx),
                    "n": n,
                    "mu": mu,
                }
                for h in WINDOWS:
                    rec[f"nd_{h:g}"] = int(counts_in_window(dmz, mu, h))
                    rec[f"ns_{h:g}"] = int(counts_in_window(src_all, mu, h))
                    rec[f"nsa_{h:g}"] = int(counts_in_window(src_assigned, mu, h))
                rows.append(rec)
        print(deriv, "positions", len(rows))
    pos = pd.DataFrame(rows)

    report = {"anchors": len(anchors), "by_window": [], "policy": {}}
    for h in WINDOWS:
        nd = pos[f"nd_{h:g}"].to_numpy()
        ns = pos[f"ns_{h:g}"].to_numpy()
        nsa = pos[f"nsa_{h:g}"].to_numpy()
        reliable = (nd == 1) & (ns == 0)
        reliable_a = (nd == 1) & (nsa == 0)
        for deriv in ("cd3", "cd3co"):
            m = pos["deriv"].to_numpy() == deriv
            report["by_window"].append(
                {
                    "deriv": deriv,
                    "h_da": h,
                    "n_positions": int(m.sum()),
                    "mean_nd": round(float(nd[m].mean()), 3),
                    "mean_ns_all": round(float(ns[m].mean()), 3),
                    "mean_ns_assigned": round(float(nsa[m].mean()), 3),
                    "mean_sum": round(float((nd[m] + ns[m]).mean()), 3),
                    "share_nd0": round(float((nd[m] == 0).mean()), 4),
                    "share_nd1": round(float((nd[m] == 1).mean()), 4),
                    "share_nd2": round(float((nd[m] >= 2).mean()), 4),
                    "share_reliable": round(float(reliable[m].mean()), 4),
                    "share_reliable_assigned_src": round(
                        float(reliable_a[m].mean()), 4
                    ),
                }
            )

    # политика: последний reliable / последний unreliable в непрерывном префиксе
    for h in (0.00030, 0.00050, 0.00080):
        nd = pos[f"nd_{h:g}"].to_numpy()
        ns = pos[f"ns_{h:g}"].to_numpy()
        for deriv in ("cd3", "cd3co"):
            sub = pos[pos["deriv"] == deriv].sort_values(["anchor_idx", "n"])
            a_arr = sub["anchor_idx"].to_numpy()
            nd_s = nd[sub.index.to_numpy()]
            ns_s = ns[sub.index.to_numpy()]
            conf, unc = [], []
            start = 0
            for i in range(1, len(sub) + 1):
                if i == len(sub) or a_arr[i] != a_arr[start]:
                    last_rel = 0
                    last_unrel = 0
                    for j in range(start, i):
                        if nd_s[j] == 0:
                            break
                        if nd_s[j] == 1 and ns_s[j] == 0:
                            last_rel = j - start + 1
                        else:
                            last_unrel = j - start + 1
                    conf.append(last_rel)
                    unc.append(last_unrel if last_unrel > last_rel else 0)
                    start = i
            report["policy"][f"{deriv}_{h:g}"] = {
                "n_anchors": len(conf),
                "mean_confirmed": round(float(np.mean(conf)), 3),
                "mean_unconfirmed_tail": round(float(np.mean(unc)), 3),
                "share_confirmed_ge2": round(float((np.asarray(conf) >= 2).mean()), 4),
                "share_confirmed_ge4": round(float((np.asarray(conf) >= 4).mean()), 4),
                "conf_hist": {
                    str(k): int((np.asarray(conf) == k).sum()) for k in range(1, 11)
                },
            }
    Path("D:/Temp/User/ppd_policy_f16.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report["by_window"][:6], ensure_ascii=False, indent=1))
    print(json.dumps(report["policy"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
