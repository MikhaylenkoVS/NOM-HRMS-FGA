"""Smoke tests for pipeline.py: imports, dataclasses, helper functions."""

import pytest
import pandas as pd
import numpy as np
import tempfile
from pathlib import Path


class TestPipelineImports:
    """Verify critical pipeline symbols can be imported."""

    def test_import_run_pipeline(self):
        from src.core.pipeline import run_pipeline
        assert callable(run_pipeline)

    def test_import_dataclasses(self):
        from src.core.pipeline import (
            PipelineStats,
            PipelineRunResult,
            TestSetResult,
            SeriesStats,
        )

    def test_import_helpers(self):
        from src.core.pipeline import _ppm_error, _normalize_brutto, _match_row_by_mass


class TestPipelineStats:
    """Default values of PipelineStats."""

    def test_defaults(self):
        from src.core.pipeline import PipelineStats

        s = PipelineStats()
        assert s.src_loaded == 0
        assert s.src_denoised == 0
        assert s.assigned_count == 0
        assert s.assigned_ratio == 0.0
        assert s.result_rows == 0
        assert s.result_n_cooh_gt0 == 0
        assert s.result_n_oh_gt0 == 0

    def test_series_stats_defaults(self):
        from src.core.pipeline import SeriesStats

        s = SeriesStats()
        assert s.rows == 0
        assert s.max_groups == 0
        assert s.missing_total == 0


class TestPipelineRunResult:
    """PipelineRunResult dataclass behaviour."""

    def test_construction(self):
        from src.core.pipeline import PipelineRunResult, PipelineStats

        stats = PipelineStats()
        result = PipelineRunResult(table=pd.DataFrame(), stats=stats, messages=[])
        assert result.table is not None
        assert isinstance(result.stats, PipelineStats)
        assert result.messages == []

    def test_default_messages(self):
        from src.core.pipeline import PipelineRunResult, PipelineStats

        result = PipelineRunResult(table=pd.DataFrame(), stats=PipelineStats())
        assert result.messages == []


class TestTestSetResult:
    """TestSetResult dataclass and properties."""

    def test_construction(self):
        from src.core.pipeline import TestSetResult

        r = TestSetResult(set_name="set_01")
        assert r.set_name == "set_01"
        assert r.total_signals == 0
        assert r.denoised_kept == 0
        assert r.assigned_ok == 0
        assert r.dmet_found == 0
        assert r.dmet_matched == 0
        assert r.dmet_wrong == 0
        assert r.dacet_found == 0
        assert r.dacet_matched == 0
        assert r.dacet_wrong == 0
        assert r.errors == []

    def test_denoise_recall_property(self):
        from src.core.pipeline import TestSetResult

        r = TestSetResult(set_name="set_01", total_signals=100, denoised_kept=95)
        assert abs(r.denoise_recall - 0.95) < 1e-9

    def test_denoise_recall_zero_total(self):
        from src.core.pipeline import TestSetResult

        r = TestSetResult(set_name="set_01")
        assert r.denoise_recall == 0.0

    def test_assign_recall_property(self):
        from src.core.pipeline import TestSetResult

        r = TestSetResult(set_name="set_01", total_signals=100, assigned_ok=80)
        assert abs(r.assign_recall - 0.80) < 1e-9

    def test_assign_recall_zero_total(self):
        from src.core.pipeline import TestSetResult

        r = TestSetResult(set_name="set_01")
        assert r.assign_recall == 0.0


class TestNormalizeBrutto:
    """Supplement normalize_brutto tests (import from pipeline)."""

    def test_nan(self):
        from src.core.pipeline import _normalize_brutto
        assert _normalize_brutto(pd.NA) is None

    def test_canonical(self):
        from src.core.pipeline import _normalize_brutto
        assert _normalize_brutto("C7H6O2") == "C7H6O2"

    def test_reorder(self):
        from src.core.pipeline import _normalize_brutto
        assert _normalize_brutto("O2C7H6") == "C7H6O2"


class TestPpmError:
    """_ppm_error from pipeline (cross-check)."""

    def test_zero_theoretical(self):
        from src.core.pipeline import _ppm_error
        assert _ppm_error(100.0, 0.0) == float("inf")

    def test_identical(self):
        from src.core.pipeline import _ppm_error
        assert _ppm_error(200.0, 200.0) == 0.0

    def test_1ppm_at_1000(self):
        from src.core.pipeline import _ppm_error
        result = _ppm_error(1000.001, 1000.0)
        assert abs(result - 1.0) < 0.01


class TestMatchRowByMass:
    """Tests for _match_row_by_mass helper."""

    @pytest.fixture
    def sample_table(self):
        """Small table with mass and assign columns."""
        return pd.DataFrame({
            "mass": [100.0000, 100.0010, 200.0000, 300.0000],
            "intensity": [1e6, 5e5, 2e5, 1e5],
            "assign": [True, False, True, True],
            "formula": ["C5H8O2", "C5H8O2_alt", "C10H16", "C15H24"],
        })

    def test_exact_match(self, sample_table):
        """Exact mass → closest row returned."""
        from src.core.pipeline import _match_row_by_mass
        match = _match_row_by_mass(sample_table, mass_obs=100.0000, ppm_tol=10.0)
        assert match is not None
        assert match["mass"] == 100.0000

    def test_match_within_ppm(self, sample_table):
        """Mass within tolerance → closest row returned."""
        from src.core.pipeline import _match_row_by_mass
        match = _match_row_by_mass(sample_table, mass_obs=100.0005, ppm_tol=10.0)
        assert match is not None
        assert match["mass"] == 100.0000  # 100.0000 closer than 100.0010

    def test_no_match_outside_ppm(self, sample_table):
        """Mass outside tolerance → None."""
        from src.core.pipeline import _match_row_by_mass
        match = _match_row_by_mass(sample_table, mass_obs=500.0, ppm_tol=1.0)
        assert match is None

    def test_empty_table_returns_none(self):
        """Empty DataFrame → None."""
        from src.core.pipeline import _match_row_by_mass
        match = _match_row_by_mass(pd.DataFrame(), mass_obs=100.0, ppm_tol=10.0)
        assert match is None

    def test_none_table_returns_none(self):
        """None table → None."""
        from src.core.pipeline import _match_row_by_mass
        match = _match_row_by_mass(None, mass_obs=100.0, ppm_tol=10.0)
        assert match is None

    def test_missing_mass_column_returns_none(self):
        """Table without the expected mass column → None."""
        from src.core.pipeline import _match_row_by_mass
        df = pd.DataFrame({"mz": [100.0]})
        match = _match_row_by_mass(df, mass_obs=100.0, ppm_tol=10.0, mass_col="mass")
        assert match is None

    def test_require_assigned_filters_unassigned(self, sample_table):
        """require_assigned=True skips rows with assign=False."""
        from src.core.pipeline import _match_row_by_mass
        # mass 100.0010 has assign=False and should be skipped,
        # so the best match becomes 100.0000 (assign=True)
        match = _match_row_by_mass(
            sample_table, mass_obs=100.0010, ppm_tol=10.0, require_assigned=True
        )
        assert match is not None
        assert match["mass"] == 100.0000

    def test_require_assigned_no_assigned_rows(self, sample_table):
        """require_assigned=True + no assign=True rows → None."""
        from src.core.pipeline import _match_row_by_mass
        df = sample_table.copy()
        df["assign"] = False
        match = _match_row_by_mass(
            df, mass_obs=100.0000, ppm_tol=10.0, require_assigned=True
        )
        assert match is None

    def test_require_assigned_missing_assign_column(self, sample_table):
        """require_assigned=True + no 'assign' column → None."""
        from src.core.pipeline import _match_row_by_mass
        df = sample_table.drop(columns=["assign"])
        match = _match_row_by_mass(
            df, mass_obs=100.0000, ppm_tol=10.0, require_assigned=True
        )
        assert match is None

    def test_closest_match_when_multiple_in_range(self, sample_table):
        """Multiple masses within tolerance → closest ppm wins."""
        from src.core.pipeline import _match_row_by_mass
        match = _match_row_by_mass(sample_table, mass_obs=100.0008, ppm_tol=50.0)
        assert match is not None
        # 100.0010 is 0.0002 away; 100.0000 is 0.0008 away → 100.0010 wins
        assert match["mass"] == 100.0010
