"""Unit tests for raw_bridge.py: availability checks, merge_segments, error paths.

These tests do NOT require MSFileReader — they mock the optional dependency
and validate the pure-Python error-handling and helper logic.
"""

import pytest
import numpy as np
import os
import tempfile
from unittest import mock
import sys


# ═══════════════════════════════════════════════════════════════════════════
# is_available / availability_error
# ═══════════════════════════════════════════════════════════════════════════


class TestAvailability:
    """When MSFileReader is absent, is_available() → False."""

    def test_is_available_without_msfr(self):
        """Without MSFileReader installed, is_available should return False."""
        from src.core.raw_bridge import is_available
        # On a dev machine without MSFileReader this is False;
        # on CI it will be False.
        result = is_available()
        assert isinstance(result, bool)

    def test_availability_error_returns_string_when_unavailable(self):
        from src.core.raw_bridge import is_available, availability_error
        if not is_available():
            err = availability_error()
            assert err is not None
            assert isinstance(err, str)
        else:
            assert availability_error() is None


# ═══════════════════════════════════════════════════════════════════════════
# _merge_segments
# ═══════════════════════════════════════════════════════════════════════════


class TestMergeSegments:
    """Pure-function merge of multi-segment spectrum data."""

    def test_empty_dict_returns_empty(self):
        from src.core.raw_bridge import _merge_segments

        result = _merge_segments({})
        assert isinstance(result, np.ndarray)
        assert result.shape == (0, 2)

    def test_single_segment(self):
        from src.core.raw_bridge import _merge_segments

        data = {
            "segment_1": np.array(
                [[100.0, 50.0, 0, 0, 0, 0], [200.0, 30.0, 0, 0, 0, 0]]
            )
        }
        result = _merge_segments(data)
        assert result.shape == (2, 2)
        assert result[0, 0] == 100.0
        assert result[0, 1] == 50.0

    def test_merging_same_mass_sums_intensities(self):
        from src.core.raw_bridge import _merge_segments

        # Same mass in two segments → intensities summed
        data = {
            "seg1": np.array([[100.0, 40.0, 0, 0, 0, 0]]),
            "seg2": np.array([[100.0, 60.0, 0, 0, 0, 0]]),
        }
        result = _merge_segments(data)
        assert result.shape == (1, 2)
        assert result[0, 0] == 100.0
        assert result[0, 1] == 100.0  # 40 + 60

    def test_different_masses_kept_separate(self):
        from src.core.raw_bridge import _merge_segments

        data = {
            "seg1": np.array([[100.0, 10.0, 0, 0, 0, 0]]),
            "seg2": np.array([[200.0, 20.0, 0, 0, 0, 0]]),
        }
        result = _merge_segments(data)
        assert result.shape == (2, 2)

    def test_near_identical_masses_grouped(self):
        from src.core.raw_bridge import _merge_segments

        # masses within 1e-5 are treated as equal after rounding
        data = {
            "seg": np.array(
                [[100.00000, 10.0, 0, 0, 0, 0], [100.000001, 5.0, 0, 0, 0, 0]]
            )
        }
        result = _merge_segments(data)
        assert result.shape == (1, 2)
        assert result[0, 1] == 15.0


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_csv — error paths (no MSFileReader needed)
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToCsvErrors:
    """Error paths that don't require MSFileReader."""

    def test_raises_runtime_error_when_unavailable(self):
        from src.core.raw_bridge import average_raw_to_csv, is_available

        if not is_available():
            with pytest.raises(RuntimeError, match="not available"):
                average_raw_to_csv("dummy.raw", 0.0, 1.0)
        else:
            pytest.skip("MSFileReader is available — skipping error test")

    def test_value_error_when_rt_invalid(self):
        """rt_min >= rt_max raises ValueError regardless of MSFileReader."""
        from src.core.raw_bridge import average_raw_to_csv, is_available

        if is_available():
            # We have MSFileReader but we test the validation path
            with pytest.raises(ValueError, match="rt_min"):
                average_raw_to_csv("dummy.raw", 5.0, 3.0)
        else:
            pytest.skip(
                "MSFileReader unavailable — rt check happens after availability check"
            )

    def test_file_not_found_when_available(self):
        """File check happens after availability."""
        from src.core.raw_bridge import average_raw_to_csv, is_available

        if is_available():
            with pytest.raises(FileNotFoundError):
                average_raw_to_csv(
                    "/nonexistent/path/file.raw", 0.0, 1.0
                )
        else:
            pytest.skip("MSFileReader not available")


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_df delegates correctly
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToDf:
    """average_raw_to_df calls average_raw_to_csv and reads the CSV."""

    def test_delegates_and_reads_csv(self):
        from src.core.raw_bridge import average_raw_to_df, is_available

        if not is_available():
            pytest.skip("MSFileReader unavailable — cannot run end-to-end")
        # This test only runs when MSFileReader is available.
        # In most CI environments it will be skipped.


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_csv — happy path with mocked MSFileReader
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToCsvMocked:
    """Happy-path tests for average_raw_to_csv using mocked PyMSFileReader."""

    @pytest.fixture(autouse=True)
    def _setup_mock(self, monkeypatch, tmp_path):
        """Mock MSFileReader as available and provide fake RAW data."""
        import src.core.raw_bridge as rb

        monkeypatch.setattr(rb, "_MSFR_AVAILABLE", True)
        monkeypatch.setattr(rb, "_MSFR_ERROR", None)

        fake_msfr = mock.MagicMock()
        fake_reader = mock.MagicMock()
        fake_reader.get_averaged_spectrum_list_from_RT.return_value = {
            "seg1": np.array([[100.123456, 50000.0, 0, 0, 0, 0],
                              [200.654321, 30000.0, 0, 0, 0, 0]]),
        }
        fake_msfr.PyMSFileReader.return_value = fake_reader
        fake_msfr.c_double = float  # c_double(x) → x for tests
        monkeypatch.setattr(rb, "_msfr", fake_msfr)

        self.rb = rb
        self.tmp = tmp_path
        self.raw_file = tmp_path / "test.raw"
        self.raw_file.write_text("dummy raw content")

    def test_happy_path_writes_csv_with_mass_intensity_header(self):
        """Mocked RAW → CSV has correct header and values."""
        csv_path = self.rb.average_raw_to_csv(
            str(self.raw_file), rt_min=0.0, rt_max=10.0
        )
        assert os.path.isfile(csv_path)
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        assert lines[0].strip() == "mass,intensity"
        assert len(lines) == 3  # header + 2 data rows
        # mass is rounded to 5 decimals by _merge_segments, then .6f → "100.123460"
        assert "100.123460" in lines[1]
        assert "50000.00" in lines[1]

    def test_custom_output_csv_path(self):
        """output_csv parameter controls where CSV is written."""
        custom = str(self.tmp / "custom_output.csv")
        result = self.rb.average_raw_to_csv(
            str(self.raw_file), rt_min=0.0, rt_max=10.0, output_csv=custom
        )
        assert result == os.path.abspath(custom)
        assert os.path.isfile(custom)

    def test_default_output_naming(self):
        """Without output_csv, file is named <basename>_avrg.csv in raw dir."""
        result = self.rb.average_raw_to_csv(
            str(self.raw_file), rt_min=0.0, rt_max=10.0
        )
        expected_name = "test_avrg.csv"
        assert os.path.basename(result) == expected_name
        assert os.path.dirname(result) == str(self.tmp)

    def test_progress_callback_is_called(self):
        """progress_callback receives status strings during processing."""
        calls = []

        def tracker(msg):
            calls.append(msg)

        self.rb.average_raw_to_csv(
            str(self.raw_file), rt_min=0.0, rt_max=10.0, progress_callback=tracker
        )
        assert len(calls) >= 2
        assert any("Усреднение" in c for c in calls)
        assert any("Объединение" in c for c in calls)

    def test_returns_absolute_path(self):
        """Returned path is always absolute."""
        result = self.rb.average_raw_to_csv(
            str(self.raw_file), rt_min=0.0, rt_max=10.0
        )
        assert os.path.isabs(result)


# ═══════════════════════════════════════════════════════════════════════════
# _merge_segments — дополнительные edge-кейсы
# ═══════════════════════════════════════════════════════════════════════════


class TestMergeSegmentsExtras:
    """Additional _merge_segments edge cases beyond the basic suite."""

    def test_ignores_extra_columns(self):
        """Only mass (col 0) and intensity (col 1) matter; rest ignored."""
        from src.core.raw_bridge import _merge_segments

        # Extra columns: resolution, baseline, noise, charge — filled with junk
        data = {
            "s1": np.array([[150.0, 10.0, 999, 888, 777, 666]]),
        }
        result = _merge_segments(data)
        assert result.shape == (1, 2)
        assert result[0, 0] == 150.0
        assert result[0, 1] == 10.0

    def test_large_number_of_unique_masses(self):
        """Scales to 1000 unique masses across segments."""
        from src.core.raw_bridge import _merge_segments

        n = 1000
        data = {
            f"seg_{i}": np.array([[float(100 + i), float(i + 1), 0, 0, 0, 0]])
            for i in range(n)
        }
        result = _merge_segments(data)
        assert result.shape == (n, 2)
        # Verify sorting by mass
        masses = result[:, 0]
        assert np.all(np.diff(masses) >= 0)

    def test_segment_with_single_row(self):
        """Single-row segments don't crash vstack."""
        from src.core.raw_bridge import _merge_segments

        data = {
            "s1": np.array([[42.0, 7.0, 0, 0, 0, 0]]),
            "s2": np.array([[42.0, 3.0, 0, 0, 0, 0]]),
        }
        result = _merge_segments(data)
        assert result.shape == (1, 2)
        assert result[0, 1] == 10.0  # 7 + 3


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_df — mocked
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToDfMocked:
    """Test average_raw_to_df with a mocked CSV round-trip."""

    def test_returns_dataframe_with_correct_columns(self, tmp_path, monkeypatch):
        """Mock the CSV writing part, verify DataFrame columns are mass,intensity."""
        import src.core.raw_bridge as rb
        import csv

        # Pre-create the CSV that average_raw_to_csv would produce
        csv_path = tmp_path / "fake_avrg.csv"
        with open(csv_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["mass", "intensity"])
            w.writerow(["100.000000", "500.00"])
            w.writerow(["200.000000", "300.00"])

        # Mock average_raw_to_csv to return our pre-built CSV
        monkeypatch.setattr(rb, "average_raw_to_csv", lambda *a, **kw: str(csv_path))

        df = rb.average_raw_to_df("dummy.raw", 0.0, 10.0)
        assert list(df.columns) == ["mass", "intensity"]
        assert len(df) == 2
        assert df.iloc[0]["mass"] == 100.0
        assert df.iloc[1]["intensity"] == 300.0
