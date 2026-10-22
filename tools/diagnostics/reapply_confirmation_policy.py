"""Пересчитать confirmed/ambiguous по уже готовым result.csv.gz.

Новое правило подтверждения: ступень reliable, если у неё нет
``source_overlap`` и ``conflict_overlap``; остальные штрафы остаются в
confidence/reasons. Пайплайн заново не запускается.
"""

from __future__ import annotations

import argparse
import ast
import gzip
import json
from collections import Counter
from pathlib import Path

import pandas as pd

from src.core.spectrum._series import _finalize_policy


def _details(value):
    if isinstance(value, list):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = ast.literal_eval(value)
            return parsed if isinstance(parsed, list) else []
        except (ValueError, SyntaxError):
            return []
    return []


def _hist(values) -> dict[str, int]:
    out: Counter[str] = Counter(str(int(v)) for v in values)
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def _column_summary(values, raw_values, amb_values) -> dict:
    vals = [int(v) for v in values]
    raw = [int(v) for v in raw_values]
    amb = [int(v) for v in amb_values]
    return {
        "rows": len(vals),
        "confirmed_gt0": sum(1 for v in vals if v > 0),
        "raw_gt0": sum(1 for v in raw if v > 0),
        "confirmed_mean": round(sum(vals) / len(vals), 3) if vals else 0.0,
        "raw_mean": round(sum(raw) / len(raw), 3) if raw else 0.0,
        "confirmed_max": max(vals, default=0),
        "ambiguous_max": max(amb, default=0),
        "confirmed_hist": _hist(vals),
        "raw_hist": _hist(raw),
    }


def process_dataset(src_dir: Path, dst_dir: Path) -> dict:
    df = pd.read_csv(src_dir / "result.csv.gz")
    statuses: Counter[str] = Counter()
    steps = 0
    for row_idx in range(len(df)):
        for prefix, col in (("dmet", "N_COOH_details"), ("dacet", "N_OH_details")):
            details = _details(df.at[row_idx, col]) if col in df.columns else []
            if not details:
                continue
            policy = _finalize_policy(details)
            df.at[row_idx, col] = repr(details)
            df.at[row_idx, f"N_{'COOH' if prefix == 'dmet' else 'OH'}"] = policy[
                "confirmed_length"
            ]
            df.at[row_idx, f"N_{'COOH' if prefix == 'dmet' else 'OH'}_ambiguous"] = (
                policy["ambiguous_length"]
            )
            df.at[row_idx, f"N_{'COOH' if prefix == 'dmet' else 'OH'}_display"] = (
                policy["display_length"]
            )
            df.at[row_idx, f"N_{'COOH' if prefix == 'dmet' else 'OH'}_confidence"] = (
                policy["confidence"]
            )
            # N_*_confirmed — синоним N_* в итоговой таблице.
            df.at[row_idx, f"N_{'COOH' if prefix == 'dmet' else 'OH'}_confirmed"] = (
                policy["confirmed_length"]
            )
            for detail in details:
                statuses[str(detail.get("status") or "")] += 1
                steps += 1

    dst_dir.mkdir(parents=True, exist_ok=True)
    with gzip.open(
        dst_dir / "result_overlap_only.csv.gz", "wt", encoding="utf-8"
    ) as fh:
        df.to_csv(fh, index=False)

    summary = {
        "dataset": src_dir.name,
        "confirmation_mode": "overlap_only",
        "rows": len(df),
        "steps": steps,
        "statuses": dict(statuses.most_common()),
        "result": {},
    }
    for col in ("N_COOH", "N_OH"):
        summary["result"][col] = _column_summary(
            df[col],
            df[f"{col}_raw"] if f"{col}_raw" in df.columns else df[col],
            (
                df[f"{col}_ambiguous"]
                if f"{col}_ambiguous" in df.columns
                else [0] * len(df)
            ),
        )
    (dst_dir / "summary_overlap_only.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="output/real_sets_2026-10-22")
    ap.add_argument("--out", default="output/real_sets_overlap_only")
    ap.add_argument("--datasets", default="all")
    args = ap.parse_args()
    src = Path(args.src)
    out = Path(args.out)
    names = [
        p.name for p in src.iterdir() if p.is_dir() and (p / "result.csv.gz").is_file()
    ]
    if args.datasets.strip().lower() not in ("all", "real"):
        wanted = {x.strip().lower() for x in args.datasets.split(",")}
        names = [n for n in names if n.lower() in wanted]
    summaries = []
    for name in names:
        summary = process_dataset(src / name, out / name)
        summaries.append(summary)
        print(
            f"{name}: rows={summary['rows']} "
            f"CD3>0={summary['result']['N_COOH']['confirmed_gt0']} "
            f"OH>0={summary['result']['N_OH']['confirmed_gt0']}",
            flush=True,
        )
    (out / "summary_overlap_only.json").write_text(
        json.dumps(summaries, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"written: {out}")


if __name__ == "__main__":
    main()
