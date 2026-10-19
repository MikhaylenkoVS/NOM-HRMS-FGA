"""Динамический набор комбинаций галогенов (требования пользователя).

Проверяем:
  * лимит по умолчанию (16) — это ДИНАМИЧЕСКИЙ набор, а не жёсткий список;
  * набор определяется окнами элементов (Cl<=5, Br<=3 → Br4 уже невозможен);
  * приоритет: больше атомов одного галогена важнее (F5, Cl4F > F2ClBrI);
  * полный режим («галочка») отдаёт все допустимые комбинации.
"""

from __future__ import annotations

import pytest

from src.core.spectrum._constants import FormulaSearchConfig
from src.core.spectrum._formula_source import (
    combo_priority,
    halogen_combos_within,
    halogen_limits,
    select_halogen_combos,
)

HALO = ("F", "Cl", "Br", "I")


def _cfg(**limits: int) -> FormulaSearchConfig:
    """Конфиг с окнами галогенов 0..N (остальные элементы — по умолчанию)."""
    cfg = FormulaSearchConfig()
    ranges = dict(cfg.ranges or {})
    for el in HALO:
        ranges[el] = (0, int(limits.get(el, 0)))
    cfg.ranges = ranges
    return cfg


def _names(combos) -> list[str]:
    return ["".join(el + (str(n) if n > 1 else "") for el, n in c) for c in combos]


class TestComboPriority:
    """Правило заказчика: начинать с наименьших количеств каждого галогена."""

    def test_starts_with_single_atoms(self):
        """Первыми идут одиночные подстановки F1/Cl1/Br1/I1."""
        singles = [combo_priority(((el, 1),)) for el in HALO]
        pair = combo_priority((("Cl", 2),))
        assert all(sp > pair for sp in singles)

    def test_fewer_atoms_win_over_more(self):
        """Меньше атомов — выше приоритет (перебор от меньших количеств)."""
        assert combo_priority((("Cl", 1),)) > combo_priority((("Cl", 2),))
        assert combo_priority((("Cl", 2),)) > combo_priority((("Cl", 3),))
        assert combo_priority((("F", 2),)) > combo_priority((("F", 3),))

    def test_within_same_total_concentrated_first(self):
        """При равном числе атомов концентрированные важнее смешанных."""
        f5 = combo_priority((("F", 5),))
        cl4f = combo_priority((("Cl", 4), ("F", 1)))
        mixed = combo_priority((("F", 2), ("Cl", 1), ("Br", 1), ("I", 1)))
        assert f5 > cl4f > mixed

    def test_empty_combo_is_lowest(self):
        assert combo_priority((("F", 1),)) > combo_priority(())


class TestDynamicSelection:
    def test_wide_windows_start_from_smallest_counts(self):
        """Широкие окна: набор из 16 начинается с одиночных и двойных."""
        cfg = _cfg(F=5, Cl=5, Br=5, I=5)
        combos, allowed = select_halogen_combos(cfg, 16, False, 5)
        assert allowed == 125
        names = _names(combos)
        assert len(names) == 16
        # первые четыре — одиночные подстановки
        assert set(names[:4]) == {"F", "Cl", "Br", "Cl", "I"} or set(names[:4]) == {
            "F",
            "Cl",
            "Br",
            "I",
        }
        # Cl1 и Br1 обязаны присутствовать (основной реальный случай)
        assert {"Cl", "Br"} <= set(names)
        # F2ClBrI (5 атомов, 4 разных галогена) в набор из 16 не попадает
        assert "F2ClBrI" not in names
        # максимальное число атомов в наборе из 16 — 3
        assert max(sum(n for _, n in c) for c in combos) <= 3

    def test_narrow_windows_shrink_space(self):
        """Cl<=5, Br<=3 (остальные 0): Br4 и F-комбинации невозможны."""
        cfg = _cfg(Cl=5, Br=3)
        combos, allowed = select_halogen_combos(cfg, 16, False, 5)
        assert allowed == 17, _names(combos)
        joined = _names(combos)
        assert all("F" not in n and "I" not in n for n in joined)
        assert not any("Br4" in n or "Br5" in n for n in joined)

    def test_limit_not_padded_when_space_smaller(self):
        """Если допустимых меньше лимита — берутся все, ничего не добирается."""
        cfg = _cfg(Cl=1)
        combos, allowed = select_halogen_combos(cfg, 16, False, 5)
        assert allowed == 1
        assert len(combos) == 1

    def test_total_atoms_cap(self):
        cfg = _cfg(F=5, Cl=5, Br=5, I=5)
        combos, _ = select_halogen_combos(cfg, 16, False, 2)
        assert all(sum(n for _, n in c) <= 2 for c in combos)
        assert "F5" not in _names(combos)

    def test_exhaustive_returns_everything(self):
        cfg = _cfg(F=5, Cl=5, Br=5, I=5)
        combos, allowed = select_halogen_combos(cfg, 16, True, 5)
        assert len(combos) == allowed == 125
        assert "F2ClBrI" in _names(combos)

    def test_limits_reflect_user_windows(self):
        cfg = _cfg(F=2, Cl=5, Br=3, I=1)
        limits = halogen_limits(cfg)
        assert limits == {"F": 2, "Cl": 5, "Br": 3, "I": 1}
        combos = halogen_combos_within(limits, 5)
        assert combos, "набор не должен быть пустым"
        for c in combos:
            for el, n in c:
                assert n <= limits[el]

    def test_zero_windows_give_empty_space(self):
        cfg = _cfg(F=0, Cl=0, Br=0, I=0)
        combos, allowed = select_halogen_combos(cfg, 16, True, 5)
        assert combos == []
        assert allowed == 0


@pytest.fixture(scope="module")
def db():
    """Открытая сжатая база формул (или пропуск тестов)."""
    from src.core.spectrum._formula_source import open_formula_db

    reader = open_formula_db()
    if reader is None:
        pytest.skip("сжатая база формул недоступна")
    yield reader
    reader.close()


class TestPipelineIntegration:
    """Настройки доходят до поиска по базе и меняют число кандидатов."""

    def test_default_is_subset_of_exhaustive(self, db):
        from src.core.spectrum._formula_source import db_candidates

        cfg = _cfg(F=5, Cl=5, Br=5, I=5)
        rows_def, _ = db_candidates(
            db, cfg, 400.1, 0.002, include_halogens=True, max_halogen_atoms=5
        )
        rows_full, _ = db_candidates(
            db,
            cfg,
            400.1,
            0.002,
            include_halogens=True,
            max_halogen_atoms=5,
            halogen_exhaustive=True,
        )
        assert len(rows_def) <= len(rows_full)
        assert len(rows_full) > 0

    def test_narrow_windows_exclude_forbidden_combos(self, db):
        from src.core.spectrum._formula_source import db_candidates
        from src.core.spectrum._constants import FormulaSearchConfig

        cfg = FormulaSearchConfig()
        ranges = dict(cfg.ranges or {})
        ranges.update({"F": (0, 0), "Cl": (0, 5), "Br": (0, 1), "I": (0, 0)})
        cfg.ranges = ranges
        rows, _ = db_candidates(
            db,
            cfg,
            400.1,
            0.002,
            include_halogens=True,
            max_halogen_atoms=5,
            halogen_exhaustive=True,
        )
        elements = tuple(cfg.elements)
        idx = {
            el: elements.index(el) for el in ("F", "Cl", "Br", "I") if el in elements
        }
        for row in rows:
            if "F" in idx:
                assert int(row[idx["F"]]) == 0
            if "I" in idx:
                assert int(row[idx["I"]]) == 0
            if "Br" in idx:
                assert int(row[idx["Br"]]) <= 1


class TestGuiWiring:
    def test_default_limit_16(self):
        from src.ui._params import ParamsMixin

        assert ParamsMixin.HALOGEN_MAX_COMBINATIONS == 16

    def test_settings_window_and_flag_wired(self):
        from pathlib import Path

        src = Path("src/ui/_params.py").read_text(encoding="utf-8")
        assert "Настройки поиска по галогенам" in src
        assert "Проверить все комбинации галогенов" in src
        assert "halogen_exhaustive=" in src
        app = Path("src/app.py").read_text(encoding="utf-8")
        assert "halogen_exhaustive_var" in app

    def test_cli_flags_present(self):
        from pathlib import Path

        cli = Path("src/cli.py").read_text(encoding="utf-8")
        assert "--halogen-exhaustive" in cli
        assert "--halogen-max-combinations" in cli


class TestSearchPlanAndSlowdown:
    """Предупреждение и таблица замедления (требование заказчика)."""

    def test_slowdown_table_is_monotone(self):
        from src.core.spectrum._formula_source import slowdown_factor

        values = [slowdown_factor(n) for n in (16, 20, 30, 40, 60, 80, 100, 125)]
        assert values[0] == 1.0
        assert all(b >= a for a, b in zip(values, values[1:])), values
        assert values[-1] > 1.5

    def test_plan_warns_above_threshold(self):
        from src.core.spectrum._formula_source import halogen_search_plan

        cfg = _cfg(F=5, Cl=5, Br=5, I=5)
        quiet = halogen_search_plan(cfg, 16, False, 5)
        assert quiet["warn"] is False
        assert quiet["slowdown"] == 1.0

        full = halogen_search_plan(cfg, 16, True, 5)
        assert full["warn"] is True
        assert full["selected"] == full["allowed"] == 125
        assert full["slowdown"] > 1.0

    def test_plan_respects_narrow_windows(self):
        from src.core.spectrum._formula_source import halogen_search_plan

        plan = halogen_search_plan(_cfg(Cl=5, Br=3), 16, True, 5)
        assert plan["allowed"] == 17
        assert plan["limits"]["Br"] == 3
        assert plan["limits"]["F"] == 0

    def test_exhaustive_is_default_in_config(self):
        from src.configs import FORMULA_SEARCH_CFG

        hs = getattr(FORMULA_SEARCH_CFG, "halogen_search", {}) or {}
        assert hs.get("exhaustive") is True
        assert hs.get("max_combinations") == 16
        assert hs.get("warn_from") == 21

    def test_warning_text_mentions_window_and_slowdown(self):
        """Механика предупреждения сохранена (может понадобиться позже)."""
        from pathlib import Path

        params = Path("src/ui/_params.py").read_text(encoding="utf-8")
        assert "Настройки поиска по галогенам" in params
        assert "Ориентировочное замедление" in params
        cli = Path("src/cli.py").read_text(encoding="utf-8")
        assert "Ориентировочное замедление" in cli

    def test_warning_display_disabled_by_default(self):
        """Показ предупреждения выключен: замедление оказалось незначительным."""
        from src.configs import FORMULA_SEARCH_CFG
        from src.core.spectrum._formula_source import halogen_search_plan

        hs = getattr(FORMULA_SEARCH_CFG, "halogen_search", {}) or {}
        assert hs.get("show_warning") is False

        plan = halogen_search_plan(_cfg(F=5, Cl=5, Br=5, I=5), 16, True, 5)
        assert plan["warn"] is True  # данные о превышении порога остаются
        assert plan["warn_enabled"] is False  # но пользователю не показываем
