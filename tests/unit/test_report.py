"""Unit tests for the PDF report generator (REPORT-01)."""

from pathlib import Path

import pandas as pd
import pytest

from src.core.report import generate_pdf_report


def _make_table():
    return pd.DataFrame(
        {
            "mass": [300.0, 400.0, 500.0],
            "intensity": [10.0, 20.0, 30.0],
            "brutto": ["C6H6", "C7H8O", "C8H10"],
            "N_COOH": [0, 1, 2],
            "N_OH": [1, 0, 1],
        }
    )


@pytest.mark.unit
def test_generate_pdf_report(tmp_path):
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(
        output_path=out,
        sample_name="test",
        table=_make_table(),
        params={"sign": "[M-H]-", "rel_error": 1.0},
        version="0.6.1",
    )
    assert Path(path).exists()
    assert Path(path).read_bytes()[:5] == b"%PDF-"


@pytest.mark.unit
def test_generate_pdf_report_empty_table(tmp_path):
    out = tmp_path / "report.pdf"
    path = generate_pdf_report(
        output_path=out, sample_name="test", table=pd.DataFrame()
    )
    assert Path(path).exists()
    assert Path(path).read_bytes()[:5] == b"%PDF-"
