"""Regression tests for GUI-01: GUI settings must reach the scientific stages.

Covers the three gaps found by the GUI audit:

1. ``sign`` was accepted by ``run_pipeline`` but never forwarded to
   ``assign_formulas`` / ``find_series``.
2. ``brutto_dict`` was accepted but never forwarded to ``assign_formulas``.
3. Preset noise parameters were written to dead GUI variables.
"""

import re
from pathlib import Path

from src.configs import CHEM, PATHS
from src.core.pipeline._helpers import _ion_mode_from_sign
from src.core.pipeline._run import _search_config_from_brutto
from src.core.spectrum import FormulaSearchConfig

THIS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = THIS_DIR.parent
SET01 = PROJECT_ROOT / PATHS.test_sets_dir / "set_01"


def _set01_paths():
    return (
        str(SET01 / "original.csv"),
        str(SET01 / "deutermethylated.csv"),
        str(SET01 / "deuteroacylated.csv"),
    )


def _formula_c_count(formula: str) -> int:
    match = re.search(r"C(\d*)", formula)
    if not match:
        return 1 if "C" in formula else 0
    return int(match.group(1) or 1)


# ── 1. sign → ion_mode mapping ────────────────────────────────────────────────


class TestIonModeFromSign:
    def test_plus_maps_to_protonated(self):
        assert _ion_mode_from_sign("+") == "[M+H]+"

    def test_minus_maps_to_deprotonated(self):
        assert _ion_mode_from_sign("-") == "[M-H]-"

    def test_unknown_falls_back_to_default(self):
        assert _ion_mode_from_sign("?") == CHEM.default_ion_mode

    def test_none_falls_back_to_default(self):
        assert _ion_mode_from_sign(None) == CHEM.default_ion_mode


# ── 2. brutto_dict → FormulaSearchConfig ──────────────────────────────────────


class TestSearchConfigFromBrutto:
    def test_none_returns_none(self):
        assert _search_config_from_brutto(None) is None

    def test_empty_returns_none(self):
        assert _search_config_from_brutto({}) is None

    def test_full_ranges(self):
        cfg = _search_config_from_brutto(
            {"C": (5, 60), "H": (4, 120), "O": (1, 30), "N": (0, 3)}
        )
        assert cfg.ranges["C"] == (5, 60)
        assert cfg.ranges["H"] == (4, 120)
        assert cfg.ranges["O"] == (1, 30)
        assert cfg.ranges["N"] == (0, 3)

    def test_partial_ranges_completed_from_defaults(self):
        cfg = _search_config_from_brutto({"C": (1, 3)})
        assert cfg.ranges["C"] == (1, 3)
        default_ranges = FormulaSearchConfig().ranges
        assert cfg.ranges["H"] == default_ranges["H"]
        assert cfg.ranges["O"] == default_ranges["O"]
        assert cfg.ranges["N"] == default_ranges["N"]


# ── 3. end-to-end: sign and brutto_dict change pipeline output ────────────────


def _base_kwargs():
    src, dmet, dacet = _set01_paths()
    return dict(
        src_path=src,
        dmet_path=dmet,
        dacet_path=dacet,
        visualize=False,
        use_cache=False,
        load_mass_min=100.0,
        load_mass_max=1000.0,
        rel_error=0.5,
    )


class TestPipelineSettingsWiring:
    def test_sign_changes_pipeline_result(self):
        from src.core import run_pipeline

        res_neg = run_pipeline(sign="-", **_base_kwargs())
        res_pos = run_pipeline(sign="+", **_base_kwargs())

        assert len(res_neg.table) > 0, "sign='-' должен давать непустую таблицу"
        assert len(res_pos.table) > 0, "sign='+' должен давать непустую таблицу"
        assert not res_neg.table.equals(
            res_pos.table
        ), "sign='-' и sign='+' дали идентичные таблицы — sign не проброшен"

    def test_brutto_dict_limits_pipeline_result(self):
        from src.core import run_pipeline

        res = run_pipeline(
            brutto_dict={"C": (1, 3), "H": (0, 100), "O": (0, 25), "N": (0, 10)},
            **_base_kwargs(),
        )
        assert len(res.table) > 0, "узкий диапазон C:1-3 дал пустую таблицу"
        for formula in res.table["brutto"].dropna():
            assert (
                _formula_c_count(str(formula)) <= 3
            ), f"Формула {formula} вне диапазона C:1-3"


# ── 4. preset noise parameters map to the real GUI fields ─────────────────────


class TestNoiseWidgetValues:
    def test_intensity_wins(self):
        from src.ui._presets import _noise_widget_values

        assert _noise_widget_values({"noise_intensity": 300}) == ("intensity", "300")

    def test_quantile(self):
        from src.ui._presets import _noise_widget_values

        assert _noise_widget_values({"noise_quantile": 0.01}) == ("quantile", "0.01")

    def test_force(self):
        from src.ui._presets import _noise_widget_values

        assert _noise_widget_values({"noise_force": 5.0}) == ("auto", "5.0")

    def test_no_noise_params(self):
        from src.ui._presets import _noise_widget_values

        assert _noise_widget_values({"rel_error": 0.5}) is None
