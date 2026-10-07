# Acceptance — PACKAGE-05

## Критерии приёмки

| # | Критерий | Метод проверки | Ожидаемый результат |
|---|---|---|---|
| B1 | `formula_search.json` загружается | `python -c "from src.configs import FORMULA_SEARCH_CFG; print(FORMULA_SEARCH_CFG['ranges'])"` | значения совпадают с прежними `pipeline.json → formula_search.ranges` |
| B2 | `pipeline.json` не содержит дублей | `python -c "import json; d=json.load(open('src/configs/pipeline.json')); print('formula_search' in d, 'default_brutto_dict' in d)"` | `False False` |
| B3 | Диапазоны формул берутся из нового источника | `_constants._FORMULA_SEARCH` указует на `FORMULA_SEARCH_CFG` | подтверждено чтением кода + B1 |
| B4 | `default_brutto_dict` из нового источника | `DEFAULT_BRUTTO_DICT` == прежние значения C[0,50] H[0,100] O[0,25] N[0,10] | совпадение |
| B5 | Маппинг колонок из JSON | `CSV_COLUMN_MAPPER` содержит прежние 8 пар, включая синонимы `m/z`, `M/Z`, `mz`, `I`, `int`, `Int` | полное совпадение словарей |
| B6 | `run_pipeline(test_mode=True)` читает `PIPELINE.test_mode` | прогон тест-режима | `rel_error=0.5`, `ppm_tol=0.5`, окно None/None |
| B7 | Параметры GMM из конфига | `NOISE_CFG` читается в `_denoise` | `max_components=5` вместо 15 |
| B8 | Ошибки и предупреждения разделены | `PipelineRunResult.ok`, `.errors`, `.messages` | ошибка этапа → `ok=False`; предупреждение визуализации → `ok=True` |
| B9 | CLI: код 1 только при ошибках | прогон с недостижимым `--output` внутри каталога без прав | код 1 при ошибке; предупреждение не влияет |
| B10 | Пустой спектр не падает | `pytest tests/unit/test_spectrum_ops.py -q` | тест пройден, `xfail` снят |
| B11 | Guard'ы краевых случаев | новые тесты (S-09…S-11, K-11, K-22…K-24) | все проходят |
| B12 | **Результат не изменился (разделы 2.1–2.2)** | CLI на set_01 + `md5sum` | `33cde0049db29f91dfeab2c71d13b77e` |
| B13 | Тесты | `pytest tests/ -q` | 0 failures |
| B14 | Линтеры | `flake8`, `black --check` | 0 ошибок |
| B15 | `--cov-fail-under` включён | чтение `ci.yml` + локальный прогон CI-эквивалента | порог задан и пройден |
| B16 | Task packet валиден | `python tools/ai_workflow.py validate-task fix-05-config-and-error-contract` | 0 errors |

## Стоп-факторы

* Любое изменение `src/configs/chemistry.json`.
* Изменение значений `ranges`, `max_hc/max_oc/max_nc/max_dbe/min_c`,
  `default_brutto_dict` относительно действовавших (кроме явно согласованных).
* Изменение поведения скоринга (пороги 20 / 0.3 / N>3, веса).
* Изменение состава/порядка колонок итоговой таблицы.
* Изменение md5 результата на set_01 для разделов 2.1–2.2.
* Удаление публичных атрибутов (`PipelineRunResult.messages` сохраняется).

## Требует отдельного подтверждения владельца

Изменение порога GMM из-за `max_components` 15 → 5 (раздел 2.3). Если владелец
решит сохранить прежнее поведение, в `constants/noise.json` следует вернуть
`max_components = 15` — это правка конфига, а не кода.

## Definition of Done

1. B1–B16 выполнены; расхождения (если есть) описаны в `implementation_report.md`.
2. `reference_validation.md` заполнен фактическими диффами.
3. Коммиты по подзадачам в ветке `dev`.
4. PR и merge не выполняются без явной команды человека.
