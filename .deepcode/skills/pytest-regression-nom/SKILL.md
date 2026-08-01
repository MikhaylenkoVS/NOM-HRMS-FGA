---
name: pytest-regression-nom
description: >
  Написание и расширение pytest-тестов для NOM-HRMS-FGA: unit, integration,
  smoke. Работа с эталонными синтетическими наборами set_01–set_05, проверка
  метрик (denoise_recall, assign_recall, wrong_ratio) по допустимым порогам из
  pipeline.json. Активировать когда пользователь говорит «тесты», «pytest»,
  «напиши тест», «test», «unit», «integration», «smoke», «регрессия»,
  «set_01», «set_02», «эталонные данные», «recall», «wrong_ratio»,
  «thresholds»; либо при редактировании файлов в tests/, conftest.py,
  pytest.ini, pipeline.json (секция thresholds или test_mode).
---

# Pytest Regression NOM — регрессионное тестирование

Стандарт написания и расширения тестов для проекта. Использует pytest с
маркерами unit/integration/smoke. Эталонные данные — синтетические наборы
set_01..set_05 в `data/test_sets/`. Пороговые метрики — в `pipeline.json`.

## Структура тестового окружения

```
tests/
├── conftest.py              # Фикстуры PROJECT_ROOT, TEST_SETS_ROOT
├── README.md                # Обзор тестового набора (105 тестов)
├── unit/
│   ├── test__safety.py      # _safe_df, safe()
│   ├── test_annotations_consistency.py  # Согласованность annotations ↔ спектры
│   ├── test_app_fallback.py # Консистентность сигнатур embed_figure
│   ├── test_assign_formulas.py  # Назначение брутто-формул
│   ├── test_atoms.py        # Классы Atom, Hybridization, ELEMENT_DATA
│   ├── test_chemical_validity.py  # Хим. корректность carboxyl/hydroxyl_counts
│   ├── test_core_utils.py   # _ppm_error, parse_formula, нормализация, exact_mass
│   ├── test_denoise.py      # Шумоподавление: recall сигналов и шума
│   ├── test_find_series.py  # Поиск гомологических серий
│   ├── test_fragment_combinations.py  # Сборка фрагментов в молекулы
│   ├── test_fragments.py    # Строительные блоки MoleculeFragment
│   ├── test_isotope_filter.py  # Изотопный фильтр Бейнона
│   ├── test_molecule.py     # Класс Molecule (атомы, связи, IHD)
│   ├── test_nom_prioritize.py  # NOM-приоритизация формул
│   ├── test_pipeline.py     # Модульные тесты pipeline
│   ├── test_raw_bridge.py   # ThermoRAW-мост
│   ├── test_rdkit_bridge.py # RDKit-мост
│   ├── test_spectrum_ops.py # Операции над спектрами
│   ├── test_structural_validity.py  # Структура CSV-файлов
│   └── test_van_krevelen.py # Диаграммы Ван-Кревелена
└── integration/
    ├── test_pipeline_integration.py  # Сквозной прогон по всем set_*
    ├── test_app_smoke.py     # Smoke-прогон GUI
    └── test_raw_integration.py  # Интеграция ThermoRAW
```

## Маркеры pytest и их назначение

| Маркер | Команда запуска | Что тестирует | Время |
|--------|----------------|---------------|-------|
| `unit` | `pytest tests/ -q -m unit` | Отдельные функции/классы | ~30 сек |
| `integration` | `pytest tests/ -q -m integration` | Сквозной прогон по set_* | ~1 мин |
| `smoke` | `pytest tests/ -q -m smoke` | Быстрые проверки целостности | ~10 сек |
| `slow` | `pytest tests/ -q -m slow` | Ресурсоёмкие тесты | >1 мин |

Конфигурация в `pytest.ini` и `pyproject.toml [tool.pytest.ini_options]`.

## Пороговые метрики (pipeline.json → thresholds)

| Ключ | Значение | Смысл | Вычисляется в |
|------|----------|-------|--------------|
| `min_denoise_recall` | 0.90 | Минимальная доля сохранённых сигналов | `TestSetResult.denoise_recall` |
| `min_assign_recall` | 0.90 | Минимальная доля правильно назначенных формул | `TestSetResult.assign_recall` |
| `max_wrong_ratio` | 0.15 | Максимальная доля неверно определённых серий | Сравнивается с `dmet_wrong/dmet_found` |

**ВАЖНО:** пороги ориентировочные («на глаз»), не утверждены. При написании
нового теста допускается временное непрохождение порога, но это должно быть
явно зафиксировано как `pytest.mark.xfail(reason="Временное снижение — см. issue #N")`.

## Формат эталонных данных

### Структура test_set (например, set_01)

```
data/test_sets/set_01/
├── original.csv           # Исходный спектр [M–H]⁻: mass, intensity
├── deutermethylated.csv   # Спектр после CD₃-метилирования (–COOH)
├── deuteroacylated.csv    # Спектр после CD₃CO-ацилирования (–OH)
├── annotations.csv        # Эталонная разметка пиков
└── molecules.csv          # Список молекул-кандидатов
```

**config.json отсутствует** — конфигурация в `src/configs/`. Наборы отличаются
только набором молекул, параметры генерации едины.

### Формат annotations.csv

Колонки: `spectrum_type`, `mass_obs`, `mass_theor`, `mass_error_ppm`, `intensity`,
`brutto_formula`, `n_cooh`, `n_oh`, (возможно, `formula`).

- `spectrum_type`: "original", "deutermethylated" или "deuteroacylated".
- `mass_obs`: наблюдаемая m/z.
- `mass_theor`: теоретическая m/z.
- `mass_error_ppm`: отклонение в ppm: `(mass_obs − mass_theor) / mass_theor × 1e6`.
- Допуск: `|mass_error_ppm| ≤ 0.5` для синтетических данных.

### Формат molecules.csv

Колонки: `formula`, `carboxyl_count`, `hydroxyl_count`.

**Устарело:** формула `hydroxyl_count = hydroxyl_count − carboxyl_count` —
должна быть удалена. В molecules.csv hydroxyl_count — это число свободных
OH-групп (не включая OH в составе COOH).

## Как писать новый тест

### 1. Определи тип теста

- **Unit:** тестирует одну функцию/класс без файловой системы. Использует
  синтетические данные в памяти.
- **Integration:** загружает реальные CSV из `data/test_sets/`. Проверяет
  denoise_recall, assign_recall, wrong_ratio.
- **Smoke:** быстрый прогон (≤10 сек), проверяет импорты и базовую
  работоспособность.

### 2. Используй фикстуры из conftest.py

```python
from tests.conftest import PROJECT_ROOT, TEST_SETS_ROOT
from src.configs import CHEM, PIPELINE, PATHS
```

### 3. Ссылайся на конфигурацию, не хардкодь

```python
# ПРАВИЛЬНО:
REL_ERROR_PPM = PIPELINE.test_mode["assign"]["rel_error_ppm"]
MATCH_PPM = PIPELINE.test_mode["match_ppm"]
MIN_DENOISE_RECALL = PIPELINE.thresholds["min_denoise_recall"]

# НЕПРАВИЛЬНО:
REL_ERROR_PPM = 0.5   # хардкод!
```

### 4. Для интеграционных тестов: параметризуй по всем наборам

```python
from tests.conftest import PROJECT_ROOT, TEST_SETS_ROOT

TEST_SETS = sorted([p for p in TEST_SETS_ROOT.glob("set_*") if p.is_dir()])

@pytest.mark.integration
@pytest.mark.parametrize("set_dir", TEST_SETS, ids=[p.name for p in TEST_SETS])
def test_denoise_recall_on_all_sets(set_dir):
    ...
```

### 5. Добавь маркер

```python
@pytest.mark.unit
def test_my_function():
    ...

@pytest.mark.integration
def test_pipeline_on_set_01():
    ...
```

### 6. Проверочный список перед коммитом теста

- [ ] Тест использует `CHEM`/`PIPELINE`/`PATHS` вместо хардкода.
- [ ] Для новых integration-тестов: параметризованы по всем 5 наборам (или обосновано, почему один).
- [ ] Маркер (unit/integration/smoke/slow) проставлен.
- [ ] `pytest tests/ -q` — все 105+ тестов зелёные.
- [ ] Если новый тест временно падает — `@pytest.mark.xfail` с комментарием.
- [ ] Тест не зависит от порядка выполнения (нет общего глобального состояния).
- [ ] Для тестов, читающих CSV: путь через `PATHS.spectrum_files["original"]`, а не хардкод `"original.csv"`.

## Типичные ошибки в тестах

1. **Хардкод ppm=0.5** вместо `PIPELINE.test_mode["assign"]["rel_error_ppm"]`.
2. **Тестирование только set_01** — для integration-тестов обязательно все 5.
3. **Зависимость от порядка:** глобальная переменная, модифицируемая в одном
   тесте и читаемая в другом.
4. **Слишком жёсткий assert:** `if denoise_recall < 0.90: raise` — если пороги
   временно снижены, тест должен это отражать через xfail.
5. **Отсутствие маркера:** CI не сможет выборочно запускать тесты.

## Связанные скиллы

- `test-set-generator` — генерация новых синтетических наборов.
- `config-safety-audit` — аудит порогов в pipeline.json.
- `spectrum-denoise-review` — метрики denoise_recall.
- `hrms-formula-assignment` — метрики assign_recall.
