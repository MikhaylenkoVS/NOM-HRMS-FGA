"""Сводка по просканированным конкурентам: матрицы и индексы.

Читает <project>_index.json и <project>_operations.json из каталога raw и
собирает:

  * _combined_summary.json  — метрики по проектам (файлы/строки/символы/лицензия/
    число попаданий по операциям);
  * _operations_matrix.json — матрица «операция × проект»: сколько попаданий,
    в скольких файлах, топ-файлы по попаданиям;
  * _operations_matrix.md   — то же в читаемом виде (для отчёта).

Никакой фильтрации «важного» нет: в матрицу попадают ВСЕ операции и все
проекты, для которых есть данные.
"""

from __future__ import annotations

import json
from pathlib import Path

RAW = Path("docs/competitors/raw")


def main() -> None:
    indexes = {}
    operations = {}
    for f in sorted(RAW.glob("*_index.json")):
        pid = f.name[: -len("_index.json")]
        indexes[pid] = json.loads(f.read_text(encoding="utf-8"))
    for f in sorted(RAW.glob("*_operations.json")):
        pid = f.name[: -len("_operations.json")]
        operations[pid] = json.loads(f.read_text(encoding="utf-8"))

    projects = sorted(indexes)

    # ── сводка по проектам ────────────────────────────────────────────────
    summary = []
    for pid in projects:
        idx = indexes[pid]
        ops = operations.get(pid, {}).get("operations", {})
        inv = idx["inventory"]
        summary.append(
            {
                "project": pid,
                "git_commit": idx["git"].get("commit", ""),
                "git_commit_date": idx["git"].get("commit_date", ""),
                "remote": idx["git"].get("remote", ""),
                "license": idx["license"].get("spdx_guess"),
                "license_file": idx["license"].get("file"),
                "license_files_found": idx["license"].get("license_files_found", []),
                "files": inv["files"],
                "lines": inv["total_lines"],
                "bytes": inv["total_bytes"],
                "by_language": inv["by_language"],
                "symbols": idx["symbols_count"],
                "skipped_source_files_by_dir": idx.get(
                    "skipped_source_files_by_dir", {}
                ),
                "operations_with_hits": sum(
                    1 for v in ops.values() if v["total_hits"] > 0
                ),
                "operations_total": len(ops),
            }
        )
    (RAW / "_combined_summary.json").write_text(
        json.dumps({"projects": summary}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    # ── матрица операций ─────────────────────────────────────────────────
    op_names: list[str] = []
    for pid in projects:
        for op in operations.get(pid, {}).get("operations", {}):
            if op not in op_names:
                op_names.append(op)

    matrix: dict[str, dict] = {}
    for op in op_names:
        row: dict[str, dict] = {}
        for pid in projects:
            data = operations.get(pid, {}).get("operations", {}).get(op)
            if not data:
                row[pid] = {"hits": 0, "files": 0, "top_files": []}
                continue
            top = sorted(data["files"])
            row[pid] = {
                "hits": data["total_hits"],
                "files": len(data["files"]),
                "top_files": top[:8],
                "first_hits": data["hits"][:5],
            }
        matrix[op] = row
    (RAW / "_operations_matrix.json").write_text(
        json.dumps({"operations": matrix}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )

    # ── читаемая матрица ─────────────────────────────────────────────────
    lines = ["# Матрица операций: попадания по проектам", ""]
    lines.append(
        "Числа — количество вхождений ключевых слов операции в исходный код "
        "(без фильтрации и без «избранного»). Прочерк — нет попаданий."
    )
    lines.append("")
    header = "| Операция | " + " | ".join(projects) + " |"
    sep = "|" + "---|" * (len(projects) + 1)
    lines += [header, sep]
    for op in op_names:
        cells = []
        for pid in projects:
            h = matrix[op][pid]["hits"]
            cells.append("—" if not h else str(h))
        lines.append(f"| {op} | " + " | ".join(cells) + " |")
    lines.append("")
    lines.append("## Топ-файлы по операциям и проектам")
    lines.append("")
    for op in op_names:
        lines.append(f"### {op}")
        lines.append("")
        for pid in projects:
            info = matrix[op][pid]
            if not info["hits"]:
                continue
            files = ", ".join(f"`{f}`" for f in info["top_files"][:4])
            lines.append(
                f"* **{pid}** — {info['hits']} попаданий в "
                f"{info['files']} файлах; например: {files}"
            )
        lines.append("")
    (RAW / "_operations_matrix.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"проектов: {len(projects)}; операций: {len(op_names)}")
    print(f"сводка:  {RAW / '_combined_summary.json'}")
    print(f"матрица: {RAW / '_operations_matrix.json'}")
    print(f"читаемо: {RAW / '_operations_matrix.md'}")


if __name__ == "__main__":
    main()
