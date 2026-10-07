"""Shared fixtures, constants and automatic markers for all tests.

Provides:
- ``PROJECT_ROOT`` — absolute path to the repository root.
- ``TEST_SETS_ROOT`` — absolute path to ``data/test_sets/``.
- automatic ``unit`` / ``integration`` / ``smoke`` markers (see
  :func:`pytest_collection_modifyitems`), so that ``pytest -m unit`` and
  ``pytest -m integration`` select tests by location.
"""

from pathlib import Path

import pytest

# ── paths ─────────────────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_SETS_ROOT = PROJECT_ROOT / "data" / "test_sets"

#: Каталог → автоматический маркер.
_DIR_MARKERS = {"unit": "unit", "integration": "integration"}


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def project_root() -> Path:
    """Repository root as a session-scoped fixture."""
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def test_sets_root() -> Path:
    """Path to ``data/test_sets/``."""
    return TEST_SETS_ROOT


# ── автоматическая маркировка ─────────────────────────────────────────────────


def _auto_marker_for(path: Path) -> str | None:
    """Вернуть маркер, соответствующий расположению теста.

    Приоритет: ``smoke`` — для файлов со словом «smoke» в имени, затем
    ``unit`` / ``integration`` — по ближайшему родительскому каталогу.
    """
    if "smoke" in path.name:
        return "smoke"
    for part in reversed(path.parts):
        if part in _DIR_MARKERS:
            return _DIR_MARKERS[part]
    return None


def pytest_collection_modifyitems(config, items) -> None:
    """Проставить тестам маркеры по расположению файла.

    Маркеры ``unit``, ``integration`` и ``smoke`` объявлены в
    ``[tool.pytest.ini_options]``, но вручную были проставлены лишь в
    единичных тестах, поэтому ``pytest -m unit`` выбирал 24 теста из 400+.
    Здесь маркер добавляется автоматически; явно проставленные в тестах
    маркеры не дублируются.
    """
    for item in items:
        marker_name = _auto_marker_for(Path(str(item.path)))
        if marker_name is None:
            continue
        if item.get_closest_marker(marker_name) is None:
            item.add_marker(getattr(pytest.mark, marker_name))
