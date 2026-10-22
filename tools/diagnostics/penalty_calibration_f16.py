"""Черновая калибровка весов штрафов по target/decoy на F16.

Запуск:
    python tools/diagnostics/penalty_calibration_f16.py --decoys 10 --samples 100
"""

from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import pandas as pd

from src.configs import CHEM
from src.core.spectrum._decoy import DECOY_SEED, decoy_shifts
from src.core.spectrum._penalty import PenaltyWeights
from src.core.spectrum._series import find_series

CACHE = Path("D:/Temp/User/nom_restrict_cache/restricted.pkl")
OUT = Path("D:/Temp/User/penalty_calibration_f16")
OUT.mkdir(parents=True, exist_ok=True)


def _reweight(df: pd.DataFrame, w: PenaltyWeights) -> pd.Series:
    lengths = []
    for _, row in df.iterrows():
        o_limit = int(row.get("o_limit", 0))
        details = row.get("step_details", [])
        statuses = []
        for d in details:
            pen: dict[str, float] = {}
            if d.get("status") == "gap":
                pen["gap"] = w.gap(1)
            else:
                n = int(d.get("n", 0))
                if d.get("n_src", 0) > 0 and not d.get("profile_resolved"):
                    pen["source"] = w.source_overlap(int(d["n_src"]))
                if d.get("o_excess") or n > o_limit:
                    pen["o_excess"] = w.o_excess(n - o_limit)
                if d.get("iso_status") == "inconsistent":
                    pen["isotope"] = w.isotope(float(d.get("iso_dev", float("nan"))))
                if d.get("conflict_overlap"):
                    pen["conflict_overlap"] = w.conflict_overlap
                if d.get("conflict_no_prev"):
                    pen["conflict_no_prev"] = w.conflict_no_prev
                # soft-штрафы применяем только к уже ambiguous-шагам
                if d.get("status") != "reliable":
                    p = d.get("persistence")
                    if p is not None:
                        val = w.persistence(float(p))
                        if val:
                            pen["persistence"] = val
                    if d.get("shape_ok") is False:
                        pen["peak_profile"] = w.peak_profile
                    if d.get("multi") is True:
                        pen["poor_resolution"] = w.multi_resolution
                    jump = d.get("intensity_jump")
                    if jump is not None:
                        val = w.intensity(5.0 * (float(jump) / 10.0 - 1.0))
                        if val:
                            pen["intensity_profile"] = val
            total = min(100.0, float(sum(pen.values())))
            status = (
                "gap"
                if d.get("status") == "gap"
                else ("reliable" if total == 0.0 else "ambiguous")
            )
            statuses.append((int(d["n"]), status))
        reliable = [n for n, st in statuses if st == "reliable"]
        confirmed = max(reliable, default=0)
        amb = [n for n, st in statuses if st != "reliable" and n > confirmed]
        lengths.append(max(amb, default=confirmed))
    return pd.Series(lengths, index=df.index, dtype=int)


def _fdr(
    target: np.ndarray, decoys: list[np.ndarray], min_len: int = 2
) -> tuple[float, int, float]:
    if target.size == 0:
        return 1.0, 0, 0.0
    n_t = int((target >= min_len).sum())
    n_d = float(np.mean([(d >= min_len).sum() for d in decoys])) if decoys else 0.0
    return (n_d / max(1, n_t), n_t, n_d)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decoys", type=int, default=10)
    ap.add_argument("--samples", type=int, default=80)
    ap.add_argument("--rows", type=int, default=0)
    ap.add_argument("--frac", type=float, default=0.2)
    args = ap.parse_args()

    cache = pd.read_pickle(CACHE)
    src, dmet, dacet = cache["src"], cache["dmet"], cache["dacet"]
    d3 = float(CHEM.derivatization_shifts["delta_cd3"])
    d3co = float(CHEM.derivatization_shifts["delta_cd3co"])
    base = dict(max_groups=10, max_gaps=0, require_first_step=False)

    t0 = time.time()
    target = {
        "cd3": find_series(src, dmet, d3, **base),
        "cd3co": find_series(src, dacet, d3co, **base),
    }
    if args.frac > 0:
        target = {
            k: v.sample(frac=min(1.0, args.frac), random_state=1).reset_index(drop=True)
            for k, v in target.items()
        }
    elif args.rows > 0:
        target = {
            k: v.sample(n=min(args.rows, len(v)), random_state=1).reset_index(drop=True)
            for k, v in target.items()
        }
    shifts = decoy_shifts(d3, k=args.decoys, seed=DECOY_SEED)
    decoys = {"cd3": [], "cd3co": []}
    for i, sh in enumerate(shifts):
        f3 = find_series(src, dmet, d3 + sh, **base)
        f3co = find_series(src, dacet, d3co + sh, **base)
        if args.frac > 0:
            f3 = f3.sample(frac=min(1.0, args.frac), random_state=1).reset_index(
                drop=True
            )
            f3co = f3co.sample(frac=min(1.0, args.frac), random_state=1).reset_index(
                drop=True
            )
        elif args.rows > 0:
            f3 = f3.sample(n=min(args.rows, len(f3)), random_state=1).reset_index(
                drop=True
            )
            f3co = f3co.sample(n=min(args.rows, len(f3co)), random_state=1).reset_index(
                drop=True
            )
        decoys["cd3"].append(f3)
        decoys["cd3co"].append(f3co)
        if (i + 1) % 5 == 0:
            print(
                f"[{time.strftime('%H:%M:%S')}] decoys {i+1}/{len(shifts)}", flush=True
            )

    target_lengths = {k: _reweight(v, PenaltyWeights()) for k, v in target.items()}
    decoy_lengths = {
        k: [_reweight(frame, PenaltyWeights()) for frame in frames]
        for k, frames in decoys.items()
    }
    base_metrics = {
        k: {
            f"fdr_{L}": _fdr(
                target_lengths[k].to_numpy(),
                [s.to_numpy() for s in decoy_lengths[k]],
                min_len=L,
            )[0]
            for L in range(1, 9)
        }
        for k in target
    }
    print("base", base_metrics, flush=True)

    rng = random.Random(20261022)
    factors = [0.5, 1.0, 2.0, 3.0]
    rows = []
    for s in range(args.samples):
        w = PenaltyWeights(
            source_overlap_max=30.0 * rng.choice(factors),
            o_excess_max=40.0 * rng.choice(factors),
            isotope_max=30.0 * rng.choice(factors),
            gap_per=15.0 * rng.choice(factors),
            conflict_overlap=10.0 * rng.choice(factors),
            conflict_no_prev=30.0 * rng.choice(factors),
        )
        rec = {"sample": s, **w.__dict__}
        ok = True
        for k in target:
            tl = _reweight(target[k], w).to_numpy()
            dl = [_reweight(f, w).to_numpy() for f in decoys[k]]
            fdr, n_t, n_d = _fdr(tl, dl, min_len=2)
            rec[f"{k}_fdr1"] = _fdr(tl, dl, min_len=1)[0]
            rec[f"{k}_fdr2"] = fdr
            rec[f"{k}_fdr3"] = _fdr(tl, dl, min_len=3)[0]
            rec[f"{k}_fdr"] = fdr
            rec[f"{k}_target"] = n_t
            rec[f"{k}_decoy"] = n_d
            rec[f"{k}_mean_len"] = float(tl.mean())
            if fdr > 0.05:
                ok = False
        rec["pass"] = ok
        rec["target_total"] = rec["cd3_target"] + rec["cd3co_target"]
        rows.append(rec)

    if not rows:
        summary = {"decoys": args.decoys, "samples": 0, "base": base_metrics}
        (OUT / "summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    out = pd.DataFrame(rows).sort_values(
        ["pass", "target_total"], ascending=[False, False]
    )
    out.to_csv(OUT / "grid.csv", index=False)
    summary = {
        "decoys": args.decoys,
        "samples": args.samples,
        "base": base_metrics,
        "best": out.head(10).to_dict("records"),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
