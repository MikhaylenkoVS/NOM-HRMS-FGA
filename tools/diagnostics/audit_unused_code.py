"""Аудит кода: какие модули нигде не используются (мёртвые/служебные).

Проверяет все .py в src/ и tools/, считает, сколько раз модуль импортируется
из других файлов, и отдельно ловит «экспериментальные» модули, упомянутые
только в докстрингах.

Запуск:  python tools/diagnostics/audit_unused_code.py [--json out.json]
"""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCAN_DIRS = ("src", "tools", "tests")


def module_name(path: Path) -> str:
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def iter_modules():
    for d in SCAN_DIRS:
        base = ROOT / d
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.py")):
            if "__pycache__" in p.parts:
                continue
            yield p, module_name(p)


def _package_parts(path: Path) -> list[str]:
    """Части пакета файла (без имени модуля)."""
    rel = path.relative_to(ROOT).with_suffix("")
    parts = list(rel.parts)[:-1]
    return parts


def collect_imports(path: Path) -> set[str]:
    """Имена импортируемых модулей, включая относительные импорты."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return set()
    found: set[str] = set()
    pkg = _package_parts(path)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                found.add(a.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:
                if node.module:
                    found.add(node.module)
                    for a in node.names:
                        found.add(f"{node.module}.{a}")
                continue
            # относительный импорт: from .x / from ..pkg.x import y
            base = pkg[: len(pkg) - (node.level - 1)] if node.level > 1 else pkg
            target = base + ([node.module] if node.module else [])
            if target:
                found.add(".".join(target))
                for a in node.names:
                    found.add(".".join(target + [a.name]))
    return found


def referenced_in_text(path: Path, needle: str) -> int:
    """Сколько файлов (кроме самого модуля) упоминают имя строкой."""
    count = 0
    for p in ROOT.rglob("*.py"):
        if "__pycache__" in p.parts or p == path:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        if re.search(rf"\b{re.escape(needle)}\b", text):
            count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    a = ap.parse_args()

    modules = list(iter_modules())
    importers: dict[str, set[str]] = {name: set() for _, name in modules}
    for path, name in modules:
        for imp in collect_imports(path):
            if imp in importers:
                importers[imp].add(name)
            # подмодули вида src.x.y
            root = imp.split(".")[0]
            for other, _ in modules:
                if other == root and other != name:
                    importers[other].add(name)

    rows = []
    print(f"{'модуль':60s} {'импортёров':>10s} {'упоминаний':>11s}")
    print("-" * 85)
    for path, name in modules:
        if name.startswith("tests"):
            continue  # тесты — точки входа, «импортёров» у них нет по определению
        if name.startswith(("src.", "tools.")) and name.endswith("__init__"):
            continue
        n_imp = len(importers[name])
        if n_imp:
            continue
        n_ref = referenced_in_text(path, Path(name).name)
        rel = path.relative_to(ROOT).as_posix()
        verdict = "мёртвый?" if n_ref == 0 else "только упоминание"
        rows.append(
            {
                "file": rel,
                "module": name,
                "importers": 0,
                "mentions": n_ref,
                "verdict": verdict,
            }
        )
        print(f"{rel:60s} {n_imp:10d} {n_ref:11d}  {verdict}")

    print(f"\nвсего модулей: {len(modules)}; без импортёров: {len(rows)}")
    if a.json:
        Path(a.json).write_text(
            json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"записано: {a.json}")


if __name__ == "__main__":
    main()
