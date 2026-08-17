"""Benchmark ``assign_formulas`` and candidate generation on a reference spectrum.

Usage::

    python -m src.core.benchmark_assign [csv_path] [mass_min] [mass_max] [ppm]

Defaults to ``data/test_sets/set_01/original.csv`` over the 200–700 Da window.
"""

import sys
import time
from pathlib import Path

from src.core.spectrum import load_spectrum, assign_formulas
from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._generate import _generate_cached, _generate_candidate_formulas
from src.configs import CHEM


def _median(values):
    s = sorted(values)
    return s[len(s) // 2]


def benchmark(
    csv_path: str,
    mass_min: float = 200.0,
    mass_max: float = 700.0,
    ppm: float = 1.0,
    runs: int = 5,
) -> None:
    cfg = FormulaSearchConfig()
    gen_min = mass_min + CHEM.proton_mass
    gen_max = mass_max + CHEM.proton_mass

    # ── Генерация кандидатов (cold vs cached) ───────────────────────────────
    t0 = time.perf_counter()
    candidates = _generate_candidate_formulas(gen_min, gen_max, cfg, "nom_like")
    t_cold = time.perf_counter() - t0

    t0 = time.perf_counter()
    _generate_candidate_formulas(gen_min, gen_max, cfg, "nom_like")
    t_warm = time.perf_counter() - t0

    print(f"peaks file     : {csv_path}")
    print(f"mass window    : {mass_min}–{mass_max} Da")
    print(f"candidates     : {len(candidates):,}")
    print(f"generate cold  : {t_cold:.4f}s")
    print(f"generate cached: {t_warm:.6f}s  ({t_cold / max(t_warm, 1e-9):.0f}x)")
    print(f"cache info     : {_generate_cached.cache_info()}")

    # ── assign_formulas (warm cache) ────────────────────────────────────────
    times = []
    for _ in range(runs):
        src = load_spectrum(csv_path, mass_min=mass_min, mass_max=mass_max)
        t0 = time.perf_counter()
        res = assign_formulas(src, rel_error_ppm=ppm, mass_min=None, mass_max=None)
        times.append(time.perf_counter() - t0)
    n_assigned = int(res.table["assign"].sum()) if "assign" in res.table else 0
    print(
        f"assign_formulas median: {_median(times):.4f}s  ({runs} runs, {n_assigned} assigned)"
    )


if __name__ == "__main__":
    root = Path("data/test_sets/set_01")
    csv_path = sys.argv[1] if len(sys.argv) > 1 else str(root / "original.csv")
    mass_min = float(sys.argv[2]) if len(sys.argv) > 2 else 200.0
    mass_max = float(sys.argv[3]) if len(sys.argv) > 3 else 700.0
    ppm = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    benchmark(csv_path, mass_min, mass_max, ppm)
