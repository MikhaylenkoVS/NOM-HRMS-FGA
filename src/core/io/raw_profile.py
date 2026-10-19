"""Проверка пиков по сырым данным: персистентность по сканам, форма, локальный S/N.

Модуль работает с Thermo RAW напрямую (RawFileReader) и нужен только для
**кандидатов в шаги серий** (тысячи масс, а не миллионы точек): полный профиль
скана читается один раз на скан и нарезается локальными окнами.

Метрики на каждую массу:
  * ``persistence`` — доля сканов, где в ppm-окне есть центроид (0..1);
  * ``snr``         — локальный S/N по профилю (медиана/MAD вокруг пика);
  * ``fwhm``        — ширина пика на полувысоте, Да;
  * ``shape_ok``    — S/N ≥ порога, FWHM в разумных пределах, есть вершина.
"""

from __future__ import annotations

import logging
import sys

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def _open_raw(raw_path: str):
    """Открыть RAW через RawFileReader (как в raw_thermo_adapter)."""
    from src.core.io.raw_thermo_adapter import _thermo_dll_dir

    sys.path.insert(0, _thermo_dll_dir())
    import clr

    clr.AddReference("ThermoFisher.CommonCore.Data")
    clr.AddReference("ThermoFisher.CommonCore.RawFileReader")
    from ThermoFisher.CommonCore.Data.Business import Device
    from ThermoFisher.CommonCore.RawFileReader import RawFileReaderAdapter

    raw = RawFileReaderAdapter.FileFactory(raw_path)
    if not raw.IsOpen or raw.IsError:
        raise RuntimeError(f"Не удалось открыть RAW: {raw.FileError}")
    raw.SelectInstrument(Device.MS, 1)
    return raw


def scan_numbers(raw, max_scans: int | None = None) -> list[int]:
    first = int(raw.RunHeaderEx.FirstSpectrum)
    last = int(raw.RunHeaderEx.LastSpectrum)
    nums = list(range(first, last + 1))
    if max_scans and len(nums) > max_scans:
        idx = np.linspace(0, len(nums) - 1, max_scans).round().astype(int)
        nums = [nums[i] for i in idx]
    return nums


def scan_centroids(raw, scan: int) -> tuple[np.ndarray, np.ndarray]:
    cs = raw.GetCentroidStream(scan, False)
    if cs is None or getattr(cs, "Length", 0) == 0:
        return np.empty(0), np.empty(0)
    return (
        np.fromiter(cs.Masses, dtype=float),
        np.fromiter(cs.Intensities, dtype=float),
    )


def scan_profile(raw, scan: int) -> tuple[np.ndarray, np.ndarray]:
    stats = raw.GetScanStatsForScanNumber(scan)
    seg = raw.GetSegmentedScanFromScanNumber(scan, stats)
    if seg is None:
        return np.empty(0), np.empty(0)
    return (
        np.fromiter(seg.Positions, dtype=float),
        np.fromiter(seg.Intensities, dtype=float),
    )


def _shape_metrics(
    mz: np.ndarray,
    inten: np.ndarray,
    target: float,
    half_width_da: float,
    noise_half_da: float = 0.2,
) -> dict:
    """S/N, FWHM (непрерывная полуширина) и признаки формы для одной массы."""
    lo = int(np.searchsorted(mz, target - half_width_da))
    hi = int(np.searchsorted(mz, target + half_width_da))
    if hi - lo < 3:
        return {"present": False, "snr": 0.0, "fwhm": float("nan"), "ok": False}
    win_i = inten[lo:hi]
    win_mz = mz[lo:hi]
    apex_off = int(np.argmax(win_i))
    apex = float(win_i[apex_off])

    # Локальный шум: медиана/MAD в окрестности, исключая область пика.
    nlo = int(np.searchsorted(mz, target - noise_half_da))
    nhi = int(np.searchsorted(mz, target + noise_half_da))
    noise = np.concatenate([inten[nlo:lo], inten[hi:nhi]])
    if noise.size < 10:
        return {"present": True, "snr": 0.0, "fwhm": float("nan"), "ok": False}
    med = float(np.median(noise))
    mad = float(np.median(np.abs(noise - med))) * 1.4826
    sigma = mad if mad > 0 else float(np.std(noise))
    if sigma <= 0:
        sigma = max(1e-9, abs(med) * 1e-6)
    snr = min(1e6, max(0.0, (apex - med) / sigma))

    # FWHM: непрерывный спуск от вершины до половины высоты (не «все точки»).
    half = apex / 2.0
    left = apex_off
    while left > 0 and win_i[left - 1] >= half:
        left -= 1
    right = apex_off
    while right < win_i.size - 1 and win_i[right + 1] >= half:
        right += 1
    fwhm = float(win_mz[right] - win_mz[left])
    touches_edge = left == 0 or right == win_i.size - 1

    # Одиночность: смотрим только ближайшую окрестность (±max(4·FWHM, 2 мДа)).
    # В плотном NOM-спектре окно ±20 мДа почти всегда содержит соседний пик,
    # поэтому проверять «весь» профиль вокруг нельзя.
    step = (win_mz[-1] - win_mz[0]) / max(1, win_mz.size - 1)
    guard = max(4.0 * fwhm if np.isfinite(fwhm) else 0.002, 0.002)
    guard_pts = int(guard / step) + 1 if step > 0 else 1
    outside = np.concatenate(
        [
            win_i[max(0, left - guard_pts) : left],
            win_i[right + 1 : right + 1 + guard_pts],
        ]
    )
    single = not (outside.size and outside.max() >= half)
    return {
        "present": True,
        "snr": snr,
        "fwhm": fwhm,
        "ok": (not touches_edge) and single,
    }


def validate_masses(
    raw_path: str,
    masses,
    *,
    ppm: float = 2.0,
    max_scans: int | None = None,
    shape_scans: int = 3,
    half_width_da: float = 0.02,
    min_snr: float = 3.0,
    fwhm_bounds: tuple[float, float] = (1e-4, 0.05),
) -> pd.DataFrame:
    """Проверить список масс по сырому RAW.

    Персистентность считается по центроидам всех (или ``max_scans``) сканов;
    форма и S/N — по профилю нескольких сканов (``shape_scans``), чтобы не
    читать миллионы точек на каждый скан.

    Returns
    -------
    DataFrame
        ``mass, persistence, snr, fwhm, shape_ok``.
    """
    masses = np.asarray(list(masses), dtype=float)
    out = pd.DataFrame(
        {
            "mass": masses,
            "persistence": np.zeros(masses.size),
            "snr": np.full(masses.size, np.nan),
            "fwhm": np.full(masses.size, np.nan),
            "shape_ok": np.zeros(masses.size, dtype=bool),
        }
    )
    if masses.size == 0:
        return out

    raw = _open_raw(raw_path)
    try:
        scans = scan_numbers(raw, max_scans=max_scans)
        logger.info("RAW %s: сканов %d", raw_path, len(scans))
        found = np.zeros(masses.size, dtype=int)
        for scan in scans:
            mz, inten = scan_centroids(raw, scan)
            if mz.size == 0:
                continue
            pos = np.searchsorted(mz, masses)
            left = np.clip(pos - 1, 0, mz.size - 1)
            right = np.clip(pos, 0, mz.size - 1)
            with np.errstate(invalid="ignore", divide="ignore"):
                d1 = np.abs(mz[left] - masses) / masses * 1e6
                d2 = np.abs(mz[right] - masses) / masses * 1e6
            found += (np.minimum(d1, d2) <= ppm).astype(int)
        out["persistence"] = found / max(1, len(scans))

        # форма/S/N — только по нескольким сканам профиля
        pick = (
            scans
            if len(scans) <= shape_scans
            else [
                scans[i]
                for i in np.linspace(0, len(scans) - 1, shape_scans).round().astype(int)
            ]
        )
        snr = np.full(masses.size, np.nan)
        fwhm = np.full(masses.size, np.nan)
        ok = np.zeros(masses.size, dtype=bool)
        for scan in pick:
            mz, inten = scan_profile(raw, scan)
            if mz.size == 0:
                continue
            for i, m in enumerate(masses):
                met = _shape_metrics(mz, inten, float(m), half_width_da)
                if not met["present"]:
                    continue
                snr[i] = met["snr"] if np.isnan(snr[i]) else max(snr[i], met["snr"])
                fwhm[i] = met["fwhm"] if np.isnan(fwhm[i]) else met["fwhm"]
                in_bounds = (
                    fwhm_bounds[0] <= met["fwhm"] <= fwhm_bounds[1]
                    if np.isfinite(met["fwhm"])
                    else False
                )
                ok[i] = ok[i] or (met["ok"] and met["snr"] >= min_snr and in_bounds)
        out["snr"] = np.round(snr, 2)
        out["fwhm"] = np.round(fwhm, 6)
        out["shape_ok"] = ok
    finally:
        raw.Dispose()
    return out
