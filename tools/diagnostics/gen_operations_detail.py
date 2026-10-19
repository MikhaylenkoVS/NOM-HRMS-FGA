"""Сгенерировать docs/competitors/operations_detail.md — подробное приложение
«операция × проект» из сырых данных сканирования (без фильтрации).

Для каждой из 29 операций и каждого проекта: число попаданий, число файлов,
топ-файлы и примеры строк кода (первыми 6 попаданиями).
"""

from __future__ import annotations

import json
from pathlib import Path

RAW = Path("docs/competitors/raw")
OUT = Path("docs/competitors/operations_detail.md")

RU = {
    "raw_vendor_io": "Чтение сырых файлов приборов (RAW/MzML/…)",
    "transient_ft": "Обработка транзиента и Фурье-преобразование",
    "profile_preprocessing": "Профильная обработка: baseline, сглаживание, усреднение",
    "peak_picking_centroiding": "Пикинг пиков и центроидирование",
    "noise_estimation": "Оценка шума (не только порог)",
    "mass_calibration": "Калибровка/рекалибровка масс",
    "rt_alignment": "Выравнивание по времени удержания",
    "chromatographic_features": "Хроматографические признаки (XIC/деконволюция)",
    "gap_filling": "Заполнение пропусков (gap filling)",
    "isotope_detection": "Изотопы: паттерны, изотопологи, 13C/34S",
    "adduct_ion_identity": "Аддукты и ионные формы (ion identity)",
    "charge_state": "Зарядовые состояния",
    "formula_assignment": "Назначение брутто-формул",
    "formula_scoring": "Скоринг формул (ppm, confidence, ранжирование)",
    "ambiguity_handling": "Неоднозначные/неназначенные результаты",
    "chemical_rules": "Химические правила (DBE, валентность, диапазоны)",
    "halogen_support": "Поддержка галогенов",
    "internal_recalibration_series": "Внутренняя рекалибровка по гомологическим сериям",
    "kendrick": "Kendrick mass defect",
    "descriptors": "Дескрипторы (Ван-Кревелен, DBE, AI, NOSC)",
    "similarity": "Сходство/расстояния между спектрами",
    "statistics": "Статистика (PCA, PLS, кластеризация)",
    "visualization": "Визуализация (графики, карты, сети)",
    "msms": "MS/MS: фрагменты, нейтральные потери, библиотеки",
    "ion_mobility_ccs": "Ионная подвижность / CCS",
    "molecular_networking": "Молекулярные сети",
    "qc_metrics": "QC-метрики (blank, CV, дрейф)",
    "provenance_workflow": "Workflow, provenance, параметры, batch",
    "io_export": "Экспорт результатов (CSV/XLSX/JSON/HDF5)",
}


def main() -> None:
    summary = json.loads((RAW / "_combined_summary.json").read_text(encoding="utf-8"))
    projects = [p["project"] for p in summary["projects"]]
    ops_data = {}
    for pid in projects:
        f = RAW / f"{pid}_operations.json"
        ops_data[pid] = json.loads(f.read_text(encoding="utf-8"))["operations"]

    op_names = list(RU)
    lines = [
        "# Приложение: реализации по операциям (сырые данные, без фильтрации)",
        "",
        "Сгенерировано из `docs/competitors/raw/*_operations.json`. Для каждой операции "
        "показаны все проекты, где встречаются соответствующие ключевые слова: число "
        "попаданий, число файлов, топ-файлы и примеры строк. Это первичный материал "
        "для доработки, а не отбор «важного».",
        "",
    ]
    for op in op_names:
        lines.append(f"## {op} — {RU[op]}")
        lines.append("")
        total = 0
        for pid in projects:
            info = ops_data[pid][op]
            if not info["total_hits"]:
                continue
            total += info["total_hits"]
        lines.append(f"Всего попаданий по всем проектам: **{total}**.")
        lines.append("")
        for pid in projects:
            info = ops_data[pid][op]
            if not info["total_hits"]:
                continue
            lines.append(
                f"### {pid} — {info['total_hits']} попаданий в {len(info['files'])} файлах"
            )
            lines.append("")
            lines.append("Файлы: " + ", ".join(f"`{f}`" for f in info["files"][:12]))
            lines.append("")
            lines.append("Примеры:")
            lines.append("")
            lines.append("```")
            for h in info["hits"][:6]:
                lines.append(f"{h['file']}:{h['line']}: {h['text'][:160]}")
            lines.append("```")
            lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"записано: {OUT} ({OUT.stat().st_size / 1e6:.1f} МБ)")


if __name__ == "__main__":
    main()
