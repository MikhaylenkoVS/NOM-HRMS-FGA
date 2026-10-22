"""Разбор reliability-причин в готовой таблице результата.

Читает result.csv.gz и считает статусы ступеней и штрафы по N_COOH/N_OH.
"""

from __future__ import annotations

import argparse
import ast
import json
from collections import Counter
from pathlib import Path

import pandas as pd


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


def analyze(df: pd.DataFrame) -> dict:
    out: dict[str, dict] = {}
    for col in ("N_COOH_details", "N_OH_details"):
        if col not in df.columns:
            continue
        statuses: Counter[str] = Counter()
        penalties: Counter[str] = Counter()
        reasons: Counter[str] = Counter()
        steps = 0
        series_with_steps = 0
        for value in df[col]:
            details = _details(value)
            if not details:
                continue
            series_with_steps += 1
            for detail in details:
                if not isinstance(detail, dict):
                    continue
                steps += 1
                statuses[str(detail.get("status") or "")] += 1
                for key in detail.get("penalties") or {}:
                    penalties[str(key)] += 1
                for reason in detail.get("reasons") or []:
                    reasons[str(reason).split(":")[0]] += 1
        out[col] = {
            "series_with_steps": series_with_steps,
            "steps": steps,
            "statuses": dict(statuses.most_common()),
            "penalties": dict(penalties.most_common()),
            "reasons": dict(reasons.most_common(30)),
        }
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--result", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    df = pd.read_csv(args.result)
    payload = analyze(df)
    Path(args.out).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
