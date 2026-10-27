import numpy as np

from src.core.spectrum._local_noise import local_noise_mad_sorted


def test_local_noise_mad_sorted_positive_and_excludes_peak():
    rng = np.random.default_rng(1)
    mass = np.linspace(99.5, 100.5, 1000)
    intensity = rng.normal(100.0, 5.0, mass.size)
    target = 100.0
    # peak itself + narrow exclusion region
    intensity[np.abs(mass - target) <= 0.02] = 1e6
    noise = local_noise_mad_sorted(mass, intensity, target)
    assert 0.1 < noise < 20.0


def test_local_noise_mad_sorted_requires_enough_points():
    mass = np.array([100.0, 100.001, 100.002])
    intensity = np.array([1.0, 2.0, 3.0])
    assert local_noise_mad_sorted(mass, intensity, 100.0) == 0.0
