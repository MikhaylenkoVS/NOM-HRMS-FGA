"""Прогон пайплайна с текущими умолчаниями + отчёт по степеням дериватизации.

Печатает и сохраняет:
  * число пиков и сколько удалено вычитанием;
  * число серий и их максимальную длину;
  * распределение N_COOH / N_OH (сырое и «значимое» — только статистически
    достоверные серии);
  * долю значимых серий, среднее/медиану, распределение p-значений.

Запуск:
  python tools/diagnostics/run_defaults_report.py --dataset "Fulvagra F16" \
      --json D:/Temp/User/defaults_f16.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from subtract_source_effect import REAL_SETS, _hist, _resolve  # type: ignore


def hist_of(values) -> dict[str, int]:
    return _hist(values)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--json", default="D:/Temp/User/defaults_f16.json")
    a = ap.parse_args()

    s, m, d = REAL_SETS[a.dataset]
    base = Path("data/real_sets") / a.dataset
    old = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = a.variant
    from src.core import run_pipeline

    try:
        t0 = time.perf_counter()
        res = run_pipeline(
            src_path=_resolve(str(base / s)),
            dmet_path=_resolve(str(base / m)),
            dacet_path=_resolve(str(base / d)),
            sep=",",
            visualize=False,
            use_cache=False,
        )
        seconds = time.perf_counter() - t0
    finally:
        if old is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old

    st = res.stats
    df = res.table
    payload = {
        "dataset": a.dataset,
        "variant": a.variant,
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
        "result": {},
    }

    for col in ("N_COOH", "N_OH"):
        raw = df[col] if col in df.columns else []
        conf_col = f"{col}_confirmed"
        conf = df[conf_col] if conf_col in df.columns else []
        payload["result"][col] = {
            "mean_raw": round(float(sum(int(v) for v in raw) / len(df)), 2),
            "mean_confirmed": round(float(sum(int(v) for v in conf) / len(df)), 2),
            "hist_raw": hist_of(raw),
            "hist_confirmed": hist_of(conf),
            "gt0_raw": int(sum(1 for v in raw if v > 0)),
            "gt0_confirmed": int(sum(1 for v in conf if v > 0)),
        }

    print(f"\n=== {a.dataset} / {a.variant} (умолчания) ===")
    print(
        f"время {seconds:.0f} c | пики src={st.src_denoised}, "
        f"dmet={st.dmet_denoised} (удалено {payload['overlap_removed']['dmet']}), "
        f"dacet={st.dacet_denoised} (удалено {payload['overlap_removed']['dacet']})"
    )
    print(
        f"серии: CD3 {payload['series']['cd3_rows']} (макс {payload['series']['cd3_max']}), "
        f"CD3CO {payload['series']['cd3co_rows']} (макс {payload['series']['cd3co_max']})"
    )
    for col in ("N_COOH", "N_OH"):
        r = payload["result"][col]
        print(
            f"{col}: среднее сырое {r['mean_raw']}, значимое {r['mean_confirmed']} | "
            f">0 сырое {r['gt0_raw']}, значимое {r['gt0_confirmed']}"
        )
        print(f"  сырое:      {r['hist_raw']}")
        print(f"  значимое:   {r['hist_confirmed']}")

    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
