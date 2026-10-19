"""Откуда берутся конфликты пиков и насколько они реальны.

Скрипт повторяет подготовку ``ablation_f16.py`` (загрузка, денойз, assign,
серии CD3/CD3CO) и разбирает каждый кластер пика, который делят ≥ 2 серии.

Ключевой факт: если две серии делят один и тот же пик на ступенях ``a`` и ``b``,
то их исходные массы автоматически отличаются на ``(a - b)·Δ`` — «Δ-лестница»
возникает по построению и сама по себе ничего не доказывает. Поэтому каждая
неоднозначная серия классифицируется по тому, **совпадает ли вся её цепочка**
со сдвинутой цепочкой конкурента:

* ``same_precursor`` — пик делится на одной и той же ступени (Δm0 ≈ 0):
  дубль назначения одной исходной массы;
* ``alias`` — ≥ 80 % ступеней серии совпадают со сдвинутыми ступенями
  конкурента: серия является «эхом» уже найденной цепочки;
* ``partial`` — совпадает часть ступеней (34–80 %);
* ``independent`` — совпадает только сам спорный пик: цепочки разные,
  а пик — реальное случайное наложение двух соединений.

Для ``alias``/``same_precursor`` конфликт «реален», но серия избыточна
(дубль). Для ``independent`` выбрасывать серию — потеря реальных данных.

Рабочий режим — **без фильтра правдоподобия** (он выключен в пайплайне:
влияние конфликтов на реальные серии минимально). Отчёт дополнительно считает
экспериментальный вариант `plausible_only` (CHNOPS, без галогенов, S ≤ 2,
P ≤ 1, N ≤ 5, отношения H/C, O/C, N/C, S/C, P/C, DBE ≥ 0) — сколько
ambiguous осталось бы, если не считать конфликты с абсурдными формулами.

Первый прогон ~10 мин; результат кешируется, повторный анализ:
  python tools/diagnostics/conflict_pairs_f16.py --reuse

Запуск:
  python tools/diagnostics/conflict_pairs_f16.py \
      --json D:/Temp/User/conflicts_f16.json \
      --csv D:/Temp/User/conflicts_f16_pairs.csv
"""

from __future__ import annotations

import argparse
import json
import os
import time
from collections import Counter
from pathlib import Path

import pandas as pd

from ablation_f16 import DECOYS, REAL, resolve

from src.configs import CHEM, PIPELINE
from src.core.domain.molecule import parse_formula
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.pipeline._run import _search_config_from_brutto
from src.core.spectrum import assign_formulas, denoise, find_series
from src.core.spectrum._conflicts import analyze_conflicts, mark_conflicts
from src.core.spectrum._decoy import DECOY_SEED, decoy_shifts
from src.core.spectrum._formula_check import is_plausible_brutto
from src.core.spectrum._formula_source import open_formula_db
from src.core.spectrum._load import load_spectrum
from src.core.spectrum._series import _theor_ion_mass_cached
from src.core.spectrum._validate import attach_fdr, attach_formula_check

#: Допуск на «ту же исходную массу» (ppm).
SAME_PPM = 5.0
#: Допуск на совпадение пиков соседних ступеней, Да.
PEAK_DA = 0.001
#: Точное совпадение m/z (один и тот же пик таблицы).
EXACT_DA = 1e-9
#: Порог доли совпавших ступеней для «эха» и «частичного» совпадения.
ALIAS_FRAC = 0.8
PARTIAL_FRAC = 0.34
KINDS = ("same_precursor", "alias", "partial", "independent")
PRIORITY = {name: i for i, name in enumerate(KINDS)}
EXAMPLES_PER_GROUP = 4


def _m0_theor(brutto: str, ion_mode: str, fallback: float) -> float:
    try:
        return float(_theor_ion_mass_cached(str(brutto), ion_mode))
    except Exception:
        return float(fallback)


def _row_info(df: pd.DataFrame, idx: int, step: int, ion_mode: str) -> dict:
    row = df.iloc[idx]
    m0_obs = float(row["mass_src"])
    mz_by_step = {
        pos + 1: float(mz) for pos, mz in enumerate(row["series_mz"]) if mz is not None
    }
    return {
        "row": int(idx),
        "m0": _m0_theor(row.get("brutto", ""), ion_mode, m0_obs),
        "m0_obs": m0_obs,
        "brutto": str(row.get("brutto", "")),
        "n_groups": int(row["n_groups"]),
        "step": int(step),
        "steps_found": [int(s) for s in row["steps_found"]],
        "mz_by_step": mz_by_step,
        "significant": bool(row.get("significant", False)),
        "q_value": float(row["q_value"]) if "q_value" in df.columns else None,
        "fdr_significant": bool(row.get("fdr_significant", False)),
        "formula_ok": bool(row.get("formula_ok", False)),
        "formula_reason": str(row.get("formula_reason", "")),
        "ambiguous": bool(row.get("ambiguous", False)),
    }


def _alias_stats(loser: dict, ref: dict) -> dict:
    """Сколько ступеней серии ``loser`` совпадает со сдвинутой цепочкой ``ref``.

    Пик делится на ступенях ``ref["step"]`` и ``loser["step"]``; сдвиг
    ``k = ref.step - loser.step``. Для каждой ступени ``j`` серии ``loser``
    проверяется пик ``j + k`` у ``ref``.

    Совпадение считается **точным**, если m/z равны как числа: обе серии
    строятся по одной таблице пиков, поэтому один и тот же пик даёт
    бит-в-бит одинаковое значение. Допуск ``PEAK_DA`` учитывает только
    «рядом лежащие» пики и в дробь ``alias_frac`` не входит.
    """
    k = int(ref["step"]) - int(loser["step"])
    matched: list[int] = []
    near: list[int] = []
    comparable = 0
    for step, mz in loser["mz_by_step"].items():
        other_mz = ref["mz_by_step"].get(step + k)
        if other_mz is None:
            continue
        comparable += 1
        diff = abs(float(mz) - float(other_mz))
        if diff <= EXACT_DA:
            matched.append(int(step))
        elif diff <= PEAK_DA:
            near.append(int(step))
    frac = len(matched) / comparable if comparable else 0.0
    near_frac = len(near) / comparable if comparable else 0.0
    return {
        "k_step": k,
        "alias_frac": frac,
        "near_frac": near_frac,
        "matched_steps": len(matched),
        "near_steps": len(near),
        "comparable_steps": comparable,
        "matched_positions": matched,
    }


def _kind(stats: dict) -> str:
    if stats["k_step"] == 0:
        return "same_precursor"
    # Меньше двух сравнимых ступеней — судить не о чем: конкурент слишком
    # короткий, чтобы объяснить цепочку.
    if stats["comparable_steps"] < 2:
        return "independent"
    if stats["alias_frac"] >= ALIAS_FRAC:
        return "alias"
    if stats["alias_frac"] >= PARTIAL_FRAC:
        return "partial"
    return "independent"


def _rank(stats: dict, kind: str) -> tuple[int, float]:
    """Сильнейшее объяснение: дубль → эхо → частичное → независимость."""
    return (PRIORITY[kind], -stats["alias_frac"])


def _best_explanation(row: dict, others: list[dict]) -> dict | None:
    best = None
    for other in others:
        if other["row"] == row["row"]:
            continue
        stats = _alias_stats(row, other)
        kind = _kind(stats)
        if best is None or _rank(stats, kind) < _rank(best["stats"], best["kind"]):
            best = {"kind": kind, "stats": stats, "other": other}
    return best


def _quality(records: list[dict]) -> dict:
    return {
        "n": len(records),
        "fdr_significant": sum(1 for r in records if r["row"]["fdr_significant"]),
        "formula_ok": sum(1 for r in records if r["row"]["formula_ok"]),
        "fdr_and_formula": sum(
            1 for r in records if r["row"]["fdr_significant"] and r["row"]["formula_ok"]
        ),
        "n_groups_ge4": sum(1 for r in records if r["row"]["n_groups"] >= 4),
        "fdr_formula_len4": sum(
            1
            for r in records
            if r["row"]["fdr_significant"]
            and r["row"]["formula_ok"]
            and r["row"]["n_groups"] >= 4
        ),
        "supported_ge2": sum(1 for r in records if r["supported_n"] >= 2),
        "median_n_groups": (
            float(pd.Series([r["row"]["n_groups"] for r in records]).median())
            if records
            else 0.0
        ),
    }


def _supported_bucket(n: int) -> str:
    return "0" if n == 0 else ("1" if n == 1 else "2+")


def analyze_frame(
    df: pd.DataFrame, group: str, decoys, counts_by_brutto, ion_mode: str
) -> tuple[dict, list[dict]]:
    """Разметить серии и вернуть (сводка, записи неоднозначных серий)."""
    marked = attach_formula_check(df, group, counts_by_brutto)
    marked = attach_fdr(marked, decoys)
    # Рабочий режим — без фильтра правдоподобия (он выключен в пайплайне).
    marked = mark_conflicts(marked).reset_index(drop=True)
    clusters = analyze_conflicts(marked)
    # Эксперимент: сколько конфликтов осталось бы только по правдоподобным.
    plausible = [bool(is_plausible_brutto(str(b))[0]) for b in marked["brutto"]]
    filtered = mark_conflicts(marked, plausible_only=True)
    ambiguous_filtered = int(filtered["ambiguous"].sum())

    cluster_of: dict[float, dict] = {}
    for cluster in clusters:
        for m in cluster["members"]:
            cluster_of[m["mz"]] = cluster

    records: list[dict] = []
    for row_index, row in marked.iterrows():
        if not bool(row["ambiguous"]):
            continue
        mz_list = list(row["series_mz"])
        steps = [pos + 1 for pos, mz in enumerate(mz_list) if mz is not None]
        if not steps:
            continue
        last_step = max(steps)
        cluster = cluster_of.get(float(mz_list[last_step - 1]))
        if cluster is None:
            continue
        members = [
            _row_info(marked, m["row"], m["step"], ion_mode) for m in cluster["members"]
        ]
        me = next((m for m in members if m["row"] == row_index), None)
        if me is None:
            continue
        best = _best_explanation(me, members)
        if best is None:
            continue
        stats = best["stats"]
        records.append(
            {
                "kind": best["kind"],
                "peak_mz": round(float(mz_list[last_step - 1]), 6),
                "cluster_spread_mDa": round(
                    (cluster["end"] - cluster["start"]) * 1000.0, 4
                ),
                "n_in_cluster": len({m["row"] for m in members}),
                "supported_n": len(cluster["supported"]),
                "has_owner": cluster["owner"] is not None,
                "row": me,
                "other": best["other"],
                "dm0": float(me["m0"]) - float(best["other"]["m0"]),
                **stats,
            }
        )

    by_kind = {name: [] for name in KINDS}
    for rec in records:
        by_kind[rec["kind"]].append(rec)
    by_supported = {b: [] for b in ("0", "1", "2+")}
    for rec in records:
        by_supported[_supported_bucket(rec["supported_n"])].append(rec)

    explained = by_kind["same_precursor"] + by_kind["alias"]
    unexplained = by_kind["partial"] + by_kind["independent"]
    summary = {
        "group": group,
        "n_series": int(len(marked)),
        "n_significant": int(marked["significant"].sum()),
        "n_implausible": int(sum(1 for v in plausible if not v)),
        "share_implausible": round(
            float(sum(1 for v in plausible if not v)) / max(1, len(plausible)), 4
        ),
        "n_ambiguous": int(marked["ambiguous"].sum()),
        "share_ambiguous": round(float(marked["ambiguous"].mean()), 4),
        "n_ambiguous_plausible_only": ambiguous_filtered,
        "share_ambiguous_plausible_only": round(
            ambiguous_filtered / max(1, len(marked)), 4
        ),
        "n_clusters": len(clusters),
        "clusters_by_supported": dict(
            Counter(_supported_bucket(len(c["supported"])) for c in clusters)
        ),
        "ambiguous_by_kind": {name: len(items) for name, items in by_kind.items()},
        "explained_by_other_series": len(explained),
        "unexplained_by_other_series": len(unexplained),
        "ambiguous_quality": _quality(records),
        "by_kind": {name: _quality(items) for name, items in by_kind.items()},
        "explained_quality": _quality(explained),
        "unexplained_quality": _quality(unexplained),
        "by_supported": {
            bucket: {
                "n": len(items),
                "kinds": dict(Counter(r["kind"] for r in items)),
                "quality": _quality(items),
            }
            for bucket, items in by_supported.items()
        },
        "cluster_size_hist": dict(
            Counter(
                len({m["row"] for m in c["members"]}) for c in clusters
            ).most_common()
        ),
        "alias_frac_bins": _frac_bins([r["alias_frac"] for r in records]),
        "near_frac_bins": _frac_bins([r["near_frac"] for r in records]),
    }
    return summary, records


def _frac_bins(values) -> dict:
    out = Counter()
    for v in values:
        if v == 0:
            out["0"] += 1
        elif v < PARTIAL_FRAC:
            out["0–0.34"] += 1
        elif v < ALIAS_FRAC:
            out["0.34–0.8"] += 1
        else:
            out["0.8–1"] += 1
    return dict(out)


def _example_sort_key(rec: dict) -> tuple:
    return (
        int(rec["row"]["fdr_significant"])
        + int(rec["row"]["formula_ok"])
        + int(rec["row"]["n_groups"] >= 4)
        + int(rec["supported_n"] >= 2),
        rec["row"]["n_groups"],
    )


def collect_examples(records: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = {}
    for rec in records:
        key = (rec["kind"], _supported_bucket(rec["supported_n"]))
        groups.setdefault(key, []).append(rec)
    examples: list[dict] = []
    for key in sorted(groups):
        subset = sorted(groups[key], key=_example_sort_key, reverse=True)
        examples.extend(subset[:EXAMPLES_PER_GROUP])
    return examples


def prepare(dataset: str, variant: str, cache_dir: Path):
    """Тяжёлая подготовка; результат кешируется в ``cache_dir``."""
    s, m, d = REAL[dataset]
    base = Path("data/real_sets") / dataset
    defaults = PIPELINE.run_pipeline_defaults

    src_raw = load_spectrum(resolve(str(base / s)), sep=",")
    dmet_raw = load_spectrum(resolve(str(base / m)), sep=",")
    dacet_raw = load_spectrum(resolve(str(base / d)), sep=",")
    src_original = src_raw.copy()
    src = denoise(src_raw, force=defaults["noise_force"])
    dmet = denoise(dmet_raw, force=2.0)
    dacet = denoise(dacet_raw, force=2.0)
    print(f"[{time.strftime('%H:%M:%S')}] загрузка+денойз готовы", flush=True)

    ion_mode = _ion_mode_from_sign(defaults["sign"])
    formula_db = open_formula_db()
    try:
        src = assign_formulas(
            src,
            rel_error_ppm=defaults["rel_error"],
            mass_min=defaults["assign_mass_min"],
            mass_max=defaults["assign_mass_max"],
            search_config=_search_config_from_brutto(None),
            ion_mode=ion_mode,
            isotope_filter=True,
            isotope_variants=True,
            original=src_original,
            formula_db=formula_db,
        )
    finally:
        if formula_db is not None:
            formula_db.close()
    print(
        f"[{time.strftime('%H:%M:%S')}] назначено {int(src.table['assign'].sum())}",
        flush=True,
    )

    kw = dict(
        ppm_tol=defaults["ppm_tol"],
        max_groups=defaults["max_groups"],
        max_gaps=defaults["max_gaps"],
        require_first_step=True,
        significance_level=defaults["significance_level"],
    )
    d_cd3 = CHEM.derivatization_shifts["delta_cd3"]
    d_cd3co = CHEM.derivatization_shifts["delta_cd3co"]
    c3 = find_series(src, dmet, d_cd3, **kw)
    c3co = find_series(src, dacet, d_cd3co, **kw)
    print(
        f"[{time.strftime('%H:%M:%S')}] серии: CD3 {len(c3)}, CD3CO {len(c3co)}",
        flush=True,
    )

    shifts = decoy_shifts(d_cd3, k=DECOYS, seed=DECOY_SEED)
    dec3 = [find_series(src, dmet, d_cd3 + sh, **kw) for sh in shifts]
    dec3co = [find_series(src, dacet, d_cd3co + sh, **kw) for sh in shifts]
    print(f"[{time.strftime('%H:%M:%S')}] decoy готовы", flush=True)

    cache_dir.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(
        {"c3": c3, "c3co": c3co, "dec3": dec3, "dec3co": dec3co},
        cache_dir / "series.pkl",
    )
    return c3, c3co, dec3, dec3co


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--json", default="D:/Temp/User/conflicts_f16.json")
    ap.add_argument("--csv", default="D:/Temp/User/conflicts_f16_pairs.csv")
    ap.add_argument("--cache-dir", default="D:/Temp/User/conflict_cache")
    ap.add_argument("--reuse", action="store_true", help="взять серии из кеша")
    a = ap.parse_args()

    cache_dir = Path(a.cache_dir)
    payload = cache_dir / "series.pkl"
    defaults = PIPELINE.run_pipeline_defaults
    ion_mode = _ion_mode_from_sign(defaults["sign"])
    old_env = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = a.variant
    t0 = time.perf_counter()
    try:
        if a.reuse and payload.exists():
            cached = pd.read_pickle(payload)
            c3, c3co = cached["c3"], cached["c3co"]
            dec3, dec3co = cached["dec3"], cached["dec3co"]
            print(f"[{time.strftime('%H:%M:%S')}] серии из кеша {payload}", flush=True)
        else:
            c3, c3co, dec3, dec3co = prepare(a.dataset, a.variant, cache_dir)

        counts_by_brutto = {}
        for brutto in pd.concat([c3["brutto"], c3co["brutto"]]).unique():
            try:
                counts_by_brutto[str(brutto)] = parse_formula(str(brutto))
            except Exception:
                continue

        report: dict = {
            "dataset": a.dataset,
            "variant": a.variant,
            "decoy_shifts": len(dec3),
            "decoy_seed": DECOY_SEED,
            "same_ppm": SAME_PPM,
            "peak_Da": PEAK_DA,
            "exact_Da": EXACT_DA,
            "alias_frac": ALIAS_FRAC,
            "partial_frac": PARTIAL_FRAC,
            "categories": {},
            "examples": [],
        }
        all_records: list[dict] = []
        for label, frame, group, decoys in (
            ("N_COOH", c3, "cd3", dec3),
            ("N_OH", c3co, "cd3co", dec3co),
        ):
            summary, records = analyze_frame(
                frame, group, decoys, counts_by_brutto, ion_mode
            )
            report["categories"][label] = summary
            report["examples"].extend(
                {"derivative": label, **rec} for rec in collect_examples(records)
            )
            all_records.extend({"derivative": label, **rec} for rec in records)
            print(
                f"[{time.strftime('%H:%M:%S')}] {label}: {summary['n_series']} серий, "
                f"ambiguous {summary['n_ambiguous']} "
                f"({summary['share_ambiguous']:.1%}), "
                f"кластеров {summary['n_clusters']}, "
                f"по классам {summary['ambiguous_by_kind']}",
                flush=True,
            )

        report["seconds"] = round(time.perf_counter() - t0, 1)
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        if all_records:
            flat = pd.json_normalize(all_records, sep=".")
            Path(a.csv).parent.mkdir(parents=True, exist_ok=True)
            flat.to_csv(a.csv, index=False, sep=";", encoding="utf-8-sig")
    finally:
        if old_env is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old_env

    print("\n=== КОНФЛИКТЫ (F16) ===")
    for label, r in report["categories"].items():
        print(
            f"\n{label}: серий {r['n_series']}, "
            f"неправдоподобных {r['n_implausible']} "
            f"({r['share_implausible']:.1%}), ambiguous {r['n_ambiguous']} "
            f"({r['share_ambiguous']:.1%})"
        )
        print(
            f"  эксперимент (plausible_only): ambiguous было бы "
            f"{r['n_ambiguous_plausible_only']} "
            f"({r['share_ambiguous_plausible_only']:.1%})"
        )
        print(f"  кластеры по supported: {r['clusters_by_supported']}")
        print(f"  классы: {r['ambiguous_by_kind']}")
        print(f"  доля точных совпадений ступеней: {r['alias_frac_bins']}")
        print(f"  доля совпадений в пределах 1 мДа: {r['near_frac_bins']}")
        print(
            f"  объяснимы другой серией: {r['explained_by_other_series']}, "
            f"не объяснимы: {r['unexplained_by_other_series']}"
        )
        print(
            f"  сильных (FDR+формула+N≥4): объяснимые "
            f"{r['explained_quality']['fdr_formula_len4']}, "
            f"необъяснимые {r['unexplained_quality']['fdr_formula_len4']}"
        )
        for name in KINDS:
            q = r["by_kind"][name]
            if q["n"]:
                print(
                    f"    {name}: n={q['n']}, FDR={q['fdr_significant']}, "
                    f"формула={q['formula_ok']}, "
                    f"FDR+формула={q['fdr_and_formula']}, "
                    f"N≥4={q['n_groups_ge4']}, "
                    f"FDR+формула+N≥4={q['fdr_formula_len4']}"
                )
        for bucket, info in r["by_supported"].items():
            print(
                f"  supported={bucket}: n={info['n']}, {info['kinds']}, "
                f"strong={info['quality']['fdr_formula_len4']}"
            )

    print("\n=== ПРИМЕРЫ ===")
    for e in report["examples"][:80]:
        me, other = e["row"], e["other"]
        print(
            f"[{e['derivative']}/{e['kind']}/sup{e['supported_n']}] "
            f"пик {e['peak_mz']:.4f}: серия {me['brutto']} m0={me['m0']:.4f} "
            f"шаг {me['step']} N={me['n_groups']} | конкурент {other['brutto']} "
            f"m0={other['m0']:.4f} шаг {other['step']} N={other['n_groups']} | "
            f"точно совпало {e['matched_steps']}/{e['comparable_steps']} "
            f"ступеней ({e['alias_frac']:.0%}), рядом {e['near_steps']}, "
            f"шаги {e['matched_positions']}, "
            f"q={me['q_value']}, формула={me['formula_ok']}"
        )
    print(f"\nвремя: {report['seconds']} c | json: {a.json} | csv: {a.csv}")


if __name__ == "__main__":
    main()
