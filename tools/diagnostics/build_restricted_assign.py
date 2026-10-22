"""Assign формул с ограничениями NOM (F16) и кеширование результата.

Ограничения:
  C 5-60, H 4-120, O 1-30 (NOM-like);
  N <= 5, S <= 2, P <= 1, Cl <= 2; F/Br/I = 0;
  NOM-ratio: H/C 0.3-2.5, O/C <= 1.2, N/C <= 0.5, S/C <= 0.1, P/C <= 0.05;
  DBE/валентность через counts_valid.

После assign кандидаты фильтруются: остаются только прошедшие проверку;
первый прошедший становится brutto, иначе assign=False.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ablation_f16 import REAL, resolve

from src.configs import PIPELINE
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.spectrum import assign_formulas, denoise
from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._formula_check import counts_valid
from src.core.spectrum._formula_source import open_formula_db
from src.core.spectrum._load import load_spectrum
from src.core.domain.molecule import parse_formula

CFG = FormulaSearchConfig(
    elements=("C", "H", "O", "N", "S", "P", "Cl"),
    ranges={
        "C": (5, 60),
        "H": (4, 120),
        "O": (1, 30),
        "N": (0, 5),
        "S": (0, 2),
        "P": (0, 1),
        "Cl": (0, 2),
    },
    max_hc=2.5,
    max_oc=1.2,
    max_nc=0.5,
    max_sc=0.1,
    max_pc=0.05,
    max_dbe=30.0,
    min_c=5,
)


def nom_cl_ok(brutto: str) -> bool:
    try:
        c = parse_formula(str(brutto))
    except Exception:
        return False
    if any(int(c.get(el, 0)) > 0 for el in ("F", "Br", "I")):
        return False
    if int(c.get("Cl", 0)) > 2:
        return False
    if int(c.get("S", 0)) > 2 or int(c.get("P", 0)) > 1 or int(c.get("N", 0)) > 5:
        return False
    ok, _ = counts_valid(c)
    if not ok:
        return False
    nC, nH, nO = int(c.get("C", 0)), int(c.get("H", 0)), int(c.get("O", 0))
    nN, nS, nP = int(c.get("N", 0)), int(c.get("S", 0)), int(c.get("P", 0))
    if nC < 1 or nH < 1:
        return False
    if not (0.3 <= nH / nC <= 2.5):
        return False
    if nO / nC > 1.2 or nN / nC > 0.5 or nS / nC > 0.1 or nP / nC > 0.05:
        return False
    return True


def main() -> None:
    t0 = time.perf_counter()
    base = Path("data/real_sets") / "Fulvagra F16"
    s, m, d = REAL["Fulvagra F16"]
    defaults = PIPELINE.run_pipeline_defaults

    src_raw = load_spectrum(resolve(str(base / s)), sep=",")
    dmet_raw = load_spectrum(resolve(str(base / m)), sep=",")
    dacet_raw = load_spectrum(resolve(str(base / d)), sep=",")
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
            search_config=CFG,
            brutto_generation_mode="nom_like",
            ion_mode=ion_mode,
            isotope_filter=True,
            isotope_variants=False,
            isotope_satellites=False,
            original=src_raw.copy(),
            formula_db=formula_db,
        )
    finally:
        if formula_db is not None:
            formula_db.close()
    print(
        f"[{time.strftime('%H:%M:%S')}] assign до фильтра: "
        f"{int(src.table['assign'].sum())}",
        flush=True,
    )

    table = src.table
    n_before = int(table["assign"].sum())
    kept = 0
    cand_counts = []
    for i in range(len(table)):
        cands = table.at[i, "all_candidates"]
        cands = list(cands) if isinstance(cands, (list, tuple)) else []
        plausible = [str(c) for c in cands if nom_cl_ok(str(c))]
        cand_counts.append(len(plausible))
        if plausible:
            table.at[i, "brutto"] = plausible[0]
            table.at[i, "assign"] = True
            table.at[i, "all_candidates"] = plausible
            kept += 1
        else:
            table.at[i, "brutto"] = None
            table.at[i, "assign"] = False
            table.at[i, "all_candidates"] = []
    # Изотопные поля относятся к старой формуле — обнуляем.
    if "iso_status" in table.columns:
        table["iso_status"] = "uninformative"
    if "iso_satellite_of" in table.columns:
        table["iso_satellite_of"] = np.nan
    if "iso_variants" in table.columns:
        table["iso_variants"] = None
    print(
        f"[{time.strftime('%H:%M:%S')}] после фильтра: {kept} "
        f"(было {n_before}); пиков с кандидатами: "
        f"{int((np.asarray(cand_counts) > 0).sum())}",
        flush=True,
    )

    out = Path("D:/Temp/User/nom_restrict_cache")
    out.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(
        {"src": src, "dmet": dmet, "dacet": dacet, "config": CFG},
        out / "restricted.pkl",
    )
    stats = {
        "assign_before_filter": n_before,
        "assign_after_filter": kept,
        "peaks_with_candidates": int((np.asarray(cand_counts) > 0).sum()),
        "total_peaks": int(len(table)),
        "seconds": round(time.perf_counter() - t0, 1),
        "config": {
            "elements": list(CFG.elements),
            "ranges": CFG.ranges,
            "max_hc": CFG.max_hc,
            "max_oc": CFG.max_oc,
            "max_nc": CFG.max_nc,
            "max_sc": CFG.max_sc,
            "max_pc": CFG.max_pc,
            "max_dbe": CFG.max_dbe,
        },
    }
    (out / "stats.json").write_text(
        json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"время: {stats['seconds']} c | {out/'restricted.pkl'}")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    main()
