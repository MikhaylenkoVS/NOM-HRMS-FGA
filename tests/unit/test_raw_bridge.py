"""Unit tests for raw_bridge.py → raw_thermo_adapter integration.

Tests validate the facade layer: availability checks, error paths,
and DataFrame round-trip.
"""

import pytest
import numpy as np
import os
import csv


# ═══════════════════════════════════════════════════════════════════════════
# is_available / availability_error
# ═══════════════════════════════════════════════════════════════════════════


class TestAvailability:
    """Availability probe always returns a bool."""

    def test_is_available_returns_bool(self):
        from src.core.io.raw_bridge import is_available
        result = is_available()
        assert isinstance(result, bool)

    def test_availability_error_consistent(self):
        from src.core.io.raw_bridge import is_available, availability_error
        if not is_available():
            err = availability_error()
            assert err is not None
            assert isinstance(err, str)
        else:
            assert availability_error() is None


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_csv — error paths (no RAW file needed)
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToCsvErrors:
    """Error paths that do not require a real .raw file."""

    def test_value_error_when_rt_invalid(self):
        """rt_min >= rt_max raises ValueError before file check."""
        from src.core.io.raw_bridge import average_raw_to_csv
        with pytest.raises(ValueError, match="rt_min"):
            average_raw_to_csv("nonexistent.raw", 5.0, 3.0)

    def test_raises_runtime_error_when_unavailable(self):
        """If RawFileReader is unavailable, RuntimeError is raised."""
        from src.core.io.raw_bridge import is_available, average_raw_to_csv
        if not is_available():
            with pytest.raises(RuntimeError, match="not available"):
                average_raw_to_csv("dummy.raw", 0.0, 1.0)
        else:
            pytest.skip("RawFileReader available — skipping error test")

    def test_file_not_found_when_available(self):
        """Valid RT + nonexistent file → FileNotFoundError."""
        from src.core.io.raw_bridge import is_available, average_raw_to_csv
        if is_available():
            with pytest.raises(FileNotFoundError):
                average_raw_to_csv("/nonexistent/file.raw", 0.0, 1.0)
        else:
            pytest.skip("RawFileReader not available")


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_df — mocked
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToDf:
    """average_raw_to_df round-trip with mocked output_csv."""

    def test_returns_dataframe_with_correct_columns(self, tmp_path, monkeypatch):
        """Mock the CSV → verify DataFrame columns are mass,intensity."""
        import src.core.io.raw_bridge as rb

        csv_path = tmp_path / "fake_averaged.csv"
        with open(csv_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["mass", "intensity"])
            w.writerow(["100.000000", "500.00"])
            w.writerow(["200.000000", "300.00"])

        monkeypatch.setattr(rb, "average_raw_to_csv", lambda *a, **kw: str(csv_path))

        df = rb.average_raw_to_df("dummy.raw", 0.0, 10.0)
        assert list(df.columns) == ["mass", "intensity"]
        assert len(df) == 2
        assert df.iloc[0]["mass"] == 100.0
        assert df.iloc[1]["intensity"] == 300.0
