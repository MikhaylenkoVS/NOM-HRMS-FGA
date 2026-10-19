"""Сетка экспериментов: режим шумоподавления дериватизатов × окно допуска.

Экономия вычислений (по требованию задачи):
  * RAW → таблица, шумоподавление ИСХОДНИКА и назначение формул делаются ОДИН раз;
  * для каждого варианта дериватизата (уровень шумоподавления) спектр готовится один раз;
  * вычитание исходника считается один раз на (вариант, окно вычитания);
  * дальше для каждой комбинации выполняется только `find_series` — и для
    настоящей Δ, и для контрольной (Δ+0.5), чтобы получить ложный фон.

Запускает один процесс; результат пишется инкрементально.
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
from src.core.spectrum._formula_source import open_formula_db
from src.core.spectrum._load import load_spectrum
from src.core.spectrum._overlap import subtract_matching_peaks

REAL = {
    "Fulvagra F16": (
        "Fulvagra_prep HPLC_FR16_ESI_1e6_480k_128_m-s.raw",
        "Fulvagra_prep HPLC_FR16_CD3OD_ESI_1e6_480k_128_m-s_.raw",
        "Fulvagra_prep HPLC_FR16_AC-D4_ESI_1e6_480k_128_m-s.raw",
    )
}
DENOISE_LEVELS = (None, 1.0, 2.0)  # None = без шумоподавления дериватизатов
SUBTRACT_WINDOWS = (None, 1.0, 2.0)  # None = без вычитания
SERIES_WINDOWS = (1.0, 2.0, 5.0)  # ppm для поиска серий
CONTROL_SHIFT = 0.5  # ложная Δ для негативного контроля


def resolve(path: str) -> str:
    if path.lower().endswith(".raw"):
        from src.core.io.raw_bridge import average_raw_to_json

        return average_raw_to_json(path, 0.0, 999.0)
    return path


def hist(values) -> dict[str, int]:
    out: dict[str, int] = {}
    for v in values:
        out[str(int(v))] = out.get(str(int(v)), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def series_metrics(df: pd.DataFrame, total: int) -> dict:
    if df is None or df.empty:
        return {"n": 0, "mean": 0.0, "median": 0.0, "sig_n": 0, "sig_mean": 0.0}
    n_groups = df["n_groups"].astype(int)
    sig = df["significant"].astype(bool) if "significant" in df.columns else None
    return {
        "n": int(len(df)),
        "mean": round(float(n_groups.mean()), 3),
        "median": float(n_groups.median()),
        "sig_n": int(sig.sum()) if sig is not None else 0,
        "sig_mean": (
            round(float(n_groups[sig].mean()), 3)
            if sig is not None and sig.any()
            else 0.0
        ),
        "hist": hist(n_groups),
        "total_compounds": int(total),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="Fulvagra F16")
    ap.add_argument("--variant", default="chorsphal")
    ap.add_argument("--json", default="D:/Temp/User/grid_f16.json")
    a = ap.parse_args()

    s, m, d = REAL[a.dataset]
    base = Path("data/real_sets") / a.dataset
    defaults = PIPELINE.run_pipeline_defaults
    old_env = os.environ.get("NOM_FORMULA_DB")
    os.environ["NOM_FORMULA_DB"] = a.variant

    t_start = time.perf_counter()
    try:
        # ── один раз: загрузка, денойз исходника, назначение ─────────────
        src_raw = load_spectrum(
            resolve(str(base / s)),
            sep=",",
            mass_min=defaults["load_mass_min"],
            mass_max=defaults["load_mass_max"],
        )
        dmet_raw = load_spectrum(
            resolve(str(base / m)),
            sep=",",
            mass_min=defaults["load_mass_min"],
            mass_max=defaults["load_mass_max"],
        )
        dacet_raw = load_spectrum(
            resolve(str(base / d)),
            sep=",",
            mass_min=defaults["load_mass_min"],
            mass_max=defaults["load_mass_max"],
        )
        src_original = src_raw.copy()
        src = denoise(
            src_raw,
            force=defaults["noise_force"],
            intensity=defaults["noise_intensity"],
            quantile=None,
        )
        print(
            f"[{time.strftime('%H:%M:%S')}] src денойз: {len(src.table)} пиков",
            flush=True,
        )

        ion_mode = _ion_mode_from_sign(defaults["sign"])
        search_config = _search_config_from_brutto(None)
        formula_db = open_formula_db()
        try:
            src = assign_formulas(
                src,
                rel_error_ppm=defaults["rel_error"],
                mass_min=defaults["assign_mass_min"],
                mass_max=defaults["assign_mass_max"],
                search_config=search_config,
                ion_mode=ion_mode,
                isotope_filter=True,
                isotope_variants=True,
                original=src_original,
                formula_db=formula_db,
            )
        finally:
            if formula_db is not None:
                formula_db.close()
        n_assigned = int(src.table["assign"].sum())
        print(
            f"[{time.strftime('%H:%M:%S')}] назначено {n_assigned} из {len(src.table)}",
            flush=True,
        )

        # ── варианты производных спектров ───────────────────────────────
        deriv_variants: dict[str, dict] = {}
        for level in DENOISE_LEVELS:
            name = f"den{level}"
            dmet_v = (
                denoise(dmet_raw, force=level, intensity=None, quantile=None)
                if level is not None
                else dmet_raw
            )
            dacet_v = (
                denoise(dacet_raw, force=level, intensity=None, quantile=None)
                if level is not None
                else dacet_raw
            )
            for ppm in SUBTRACT_WINDOWS:
                key = f"{name}_sub{ppm}"
                if ppm is None:
                    dm, da = dmet_v, dacet_v
                else:
                    dm, _ = subtract_matching_peaks(dmet_v, src, ppm_tol=ppm)
                    da, _ = subtract_matching_peaks(dacet_v, src, ppm_tol=ppm)
                deriv_variants[key] = {
                    "dmet": dm,
                    "dacet": da,
                    "peaks": {"dmet": len(dm.table), "dacet": len(da.table)},
                }
            print(
                f"[{time.strftime('%H:%M:%S')}] вариант {name}: "
                f"{len(dmet_v.table)} / {len(dacet_v.table)} пиков",
                flush=True,
            )

        results: list[dict] = []
        for key, var in deriv_variants.items():
            for ppm_tol in SERIES_WINDOWS:
                row = {
                    "variant": key,
                    "peaks": var["peaks"],
                    "ppm_tol": ppm_tol,
                    "elapsed": round(time.perf_counter() - t_start, 1),
                }
                for deriv_name, col, delta in (
                    ("dmet", "N_COOH", CHEM.derivatization_shifts["delta_cd3"]),
                    ("dacet", "N_OH", CHEM.derivatization_shifts["delta_cd3co"]),
                ):
                    deriv_obj = var[deriv_name]
                    for label, shift in (("real", 0.0), ("control", CONTROL_SHIFT)):
                        df = find_series(
                            src,
                            deriv_obj,
                            delta + shift,
                            ppm_tol=ppm_tol,
                            max_groups=defaults["max_groups"],
                            max_gaps=defaults["max_gaps"],
                            require_first_step=True,
                            significance_level=defaults["significance_level"],
                        )
                        row[f"{col}_{label}"] = series_metrics(df, len(src.table))
                    real = row[f"{col}_real"]["mean"]
                    ctrl = row[f"{col}_control"]["mean"]
                    row[f"{col}_signal"] = round(real - ctrl, 3)
                results.append(row)
                print(
                    f"  {key:16s} ppm={ppm_tol:>4} | "
                    f"N_COOH ср {row['N_COOH_real']['mean']:.2f} "
                    f"(значимых {row['N_COOH_real']['sig_n']}, фон {row['N_COOH_control']['mean']:.2f}, "
                    f"сигнал {row['N_COOH_signal']:+.2f}) | "
                    f"N_OH ср {row['N_OH_real']['mean']:.2f} "
                    f"(фон {row['N_OH_control']['mean']:.2f}, сигнал {row['N_OH_signal']:+.2f})",
                    flush=True,
                )
                Path(a.json).parent.mkdir(parents=True, exist_ok=True)
                Path(a.json).write_text(
                    json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
                )
    finally:
        if old_env is None:
            os.environ.pop("NOM_FORMULA_DB", None)
        else:
            os.environ["NOM_FORMULA_DB"] = old_env

    print(
        f"\nвсего {len(results)} конфигураций за {time.perf_counter() - t_start:.0f} c"
    )


if __name__ == "__main__":
    main()
