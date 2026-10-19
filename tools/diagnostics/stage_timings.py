"""Длительность каждого этапа пайплайна на каждом сете (тест-сеты и реальные RAW).

Этапы замеряются обёртками вокруг тех самых функций, которые вызывает
``run_pipeline`` (патчим имена в модуле ``src.core.pipeline._run``), поэтому
production-код не меняется, а цифры соответствуют реальному прогону.

Этапы:
  1. preprocess    — усреднение RAW в таблицу (для реальных сетов; для CSV ≈ 0);
  2. load          — загрузка спектров;
  3. denoise       — шумоподавление;
  4. assign        — назначение брутто-формул;
  5. series_cd3    — серии дейтерометилирования (N_COOH);
  6. series_cd3co  — серии дейтероацилирования (N_OH);
  7. result_table  — сборка итоговой таблицы;
  8. прочее        — всё остальное (инициализация, логирование).

Запуск:
  python tools/diagnostics/stage_timings.py --datasets real --variants chorsphal chnosp \
      --json D:/Temp/User/stage_timings_real.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

from src.core.pipeline import _run as RUN

STAGES = (
    "preprocess",
    "load",
    "denoise",
    "assign",
    "series_cd3",
    "series_cd3co",
    "result_table",
)

#: Реальные сеты: id → (исходник, CD3, CD3CO). Порядок — от быстрых к долгим.
REAL_SETS: dict[str, tuple[str, str, str]] = {
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
        "Fulvagra_prep HPLC_FR14_CD3OD mod_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR14_AC-D4_ESI_1e6_480k_128_m-s.raw",
    ),
}


def _resolve_input(path: str | None) -> tuple[str | None, float]:
    """RAW/mzML → усреднённая таблица (как в CLI). Возвращает (путь, секунды)."""
    if not path:
        return None, 0.0
    low = path.lower()
    t0 = time.perf_counter()
    if low.endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0), time.perf_counter() - t0
    if low.endswith(".mzml"):
        from src.core.io.mzml_bridge import mzml_to_json

        return mzml_to_json(path, rt_min=0.0, rt_max=999.0), time.perf_counter() - t0
    return path, time.perf_counter() - t0


def _wrap(name: str, timings: dict[str, float], key: str, counter: dict[str, int]):
    """Обёртка: копит время вызовов в ``timings``.

    Если функция вызывается несколько раз, ключ получает суффикс ``#2`` и т. п.
    """
    original = getattr(RUN, name)

    def wrapper(*args, **kwargs):
        n = counter.get(key, 0) + 1
        counter[key] = n
        used_key = key if n == 1 else f"{key}#{n}"
        t0 = time.perf_counter()
        try:
            return original(*args, **kwargs)
        finally:
            timings[used_key] = timings.get(used_key, 0.0) + time.perf_counter() - t0

    setattr(RUN, name, wrapper)
    return original


def measure(ds: dict, *, variant: str, sep: str) -> dict:
    timings: dict[str, float] = {}
    counter: dict[str, int] = {}

    # усреднение RAW — до пайплайна, но это его реальная стоимость
    src, t_src = _resolve_input(ds["src"])
    dmet, t_dmet = _resolve_input(ds["dmet"])
    dacet, t_dacet = _resolve_input(ds["dacet"])
    timings["preprocess"] = t_src + t_dmet + t_dacet

    saved = {
        name: _wrap(name, timings, key, counter)
        for name, key in (
            ("_load_triple", "load"),
            ("_denoise_triple", "denoise"),
            ("assign_formulas", "assign"),
            ("_find_series_stage", "series"),
            ("build_result_table", "result_table"),
        )
    }
    old = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = variant
    try:
        t0 = time.perf_counter()
        res = RUN.run_pipeline(
            src_path=src,
            dmet_path=dmet,
            dacet_path=dacet,
            sep=sep,
            visualize=False,
            use_cache=False,
        )
        total = time.perf_counter() - t0
    finally:
        for name, original in saved.items():
            setattr(RUN, name, original)
        if old is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old

    series = [timings.get("series", 0.0)]
    for k in ("series#2", "series#3"):
        if k in timings:
            series.append(timings[k])
    out = {
        "dataset": ds["id"],
        "variant": variant,
        "preprocess": round(timings.get("preprocess", 0.0), 2),
        "load": round(timings.get("load", 0.0), 2),
        "denoise": round(timings.get("denoise", 0.0), 2),
        "assign": round(timings.get("assign", 0.0), 2),
        "series_cd3": round(series[0], 2),
        "series_cd3co": round(series[1] if len(series) > 1 else 0.0, 2),
        "result_table": round(timings.get("result_table", 0.0), 2),
        "total": round(total + timings.get("preprocess", 0.0), 2),
        "assigned": int(getattr(res.stats, "assigned_count", 0) or 0),
        "peaks": int(getattr(res.stats, "src_denoised", 0) or 0),
    }
    out["other"] = round(out["total"] - sum(out[k] for k in STAGES), 2)
    return out


def discover(kind: str) -> list[dict]:
    """Список датасетов: 'test', 'real', 'all' или id через запятую."""
    want = kind.strip().lower()
    sets = [s.strip().lower() for s in want.split(",") if s.strip()]

    def _want(name: str, group: str) -> bool:
        if want in ("all", ""):
            return True
        if want == group:
            return True
        return name.lower() in sets

    out: list[dict] = []
    if _want("test", "test"):
        for d in sorted(Path("data/test_sets").glob("set_*")):
            if d.name.lower() in sets or want in ("all", "", "test"):
                if (d / "original.csv").is_file():
                    out.append(
                        {
                            "id": d.name,
                            "src": str(d / "original.csv"),
                            "dmet": str(d / "deutermethylated.csv"),
                            "dacet": str(d / "deuteroacylated.csv"),
                        }
                    )
    base = Path("data/real_sets")
    for name, (s, m, a) in REAL_SETS.items():
        if not _want(name, "real"):
            continue
        d = base / name
        if (d / s).is_file():
            out.append(
                {
                    "id": name,
                    "src": str(d / s),
                    "dmet": str(d / m) if (d / m).is_file() else None,
                    "dacet": str(d / a) if (d / a).is_file() else None,
                }
            )
    return out


def _print_table(rows: list[dict]) -> None:
    names = {
        "preprocess": "усреднение RAW",
        "load": "загрузка",
        "denoise": "шумоподавл.",
        "assign": "назначение",
        "series_cd3": "серии CD3",
        "series_cd3co": "серии CD3CO",
        "result_table": "итог. таблица",
        "other": "прочее",
        "total": "ВСЕГО",
    }
    by_ds: dict[str, list[dict]] = {}
    for r in rows:
        by_ds.setdefault(r["dataset"], []).append(r)

    for ds_id, group in by_ds.items():
        variants = [r["variant"] for r in group]
        print(f"\n=== {ds_id} ===")
        head = f"{'этап':16s}" + "".join(f"{v:>12s}" for v in variants)
        print(head)
        print("-" * len(head))
        for key in (*STAGES, "other", "total"):
            share = ""
            if key == "assign" and group:
                share = " | доля назначения " + ", ".join(
                    f"{r['variant']}: {r['assign'] / r['total'] * 100:.1f}%"
                    for r in group
                    if r["total"]
                )
            print(
                f"{names[key]:16s}" + "".join(f"{r[key]:12.2f}" for r in group) + share
            )
        print(
            "назначено/пиков:",
            ", ".join(f"{r['variant']}: {r['assigned']}/{r['peaks']}" for r in group),
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--datasets", default="test", help="test | real | all | список id через запятую"
    )
    ap.add_argument("--variants", nargs="*", default=["chnosp"])
    ap.add_argument("--sep", default=",")
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    sets = discover(a.datasets)
    if not sets:
        raise SystemExit("датасеты не найдены")

    rows: list[dict] = []
    for ds in sets:
        for variant in a.variants:
            print(f"[{time.strftime('%H:%M:%S')}] {ds['id']} / {variant} …", flush=True)
            row = measure(ds, variant=variant, sep=a.sep)
            rows.append(row)
            print(
                f"[{time.strftime('%H:%M:%S')}] {ds['id']} / {variant}: "
                f"всего {row['total']:.1f} c (назначение {row['assign']:.1f} c, "
                f"{row['assign'] / row['total'] * 100:.1f} %)",
                flush=True,
            )
            if a.json:  # пишем после каждого прогона — частичные результаты сохраняются
                Path(a.json).write_text(
                    json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
                )

    _print_table(rows)
    if a.json:
        print(f"\nзаписано: {a.json}")


if __name__ == "__main__":
    main()
