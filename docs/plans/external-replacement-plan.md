# Задачи по замене external/ GPL-кода на собственный

> **Создан:** 2026-07-26 | **Статус:** 🔴 план
> **Принцип:** clean-room реализация — чтение документации ThermoFisher (RawFileReader SDK, mzML spec),
> написание с нуля без просмотра GPL-исходников `pymsfilereader.py`.

## Анализ использования

| Файл в external/ | Используется проектом? | Действие |
|------------------|----------------------|----------|
| `pymsfilereader.py` (618 строк) | ✅ Да, через `raw_bridge.py` | Написать замену с нуля |
| `gmm_filter.py` (477 строк) | ❌ Нет | Удалить из production |
| `app.py` (428 строк) | ❌ Нет (отдельный GUI-инструмент) | Удалить из production |

---

## Фаза 1: Замена pymsfilereader → raw_thermo_adapter

> **Цель:** свой модуль `src/core/raw_thermo_adapter.py`, использующий RawFileReader
> (.NET DLL) вместо MSFileReader COM. Тот же API, что у `raw_bridge.py`.

### 1.1. Изучить API RawFileReader (без просмотра GPL-кода)

- [ ] Скачать RawFileReader SDK с [GitHub ThermoFisher](https://github.com/thermofisherlsms/RawFileReader)
- [ ] Изучить `RawFileReaderExample.cs` — понять:
  - Как открыть `.raw` файл
  - Как получить список сканов (scan numbers / retention times)
  - Как прочитать спектр по номеру скана (m/z + intensity массивы)
  - Какие ещё поля доступны: resolution, baseline, noise, charge
  - Как отфильтровать сканы по RT-диапазону (start_rt / end_rt)
- [ ] Задокументировать API-контракт: методы, параметры, типы возврата

### 1.2. Спроектировать raw_thermo_adapter.py

- [ ] Определить публичный API (drop-in совместимость с `raw_bridge`):
  ```
  average_raw_to_csv(raw_path, rt_min, rt_max, output_csv, progress_callback) -> str
  average_raw_to_df(raw_path, rt_min, rt_max) -> pd.DataFrame
  is_available() -> bool
  availability_error() -> str | None
  ```
- [ ] Определить внутреннюю архитектуру:
  - `_init_clr()` — загрузка .NET CLR и 4 DLL через `pythonnet`
  - `_open_raw(raw_path)` — открытие файла
  - `_get_scans_in_rt_window(rt_min, rt_max)` — список сканов
  - `_average_scans(scan_list)` — усреднение → numpy (mass, intensity)
  - `_write_csv(mz, int, output_path)` — запись CSV
- [ ] Определить стратегию разрешения путей к DLL:
  - В режиме разработки: `os.path.dirname(__file__)/../../thermo/`
  - В PyInstaller: `sys._MEIPASS/thermo/`

### 1.3. Реализовать raw_thermo_adapter.py

- [ ] Установить `pythonnet` и 4 DLL RawFileReader в `thermo/`
- [ ] Написать `is_available()` — проверка наличия DLL + `pythonnet`
- [ ] Написать `_init_clr()` — загрузка сборок
- [ ] Написать `_open_raw()` — открытие .raw, получение числа сканов, RT-диапазона
- [ ] Написать `_average_scans()` — сбор mass/intensity по всем сканам в окне
- [ ] Написать `average_raw_to_csv()` — полный пайплайн: открыть → усреднить → CSV
- [ ] Написать `average_raw_to_df()` — обёртка над `average_raw_to_csv` + `pd.read_csv`
- [ ] Протестировать на реальном `.raw`-файле
- [ ] Обработать ошибки: DLL не найдены, файл повреждён, нет сканов в окне

### 1.4. Переключить raw_bridge.py на raw_thermo_adapter

- [ ] Удалить `import pymsfilereader`, `sys.path.insert`, `_msfr` из `raw_bridge.py`
- [ ] Заменить вызов `_msfr.PyMSFileReader` на вызов raw_thermo_adapter
- [ ] `is_available()` → прокси на `raw_thermo_adapter.is_available()`
- [ ] Обновить тесты `test_raw_bridge.py`
- [ ] Убедиться, что все существующие тесты проходят
- [ ] Обновить `pyproject.toml`: `comtypes` → `pythonnet` в зависимостях

### 1.5. Тестирование

- [ ] Unit-тест: `raw_thermo_adapter.is_available()` без DLL → False
- [ ] Unit-тест: `raw_thermo_adapter` с мокнутым CLR
- [ ] Интеграционный тест: реальный `.raw` → CSV → проверить mass,intensity строки
- [ ] Smoke-тест: CLI-запуск `python -c "from src.core.raw_thermo_adapter import ..."`
- [ ] Тест на чистой Windows-машине без Python (только .exe)

---

## Фаза 2: Удаление external/ из production

> **Цель:** external/ не попадает в `.exe`, не импортируется, не линкуется.

### 2.1. Очистка кодовой базы

- [ ] Удалить `sys.path.insert(_EXTERNAL_ROOT)` из `raw_bridge.py` (уже сделано в 1.4)
- [ ] Проверить grep-ом: `grep -rn "external/usrednenie" src/` → 0 совпадений
- [ ] Проверить grep-ом: `grep -rn "pymsfilereader" src/` → 0 совпадений
- [ ] Проверить grep-ом: `grep -rn "gmm_filter\|GMMNoiseFilter" src/` → уже 0

### 2.2. Очистка сборочных файлов

- [ ] Убрать external из `NOM_HRMS_FGA.spec` (строки datas для external)
- [ ] Убрать `comtypes` из `_collect_packages` в `.spec`
- [ ] Убрать `comtypes` из `release_exe.yml`
- [ ] Убрать `comtypes` из `requirements.txt`
- [ ] Добавить `pythonnet` в `requirements.txt`

### 2.3. Документирование external/ как legacy

- [ ] Создать `external/README_LEGACY.md` с пояснением:
  - Код был частью проекта до версии 0.5.x
  - Закрыт (GPL-3.0), удалён из production
  - Оставлен только для исторической справки
  - Не используется, не поддерживается, не включается в сборку

---

## Фаза 3: Собственная реализация GMM-фильтра (опционально)

> **Статус:** gmm_filter.py не используется проектом. Если потребуется —
> реализовать с нуля по алгоритму, а не по GPL-коду.

- [ ] Изучить алгоритм GMM-фильтрации по открытым источникам (статьи, вики)
- [ ] Спроектировать API:
  ```
  class NoiseFilter:
      def __init__(self, data: np.ndarray)
      def find_threshold(self) -> float
      def denoise(self) -> np.ndarray
  ```
- [ ] Реализовать `find_threshold()` — GMM + BIC для автоопределения порога шум/сигнал
- [ ] Реализовать `denoise()` — фильтрация по порогу
- [ ] Написать тесты на синтетических данных (известный порог)

---

## Фаза 4: Инфраструктура

- [ ] Обновить CI (`release_exe.yml`): pythonnet + RawFileReader DLL
- [ ] Обновить `.spec`: bандл `thermo/*.dll`, исключить `external/`
- [ ] Обновить `README.md`: зависимости, способ установки
- [ ] Обновить лицензионную документацию (THIRD_PARTY_NOTICES, About, EULA)

---

## Итоговая структура после замены

```
src/core/
  raw_bridge.py          # Тонкий фасад, делегирует raw_thermo_adapter
  raw_thermo_adapter.py  # НОВЫЙ: работа с RawFileReader (.NET DLL), MPL-2.0
  mzml_bridge.py         # mzML → CSV (уже готов, MPL-2.0)

thermo/                  # RawFileReader DLL (проприетарные, ThermoFisher)
  ThermoFisher.CommonCore.Data.dll
  ThermoFisher.CommonCore.RawFileReader.dll
  ThermoFisher.CommonCore.MassPrecisionEstimator.dll
  ThermoFisher.CommonCore.BackgroundSubtraction.dll

external/                # ТОЛЬКО legacy reference, исключён из сборок
  README_LEGACY.md
  _legacy_reference/     # Исходный GPL-код (историческая справка)
```

---

## Граф зависимостей задач

```
1.1 (изучить API) ──> 1.2 (спроектировать) ──> 1.3 (реализовать)
                                                        │
                                                        v
                                              1.4 (переключить raw_bridge)
                                                        │
                                                        v
                                              1.5 (тестирование)
                                                        │
                        ┌───────────────────────────────┤
                        v                               v
                  2.1 (очистка кода)              Фаза 3 (GMM, опционально)
                        │
                        v
                  2.2 (очистка сборок)
                        │
                        v
                  2.3 (документирование legacy)
                        │
                        v
                   Фаза 4 (CI, README, лицензии)
```

Фазы 1 и 2 — обязательные. Фаза 3 — опциональная. Фаза 4 — финальная.

---

## Фаза 5: C-генератор формул (опционально, после валидации на реальных данных)

> **Статус:** запланировано | **Приоритет:** низкий (после замеров на реальных образцах)

Если после Python-оптимизаций генератор формул останется узким местом на реальных
данных (>500 пиков), переписать `_generate_candidate_formulas` на C (CPython
extension) или C++ с pybind11.

### API (C-расширение)

```c
// Возвращает массив структур {int c, h, o, n; double mass}
candidates_t* generate_formulas(double mass_min, double mass_max,
                                 int c_min, int c_max,
                                 int h_min, int h_max,
                                 int o_min, int o_max,
                                 int n_min, int n_max);
```

### Ожидаемое ускорение
- Python (текущий): ~8.2s на 5 тестовых сетов
- Python (после lazy strings): ~2.0s
- C: ~0.05s (×40–160)

### Риски
- Усложнение сборки (компилятор, платформозависимость)
- Дублирование химических правил (Lewis, Senior) на двух языках
- Необходимость синхронизации конфигурации (ranges) между Python и C

**Решение:** отложить до получения стабильных замеров на реальных образцах.
