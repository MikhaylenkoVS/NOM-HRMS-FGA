"""Замер вариантов базы формул по ПОЛНОМУ пайплайну на всех реальных сетах.

Заказчик: сравнивать варианты нужно по времени всего пайплайна, а не только
этапа назначения формул, и не на одном сете, а на всех доступных.

Датасеты (находятся автоматически):
  * ``set_01`` … ``set_05`` — тест-сеты (CSV: original/deutermethylated/
    deuteroacylated);
  * ``SRFA``, ``Fulvagra F14``, ``Fulvagra F16`` — реальные RAW-тройки
    (исходный, CD3, CD3CO).

Варианты: ``chorsphal`` (v3, галогены в базе), ``chnosp`` (v2 + слой
подстановок), ``none`` (перебор — внутренний резерв, медленный).

Запуск из корня проекта:
  python tools/diagnostics/measure_db_variants.py --datasets all \
      --variants chnosp chorsphal --json D:/Temp/User/measure_all.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

VARIANTS: dict[str, str] = {
    "chorsphal": "CHNOSPHal (с галогенами)",
    "chnosp": "CHNOSP (базовый)",
    "none": "без базы (перебор)",
}

TEST_SETS_DIR = Path("data/test_sets")
REAL_SETS_DIR = Path("data/real_sets")

#: Как искать тройку файлов в реальном сете (префикс исходника, CD3, CD3CO).
REAL_PATTERNS = (
    (
        "SRFA",
        "SRFA_ESI_480k_128_m-s.raw",
        "SRFA_CD3_ESI_480k_128_m-s_240829205142.raw",
        "SRFA_CD3CO_ESI_480k_128_m-s.raw",
    ),
    (
        "Fulvagra F14",
        "Fulvagra_prep HPLC_Fr14_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR14_CD3OD mod_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR14_AC-D4_ESI_1e6_480k_128_m-s.raw",
    ),
    (
        "Fulvagra F16",
        "Fulvagra_prep HPLC_Fr16_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s_.raw",
        "Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s.raw",
    ),
)


def discover(datasets: str) -> list[dict]:
    """Список датасетов: {'id', 'kind', 'src', 'dmet', 'dacet', 'sep'}."""
    want = datasets.strip().lower()
    out: list[dict] = []

    def _want(name: str, kind: str) -> bool:
        if want in ("all", ""):
            return True
        if want == "test":
            return kind == "test"
        if want == "real":
            return kind == "real"
        return name.lower() in {w.strip() for w in want.split(",")}

    for d in sorted(TEST_SETS_DIR.glob("set_*")):
        if not _want(d.name, "test"):
            continue
        src = d / "original.csv"
        dmet = d / "deutermethylated.csv"
        dacet = d / "deuteroacylated.csv"
        if src.is_file():
            out.append(
                {
                    "id": d.name,
                    "kind": "test",
                    "src": str(src),
                    "dmet": str(dmet) if dmet.is_file() else None,
                    "dacet": str(dacet) if dacet.is_file() else None,
                    "sep": ",",
                }
            )
    for name, s, m, a in REAL_PATTERNS:
        if not _want(name, "real"):
            continue
        base = REAL_SETS_DIR / name
        src, dmet, dacet = base / s, base / m, base / a
        if src.is_file():
            out.append(
                {
                    "id": name,
                    "kind": "real",
                    "src": str(src),
                    "dmet": str(dmet) if dmet.is_file() else None,
                    "dacet": str(dacet) if dacet.is_file() else None,
                    "sep": ",",
                }
            )
    return out


def _has_db(variant_id: str) -> bool:
    from src.core.formula_db._variants import DB_VARIANTS, find_variant_path

    if variant_id == "none":
        return True
    for v in DB_VARIANTS:
        if v.id == variant_id:
            return find_variant_path(v) is not None
    return False


def _resolve_input(path: str | None) -> str | None:
    """RAW/mzML → усреднённая таблица (как делает CLI); CSV остаётся как есть."""
    if not path:
        return None
    low = path.lower()
    if low.endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    if low.endswith(".mzml"):
        from src.core.io.mzml_bridge import mzml_to_json

        return mzml_to_json(path, rt_min=0.0, rt_max=999.0)
    return path


def run_pipeline_once(ds: dict, *, time_cap: float) -> dict:
    """Один полный прогон пайплайна на датасете (кэш выключен)."""
    from src.core import run_pipeline

    t0 = time.perf_counter()
    res = run_pipeline(
        src_path=_resolve_input(ds["src"]),
        dmet_path=_resolve_input(ds["dmet"]),
        dacet_path=_resolve_input(ds["dacet"]),
        sep=ds["sep"],
        visualize=False,
        use_cache=False,
    )
    seconds = time.perf_counter() - t0
    stats = getattr(res, "stats", None)
    table = getattr(res, "table", None)
    return {
        "seconds": round(seconds, 2),
        "ok": bool(getattr(res, "ok", True)),
        "rows": int(len(table)) if table is not None else 0,
        "assigned": int(getattr(stats, "assigned_count", 0) or 0),
        "src_loaded": int(getattr(stats, "src_loaded", 0) or 0),
        "src_denoised": int(getattr(stats, "src_denoised", 0) or 0),
        "errors": [str(e)[:160] for e in (getattr(res, "errors", None) or [])][:3],
        "over_cap": seconds > time_cap if time_cap else False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--datasets", default="all", help="all | test | real | список id через запятую"
    )
    ap.add_argument("--variants", nargs="*", default=["chorsphal", "chnosp", "none"])
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument(
        "--time-cap",
        type=float,
        default=0.0,
        help="если >0 — помечать прогоны длиннее этого времени",
    )
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    sets = discover(a.datasets)
    if not sets:
        raise SystemExit("датасеты не найдены")

    results: list[dict] = []
    for ds in sets:
        print(f"\n=== {ds['id']} ({ds['kind']}) ===", flush=True)
        for var_id in a.variants:
            if var_id not in VARIANTS:
                print(f"  неизвестный вариант {var_id}")
                continue
            if not _has_db(var_id):
                print(f"  пропуск {VARIANTS[var_id]}: база не найдена", flush=True)
                continue
            best: dict | None = None
            for _ in range(max(1, a.repeats)):
                old = os.environ.get("NOM_FORMULA_DB")
                os.environ["NOM_FORMULA_DB"] = var_id
                try:
                    r = run_pipeline_once(ds, time_cap=a.time_cap)
                finally:
                    if old is None:
                        os.environ.pop("NOM_FORMULA_DB", None)
                    else:
                        os.environ["NOM_FORMULA_DB"] = old
                if best is None or r["seconds"] < best["seconds"]:
                    best = r
            assert best is not None
            best.update(
                {
                    "variant": var_id,
                    "title": VARIANTS[var_id],
                    "dataset": ds["id"],
                    "kind": ds["kind"],
                }
            )
            results.append(best)
            print(
                f"  {VARIANTS[var_id]:26s} {best['seconds']:8.2f} c | "
                f"назначено {best['assigned']:6d} из {best['src_denoised']:6d} | "
                f"строк {best['rows']:6d} | ok={best['ok']}",
                flush=True,
            )

    print("\n=== СВОДКА ===")
    by_ds: dict[str, list[dict]] = {}
    for r in results:
        by_ds.setdefault(r["dataset"], []).append(r)
    for ds_id, rows in by_ds.items():
        slowest = max(r["seconds"] for r in rows)
        print(f"\n{ds_id}:")
        for r in rows:
            r["speedup"] = round(slowest / r["seconds"], 2) if r["seconds"] else 0.0
            print(
                f"  {r['title']:26s} {r['seconds']:8.2f} c  ×{r['speedup']:<6.2f} "
                f"назначено {r['assigned']:6d}  строк {r['rows']:6d}"
            )

    if a.json:
        Path(a.json).write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
