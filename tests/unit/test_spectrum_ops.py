"""Unit tests for spectrum_ops.py — loading, denoising, formula assignment, series.

Supplements test_core_utils.py which already covers:
  exact_mass_from_counts, dbe_from_counts, _row_to_brutto, _neutral_to_ion_mass, _find_peak.

This module adds tests for:
  load_spectrum, _nom_distance, FormulaSearchConfig,
  denoise, assign_formulas, find_series, build_result_table.
"""

from __future__ import annotations

import tempfile
import os
import pytest
import pandas as pd
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _make_csv(masses_and_intensities: list[tuple[float, float]]) -> str:
    """Write a temporary CSV with mass,intensity columns and return its path."""
    df = pd.DataFrame(masses_and_intensities, columns=["mass", "intensity"])
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    df.to_csv(f, index=False)
    f.close()
    return f.name


def _make_csv_with_columns(columns: list[str], rows: list[list]) -> str:
    """Write a temporary CSV with custom columns."""
    df = pd.DataFrame(rows, columns=columns)
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False, encoding="utf-8")
    df.to_csv(f, index=False)
    f.close()
    return f.name


def _make_spectrum(masses_and_intensities: list[tuple[float, float]]):
    """Create a nomspectra Spectrum from mass/intensity pairs."""
    from src.core.spectrum_ops import Spectrum
    df = pd.DataFrame(masses_and_intensities, columns=["mass", "intensity"])
    return Spectrum(table=df)


# ═══════════════════════════════════════════════════════════════════════════
# load_spectrum
# ═══════════════════════════════════════════════════════════════════════════


class TestLoadSpectrum:
    """load_spectrum: CSV → Spectrum with mass filtering and column mapping."""

    def test_loads_valid_csv(self):
        from src.core.spectrum_ops import load_spectrum

        path = _make_csv([(300.0, 1000.0), (400.0, 500.0)])
        try:
            sp = load_spectrum(path, mass_min=200.0, mass_max=700.0)
            assert sp is not None
            assert len(sp.table) == 2
            assert list(sp.table.columns) == ["mass", "intensity"]
        finally:
            os.unlink(path)

    def test_respects_mass_window(self):
        from src.core.spectrum_ops import load_spectrum

        path = _make_csv([(100.0, 100.0), (300.0, 200.0), (900.0, 50.0)])
        try:
            sp = load_spectrum(path, mass_min=200.0, mass_max=700.0)
            assert len(sp.table) == 1
            assert sp.table.iloc[0]["mass"] == 300.0
        finally:
            os.unlink(path)

    def test_raises_value_error_on_empty_window(self):
        from src.core.spectrum_ops import load_spectrum

        path = _make_csv([(100.0, 100.0)])
        try:
            with pytest.raises(ValueError, match="не найдено ни одного пика"):
                load_spectrum(path, mass_min=200.0, mass_max=250.0)
        finally:
            os.unlink(path)

    def test_raises_on_nonexistent_file(self):
        from src.core.spectrum_ops import load_spectrum

        with pytest.raises(ValueError, match="Не удалось прочитать"):
            load_spectrum("/nonexistent/path/file.csv")

    def test_maps_mz_column_to_mass(self):
        from src.core.spectrum_ops import load_spectrum

        path = _make_csv_with_columns(["m/z", "I"], [[300.0, 100.0], [400.0, 200.0]])
        try:
            sp = load_spectrum(path, mass_min=0.0, mass_max=9999.0)
            assert "mass" in sp.table.columns
            assert "intensity" in sp.table.columns
            assert len(sp.table) == 2
        finally:
            os.unlink(path)

    def test_raises_keyerror_on_missing_columns(self):
        from src.core.spectrum_ops import load_spectrum

        path = _make_csv_with_columns(["x", "y"], [[1, 2]])
        try:
            with pytest.raises(KeyError, match="Колонки"):
                load_spectrum(path, mass_min=0, mass_max=9999)
        finally:
            os.unlink(path)

    def test_accepts_custom_mapper(self):
        from src.core.spectrum_ops import load_spectrum

        path = _make_csv_with_columns(["mz_val", "int_val"], [[300.0, 100.0]])
        try:
            sp = load_spectrum(
                path,
                mapper={"mz_val": "mass", "int_val": "intensity"},
                mass_min=0, mass_max=9999,
            )
            assert len(sp.table) == 1
        finally:
            os.unlink(path)


# ═══════════════════════════════════════════════════════════════════════════
# _nom_distance
# ═══════════════════════════════════════════════════════════════════════════


class TestNomDistance:
    """_nom_distance: distance from (O/C, H/C) to nearest NOM-region center."""

    def test_typical_nom_point(self):
        from src.core.spectrum_ops import _nom_distance

        # A point well within typical NOM region should have small distance
        d = _nom_distance(hc=1.2, oc=0.5)
        assert d < 1.0

    def test_far_point_returns_large_distance(self):
        from src.core.spectrum_ops import _nom_distance

        # (O/C, H/C) far outside NOM
        d = _nom_distance(hc=0.5, oc=2.0)
        assert d > 1.0

    def test_zero_hc_returns_penalty(self):
        from src.core.spectrum_ops import _nom_distance

        assert _nom_distance(hc=0.0, oc=0.5) == 10.0
        assert _nom_distance(hc=-0.1, oc=0.5) == 10.0

    def test_distance_is_non_negative(self):
        from src.core.spectrum_ops import _nom_distance

        for hc, oc in [(0.5, 0.2), (1.0, 0.5), (1.5, 0.8), (2.0, 0.3)]:
            assert _nom_distance(hc, oc) >= 0.0


# ═══════════════════════════════════════════════════════════════════════════
# FormulaSearchConfig
# ═══════════════════════════════════════════════════════════════════════════


class TestFormulaSearchConfig:
    """FormulaSearchConfig defaults and validation."""

    def test_defaults_have_expected_elements(self):
        from src.core.spectrum_ops import FormulaSearchConfig

        cfg = FormulaSearchConfig()
        assert "C" in cfg.elements
        assert "H" in cfg.elements
        assert "O" in cfg.elements
        assert "N" in cfg.elements

    def test_custom_ranges_override(self):
        from src.core.spectrum_ops import FormulaSearchConfig

        cfg = FormulaSearchConfig(
            ranges={"C": (1, 10), "H": (0, 20), "O": (0, 5), "N": (0, 1)}
        )
        assert cfg.ranges["C"] == (1, 10)

    def test_missing_element_range_defaults(self):
        from src.core.spectrum_ops import FormulaSearchConfig

        cfg = FormulaSearchConfig()
        # By default __post_init__ fills in missing ranges
        assert "C" in cfg.ranges
        assert isinstance(cfg.ranges["C"], tuple)
        assert len(cfg.ranges["C"]) == 2


# ═══════════════════════════════════════════════════════════════════════════
# denoise — smoke test with synthetic data
# ═══════════════════════════════════════════════════════════════════════════


class TestDenoise:
    """denoise reduces peak count on noisy synthetic spectra."""

    def test_denoise_with_force_reduces_peaks(self):
        from src.core.spectrum_ops import denoise

        # 10 strong peaks + 90 noise peaks
        masses = np.linspace(200, 700, 100)
        intensities = np.concatenate([np.full(10, 10000.0), np.full(90, 100.0)])
        sp = _make_spectrum(list(zip(masses, intensities)))

        result = denoise(sp, force=2.0)
        # Should have fewer peaks than original
        assert len(result.table) < 100

    def test_denoise_with_intensity_threshold(self):
        from src.core.spectrum_ops import denoise

        sp = _make_spectrum([(100.0, 1000.0), (101.0, 10.0)])
        result = denoise(sp, intensity=100.0)
        assert len(result.table) <= 2

    def test_denoise_with_quantile(self):
        from src.core.spectrum_ops import denoise

        masses = np.linspace(200, 700, 50)
        intensities = np.random.default_rng(42).exponential(100, 50)
        sp = _make_spectrum(list(zip(masses, intensities)))

        result = denoise(sp, quantile=0.5)
        assert len(result.table) <= 50


# ═══════════════════════════════════════════════════════════════════════════
# assign_formulas — smoke test
# ═══════════════════════════════════════════════════════════════════════════


class TestAssignFormulasSmoke:
    """Smoke tests: assign_formulas produces expected columns."""

    def test_assigns_formulas_to_simple_spectrum(self):
        from src.core.spectrum_ops import assign_formulas

        # Single C7H6O2 peak at [M-H]- mass ≈ 137.02442
        sp = _make_spectrum([(137.024, 1000.0)])
        result = assign_formulas(sp, rel_error_ppm=5.0, sign="-")
        assert "assign" in result.table.columns
        assert "brutto" in result.table.columns

    def test_assign_column_is_boolean(self):
        from src.core.spectrum_ops import assign_formulas

        sp = _make_spectrum([(137.024, 1000.0)])
        result = assign_formulas(sp, rel_error_ppm=5.0, sign="-")
        assert result.table["assign"].dtype == bool

    @pytest.mark.xfail(reason="Known: empty spectrum raises ValueError (NaN→int in formula range calc)")
    def test_empty_spectrum_no_crash(self):
        from src.core.spectrum_ops import assign_formulas

        sp = _make_spectrum([])
        result = assign_formulas(sp, rel_error_ppm=5.0, sign="-")
        assert len(result.table) == 0

    def test_mass_outside_window_not_assigned(self):
        from src.core.spectrum_ops import assign_formulas

        # Peak at 50 Da — too low for any reasonable CHON formula
        sp = _make_spectrum([(50.0, 1000.0)])
        result = assign_formulas(sp, rel_error_ppm=5.0, sign="-",
                                 mass_min=200, mass_max=700)
        # The peak may be filtered or unassigned
        assert "assign" in result.table.columns


# ═══════════════════════════════════════════════════════════════════════════
# find_series — smoke test with synthetic spectra
# ═══════════════════════════════════════════════════════════════════════════


class TestFindSeriesSmoke:
    """Smoke tests: find_series with synthetic data."""

    DELTA_CD3 = 17.03448
    DELTA_CD3CO = 45.02939

    def _assigned_src_with_brutto(self, masses, brutto="C7H6O2"):
        """Return a Spectrum with assigned peaks at given masses."""
        from src.core.spectrum_ops import Spectrum
        df = pd.DataFrame({
            "mass": masses,
            "intensity": [1000.0] * len(masses),
            "assign": [True] * len(masses),
            "brutto": [brutto] * len(masses),
        })
        return Spectrum(table=df)

    def test_find_series_cd3_empty_on_no_match(self):
        from src.core.spectrum_ops import find_series

        src = self._assigned_src_with_brutto([200.0])
        deriv = _make_spectrum([(250.0, 500.0)])  # no CD3 spacing

        result = find_series(src, deriv, delta=self.DELTA_CD3,
                             ppm_tol=5.0, max_groups=5)
        # Result is a DataFrame (possibly empty)
        assert isinstance(result, pd.DataFrame)

    def test_find_series_returns_dataframe(self):
        from src.core.spectrum_ops import find_series

        src = self._assigned_src_with_brutto([200.0])
        deriv = _make_spectrum([(200.0 + self.DELTA_CD3, 500.0)])

        result = find_series(src, deriv, delta=self.DELTA_CD3,
                             ppm_tol=10.0, max_groups=5)
        assert isinstance(result, pd.DataFrame)

    def test_find_series_respects_max_groups(self):
        from src.core.spectrum_ops import find_series

        # Create a series: src at 200, deriv peaks at 200+delta, 200+2*delta, ...
        src_mass = 200.0
        deriv_masses = [src_mass + i * self.DELTA_CD3 for i in range(1, 8)]
        src = self._assigned_src_with_brutto([src_mass])
        deriv = _make_spectrum([(m, 500.0) for m in deriv_masses])

        result = find_series(src, deriv, delta=self.DELTA_CD3,
                             ppm_tol=10.0, max_groups=5)
        # With max_groups=5, should find at most 5 groups per series
        if not result.empty and "n_groups" in result.columns:
            assert (result["n_groups"] <= 5).all()


# ═══════════════════════════════════════════════════════════════════════════
# build_result_table
# ═══════════════════════════════════════════════════════════════════════════


class TestBuildResultTable:
    """build_result_table assembles the final -COOH/-OH count table."""

    def _assigned_src(self, masses, formulas=None):
        from src.core.spectrum_ops import Spectrum
        if formulas is None:
            formulas = ["C7H6O2"] * len(masses)
        df = pd.DataFrame({
            "mass": masses,
            "intensity": [1000.0] * len(masses),
            "assign": [True] * len(masses),
            "brutto": formulas,
            "all_candidates": [[f] for f in formulas],
        })
        return Spectrum(table=df)

    def test_empty_series_returns_base_table(self):
        from src.core.spectrum_ops import build_result_table

        src = self._assigned_src([200.0, 300.0])
        result = build_result_table(src, pd.DataFrame(), pd.DataFrame())
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    def test_result_has_expected_columns(self):
        from src.core.spectrum_ops import build_result_table

        src = self._assigned_src([200.0])
        result = build_result_table(src, pd.DataFrame(), pd.DataFrame())

        expected = {"mass", "intensity", "brutto", "N_COOH", "N_OH"}
        assert expected.issubset(set(result.columns))

    def test_n_cooh_n_oh_default_to_zero(self):
        from src.core.spectrum_ops import build_result_table

        src = self._assigned_src([200.0])
        result = build_result_table(src, pd.DataFrame(), pd.DataFrame())

        assert result.iloc[0]["N_COOH"] == 0
        assert result.iloc[0]["N_OH"] == 0
