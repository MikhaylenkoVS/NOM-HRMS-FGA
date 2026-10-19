"""Разложение эффекта: шумоподавление дериватизатов отдельно от вычитания.

Режимы (на одних и тех же данных F16):
  * ``base``                     — без шумоподавления дериватизатов, без вычитания;
  * ``denoise``                  — только шумоподавление дериватизатов;
  * ``subtract@5``               — только вычитание исходника (1:1) при 5 ppm;
  * ``subtract@1.5``             — только вычитание при 1.5 ppm (плотность пиков F16
                                   даёт ~26 % случайных совпадений при 5 ppm);
  * ``denoise+subtract@1.5``     — оба, окно 1.5 ppm.

Запуск:
  python tools/diagnostics/subtract_modes_f16.py --json D:/Temp/User/subtract_modes.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from subtract_source_effect import REAL_SETS, _hist, _resolve  # type: ignore


def metrics(res, *, mode: str, seconds: float, settings: dict) -> dict:
    st = res.stats
    table = res.table
    n_cooh = table["N_COOH"] if "N_COOH" in table.columns else []
    n_oh = table["N_OH"] if "N_OH" in table.columns else []
    compounds = {}
    for _, row in table.iterrows():
        compounds[round(float(row["mass"]), 4)] = (
            int(row.get("N_COOH", 0)),
            int(row.get("N_OH", 0)),
        )
    return {
        "mode": mode,
        "settings": settings,
        "seconds": round(seconds, 1),
        "peaks": {
            "src": int(st.src_denoised),
            "dmet": int(st.dmet_denoised),
            "dacet": int(st.dacet_denoised),
        },
        "overlap_removed": {
            "dmet": int(getattr(st, "dmet_overlap_removed", 0) or 0),
            "dacet": int(getattr(st, "dacet_overlap_removed", 0) or 0),
        },
        "series": {
            "cd3_rows": int(getattr(st.dmet, "rows", 0)),
            "cd3_max": int(getattr(st.dmet, "max_groups", 0)),
            "cd3_missing": int(getattr(st.dmet, "missing_total", 0)),
            "cd3co_rows": int(getattr(st.dacet, "rows", 0)),
            "cd3co_max": int(getattr(st.dacet, "max_groups", 0)),
            "cd3co_missing": int(getattr(st.dacet, "missing_total", 0)),
        },
        "result": {
            "rows": int(len(table)),
            "n_cooh_gt0": int(sum(1 for v in n_cooh if v > 0)),
            "n_oh_gt0": int(sum(1 for v in n_oh if v > 0)),
            "sum_cooh": int(sum(int(v) for v in n_cooh)),
            "sum_oh": int(sum(int(v) for v in n_oh)),
            "hist_cooh": _hist(n_cooh),
            "hist_oh": _hist(n_oh),
        },
        "compounds": compounds,
    }


def run_mode(ds: dict, *, mode: str, variant: str, settings: dict) -> dict:
    from src.core import run_pipeline

    kwargs = dict(
        src_path=_resolve(ds["src"]),
        dmet_path=_resolve(ds["dmet"]),
        dacet_path=_resolve(ds["dacet"]),
        sep=",",
        visualize=False,
        use_cache=False,
        denoise_derivatives=bool(settings.get("denoise")),
        subtract_source=bool(settings.get("subtract")),
        subtract_ppm=float(settings.get("ppm", 5.0)),
    )
    old = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = variant
    try:
        t0 = time.perf_counter()
        res = run_pipeline(**kwargs)
        seconds = time.perf_counter() - t0
    finally:
        if old is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old
    return metrics(res, mode=mode, seconds=seconds, settings=settings)


MODES = {
    "denoise": {"denoise": True, "subtract": False},
    "subtract@5": {"denoise": False, "subtract": True, "ppm": 5.0},
    "subtract@1.5": {"denoise": False, "subtract": True, "ppm": 1.5},
    "denoise+subtract@1.5": {"denoise": True, "subtract": True, "ppm": 1.5},
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--modes", nargs="*", default=list(MODES))
    ap.add_argument("--reuse-base", default="D:/Temp/User/subtract_f16.json")
    ap.add_argument("--json", default="D:/Temp/User/subtract_modes_f16.json")
    a = ap.parse_args()

    s, m, d = REAL_SETS[a.dataset]
    base_dir = Path("data/real_sets") / a.dataset
    ds = {
        "id": a.dataset,
        "src": str(base_dir / s),
        "dmet": str(base_dir / m),
        "dacet": str(base_dir / d),
    }

    results: dict[str, dict] = {}
    reuse = Path(a.reuse_base)
    if reuse.is_file():
        old = json.loads(reuse.read_text(encoding="utf-8"))
        results["base"] = dict(old["base"], compounds={}, mode="base")
        print(f"база взята из {reuse}: {results['base']['seconds']:.0f} c", flush=True)

    for mode in a.modes:
        settings = MODES[mode]
        print(f"[{time.strftime('%H:%M:%S')}] {mode}: старт…", flush=True)
        results[mode] = run_mode(ds, mode=mode, variant=a.variant, settings=settings)
        r = results[mode]
        print(
            f"[{time.strftime('%H:%M:%S')}] {mode}: {r['seconds']:.0f} c | "
            f"dmet {r['peaks']['dmet']} (удалено {r['overlap_removed']['dmet']}) | "
            f"CD3 серий {r['series']['cd3_rows']}, сумма N_COOH {r['result']['sum_cooh']} | "
            f"CD3CO серий {r['series']['cd3co_rows']}, сумма N_OH {r['result']['sum_oh']}",
            flush=True,
        )
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(
            json.dumps(
                {
                    k: {kk: vv for kk, vv in v.items() if kk != "compounds"}
                    for k, v in results.items()
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    print("\n=== СВОДКА ===")
    base = results.get("base")
    for mode, r in results.items():
        d_cooh = r["result"]["sum_cooh"] - base["result"]["sum_cooh"] if base else 0
        d_oh = r["result"]["sum_oh"] - base["result"]["sum_oh"] if base else 0
        print(
            f"  {mode:22s} {r['seconds']:7.0f} c | dmet {r['peaks']['dmet']:7d} | "
            f"N_COOH {r['result']['sum_cooh']:7d} ({d_cooh:+d}) | "
            f"N_OH {r['result']['sum_oh']:7d} ({d_oh:+d})"
        )

    print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
