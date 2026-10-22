"""Profile-уточнение вычитания исходника + occupancy на F16 (restricted assign).

Логика:
  * если в окно дериватизата не попадает мешающий исходный пик — profile НЕ
    вызывается; наличие пика в окне считаем дериватизатом;
  * если мешающий пик есть — читаем profile в объединении окон
    [min(mu, m_B)-h, max(mu, m_B)+h] и считаем разрешённые пики:
      k_obs >= k_src+1 -> present
      k_obs == k_src   -> unconfirmed
      иначе            -> unreliable;
  * unconfirmed может подтвердиться следующим шагом (chain), если n+1 present
    и его область без мешающих пиков;
  * обрыв серии — первый not present/chain.

Выход: JSON, CSV, pickle позиций, markdown.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ablation_f16 import DECOYS, REAL

from src.configs import CHEM, PIPELINE
from src.core.domain.molecule import parse_formula
from src.core.io.raw_profile import _open_raw, scan_numbers, scan_profile
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.spectrum import Spectrum, find_series
from src.core.spectrum._decoy import DECOY_SEED, decoy_shifts
from src.core.spectrum._series import _theor_ion_mass_cached
from src.core.spectrum._validate import attach_fdr

from profile_resolve import profile_peaks

WINDOWS = (
    0.00010,
    0.00015,
    0.00020,
    0.00025,
    0.00030,
    0.00035,
    0.00040,
    0.00045,
    0.00050,
    0.00060,
    0.00070,
    0.00080,
    0.00100,
)
MAX_H = max(WINDOWS)
MAX_DEG = 10


def htag(h: float) -> str:
    return f"{int(round(h * 1e5)):05d}"


def build_anchors(src) -> pd.DataFrame:
    t = src.table
    mask = t["assign"].astype(bool) & t["brutto"].notna()
    a = t.loc[mask, ["mass", "intensity", "brutto", "all_candidates"]].copy()
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
    a["O"] = [
        int(parse_formula(str(b)).get("O", 0)) if b else 0
        for b in a["brutto"].astype(str)
    ]
    a = a[a["O"] >= 1].reset_index(drop=True)
    a["anchor_idx"] = np.arange(len(a))
    return a


def load_profiles(raw_path: str):
    raw = _open_raw(raw_path)
    try:
        scans = scan_numbers(raw)
        pick = [
            scans[i]
            for i in np.linspace(0, len(scans) - 1, min(3, len(scans)))
            .round()
            .astype(int)
        ]
        out = []
        for s in pick:
            mz, inten = scan_profile(raw, s)
            if mz.size:
                out.append((mz, inten))
    finally:
        raw.Dispose()
    return out


def count_centroids(mz_sorted: np.ndarray, mu: float, h: float) -> int:
    lo = np.searchsorted(mz_sorted, mu - h, side="left")
    hi = np.searchsorted(mz_sorted, mu + h, side="right")
    return int(hi - lo)


def nearest_centroid(mz_sorted: np.ndarray, mu: float, h: float):
    lo = int(np.searchsorted(mz_sorted, mu - h, side="left"))
    hi = int(np.searchsorted(mz_sorted, mu + h, side="right"))
    if hi <= lo:
        return None
    seg = mz_sorted[lo:hi]
    return float(seg[np.argmin(np.abs(seg - mu))])


def classify_positions(anchors, spec, profiles, delta: float, deriv: str, src_ms):
    mz_sorted = np.sort(spec.table["mass"].to_numpy(float))
    rows = []
    for a in anchors.itertuples(index=False):
        max_deg = min(MAX_DEG, int(a.O))
        for n in range(1, max_deg + 1):
            mu = float(a.m0) + n * delta
            if mu < mz_sorted[0] or mu > mz_sorted[-1]:
                continue
            lo = int(np.searchsorted(src_ms, mu - 2 * MAX_H, side="left"))
            hi = int(np.searchsorted(src_ms, mu + 2 * MAX_H, side="right"))
            inter = src_ms[lo:hi]
            # для каждого окна свои k_src/union
            h_rows = {}
            if inter.size == 0:
                for h in WINDOWS:
                    cnt = count_centroids(mz_sorted, mu, h)
                    h_rows[h] = {
                        "status": "present" if cnt > 0 else "absent",
                        "k_src": 0,
                        "n_obs": cnt,
                        "peak_mz": (
                            nearest_centroid(mz_sorted, mu, h) if cnt else np.nan
                        ),
                    }
            else:
                union_lo = min(mu, float(inter.min())) - MAX_H
                union_hi = max(mu, float(inter.max())) + MAX_H
                peaks_per_scan = [
                    profile_peaks(mz, inten, union_lo, union_hi, min_snr=3.0)
                    for mz, inten in profiles
                ]
                for h in WINDOWS:
                    k_src = int(np.count_nonzero(np.abs(inter - mu) <= 2 * h))
                    if k_src == 0:
                        cnt = count_centroids(mz_sorted, mu, h)
                        h_rows[h] = {
                            "status": "present" if cnt > 0 else "absent",
                            "k_src": 0,
                            "n_obs": cnt,
                            "peak_mz": (
                                nearest_centroid(mz_sorted, mu, h) if cnt else np.nan
                            ),
                        }
                        continue
                    u_lo = min(mu, float(inter.min())) - h
                    u_hi = max(mu, float(inter.max())) + h
                    votes = []
                    for peaks in peaks_per_scan:
                        k_obs = sum(1 for p in peaks if u_lo <= p["mz"] <= u_hi)
                        if k_obs >= k_src + 1:
                            votes.append("present")
                        elif k_obs == k_src:
                            votes.append("unconfirmed")
                        else:
                            votes.append("unreliable")
                    if votes.count("present") >= 2:
                        status = "present"
                    elif votes.count("unconfirmed") >= 2:
                        status = "unconfirmed"
                    else:
                        status = "unreliable"
                    # ближайший profile-пик к mu как наблюдённый дериватизат
                    cand = [
                        p["mz"]
                        for peaks in peaks_per_scan
                        for p in peaks
                        if u_lo <= p["mz"] <= u_hi
                    ]
                    if status == "present" and cand:
                        peak_mz = float(min(cand, key=lambda z: abs(z - mu)))
                    elif status in ("unconfirmed", "unreliable"):
                        peak_mz = nearest_centroid(mz_sorted, mu, h)
                    else:
                        peak_mz = np.nan
                    h_rows[h] = {
                        "status": status,
                        "k_src": k_src,
                        "n_obs": 1 if status == "present" else 0,
                        "peak_mz": peak_mz,
                    }
            rows.append(
                {
                    "deriv": deriv,
                    "anchor_idx": int(a.anchor_idx),
                    "n": n,
                    "mu": mu,
                    "m0": float(a.m0),
                    "O": int(a.O),
                    "n_candidates": int(a.n_candidates),
                    **{
                        f"{key}_{htag(h)}": val
                        for h, d in h_rows.items()
                        for key, val in d.items()
                    },
                }
            )
    return pd.DataFrame(rows)


def apply_chain(df: pd.DataFrame) -> pd.DataFrame:
    df = df.sort_values(["deriv", "anchor_idx", "n"]).reset_index(drop=True)
    d_arr = df["deriv"].to_numpy()
    a_arr = df["anchor_idx"].to_numpy()
    for h in WINDOWS:
        st = f"status_{htag(h)}"
        ks = f"k_src_{htag(h)}"
        statuses = df[st].to_numpy().copy()
        ksrc = df[ks].to_numpy()
        start = 0
        for i in range(1, len(df) + 1):
            if i == len(df) or a_arr[i] != a_arr[start] or d_arr[i] != d_arr[start]:
                for j in range(i - 2, start - 1, -1):
                    if (
                        statuses[j] == "unconfirmed"
                        and statuses[j + 1] == "present"
                        and ksrc[j + 1] == 0
                    ):
                        statuses[j] = "chain"
                start = i
        df[st] = statuses
    return df


def occupancy(df: pd.DataFrame, spec, deriv: str) -> list[dict]:
    mz_sorted = np.sort(spec.table["mass"].to_numpy(float))
    mz_round = np.round(mz_sorted, 6)
    sub = df[df["deriv"] == deriv].sort_values(["anchor_idx", "n"])
    a_arr = sub["anchor_idx"].to_numpy()
    out = []
    for h in WINDOWS:
        st = f"status_{htag(h)}"
        pm = f"peak_mz_{htag(h)}"
        statuses = sub[st].to_numpy()
        peaks = sub[pm].to_numpy(float)
        prefixes = []
        peak_claims: dict[float, int] = {}
        n_present = 0
        start = 0
        for i in range(1, len(sub) + 1):
            if i == len(sub) or a_arr[i] != a_arr[start]:
                prefix = 0
                for j in range(start, i):
                    if statuses[j] in ("present", "chain"):
                        prefix += 1
                        n_present += 1
                        p = peaks[j]
                        if p == p:
                            key = round(float(p), 6)
                            peak_claims[key] = peak_claims.get(key, 0) + 1
                    else:
                        break
                prefixes.append(prefix)
                start = i
        prefixes = np.asarray(prefixes)
        counts = np.array([peak_claims.get(m, 0) for m in mz_round])
        out.append(
            {
                "deriv": deriv,
                "h_da": h,
                "n_anchors": int(len(prefixes)),
                "mean_prefix": round(float(prefixes.mean()), 3),
                "median_prefix": float(np.median(prefixes)),
                "prefix_ge2": round(float((prefixes >= 2).mean()), 4),
                "prefix_ge4": round(float((prefixes >= 4).mean()), 4),
                "positions_present": int(n_present),
                "mean_peaks_per_position": round(n_present / max(1, prefixes.sum()), 3),
                "unique_peaks_claimed": int(len(peak_claims)),
                "mean_positions_per_peak": round(float(counts.mean()), 3),
                "share_peaks_ge2": round(float((counts >= 2).mean()), 4),
                "share_peaks_ge1": round(float((counts >= 1).mean()), 4),
            }
        )
    return out


def hard_filter(spec, df: pd.DataFrame, h: float, deriv: str):
    st = f"status_{htag(h)}"
    pm = f"peak_mz_{htag(h)}"
    keep, remove = [], []
    for row in df[df["deriv"] == deriv].itertuples(index=False):
        p = getattr(row, pm)
        if p != p:
            continue
        if getattr(row, st) in ("present", "chain"):
            keep.append(float(p))
        elif getattr(row, st) in ("unconfirmed", "unreliable"):
            remove.append(float(p))
    table = spec.table
    masses = table["mass"].to_numpy(float)
    drop = np.zeros(len(table), dtype=bool)
    keep_idx = set()
    for p in keep:
        j = int(np.searchsorted(masses, p))
        cand = [k for k in (j - 1, j, j + 1) if 0 <= k < len(masses)]
        if cand:
            k = min(cand, key=lambda z: abs(masses[z] - p))
            if abs(masses[k] - p) <= 0.01:
                keep_idx.add(k)
    for p in remove:
        j = int(np.searchsorted(masses, p))
        cand = [k for k in (j - 1, j, j + 1) if 0 <= k < len(masses)]
        if not cand:
            continue
        k = min(cand, key=lambda z: abs(masses[z] - p))
        if abs(masses[k] - p) <= 0.01 and k not in keep_idx:
            drop[k] = True
    return Spectrum(table=table.loc[~drop].reset_index(drop=True)), int(drop.sum())


def length_hist(series: pd.DataFrame) -> dict:
    if series is None or len(series) == 0:
        return {}
    lens = series["steps_found"].map(len).astype(int)
    return {str(i): int((lens == i).sum()) for i in range(1, MAX_DEG + 1)} | {
        ">=10": int((lens >= 10).sum())
    }


def metrics(scored: pd.DataFrame) -> dict:
    keep = scored[scored["fdr_significant"]]
    return {
        "target_series": int(len(scored)),
        "retained": int(len(keep)),
        "mean_len_retained": (
            round(float(keep["steps_found"].map(len).mean()), 3) if len(keep) else 0.0
        ),
        "median_len_retained": (
            float(keep["steps_found"].map(len).median()) if len(keep) else 0.0
        ),
        "mean_len_all": round(float(scored["steps_found"].map(len).mean()), 3),
        "length_hist_all": length_hist(scored),
        "length_hist_retained": length_hist(keep),
    }


def soft_filter(scored: pd.DataFrame, status_map: dict, mass_to_idx: dict) -> dict:
    """Мягкий режим: <=1 unconfirmed/unreliable, последний шаг present/chain."""
    kept = 0
    lens = []
    for row in scored.itertuples(index=False):
        idx = mass_to_idx.get(round(float(row.mass_src), 6))
        steps = list(row.steps_found)
        if idx is None or not steps:
            continue
        statuses = [status_map.get((idx, int(n)), "unconfirmed") for n in steps]
        unconf = sum(s in ("unconfirmed", "unreliable") for s in statuses)
        last_ok = statuses[-1] in ("present", "chain")
        if unconf <= 1 and last_ok:
            kept += 1
            lens.append(len(steps))
    return {
        "retained": int(kept),
        "mean_len_retained": round(float(np.mean(lens)), 3) if lens else 0.0,
        "length_hist": {
            str(i): int(sum(1 for x in lens if x == i)) for i in range(1, MAX_DEG + 1)
        }
        | {">=10": int(sum(1 for x in lens if x >= 10))},
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", default="D:/Temp/User/nom_restrict_cache/restricted.pkl")
    ap.add_argument("--out-dir", default="D:/Temp/User")
    ap.add_argument("--limit", type=int, default=0, help="для smoke-теста")
    ap.add_argument("--json", default="D:/Temp/User/restricted_profile_f16.json")
    a = ap.parse_args()

    t0 = time.perf_counter()
    cache = pd.read_pickle(a.cache)
    src, dmet, dacet = cache["src"], cache["dmet"], cache["dacet"]
    anchors = build_anchors(src)
    if a.limit:
        anchors = anchors.head(a.limit).copy()
        anchors["anchor_idx"] = np.arange(len(anchors))
    print(
        f"[{time.strftime('%H:%M:%S')}] anchors={len(anchors)}; "
        f"dmet={dmet.n_peaks}; dacet={dacet.n_peaks}",
        flush=True,
    )

    base = Path("data/real_sets") / "Fulvagra F16"
    _, m_raw, d_raw = REAL["Fulvagra F16"]
    # Мешающие пики — наблюдаемые m/z всех назначенных исходных пиков
    # (включая O=0), как в subtract_matching_peaks.
    src_all = src.table[src.table["assign"].astype(bool) & src.table["brutto"].notna()]
    src_ms = np.sort(src_all["mass"].to_numpy(float))

    frames = []
    for deriv, spec, raw_name, delta in (
        ("cd3", dmet, m_raw, CHEM.derivatization_shifts["delta_cd3"]),
        ("cd3co", dacet, d_raw, CHEM.derivatization_shifts["delta_cd3co"]),
    ):
        t1 = time.perf_counter()
        profiles = load_profiles(str((base / raw_name).resolve()))
        df = classify_positions(anchors, spec, profiles, delta, deriv, src_ms)
        frames.append(df)
        print(
            f"[{time.strftime('%H:%M:%S')}] {deriv}: positions={len(df)}, "
            f"profile_calls={int((df[[f'k_src_{htag(h)}' for h in WINDOWS]].max(axis=1) > 0).sum())}, "
            f"{time.perf_counter()-t1:.1f} c",
            flush=True,
        )
    pos = pd.concat(frames, ignore_index=True)
    pos = apply_chain(pos)
    print(f"[{time.strftime('%H:%M:%S')}] chain применён", flush=True)

    report = {
        "dataset": "Fulvagra F16",
        "assign": "restricted NOM: C5-60 H4-120 O1-30, N<=5, S<=2, P<=1, Cl<=2, F/Br/I=0",
        "denoise": "gmm force=2.0",
        "windows_da": list(WINDOWS),
        "max_deg": MAX_DEG,
        "anchors": int(len(anchors)),
        "occupancy": [],
        "none": {},
        "hard": {},
        "soft": {},
        "seconds": None,
    }
    for deriv, spec in (("cd3", dmet), ("cd3co", dacet)):
        report["occupancy"].extend(occupancy(pos, spec, deriv))

    # Режимы для 0.0003 и 0.0005 Да: none / hard / soft
    defaults = PIPELINE.run_pipeline_defaults
    kw = dict(
        ppm_tol=defaults["ppm_tol"],
        max_groups=MAX_DEG,
        max_gaps=0,
        require_first_step=True,
        significance_level=defaults["significance_level"],
    )
    mass_to_idx = {
        round(float(m), 6): int(i)
        for m, i in zip(anchors["mass"], anchors["anchor_idx"])
    }
    for h in (0.00030, 0.00050):
        key = f"{h:.5f}"
        report["none"][key] = {}
        report["hard"][key] = {}
        report["soft"][key] = {}
        for deriv, spec, delta in (
            ("cd3", dmet, CHEM.derivatization_shifts["delta_cd3"]),
            ("cd3co", dacet, CHEM.derivatization_shifts["delta_cd3co"]),
        ):
            sub = pos[pos["deriv"] == deriv]
            shifts = decoy_shifts(delta, k=DECOYS, seed=DECOY_SEED)

            # none
            target = find_series(src, spec, delta, **kw)
            decoys = [find_series(src, spec, delta + sh, **kw) for sh in shifts]
            scored_none = attach_fdr(target, decoys)
            report["none"][key][deriv] = metrics(scored_none)

            # soft: по статусам target-серий (без FDR для decoy)
            st = f"status_{htag(h)}"
            status_map = {
                (int(r.anchor_idx), int(r.n)): getattr(r, st)
                for r in sub.itertuples(index=False)
            }
            report["soft"][key][deriv] = {
                "all": soft_filter(scored_none, status_map, mass_to_idx),
                "significant": soft_filter(
                    scored_none[scored_none["fdr_significant"]],
                    status_map,
                    mass_to_idx,
                ),
            }

            # hard
            filtered, removed = hard_filter(spec, sub, h, deriv)
            target_h = find_series(src, filtered, delta, **kw)
            decoys_h = [find_series(src, filtered, delta + sh, **kw) for sh in shifts]
            scored_h = attach_fdr(target_h, decoys_h)
            report["hard"][key][deriv] = {
                "removed_peaks": removed,
                "peaks_left": int(filtered.n_peaks),
                **metrics(scored_h),
            }
            print(
                f"[{time.strftime('%H:%M:%S')}] {deriv} h={h}: "
                f"none ret={report['none'][key][deriv]['retained']}, "
                f"hard ret={report['hard'][key][deriv]['retained']} "
                f"(removed {removed})",
                flush=True,
            )
    report["seconds"] = round(time.perf_counter() - t0, 1)
    Path(a.json).parent.mkdir(parents=True, exist_ok=True)
    Path(a.json).write_text(
        json.dumps(report, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    pos.to_pickle(Path(a.out_dir) / "restricted_profile_positions.pkl")
    pd.DataFrame(report["occupancy"]).to_csv(
        Path(a.out_dir) / "restricted_profile_occupancy.csv", index=False
    )
    print(f"время: {report['seconds']} c | {a.json}")


if __name__ == "__main__":
    main()
