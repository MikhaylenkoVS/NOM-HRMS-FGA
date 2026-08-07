# План для следующей сессии — v0.7 реструктуризация + external

> **Создан:** 2026-08-05 | **Обновлён:** 2026-08-07 | **Статус:** 🟢 v0.7-рефакторинг завершён

## ✅ Сделано (07.08.2026)

- v0.6 задачи закрыты (progress_callback, find_series оптимизация, бенчмарк)
- app.py: 1953 → 362 строки (9 миксинов в `src/ui/_*.py`)
- Предзагрузка структур (мгновенный показ в табе «Результаты»)
- Исправлены баги импортов в `pipeline/_run.py` и `pipeline/_test.py`
- **Тесты: 318 passed.**

## ✅ Уже сделано и запушено

| Пакет | Файлов | Макс. строк | Коммит |
|--------|:---:|:---:|--------|
| `domain/` (spectrum, molecule, atoms) | 3 | 337 | eb93f95 |
| `chemistry/` (fragments, rdkit, combinations) | 4 | 566 | eb93f95 |
| `io/` (raw, mzml bridges) | 3 | 255 | eb93f95 |
| `spectrum/` (бывший spectrum_ops + noise) | 10 | 330 | 2679378 |
| `pipeline/` (бывший pipeline.py) | 6 | 544 | d1f5712 |
| Константы → `configs/constants/*.json` | 4 | — | a995ea2 |
| `FRAGMENT_LIBRARY` → `_fragment_data.py` | 1 | 266 | ea1ddac |
| GPL-3.0 → MPL-2.0 | — | — | 6da88d2 |

**Тесты: 318 passed.**

---

## ⬜ app.py → `ui/` (единственная оставшаяся задача)

### Текущее состояние

- `src/app.py` — 1862 строки, класс `App(tk.Tk)` с 50 методами
- 9 миксин-классов уже написаны и лежат в `src/ui/_*.py` (созданы скриптом `_split_app.py`, но удалены при откате)
- `src/ui/plots.py` и `src/ui/theme.py` — существуют и используются

### План действий

1. **Восстановить миксины** — запустить скрипт из `_b.py` (последняя версия в истории git):
   ```bash
   git show d1f5712:_b.py  # или пересоздать
   ```
   Либо переписать скрипт разбивки — 9 миксинов, каждый со своим `ClassMixin`:

   | Файл | Класс | Методы |
   |------|-------|--------|
   | `_log.py` | `LogMixin` | `_poll_log_queue`, `_append_log_raw`, `_log`, `_clear_log`, `_save_log`, `_set_status`, `_clear_frame` |
   | `_run.py` | `RunMixin` | `_run`, `_run_worker`, `_resolve_path`, `_on_run_success_data`, `_on_run_error_data` |
   | `_params.py` | `ParamsMixin` | `_build_params_tab`, `_build_params_files`, …, `_parse_params`, `_on_noise_method_change` |
   | `_tabs.py` | `TabsMixin` | `_build_spectra_tab`, `_build_series_tab`, …, `_build_log_tab` |
   | `_results.py` | `ResultsMixin` | `_fill_result_table`, …, `_sort_tree` |
   | `_structures.py` | `StructuresMixin` | `_load_structure_preview`, `_show_structure_preview`, `_refresh_structures_tab` |
   | `_plots.py` | `PlotsMixin` | `_plot_van_krevelen`, …, `_plot_hist` |
   | `_presets.py` | `PresetsMixin` | `_import_csv`, `_apply_preset`, …, `_export_csv` |
   | `_build.py` | `BuildMixin` | `_build_ui` |

2. **Вынести общие константы в `src/ui/_config.py`**:
   ```python
   FG = "gray20"
   _GUI_DEFAULTS = _PIPE_CFG.run_pipeline_defaults
   # и остальные, используемые в миксинах
   ```

3. **Обновить `app.py`**:
   ```python
   from src.ui._config import FG, _GUI_DEFAULTS, ...
   from src.ui._log import LogMixin
   # ... все 9 миксинов
   
   class App(tk.Tk, LogMixin, RunMixin, ResultsMixin, 
             StructuresMixin, PlotsMixin, PresetsMixin,
             ParamsMixin, TabsMixin, BuildMixin):
       # __init__ остаётся в app.py
       # pass  # все методы — из миксинов
   ```

4. **Заменить `FG` → `self.FG` или импорт из `_config`** во всех миксинах

5. **Прогнать тесты**: `python -m pytest tests/`

---

## Другие отложенные задачи

| Задача | Файл |
|--------|------|
| Прогресс-бар в pipeline | `pipeline/_run.py` — добавить 4 вызова `progress_callback` |
| Бенчмарк на реальных данных | `data/real_sets/set_01/` |
| Преконфигурированные пресеты | `configs/presets/` |
| Smoke-тест в CI | `.github/workflows/release_exe.yml` |
| Bump версии | `pyproject.toml: version = "0.7.0"` |

---

## Быстрый старт

```bash
cd C:\Users\mvs\PycharmProjects\NOM-HRMS-FGA
git pull
python -m pytest tests/ -q   # должно быть 318 passed
```

Первая команда следующей сессии: создать `src/ui/_config.py` и восстановить миксины.
