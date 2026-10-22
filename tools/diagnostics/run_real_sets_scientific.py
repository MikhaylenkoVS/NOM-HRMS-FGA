"""Полный прогон текущих правил на реальных сетах + отчёт для статьи.

Запуск:
    python tools/diagnostics/run_real_sets_scientific.py --datasets all \
        --variant chorsphal --out D:/Temp/User/real_sets_2026-10-22

Скрипт можно прерывать и запускать снова: готовые датасеты пропускаются,
если нет --force.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
import platform
import statistics
import time
from datetime import datetime
from pathlib import Path

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
BASE = Path("data/real_sets")


def _resolve_input(path: str) -> str:
    """RAW/mzML → усреднённая таблица (как в CLI)."""
    low = path.lower()
    if low.endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    if low.endswith(".mzml"):
        from src.core.io.mzml_bridge import mzml_to_json

        return mzml_to_json(path, rt_min=0.0, rt_max=999.0)
    return path


def _hist(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for value in values:
        key = str(int(value))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def _series_summary(df, col: str) -> dict:
    if col not in df.columns:
        return {"present": False}
    values = [int(v) for v in df[col].dropna()]
    if not values:
        return {"present": True, "rows": len(df), "hist": {}, "mean": 0.0}
    raw = (
        [int(v) for v in df[f"{col}_raw"].dropna()]
        if f"{col}_raw" in df.columns
        else values
    )
    amb = (
        [int(v) for v in df[f"{col}_ambiguous"].dropna()]
        if f"{col}_ambiguous" in df.columns
        else [0] * len(values)
    )
    return {
        "present": True,
        "rows": len(df),
        "confirmed_gt0": sum(1 for v in values if v > 0),
        "raw_gt0": sum(1 for v in raw if v > 0),
        "confirmed_mean": round(sum(values) / len(values), 3),
        "raw_mean": round(sum(raw) / len(raw), 3) if raw else 0.0,
        "confirmed_median": statistics.median(values),
        "confirmed_max": max(values),
        "ambiguous_max": max(amb) if amb else 0,
        "confirmed_hist": _hist(values),
        "raw_hist": _hist(raw),
    }


def _dataset_summary(dataset: str, variant: str, seconds: float, res) -> dict:
    st = res.stats
    df = res.table
    summary = {
        "dataset": dataset,
        "variant": variant,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "seconds": round(seconds, 1),
        "ok": bool(res.ok),
        "errors": list(res.errors),
        "peaks": {
            "src_loaded": int(st.src_loaded),
            "dmet_loaded": int(st.dmet_loaded),
            "dacet_loaded": int(st.dacet_loaded),
            "src_denoised": int(st.src_denoised),
            "dmet_denoised": int(st.dmet_denoised),
            "dacet_denoised": int(st.dacet_denoised),
            "dmet_overlap_removed": int(getattr(st, "dmet_overlap_removed", 0) or 0),
            "dacet_overlap_removed": int(getattr(st, "dacet_overlap_removed", 0) or 0),
        },
        "assign": {
            "assigned": int(st.assigned_count),
            "ratio": round(float(st.assigned_ratio), 4),
        },
        "series": {
            "cd3_rows": int(st.dmet.rows),
            "cd3_max_groups": int(st.dmet.max_groups),
            "cd3_missing_total": int(st.dmet.missing_total),
            "cd3co_rows": int(st.dacet.rows),
            "cd3co_max_groups": int(st.dacet.max_groups),
            "cd3co_missing_total": int(st.dacet.missing_total),
        },
        "result": {
            "rows": int(len(df)),
            "unique_formulas": int(df["brutto"].nunique()) if "brutto" in df else 0,
            "n_cooh_gt0": int((df["N_COOH"] > 0).sum()) if "N_COOH" in df else 0,
            "n_oh_gt0": int((df["N_OH"] > 0).sum()) if "N_OH" in df else 0,
            "both_gt0": (
                int(((df["N_COOH"] > 0) & (df["N_OH"] > 0)).sum())
                if {"N_COOH", "N_OH"}.issubset(df.columns)
                else 0
            ),
            "N_COOH": _series_summary(df, "N_COOH"),
            "N_OH": _series_summary(df, "N_OH"),
        },
    }
    if "iso_status" in df:
        counts = df["iso_status"].fillna("").astype(str).value_counts()
        summary["iso_status"] = {str(k): int(v) for k, v in counts.items()}
    return summary


def _write_markdown(
    path: Path,
    summaries: list[dict],
    variant: str,
    meta: dict | None = None,
    reliability: dict[str, dict] | None = None,
) -> None:
    defaults = (meta or {}).get("pipeline_defaults", {})
    lines = [
        "# Анализ реальных сетов по текущим правилам",
        "",
        f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Версия программы: `{(meta or {}).get('version', '—')}`",
        f"Вариант базы формул: `{variant}`",
        "",
        "## Методика",
        "",
        "Полный пайплайн: загрузка RAW → шумоподавление → назначение брутто-формул →",
        "поиск серий CD3/CD3CO → итоговая таблица. Использованы текущие умолчания",
        "`pipeline.json`:",
        "",
        "```text",
        f"ppm_tol={defaults.get('ppm_tol')}  rel_error={defaults.get('rel_error')}  "
        f"max_groups={defaults.get('max_groups')}  max_gaps={defaults.get('max_gaps')}",
        f"require_first_step={defaults.get('require_first_step')}  "
        f"profile_check={defaults.get('profile_check')}  "
        f"significance_level={defaults.get('significance_level')}",
        "```",
        "",
        "`N_COOH` / `N_OH` — подтверждённая reliable-длина серии.",
        "`*_raw` — длина серии до отбрасывания ambiguous-шагов.",
        "В таблице ниже приведены оба значения: raw показывает найденные серии,",
        "confirmed — консервативную оценку после текущих правил надёжности.",
        "",
        "## Сводка",
        "",
        "| Сет | Пиков src | Назначено | Серии CD3 raw | Серии CD3CO raw | Строк | "
        "N_COOH raw>0 | N_COOH conf>0 | N_OH raw>0 | N_OH conf>0 | Время, с |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for s in summaries:
        p, a, r = s["peaks"], s["assign"], s["result"]
        c3 = r.get("N_COOH", {})
        oh = r.get("N_OH", {})
        lines.append(
            f"| {s['dataset']} | {p['src_denoised']:,} | {a['assigned']:,} | "
            f"{s['series']['cd3_rows']:,} | {s['series']['cd3co_rows']:,} | "
            f"{r['rows']:,} | {c3.get('raw_gt0', 0):,} | "
            f"{c3.get('confirmed_gt0', 0):,} | {oh.get('raw_gt0', 0):,} | "
            f"{oh.get('confirmed_gt0', 0):,} | {s['seconds']:.0f} |".replace(",", " ")
        )
    if reliability:
        lines += ["", "## Надёжность ступеней серий", ""]
        lines += [
            "| Сет | CD3 reliable | CD3 ambiguous | CD3CO reliable | CD3CO ambiguous |",
            "|---|---:|---:|---:|---:|",
        ]
        for s in summaries:
            rel = reliability.get(s["dataset"], {})
            c3 = rel.get("N_COOH_details", {})
            oh = rel.get("N_OH_details", {})
            c3st = c3.get("statuses", {})
            ohst = oh.get("statuses", {})
            lines.append(
                f"| {s['dataset']} | {c3st.get('reliable', 0):,} | "
                f"{c3st.get('ambiguous', 0):,} | {ohst.get('reliable', 0):,} | "
                f"{ohst.get('ambiguous', 0):,} |".replace(",", " ")
            )
        lines += [
            "",
            "Reliable — ступень без штрафов после текущих правил; ambiguous —",
            "ступень с хотя бы одним штрафом (изотоп, source overlap, конфликт,",
            "O-лимит и т.п.). Подробные причины — `reliability.json`.",
            "",
            "| Сет | isotope | source_overlap | conflict_overlap | o_excess |",
            "|---|---:|---:|---:|---:|",
        ]
        for s in summaries:
            rel = reliability.get(s["dataset"], {})
            pens: dict[str, int] = {}
            for key in ("N_COOH_details", "N_OH_details"):
                for name, count in (rel.get(key, {}).get("penalties") or {}).items():
                    pens[name] = pens.get(name, 0) + int(count)
            lines.append(
                f"| {s['dataset']} | {pens.get('isotope', 0):,} | "
                f"{pens.get('source_overlap', 0):,} | "
                f"{pens.get('conflict_overlap', 0):,} | "
                f"{pens.get('o_excess', 0):,} |".replace(",", " ")
            )
        lines += [
            "",
            "## Ограничения интерпретации",
            "",
            "- `*_raw` — найденные кандидатные серии; не все они подтверждены.",
            "- `N_COOH`/`N_OH` — консервативная reliable-длина; большое число",
            "  ambiguous-ступеней связано с изотопным паттерном, наложениями",
            "  source/derivative и конфликтами серий.",
            "- В этом прогоне не применялись target-decoy FDR и ортогональная",
            "  валидация; результаты следует рассматривать как рабочий срез,",
            "  а не как окончательно валидированные значения для публикации.",
            "- Использована база `chorsphal`; сборка exe по умолчанию содержит",
            "  CHNOSP, поэтому абсолютные числа могут немного отличаться.",
        ]

    lines += ["", "## Распределения подтверждённых групп", ""]
    for s in summaries:
        lines += [f"### {s['dataset']}", ""]
        for col in ("N_COOH", "N_OH"):
            r = s["result"].get(col, {})
            if not r.get("present"):
                continue
            lines.append(
                f"- **{col}**: >0 — {r.get('confirmed_gt0', 0)}; "
                f"среднее — {r.get('confirmed_mean', 0):.3f}; "
                f"медиана — {r.get('confirmed_median', 0)}; "
                f"максимум — {r.get('confirmed_max', 0)}"
            )
            hist = ", ".join(
                f"{k}: {v}" for k, v in r.get("confirmed_hist", {}).items()
            )
            lines.append(f"  - confirmed: {hist or '—'}")
            raw_hist = ", ".join(f"{k}: {v}" for k, v in r.get("raw_hist", {}).items())
            lines.append(f"  - raw: {raw_hist or '—'}")
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--datasets", default="all")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--out", default="D:/Temp/User/real_sets_2026-10-22")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    wanted = {
        name
        for name, triple in REAL_SETS.items()
        if args.datasets.strip().lower() in ("all", "real")
        or name.lower() in {x.strip().lower() for x in args.datasets.split(",")}
    }
    selected = [name for name in REAL_SETS if name in wanted]
    if not selected:
        raise SystemExit("реальные сеты не найдены")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    old = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = args.variant
    try:
        from src import __version__
        from src.configs import PIPELINE
        from src.core import run_pipeline

        meta = {
            "version": __version__,
            "variant": args.variant,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "started": datetime.now().isoformat(timespec="seconds"),
            "datasets": selected,
            "pipeline_defaults": dict(PIPELINE.run_pipeline_defaults),
        }
        try:
            from src.core.formula_db._variants import active_variant, find_variant_path

            _db = active_variant()
            if _db is not None:
                _mp = find_variant_path(_db)
                _fdb = (
                    _mp.with_name(_mp.name.replace(".manifest.json", ".fdb"))
                    if _mp is not None
                    else None
                )
                meta["database"] = {
                    "id": _db.id,
                    "title": _db.title,
                    "manifest": str(_mp) if _mp else None,
                    "fdb": str(_fdb) if _fdb and _fdb.is_file() else None,
                    "fdb_size_bytes": (
                        _fdb.stat().st_size if _fdb and _fdb.is_file() else None
                    ),
                }
        except Exception:
            pass
        (out / "run_metadata.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        summaries: dict[str, dict] = {}
        old_summary_path = out / "summary.json"
        if old_summary_path.is_file():
            try:
                for item in json.loads(old_summary_path.read_text(encoding="utf-8")):
                    summaries[item["dataset"]] = item
            except Exception:
                pass
        # Восстанавливаем отдельные summary, даже если общий файл был
        # перезаписан прогоном подмножества датасетов.
        for _name in REAL_SETS:
            _p = out / _name / "summary.json"
            if _name not in summaries and _p.is_file():
                try:
                    summaries[_name] = json.loads(_p.read_text(encoding="utf-8"))
                except Exception:
                    pass
        for name in selected:
            set_dir = BASE / name
            src, dmet, dacet = (
                _resolve_input(str(set_dir / f)) for f in REAL_SETS[name]
            )
            dataset_out = out / name
            summary_path = dataset_out / "summary.json"
            result_path = dataset_out / "result.csv.gz"
            if not args.force and summary_path.is_file() and result_path.is_file():
                print(f"[SKIP] {name}: уже готово", flush=True)
                summaries[name] = json.loads(summary_path.read_text(encoding="utf-8"))
                continue

            dataset_out.mkdir(parents=True, exist_ok=True)
            print(f"\n[RUN] {name}", flush=True)
            t0 = time.perf_counter()
            res = run_pipeline(
                src_path=src,
                dmet_path=dmet,
                dacet_path=dacet,
                sep=",",
                visualize=False,
                use_cache=False,
            )
            seconds = time.perf_counter() - t0
            summary = _dataset_summary(name, args.variant, seconds, res)
            summary_path.write_text(
                json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            with gzip.open(result_path, "wt", encoding="utf-8", newline="") as fh:
                res.table.to_csv(fh, index=False)
            summaries[name] = summary
            print(
                f"[DONE] {name}: {seconds:.0f} c, строк {len(res.table)}, "
                f"N_COOH>0 {summary['result']['n_cooh_gt0']}, "
                f"N_OH>0 {summary['result']['n_oh_gt0']}",
                flush=True,
            )

        reliabilities: dict[str, dict] = {}
        for _name in REAL_SETS:
            _p = out / _name / "reliability.json"
            if _p.is_file():
                try:
                    reliabilities[_name] = json.loads(_p.read_text(encoding="utf-8"))
                except Exception:
                    pass
        ordered = [summaries[name] for name in REAL_SETS if name in summaries]
        (out / "summary.json").write_text(
            json.dumps(ordered, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        _write_markdown(out / "REPORT.md", ordered, args.variant, meta, reliabilities)
        print(f"\nОтчёт: {out / 'REPORT.md'}", flush=True)
    finally:
        if old is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old


if __name__ == "__main__":
    main()
