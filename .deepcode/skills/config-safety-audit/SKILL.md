---
name: config-safety-audit
description: >
  Аудит безопасности конфигурации пайплайна: проверка, что каждая настройка
  из pipeline.json/chemistry.json/paths.json действительно применяется, не
  ведёт к крашу и не нарушает химическую валидность. Выявление хардкода
  значений в обход src/configs/. Активировать когда пользователь говорит
  «конфигурация», «config», «хардкод», «настройки», «pipeline.json»,
  «chemistry.json», «paths.json», «audit», «аудит», «проверь конфиг»,
  «константы», «магические числа»; либо при изменении любого JSON в configs/
  или loader.py, presets_loader.py.
---

# Config Safety Audit — аудит конфигурации

Проверка, что ни одна настройка пайплайна не захардкожена в обход
`src/configs/`, что все значения из JSON действительно используются, и что
изменение любого параметра не вызывает крашей или химически невалидных
результатов.

## Единый источник истины

Проект использует централизованную конфигурацию в трёх JSON-файлах:

```
src/configs/
├── chemistry.json     # Научные константы (массы, сдвиги, режим ионизации)
├── pipeline.json      # Параметры конвейера, пороги, test_mode
├── paths.json         # Относительные пути и имена файлов
├── loader.py          # ConfigNamespace + load_config()
├── presets_loader.py  # Загрузка пресетов (soil, water, peat, coal)
├── presets/
│   ├── coal.json
│   ├── peat.json
│   ├── soil.json
│   └── water.json
└── __init__.py        # Экспорт: CHEM, PIPELINE, PATHS, load_config
```

**Ключевое правило:** `from src.configs import CHEM, PIPELINE, PATHS` —
это ЕДИНСТВЕННЫЙ способ получить конфигурацию. Любой `import json` +
`open("pipeline.json")` в обход loader.py — ошибка, которая должно
отлавливаться этим скиллом.

## Методика аудита (пошагово)

### Шаг 1: Собрать все значения из JSON

```bash
python -c "
from src.configs import CHEM, PIPELINE, PATHS
print('=== CHEM ==='); print(CHEM.as_dict())
print('=== PIPELINE ==='); print(PIPELINE.as_dict())
print('=== PATHS ==='); print(PATHS.as_dict())
"
```

### Шаг 2: Найти все хардкоды

Пройти grep-ом по `src/` и `tests/`:

```bash
# Потенциальный хардкод чисел в spectrum_ops
rg -n '\b(1\.0078|1\.007276|17\.034|45\.029|0\.5|1\.0|5\.0|10\.0|20\.0|30\.0)\b' src/ tests/ --type py

# Потенциальный хардкод путей
rg -n '\b(data/|test_sets/|result_table\.csv|original\.csv|deuter.*\.csv)\b' src/ tests/ --type py
```

Каждое найденное число/строка проверяется:
- Есть ли это значение в JSON?
- Если да — заменить на `PIPELINE.xxx` / `CHEM.xxx` / `PATHS.xxx`.
- Если нет — добавить в соответствующий JSON с комментарием.

### Шаг 3: Проверить, что все ключи JSON используются

Обратный аудит: значения в JSON, которые нигде не импортируются — кандидаты
на удаление.

```bash
# Для каждого ключа верхнего уровня PIPELINE:
rg -n 'PIPELINE\.(load_spectrum_defaults|default_brutto_dict|formula_search|run_pipeline_defaults|test_mode|thresholds|smoke_pipeline_params)' src/ tests/
```

### Шаг 4: Проверить консистентность дублирующихся значений

Особое внимание к значениям, которые определены в двух местах:

| Значение | В formula_search | В default_brutto_dict | Риск |
|----------|-----------------|----------------------|------|
| C range | [1, 50] | [0, 50] | min_c различается |
| H range | [4, 100] | [0, 100] | min_h различается |
| O range | [0, 20] | [0, 25] | max_o различается |
| N range | [0, 8] | [0, 10] | max_n различается |

**`default_brutto_dict` устарел**, но `DEFAULT_BRUTTO_DICT` в spectrum_ops.py
всё ещё ссылается на него. Если код где-то использует `DEFAULT_BRUTTO_DICT`
вместо `FormulaSearchConfig().ranges` — это баг.

### Шаг 5: Проверить параметры денойзинга

| Параметр | run_pipeline_defaults | test_mode.denoise | denoise() по умолчанию |
|----------|----------------------|-------------------|----------------------|
| noise_force / force | 10 | 10.0 | 1.5 |
| noise_intensity / intensity | 100 | 100 | None |
| noise_quantile / quantile | — | null | None |

**Риск:** `force=1.5` в сигнатуре `denoise()`, а `run_pipeline` по умолчанию
передаёт `noise_force=10`. Если кто-то вызовет `denoise()` напрямую без
параметров — получит `force=1.5`, а не 10. **Рекомендация:** изменить
значение по умолчанию в `denoise()` на `force=None` и подтягивать из
PIPELINE при None.

### Шаг 6: Проверить консистентность presets

```bash
python -c "
from src.configs.presets_loader import list_presets, load_preset
for p in list_presets():
    pr = load_preset(p['id'])
    # Проверить, что все ключи из pr['params'] — валидные параметры run_pipeline
"
```

### Шаг 7: Проверить безопасность изменений

Для каждого изменённого параметра задать вопросы:
1. Может ли это значение вызвать `ZeroDivisionError`?
2. Может ли `None` сломать нижележащий код (см. `quantile: null`)?
3. Может ли изменение ppm/диапазона привести к химически невалидным формулам?
4. Пройдут ли тесты с новыми значениями?

## Карта зависимостей «JSON → модуль»

### chemistry.json
| Ключ | Импортируется в |
|------|----------------|
| `monoisotopic_masses` | `spectrum_ops.py:56` (ATOMIC_MASS), `atoms.py` (ELEMENT_DATA) |
| `atomic_mass_elements` | `spectrum_ops.py:56` (порядок элементов) |
| `proton_mass` | `spectrum_ops.py:684` (neutral→ion), `pipeline.py` |
| `electron_mass` | В коде не найден — кандидат на удаление? |
| `derivatization_shifts.delta_cd3` | `spectrum_ops.py:43` (DELTA_CD3) |
| `derivatization_shifts.delta_cd3co` | `spectrum_ops.py:46` (DELTA_CD3CO) |
| `default_ion_mode` | `spectrum_ops.py:614` (assign_formulas, значение по умолчанию) |

### pipeline.json
| Ключ | Импортируется в |
|------|----------------|
| `load_spectrum_defaults` | `spectrum_ops.py:205` (load_spectrum defaults) |
| `default_brutto_dict` | `spectrum_ops.py:328` (DEFAULT_BRUTTO_DICT) |
| `formula_search` | `spectrum_ops.py:61–65` (_FS_ELEMENTS, _FS_RANGES) |
| `formula_search.{max_hc,max_oc,max_nc,max_dbe,min_c}` | `spectrum_ops.py:101–105` (FormulaSearchConfig defaults) |
| `run_pipeline_defaults` | `pipeline.py:345–361` (run_pipeline defaults) |
| `test_mode` | `test_pipeline_integration.py:21–24` |
| `thresholds` | `test_pipeline_integration.py:37–39` |
| `smoke_pipeline_params` | `smoke_runner.py:33` |

### paths.json
| Ключ | Импортируется в |
|------|----------------|
| `data_dir` | Через `PROJECT_ROOT / PATHS.data_dir` |
| `test_sets_dir` | `test_pipeline_integration.py:33` |
| `spectrum_files` | `test_chemical_validity.py:22`, `test_annotations_consistency.py` |

## Часто встречающиеся нарушения

1. **Хардкод `proton_mass = 1.007276`** — должно быть `CHEM.proton_mass`
   (точность разная: 1.007276466812).
2. **Хардкод `delta = 17.03448`** — должно быть `CHEM.derivatization_shifts["delta_cd3"]`.
3. **Хардкод `ppm_tol = 0.5`** в тестах — должно быть `PIPELINE.test_mode["assign"]["rel_error_ppm"]`.
4. **Прямое чтение JSON** — `json.load(open("pipeline.json"))` вместо `from src.configs import PIPELINE`.
5. **Неиспользуемый ключ** в JSON — зашумляет конфигурацию, путает.

## Проверочный список

- [ ] Ни одного хардкода чисел/строк, дублирующих значения из JSON.
- [ ] Все ключи JSON используются хотя бы в одном модуле.
- [ ] При изменении JSON — обновлены значения по умолчанию в dataclass-ах (FormulaSearchConfig).
- [ ] Дублирующиеся диапазоны (formula_search vs default_brutto_dict) не разошлись.
- [ ] Presets (soil/water/peat/coal) содержат валидные имена параметров.
- [ ] `electron_mass` либо используется, либо удалён из chemistry.json.
- [ ] `DEFAULT_BRUTTO_DICT` — последний потребитель `default_brutto_dict` — либо удалён, либо явно задокументирован как deprecated.
- [ ] `pytest tests/unit/test_core_utils.py` — зелёный.
- [ ] `pytest tests/unit/test_config_consistency.py` — (рекомендуется создать) проверяет, что все JSON-ключи валидны.

## Связанные скиллы

- `hrms-formula-assignment` — использует formula_search.
- `spectrum-denoise-review` — использует test_mode.denoise.
- `pytest-regression-nom` — использует thresholds.
- `code-review-reliability-first` — ловит хардкод при ревью.
