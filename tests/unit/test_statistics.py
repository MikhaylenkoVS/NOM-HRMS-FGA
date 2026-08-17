"""Unit tests for distribution metrics and histogram plotting."""

import matplotlib.pyplot as plt
import pandas as pd
import pytest

from src.core.statistics import (
    aromaticity_index,
    compute_distribution_metrics,
    create_histograms_plot,
    dbe,
)


def _make_df():
    return pd.DataFrame(
        {
            "brutto": ["C6H6", "C7H8O", "C8H10", "C9H12O"],
            "mass": [78.0, 108.0, 106.0, 136.0],
            "intensity": [100.0, 200.0, 150.0, 250.0],
            "N_COOH": [0, 1, 0, 2],
            "N_OH": [0, 0, 1, 1],
        }
    )


@pytest.mark.unit
def test_dbe():
    assert dbe({"C": 6, "H": 6}) == 4.0  # benzene
    assert dbe({"C": 1, "H": 4}) == 0.0  # methane


@pytest.mark.unit
def test_aromaticity_index():
    # benzene C6H6: (1+6-0-0-3) / (6-0-0-0) = 4/6
    assert aromaticity_index({"C": 6, "H": 6}) == pytest.approx(4 / 6)


@pytest.mark.unit
def test_aromaticity_index_undefined():
    # denominator <= 0 → None
    assert aromaticity_index({"C": 1, "O": 1}) is None


@pytest.mark.unit
def test_compute_distribution_metrics():
    m = compute_distribution_metrics(_make_df())
    assert list(m.columns) == [
        "brutto",
        "mass",
        "intensity",
        "h_c",
        "o_c",
        "dbe",
        "ai",
        "n_cooh",
        "n_oh",
    ]
    assert len(m) == 4
    row0 = m.iloc[0]  # C6H6
    assert row0["h_c"] == 1.0
    assert row0["o_c"] == 0.0
    assert row0["dbe"] == 4.0
    row1 = m.iloc[1]  # C7H8O
    assert row1["h_c"] == pytest.approx(8 / 7)
    assert row1["o_c"] == pytest.approx(1 / 7)


@pytest.mark.unit
def test_create_histograms_plot():
    fig = create_histograms_plot(_make_df())
    assert len(fig.axes) == 6
    plt.close(fig)
