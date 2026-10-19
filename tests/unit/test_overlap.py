"""Тесты вычитания исходника из производных: модель «один к одному», только по m/z."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.core.domain.spectrum import Spectrum
from src.core.spectrum._overlap import match_mask, subtract_matching_peaks


def _spec(masses, intensities=None):
    if intensities is None:
        intensities = [1.0] * len(masses)
    return Spectrum(
        table=pd.DataFrame({"mass": list(masses), "intensity": list(intensities)})
    )


def test_exact_match_is_removed():
    src = _spec([100.0, 200.0])
    deriv = _spec([100.0, 150.0, 200.0])
    out, stats = subtract_matching_peaks(deriv, src, ppm_tol=5.0)
    assert list(out.table["mass"]) == [150.0]
    assert stats["total"] == 3
    assert stats["removed"] == 2
    assert stats["kept"] == 1
    assert stats["removed_frac"] == pytest.approx(2 / 3)
    assert stats["ppm_tol"] == 5.0
    assert stats["one_to_one"] is True
    assert stats["src_peaks"] == 2


def test_intensities_are_ignored():
    """Совпадение только по m/z: яркий исходник и слабый пик дериватизата — дубль."""
    src = _spec([300.0], [10_000.0])
    deriv = _spec([300.0], [0.001])
    out, stats = subtract_matching_peaks(deriv, src)
    assert stats["removed"] == 1
    assert len(out.table) == 0


def test_within_ppm_removed_outside_kept():
    src = _spec([500.0])
    # 3 ppm и 10 ppm от 500
    deriv = _spec([500.0 + 500.0 * 3e-6, 500.0 + 500.0 * 10e-6])
    out, stats = subtract_matching_peaks(deriv, src, ppm_tol=5.0)
    assert stats["removed"] == 1
    assert len(out.table) == 1
    assert abs(float(out.table["mass"].iloc[0]) - 500.005) < 1e-6


def test_empty_derivative():
    src = _spec([100.0])
    deriv = _spec([])
    out, stats = subtract_matching_peaks(deriv, src)
    assert stats["total"] == 0
    assert stats["removed"] == 0
    assert len(out.table) == 0


def test_empty_source_keeps_everything():
    deriv = _spec([100.0, 200.0])
    out, stats = subtract_matching_peaks(deriv, _spec([]))
    assert stats["removed"] == 0
    assert len(out.table) == 2


def test_order_is_preserved():
    src = _spec([200.0])
    deriv = _spec([300.0, 200.0, 100.0])
    out, _ = subtract_matching_peaks(deriv, src)
    assert list(out.table["mass"]) == [300.0, 100.0]


def test_negative_ppm_raises():
    with pytest.raises(ValueError, match="ppm_tol"):
        subtract_matching_peaks(_spec([100.0]), _spec([100.0]), ppm_tol=-1.0)


def test_match_mask_vectorized_edges():
    src_sorted = np.array([100.0, 400.0, 700.0])
    deriv = np.array([99.9999, 399.0, 700.0001, 1000.0])
    mask = match_mask(deriv, src_sorted, ppm_tol=5.0)
    assert list(mask) == [True, False, True, False]


def test_metadata_is_kept():
    src = _spec([100.0])
    deriv = _spec([100.0, 200.0])
    out, _ = subtract_matching_peaks(deriv, src)
    assert out.metadata is not None


def test_two_source_peaks_remove_only_one_derivative_peak():
    """Два пика исходника в окне одного пика дериватизата → вычитается один."""
    src = _spec([500.0, 500.0 + 500.0 * 2e-6])  # 0 и 2 ppm
    deriv = _spec([500.0 + 500.0 * 1e-6])  # 1 ppm от обоих
    out, stats = subtract_matching_peaks(deriv, src, ppm_tol=5.0)
    assert stats["removed"] == 1
    assert len(out.table) == 0


def test_closest_derivative_peak_is_removed():
    """Один пик исходника, два кандидата в окне → вычитается ближайший."""
    src = _spec([500.0])
    near = 500.0 + 500.0 * 1e-6  # 1 ppm
    far = 500.0 + 500.0 * 4e-6  # 4 ppm
    deriv = _spec([near, far])
    out, stats = subtract_matching_peaks(deriv, src, ppm_tol=5.0)
    assert stats["removed"] == 1
    assert list(out.table["mass"]) == [far]


def test_removed_never_exceeds_source_peaks():
    """Правило 1:1 — удалённых пиков не больше, чем пиков в исходнике."""
    src = _spec([100.0, 200.0])
    deriv = _spec([100.0, 100.0 + 100.0 * 1e-6, 200.0, 200.0 + 200.0 * 1e-6])
    _, stats = subtract_matching_peaks(deriv, src, ppm_tol=5.0)
    assert stats["removed"] <= stats["src_peaks"] == 2


def test_all_mode_matches_previous_behaviour():
    """one_to_one=False — прежнее поведение (удаляются все совпадения)."""
    src = _spec([100.0])
    deriv = _spec([100.0, 100.0 + 100.0 * 1e-6])
    out, stats = subtract_matching_peaks(deriv, src, ppm_tol=5.0, one_to_one=False)
    assert stats["removed"] == 2
    assert len(out.table) == 0
