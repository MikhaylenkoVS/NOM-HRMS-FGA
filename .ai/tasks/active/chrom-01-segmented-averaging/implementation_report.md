# Implementation Report — CHROM-01

## Изменённые файлы

| Файл | Суть изменения |
|------|----------------|
| `src/core/io/_rt_aggregate.py` | новый: `build_rt_segments`, `aggregate_scans` (чистые функции, тестируются без pymzml/pythonnet) |
| `src/core/io/segmented.py` | новый: `average_segments` — диспетчер RAW/mzML/CSV→список сегментных DataFrame с RT |
| `src/core/io/raw_thermo_adapter.py` | `average_raw_segments` + хелпер `_average_scan_range` (одно открытие файла, усреднение по сегментам) |
| `src/core/io/mzml_bridge.py` | `mzml_segments_to_dfs` (однопроходное чтение + агрегация по сегментам) |
| `src/core/pipeline/_segments.py` | новый: `run_pipeline_segmented` (усреднение/денойз/assign внутри отрезков, поиск серий по всем дериватизованным отрезкам, RT у исходных) |
| `src/core/pipeline/__init__.py` | экспорт `run_pipeline_segmented` |
| `src/core/__init__.py` | экспорт `run_pipeline_segmented` |
| `src/cli.py` | флаги `--segment-width`, `--rt-min`, `--rt-max`; сегментная ветка запуска |
| `src/app.py` | `segment_mode_var`, `segment_width_var` |
| `src/ui/_params.py` | виджеты сегментного режима на подвкладке «Обработка» |
| `src/ui/_deps.py` | импорт/fallback `run_pipeline_segmented` |
| `src/ui/_run.py` | `_run`/`_run_worker` поддерживают сегментный режим |
| `tests/unit/test_segmented_averaging.py` | 8 тестов: сегменты, агрегация, референс-эквивалентность CSV |

## Результаты проверок

| Проверка | Результат |
|----------|-----------|
| `pytest tests/unit/test_segmented_averaging.py -v` | 8 passed |
| референс-эквивалентность CSV | PASS (78 строк, общие колонки идентичны) |
| `python -m src.cli --segment-width 2 ...` | exit 0, CSV с `rt_start`/`rt_end` |
| `validate-task chrom-01-segmented-averaging` | VALIDATION PASSED |
| `pytest tests/ -q` (полный) | 463 passed, 1 skipped; 2 pre-existing failures `test_report.py` (нет `reportlab`) |

## Отклонения от design

- RT-диапазон по умолчанию для сегментного режима — `0.0–20.0` мин
  (10 отрезков по 2 мин), а не `0.0–999.0`.
- Для CSV/XLSX/JSON `average_segments` возвращает один сегмент
  `rt_start=None`/`rt_end=None`.
