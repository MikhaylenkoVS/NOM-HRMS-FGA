"""Unit tests for batch processing (triple detection + summary)."""

import pandas as pd
import pytest

from src.core.batch import (
    build_batch_summary,
    compute_sample_summary,
    detect_sample_triples,
)


def _write(tmp_path, *names):
    for n in names:
        (tmp_path / n).write_text("mass,intensity\n100,1\n", encoding="utf-8")


@pytest.mark.unit
def test_detect_sample_triples(tmp_path):
    _write(
        tmp_path,
        "sampleA_original.csv",
        "sampleA_cd3.csv",
        "sampleA_cd3co.csv",
        "sampleB_original.csv",
        "sampleB_cd3.csv",
        "sampleB_cd3co.csv",
        "readme.txt",
    )
    triples = detect_sample_triples(str(tmp_path))
    assert len(triples) == 2
    samples = {t["sample"] for t in triples}
    assert samples == {"samplea", "sampleb"}
    for t in triples:
        assert t["src"].endswith("_original.csv")
        assert t["dmet"].endswith("_cd3.csv")
        assert t["dacet"].endswith("_cd3co.csv")


@pytest.mark.unit
def test_detect_sample_triples_cd3co_not_confused_with_cd3(tmp_path):
    _write(
        tmp_path,
        "x_original.csv",
        "x_cd3.csv",
        "x_cd3co.csv",
    )
    triples = detect_sample_triples(str(tmp_path))
    assert len(triples) == 1
    t = triples[0]
    assert t["dmet"].endswith("_cd3.csv")
    assert t["dacet"].endswith("_cd3co.csv")


@pytest.mark.unit
def test_detect_sample_triples_empty(tmp_path):
    _write(tmp_path, "notes.txt")
    assert detect_sample_triples(str(tmp_path)) == []


@pytest.mark.unit
def test_compute_sample_summary():
    table = pd.DataFrame(
        {
            "mass": [100.0, 200.0, 300.0],
            "brutto": ["C1", "C2", "C3"],
            "N_COOH": [0, 1, 2],
            "N_OH": [1, 0, 1],
        }
    )
    s = compute_sample_summary(table, "s1")
    assert s["sample"] == "s1"
    assert s["n_compounds"] == 3
    assert s["N_COOH_total"] == 3
    assert s["N_OH_total"] == 2
    assert s["avg_mass"] == pytest.approx(200.0)


@pytest.mark.unit
def test_compute_sample_summary_empty():
    s = compute_sample_summary(None, "empty")
    assert s["sample"] == "empty"
    assert s["n_compounds"] == 0
    assert s["N_COOH_total"] == 0
    assert s["N_OH_total"] == 0


@pytest.mark.unit
def test_build_batch_summary():
    rows = [
        compute_sample_summary(None, "a"),
        compute_sample_summary(None, "b"),
    ]
    df = build_batch_summary(rows)
    assert list(df.columns)[0] == "sample"
    assert len(df) == 2
