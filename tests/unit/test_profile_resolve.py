"""Тесты profile-разрешения наложений."""

import numpy as np

from src.core.spectrum._profile_resolve import profile_peaks


def _two_peaks() -> tuple[np.ndarray, np.ndarray]:
    mz = np.linspace(100.0, 100.1, 2001)
    g1 = 1000.0 * np.exp(-0.5 * ((mz - 100.02) / 0.002) ** 2)
    g2 = 900.0 * np.exp(-0.5 * ((mz - 100.06) / 0.002) ** 2)
    rng = np.random.default_rng(0)
    noise = rng.normal(0.0, 2.0, mz.size)
    return mz, g1 + g2 + noise


def test_profile_resolves_two_peaks():
    mz, inten = _two_peaks()
    peaks = profile_peaks(mz, inten, 100.01, 100.07)
    assert len(peaks) == 2
    assert peaks[0]["mz"] < peaks[1]["mz"]


def test_profile_returns_one_for_single_peak():
    mz, inten = _two_peaks()
    peaks = profile_peaks(mz, inten, 100.015, 100.025)
    assert len(peaks) == 1


def test_profile_returns_empty_outside_signal():
    mz, inten = _two_peaks()
    peaks = profile_peaks(mz, inten, 100.08, 100.09)
    assert peaks == []
