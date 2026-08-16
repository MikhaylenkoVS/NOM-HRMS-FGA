"""Unit tests for raw_bridge.py → raw_thermo_adapter integration.

Tests validate the facade layer: availability checks, error paths,
and DataFrame round-trip.
"""

import pytest

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
# average_raw_to_json — error paths (no RAW file needed)
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToJsonErrors:
    """Error paths that do not require a real .raw file."""

    def test_value_error_when_rt_invalid(self):
        """rt_min >= rt_max raises ValueError before file check."""
        from src.core.io.raw_bridge import average_raw_to_json

        with pytest.raises(ValueError, match="rt_min"):
            average_raw_to_json("nonexistent.raw", 5.0, 3.0)

    def test_raises_runtime_error_when_unavailable(self):
        """If RawFileReader is unavailable, RuntimeError is raised."""
        from src.core.io.raw_bridge import is_available, average_raw_to_json

        if not is_available():
            with pytest.raises(RuntimeError, match="not available"):
                average_raw_to_json("dummy.raw", 0.0, 1.0)
        else:
            pytest.skip("RawFileReader available — skipping error test")

    def test_file_not_found_when_available(self):
        """Valid RT + nonexistent file → FileNotFoundError."""
        from src.core.io.raw_bridge import is_available, average_raw_to_json

        if is_available():
            with pytest.raises(FileNotFoundError):
                average_raw_to_json("/nonexistent/file.raw", 0.0, 1.0)
        else:
            pytest.skip("RawFileReader not available")


# ═══════════════════════════════════════════════════════════════════════════
# average_raw_to_df — mocked
# ═══════════════════════════════════════════════════════════════════════════


class TestAverageRawToDf:
    """average_raw_to_df round-trip with mocked output."""

    def test_returns_dataframe_with_correct_columns(self, tmp_path, monkeypatch):
        """Mock the JSON → verify DataFrame columns are mass,intensity."""
        import pandas as pd
        import src.core.io.raw_bridge as rb

        json_path = tmp_path / "fake_averaged.json"
        pd.DataFrame({"mass": [100.0, 200.0], "intensity": [500.0, 300.0]}).to_json(
            json_path, orient="records"
        )

        monkeypatch.setattr(rb, "average_raw_to_json", lambda *a, **kw: str(json_path))

        df = rb.average_raw_to_df("dummy.raw", 0.0, 10.0)
        assert list(df.columns) == ["mass", "intensity"]
        assert len(df) == 2
        assert df.iloc[0]["mass"] == 100.0
        assert df.iloc[1]["intensity"] == 300.0
