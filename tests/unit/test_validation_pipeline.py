"""Тесты P0-P3: decoy/FDR, конфликты, формульная проверка, статусы."""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.core.spectrum._conflicts import mark_conflicts
from src.core.spectrum._decoy import decoy_shifts, fdr_table, q_values
from src.core.spectrum._formula_check import (
    check_series_formula,
    counts_valid,
    CD3,
    CD3CO,
    product_counts,
)
from src.core.spectrum._validate import add_status, attach_fdr, summarize


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
        # значит пик принадлежит серии 0
        assert out["contested_steps"].tolist() == [1, 0, 0]
        # у серии 0 спорна последняя ступень → ambiguous;
        # у серии 2 спорна первая, а последняя (134.0) уникальна → не ambiguous
        assert out["ambiguous"].tolist() == [True, False, False]

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
