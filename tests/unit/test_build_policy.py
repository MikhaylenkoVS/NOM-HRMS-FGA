"""Итоговая таблица и переключатели NOM-ratio/DBE."""

import pandas as pd

from src.core.domain.spectrum import Spectrum
from src.core.spectrum._build import build_result_table
from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._formula_source import _passes_filters
from src.core.spectrum._generate import limits_key


def _src():
    return Spectrum(
        table=pd.DataFrame(
            {
                "mass": [200.0],
                "intensity": [1000.0],
                "assign": [True],
                "brutto": ["C7H6O2"],
                "all_candidates": [["C7H6O2"]],
            }
        )
    )


def _series():
    return pd.DataFrame(
        {
            "mass_src": [200.0],
            "brutto": ["C7H6O2"],
            "n_groups": [3],
            "steps_found": [[1, 2, 3]],
            "missing": [[]],
            "series_mz": [[217.0, 234.0, 251.0]],
            "confirmed_length": [1],
            "ambiguous_length": [3],
            "display_length": ["1(3)"],
            "confidence": [60.0],
            "step_details": [
                [
                    {"n": 1, "status": "reliable", "reasons": []},
                    {
                        "n": 2,
                        "status": "ambiguous",
                        "reasons": ["x"],
                        "confidence": 80,
                    },
                    {
                        "n": 3,
                        "status": "ambiguous",
                        "reasons": ["y"],
                        "confidence": 60,
                    },
                ]
            ],
        }
    )


def test_build_uses_confirmed_and_display():
    out = build_result_table(_src(), _series(), pd.DataFrame())
    row = out.iloc[0]
    assert row["N_COOH"] == 1
    assert row["N_COOH_raw"] == 3
    assert row["N_COOH_display"] == "1(3)"
    assert row["N_COOH_ambiguous"] == 3
    assert row["N_COOH_confidence"] == 60.0


def test_ratios_disabled_removes_ratio_limits():
    cfg = FormulaSearchConfig(ratios_enabled=False)
    limits = dict(limits_key(cfg))
    assert limits["H"] == float("inf")
    assert limits["O"] == float("inf")


def test_ratio_filter_can_be_disabled():
    cfg = FormulaSearchConfig(ratios_enabled=False)
    # H/C = 3.5, N/C = 1.5, но DBE = 1 (валентность корректна).
    counts = {"C": 10, "H": 35, "N": 15, "O": 1}
    assert _passes_filters(counts, cfg) is False
    cfg2 = FormulaSearchConfig(
        elements=("C", "H", "N", "O"),
        ranges={"C": (1, 20), "H": (1, 60), "N": (0, 20), "O": (0, 5)},
        ratios_enabled=False,
    )
    assert _passes_filters(counts, cfg2) is True
