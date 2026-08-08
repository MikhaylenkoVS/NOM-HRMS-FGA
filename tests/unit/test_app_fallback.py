# ============================================================
# tests/unit/test_app_fallback.py
# ============================================================
"""Проверка консистентности сигнатур embed_figure (реальной и fallback)."""

import inspect
import re
from pathlib import Path

import pytest

# ── реальная функция ──
from src.ui.plots import embed_figure as real_embed

REAL_SIG = inspect.signature(real_embed)
REAL_PARAMS = list(REAL_SIG.parameters.keys())


def test_real_signature_is_correct():
    """Реальная embed_figure должна иметь сигнатуру (fig, parent, toolbar)."""
    assert REAL_PARAMS == ["fig", "parent", "toolbar"], (
        f"Ожидалась сигнатура (fig, parent, toolbar), " f"получена {REAL_PARAMS}"
    )


def test_fallback_signature_matches_real():
    """Fallback embed_figure в app.py должен иметь ту же сигнатуру, что и реальная."""
    app_path = Path(__file__).resolve().parents[2] / "src" / "app.py"
    source = app_path.read_text(encoding="utf-8")

    # Находим fallback-определение внутри except-блока:
    # ищем "def embed_figure" ПОСЛЕ строки "_UI_ERROR ="
    except_pos = source.find("_UI_ERROR =")
    assert except_pos > 0, "Не найден блок except в app.py"

    fallback_match = re.search(r"def embed_figure\(([^)]*)\)", source[except_pos:])
    assert (
        fallback_match is not None
    ), "Не найдено fallback-определение embed_figure в except-блоке app.py"

    fallback_params_str = fallback_match.group(1)
    # Извлекаем имена параметров (до '=' если есть default)
    fallback_params = [
        p.strip().split("=")[0].strip()
        for p in fallback_params_str.split(",")
        if p.strip()
    ]

    assert fallback_params == REAL_PARAMS, (
        f"Fallback сигнатура {fallback_params} != реальная {REAL_PARAMS}. "
        f"В app.py: def embed_figure({fallback_params_str})"
    )


def test_call_sites_match_signature():
    """Все вызовы embed_figure в app.py и ui/_*.py используют совместимые аргументы."""
    root = Path(__file__).resolve().parents[2] / "src"
    sources = {"app.py": (root / "app.py").read_text(encoding="utf-8")}
    ui_dir = root / "ui"
    for f in ui_dir.glob("_*.py"):
        sources[f"ui/{f.name}"] = f.read_text(encoding="utf-8")

    all_calls = []
    for fname, source in sources.items():
        calls = re.findall(r"embed_figure\(([^)]*)\)", source)
        for c in calls:
            # Отфильтровываем определение fallback'а
            if (
                "def embed_figure"
                not in source[max(0, source.find(c) - 20) : source.find(c)]
            ):
                all_calls.append((fname, c))

    assert (
        len(all_calls) >= 3
    ), f"Ожидалось минимум 3 места вызова, найдено {len(all_calls)}"

    for i, (fname, args_str) in enumerate(all_calls):
        # Считаем позиционные аргументы (до первого `=` если есть keyword)
        pos_args = [
            a.strip() for a in args_str.split(",") if "=" not in a and a.strip()
        ]
        # Должно быть 2 позиционных: (fig, parent) — toolbar опциональный
        assert len(pos_args) <= 3, (
            f"Вызов #{i}: embed_figure({args_str}) — "
            f"слишком много позиционных аргументов ({len(pos_args)})"
        )
