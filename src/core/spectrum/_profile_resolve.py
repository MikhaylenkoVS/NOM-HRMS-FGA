"""Разрешение пиков в RAW profile для наложений source/derivative."""

from __future__ import annotations

from collections import Counter

import numpy as np

from src.core.io.raw_profile import _open_raw, scan_numbers, scan_profile


def profile_peaks(
    mz: np.ndarray,
    inten: np.ndarray,
    lo: float,
    hi: float,
    *,
    min_snr: float = 3.0,
    fwhm_bounds: tuple[float, float] = (1e-4, 0.05),
    min_sep_factor: float = 0.5,
    noise_half_da: float = 0.2,
) -> list[dict]:
    """Вернуть локальные максимумы в ``[lo, hi]`` с оценкой FWHM/S/N."""
    i0 = int(np.searchsorted(mz, lo, side="left"))
    i1 = int(np.searchsorted(mz, hi, side="right"))
    if i1 - i0 < 3:
        return []
    seg_mz = mz[i0:i1]
    seg_i = inten[i0:i1]

    n0 = int(np.searchsorted(mz, lo - noise_half_da, side="left"))
    n1 = int(np.searchsorted(mz, hi + noise_half_da, side="right"))
    noise = np.concatenate([inten[n0:i0], inten[i1:n1]])
    if noise.size >= 10:
        med = float(np.median(noise))
        mad = float(np.median(np.abs(noise - med))) * 1.4826
        sigma = mad if mad > 0 else float(np.std(noise))
    else:
        med = float(np.median(seg_i))
        sigma = float(np.std(seg_i))
    if sigma <= 0:
        sigma = max(1e-12, abs(med) * 1e-6)
    threshold = med + min_snr * sigma

    idx = (
        np.where(
            (seg_i[1:-1] > seg_i[:-2])
            & (seg_i[1:-1] >= seg_i[2:])
            & (seg_i[1:-1] > threshold)
        )[0]
        + 1
    )
    if idx.size == 0:
        j = int(np.argmax(seg_i))
        if 0 < j < seg_i.size - 1 and seg_i[j] > threshold:
            idx = np.array([j])
        else:
            return []

    peaks: list[dict] = []
    for j in idx:
        apex = float(seg_i[j])
        half = apex / 2.0
        left = int(j)
        while left > 0 and seg_i[left - 1] >= half:
            left -= 1
        right = int(j)
        while right < seg_i.size - 1 and seg_i[right + 1] >= half:
            right += 1
        fwhm = float(seg_mz[right] - seg_mz[left])
        if not (fwhm_bounds[0] <= fwhm <= fwhm_bounds[1]):
            continue
        peaks.append(
            {
                "mz": float(seg_mz[j]),
                "apex": apex,
                "fwhm": fwhm,
                "snr": float((apex - med) / sigma),
            }
        )

    peaks.sort(key=lambda p: p["mz"])
    merged: list[dict] = []
    for p in peaks:
        if merged:
            sep = p["mz"] - merged[-1]["mz"]
            need = min_sep_factor * max(p["fwhm"], merged[-1]["fwhm"])
            if sep < need:
                if p["apex"] > merged[-1]["apex"]:
                    merged[-1] = p
                continue
        merged.append(p)
    return merged


class ProfileResolver:
    """Читает несколько profile-сканов один раз и разрешает окна."""

    def __init__(
        self,
        raw_path: str,
        *,
        scans: int | None = None,
        min_snr: float = 3.0,
        fwhm_bounds: tuple[float, float] = (1e-4, 0.05),
        min_sep_factor: float = 0.5,
    ):
        self.raw_path = str(raw_path)
        self.min_snr = float(min_snr)
        self.fwhm_bounds = fwhm_bounds
        self.min_sep_factor = float(min_sep_factor)
        self._profiles: list[tuple[np.ndarray, np.ndarray]] = []
        raw = _open_raw(self.raw_path)
        try:
            max_scans = None if scans is None else int(scans)
            for scan in scan_numbers(raw, max_scans=max_scans):
                mz, inten = scan_profile(raw, scan)
                if mz.size:
                    self._profiles.append((mz, inten))
        finally:
            try:
                raw.Close()
            except Exception:
                pass

    def resolve(self, lo: float, hi: float) -> dict:
        """Число разрешённых пиков по большинству сканов."""
        counts: list[int] = []
        peaks: list[dict] = []
        for mz, inten in self._profiles:
            found = profile_peaks(
                mz,
                inten,
                lo,
                hi,
                min_snr=self.min_snr,
                fwhm_bounds=self.fwhm_bounds,
                min_sep_factor=self.min_sep_factor,
            )
            counts.append(len(found))
            if found:
                peaks = found
        if not counts:
            return {"n_peaks": 0, "counts": [], "peaks": []}
        # Мода; при равенстве — минимальное число (консервативно).
        freq = Counter(counts)
        best = max(freq.values())
        n_peaks = min(k for k, v in freq.items() if v == best)
        return {"n_peaks": int(n_peaks), "counts": counts, "peaks": peaks}
