"""Unit tests for result-table export (CSV / XLSX / JSON)."""

import json

import pandas as pd
import pytest

from src.core.pipeline._export import export_result_table


def _make_df():
    return pd.DataFrame(
        {"mass": [300.0, 400.0], "intensity": [10.0, 20.0], "brutto": ["C6H6", "C7H8"]}
    )


@pytest.mark.unit
def test_export_csv(tmp_path):
    p = tmp_path / "r.csv"
    export_result_table(_make_df(), p)
    back = pd.read_csv(p, sep=";")
    assert list(back.columns) == ["mass", "intensity", "brutto"]
    assert len(back) == 2


@pytest.mark.unit
def test_export_xlsx(tmp_path):
    p = tmp_path / "r.xlsx"
    export_result_table(_make_df(), p)
    back = pd.read_excel(p)
    assert list(back.columns) == ["mass", "intensity", "brutto"]
    assert len(back) == 2


@pytest.mark.unit
def test_export_json_with_metadata(tmp_path):
    p = tmp_path / "r.json"
    export_result_table(_make_df(), p, metadata={"params": {"sign": "-"}})
    with open(p, encoding="utf-8") as fh:
        payload = json.load(fh)

    assert "metadata" in payload
    assert "generated_at" in payload["metadata"]
    assert payload["metadata"]["params"]["sign"] == "-"
    assert "data" in payload
    assert payload["data"][0]["mass"] == 300.0
    assert payload["data"][1]["brutto"] == "C7H8"
