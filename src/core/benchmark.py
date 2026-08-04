"""Benchmark pipeline on real data sets.

Usage: python -m src.core.benchmark data/real_sets/set_01
"""

import sys
import time
from pathlib import Path

from src.core.pipeline import run_pipeline
from src.configs import PIPELINE


def benchmark(set_dir: str) -> None:
    root = Path(set_dir)
    src_csv = root / "original.csv"
    dmet_csv = root / "deutermethylated.csv"
    dacet_csv = root / "deuteroacylated.csv"

    if not src_csv.exists():
        print(f"ERROR: {src_csv} not found")
        return

    print(f"Benchmark: {root.name}")
    print(f"  src:  {src_csv.stat().st_size:,} bytes" if src_csv.exists() else "  src: MISSING")
    print(f"  dmet: {dmet_csv.stat().st_size:,} bytes" if dmet_csv.exists() else "  dmet: MISSING")
    print(f"  dacet: {dacet_csv.stat().st_size:,} bytes" if dacet_csv.exists() else "  dacet: MISSING")

    defaults = PIPELINE.run_pipeline_defaults
    t0 = time.perf_counter()
    res = run_pipeline(
        src_path=str(src_csv),
        dmet_path=str(dmet_csv) if dmet_csv.exists() else None,
        dacet_path=str(dacet_csv) if dacet_csv.exists() else None,
        use_cache=False,
    )
    elapsed = time.perf_counter() - t0

    timings = getattr(res, "timings", None)
    print(f"\nTotal: {elapsed:.2f}s")
    if timings:
        print(f"  Breakdown: {timings.summary()}")
    print(f"  Result rows: {len(res.table) if hasattr(res, 'table') and res.table is not None else 'N/A'}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        benchmark(sys.argv[1])
    else:
        print("Usage: python -m src.core.benchmark <set_dir>")
