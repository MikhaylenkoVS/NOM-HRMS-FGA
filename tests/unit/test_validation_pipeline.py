"""Тесты P0-P3: decoy/FDR, конфликты, формульная проверка, статусы."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.core.spectrum._conflicts import analyze_conflicts, mark_conflicts
from src.core.spectrum._decoy import decoy_shifts, fdr_table, q_values
from src.core.spectrum._formula_check import (
    check_series_formula,
    counts_valid,
    is_plausible_brutto,
    is_plausible_nom,
    CD3,
    CD3CO,
    product_counts,
)
from src.core.spectrum._validate import (
    add_status,
    attach_fdr,
    attach_last_steps,
    summarize,
    trim_to_confirmed_last,
)


# ── decoy / FDR ──────────────────────────────────────────────────────────
class TestDecoy:
    def test_count_and_range(self):
        shifts = decoy_shifts(17.03448, k=25, seed=1)
        assert len(shifts) == 25
        assert all(0.05 <= abs(s) <= 0.9 for s in shifts)
        assert any(s > 0 for s in shifts) and any(s < 0 for s in shifts)

    def test_deterministic(self):
        assert decoy_shifts(17.03448, k=10, seed=7) == decoy_shifts(
            17.03448, k=10, seed=7
        )

    def test_avoids_chemistry(self):
        shifts = decoy_shifts(17.03448, k=40, seed=3)
        for banned in (1.003355, 14.01565, 15.994915, 17.03448):
            assert all(abs(abs(s) - banned) >= 0.05 - 1e-9 for s in shifts)

    def test_invalid_k(self):
        with pytest.raises(ValueError):
            decoy_shifts(17.0, k=0)

    def test_fdr_table(self):
        rows = fdr_table([3, 4, 5], [[1, 2], [1, 1]], min_length=1, max_length=5)
        by_len = {r["length"]: r for r in rows}
        assert by_len[3]["n_target"] == 3
        assert by_len[3]["n_decoy_mean"] == 0.0
        assert by_len[1]["n_decoy_mean"] == 2.0
        assert by_len[1]["fdr"] == pytest.approx(2.0 / 3, abs=1e-3)
        assert by_len[5]["n_target"] == 1

    def test_q_values(self):
        table = [
            {"length": 1, "fdr": 0.9},
            {"length": 2, "fdr": 0.4},
            {"length": 3, "fdr": 0.01},
        ]
        assert q_values([1, 2, 3], table) == [0.9, 0.4, 0.01]


# ── конфликты ────────────────────────────────────────────────────────────
class TestConflicts:
    def test_shared_step_is_contested(self):
        df = pd.DataFrame({"series_mz": [[100.0, 117.03], [200.0], [117.031, 134.0]]})
        out = mark_conflicts(df, tolerance=0.001)
        # правило цепочки: у серии 0 есть предыдущая ступень, у серии 2 — нет,
        # значит пик принадлежит серии 0 и для неё не спорный
        assert out["contested_steps"].tolist() == [0, 0, 1]
        # серия 0 владеет спорным пиком; у серии 2 спорна первая ступень,
        # а последняя (134.0) уникальна → не ambiguous
        assert out["ambiguous"].tolist() == [False, False, False]

    def test_independent_series_clean(self):
        out = mark_conflicts(pd.DataFrame({"series_mz": [[100.0], [300.0]]}))
        assert not out["ambiguous"].any()

    def test_empty(self):
        out = mark_conflicts(pd.DataFrame({"series_mz": []}))
        assert out["contested_steps"].tolist() == []


# ── формульная проверка ─────────────────────────────────────────────────
class TestFormulaCheck:
    SRC = {"C": 20, "H": 20, "O": 8, "N": 1, "S": 0, "P": 0}

    def test_cd3_dbe_invariant(self):
        prod = product_counts(self.SRC, 3, CD3)
        base = (2 * 20 + 2 + 1 - 20) / 2
        after = (2 * prod["C"] + 2 + 1 - prod["H"]) / 2
        assert after == base

    def test_cd3co_dbe_grows(self):
        prod = product_counts(self.SRC, 2, CD3CO)
        base = (2 * 20 + 2 + 1 - 20) / 2
        after = (2 * prod["C"] + 2 + 1 - prod["H"]) / 2
        assert after == base + 2

    def test_groups_cannot_exceed_oxygen(self):
        assert check_series_formula(self.SRC, 8, "cd3")["ok"] is True
        res = check_series_formula(self.SRC, 9, "cd3")
        assert res["ok"] is False and "O" in res["reason"]

    def test_valence_violation(self):
        bad = {"C": 1, "H": 10, "O": 0}
        ok, reason = counts_valid(bad)
        assert ok is False and "валентность" in reason

    def test_unknown_group(self):
        with pytest.raises(ValueError):
            check_series_formula(self.SRC, 1, "nope")


# ── статусы и FDR-колонки ───────────────────────────────────────────────
class TestStatus:
    def _frame(self):
        return pd.DataFrame(
            {
                "n_groups": [6, 2, 5, 4],
                "significant": [True, False, True, True],
                "series_mz": [[1.0, 2.0], [3.0], [4.0, 5.0], [6.0]],
            }
        )

    def test_attach_fdr_and_status(self):
        df = self._frame()
        decoys = [
            pd.DataFrame({"n_groups": [1, 1, 2]}),
            pd.DataFrame({"n_groups": [1]}),
        ]
        out = attach_fdr(df, decoys, alpha=0.05)
        assert "q_value" in out and "fdr_significant" in out
        out["formula_ok"] = [True, True, True, False]
        out["ambiguous"] = [False, False, True, False]
        out["shape_ok"] = [True, False, True, True]
        out = add_status(out)
        st = out["status"].tolist()
        assert st[0] == "supported"
        assert st[1] == "rejected_noise"
        assert st[2] == "ambiguous"
        assert st[3] == "real_peak_unrelated"

    def test_summarize_empty(self):
        assert summarize(pd.DataFrame())["n"] == 0


# ── конфликты при пропусках ──────────────────────────────────────────────
class TestConflictsWithGaps:
    def test_gap_does_not_hide_ambiguous_last_step(self):
        # Серия 0: ступени 1 и 3 (ступень 2 пропущена), последняя ступень 3
        # делит пик с серией 1. Раньше позиция последней ступени бралась как
        # index() в steps_found (1) и попадала в пропуск → ambiguous=False.
        df = pd.DataFrame(
            {
                "series_mz": [[100.0, None, 134.0], [134.0]],
                "steps_found": [[1, 3], [1]],
                "n_groups": [3, 1],
            }
        )
        out = mark_conflicts(df)
        assert out["contested_steps"].tolist() == [1, 1]
        assert out["ambiguous"].tolist() == [True, True]

    def test_unshared_step_after_gap_is_not_contested(self):
        df = pd.DataFrame(
            {
                "series_mz": [[100.0, None, 134.0], [200.0]],
                "steps_found": [[1, 3], [1]],
                "n_groups": [3, 1],
            }
        )
        out = mark_conflicts(df)
        assert out["contested_steps"].tolist() == [0, 0]
        assert not out["ambiguous"].any()

    def test_chain_rule_with_gap(self):
        # Серия 0: ступени 2 и 3 (ступень 1 пропущена), для спорной ступени 3
        # предыдущая ступень 2 найдена; у серии 1 предыдущей нет.
        df = pd.DataFrame(
            {
                "series_mz": [[None, 117.0, 134.0], [134.0]],
                "steps_found": [[2, 3], [1]],
                "n_groups": [3, 1],
            }
        )
        out = mark_conflicts(df)
        # пик принадлежит серии 0 (есть ступень 2), серия 1 теряет свой
        # единственный шаг → ambiguous
        assert out["contested_steps"].tolist() == [0, 1]
        assert out["ambiguous"].tolist() == [False, True]


# ── profile/персистентность последних ступеней ───────────────────────────
class TestAttachLastSteps:
    @staticmethod
    def _fake_metrics(monkeypatch, table):
        import src.core.io.raw_profile as rp

        def fake(raw_path, masses, **kwargs):
            rows = [
                {
                    "mass": float(m),
                    "persistence": table[m]["persistence"],
                    "shape_ok": table[m]["shape_ok"],
                    "multi": table[m].get("multi", False),
                    "snr": 10.0,
                    "fwhm": 0.002,
                }
                for m in masses
            ]
            return pd.DataFrame(rows)

        monkeypatch.setattr(rp, "validate_masses", fake)

    def test_last_step_after_gap(self, monkeypatch):
        self._fake_metrics(
            monkeypatch,
            {
                100.0: {"persistence": 0.9, "shape_ok": True},
                134.0: {"persistence": 0.6, "shape_ok": True, "multi": True},
            },
        )
        df = pd.DataFrame(
            {
                "series_mz": [[100.0, None, 134.0]],
                "steps_found": [[1, 3]],
                "n_groups": [3],
            }
        )
        out = attach_last_steps(df, "fake.raw")
        assert out["last_persistence"].tolist() == [0.6]
        assert out["last_shape_ok"].tolist() == [True]
        assert out["last_multi"].tolist() == [True]
        assert out["prev_persistence"].tolist() == [0.9]
        assert out["prev_ok"].tolist() == [True]

    def test_single_step_has_no_prev(self, monkeypatch):
        self._fake_metrics(monkeypatch, {100.0: {"persistence": 0.8, "shape_ok": True}})
        df = pd.DataFrame(
            {"series_mz": [[100.0]], "steps_found": [[1]], "n_groups": [1]}
        )
        out = attach_last_steps(df, "fake.raw")
        assert out["last_persistence"].tolist() == [0.8]
        assert out["prev_persistence"].tolist() == [0.0]
        assert out["prev_ok"].tolist() == [False]

    def test_empty_frame(self):
        out = attach_last_steps(pd.DataFrame(), "fake.raw")
        for col in (
            "last_persistence",
            "last_shape_ok",
            "last_multi",
            "prev_persistence",
            "prev_ok",
        ):
            assert col in out.columns


class TestTrimToConfirmedLast:
    def test_trim_and_drop(self):
        df = pd.DataFrame(
            {
                "n_groups": [3, 3, 3, 1],
                "last_persistence": [0.9, 0.1, 0.1, 0.1],
                "last_shape_ok": [True, True, True, True],
                "prev_persistence": [0.8, 0.8, 0.2, 0.0],
                "prev_ok": [True, True, True, False],
            }
        )
        out = trim_to_confirmed_last(df, persistence_min=0.5)
        assert out["n_groups"].tolist() == [3, 2]
        assert out["trimmed_steps"].tolist() == [0, 1]

    def test_prev_shape_alone_is_not_enough(self):
        df = pd.DataFrame(
            {
                "n_groups": [4],
                "last_persistence": [0.0],
                "last_shape_ok": [False],
                "prev_persistence": [0.3],
                "prev_ok": [True],
            }
        )
        assert trim_to_confirmed_last(df).empty


# ── правдоподобие NOM-формул ─────────────────────────────────────────────
class TestNomPlausibility:
    def test_plausible(self):
        assert is_plausible_brutto("C20H21O8N")[0] is True
        assert is_plausible_brutto("C10H8O5")[0] is True

    def test_halogens_rejected(self):
        assert is_plausible_brutto("C23H32O6S4FCl")[0] is False
        assert "галогены" in is_plausible_brutto("C10H8O5Cl")[1]

    def test_element_limits(self):
        assert is_plausible_brutto("C10H10O5S3")[0] is False
        assert is_plausible_brutto("C10H10O5P2")[0] is False
        assert is_plausible_brutto("C10H5N6")[0] is False

    def test_ratios(self):
        assert is_plausible_brutto("C10H30O5")[0] is False  # H/C = 3
        assert is_plausible_brutto("C10H6O20")[0] is False  # O/C = 2
        assert is_plausible_brutto("C10H4O5")[0] is True

    def test_bad_formula(self):
        assert is_plausible_brutto("не формула")[0] is False
        assert is_plausible_nom({"C": 0, "H": 2})[0] is False


class TestConflictsUseOnlyPlausible:
    def _frame(self):
        # A: ступени 1-2, B: ступени 1-3; пик 117.034 — последний у обоих,
        # у обоих есть предыдущая ступень → правило цепочки не разрешает.
        return pd.DataFrame(
            {
                "series_mz": [[100.0, 117.034], [82.9655, 100.0, 117.034]],
                "steps_found": [[1, 2], [1, 2, 3]],
                "n_groups": [2, 3],
                "brutto": ["C10H8O5", "C23H32O6S4FCl"],
            }
        )

    def test_implausible_competitor_does_not_create_conflict(self):
        out = mark_conflicts(self._frame())
        assert out["contested_steps"].tolist() == [0, 0]
        assert out["ambiguous"].tolist() == [False, False]

    def test_without_filter_conflict_exists(self):
        out = mark_conflicts(self._frame(), valid=[True, True])
        # делятся два пика: 100.0 (шаг 1 vs 2) и 117.034 (шаг 2 vs 3)
        assert out["contested_steps"].tolist() == [2, 1]
        assert out["ambiguous"].tolist() == [True, True]

    def test_plausible_competitor_still_conflicts(self):
        df = self._frame()
        df.loc[1, "brutto"] = "C10H8O5"
        out = mark_conflicts(df)
        assert out["contested_steps"].tolist() == [2, 1]
        assert out["ambiguous"].tolist() == [True, True]

    def test_analyze_conflicts_respects_mask(self):
        df = self._frame()
        assert len(analyze_conflicts(df)) == 0
        assert len(analyze_conflicts(df, valid=[True, True])) == 2

    def test_bad_mask_length(self):
        with pytest.raises(ValueError):
            mark_conflicts(self._frame(), valid=[True])
