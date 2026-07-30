# Замена nomspectra (GPLv3) на собственный код

> **Создан:** 2026-07-30 | **Статус:** 🔴 план | **Зависит от:** external-replacement-plan.md
> **Принцип:** clean-room — свой класс Spectrum (обёртка над DataFrame) +
> отказ от nomspectra.assign_formula в пользу собственной реализации.

## Анализ использования nomspectra в коде

### Импорты (3 файла)
```
src/core/spectrum_ops.py:24     from nomspectra.spectrum import Spectrum
src/testing/artifact_export.py:153   from nomspectra.spectrum import Spectrum
tests/unit/test_nom_prioritize.py:5  from nomspectra.spectrum import Spectrum
```

### Полный перечень используемого API nomspectra

Проверены: прямые импорты, вызовы методов Spectrum, функции-обёртки.
Никаких скрытых обёрток нет. Только 3 точки входа:

| # | API nomspectra | Вхождений | Где | Сложность замены |
|---|---------------|:---:|-----|:---:|
| 1 | `Spectrum(table=df, metadata=meta)` | 38 | spectrum_ops, pipeline, tests | Тривиально |
| 2 | `spec.table` / `spec.table = df` | 55 | spectrum_ops, pipeline | Тривиально |
| 3 | `spec.noise_filter(force, intensity, quantile)` | 6 (через обёртку `denoise()`) | `spectrum_ops.py:319`, pipeline, smoke | Просто (~40 строк) |

**НЕ используются:**
- `spec.assign_formula()` — заменён на свою `assign_formulas()`
- `spec.merge()`, `spec.filter()`, `spec.isotope()` — нигде не вызываются
- `spec.get()`, `spec.metadata.add()` — нигде в коде проекта (только внутри самого nomspectra)
- `assign_formulas_nomspectra()` — мёртвый код, не вызывается из пайплайна

### Исходный код `noise_filter` (40 строк)

```python
@_copy
def noise_filter(self, force=1.5, intensity=None, quantile=None):
    if intensity is not None:
        self.table = self.table.loc[self.table['intensity'] > intensity]
    elif quantile is not None:
        tresh = self.table['intensity'].quantile(quantile)
        self.table = self.table.loc[self.table['intensity'] > tresh]
    else:
        intens = self.table['intensity'].values
        cut_diapasone = np.linspace(0, np.mean(intens), 100)
        d = [len(intens[intens > i]) for i in cut_diapasone]
        dx = np.gradient(d, 1)
        tresh = np.where(dx == np.min(dx))
        cut = cut_diapasone[tresh[0][0]] * force
        self.table = self.table.loc[self.table['intensity'] > cut]
```

Алгоритм auto-режима: сканирует 100 порогов от 0 до средней интенсивности → строит гистограмму числа пиков выше порога → находит порог с минимальным градиентом (излом кривой = граница шум/сигнал) → умножает на force.

---

## Фаза 1: Свой класс Spectrum (с нуля)

### 1.1. Спроектировать API

```python
@dataclass
class Spectrum:
    table: pd.DataFrame      # Основные данные (колонки: mass, intensity, ...)
    metadata: dict           # Произвольные метаданные

    def get(self, key, default=None):  # Доступ к метаданным
        return self.metadata.get(key, default)

    def __len__(self):                  # len(spec) → количество пиков
        return len(self.table)
```

Требования к таблице `table`:
- Обязательные колонки: `mass`, `intensity`
- Опциональные: `assign` (bool), `brutto` (str), `all_candidates` (list), `mass_key` (float)

### 1.2. Реализовать в `src/core/spectrum.py`

- [ ] Создать `src/core/spectrum.py` с классом `Spectrum`
- [ ] Конструктор: `Spectrum(table, metadata=None)` — валидация колонок `mass`, `intensity`
- [ ] Метод `get(key, default=None)` — прокси к `metadata`
- [ ] `__len__`, `__repr__`
- [ ] Написать unit-тесты: конструктор, get, len, repr

### 1.3. Заменить импорты

- [ ] `src/core/spectrum_ops.py:24` — `from .spectrum import Spectrum`
- [ ] `src/testing/artifact_export.py:153` — `from src.core.spectrum import Spectrum`
- [ ] `tests/unit/test_nom_prioritize.py:5` — `from src.core.spectrum import Spectrum`
- [ ] `tests/unit/test_spectrum_ops.py` — `from src.core.spectrum import Spectrum`

### 1.4. Адаптировать код под новый Spectrum

- [ ] Проверить, что `spec.table` работает без изменений (доступ к DataFrame)
- [ ] Проверить, что `spec.table = df` работает без изменений
- [ ] Проверить, что `Spectrum(table=df, metadata=meta)` работает без изменений
- [ ] Проверить `hasattr(src, "table")` → работает
- [ ] Проверить `len(src.table)` → работает

### 1.5. Тестирование

- [ ] Прогнать все существующие тесты — должны пройти
- [ ] Прогнать smoke-тест пайплайна на тестовых данных
- [ ] Проверить GUI: загрузка CSV, анализ, визуализация

---

## Фаза 2: Убрать nomspectra из assign_formulas

### 2.1. Анализ текущего состояния

- `assign_formulas_nomspectra()` (spectrum_ops.py:813) — обёртка над nomspectra
- В `pipeline.py:600` вызывается `assign_formulas()` (своя реализация), а не nomspectra
- `assign_formulas_nomspectra` НЕ вызывается из основного пайплайна — мёртвый код
- `assign_formulas` в spectrum_ops.py:607 — своя clean-room реализация

### 2.2. Действия

- [ ] Удалить `assign_formulas_nomspectra()` из spectrum_ops.py (мёртвый код)
- [ ] Убедиться, что `assign_formulas()` (своя) покрывает все нужные сценарии
- [ ] Удалить импорт/зависимость nomspectra из `assign_formulas` сигнатур

---

## Фаза 3: Реализовать свой noise_filter

### 3.1. Алгоритм auto-режима

Из анализа исходного кода `noise_filter` (~40 строк):

1. `intensity` задан → фильтр `table.intensity > intensity`
2. `quantile` задан → порог = квантиль распределения интенсивностей
3. Авто-режим:
   - 100 порогов от 0 до `mean(intensity)`
   - Для каждого порога — подсчёт числа пиков выше него
   - `np.gradient` по кривой «пиков выше порога»
   - Порог с минимальным градиентом = граница шум/сигнал
   - Итоговый порог = `auto_threshold * force`

### 3.2. Реализовать

- [ ] Добавить метод `noise_filter(self, force=1.5, intensity=None, quantile=None)` в свой класс `Spectrum`
- [ ] Три ветки: intensity / quantile / auto (алгоритм выше)
- [ ] Возвращать новый Spectrum (не мутировать исходный — семантика `@_copy`)
- [ ] Обновить обёртку `denoise()` в `spectrum_ops.py:319` — должен вызывать `spec.noise_filter(...)`

### 3.3. Тестирование

- [ ] Unit: `intensity=100` → все пики с `intens > 100` сохранены
- [ ] Unit: `quantile=0.1` → обрезаны 10% самых слабых пиков
- [ ] Unit: auto-режим на синтетическом спектре (шум + сигнал)
- [ ] Интеграционный: pipeline denoise → результат совпадает с nomspectra-версией в пределах погрешности

---

## Фаза 4: Очистка зависимостей

- [ ] Удалить `nomspectra>=1.0.0` из `pyproject.toml` dependencies
- [ ] Удалить `nomspectra` из `requirements.txt`
- [ ] Удалить `nomspectra` из `_collect_packages` в `.spec`
- [ ] Удалить `collect_submodules("nomspectra")` из `.spec`
- [ ] Удалить `nomspectra` из `release_exe.yml`
- [ ] Проверить grep-ом: `grep -rn "nomspectra" src/ tests/` → 0 совпадений

---

## Фаза 5: Тестирование и верификация

- [ ] Unit-тесты Spectrum
- [ ] Интеграционный тест: load_spectrum → denoise → assign → build_result_table
- [ ] Smoke-тест пайплайна на тестовых наборах
- [ ] GUI: полный цикл (загрузка CSV → анализ → визуализация)
- [ ] Сборка .exe без nomspectra в бандле

---

## Итоговая структура после замены

```
src/core/
  spectrum.py        # НОВЫЙ: свой класс Spectrum (MPL-2.0)
  spectrum_ops.py    # ОБНОВЛЁН: импорт из .spectrum, удалён assign_formulas_nomspectra
  pipeline.py        # Без изменений (уже использует assign_formulas, не nomspectra)
  mzml_bridge.py     # Без изменений
  raw_bridge.py      # Без изменений (будет заменён в external-replacement-plan)
```

---

## Оценка времени

### external/ замена (pymsfilereader → raw_thermo_adapter)

| Задача | Часов |
|--------|:---:|
| Изучение RawFileReader API | 3–4 |
| Проектирование raw_thermo_adapter | 2–3 |
| Реализация (pythonnet + CLR + .NET DLL) | 6–10 |
| Отладка интеграции (пути к DLL, ошибки CLR) | 3–5 |
| Переключение raw_bridge + тесты | 3–4 |
| Очистка external из сборок | 1–2 |
| **Итого external** | **18–28 ч** |

### nomspectra замена

| Задача | Часов |
|--------|:---:|
| Реализация своего Spectrum (класс + `noise_filter`) | 2–3 |
| Замена импортов (3 файла) | 0.5 |
| Прогон тестов + багфиксы | 3–5 |
| Удаление assign_formulas_nomspectra | 0.5 |
| Удаление nomspectra из зависимостей/сборок | 1 |
| **Итого nomspectra** | **7–10 ч** |

### Общая оценка

| Компонент | Часов |
|-----------|:---:|
| external (pymsfilereader → RawFileReader) | 18–28 |
| nomspectra (Spectrum + noise_filter) | 7–10 |
| Лицензии, CI, очистка | 4–6 |
| **Всего GPL-замена** | **29–44 часов** |

**Риски:**
- `pythonnet` + PyInstaller onefile — могут быть неожиданные проблемы (×1.5 к оценке)
- .NET CLR на чистых Windows-машинах — может потребоваться .NET Runtime (×1.2)
- Spectrum замена — низкий риск, т.к. используется только `.table` и конструктор
