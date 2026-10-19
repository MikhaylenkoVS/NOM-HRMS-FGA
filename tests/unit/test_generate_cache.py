"""Unit tests for the LRU-cached candidate generator (OPT-10)."""

import pytest

from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._generate import (
    _generate_cached,
    _generate_candidate_formulas,
    limits_key,
    ranges_key,
)


@pytest.mark.unit
def test_cached_generation_is_consistent():
    cfg = FormulaSearchConfig()

    _generate_cached.cache_clear()
    a = _generate_cached(
        200.0, 210.0, ranges_key(cfg), limits_key(cfg), cfg.min_c, cfg.max_dbe
    )
    b = _generate_cached(
        200.0, 210.0, ranges_key(cfg), limits_key(cfg), cfg.min_c, cfg.max_dbe
    )

    assert a == b
    assert len(a[0]) > 0
    assert len(a[0]) == len(a[1])  # количества и массы идут параллельно
    assert _generate_cached.cache_info().hits >= 1


@pytest.mark.unit
def test_wrapper_returns_list_of_tuples():
    cfg = FormulaSearchConfig()
    result = _generate_candidate_formulas(200.0, 210.0, cfg, "nom_like")

    assert isinstance(result, list)
    # Каждый кортеж: количества по всем элементам конфига + масса в конце.
    assert all(isinstance(x, tuple) and len(x) == len(cfg.elements) + 1 for x in result)


@pytest.mark.unit
def test_generated_formulas_satisfy_chemistry_rules():
    """Проверка, что генератор соблюдает DBE, чётность и лимиты отношений."""
    from src.core.spectrum._constants import ATOMIC_MASS, HALOGENS

    cfg = FormulaSearchConfig()
    rows, masses = _generate_cached(
        300.0, 310.0, ranges_key(cfg), limits_key(cfg), cfg.min_c, cfg.max_dbe
    )
    assert rows, "на окне 300–310 Да должны быть формулы"

    idx = {el: i for i, el in enumerate(cfg.elements)}
    for counts, mass in zip(rows, masses):
        c = counts[idx["C"]]
        h = counts[idx["H"]]
        n = counts[idx["N"]]
        o = counts[idx["O"]]
        p = counts[idx["P"]]
        s = counts[idx["S"]]
        x = sum(counts[idx[el]] for el in HALOGENS if el in idx)
        assert c >= 1
        # масса собирается из количеств
        calc = sum(counts[idx[el]] * ATOMIC_MASS[el] for el in cfg.elements)
        assert abs(calc - mass) < 1e-6
        # неотрицательный целый DBE
        dbe_num = 2 * c + 2 + n + p - h - x
        assert dbe_num >= 0 and dbe_num % 2 == 0
        # лимиты отношений
        # лимиты отношений: выключенные лимиты (None) в проверку не попадают
        # (например, X/C по умолчанию выключен — см. FormulaSearchConfig.max_xc)
        for el, limit in cfg.ratio_limits().items():
            assert counts[idx[el]] / c <= limit + 1e-9, el
