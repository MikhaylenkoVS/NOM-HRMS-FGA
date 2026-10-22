"""Сетка шумоподавления дериватизатов с оценкой FDR (F16).

Сравниваются встроенные режимы ``noise_filter``:
  * ``gmm``      — авто-порог GMM+BIC с множителем ``force``;
  * ``quantile`` — нижний квантиль интенсивностей;
  * ``intensity``— фиксированный порог по интенсивности (доля базового пика);
  * ``none``     — без шумоподавления (референс).

Исходный спектр денойзится один раз (GMM force=2.0) и назначается один раз;
меняются только производные (dmet/dacet). Для каждого варианта считаются
target-серии, 20 decoy-прогонов, FDR/q-value и метрики качества.

Запуск:
  python tools/diagnostics/grid_denoise_fdr.py \
      --json D:/Temp/User/grid_denoise_fdr.json
"""

from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

from ablation_f16 import DECOYS, REAL, resolve

from src.configs import CHEM, PIPELINE
from src.core.domain.molecule import parse_formula
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.pipeline._run import _search_config_from_brutto
from src.core.spectrum import assign_formulas, denoise, find_series
from src.core.spectrum._decoy import DECOY_SEED, decoy_shifts
from src.core.spectrum._formula_source import open_formula_db
from src.core.spectrum._load import load_spectrum
from src.core.spectrum._validate import attach_formula_check

ALPHA = 0.05
BATCH = 200

VARIANTS: list[tuple[str, str, float | None]] = [
    ("none", "none", None),
    ("gmm_1.0", "gmm", 1.0),
    ("gmm_2.0", "gmm", 2.0),
    ("gmm_3.0", "gmm", 3.0),
    ("gmm_5.0", "gmm", 5.0),
    ("quantile_0.5", "quantile", 0.5),
    ("quantile_0.7", "quantile", 0.7),
    ("quantile_0.8", "quantile", 0.8),
    ("quantile_0.9", "quantile", 0.9),
    ("intensity_1e-4", "intensity", 1e-4),
    ("intensity_3e-4", "intensity", 3e-4),
    ("intensity_1e-3", "intensity", 1e-3),
    ("intensity_3e-3", "intensity", 3e-3),
    ("intensity_1e-2", "intensity", 1e-2),
]


def make_variant(spec, mode: str, value, no_guard: bool = False):
    """Вернуть (спектр, метаданные фильтра)."""
    n_before = spec.n_peaks
    intens = spec.intensity
    base = float(np.max(intens)) if intens.size else 0.0
    guard = 1.0 if no_guard else None
    meta = {
        "mode": mode,
        "value": value,
        "peaks_before": n_before,
        "guard_disabled": no_guard,
    }
    if mode == "none":
        out = spec.copy()
        meta.update(threshold=None, expected_kept=n_before)
    elif mode == "gmm":
        out = denoise(spec, force=value, max_removed_ratio=guard)
        meta.update(threshold=None, expected_kept=None)
    elif mode == "quantile":
        threshold = float(spec.table["intensity"].quantile(value))
        out = denoise(spec, quantile=value, max_removed_ratio=guard)
        meta.update(
            threshold=threshold,
            expected_kept=int((np.asarray(intens) > threshold).sum()),
        )
    elif mode == "intensity":
        threshold = float(value) * base
        out = denoise(
            spec,
            intensity=float(value),
            intensity_relative=True,
            max_removed_ratio=guard,
        )
        meta.update(
            threshold=threshold,
            expected_kept=int((np.asarray(intens) > threshold).sum()),
        )
    else:
        raise ValueError(mode)
    meta.update(
        base_intensity=base,
        peaks_after=int(out.n_peaks),
        removed_ratio=round(1.0 - out.n_peaks / max(1, n_before), 4),
    )
    # Предохранитель noise_filter может молча не применить фильтр.
    meta["guard_noop"] = bool(
        meta["expected_kept"] is not None
        and out.n_peaks == n_before
        and meta["expected_kept"] != n_before
    )
    return out, meta


def cum_counts(lengths, maxlen: int) -> np.ndarray:
    """Число серий с длиной >= L для L=1..maxlen."""
    arr = np.asarray(lengths, dtype=int)
    return np.array([int((arr >= L).sum()) for L in range(1, maxlen + 1)])


def fdr_metrics(target: pd.DataFrame, decoys: list[pd.DataFrame], group: str, counts):
    """FDR/q-value, порог, LOO-калибровка и бутстрэп по decoy-ансамблю."""
    t = target["n_groups"].astype(int).to_numpy()
    d_lists = [f["n_groups"].astype(int).to_numpy() for f in decoys]
    maxlen = int(t.max())
    target_cum = cum_counts(t, maxlen)
    decoy_cum = np.vstack([cum_counts(d, maxlen) for d in d_lists])  # K × maxlen
    mean_decoy = decoy_cum.mean(axis=0)
    with np.errstate(divide="ignore", invalid="ignore"):
        fdr = np.where(target_cum > 0, mean_decoy / target_cum, 1.0)
    fdr = np.clip(fdr, 0.0, 1.0)
    q = np.minimum.accumulate(fdr)  # не возрастает с длиной
    ok = np.where(q <= ALPHA)[0]
    lstar = int(ok[0] + 1) if ok.size else None
    retained = int(target_cum[lstar - 1]) if lstar else 0
    fdr_at = float(fdr[lstar - 1]) if lstar else None

    def _threshold(q_arr):
        idx = np.where(q_arr <= ALPHA)[0]
        return int(idx[0] + 1) if idx.size else None

    # LOO: каждый decoy-прогон как цель против остальных
    loo_sig = []
    for i, d in enumerate(d_lists):
        others = np.vstack([decoy_cum[j] for j in range(len(d_lists)) if j != i])
        d_cum = cum_counts(d, maxlen)
        with np.errstate(divide="ignore", invalid="ignore"):
            f = np.where(d_cum > 0, others.mean(axis=0) / d_cum, 1.0)
        f = np.clip(f, 0.0, 1.0)
        qq = np.minimum.accumulate(f)
        idx = _threshold(qq)
        loo_sig.append(float(d_cum[idx - 1] / max(1, len(d))) if idx else 0.0)

    # Бутстрэп по decoy-ансамблю
    rng = np.random.default_rng(0)
    boot_ret, boot_lstar = [], []
    for _ in range(BATCH):
        idx = rng.integers(0, len(d_lists), len(d_lists))
        md = decoy_cum[idx].mean(axis=0)
        with np.errstate(divide="ignore", invalid="ignore"):
            f = np.where(target_cum > 0, md / target_cum, 1.0)
        f = np.clip(f, 0.0, 1.0)
        qq = np.minimum.accumulate(f)
        ls = _threshold(qq)
        boot_lstar.append(ls)
        boot_ret.append(int(target_cum[ls - 1]) if ls else 0)

    # Качество оставшихся
    scored = attach_formula_check(target, group, counts)
    if lstar:
        keep = (target["n_groups"].astype(int) >= lstar).to_numpy()
        formula_ok = float(scored.loc[keep, "formula_ok"].mean())
    else:
        keep = np.zeros(len(target), dtype=bool)
        formula_ok = 0.0
    decoy_mean_at = float(mean_decoy[lstar - 1]) if lstar else 0.0

    def _fixed(length: int) -> dict:
        if length > maxlen:
            return {"retained": 0, "fdr": None}
        return {
            "retained": int(target_cum[length - 1]),
            "fdr": round(float(fdr[length - 1]), 4),
        }

    l5, l6 = _fixed(5), _fixed(6)
    return {
        "n_target": int(len(t)),
        "decoy_mean_total": round(float(mean_decoy[0]), 1),
        "lstar": lstar,
        "retained": retained,
        "share_retained": round(retained / max(1, len(t)), 4),
        "mean_len_retained": (
            round(float(t[t >= (lstar or 10**9)].mean()), 3) if lstar else 0.0
        ),
        "fdr_at_lstar": round(fdr_at, 4) if fdr_at is not None else None,
        "decoy_mean_at_lstar": round(decoy_mean_at, 2),
        "retained_at_L5": l5["retained"],
        "fdr_at_L5": l5["fdr"],
        "retained_at_L6": l6["retained"],
        "fdr_at_L6": l6["fdr"],
        "formula_ok_retained": round(formula_ok, 4),
        "loo_fpr": round(float(np.mean(loo_sig)), 4),
        "loo_max": round(float(np.max(loo_sig)), 4),
        "boot_retained_p05": int(np.percentile(boot_ret, 5)),
        "boot_retained_p50": int(np.percentile(boot_ret, 50)),
        "boot_retained_p95": int(np.percentile(boot_ret, 95)),
        "boot_lstar_mode": (
            int(pd.Series([v for v in boot_lstar if v is not None]).mode().iloc[0])
            if any(v is not None for v in boot_lstar)
            else None
        ),
    }


def prepare(cache_dir: Path):
    """Загрузка, денойз исходника и однократный assign."""
    s, m, d = REAL["Fulvagra F16"]
    base = Path("data/real_sets") / "Fulvagra F16"
    defaults = PIPELINE.run_pipeline_defaults

    src_raw = load_spectrum(resolve(str(base / s)), sep=",")
    dmet_raw = load_spectrum(resolve(str(base / m)), sep=",")
    dacet_raw = load_spectrum(resolve(str(base / d)), sep=",")
    src_original = src_raw.copy()
    src = denoise(src_raw, force=defaults["noise_force"])
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

    cache_dir.mkdir(parents=True, exist_ok=True)
    pd.to_pickle(
        {"src": src, "dmet": dmet_raw, "dacet": dacet_raw},
        cache_dir / "denoise_grid_src.pkl",
    )
    return src, dmet_raw, dacet_raw


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default="D:/Temp/User/grid_denoise_fdr.json")
    ap.add_argument("--cache-dir", default="D:/Temp/User/denoise_grid_cache")
    ap.add_argument("--reuse", action="store_true")
    ap.add_argument(
        "--no-guard",
        action="store_true",
        help="отключить предохранитель max_removed_ratio (для сравнения режимов)",
    )
    a = ap.parse_args()

    cache_dir = Path(a.cache_dir)
    payload = cache_dir / "denoise_grid_src.pkl"
    t0 = time.perf_counter()
    if a.reuse and payload.exists():
        cached = pd.read_pickle(payload)
        src, dmet_raw, dacet_raw = cached["src"], cached["dmet"], cached["dacet"]
        print(f"[{time.strftime('%H:%M:%S')}] исходник из кеша", flush=True)
    else:
        src, dmet_raw, dacet_raw = prepare(cache_dir)

    defaults = PIPELINE.run_pipeline_defaults
    kw = dict(
        ppm_tol=defaults["ppm_tol"],
        max_groups=defaults["max_groups"],
        max_gaps=defaults["max_gaps"],
        require_first_step=True,
        significance_level=defaults["significance_level"],
    )
    d_delta = {
        "N_COOH": CHEM.derivatization_shifts["delta_cd3"],
        "N_OH": CHEM.derivatization_shifts["delta_cd3co"],
    }
    shifts = {
        key: decoy_shifts(delta, k=DECOYS, seed=DECOY_SEED)
        for key, delta in d_delta.items()
    }

    counts_by_brutto = {}
    for brutto in src.table["brutto"].dropna().unique():
        try:
            counts_by_brutto[str(brutto)] = parse_formula(str(brutto))
        except Exception:
            continue

    report: dict = {
        "dataset": "Fulvagra F16",
        "decoy_shifts": DECOYS,
        "decoy_seed": DECOY_SEED,
        "alpha": ALPHA,
        "src_assign": int(src.table["assign"].sum()),
        "guard_disabled": bool(a.no_guard),
        "variants": [],
        "seconds": None,
    }
    retained_keys: dict[tuple[str, str], set] = {}
    for name, mode, value in VARIANTS:
        row: dict = {"variant": name, "mode": mode, "value": value, "groups": {}}
        for group_label, group_id, deriv_raw, key in (
            ("N_COOH", "cd3", dmet_raw, "N_COOH"),
            ("N_OH", "cd3co", dacet_raw, "N_OH"),
        ):
            deriv, meta = make_variant(deriv_raw, mode, value, no_guard=a.no_guard)
            delta = d_delta[key]
            target = find_series(src, deriv, delta, **kw)
            decoys = [find_series(src, deriv, delta + sh, **kw) for sh in shifts[key]]
            metrics = fdr_metrics(target, decoys, group_id, counts_by_brutto)
            peaks = max(1, meta["peaks_after"])
            lstar = metrics["lstar"]
            if lstar:
                mask = (target["n_groups"].astype(int) >= lstar).to_numpy()
                keys = set(
                    zip(
                        target.loc[mask, "mass_src"].round(4).tolist(),
                        target.loc[mask, "brutto"].astype(str).tolist(),
                        target.loc[mask, "n_groups"].astype(int).tolist(),
                    )
                )
            else:
                keys = set()
            retained_keys[(name, group_label)] = keys
            metrics.update(
                {
                    "peaks": meta["peaks_after"],
                    "peaks_before": meta["peaks_before"],
                    "removed_ratio": meta["removed_ratio"],
                    "threshold": meta["threshold"],
                    "base_intensity": round(meta["base_intensity"], 3),
                    "expected_kept": meta["expected_kept"],
                    "guard_noop": meta["guard_noop"],
                    "retained_per_1000": round(metrics["retained"] / peaks * 1000, 2),
                }
            )
            row["groups"][group_label] = metrics
        report["variants"].append(row)
        g1, g2 = row["groups"]["N_COOH"], row["groups"]["N_OH"]
        print(
            f"[{time.strftime('%H:%M:%S')}] {name:<16} "
            f"CD3 peaks={g1['peaks']:<7} ret={g1['retained']:<6} "
            f"L*={g1['lstar']} fdr={g1['fdr_at_lstar']} | "
            f"CD3CO peaks={g2['peaks']:<7} ret={g2['retained']:<6} "
            f"L*={g2['lstar']} fdr={g2['fdr_at_lstar']}",
            flush=True,
        )

    # Пересечение с базой gmm_2.0 и согласие между «разумными» вариантами
    report["consensus"] = {}
    for group_label in ("N_COOH", "N_OH"):
        base_keys = retained_keys[("gmm_2.0", group_label)]
        sane = []
        for row in report["variants"]:
            name = row["variant"]
            m = row["groups"][group_label]
            keys = retained_keys[(name, group_label)]
            inter = len(keys & base_keys)
            m.update(
                {
                    "overlap_gmm2": inter,
                    "baseline_recovered": round(inter / max(1, len(base_keys)), 4),
                    "new_vs_gmm2": len(keys - base_keys),
                    "jaccard_gmm2": round(inter / max(1, len(keys | base_keys)), 4),
                }
            )
            if m["lstar"] is not None and m["lstar"] >= 4:
                sane.append(name)

        counts: Counter = Counter()
        for name in sane:
            counts.update(retained_keys[(name, group_label)])
        report["consensus"][group_label] = {
            "sane_variants": sane,
            "n_keys": len(counts),
            "ge2": sum(1 for v in counts.values() if v >= 2),
            "ge3": sum(1 for v in counts.values() if v >= 3),
            "all": sum(1 for v in counts.values() if v == len(sane)),
        }

    report["seconds"] = round(time.perf_counter() - t0, 1)
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nвремя: {report['seconds']} c | записано: {a.json}")


if __name__ == "__main__":
    main()
