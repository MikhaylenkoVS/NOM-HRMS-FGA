"""Unit tests for the LRU-cached candidate generator (OPT-10)."""

import pytest

from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._generate import _generate_cached, _generate_candidate_formulas


@pytest.mark.unit
def test_cached_generation_is_consistent():
    cfg = FormulaSearchConfig()
    c_range = tuple(cfg.ranges["C"])
    h_range = tuple(cfg.ranges["H"])
    o_range = tuple(cfg.ranges.get("O", (0, 0)))
    n_range = tuple(cfg.ranges.get("N", (0, 0)))

    _generate_cached.cache_clear()
    a = _generate_cached(200.0, 210.0, c_range, h_range, o_range, n_range)
    b = _generate_cached(200.0, 210.0, c_range, h_range, o_range, n_range)

    assert a == b
    assert len(a) > 0
    assert _generate_cached.cache_info().hits >= 1


@pytest.mark.unit
def test_wrapper_returns_list_of_tuples():
    cfg = FormulaSearchConfig()
    result = _generate_candidate_formulas(200.0, 210.0, cfg, "nom_like")

    assert isinstance(result, list)
    assert all(isinstance(x, tuple) and len(x) == 5 for x in result)
