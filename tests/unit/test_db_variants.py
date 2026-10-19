"""Варианты базы формул: реестр, автовыбор, принудительный выбор.

Соответствует выбору в инсталлере: CHNOSP-база, CHNOSPHal-база или без базы.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.formula_db._variants import (
    DB_VARIANTS,
    active_variant,
    describe_choice,
    find_variant_path,
    installed_variants,
    variants_report,
)


class TestRegistry:
    def test_variants_described(self):
        ids = {v.id for v in DB_VARIANTS}
        # Вариант «без базы» в инсталлер не выносится.
        assert ids == {"chnosp", "chorsphal"}
        for v in DB_VARIANTS:
            assert v.title and v.speedup
            assert v.size_mb >= 0
            if v.id != "none":
                assert v.manifest.endswith(".manifest.json")
                assert v.formulas > 0

    def test_priority_order(self):
        """CHNOSPHal приоритетнее CHNOSP (он и берётся, если стоят обе)."""
        by_id = {v.id: v for v in DB_VARIANTS}
        assert by_id["chorsphal"].priority > by_id["chnosp"].priority

    def test_report_rows(self, tmp_path):
        rows = variants_report([tmp_path])
        assert len(rows) == len(DB_VARIANTS)
        assert all("installed" in r and "speedup" in r for r in rows)
        assert not any(r["installed"] for r in rows)  # в пустой папке ничего нет


class TestSelection:
    def test_nothing_installed_gives_none(self, tmp_path):
        assert active_variant([tmp_path]) is None
        assert "перебор" in describe_choice([tmp_path])

    def test_chnosp_installed(self, tmp_path):
        (tmp_path / "chposp_1000_zstd9_v2.manifest.json").write_text("{}")
        v = active_variant([tmp_path])
        assert v is not None and v.id == "chnosp"
        assert "CHNOSP" in describe_choice([tmp_path])

    def test_chorsphal_wins_when_both(self, tmp_path):
        """Если стоят обе базы, берётся более быстрая (с галогенами)."""
        (tmp_path / "chposp_1000_zstd9_v2.manifest.json").write_text("{}")
        (tmp_path / "chorsphal_1000_v3.manifest.json").write_text("{}")
        assert active_variant([tmp_path]).id == "chorsphal"
        assert len(installed_variants([tmp_path])) == 2

    def test_env_none_disables_db(self, tmp_path, monkeypatch):
        (tmp_path / "chposp_1000_zstd9_v2.manifest.json").write_text("{}")
        monkeypatch.setenv("NOM_FORMULA_DB", "none")
        assert active_variant([tmp_path]) is None

    def test_env_choice_forced(self, tmp_path, monkeypatch):
        (tmp_path / "chposp_1000_zstd9_v2.manifest.json").write_text("{}")
        monkeypatch.setenv("NOM_FORMULA_DB", "chnosp")
        assert active_variant([tmp_path]).id == "chnosp"
        monkeypatch.setenv("NOM_FORMULA_DB", "chorsphal")  # не установлена
        assert active_variant([tmp_path]) is None

    def test_find_variant_path(self, tmp_path):
        p = tmp_path / "chorsphal_1000_v3.manifest.json"
        p.write_text("{}")
        assert find_variant_path(DB_VARIANTS[0], [tmp_path]) == p
        assert find_variant_path(DB_VARIANTS[1], [tmp_path]) is None  # не установлена


class TestWiring:
    def test_project_db_is_chnosp(self):
        """В проекте сейчас должна находиться CHNOSP-база."""
        root = Path(__file__).resolve().parents[2]
        rows = {r["id"]: r for r in variants_report([root / "data" / "formula_db"])}
        assert rows["chnosp"]["installed"] is True
        assert rows["chnosp"]["size_mb"] > 0

    def test_find_manifest_uses_registry(self):
        root = Path(__file__).resolve().parents[2]
        src = (root / "src" / "core" / "spectrum" / "_formula_source.py").read_text(
            encoding="utf-8"
        )
        assert "active_variant" in src
        assert "NOM_FORMULA_DB" in src

    def test_cli_flag_and_gui_dialog(self):
        root = Path(__file__).resolve().parents[2]
        cli = (root / "src" / "cli.py").read_text(encoding="utf-8")
        params = (root / "src" / "ui" / "_params.py").read_text(encoding="utf-8")
        assert "--db-variants" in cli
        # именно определение метода, а не только ссылка из кнопки
        assert "def _show_db_variants" in params
        assert "command=self._show_db_variants" in params
        assert "База формул" in params
        # метод должен быть реально вызываемым: проверим компиляцию модуля
        import ast

        tree = ast.parse(params)
        names = {
            n.name
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        assert "_show_db_variants" in names

    def test_installer_rule(self):
        """CHNOSP ставится всегда; переключатель — только при сравнимых объёмах."""
        from src.core.formula_db._variants import (
            installer_options,
            installer_plan,
            mandatory_variants,
        )

        always = [v.id for v in mandatory_variants()]
        assert always == ["chnosp"]
        assert installer_options() == []  # сейчас выбора нет
        plan = installer_plan()
        assert plan["always"] == ["chnosp"]
        assert plan["needs_choice"] is False
        assert "выбор не нужен" in plan["summary"]

    def test_toggle_would_appear_for_comparable_size(self, monkeypatch):
        """Если объём сопоставим — появляется переключатель «или одно, или другое»."""
        from src.core.formula_db import _variants as V

        small_hal = V.FormulaDbVariant(
            id="chorsphal",
            title="CHNOSPHal (ужатый)",
            manifest="chorsphal_test.manifest.json",
            formulas=1000,
            size_mb=next(
                v for v in V.DB_VARIANTS if v.mandatory
            ).size_mb,  # как у CHNOSP
            speedup="×25",
            description="тестовый вариант сопоставимого объёма",
            priority=20,
        )
        monkeypatch.setattr(V, "DB_VARIANTS", (small_hal, *V.DB_VARIANTS[1:]))
        options = V.installer_options()
        assert [v.id for v in options] == ["chorsphal"]
        plan = V.installer_plan()
        assert plan["needs_choice"] is True
        assert "переключатель" in plan["summary"]

    def test_no_db_option_not_offered(self):
        """Вариант «без базы» в инсталлер не выносится."""
        from src.core.formula_db._variants import DB_VARIANTS

        assert "none" not in {v.id for v in DB_VARIANTS}


@pytest.mark.parametrize("variant_id", ["chnosp", "chorsphal"])
def test_sizes_are_plausible(variant_id):
    v = next(x for x in DB_VARIANTS if x.id == variant_id)
    assert 1.0 < v.size_mb < 5000.0
