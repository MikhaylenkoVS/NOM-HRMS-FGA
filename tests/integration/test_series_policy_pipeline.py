"""Интеграция find_series → build_result_table."""

import pandas as pd

from src.core.domain.spectrum import Spectrum
from src.core.spectrum._build import build_result_table
from src.core.spectrum._series import find_series

DELTA = 17.03448


def test_series_to_result_table_display():
    src = Spectrum(
        table=pd.DataFrame(
            {
                "mass": [100.0],
                "intensity": [1000.0],
                "assign": [True],
                "brutto": ["C7H6O2"],
                "all_candidates": [["C7H6O2"]],
            }
        )
    )
    deriv = Spectrum(
        table=pd.DataFrame(
            {
                "mass": [100.0 + n * DELTA for n in (1, 2, 3)],
                "intensity": [1000.0, 800.0, 600.0],
            }
        )
    )
    series = find_series(src, deriv, DELTA, max_groups=5, max_gaps=0)
    assert not series.empty
    out = build_result_table(src, series, pd.DataFrame())
    row = out.iloc[0]
    assert row["N_COOH"] == 1
    assert row["N_COOH_raw"] == 3
    assert row["N_COOH_display"] == "1(3)"
    assert row["N_COOH_ambiguous"] == 3
