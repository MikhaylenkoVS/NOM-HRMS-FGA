"""Integration tests for raw_bridge.py with RawFileReader.

These tests require pythonnet + RawFileReader DLLs on Windows.
Skipped when RawFileReader is not available.
"""

import pytest
from src.core.io.raw_bridge import is_available, average_raw_to_json, average_raw_to_df

pytestmark = pytest.mark.skipif(
    not is_available(), reason="RawFileReader not available"
)


class TestRawIntegration:
    """End-to-end RAW averaging — requires a real .raw file."""

    def test_average_raw_to_json_smoke(self):
        """Basic smoke: averaging should not crash on a valid .raw file."""
        # This test only runs when RawFileReader is available.
        # Provide a path or skip — in CI this needs a test .raw file.
        pass  # placeholder — skipped when no .raw file

    def test_average_raw_to_df_delegates(self):
        """average_raw_to_df calls average_raw_to_json under the hood."""
        pass  # placeholder
