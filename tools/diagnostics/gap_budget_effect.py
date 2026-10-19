"""Насколько ограничение «не более 1 пропуска» ускоряет поиск серий.

Идея: в одном прогоне пайплайна подменяем ``find_series`` обёрткой, которая
считает серии дважды на **одних и тех же** входных данных:

  * новое правило — ``max_gaps`` по умолчанию (1);
  * старое поведение — большой ``max_gaps`` (бюджет не срабатывает, обрыв только
    по ``max_consecutive_misses=3``), что эквивалентно прежней логике.

Замеряются время, число серий и суммы N_COOH / N_OH для обоих режимов, поэтому
видно и ускорение, и научный эффект (сколько групп перестало завышаться).

Запуск:
  python tools/diagnostics/gap_budget_effect.py --dataset "Fulvagra F16" \
      --variant chorsphal --json D:/Temp/User/gap_effect_f16.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from src.core.pipeline import _stages as ST  # noqa: F401  (патчим find_series)

REAL_SETS = {
    "Fulvagra F16": (
        "Fulvagra_prep HPLC_FR16_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s_.raw",
        "Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s.raw",
    ),
    "SRFA": (
        "SRFA_ESI_480k_128_m-s.raw",
        "SRFA_CD3_ESI_480k_128_m-s_240829205142.raw",
        "SRFA_CD3CO_ESI_480k_128_m-s.raw",
    ),
    "Fulvagra F14": (
        "Fulvagra_prep HPLC_Fr14_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR16_CD3OD mod_ESI_1e6_480k_128_m-s.raw",  # заменяется ниже
        "Fulvagra_prep HPLC_FR14_AC-D4_ESI_1e6_480k_128_m-s.raw",
    ),
}
REAL_SETS["Fulvagra F14"] = (
    "Fulvagra_prep HPLC_Fr14_ESI_1e6_480k_128_m-s.raw",
    "Fulvagra_prep HPLC_FR14_CD3OD mod_ESI_1e6_480k_128_m-s.raw",
    "Fulvagra_prep HPLC_FR14_AC-D4_ESI_1e6_480k_128_m-s.raw",
)

OLD_MAX_GAPS = 10_000  # бюджет не срабатывает → прежнее поведение

RECORDS: list[dict] = []


def _delta_label(delta: float, deltas: dict) -> str:
    for name, value in deltas.items():
        if abs(value - delta) < 1e-9:
            return name
    return f"delta={delta:.5f}"


def _stats(df, column: str) -> dict:
    if df is None or df.empty:
        return {"rows": 0, "sum": 0, "max": 0}
    if column not in df.columns:
        return {"rows": len(df), "sum": 0, "max": 0}
    return {
        "rows": int(len(df)),
        "sum": int(df[column].sum()),
        "max": int(df[column].max()),
    }


def _install_wrapper(new_max_gaps: int, labels: dict[str, float]) -> object:
    original = ST.find_series

    def wrapper(*args, **kwargs):
        delta = kwargs.get("delta")
        if delta is None and len(args) >= 3:
            delta = args[2]
        label = _delta_label(float(delta), labels)

        kw_new = dict(kwargs)
        kw_new["max_gaps"] = new_max_gaps
        t0 = time.perf_counter()
        df_new = original(*args, **kw_new)
        t_new = time.perf_counter() - t0

        kw_old = dict(kwargs)
        kw_old["max_gaps"] = OLD_MAX_GAPS
        t0 = time.perf_counter()
        df_old = original(*args, **kw_old)
        t_old = time.perf_counter() - t0

        rec = {
            "series": label,
            "new_seconds": round(t_new, 1),
            "old_seconds": round(t_old, 1),
            "speedup": round(t_old / t_new, 2) if t_new else 0.0,
            "new": _stats(df_new, "n_groups"),
            "old": _stats(df_old, "n_groups"),
        }
        RECORDS.append(rec)
        print(
            f"  {label}: новое {t_new:8.1f} c | старое {t_old:8.1f} c | "
            f"×{rec['speedup']:.2f} | серий {rec['new']['rows']} против "
            f"{rec['old']['rows']}, сумма групп {rec['new']['sum']} против "
            f"{rec['old']['sum']}",
            flush=True,
        )
        return df_new

    ST.find_series = wrapper
    return original


def _resolve(path: str | None) -> str | None:
    if not path:
        return None
    if path.lower().endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    return path


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--max-gaps", type=int, default=1)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    from src.configs import CHEM
    from src.core import run_pipeline

    base = Path("data/real_sets") / a.dataset
    s, m, d = REAL_SETS[a.dataset]
    labels = {
        "CD3": float(CHEM.derivatization_shifts["delta_cd3"]),
        "CD3CO": float(CHEM.derivatization_shifts["delta_cd3co"]),
    }

    original = _install_wrapper(a.max_gaps, labels)
    old_env = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = a.variant
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
        total = time.perf_counter() - t0
    finally:
        ST.find_series = original
        if old_env is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old_env

    print(f"\nпайплайн целиком: {total:.1f} c, ок={res.ok}")
    sum_new = sum(r["new_seconds"] for r in RECORDS)
    sum_old = sum(r["old_seconds"] for r in RECORDS)
    print(f"серии вместе: новое {sum_new:.1f} c, старое {sum_old:.1f} c")
    if sum_new:
        print(f"ускорение поиска серий: ×{sum_old / sum_new:.2f}")
        print(
            f"экономия на F16: {sum_old - sum_new:.1f} c "
            f"({(sum_old - sum_new) / (total + sum_old):.1%} от времени с новым правилом)"
        )

    if a.json:
        Path(a.json).write_text(
            json.dumps(
                {
                    "dataset": a.dataset,
                    "variant": a.variant,
                    "pipeline_seconds": round(total, 1),
                    "series": RECORDS,
                    "series_new_seconds": round(sum_new, 1),
                    "series_old_seconds": round(sum_old, 1),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        print(f"записано: {a.json}")


if __name__ == "__main__":
    main()
