"""Негативный контроль поиска серий: сколько «групп» находится при неверной Δ.

Идея: если поиск серий даёт много ложных ступеней из-за случайных совпадений
пиков, то при заведомо неверном сдвиге Δ он всё равно «найдёт» серии. Тогда
распределение N_COOH при ложной Δ — это фон ложноположительных срабатываний.

Сравниваются три прогона на одних данных (режим: шумоподавление дериватизатов +
вычитание исходника):
  * ``real``      — настоящие Δ (17.03448 и 45.02939);
  * ``shift+0.1`` — Δ увеличены на 0.1 Да (химически бессмысленно);
  * ``shift+0.5`` — Δ увеличены на 0.5 Да.

Запуск:
  python tools/diagnostics/series_negative_control.py \
      --dataset "Fulvagra F16" --json D:/Temp/User/neg_control_f16.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from subtract_source_effect import REAL_SETS, _hist, _resolve  # type: ignore

MODES = {
    "real": (0.0, 0.0),
    "shift+0.1": (0.1, 0.1),
    "shift+0.5": (0.5, 0.5),
}


def run(ds: dict, *, mode: str, variant: str) -> dict:
    from src.core.pipeline import _run as RUN

    d_cd3, d_cd3co = MODES[mode]
    old_cd3, old_cd3co = RUN.DELTA_CD3, RUN.DELTA_CD3CO
    RUN.DELTA_CD3 = old_cd3 + d_cd3
    RUN.DELTA_CD3CO = old_cd3co + d_cd3co
    old_env = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = variant
    try:
        t0 = time.perf_counter()
        res = RUN.run_pipeline(
            src_path=_resolve(ds["src"]),
            dmet_path=_resolve(ds["dmet"]),
            dacet_path=_resolve(ds["dacet"]),
            sep=",",
            visualize=False,
            use_cache=False,
            denoise_derivatives=True,
            subtract_source=True,
            subtract_ppm=5.0,
        )
        seconds = time.perf_counter() - t0
    finally:
        RUN.DELTA_CD3, RUN.DELTA_CD3CO = old_cd3, old_cd3co
        if old_env is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old_env

    st = res.stats
    table = res.table
    cooh = table["N_COOH"] if "N_COOH" in table.columns else []
    oh = table["N_OH"] if "N_OH" in table.columns else []
    return {
        "mode": mode,
        "delta_shift": d_cd3,
        "seconds": round(seconds, 1),
        "peaks": {"dmet": int(st.dmet_denoised), "dacet": int(st.dacet_denoised)},
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
            "n_cooh_gt0": int(sum(1 for v in cooh if v > 0)),
            "n_oh_gt0": int(sum(1 for v in oh if v > 0)),
            "sum_cooh": int(sum(int(v) for v in cooh)),
            "sum_oh": int(sum(int(v) for v in oh)),
            "mean_cooh": round(float(sum(int(v) for v in cooh) / len(cooh)), 2),
            "mean_oh": round(float(sum(int(v) for v in oh) / len(oh)), 2),
            "hist_cooh": _hist(cooh),
            "hist_oh": _hist(oh),
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--modes", nargs="*", default=list(MODES))
    ap.add_argument("--json", default="D:/Temp/User/neg_control_f16.json")
    a = ap.parse_args()

    s, m, d = REAL_SETS[a.dataset]
    base = Path("data/real_sets") / a.dataset
    ds = {
        "id": a.dataset,
        "src": str(base / s),
        "dmet": str(base / m),
        "dacet": str(base / d),
    }

    out: dict[str, dict] = {}
    for mode in a.modes:
        print(f"[{time.strftime('%H:%M:%S')}] {mode}: старт…", flush=True)
        out[mode] = run(ds, mode=mode, variant=a.variant)
        r = out[mode]
        print(
            f"[{time.strftime('%H:%M:%S')}] {mode}: {r['seconds']:.0f} c | "
            f"CD3 серий {r['series']['cd3_rows']}, среднее N_COOH {r['result']['mean_cooh']} | "
            f"CD3CO серий {r['series']['cd3co_rows']}, среднее N_OH {r['result']['mean_oh']}",
            flush=True,
        )
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(
            json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    print("\n=== НЕГАТИВНЫЙ КОНТРОЛЬ ===")
    print(
        f"{'режим':12s} {'сдвиг Δ, Да':>12s} {'ср. N_COOH':>11s} {'ср. N_OH':>10s} "
        f"{'CD3 серий':>10s}"
    )
    for mode, r in out.items():
        print(
            f"{mode:12s} {r['delta_shift']:12.1f} {r['result']['mean_cooh']:11.2f} "
            f"{r['result']['mean_oh']:10.2f} {r['series']['cd3_rows']:10d}"
        )
    print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
