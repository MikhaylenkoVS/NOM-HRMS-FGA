"""Занятость ppm-окон ожидаемых продуктов дериватизации (F16, GMM 2.0).

Для каждого назначенного исходного пика (assign=True, не изотопный сателлит)
и каждой химически допустимой степени n <= O считаются ожидаемые позиции
mu = m0 + n*delta. Для окон 0.5/1/2/3/5/10 ppm считается, сколько пиков
дериватизата попадает в окно.

Факторы: производная, степень, m/z, локальная плотность, интенсивность
исходника, неоднозначность assign (len(all_candidates)), iso_status,
размеры формулы. Выход: JSON + CSV агрегатов, pickle позиций, markdown.

Запуск (кеш уже содержит src + dmet/dacet RAW):
  python tools/diagnostics/ppm_window_occupancy_f16.py \
      --cache D:/Temp/User/denoise_grid_cache/denoise_grid_src.pkl \
      --out-dir D:/Temp/User
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

from src.configs import CHEM, PIPELINE
from src.core.domain.molecule import parse_formula
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.spectrum import denoise
from src.core.spectrum._series import _theor_ion_mass_cached

WINDOWS = (0.5, 1.0, 2.0, 3.0, 5.0, 10.0)
MAX_DEG = 10
LOCAL_DA = 5.0  # полуширина окна локальной плотности, Да


def build_anchors(src) -> pd.DataFrame:
    """Назначенные исходные пики с теоретической m0 и признаками формулы."""
    t = src.table
    mask = t["assign"].astype(bool) & t["iso_satellite_of"].isna()
    a = t.loc[
        mask, ["mass", "intensity", "brutto", "iso_status", "all_candidates"]
    ].copy()
    ion_mode = _ion_mode_from_sign(PIPELINE.run_pipeline_defaults["sign"])

    m0 = []
    for mass, brutto in zip(a["mass"].to_numpy(float), a["brutto"].astype(str)):
        try:
            m = _theor_ion_mass_cached(brutto, ion_mode)
            if abs(m - mass) / mass > 0.001:
                m = mass
        except Exception:
            m = mass
        m0.append(float(m))
    a["m0"] = m0
    a["n_candidates"] = a["all_candidates"].map(len)

    feats = []
    for brutto in a["brutto"].astype(str):
        try:
            c = parse_formula(brutto)
        except Exception:
            c = {}
        feats.append(
            {
                "C": c.get("C", 0),
                "H": c.get("H", 0),
                "O": c.get("O", 0),
                "N": c.get("N", 0),
                "S": c.get("S", 0),
                "P": c.get("P", 0),
                "X": sum(c.get(x, 0) for x in ("F", "Cl", "Br", "I")),
            }
        )
    f = pd.DataFrame(feats, index=a.index)
    a = pd.concat([a, f], axis=1)
    a["DBE"] = (2 * a["C"] + 2 + a["N"] - a["H"] - a["X"]) / 2.0
    a["log_intensity"] = np.log10(a["intensity"].clip(lower=1.0))
    a["log_candidates"] = np.log10(a["n_candidates"].clip(lower=1))
    a = a.reset_index(drop=True)
    a["anchor_idx"] = np.arange(len(a))
    return a


def count_windows(mz: np.ndarray, mu: float) -> tuple[list[int], float]:
    halves = [w * 1e-6 * mu for w in WINDOWS]
    lo = int(np.searchsorted(mz, mu - halves[-1], side="left"))
    hi = int(np.searchsorted(mz, mu + halves[-1], side="right"))
    seg = mz[lo:hi]
    counts = [int(np.count_nonzero(np.abs(seg - mu) <= h)) for h in halves]
    dlo = int(np.searchsorted(mz, mu - LOCAL_DA, side="left"))
    dhi = int(np.searchsorted(mz, mu + LOCAL_DA, side="right"))
    n_local = dhi - dlo
    spacing = (2 * LOCAL_DA) / max(1, n_local - 1)
    return counts, spacing


def build_positions(anchors: pd.DataFrame, spec, deriv: str, delta: float):
    mz = np.sort(spec.table["mass"].to_numpy(float))
    mz_min, mz_max = float(mz[0]), float(mz[-1])
    rows = []
    dropped_out = 0
    for a in anchors.itertuples(index=False):
        max_deg = min(MAX_DEG, int(a.O))
        for n in range(1, max_deg + 1):
            mu = float(a.m0) + n * delta
            if mu < mz_min or mu > mz_max:
                dropped_out += 1
                continue
            counts, spacing = count_windows(mz, mu)
            rows.append(
                (
                    deriv,
                    int(a.anchor_idx),
                    n,
                    mu,
                    float(a.m0),
                    float(a.intensity),
                    float(a.log_intensity),
                    int(a.n_candidates),
                    float(a.log_candidates),
                    str(a.iso_status),
                    int(a.C),
                    int(a.H),
                    int(a.O),
                    int(a.N),
                    int(a.S),
                    int(a.P),
                    int(a.X),
                    float(a.DBE),
                    float(spacing),
                    *counts,
                )
            )
    cols = [
        "deriv",
        "anchor_idx",
        "n",
        "mu",
        "m0",
        "src_intensity",
        "log_intensity",
        "n_candidates",
        "log_candidates",
        "iso_status",
        "C",
        "H",
        "O",
        "N",
        "S",
        "P",
        "X",
        "DBE",
        "local_spacing",
        *[f"count_{w:g}" for w in WINDOWS],
    ]
    df = pd.DataFrame(rows, columns=cols)
    df["local_density"] = 1.0 / df["local_spacing"]
    for w in WINDOWS:
        expected = (2 * w * 1e-6 * df["mu"]) / df["local_spacing"]
        df[f"expected_{w:g}"] = expected
        df[f"excess_{w:g}"] = df[f"count_{w:g}"] / expected.replace(0, np.nan)
    return df, len(mz), dropped_out


def agg_windows(df: pd.DataFrame) -> list[dict]:
    out = []
    for deriv, g in df.groupby("deriv", sort=True):
        for win in WINDOWS:
            c = g[f"count_{win:g}"]
            out.append(
                {
                    "deriv": deriv,
                    "window_ppm": win,
                    "n_positions": int(len(g)),
                    "mean": round(float(c.mean()), 4),
                    "median": float(c.median()),
                    "share_0": round(float((c == 0).mean()), 4),
                    "share_1": round(float((c == 1).mean()), 4),
                    "share_ge2": round(float((c >= 2).mean()), 4),
                    "share_ge3": round(float((c >= 3).mean()), 4),
                    "total_pairs": int(c.sum()),
                }
            )
    return out


def agg_group(df: pd.DataFrame, by: str, win: float = 2.0) -> list[dict]:
    out = []
    for keys, g in df.groupby(["deriv", by], sort=True):
        deriv, val = keys
        c = g[f"count_{win:g}"]
        out.append(
            {
                "deriv": deriv,
                by: (
                    val
                    if not isinstance(val, (np.integer, np.floating))
                    else float(val)
                ),
                "n_positions": int(len(g)),
                "mean": round(float(c.mean()), 4),
                "share_ge1": round(float((c >= 1).mean()), 4),
                "share_ge2": round(float((c >= 2).mean()), 4),
                "mean_expected": round(float(g[f"expected_{win:g}"].mean()), 4),
                "mean_excess": round(
                    float(
                        g[f"excess_{win:g}"].replace([np.inf, -np.inf], np.nan).mean()
                    ),
                    4,
                ),
            }
        )
    return out


def corr_table(df: pd.DataFrame, win: float = 2.0) -> list[dict]:
    factors = [
        "mu",
        "n",
        "log_intensity",
        "log_candidates",
        "C",
        "H",
        "O",
        "N",
        "S",
        "P",
        "X",
        "DBE",
        "local_density",
        "local_spacing",
        f"expected_{win:g}",
    ]
    out = []
    for deriv, g in df.groupby("deriv", sort=True):
        sample = g.sample(n=min(60000, len(g)), random_state=0)
        y = sample[f"count_{win:g}"]
        for fac in factors:
            rho, p = stats.spearmanr(sample[fac], y, nan_policy="omit")
            out.append(
                {
                    "deriv": deriv,
                    "factor": fac,
                    "spearman_rho": round(float(rho), 4),
                    "p_value": float(p),
                    "n": int(len(sample)),
                }
            )
    return out


def fit_poisson(df: pd.DataFrame, win: float = 2.0) -> dict:
    """Пуассоновская GLM на выборке: ассоциации, не причинность."""
    out = {}
    for deriv, g in df.groupby("deriv", sort=True):
        s = g.sample(n=min(80000, len(g)), random_state=1).copy()
        y = s[f"count_{win:g}"].to_numpy(float)
        feats = {
            "log_mu": np.log(s["mu"].to_numpy(float)),
            "log_density": np.log(s["local_density"].clip(lower=1e-6)),
            "n": s["n"].to_numpy(float),
            "log_intensity": s["log_intensity"].to_numpy(float),
            "log_candidates": s["log_candidates"].to_numpy(float),
            "C": s["C"].to_numpy(float),
            "O": s["O"].to_numpy(float),
            "is_cd3co": (s["deriv"] == "cd3co").astype(float).to_numpy(),
            "iso_confirmed": (s["iso_status"] == "confirmed").astype(float).to_numpy(),
        }
        names = ["intercept"] + list(feats)
        X = np.column_stack(
            [np.ones(len(s))]
            + [(v - v.mean()) / (v.std() or 1.0) for v in feats.values()]
        )
        # is_cd3co внутри одной производной константа — убираем
        if deriv in ("cd3", "cd3co"):
            keep = [i for i, nm in enumerate(names) if nm != "is_cd3co"]
            X = X[:, keep]
            names = [names[i] for i in keep]

        def nll(beta):
            eta = np.clip(X @ beta, -20, 20)
            return float(np.sum(np.exp(eta) - y * eta))

        def grad(beta):
            eta = np.clip(X @ beta, -20, 20)
            return X.T @ (np.exp(eta) - y)

        res = minimize(nll, np.zeros(X.shape[1]), jac=grad, method="L-BFGS-B")
        beta = res.x
        eta = np.clip(X @ beta, -20, 20)
        mu = np.exp(eta)
        # ковариация (без поправки на overdispersion)
        hess = X.T @ (X * mu[:, None])
        try:
            cov = np.linalg.inv(hess)
            se = np.sqrt(np.diag(cov))
        except np.linalg.LinAlgError:
            se = np.full(len(beta), np.nan)
        null_mu = np.full(len(y), max(y.mean(), 1e-12))
        mu_safe = np.maximum(mu, 1e-12)
        mask = y > 0
        ll = np.zeros(len(y))
        ll0 = np.zeros(len(y))
        ll[mask] = y[mask] * np.log(y[mask] / mu_safe[mask])
        ll0[mask] = y[mask] * np.log(y[mask] / null_mu[mask])
        dev = 2 * np.sum(ll - (y - mu))
        dev0 = 2 * np.sum(ll0 - (y - null_mu))
        coefs = []
        for nm, b, s in zip(names, beta, se):
            z = b / s if s and np.isfinite(s) else np.nan
            coefs.append(
                {
                    "term": nm,
                    "coef": round(float(b), 4),
                    "irr": round(float(np.exp(b)), 4),
                    "se": round(float(s), 4) if np.isfinite(s) else None,
                    "z": round(float(z), 3) if np.isfinite(z) else None,
                }
            )
        out[deriv] = {
            "n": int(len(y)),
            "converged": bool(res.success),
            "deviance_explained": round(float(1 - dev / dev0), 4) if dev0 > 0 else None,
            "coefficients": coefs,
        }
    return out


def reverse_counts(spec, positions: pd.DataFrame, deriv: str) -> list[dict]:
    mz = np.sort(spec.table["mass"].to_numpy(float))
    mu = np.sort(positions.loc[positions["deriv"] == deriv, "mu"].to_numpy(float))
    out = []
    for w in WINDOWS:
        h = w * 1e-6 * mz
        lo = np.searchsorted(mu, mz - h, side="left")
        hi = np.searchsorted(mu, mz + h, side="right")
        c = hi - lo
        out.append(
            {
                "deriv": deriv,
                "window_ppm": w,
                "n_peaks": int(len(mz)),
                "mean_positions_per_peak": round(float(c.mean()), 4),
                "share_0": round(float((c == 0).mean()), 4),
                "share_1": round(float((c == 1).mean()), 4),
                "share_ge2": round(float((c >= 2).mean()), 4),
                "total_pairs": int(c.sum()),
            }
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--cache", default="D:/Temp/User/denoise_grid_cache/denoise_grid_src.pkl"
    )
    ap.add_argument("--out-dir", default="D:/Temp/User")
    ap.add_argument("--md", default="docs/ppm_window_occupancy_f16.md")
    a = ap.parse_args()

    t0 = time.perf_counter()
    cache = pd.read_pickle(a.cache)
    src, dmet_raw, dacet_raw = cache["src"], cache["dmet"], cache["dacet"]
    dmet = denoise(dmet_raw, force=2.0)
    dacet = denoise(dacet_raw, force=2.0)
    anchors = build_anchors(src)
    print(
        f"[{time.strftime('%H:%M:%S')}] anchors={len(anchors)}, "
        f"dmet={dmet.n_peaks}, dacet={dacet.n_peaks}",
        flush=True,
    )

    frames = []
    meta = {"anchors": int(len(anchors)), "dropped_out_of_range": {}}
    for deriv, spec, delta in (
        ("cd3", dmet, CHEM.derivatization_shifts["delta_cd3"]),
        ("cd3co", dacet, CHEM.derivatization_shifts["delta_cd3co"]),
    ):
        df, n_peaks, dropped = build_positions(anchors, spec, deriv, delta)
        frames.append(df)
        meta["dropped_out_of_range"][deriv] = int(dropped)
        print(
            f"[{time.strftime('%H:%M:%S')}] {deriv}: positions={len(df)}, "
            f"peaks={n_peaks}, dropped_out={dropped}",
            flush=True,
        )
    pos = pd.concat(frames, ignore_index=True)

    # Признак «у якоря есть серия» (для сравнения; отбор циркулярен).
    # c3/c3co лежат в кеше conflict_pairs, а не в кеше денойза.
    series_map = {}
    series_cache = Path("D:/Temp/User/conflict_cache/series.pkl")
    if series_cache.exists():
        sc = pd.read_pickle(series_cache)
    else:
        sc = cache
    for deriv, key in (("cd3", "c3"), ("cd3co", "c3co")):
        if key in sc and sc[key] is not None:
            f = sc[key]
            series_map[deriv] = f.set_index(f["mass_src"].round(6))[
                "n_groups"
            ].to_dict()
    anchors["mass_key"] = anchors["mass"].round(6)
    pos["mass_key"] = anchors["mass"].round(6).to_numpy()[pos["anchor_idx"].to_numpy()]
    pos["series_n_groups"] = [
        series_map.get(d, {}).get(m, np.nan)
        for d, m in zip(pos["deriv"], pos["mass_key"])
    ]
    pos["has_series"] = pos["series_n_groups"].notna()

    report = {
        "dataset": "Fulvagra F16",
        "denoise": "gmm force=2.0",
        "windows_ppm": list(WINDOWS),
        "max_degree": MAX_DEG,
        "degree_bound": "n <= O (верхняя химическая граница)",
        "local_da": LOCAL_DA,
        "meta": meta,
        "windows": agg_windows(pos),
        "by_degree": agg_group(pos, "n"),
        "by_iso_status": agg_group(pos, "iso_status"),
        "by_has_series": agg_group(pos, "has_series"),
        "correlations": corr_table(pos),
        "poisson": fit_poisson(pos),
        "reverse": [],
        "sanity_total_pairs": {},
        "seconds": None,
    }

    for deriv, spec in (("cd3", dmet), ("cd3co", dacet)):
        report["reverse"].extend(reverse_counts(spec, pos, deriv))

    # Массовые бины и квартили факторов
    bins = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]
    pos["mass_bin"] = pd.cut(pos["mu"], bins=bins, right=False)
    report["by_mass_bin"] = agg_group(pos, "mass_bin")
    for fac in ("local_density", "log_intensity", "log_candidates"):
        pos[f"{fac}_q"] = pos.groupby("deriv")[fac].transform(
            lambda s: pd.qcut(
                s.rank(method="first"), 4, labels=["Q1", "Q2", "Q3", "Q4"]
            )
        )
        report[f"by_{fac}_quartile"] = agg_group(pos, f"{fac}_q")

    # Сколько кандидатов приходится на один исходный компонент (сумма по
    # степеням) — альтернативный взгляд на «среднее число пиков».
    per_anchor = (
        pos.groupby(["deriv", "anchor_idx"])
        .agg(
            n_degrees=("n", "size"),
            **{f"pairs_{w:g}": (f"count_{w:g}", "sum") for w in WINDOWS},
        )
        .reset_index()
    )
    report["per_anchor"] = []
    for deriv, g in per_anchor.groupby("deriv"):
        row = {
            "deriv": deriv,
            "n_anchors": int(len(g)),
            "mean_degrees": round(float(g["n_degrees"].mean()), 2),
        }
        for w in WINDOWS:
            col = f"pairs_{w:g}"
            row[f"mean_pairs_{w:g}"] = round(float(g[col].mean()), 3)
            row[f"share_ge1_{w:g}"] = round(float((g[col] >= 1).mean()), 4)
            row[f"share_ge2_{w:g}"] = round(float((g[col] >= 2).mean()), 4)
        report["per_anchor"].append(row)

    for w in WINDOWS:
        fwd = int(pos[f"count_{w:g}"].sum())
        rev = sum(r["total_pairs"] for r in report["reverse"] if r["window_ppm"] == w)
        report["sanity_total_pairs"][str(w)] = {"forward": fwd, "reverse": rev}

    report["seconds"] = round(time.perf_counter() - t0, 1)
    out_dir = Path(a.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "ppm_window_occupancy_f16.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    pos.drop(columns=["mass_key"]).to_pickle(out_dir / "ppm_window_occupancy_f16.pkl")
    for key in (
        "windows",
        "by_degree",
        "by_iso_status",
        "by_has_series",
        "by_mass_bin",
        "by_local_density_quartile",
        "by_log_intensity_quartile",
        "by_log_candidates_quartile",
        "per_anchor",
    ):
        pd.DataFrame(report[key]).to_csv(out_dir / f"ppm_window_{key}.csv", index=False)
    pd.DataFrame(report["correlations"]).to_csv(
        out_dir / "ppm_window_correlations.csv", index=False
    )

    # Краткий markdown-черновик (интерпретация — в docs вручную)
    lines = [
        "# Занятость ppm-окон ожидаемых продуктов (F16, GMM 2.0)",
        "",
        f"Позиций: {len(pos)}; якорей: {meta['anchors']}; "
        f"вне диапазона: {meta['dropped_out_of_range']}.",
        "",
        "## По ширине окна",
        "",
        "| Производная | Окно, ppm | Среднее | Медиана | 0 | 1 | ≥2 | ≥3 |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in report["windows"]:
        lines.append(
            f"| {r['deriv']} | {r['window_ppm']} | {r['mean']} | {r['median']} | "
            f"{r['share_0']:.1%} | {r['share_1']:.1%} | {r['share_ge2']:.1%} | "
            f"{r['share_ge3']:.1%} |"
        )
    lines += ["", "## По степени (2 ppm)", ""]
    lines += [
        "| Производная | n | Позиций | Среднее | ≥1 | ≥2 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in report["by_degree"]:
        if r["n"] <= 10:
            lines.append(
                f"| {r['deriv']} | {int(r['n'])} | {r['n_positions']} | "
                f"{r['mean']} | {r['share_ge1']:.1%} | {r['share_ge2']:.1%} |"
            )
    lines += ["", "## Корреляции (2 ppm)", ""]
    lines += [
        "| Производная | Фактор | Spearman ρ |",
        "|---|---|---:|",
    ]
    for r in report["correlations"]:
        lines.append(f"| {r['deriv']} | {r['factor']} | {r['spearman_rho']} |")
    lines += ["", "## Poisson GLM (2 ppm)", ""]
    for deriv, g in report["poisson"].items():
        lines.append(
            f"**{deriv}**: n={g['n']}, deviance explained={g['deviance_explained']}"
        )
        lines += ["", "| Терм | coef | IRR | z |", "|---|---:|---:|---:|"]
        for c in g["coefficients"]:
            lines.append(f"| {c['term']} | {c['coef']} | {c['irr']} | {c['z']} |")
        lines.append("")
    lines += ["## На один исходный компонент (сумма по степеням)", ""]
    lines += [
        "| Производная | Якорей | Ср. степеней | Ср. кандидатов @2 ppm | ≥1 @2 ppm | ≥2 @2 ppm |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in report["per_anchor"]:
        lines.append(
            f"| {r['deriv']} | {r['n_anchors']} | {r['mean_degrees']} | "
            f"{r['mean_pairs_2']} | {r['share_ge1_2']:.1%} | "
            f"{r['share_ge2_2']:.1%} |"
        )
    lines += ["", "## Обратное направление", ""]
    lines += [
        "| Производная | Окно, ppm | Позиций на пик | 0 | 1 | ≥2 |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in report["reverse"]:
        lines.append(
            f"| {r['deriv']} | {r['window_ppm']} | {r['mean_positions_per_peak']} | "
            f"{r['share_0']:.1%} | {r['share_1']:.1%} | {r['share_ge2']:.1%} |"
        )
    Path(a.md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(
        f"\nвремя: {report['seconds']} c | JSON: {out_dir/'ppm_window_occupancy_f16.json'}"
    )
    print(f"markdown: {a.md}")


if __name__ == "__main__":
    main()
