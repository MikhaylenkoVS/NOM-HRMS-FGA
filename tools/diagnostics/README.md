# tools/diagnostics/ — проверки, замеры, оценки

Инструменты, которые могут понадобиться другому разработчику. Все запускаются
из корня проекта. В пользовательскую сборку (`exe`) не попадают: launcher их не
импортирует, в архиве `dist/NOM_HRMS_FGA.exe` их нет.

## Проверки корректности

* `independent_crosscheck.py` — независимый перебор (свои литералы масс, свои
  правила DBE) против рабочей модели. Проверяет полноту множества формул,
  точность масс и восстановление H. Пример:
  `python tools/diagnostics/independent_crosscheck.py --max-mass 250 --halogen-cap 5`
* `audit_unused_code.py` — какие модули нигде не импортируются (мёртвый код и
  служебные скрипты): `python tools/diagnostics/audit_unused_code.py`

## Замеры скорости

* `measure_halogen_slowdown.py` — замедление от числа галогенных комбинаций
  (таблица `halogen_search.slowdown_table` в `formula_search.json`).
* `measure_real_vs_synthetic.py` — то же на реальном спектре и на синтетике,
  плюс сверка с историческим замедлением: `--peaks 200`.
* `bin_benchmark.py`, `bin_full_benchmark.py` — скорость поиска по сжатой базе.

## Оценки размера и формата базы

* `estimate_full_db_size.py`, `estimate_full_db_size_v2.py`,
  `estimate_halogen_db.py`, `estimate_halogen_db_v2.py` — экстраполяция размера
  базы (v2 — уточнённая методика; v1 оставлены для истории).
* `compression_benchmark.py` — бенчмарк сжатия вариантов формата записей.
* `build_halogen_db.py` — сборка базы с галогенами (v3), пока не подключена к
  рабочему пути; использует `src/core/formula_db/_packed64.py`.

## Одноразовое

Скрипты-эксперименты лежат в `tools/_scratch/` (папка в `.gitignore`).
