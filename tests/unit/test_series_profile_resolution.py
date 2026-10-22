"""Интеграция profile-разрешения в find_series (с подменой RAW)."""

import pandas as pd
import pytest

from src.core.domain.spectrum import Spectrum
from src.core.spectrum._series import find_series

DELTA = 17.03448


class _FakeResolver:
    def __init__(self, raw_path, scans=None):
        self.raw_path = raw_path
        self.scans = scans

    def resolve(self, lo, hi):
        return {"n_peaks": 2, "counts": [2, 2, 2], "peaks": []}


def test_profile_resolution_removes_source_penalty(monkeypatch):
    monkeypatch.setattr(
        "src.core.spectrum._profile_resolve.ProfileResolver", _FakeResolver
    )
    src = Spectrum(
        table=pd.DataFrame(
            {
                "mass": [100.0, 100.0 + DELTA],
                "brutto": ["C7H6O2", "C7H6O2"],
                "assign": [True, False],
            }
        )
    )
    deriv = Spectrum(
        table=pd.DataFrame(
            {
                "mass": [100.0 + DELTA],
                "intensity": [1000.0],
            }
        )
    )
    result = find_series(
        src,
        deriv,
        DELTA,
        max_groups=3,
        max_gaps=0,
        raw_path="dummy.raw",
    )
    assert not result.empty
    row = result.iloc[0]
    detail = row["step_details"][0]
    assert detail.get("profile_resolved") is True
    assert "source_overlap" not in detail["penalties"]
    assert detail["status"] == "reliable"
    assert row["confirmed_length"] == 1
