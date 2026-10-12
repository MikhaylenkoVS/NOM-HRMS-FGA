# Acceptance — CHROM-01

## Критерии приёмки

| # | Критерий | Метод проверки | Ожидаемый результат |
|---|---|---|---|
| C1 | `build_rt_segments` строит отрезки | юнит-тест | 0–20 мин, ширина 2 → 10 отрезков `(0,2)…(18,20)` |
| C2 | Агрегация сканов по сегментам | юнит-тест `aggregate_scan_lists` | интенсивности суммируются только внутри сегмента; m/z группируются по 5-му знаку |
| C3 | CSV = один сегмент | референс-тест | `run_pipeline_segmented` на CSV даёт те же mass/brutto/N_COOH/N_OH, что и `run_pipeline` |
| C4 | RT сохраняется у исходных пиков | код + тест | в таблице есть `rt_start`/`rt_end`; для CSV — `None` |
| C5 | Дериватизованные ищутся по всем сегментам | код: `find_series(src_k, dmet_all, ...)` | подтверждено |
| C6 | Шумоподавление внутри отрезка | код: `denoise` вызывается для каждого сегмента | подтверждено |
| C7 | CLI-флаги | `python -m src.cli --help` | есть `--segment-width`, `--rt-min`, `--rt-max` |
| C8 | CLI сегментный прогон | команда из task.json | exit 0, CSV с колонками `rt_start` |
| C9 | GUI-виджеты | чтение `_params.py`/`app.py` | галочка + поле ширины; `_run_worker` вызывает `run_pipeline_segmented` |
| C10 | Обычный режим не изменился | `pytest tests/ -q` | 0 новых падений |
| C11 | Task packet валиден | `validate-task chrom-01-segmented-averaging` | 0 errors |
| C12 | ADR в индексе | `.ai/decisions/0003-*.md`, `index.md` | ссылка в `task.json → links.adr` |

## Стоп-факторы

- Изменение `src/configs/chemistry.json`.
- Изменение научных констант и скоринга.
- Изменение формата таблицы обычного `run_pipeline`.
- Новые зависимости.

## Definition of Done

1. C1–C12 выполнены; расхождения описаны в `implementation_report.md`.
2. `reference_validation.md` заполнен фактическим сравнением.
3. Коммит в ветке `feat/chrom-01-segmented-averaging`.
4. PR/merge — только по явной команде человека.
