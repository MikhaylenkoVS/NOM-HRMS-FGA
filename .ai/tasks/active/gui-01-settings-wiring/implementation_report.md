# Implementation Report — GUI-01

## Изменённые файлы

| Файл | Суть изменения |
|------|----------------|
| `src/core/pipeline/_helpers.py` | Добавлена `_ion_mode_from_sign(sign)`: `-`→`[M-H]-`, `+`→`[M+H]+`, прочее→`CHEM.default_ion_mode` |
| `src/core/pipeline/_run.py` | `run_pipeline` пробрасывает `ion_mode` и `search_config` в `assign_formulas`, `ion_mode` в `_find_series_stage`; добавлена `_search_config_from_brutto()` |
| `src/core/pipeline/_stages.py` | `_find_series_stage` принимает и передаёт `ion_mode` в `find_series` |
| `src/core/pipeline/_test_set.py` | Тест-режим тоже пробрасывает `ion_mode=_ion_mode_from_sign(sign)` в `assign_formulas` |
| `src/core/spectrum/_series.py` | `find_series` получил необязательный `ion_mode=None` и использует его для теоретической m/z |
| `src/core/spectrum/_assign.py` | Удалён неиспользуемый параметр `sign` |
| `src/ui/_presets.py` | Пресет шумоподавления маппится в реальные GUI-поля (метод+значение); добавлена чистая функция `_noise_widget_values()` |
| `src/app.py` | Удалены мёртвые `noise_force_var` / `noise_int_var` |
| `tests/unit/test_gui_settings_wiring.py` | Новые регрессионные тесты (14 шт.) |
| `tests/unit/test_spectrum_ops.py` | Вызовы `assign_formulas(sign=...)` заменены на `ion_mode=` |

## Результаты проверок

| Проверка | Результат |
|----------|-----------|
| `pytest tests/unit/test_gui_settings_wiring.py` | 14 passed |
| `pytest tests/unit/test_spectrum_ops.py tests/unit/test_pipeline.py tests/unit/test_cli.py tests/unit/test_find_series.py` | 92 passed |
| md5 set_01 (дефолт) | `33cde0049db29f91dfeab2c71d13b77e` — совпал с baseline |
| `sign="+"` vs `"-"` | 52 vs 78 строк — настройка влияет |
| `brutto_dict` C:1-3 vs C:40-60 | 2 vs 47 строк — настройка влияет |
| `validate-task gui-01-settings-wiring` | VALIDATION PASSED |
| `pytest tests/ -q` (полный) | 469 passed, 1 skipped; 2 pre-existing failures в `test_report.py` из-за отсутствующего `reportlab` (модуль `src/core/report.py` не изменялся) |

## Отклонения от design

- `_ion_mode_from_sign` вынесена в `src/core/pipeline/_helpers.py` (а не в
  `_run.py`), чтобы тест-режим (`_test_set.py`) тоже мог её использовать без
  циклического импорта.
- `_search_config_from_brutto` дополняет частично заданные диапазоны
  элементов дефолтными (CLI `--element-ranges C:1-3` больше не падает на
  `FormulaSearchConfig`).
