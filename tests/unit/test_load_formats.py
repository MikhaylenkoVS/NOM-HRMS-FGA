"""Unit tests for ``load_spectrum`` multi-format support (CSV / XLSX / JSON)."""

import pandas as pd
import pytest

from src.core.spectrum import load_spectrum


def _make_df():
    return pd.DataFrame(
        {"mass": [300.0, 400.0, 500.0], "intensity": [10.0, 20.0, 30.0]}
    )


@pytest.mark.unit
def test_load_spectrum_from_csv(tmp_path):
    p = tmp_path / "s.csv"
    _make_df().to_csv(p, index=False)
    sp = load_spectrum(p)
    assert list(sp.table.columns) == ["mass", "intensity"]
    assert len(sp.table) == 3


@pytest.mark.unit
def test_load_spectrum_from_xlsx(tmp_path):
    p = tmp_path / "s.xlsx"
    _make_df().to_excel(p, index=False)
    sp = load_spectrum(p)
    assert list(sp.table.columns) == ["mass", "intensity"]
    assert len(sp.table) == 3


@pytest.mark.unit
def test_load_spectrum_from_json(tmp_path):
    p = tmp_path / "s.json"
    _make_df().to_json(p, orient="records")
    sp = load_spectrum(p)
    assert list(sp.table.columns) == ["mass", "intensity"]
    assert len(sp.table) == 3
