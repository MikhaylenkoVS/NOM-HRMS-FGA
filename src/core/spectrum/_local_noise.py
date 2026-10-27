"""Локальный шум по центроидному спектру (MAD в окне вокруг массы)."""

from __future__ import annotations

import numpy as np


def local_noise_mad_sorted(
    mass: np.ndarray,
    intensity: np.ndarray,
    target: float,
    *,
    half_window: float = 0.2,
    exclude: float = 0.02,
    min_points: int = 10,
) -> float:
    """MAD интенсивностей в ±``half_window`` Да, без ±``exclude`` Да.

    ``mass`` и ``intensity`` должны быть отсортированы по массе.
    Возвращает 0.0, если локальных точек недостаточно.
    """
    lo = int(np.searchsorted(mass, target - half_window, side="left"))
    hi = int(np.searchsorted(mass, target + half_window, side="right"))
    plo = int(np.searchsorted(mass, target - exclude, side="left"))
    phi = int(np.searchsorted(mass, target + exclude, side="right"))
    noise = np.concatenate([intensity[lo:plo], intensity[phi:hi]])
    if noise.size < min_points:
        return 0.0
    med = float(np.median(noise))
    mad = float(np.median(np.abs(noise - med))) * 1.4826
    if mad > 0:
        return mad
    return float(np.std(noise))


def local_noise_mad(
    mass: np.ndarray,
    intensity: np.ndarray,
    target: float,
    **kwargs,
) -> float:
    """То же, но с сортировкой входных массивов."""
    mass = np.asarray(mass, dtype=float)
    intensity = np.asarray(intensity, dtype=float)
    order = np.argsort(mass)
    return local_noise_mad_sorted(
        mass[order], intensity[order], float(target), **kwargs
    )
