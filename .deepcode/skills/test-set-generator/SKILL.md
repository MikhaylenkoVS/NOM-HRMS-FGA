---
name: test-set-generator
description: >
  Генерация синтетических тестовых наборов (set_NN) через
  src/simulations/generate_test_sets.py. Создаёт original.csv, deuter*.csv,
  annotations.csv, molecules.csv для регрессионного тестирования. Работа с
  PubChem (search_pubchem_nom_like_cids.py, process_pubchem_candidates.py)
  и ref_data/ref_molecules_all_pubchem_filtered.csv. Активировать когда
  пользователь говорит «сгенерировать тест-сет», «тестовый набор», «set_06»,
  «новый набор», «синтетический спектр», «generate_test_sets», «PubChem»,
  «молекулы-кандидаты», «симуляция»; либо при изменениях в simulations/.
---

# Test Set Generator — генератор синтетических тестовых наборов

Создание новых синтетических наборов данных для регрессионного тестирования
конвейера. Использует молекулы из PubChem (NOM-подобные, отфильтрованные по
Ван-Кревелену) и генерирует три спектра (original, deuteromethylated,
deuteroacylated) с эталонной разметкой.

## Источники истины

| Файл | Назначение |
|------|-----------|
| `src/simulations/generate_test_sets.py` (29K) | Основной генератор спектров |
| `src/simulations/search_pubchem_nom_like_cids.py` | Поиск NOM-подобных CID в PubChem |
| `src/simulations/process_pubchem_candidates.py` | Фильтрация и сохранение кандидатов |
| `data/ref_data/ref_molecules_all_pubchem_filtered.csv` | Справочный список молекул |
| `data/ref_data/van_krevelen_nom_like.png` | Визуализация справочного набора |
| `src/configs/paths.json` | `num_test_sets: 5`, имена спектров |
| `src/configs/pipeline.json` | `test_mode`, `default_brutto_dict` |
| `src/core/van_krevelen.py` | `NOM_REGIONS` — полигоны для проверки NOM-like |

## Последовательность генерации нового набора

### Шаг 1: Получить молекулы-кандидаты

**Вариант A — использовать готовый справочник:**
```python
import pandas as pd
from tests.conftest import PROJECT_ROOT
from src.configs import PATHS

ref = pd.read_csv(PROJECT_ROOT / PATHS.ref_data_dir / "ref_molecules_all_pubchem_filtered.csv")
# Отфильтровать по числу –COOH/–OH, массе, etc.
```

**Вариант B — пополнить из PubChem:**
```bash
python -m src.simulations.search_pubchem_nom_like_cids  # поиск CID
python -m src.simulations.process_pubchem_candidates     # фильтрация
```
Результат добавится в `ref_molecules_all_pubchem_filtered.csv`.

### Шаг 2: Сгенерировать спектры

```bash
python -m src.simulations.generate_test_sets \
    --molecules path/to/molecules.csv \
    --output data/test_sets/set_06 \
    --ppm 0.5 \
    --noise_level 0.05 \
    --seed 42
```

Генератор создаст:
- `original.csv` — пики [M–H]⁻: mass, intensity.
- `deutermethylated.csv` — пики после CD₃-метилирования (–COOH).
- `deuteroacylated.csv` — пики после CD₃CO-ацилирования (–OH).
- `annotations.csv` — разметка (spectrum_type, mass_obs, mass_theor,
  mass_error_ppm, intensity, brutto_formula, n_cooh, n_oh).
- `molecules.csv` — исходные молекулы (formula, carboxyl_count, hydroxyl_count).

### Шаг 3: Проверить валидность

```bash
# Проверить структуру CSV:
pytest tests/unit/test_structural_validity.py -v

# Проверить согласованность аннотаций:
pytest tests/unit/test_annotations_consistency.py -v

# Проверить химическую валидность:
pytest tests/unit/test_chemical_validity.py -v
```

### Шаг 4: Зарегистрировать в pytest

```python
# tests/conftest.py: обновить TEST_SETS_ROOT если надо
# tests/integration/test_pipeline_integration.py: TEST_SETS автоматически
#   подхватит новый set_* через glob("set_*")
```

Новый набор будет автоматически включён в интеграционные тесты, т.к.
`TEST_SETS = sorted([p for p in TEST_SETS_ROOT.glob("set_*") if p.is_dir()])`.

### Шаг 5: Обновить num_test_sets

В `paths.json`: `"num_test_sets": 6` (было 5).

## Параметры генерации (ключевые)

| Параметр | Типичное значение | Описание |
|----------|-------------------|----------|
| `ppm` | 0.5 | Точность генерации пиков (ppm) |
| `noise_level` | 0.05 | Относительный уровень шума |
| `seed` | 42 | Для воспроизводимости |
| `mass_range` | [100, 800] | Диапазон масс молекул |
| `max_cooh` | 5 | Макс. число –COOH |
| `max_oh` | 5 | Макс. число –OH |

## Отличия тестовых наборов

**Единственное различие между set_01..set_05 — набор молекул.** Все остальные
параметры генерации едины (ppm=0.5, noise_level=0.05). При создании нового
набора можно варьировать:
- Классы молекул (липиды, лигнин, белки, углеводы).
- Диапазон масс (низкомолекулярные vs высокомолекулярные).
- Число функциональных групп (–COOH, –OH).
- Уровень шума (для тестирования denoise).

## Проверочный список

- [ ] Seed зафиксирован для воспроизводимости.
- [ ] `molecules.csv` содержит `carboxyl_count` и `hydroxyl_count` (НЕ формула
      `hydroxyl = hydroxyl - carboxyl` — устарела и удалена).
- [ ] `annotations.csv` содержит все три типа спектров (original,
      deutermethylated, deuteroacylated).
- [ ] `|mass_error_ppm| ≤ 0.5` для всех аннотаций.
- [ ] Интенсивности положительные, без NaN.
- [ ] Набор проходит `test_structural_validity.py`.
- [ ] Набор проходит `test_annotations_consistency.py`.
- [ ] Набор проходит `test_chemical_validity.py`.
- [ ] `num_test_sets` в `paths.json` обновлён.
- [ ] Интеграционный тест проходит с новым набором:
      `pytest tests/integration/test_pipeline_integration.py -v`.

## Ручная валидация нового набора

Перед коммитом выполнить:

```bash
# Полный прогон через test_mode:
python -m src.core.pipeline --test --sets-root data/test_sets

# Ожидаемый результат для нового набора:
# denoise_recall ≥ 0.90
# assign_recall ≥ 0.90
# wrong_ratio ≤ 0.15
#
# Если не проходит — проверить молекулы на предмет:
# - Не-NOM-like (не проходят химические фильтры)
# - Слишком слабые пики (шумоподавление вырезает)
# - Конфликт формул (разные молекулы на близких массах)
```

## Типичные проблемы при генерации

1. **Масс-конфликт:** две молекулы с близкими массами (±0.5 ppm).
   Решение: разнести массы или увеличить разрешение генератора.
2. **Молекула не проходит фильтры NOM:** DBE > 30, H/C > 3, etc.
   Решение: отфильтровать до генерации.
3. **Нет OH групп:** `hydroxyl_count = 0` у всей выборки → нет CD3CO серий.
   Решение: добавить молекулы с алифатическими/фенольными OH.

## Связанные скиллы

- `pytest-regression-nom` — интеграция нового набора в тесты.
- `nom-chemical-validity` — проверка NOM-like молекул.
- `config-safety-audit` — обновление paths.json.
