"""Статистика ambiguous для F16: формулы, последний шаг, хвост."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from reliability_policy_f16 import build_anchors


def main() -> None:
    cache = pd.read_pickle("D:/Temp/User/nom_restrict_cache/restricted.pkl")
    src = cache["src"]
    anchors = build_anchors(src)
    pos = pd.read_pickle("D:/Temp/User/reliability_policy_v2_positions.pkl")

    assigned = src.table[src.table["assign"].astype(bool)].copy()
    formulas_all = set(assigned["brutto"].astype(str))
    formulas_anchor = set(anchors["brutto"].astype(str))
    report = {
        "assigned_peaks": int(len(assigned)),
        "unique_formulas_all": int(len(formulas_all)),
        "anchors_O_ge_1": int(len(anchors)),
        "unique_formulas_anchors": int(len(formulas_anchor)),
        "by_deriv": {},
    }

    for deriv in ("cd3", "cd3co"):
        g = pos[pos["deriv"] == deriv].sort_values(["anchor_idx", "n"])
        a_ids = anchors["anchor_idx"].to_numpy()
        n_anchors = len(a_ids)
        # позиции могут отсутствовать для якоря (mu вне диапазона) — считаем 0
        sub = {int(i): gg for i, gg in g.groupby("anchor_idx", sort=False)}

        for htag in ("00030", "00050", "00080"):
            nd = f"nd_{htag}"
            st = f"st_{htag}"
            positive = 0
            last_amb = 0
            tail_counts = []
            tail_positive = 0
            n1_any = 0
            n1_rel = 0
            n1_amb = 0
            n1_absent = 0
            formulas_n1 = set()
            formulas_n1_rel = set()
            formulas_positive = set()
            for i in a_ids:
                gg = sub.get(int(i))
                brutto = str(anchors.loc[anchors["anchor_idx"] == i, "brutto"].iloc[0])
                if gg is None or len(gg) == 0:
                    n1_absent += 1
                    continue
                steps = gg[["n", nd, st]].to_dict("records")
                # n=1
                first = next((r for r in steps if int(r["n"]) == 1), None)
                if first is None or int(first[nd]) == 0:
                    n1_absent += 1
                else:
                    n1_any += 1
                    formulas_n1.add(brutto)
                    if first[st] == "reliable":
                        n1_rel += 1
                        formulas_n1_rel.add(brutto)
                    else:
                        n1_amb += 1
                # префикс до первого nd=0
                prefix = []
                for r in steps:
                    if int(r[nd]) == 0:
                        break
                    prefix.append(r)
                if not prefix:
                    continue
                positive += 1
                formulas_positive.add(brutto)
                last = prefix[-1]
                if last[st] == "ambiguous":
                    last_amb += 1
                # reliable-степени в префиксе
                rel_degrees = [int(r["n"]) for r in prefix if r[st] == "reliable"]
                last_rel = max(rel_degrees) if rel_degrees else 0
                tail = sum(
                    1 for r in prefix if int(r["n"]) > last_rel and r[st] == "ambiguous"
                )
                tail_counts.append(tail)
                if tail > 0:
                    tail_positive += 1
            tail_counts = np.asarray(tail_counts)
            report["by_deriv"][f"{deriv}_{htag}"] = {
                "n_anchors": n_anchors,
                "n1_any": n1_any,
                "n1_reliable": n1_rel,
                "n1_ambiguous": n1_amb,
                "n1_absent": n1_absent,
                "unique_formulas_n1": len(formulas_n1),
                "unique_formulas_n1_reliable": len(formulas_n1_rel),
                "positive_series": positive,
                "unique_formulas_positive": len(formulas_positive),
                "last_ambiguous": last_amb,
                "last_ambiguous_share_positive": (
                    round(last_amb / positive, 4) if positive else 0.0
                ),
                "last_ambiguous_share_all": round(last_amb / n_anchors, 4),
                "tail_mean_positive": (
                    round(float(tail_counts.mean()), 3) if tail_counts.size else 0.0
                ),
                "tail_mean_positive_nonzero": (
                    round(float(tail_counts[tail_counts > 0].mean()), 3)
                    if tail_positive
                    else 0.0
                ),
                "tail_positive_share": (
                    round(tail_positive / positive, 4) if positive else 0.0
                ),
                "tail_hist": {
                    str(k): int((tail_counts == k).sum()) for k in range(0, 8)
                }
                | {">=8": int((tail_counts >= 8).sum())},
            }
    Path("D:/Temp/User/ambiguous_stats_f16.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
