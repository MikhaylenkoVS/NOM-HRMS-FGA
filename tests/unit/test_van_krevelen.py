"""
tests/unit/test_van_krevelen.py
================================
Unit tests for the Van Krevelen diagram module (src/core/van_krevelen.py).
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import matplotlib.pyplot as plt

from src.core.van_krevelen import (
    NOM_REGIONS,
    FIGURE_FIGSIZE,
    X_LIM,
    Y_LIM,
    compute_van_krevelen_data,
    create_van_krevelen_plot,
)


# ======================================================================
# Fixtures
# ======================================================================


@pytest.fixture
def sample_result_df() -> pd.DataFrame:
    """A minimal result table with a few synthetic compounds."""
    return pd.DataFrame(
        {
            "mass": [100.0524, 150.0681, 200.1049, 250.1206],
            "intensity": [1.0e6, 5.0e5, 2.0e5, 8.0e5],
            "brutto": ["C4H8O2", "C6H10O4", "C8H16O5", "C10H18O7"],
            "N_COOH": [1, 2, 0, 3],
        }
    )


@pytest.fixture
def sample_with_nan_brutto() -> pd.DataFrame:
    """Result table containing a row with 'nan' brutto (should be skipped)."""
    return pd.DataFrame(
        {
            "mass": [100.0, 150.0, 200.0],
            "intensity": [1.0, 2.0, 3.0],
            "brutto": ["CH4O", "nan", "C2H6O2"],
            "N_COOH": [0, 1, 2],
        }
    )


@pytest.fixture
def sample_zero_carbon() -> pd.DataFrame:
    """Row with a formula that has zero carbon (should be skipped/warn)."""
    return pd.DataFrame(
        {
            "mass": [100.0, 150.0],
            "intensity": [1.0, 2.0],
            "brutto": ["H2O", "C2H6O"],
            "N_COOH": [0, 1],
        }
    )


@pytest.fixture
def empty_result_df() -> pd.DataFrame:
    """Empty result table."""
    return pd.DataFrame(columns=["mass", "intensity", "brutto", "N_COOH"])


@pytest.fixture
def missing_column_df() -> pd.DataFrame:
    """DataFrame missing the required 'N_COOH' column."""
    return pd.DataFrame({"mass": [100.0], "intensity": [1.0], "brutto": ["CH4"]})


@pytest.fixture
def precomputed_data() -> pd.DataFrame:
    """DataFrame that already has h_c / o_c columns (bypass compute)."""
    return pd.DataFrame(
        {
            "h_c": [2.0, 1.5, 1.0],
            "o_c": [0.5, 0.6, 0.7],
            "n_cooh": [1, 2, 3],
            "intensity": [100.0, 200.0, 300.0],
            "mass": [100.0, 150.0, 200.0],
            "brutto": ["CH2O", "C2H3O2", "C3H4O3"],
        }
    )


# ======================================================================
# Tests: NOM_REGIONS structure
# ======================================================================


class TestNomRegions:
    def test_regions_are_nonempty(self):
        assert len(NOM_REGIONS) > 0

    def test_each_region_has_required_keys(self):
        required = {"name", "color", "vertices"}
        for region in NOM_REGIONS:
            assert required.issubset(region.keys()), f"Missing keys in {region['name']}"

    def test_each_region_has_valid_vertices(self):
        for region in NOM_REGIONS:
            verts = region["vertices"]
            assert len(verts) >= 3, f"Region '{region['name']}' has <3 vertices"
            for x, y in verts:
                assert isinstance(x, (int, float))
                assert isinstance(y, (int, float))


# ======================================================================
# Tests: compute_van_krevelen_data
# ======================================================================


class TestComputeVanKrevelenData:
    def test_basic_computation(self, sample_result_df):
        data = compute_van_krevelen_data(sample_result_df)
        assert isinstance(data, pd.DataFrame)
        assert list(data.columns) == [
            "h_c",
            "o_c",
            "n_cooh",
            "intensity",
            "mass",
            "brutto",
        ]
        assert len(data) == 4

        # C4H8O2: H/C = 2.0, O/C = 0.5
        np.testing.assert_almost_equal(data["h_c"].iloc[0], 2.0)
        np.testing.assert_almost_equal(data["o_c"].iloc[0], 0.5)

        # C6H10O4: H/C ≈ 1.6667, O/C ≈ 0.6667
        np.testing.assert_almost_equal(data["h_c"].iloc[1], 10 / 6)
        np.testing.assert_almost_equal(data["o_c"].iloc[1], 4 / 6)

        # C8H16O5: H/C = 2.0, O/C = 0.625
        np.testing.assert_almost_equal(data["h_c"].iloc[2], 2.0)
        np.testing.assert_almost_equal(data["o_c"].iloc[2], 5 / 8)

    def test_skips_nan_brutto(self, sample_with_nan_brutto):
        data = compute_van_krevelen_data(sample_with_nan_brutto)
        assert len(data) == 2  # только CH4O и C2H6O2

    def test_skips_zero_carbon(self, sample_zero_carbon):
        data = compute_van_krevelen_data(sample_zero_carbon)
        assert len(data) == 1  # только C2H6O
        assert data["brutto"].iloc[0] == "C2H6O"

    def test_raises_on_missing_column(self, missing_column_df):
        with pytest.raises(ValueError, match="missing required columns"):
            compute_van_krevelen_data(missing_column_df)

    def test_raises_on_empty_after_filter(self, empty_result_df):
        with pytest.raises(ValueError, match="No valid data"):
            compute_van_krevelen_data(empty_result_df)

    def test_raises_on_all_zero_carbon(self):
        df = pd.DataFrame(
            {
                "mass": [100.0, 150.0],
                "intensity": [1.0, 2.0],
                "brutto": ["H2O", "NH3"],
                "N_COOH": [0, 0],
            }
        )
        with pytest.raises(ValueError, match="No valid data"):
            compute_van_krevelen_data(df)


# ======================================================================
# Tests: create_van_krevelen_plot
# ======================================================================


class TestCreateVanKrevelenPlot:
    def test_returns_figure(self, sample_result_df):
        """create_van_krevelen_plot returns a matplotlib Figure."""
        fig = create_van_krevelen_plot(sample_result_df)
        assert fig is not None
        assert hasattr(fig, "savefig")
        plt.close(fig)

    def test_accepts_precomputed_data(self, precomputed_data):
        """Should work when data already has h_c/o_c columns."""
        fig = create_van_krevelen_plot(precomputed_data)
        assert fig is not None
        plt.close(fig)

    def test_figure_size_default(self, sample_result_df):
        fig = create_van_krevelen_plot(sample_result_df)
        w, h = fig.get_size_inches()
        assert (w, h) == pytest.approx(FIGURE_FIGSIZE)
        plt.close(fig)

    def test_figure_size_custom(self, sample_result_df):
        custom = (6, 5)
        fig = create_van_krevelen_plot(sample_result_df, figsize=custom)
        w, h = fig.get_size_inches()
        assert (w, h) == pytest.approx(custom)
        plt.close(fig)

    def test_axes_limits(self, sample_result_df):
        fig = create_van_krevelen_plot(sample_result_df)
        ax = fig.axes[0]
        assert ax.get_xlim() == pytest.approx(X_LIM)
        assert ax.get_ylim() == pytest.approx(Y_LIM)
        plt.close(fig)

    def test_save_png(self, sample_result_df):
        """Saving to a PNG file creates a non-empty file."""
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            fig = create_van_krevelen_plot(sample_result_df, output_path=tmp_path)
            plt.close(fig)
            assert Path(tmp_path).exists()
            assert Path(tmp_path).stat().st_size > 0
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_no_crash_on_single_point(self):
        """Single valid compound should not crash."""
        df = pd.DataFrame(
            {
                "mass": [100.0],
                "intensity": [1.0],
                "brutto": ["CH4O"],
                "N_COOH": [0],
            }
        )
        fig = create_van_krevelen_plot(df)
        assert fig is not None
        plt.close(fig)

    def test_no_crash_on_equal_intensities(self):
        """All intensities equal → should use fallback size."""
        df = pd.DataFrame(
            {
                "mass": [100.0, 150.0],
                "intensity": [1.0, 1.0],
                "brutto": ["CH4O", "C2H6O2"],
                "N_COOH": [0, 1],
            }
        )
        fig = create_van_krevelen_plot(df)
        assert fig is not None
        plt.close(fig)
