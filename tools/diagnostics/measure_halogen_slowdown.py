"""Замер замедления назначения формул от числа галогенных комбинаций.

Требование заказчика: таблица «число комбинаций → замедление» должна быть
измерена на доступных сетах и зафиксирована константами.

Метод: берём реальные пики из тест-сетов (по умолчанию set_01/set_02, спектр
original), для каждого N выбираем верхние N комбинаций тем же кодом, что и в
продукте (``select_halogen_combos``), и измеряем время поиска кандидатов по
базе. Базовая точка — 16 комбинаций (замедление ×1).

Запуск (из корня проекта): python tools/measure_halogen_slowdown.py --peaks 40
"""

from __future__ import annotations

import argparse
import json
import time

import numpy as np

from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._formula_source import (
    db_candidates,
    open_formula_db,
    select_halogen_combos,
)
from src.core.spectrum._load import load_spectrum

#: Точки, которые нужно измерить (края band'ов заказчика).
GRID = [4, 10, 16, 20, 24, 30, 32, 40, 50, 64, 80, 100, 125]


def sample_masses(paths: list[str], count: int) -> np.ndarray:
    """Массы пиков из реальных спектров (по убыванию интенсивности)."""
    masses: list[float] = []
    for path in paths:
        try:
            spec = load_spectrum(path, sep=",")
        except Exception:
            continue
        t = spec.table
        order = np.argsort(-np.asarray(t["intensity"], dtype=float))
        sel = t.iloc[order[: max(5, count // max(1, len(paths)))]]
        masses.extend(float(m) for m in sel["mass"])
    uniq = sorted(set(round(m, 4) for m in masses))
    return np.asarray(uniq[:count], dtype=float)


def measure(db, cfg, masses: np.ndarray, n_combos: int, exhaustive: bool) -> float:
    """Среднее время поиска кандидатов на пик, мс."""
    t0 = time.perf_counter()
    for m in masses:
        db_candidates(
            db,
            cfg,
            float(m),
            0.002,
            include_halogens=True,
            max_halogen_atoms=5,
            halogen_exhaustive=exhaustive,
            halogen_max_combinations=n_combos,
        )
    return (time.perf_counter() - t0) * 1e3 / max(1, len(masses))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--spectra",
        nargs="*",
        default=[
            "data/test_sets/set_01/original.csv",
            "data/test_sets/set_02/original.csv",
        ],
    )
    ap.add_argument("--peaks", type=int, default=40)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    masses = sample_masses(a.spectra, a.peaks)
    print(
        f"пиков для замера: {len(masses)} (диапазон {masses.min():.0f}–{masses.max():.0f} Да)"
    )

    db = open_formula_db()
    if db is None:
        raise SystemExit("сжатая база формул недоступна")
    cfg = FormulaSearchConfig()

    rows = []
    base = None
    for n in GRID:
        exhaustive = n >= max(GRID)
        combos, allowed = select_halogen_combos(cfg, n, exhaustive, 5)
        ms = measure(db, cfg, masses, n, exhaustive)
        if n == 16:
            base = ms
        rows.append(
            {"combos": len(combos), "allowed": allowed, "ms_per_peak": round(ms, 3)}
        )
        print(f"  комбинаций {len(combos):4d} (из {allowed}): {ms:7.3f} мс/пик")
    db.close()

    print("\nзамедление относительно 16 комбинаций:")
    table = []
    for r in rows:
        factor = r["ms_per_peak"] / base if base else 1.0
        r["slowdown"] = round(factor, 2)
        table.append([r["combos"], r["slowdown"]])
        print(f"  {r['combos']:4d} комбинаций: ×{factor:.2f}")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(
                {"peaks": len(masses), "base_ms": base, "rows": rows},
                fh,
                ensure_ascii=False,
                indent=2,
            )
        print(f"записано: {a.json}")


if __name__ == "__main__":
    main()
