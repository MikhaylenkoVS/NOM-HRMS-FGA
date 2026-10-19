"""Быстрый замер «этапа назначения» на реальных сетах (все варианты базы).

Полный пайплайн на реальных RAW идёт часами (SRFA: ~380 тыс. пиков после
шумоподавления), поэтому здесь меряется именно та часть, которая зависит от базы:
генерация кандидатов ``db_candidates`` на выборке пиков. Это позволяет быстро и
сопоставимо сравнить варианты; полные пайплайновые числа даёт
``measure_db_variants.py``.

Запуск:
  python tools/diagnostics/measure_assign_real.py --sets SRFA,"Fulvagra F14" \\
      --peaks 2000 --peaks-none 200 --json D:/Temp/User/assign_real.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

#: Перебор (без базы) здесь НЕ измеряется: он живёт внутри стадии назначения
#: (`_generate_cached`), а не в `db_candidates`. Его числа даёт полный пайплайн
#: (`measure_db_variants.py`).
VARIANTS = {
    "chorsphal": "CHNOSPHal (галогены в базе)",
    "chnosp": "CHNOSP + слой подстановок",
}

REAL_ORIGINAL = {
    "SRFA": "SRFA_ESI_480k_128_m-s.raw",
    "Fulvagra F14": "Fulvagra_prep HPLC_Fr14_ESI_1e6_480k_128_m-s.raw",
    "Fulvagra F16": "Fulvagra_prep HPLC_FR16_ESI_1e6_480k_128_m-s.raw",
}


def _peaks(dataset: str, limit: int) -> list[float]:
    """Нейтральные массы выборки пиков реального сета."""
    import json as _json

    from src.core.io.raw_bridge import average_raw_to_json
    from src.core.spectrum._denoise import denoise
    from src.core.spectrum._generate import _ion_shift
    from src.core.spectrum._load import load_spectrum

    raw = f"data/real_sets/{dataset}/" + REAL_ORIGINAL[dataset]
    path = average_raw_to_json(raw, 0.0, 999.0)
    spec = denoise(load_spectrum(path, sep=","))
    chem = _json.loads(Path("src/configs/chemistry.json").read_text(encoding="utf-8"))
    shift = _ion_shift(chem.get("default_ion_mode", "[M-H]-"))
    masses = [float(m) - shift for m in spec.table["mass"].to_numpy()]
    if limit and len(masses) > limit:
        step = max(1, len(masses) // limit)
        masses = masses[::step][:limit]
    return masses


def _run_variant(masses: list[float]) -> dict:
    from src.core.spectrum._constants import FormulaSearchConfig
    from src.core.spectrum._formula_source import db_candidates, open_formula_db

    cfg = FormulaSearchConfig()
    reader = open_formula_db()
    n_cand = 0
    empty = 0
    t0 = time.perf_counter()
    for m in masses:
        half = m * 5.0 * 1e-6
        rows, _masses = db_candidates(
            reader, cfg, m, half, include_halogens=True, halogen_exhaustive=True
        )
        n_cand += len(rows)
        empty += 0 if len(rows) else 1
    dt = time.perf_counter() - t0
    if reader is not None:
        reader.close()
    return {
        "seconds": round(dt, 2),
        "ms_per_peak": round(dt / len(masses) * 1000, 2),
        "candidates": n_cand,
        "avg_candidates": round(n_cand / len(masses), 1),
        "empty": empty,
        "peaks": len(masses),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sets", default="SRFA,Fulvagra F14,Fulvagra F16")
    ap.add_argument("--peaks", type=int, default=2000)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    results: list[dict] = []
    for ds in [s.strip() for s in a.sets.split(",") if s.strip()]:
        masses = _peaks(ds, a.peaks)
        print(f"\n=== {ds}: пиков в выборке {len(masses)} ===", flush=True)
        for var_id, title in VARIANTS.items():
            sample = masses
            if not _has_db(var_id):
                print(f"  пропуск {title}: база не найдена", flush=True)
                continue
            old = os.environ.get("NOM_FORMULA_DB")
            os.environ["NOM_FORMULA_DB"] = var_id
            try:
                r = _run_variant(sample)
            finally:
                if old is None:
                    os.environ.pop("NOM_FORMULA_DB", None)
                else:
                    os.environ["NOM_FORMULA_DB"] = old
            r.update({"variant": var_id, "title": title, "dataset": ds})
            results.append(r)
            print(
                f"  {title:30s} {r['ms_per_peak']:8.2f} мс/пик | "
                f"кандидатов {r['candidates']:8d} ({r['avg_candidates']:6.1f}/пик) | "
                f"без кандидатов {r['empty']:5d}",
                flush=True,
            )

    print("\n=== СВОДКА (мс/пик) ===")
    for ds in {r["dataset"] for r in results}:
        rows = [r for r in results if r["dataset"] == ds]
        base = next((r for r in rows if r["variant"] == "chnosp"), None)
        for r in rows:
            factor = (
                (base["ms_per_peak"] / r["ms_per_peak"])
                if base and r["ms_per_peak"]
                else 0
            )
            print(
                f"  {ds:14s} {r['title']:30s} {r['ms_per_peak']:8.2f} мс/пик "
                f"(×{factor:.2f} к CHNOSP) кандидатов {r['avg_candidates']:6.1f}/пик"
            )

    if a.json:
        Path(a.json).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nзаписано: {a.json}")


def _has_db(variant_id: str) -> bool:
    from src.core.formula_db._variants import DB_VARIANTS, find_variant_path

    if variant_id == "none":
        return True
    for v in DB_VARIANTS:
        if v.id == variant_id:
            return find_variant_path(v) is not None
    return False


if __name__ == "__main__":
    main()
