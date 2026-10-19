"""Замер замедления назначения формул: реальный спектр против синтетики.

Сравниваются режимы:
  A. без галогенов (CHNOSP) — базовая точка ×1;
  B. новый пакетный путь, 16 комбинаций;
  C. новый пакетный путь, все комбинации;
  D. старый путь (запрос на каждую комбинацию), 16 комбинаций — как в v0.9.0;
  E. старый путь, все комбинации — источник прежней оценки ×10–30.

Запуск (из корня проекта):
  python tools/measure_real_vs_synthetic.py --peaks 200
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np
import pandas as pd

from src.core.domain.spectrum import Spectrum
from src.core.spectrum._assign import assign_formulas
from src.core.spectrum._denoise import denoise
from src.core.spectrum._formula_source import open_formula_db
from src.core.spectrum._load import load_spectrum

REAL = "C:/Users/mvs/Downloads/SRFA_ESI_480k_128_m-s Scan[1]_averaged.csv"
SYNTH = "data/test_sets/set_01/original.csv"


class _NoBatchReader:
    """Обёртка: скрывает пакетный API, чтобы включить старый путь (по комбинации)."""

    def __init__(self, reader):
        self._reader = reader

    def __getattr__(self, name):
        return getattr(self._reader, name)


def sample_spectrum(path: str, count: int) -> Spectrum:
    """Спектр из реальных пиков: половина самых интенсивных, половина случайных."""
    spec = load_spectrum(path, sep=",")
    spec = denoise(spec)
    t = spec.table
    inten = np.asarray(t["intensity"], dtype=float)
    order = np.argsort(-inten)
    k = max(1, count // 2)
    idx = list(order[:k])
    rng = np.random.default_rng(42)
    rest = [i for i in range(len(t)) if i not in set(idx)]
    if rest:
        idx += list(rng.choice(rest, size=min(k, len(rest)), replace=False))
    sub = t.iloc[sorted(idx)][["mass", "intensity"]].reset_index(drop=True)
    return Spectrum(table=sub)


def time_assignment(spec: Spectrum, db, **kwargs) -> float:
    s = spec.copy()
    orig = spec.copy()
    t0 = time.perf_counter()
    assign_formulas(
        s,
        rel_error_ppm=5.0,
        mass_min=0.0,
        mass_max=1000.0,
        isotope_filter=True,
        original=orig,
        isotope_satellites=False,
        formula_db=db,
        **kwargs,
    )
    return time.perf_counter() - t0


def measure(name: str, path: str, peaks: int, db, max_combos_all: int) -> dict:
    spec = sample_spectrum(path, peaks)
    n = len(spec.table)
    masses = np.asarray(spec.table["mass"], dtype=float)
    print(f"\n=== {name}: {n} пиков ({masses.min():.0f}–{masses.max():.0f} Да) ===")

    import src.core.spectrum._formula_source as fs

    saved_cap = fs._MAX_HALOGEN_COMBOS
    rows = []
    try:
        variants = [
            ("A. без галогенов", {"db_halogen_atoms": 0}, db),
            ("B. новый путь, 16 комб.", {"db_halogen_atoms": 5}, db),
            (
                "C. новый путь, все комб.",
                {"db_halogen_atoms": 5, "db_halogen_exhaustive": True},
                db,
            ),
            ("D. старый путь, 16 комб.", {"db_halogen_atoms": 5}, _NoBatchReader(db)),
            (
                "E. старый путь, все комб.",
                {"db_halogen_atoms": 5, "db_halogen_max_combinations": max_combos_all},
                _NoBatchReader(db),
            ),
        ]
        for label, kwargs, reader in variants:
            if label.startswith("E"):
                fs._MAX_HALOGEN_COMBOS = max_combos_all
            dt = time_assignment(spec, reader, **kwargs)
            rows.append((label, dt, dt / n * 1e3))
            print(f"  {label:26s}: {dt:7.2f} c  ({dt / n * 1e3:7.2f} мс/пик)")
    finally:
        fs._MAX_HALOGEN_COMBOS = saved_cap

    base = rows[0][1]
    table = []
    print("  замедление относительно режима без галогенов:")
    for label, dt, ms in rows:
        factor = dt / base if base else 1.0
        table.append(
            {
                "mode": label,
                "seconds": round(dt, 3),
                "ms_per_peak": round(ms, 3),
                "slowdown": round(factor, 2),
            }
        )
        print(f"    {label:26s}: ×{factor:.2f}")
    return {"dataset": name, "peaks": n, "rows": table}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--peaks", type=int, default=200)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    db = open_formula_db()
    if db is None:
        raise SystemExit("сжатая база формул недоступна")
    results = [
        measure("РЕАЛЬНЫЙ (SRFA)", REAL, a.peaks, db, 125),
        measure("СИНТЕТИЧЕСКИЙ (set_01)", SYNTH, a.peaks, db, 125),
    ]
    db.close()
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(results, fh, ensure_ascii=False, indent=2)
        print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
