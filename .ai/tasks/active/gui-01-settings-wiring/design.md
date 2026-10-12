# Design — GUI-01: проброс настроек GUI в пайплайн

## Проблема

Аудит показал, что часть настроек GUI принимается `run_pipeline`, но не
доходит до научных стадий:

1. **`sign` (знак иона).** GUI/CLI передают `sign` в `run_pipeline`, но
   `assign_formulas` вызывается без `ion_mode`, поэтому всегда используется
   `CHEM.default_ion_mode` (`[M-H]-`). Параметр `sign` у `assign_formulas`
   объявлен, но не используется. `find_series` также жёстко использует
   `CHEM.default_ion_mode`.
2. **`brutto_dict` (диапазоны элементов).** `run_pipeline` принимает
   `brutto_dict`, но не передаёт его в `assign_formulas`; генерация
   кандидатов всегда идёт с `FormulaSearchConfig()` из конфига.
3. **Пресеты шумоподавления.** `_apply_preset` пишет `noise_force` /
   `noise_intensity` в `self.noise_force_var` / `self.noise_int_var`,
   которые не подключены ни к одному виджету и не читаются `_parse_params`.

## Решение

### 1. Знак иона → режим ионизации

Маппинг (научное правило, фиксируется ADR-0002):

- `"-"` → `"[M-H]-"`
- `"+"` → `"[M+H]+"`
- любое другое/пустое значение → `CHEM.default_ion_mode` (безопасный fallback)

Реализация:

- В `src/core/pipeline/_run.py` добавить приватную функцию
  `_ion_mode_from_sign(sign)`.
- Передавать `ion_mode=_ion_mode_from_sign(sign)` в `assign_formulas`.
- Передавать тот же `ion_mode` в `_find_series_stage` → `find_series`.
- В `src/core/spectrum/_series.py` добавить необязательный параметр
  `ion_mode: str | None = None`; при `None` использовать
  `CHEM.default_ion_mode` (обратная совместимость).
- В `src/core/spectrum/_assign.py` удалить неиспользуемый параметр
  `sign: str | None = None` (в проекте нет вызовов с ним).

### 2. Диапазоны элементов → FormulaSearchConfig

- В `src/core/pipeline/_run.py` перед вызовом `assign_formulas` построить
  `search_config`:
  - `brutto_dict is None` → `None` (дефолтный `FormulaSearchConfig()`);
  - иначе `FormulaSearchConfig(ranges={el: tuple(rng) for el, rng in brutto_dict.items()})`.
- Передавать `search_config=search_config` в `assign_formulas`.
- Импортировать `FormulaSearchConfig` из `src.core.spectrum` (уже
  экспортируется в `spectrum/__init__.py`).

Формат `brutto_dict` из GUI: `{"C": (min, max), "H": ..., "O": ..., "N": ...}`.
`FormulaSearchConfig.elements` по умолчанию — `("C", "H", "O", "N")`;
лишние ключи в `ranges` безопасно игнорируются генератором.

### 3. Пресеты шумоподавления

- В `src/ui/_presets.py` заменить запись в мёртвые переменные на
  маппинг в реально используемые поля:
  - приоритет как в `denoise`: `intensity` > `quantile` > `force`;
  - `noise_intensity` → `noise_method_var = "intensity"`,
    `noise_value_var = str(intensity)`;
  - `noise_quantile` → `noise_method_var = "quantile"`,
    `noise_value_var = str(quantile)`;
  - `noise_force` → `noise_method_var = "auto"`,
    `noise_value_var = str(force)`.
- Вынести маппинг в чистую функцию `_apply_noise_preset(app, params)` или
  `_noise_widget_values(params)` для юнит-тестирования.
- В `src/app.py` удалить `self.noise_force_var` / `self.noise_int_var`
  (мёртвые переменные).

### 4. Консистентность

- `sign` и `brutto_dict` остаются в кэш-ключе — после исправления это
  становится осмысленным (разные параметры дают разные результаты).

## Карта изменений

| Файл | Изменение |
|------|-----------|
| `src/core/pipeline/_run.py` | маппинг sign→ion_mode; проброс ion_mode и search_config в assign_formulas; проброс ion_mode в _find_series_stage |
| `src/core/pipeline/_stages.py` | `_find_series_stage(..., ion_mode)` → `find_series(..., ion_mode=ion_mode)` |
| `src/core/spectrum/_series.py` | параметр `ion_mode=None`, использование в m0_theor |
| `src/core/spectrum/_assign.py` | удаление мёртвого параметра `sign` |
| `src/ui/_presets.py` | маппинг пресетного шума в метод+значение; чистая функция для теста |
| `src/app.py` | удаление `noise_force_var` / `noise_int_var` |
| `tests/` | новые регрессионные тесты |

## Не меняется

- `src/configs/chemistry.json` (научные константы).
- Скоринг NOM-правдоподобия, пороги, веса.
- Формат и порядок колонок итоговой таблицы.
- Поведение при дефолтных параметрах (`sign="-"`, `brutto_dict=None` или
  диапазоны из formula_search.json).
