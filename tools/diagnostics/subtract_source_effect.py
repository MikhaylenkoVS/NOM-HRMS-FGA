"""Эффект «шумоподавление дериватизатов + вычитание исходника» (A/B на одном сете).

Сравниваются два режима на одних и тех же данных:

  * ``base`` — текущие умолчания: дериватизаты не шумоподавляются, исходник не
    вычитается;
  * ``new``  — шумоподавление дериватизатов + вычитание исходника из них
    (сопоставление только по m/z, интенсивности не учитываются).

Метрики: время, число пиков дериватизатов, число серий, суммы и распределения
N_COOH / N_OH, а также сколько соединений изменило счётчики.

Запуск:
  python tools/diagnostics/subtract_source_effect.py --dataset "Fulvagra F16" \
      --variant chorsphal --json D:/Temp/User/subtract_f16.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

REAL_SETS = {
    "Fulvagra F16": (
        "Fulvagra_prep HPLC_FR16_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s_.raw",
        "Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s.raw",
    ),
}


def _resolve(path: str) -> str:
    if path.lower().endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    return path


def _hist(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        key = str(int(v))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def run(ds: dict, *, mode: str, variant: str) -> dict:
    from src.core import run_pipeline

    kwargs = dict(
        src_path=_resolve(ds["src"]),
        dmet_path=_resolve(ds["dmet"]),
        dacet_path=_resolve(ds["dacet"]),
        sep=",",
        visualize=False,
        use_cache=False,
    )
    if mode == "new":
        kwargs.update(denoise_derivatives=True, subtract_source=True, subtract_ppm=5.0)
    else:
        kwargs.update(denoise_derivatives=False, subtract_source=False)

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

    st = res.stats
    table = res.table
    n_cooh = table["N_COOH"] if "N_COOH" in table.columns else []
    n_oh = table["N_OH"] if "N_OH" in table.columns else []
    compounds = {}
    if "brutto" in table.columns:
        for _, row in table.iterrows():
            compounds[round(float(row["mass"]), 4)] = (
                int(row.get("N_COOH", 0)),
                int(row.get("N_OH", 0)),
            )
    return {
        "mode": mode,
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


def compare(base: dict, new: dict) -> dict:
    b, n = base["compounds"], new["compounds"]
    keys = set(b) & set(n)
    changed = [k for k in keys if b[k] != n[k]]
    delta_cooh = sum(n[k][0] - b[k][0] for k in keys)
    delta_oh = sum(n[k][1] - b[k][1] for k in keys)
    examples = [
        {"mass": k, "base": b[k], "new": n[k]}
        for k in sorted(
            changed, key=lambda k: -(abs(b[k][0] - n[k][0]) + abs(b[k][1] - n[k][1]))
        )[:10]
    ]
    return {
        "compounds_common": len(keys),
        "compounds_changed": len(changed),
        "delta_sum_cooh": delta_cooh,
        "delta_sum_oh": delta_oh,
        "examples": examples,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    s, m, d = REAL_SETS[a.dataset]
    base_dir = Path("data/real_sets") / a.dataset
    ds = {
        "id": a.dataset,
        "src": str(base_dir / s),
        "dmet": str(base_dir / m),
        "dacet": str(base_dir / d),
    }

    results = {}
    for mode in ("base", "new"):
        print(f"[{time.strftime('%H:%M:%S')}] {mode}: старт…", flush=True)
        results[mode] = run(ds, mode=mode, variant=a.variant)
        r = results[mode]
        print(
            f"[{time.strftime('%H:%M:%S')}] {mode}: {r['seconds']:.0f} c | "
            f"dmet {r['peaks']['dmet']}, dacet {r['peaks']['dacet']} | "
            f"серии CD3 {r['series']['cd3_rows']}, CD3CO {r['series']['cd3co_rows']} | "
            f"сумма N_COOH {r['result']['sum_cooh']}, N_OH {r['result']['sum_oh']}",
            flush=True,
        )

    diff = compare(results["base"], results["new"])
    print("\n=== СРАВНЕНИЕ ===")
    print(
        f"  время: {results['base']['seconds']:.0f} → {results['new']['seconds']:.0f} c"
    )
    print(
        f"  сумма N_COOH: {results['base']['result']['sum_cooh']} → "
        f"{results['new']['result']['sum_cooh']} (Δ{diff['delta_sum_cooh']:+d})"
    )
    print(
        f"  сумма N_OH:   {results['base']['result']['sum_oh']} → "
        f"{results['new']['result']['sum_oh']} (Δ{diff['delta_sum_oh']:+d})"
    )
    print(
        f"  соединений с сериями: CD3 {results['base']['series']['cd3_rows']} → "
        f"{results['new']['series']['cd3_rows']}, CD3CO "
        f"{results['base']['series']['cd3co_rows']} → {results['new']['series']['cd3co_rows']}"
    )
    print(
        f"  изменили счётчики: {diff['compounds_changed']} из {diff['compounds_common']}"
    )
    for e in diff["examples"][:5]:
        print(f"    {e['mass']}: {e['base']} → {e['new']}")

    if a.json:
        payload = {
            "dataset": a.dataset,
            "variant": a.variant,
            "base": {k: v for k, v in results["base"].items() if k != "compounds"},
            "new": {k: v for k, v in results["new"].items() if k != "compounds"},
            "diff": diff,
        }
        Path(a.json).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
