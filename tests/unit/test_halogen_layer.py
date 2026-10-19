"""Регрессионные тесты галогенного слоя (база формул + F/Cl/Br/I).

Проверяем именно тот дефект, который нашёлся после релиза 0.9.0: база
искалась как ``молекула − X``, из-за чего для нечётного числа галогенов
базовая формула имела нечётную DBE (в закрыто-оболочечной базе её нет) и
галогенорганические формулы не находились вовсе. Правильная модель —
замещение ``H -> X``: база содержит на ``n_X`` больше водородов.
"""

from __future__ import annotations

import pytest

from src.core.spectrum._constants import ATOMIC_MASS, FormulaSearchConfig
from src.core.spectrum._formula_source import (
    _passes_filters,
    db_candidates,
    halogen_combos,
    open_formula_db,
)

pytestmark = pytest.mark.skipif(
    open_formula_db() is None,
    reason="сжатая база формул недоступна (data/formula_db)",
)


def _neutral(counts: dict[str, int]) -> float:
    return sum(ATOMIC_MASS[el] * n for el, n in counts.items())


def _find(counts: dict[str, int], cfg: FormulaSearchConfig, atoms: int = 1):
    """Вернуть массу найденной цели или None."""
    db = open_formula_db()
    try:
        rows, masses = db_candidates(
            db,
            cfg,
            _neutral(counts),
            0.0015,
            include_halogens=True,
            max_halogen_atoms=atoms,
        )
    finally:
        db.close()
    elements = tuple(cfg.elements)
    for row, mass in zip(rows, masses):
        d = {el: int(v) for el, v in zip(elements, row)}
        if all(d.get(el, 0) == n for el, n in counts.items()):
            return float(mass)
    return None


class TestHalogenLayer:
    def test_halogen_combos_one_atom(self):
        assert halogen_combos(1) == [
            (("F", 1),),
            (("Cl", 1),),
            (("Br", 1),),
            (("I", 1),),
        ]

    def test_halogen_combos_two_atoms_include_pairs(self):
        combos = halogen_combos(2)
        assert (("Cl", 2),) in combos
        assert (("Cl", 1), ("Br", 1)) in combos
        assert len(combos) == 4 + 10  # 4 одиночных + 10 пар с повторами

    def test_odd_halogen_found_with_default_limits(self):
        """C20H29ClO: до фикса не находилась (нечётная DBE у базы)."""
        cfg = FormulaSearchConfig()
        target = {"C": 20, "H": 29, "Cl": 1, "O": 1}
        assert _passes_filters(target, cfg) is True  # проходит лимиты X/C, H/C, O/C
        mass = _find(target, cfg)
        assert mass is not None, "хлорорганическая формула не найдена базой"
        assert abs(mass - _neutral(target)) < 1e-6

    def test_two_halogens_found(self):
        cfg = FormulaSearchConfig()
        target = {"C": 20, "H": 30, "Cl": 2, "O": 1}
        assert _passes_filters(target, cfg) is True
        mass = _find(target, cfg, atoms=2)
        assert mass is not None
        assert abs(mass - _neutral(target)) < 1e-6

    def test_xc_filter_is_user_option_off_by_default(self):
        """X/C — пользовательский фильтр: по умолчанию выключен.

        C6H5ClO (X/C ≈ 0.167) при выключенном фильтре находится, при
        включённом лимите 0.1 — отсекается.
        """
        target = {"C": 6, "H": 5, "Cl": 1, "O": 1}
        default = FormulaSearchConfig()
        assert default.max_xc is None
        assert _passes_filters(target, default) is True
        assert _find(target, default) is not None

        strict = FormulaSearchConfig()
        strict.max_xc = 0.1
        assert _passes_filters(target, strict) is False

    def test_base_without_halogens_still_found(self):
        """Обычный CHNOSP-поиск не сломан фиксом (фенол)."""
        cfg = FormulaSearchConfig()
        target = {"C": 6, "H": 6, "O": 1}
        assert _find(target, cfg) is not None


class _Spec:
    """Минимальный спектр для assign_formulas."""

    def __init__(self, table):
        self.table = table


def _assign(rows, db, **kwargs):
    """Назначить формулы на синтетическом спектре; вернуть таблицу."""
    import pandas as pd

    from src.core.spectrum._assign import assign_formulas

    df = pd.DataFrame(rows, columns=["mass", "intensity"])
    spec = _Spec(df.copy())
    assign_formulas(
        spec,
        rel_error_ppm=5.0,
        ion_mode="[M-H]-",
        isotope_filter=True,
        isotope_variants=True,
        original=_Spec(df.copy()),
        formula_db=db,
        **kwargs,
    )
    return spec.table


class TestHalogenIsotopeConsistency:
    """Галогенная формула принимается только при подтверждении паттерном.

    Иначе пик без изотопных сателлитов (например, шумовый) получал бы
    галогенсодержащую формулу — это и наблюдалось на шумовых пиках set_01.
    """

    _PROTON = 1.007276466812
    _TARGET = {"C": 20, "H": 29, "Cl": 1, "O": 1}

    def _base_mz(self) -> float:
        return _neutral(self._TARGET) - self._PROTON

    def test_chlorinated_peak_with_pattern_is_assigned(self):
        from src.core.spectrum._isotopes import pattern

        db = open_formula_db()
        try:
            m0 = self._base_mz()
            pat = pattern(self._TARGET, max_shift=2)
            table = _assign(
                [
                    (m0, 1000.0),
                    (m0 + 1.00335483507, 1000.0 * pat[1]),
                    (m0 + 1.99704990648, 1000.0 * pat[2]),
                ],
                db,
            )
        finally:
            db.close()
        assert table["brutto"][0] == "C20H29OCl"

    def test_peak_without_pattern_gets_no_halogen(self):
        """Одиночный пик без сателлитов не должен становиться галогенидом."""
        db = open_formula_db()
        try:
            table = _assign([(self._base_mz(), 1000.0)], db)
        finally:
            db.close()
        formula = table["brutto"][0]
        if formula is not None and formula == formula:  # не NaN
            assert not any(el in str(formula) for el in ("F", "Cl", "Br", "I"))
