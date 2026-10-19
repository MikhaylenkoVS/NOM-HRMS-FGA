"""Материалы для статьи: рисунки и таблицы (без текстовых отчётов).

Проверяем, что генератор создаёт файлы нужных типов и что технические
характеристики действительно содержат ключевые пункты.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


def _df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "mass": [200.1, 250.2, 300.3, 350.4, 400.5, 450.6],
            "intensity": [1000.0, 800.0, 600.0, 400.0, 200.0, 100.0],
            "brutto": [
                "C10H12O5",
                "C12H14O6",
                "C14H16O7",
                "C16H18O8",
                "C18H20O9",
                "C20H29OCl",
            ],
            "N_COOH": [0, 1, 1, 2, 2, 3],
            "N_OH": [0, 1, 2, 2, 3, 3],
            "iso_status": [
                "confirmed",
                "uninformative",
                "inconsistent",
                "inconsistent",
                "uninformative",
                "confirmed",
            ],
            "iso_halogen_unconfirmed": [False, False, False, False, False, True],
        }
    )


class TestArticleReport:
    def test_generates_figures_and_tables(self, tmp_path):
        from tools.article_report import generate_article_report

        res = generate_article_report(
            df=_df(), outdir=tmp_path, progress=lambda _m: None
        )
        names = {Path(p).name for p in res["figures"]} | {
            Path(p).name for p in res["tables"]
        }
        # рисунки: Ван-Кревелен, распределения, группы, изотопы, тех. таблица
        assert "fig_02_van_krevelen.png" in names
        assert "fig_04_groups.png" in names
        assert "fig_05_isotope_status.png" in names
        assert "fig_06_technical.png" in names
        # таблицы
        assert "table_01_results.xlsx" in names
        assert "table_02_technical.xlsx" in names
        assert "table_03_groups.xlsx" in names
        for rel in list(res["figures"]) + list(res["tables"]):
            p = Path(rel)
            assert p.exists() and p.stat().st_size > 0

    def test_no_text_reports(self, tmp_path):
        """Отчёты не текстовые: только изображения и таблицы."""
        from tools.article_report import generate_article_report

        res = generate_article_report(
            df=_df(), outdir=tmp_path, progress=lambda _m: None
        )
        for rel in list(res["figures"]) + list(res["tables"]):
            assert Path(rel).suffix.lower() in {".png", ".xlsx", ".sdf"}

    def test_technical_characteristics_content(self):
        from tools.article_report import technical_characteristics

        tech = technical_characteristics(_df(), timing={"Обработка спектров": 12.5})
        keys = " ".join(tech["Характеристика"].astype(str))
        for expected in (
            "Версия программы",
            "Python",
            "Платформа",
            "Соединений в отчёте",
            "Формул с галогенами",
            "Среднее N_COOH",
            "Обработка спектров",
        ):
            assert expected in keys, expected
        halogen_row = tech[tech["Характеристика"] == "Формул с галогенами"]
        assert halogen_row["Значение"].iloc[0] == "1"  # C20H29OCl

    def test_groups_table(self):
        from tools.article_report import table_groups

        groups = table_groups(_df())
        assert set(groups["группа"]) == {"N_COOH", "N_OH"}
        assert groups["соединений"].sum() == 12  # 6 строк × 2 группы


class TestCodePlacement:
    """Правила размещения кода (см. tools/README.md)."""

    def test_scratch_dir_is_gitignored(self):
        root = Path(__file__).resolve().parents[2]
        ignored = (root / ".gitignore").read_text(encoding="utf-8")
        assert "tools/_scratch/" in ignored

    def test_diagnostics_documented(self):
        root = Path(__file__).resolve().parents[2]
        readme = root / "tools" / "diagnostics" / "README.md"
        assert readme.exists()
        text = readme.read_text(encoding="utf-8")
        assert "independent_crosscheck.py" in text
        assert "measure_halogen_slowdown.py" in text

    def test_article_report_has_no_text_output(self):
        root = Path(__file__).resolve().parents[2]
        src = (root / "tools" / "article_report.py").read_text(encoding="utf-8")
        # отчёты — картинки и таблицы, текстовых файлов не пишем
        for forbidden in (".md'", ".txt'", "open(.*'w'.*report"):
            assert forbidden not in src

    def test_gui_button_wired(self):
        root = Path(__file__).resolve().parents[2]
        tabs = (root / "src" / "ui" / "_tabs.py").read_text(encoding="utf-8")
        presets = (root / "src" / "ui" / "_presets.py").read_text(encoding="utf-8")
        assert "Материалы для статьи" in tabs
        assert "_export_article_materials" in presets


@pytest.mark.parametrize("name", ["article_report.py"])
def test_article_report_importable(name):
    import importlib

    assert importlib.import_module(f"tools.{name[:-3]}") is not None
