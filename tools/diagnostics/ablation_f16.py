"""Ablation: вклад каждой новой проверки на F16 при минимальных пересчётах.

Один раз: загрузка, шумоподавление исходника, assign, денойз дериватизатов 2.0.
Затем один раз считаются серии (base) и ансамбль decoy-сдвигов; все проверки
применяются как пост-обработка к тем же сериям — без повторного поиска.

Запуск:
  python tools/diagnostics/ablation_f16.py --json D:/Temp/User/ablation_f16.json
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import pandas as pd

from src.configs import CHEM, PIPELINE
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.pipeline._run import _search_config_from_brutto
from src.core.spectrum import assign_formulas, denoise, find_series
from src.core.spectrum._decoy import DECOY_SEED, decoy_shifts
from src.core.spectrum._formula_source import open_formula_db
from src.core.spectrum._load import load_spectrum
from src.core.spectrum._validate import (
    add_status,
    attach_conflicts,
    attach_fdr,
    attach_formula_check,
    attach_last_steps,
    trim_to_confirmed_last,
)

REAL = {
    "Fulvagra F16": (
        "Fulvagra_prep HPLC_FR16_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s_.raw",
        "Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s.raw",
    )
}
DECOYS = 20


def resolve(path: str) -> str:
    if path.lower().endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    return path


def metrics(df: pd.DataFrame, label: str) -> dict:
    return {
        "label": label,
        "n": int(len(df)),
        "mean": round(float(df["n_groups"].mean()), 3) if len(df) else 0.0,
        "median": float(df["n_groups"].median()) if len(df) else 0.0,
        "sig_n": int(df["significant"].sum()) if "significant" in df else 0,
        "sig_mean": (
            round(float(df.loc[df["significant"], "n_groups"].mean()), 3)
            if "significant" in df and df["significant"].any()
            else 0.0
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--json", default="D:/Temp/User/ablation_f16.json")
    a = ap.parse_args()

    s, m, d = REAL[a.dataset]
    base = Path("data/real_sets") / a.dataset
    defaults = PIPELINE.run_pipeline_defaults
    old_env = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = a.variant
    t0 = time.perf_counter()
    report: dict = {}
    try:
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

        # ── decoy-ансамбль (фон) ─────────────────────────────────────────
        shifts = decoy_shifts(d_cd3, k=DECOYS, seed=DECOY_SEED)
        dec3 = [find_series(src, dmet, d_cd3 + sh, **kw) for sh in shifts]
        dec3co = [find_series(src, dacet, d_cd3co + sh, **kw) for sh in shifts]
        floor3 = sum(len(f) for f in dec3) / len(dec3)
        floor3co = sum(len(f) for f in dec3co) / len(dec3co)
        mean_floor3 = sum(float(f["n_groups"].mean()) for f in dec3 if len(f)) / max(
            1, sum(1 for f in dec3 if len(f))
        )
        mean_floor3co = sum(
            float(f["n_groups"].mean()) for f in dec3co if len(f)
        ) / max(1, sum(1 for f in dec3co if len(f)))
        print(
            f"[{time.strftime('%H:%M:%S')}] decoy ({len(shifts)}): CD3 {floor3:.0f} серий "
            f"(ср. {mean_floor3:.2f}), CD3CO {floor3co:.0f} (ср. {mean_floor3co:.2f})",
            flush=True,
        )

        # ── проверки как пост-обработка ─────────────────────────────────
        from src.core.domain.molecule import parse_formula

        counts_by_brutto = {}
        for brutto in pd.concat([c3["brutto"], c3co["brutto"]]).unique():
            try:
                counts_by_brutto[str(brutto)] = parse_formula(str(brutto))
            except Exception:
                continue

        variants: dict[str, dict] = {}
        for label, frame, group, decoys, raw in (
            ("N_COOH", c3, "cd3", dec3, str(base / m)),
            ("N_OH", c3co, "cd3co", dec3co, str(base / d)),
        ):
            f = frame.copy()
            rows = {}
            rows["base"] = metrics(f, "base")
            f_form = attach_formula_check(f, group, counts_by_brutto)
            rows["formula"] = metrics(f_form[f_form["formula_ok"]], "formula")
            f_conf = attach_conflicts(f)
            rows["conflicts"] = metrics(f_conf[~f_conf["ambiguous"]], "conflicts")
            f_fdr = attach_fdr(f, decoys)
            rows["fdr"] = metrics(f_fdr[f_fdr["fdr_significant"]], "fdr")
            # profile/персистентность — только последний пик, с откатом на предпоследний
            f_last = attach_last_steps(f, raw, ppm=defaults["ppm_tol"], max_scans=16)
            rows["profile_last"] = metrics(f_last, "profile(last)")
            f_trim = trim_to_confirmed_last(f_last, persistence_min=0.5)
            rows["trimmed"] = metrics(f_trim, "trim to confirmed")
            rows["no_overlap"] = metrics(
                f_last[~f_last["last_multi"]], "last without overlap"
            )
            allf = add_status(
                attach_last_steps(
                    attach_fdr(
                        attach_conflicts(
                            attach_formula_check(f, group, counts_by_brutto)
                        ),
                        decoys,
                    ),
                    raw,
                    ppm=defaults["ppm_tol"],
                    max_scans=16,
                )
            )
            allf = trim_to_confirmed_last(allf, persistence_min=0.5)
            rows["all"] = metrics(allf[allf["status"] == "supported"], "all")
            rows["all"]["statuses"] = allf["status"].value_counts().to_dict()
            variants[label] = rows

        report = {
            "dataset": a.dataset,
            "variant": a.variant,
            "decoy_shifts": len(shifts),
            "decoy_seed": DECOY_SEED,
            "decoy_floor_series": {
                "N_COOH": round(floor3, 1),
                "N_OH": round(floor3co, 1),
            },
            "decoy_floor_mean": {
                "N_COOH": round(mean_floor3, 3),
                "N_OH": round(mean_floor3co, 3),
            },
            "variants": variants,
            "seconds": round(time.perf_counter() - t0, 1),
        }
        Path(a.json).parent.mkdir(parents=True, exist_ok=True)
        Path(a.json).write_text(
            json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    finally:
        if old_env is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old_env

    print("\n=== ABLATION (F16) ===")
    for col, rows in report["variants"].items():
        print(f"\n{col}:")
        print(
            f"  {'вариант':16s} {'серий':>6s} {'ср.':>6s} {'значимых':>9s} {'ср.знач':>8s}"
        )
        for label, r in rows.items():
            print(
                f"  {label:16s} {r['n']:6d} {r['mean']:6.2f} {r['sig_n']:9d} {r['sig_mean']:8.2f}"
            )
        if "statuses" in rows.get("all", {}):
            print(f"  статусы: {rows['all']['statuses']}")
    print(f"\nвремя: {report['seconds']} c | записано: {a.json}")


if __name__ == "__main__":
    main()
