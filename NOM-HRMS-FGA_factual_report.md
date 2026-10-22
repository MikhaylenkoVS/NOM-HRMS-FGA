# Фактологический отчёт о проекте NOM-HRMS-FGA

**Объект:** https://github.com/MikhaylenkoVS/NOM-HRMS-FGA (локальная копия `C:\Users\mvs\PycharmProjects\NOM-HRMS-FGA`)
**Вершина кода:** `main` @ `30194d66eb259902bab3a36860068223dabace4c` (2026-08-19 17:58:33 +0300, «feat: headless CLI (CLI-01) (#171)»); `origin/main` совпадает с HEAD
**Дата подготовки отчёта:** 2026-10-07
**Метод:** прямое чтение кода `main` + запуск кода и тестов в локальном окружении. Каждое числовое значение либо процитировано из файла (с указанием строки), либо получено запуском (команды приведены).
**Окружение запусков:** `.venv/Scripts/python.exe` → Python 3.14.6; numpy 2.5.1, pandas 3.0.3, matplotlib 3.11.0, rdkit 2026.03.3, reportlab 5.0.0, openpyxl 3.1.5, zstandard 0.25.0, Pillow 12.3.0, pytest 9.1.1, pymzml 2.6.1, requests 2.34.2, platformdirs 4.10.0, pythonnet (clr) 3.1.0. ОС: Windows (MINGW64_NT-10.0-26300).

**Структура документа.** Часть I — фактический аудит кода (разделы «карта», «расхождения» и этапы 0–16, сводные таблицы). Часть II — уточнения, полученные от автора проекта, каноническая эталонная конфигурация, итоговые метрики, оценка влияния подтверждённых дефектов и план исправлений. Часть II имеет приоритет в вопросах «какие значения считать эталонными»; Часть I описывает фактическое состояние кода.

**Пометки достоверности:**
* «(код)» — установлено чтением файлов и/или запуском.
* «(подтв. автор)» — подтверждено автором проекта в переписке.
* **НЕ НАЙДЕНО** — в репозитории отсутствует.
* **ТРЕБУЕТ УТОЧНЕНИЯ** — однозначного ответа нет.

---

# ЧАСТЬ I. ФАКТИЧЕСКИЙ АУДИТ КОДА

## ОГЛАВЛЕНИЕ

1. [Краткая карта «Функция → статус → файл → тесты»](#карта)
2. [Расхождения между документацией и кодом](#расхождения)
3. [Этап 0. Идентификация версии](#этап-0)
4. [Этап 1. Назначение и постановка задачи](#этап-1)
5. [Этап 2. Архитектура](#этап-2)
6. [Этап 3. Входные данные](#этап-3)
7. [Этап 4. Предобработка и фильтрация шума](#этап-4)
8. [Этап 5. Назначение молекулярных формул (ядро)](#этап-5)
9. [Этап 6. Пресеты и конфигурации](#этап-6)
10. [Этап 7. Изотопное мечение](#этап-7)
11. [Этап 8. Структурный модуль и симуляции](#этап-8)
12. [Этап 9. Химические проекции и метрики](#этап-9)
13. [Этап 10. Вывод данных](#этап-10)
14. [Этап 11. Тестирование и валидация](#этап-11)
15. [Этап 12. История разработки](#этап-12)
16. [Этап 13. Зависимости, установка, воспроизводимость](#этап-13)
17. [Этап 14. Документация и литература](#этап-14)
18. [Этап 15. Ограничения, риски, открытые вопросы](#этап-15)
19. [Этап 16. Материалы для иллюстраций](#этап-16)
20. [Сводная таблица числовых параметров и констант](#сводка-числа)
21. [Сводная таблица настроек](#сводка-настройки)
22. [Что не проверено и почему](#не-проверено)
23. [Вопросы к автору проекта](#вопросы)

---

<a name="карта"></a>
## 1. КРАТКАЯ КАРТА: «Функция → статус (а/б/в/г) → файл → тесты»

Статусы: **(а)** реализовано и покрыто тестами; **(б)** реализовано без тестов; **(в)** заявлено в документации, но в коде нет; **(г)** экспериментальное / отключённое / мёртвый код.

| Функция / модуль | Статус | Файл (строки) | Тесты |
|---|---|---|---|
| `run_pipeline()` — главный конвейер | а | `src/core/pipeline/_run.py:41–520` | `tests/integration/test_pipeline_integration.py`, `tests/unit/test_pipeline.py` |
| `load_spectrum()` — загрузка CSV/XLSX/JSON | а | `src/core/spectrum/_load.py:50–134` | `tests/unit/test_load_formats.py`, `test_core_utils.py` |
| `denoise()` — обёртка шумоподавления | а | `src/core/spectrum/_denoise.py:16–47` | `tests/unit/test_denoise.py` |
| `compute_noise_threshold()` — GMM+BIC | а | `src/core/spectrum/_denoise.py:265–351` | `tests/unit/test_denoise.py` (косвенно) |
| `fit_gmm_1d()`, `bic()`, `gaussian_intersection()` | б | `_denoise.py:64–235` | прямых тестов нет |
| `assign_formulas()` — назначение CHON-формул | а | `src/core/spectrum/_assign.py:29–238` | `test_assign_formulas.py`, `test_spectrum_ops.py`, `test_nom_prioritize.py`, интеграционный |
| `_generate_candidate_formulas()` + LRU-кэш | а | `src/core/spectrum/_generate.py:21–135` | `tests/unit/test_generate_cache.py` |
| `_neutral_to_ion_mass()`, `_ion_shift()` | а | `_generate.py:138–195` | `tests/unit/test_core_utils.py` |
| `find_series()` — поиск серий метки | а | `src/core/spectrum/_series.py:48–215` | `tests/unit/test_find_series.py` (717 строк) |
| `build_result_table()` | а | `src/core/spectrum/_build.py:12–88` | интеграционный |
| `visualize_series()` | б | `src/core/spectrum/_visualize.py:18–176` | прямых тестов нет |
| `export_result_table()` — CSV/XLSX/JSON | а | `src/core/pipeline/_export.py:18–38` | `tests/unit/test_export.py` |
| `run_pipeline(test_mode=True)` + `_run_single_test_set()` | а | `_test.py:31–209`, `_test_set.py:26–403` | `tests/integration/` |
| `_verify_series_against_annotations()` | б | `_test_verify.py:8–133` | прямых тестов нет |
| `create_van_krevelen_plot()`, `NOM_REGIONS` | а | `src/core/van_krevelen.py:88–353` | `tests/unit/test_van_krevelen.py` |
| `compute_distribution_metrics()`, `aromaticity_index()`, `dbe()` | а | `src/core/statistics.py:18–129` | `tests/unit/test_statistics.py` |
| `Molecule`, `parse_formula()`, `calculate_IHD()` | а | `src/core/domain/molecule.py:6–335` | `tests/unit/test_molecule.py` |
| `Atom`, `ELEMENT_DATA` | а | `src/core/domain/atoms.py:4–173` | `tests/unit/test_atoms.py` |
| `Spectrum`, `Peak`, `noise_filter()` | а | `src/core/domain/spectrum.py:23–319` | `test_spectrum_ops.py`, `test_pipeline.py` |
| `find_fragment_combinations()`, `assemble_*` | а | `src/core/chemistry/fragment_combinations.py:14–353` | `tests/unit/test_fragment_combinations.py` |
| `FRAGMENT_LIBRARY`, `FUNCTIONAL_GROUPS` | а | `src/core/chemistry/_fragment_data.py` | `tests/unit/test_fragments.py` |
| `find_and_visualize_molecules()` | б | `src/core/chemistry/_visualize.py:13–236` | прямых тестов нет |
| `to_rdkit_mol()`, `visualize_*` (rdkit_bridge) | а | `src/core/chemistry/rdkit_bridge.py:19–328` | `tests/unit/test_rdkit_bridge.py` |
| RAW-мост (Thermo RawFileReader .NET) | б | `src/core/io/raw_thermo_adapter.py:31–262` | `tests/unit/test_raw_bridge.py` (мок) |
| mzML-мост | б | `src/core/io/mzml_bridge.py:29–231` | прямых тестов нет |
| CLI (`nom-hrms-fga-cli`) | а | `src/cli.py:74–192` | `tests/unit/test_cli.py` |
| GUI (tkinter, `App` + 8 миксинов) | б | `src/app.py:139–285`, `src/ui/_*.py` | только smoke `tests/integration/test_app_smoke.py` |
| PDF-отчёт | а | `src/core/report.py:187–273` | `tests/unit/test_report.py` |
| Batch-обработка | а | `src/core/batch.py:13–108` | `tests/unit/test_batch.py` |
| Smoke-suite (`run_smoke_suite`) | **г** (сломан вызов `assign_formulas_simple`) | `src/testing/smoke_runner.py:37–302` | `tests/integration/test_app_smoke.py` |
| `FormulaDatabaseReader`, `DatabaseManager` (Zstd CNOSP) | **г** (не интегрирован; тесты исключены из CI) | `src/core/formula_db/*.py` | `tests/unit/test_formula_db.py` (43 теста) |
| `PipelineCache`, `_result_cache` | б | `src/core/pipeline/_cache.py:9–120` | косвенно |
| `PipelineTimings`, `StageTimer` | **г** (объявлены, `run_pipeline` не использует) | `src/core/timer.py:18–60` | нет |
| `benchmark()`, `benchmark_assign()` | б | `src/core/benchmark.py`, `benchmark_assign.py` | нет |
| `generate_test_sets.py` | б | `src/sim/generate_test_sets.py:37–820` | нет |
| PubChem-скрипты | б | `src/sim/search_pubchem_nom_like_cids.py`, `process_pubchem_candidates.py` | нет |
| `src/core/spectrum_ops.py`, `src/core/pipeline.py`, `src/core/molecule.py`, `src/core/atoms.py`, `src/core/raw_bridge.py`, `src/simulations/` | **в** (упоминаются в README/docs, в коде отсутствуют) | — | — |

---

<a name="расхождения"></a>
## 2. РАСХОЖДЕНИЯ (документация ↔ код)

Проверено чтением и/или запуском (`код`), либо подтверждено автором (`подтв. автор`).

| # | Документ утверждает | Фактически в коде | Источник |
|---|---|---|---|
| R1 | `README.md:34,239`, `pyproject.toml:20` — лицензия **GPL-3.0** | `LICENSE` (363 строки) — **Mozilla Public License 2.0**; `pyproject.toml:12` `license={text="MPL-2.0"}` | код; **подтв. автор: окончательная лицензия — MPL-2.0** |
| R2 | `README.md:222` «tests/ (105 шт.)»; `CODE_AVAILABILITY.md:73` «318 tests»; `RELEASE_NOTES_v0.7.0.md:44` «419 passed» | собрано **424** теста | код |
| R3 | `README.md:150,156,169,176` — `from src.core.spectrum_ops import …`, `assign_formulas(clean, mode="simple")`, `from src.core.raw_bridge import average_raw_to_csv`, `python -m src.core.pipeline --help` | `src.core.spectrum_ops` не существует; `assign_formulas()` не принимает `mode=` (`TypeError`); модуль — `src.core.io.raw_bridge`; `python -m src.core.pipeline` → `No module named src.core.pipeline.__main__` | код (запуск) |
| R4 | `README.md:124–131`, `docs/architecture.md:18–24` — 7 вкладок GUI | вкладок 9 (Параметры, Спектры, Серии, Результаты, Van Krevelen, Гистограммы, Batch, Лог, Структуры) | `src/ui/_build.py:49–74` |
| R5 | `docs/architecture.md` (v0.5.1) описывает `src/core/pipeline.py`, `spectrum_ops.py`, `molecule.py`, `atoms.py`, `raw_bridge.py`, `src/simulations/` | переехало в `src/core/pipeline/`, `src/core/spectrum/`, `src/core/domain/`, `src/core/io/`, `src/sim/` | код |
| R6 | `docs/data_sources.md:22` — «~300 молекул» в `ref_molecules_all_pubchem_filtered.csv` | 154 строки данных | код |
| R7 | `docs/data_sources.md:64` — шум управляется `pipeline.json → test_mode → denoise` | шум захардкожен: `peak_count=500`, `intensity_fraction_max=0.1` | `generate_test_sets.py:104–107` |
| R8 | `data/README.md:29–30` — в каждом наборе есть `config.json` и `*.bak` | таких файлов нет | код (`ls`) |
| R9 | `data/README.md:29` — параметры генерации в `config.json` | `generate_test_sets.py:71–74`: «no per-set config.json is written» | код |
| R10 | `CODE_AVAILABILITY.md:33` — MPL-2.0 | совпадает с `LICENSE`, противоречит `README.md:239` | код |
| R11 | `docs/user_guide.md:3` — «Версия 0.6.0» | `src/__init__.py:3` = `0.7.0` | код |
| R12 | `.zenodo.json` — `"version": "0.6.0"` | `pyproject.toml:7`, `CITATION.cff:14` = `0.7.0` | код |
| R13 | `.zenodo.json` ORCID `0000-0001-7545-6275` | `CITATION.cff` ORCID `0000-0000-0000-0000`, DOI `10.XXXX/zenodo.YYYYY` (плейсхолдеры) | код; **подтв. автор: появятся** |
| R14 | `README.md:102` — `python -m src.core.pipeline --help` | рабочая точка входа — `python -m src.cli` / `nom-hrms-fga-cli` | код (запуск) |
| R15 | `docs/architecture.md:150` — «105 тестов, ~2 мин» | 424 теста, 26.15 с | код |
| R16 | сторонние skill-документы: `noise_force=10`, `noise_intensity=100` в `run_pipeline_defaults` | `noise_force=2.0`, `noise_intensity=null` | код |
| R17 | `THIRD_PARTY_NOTICES.md:42` перечисляет `scipy` | `scipy` нет в зависимостях и в коде (только `tools/NOM_HRMS_FGA.spec:45`) | код |
| R18 | `README.md:107` — требуется MSFileReader 3.1 SP4 | используется RawFileReader .NET; COM/MSFileReader удалён | код + git log |
| R19 | `README.md:190` — `pytest -m unit` = «только unit-тесты» | маркер `unit` стоит на 24 из 424 → `24 passed, 400 deselected` | код (запуск) |
| R20 | `docs/architecture.md:71`, `src/README.md:27` — «ключевой модуль core/pipeline.py» | `src/core/pipeline/` — пакет, ключевой модуль — `_run.py` | код |
| R21 | `external/README.md:8–9,22–24` — «GPL-3.0 основного проекта» | основная лицензия MPL-2.0; формулировка внутренне противоречива | код |
| R22 | skill-документы `.deepcode/skills/*` описывают `spectrum_ops.py:607–812`, `**kwargs`, конверсию `sign`→`ion_mode` в `run_pipeline`, `noise_force=10` | ничего из этого в коде нет | код |
| R23 | — (ответ автора: стандартные диапазоны **C4–40, H0–100, O0–12, N0–12**) | ни один из трёх наборов диапазонов в репозитории не совпадает с заявленным | код; подтв. автор |
| R24 | GUI/CLI/пресеты позиционируют диапазоны элементов как настраиваемые | `brutto_dict` не передаётся в `assign_formulas`; результат идентичен при `C:1-1` и `C:1-50` | код (запуск); **подтв. автор: дефект** |
| R25 | `formula_search.max_hc/max_oc/max_nc/max_dbe` | не применяются и нигде не переопределены; фактически действуют недокументированные soft-пороги 20 (DBE), 0.3 (N/C), N>3 | код (grep); **подтв. автор: должны быть soft-фильтрами, пороги — из конфига** |
| R26 | — | DBE в скоринге: `1 + C − H/2 + O/2` вместо `+ N/2` | `_assign.py:150`; **подтв. автор: дефект** |
| R27 | `thresholds.max_wrong_ratio = 0.15` считается выполненным (CI зелёный) | каноническая метрика (общий знаменатель) даёт 51.6–71.0 % для dacet на всех 5 наборах; интеграционный тест использует неканоническую методику | код (запуск); **подтв. автор: знаменатель — общий** |
| R28 | `CITATION.cff` ORCID/DOI, `.zenodo.json` version, classifier MPL | плейсхолдеры и устаревшая версия | код; подтв. автор |
| R29 | — | источник моноизотопных масс и коэффициентов Бейнона в репозитории не указан | код; **подтв. автор: не подтверждены / неизвестен** |
| R30 | эталонный прогон воспроизводится штатной точкой входа | `python -m src.core.pipeline._test --test` и `run_pipeline(test_mode=True)` подставляют `rel_error=1.0`, `ppm_tol=5.0`, окно 0/1000 вместо `test_mode` (0.5/0.5/None/None) | код (запуск); каноничность параметров подтв. автором |

---

<a name="этап-0"></a>
## ЭТАП 0. ИДЕНТИФИКАЦИЯ ВЕРСИИ

### 0.1. Ветка и последний коммит

| Параметр | Значение | Команда |
|---|---|---|
| Ветка рабочего дерева | `test_ai_orchestrator` | `git branch --show-current` |
| HEAD | `30194d66eb259902bab3a36860068223dabace4c` | `git rev-parse HEAD` |
| `origin/main` | тот же SHA | `git rev-parse origin/main` |
| Дата / автор / сообщение | 2026-08-19 17:58:33 +0300, Vladimir S. Mikhaylenko, `feat: headless CLI (CLI-01) (#171)` | `git log -1` |

Более новых коммитов в `origin/main` нет. Код рабочего дерева == код `main`.

### 0.2. Теги

| Тег | Дата | Commit |
|---|---|---|
| v0.3.0 | 2026-06-19 17:49:19 +0300 | 58b1999 |
| v0.3.1 | 2026-06-21 20:25:10 +0300 | e8131f0 |
| v0.3.2 | 2026-07-07 17:38:22 +0300 | 5bd961d |
| v0.4.0 | 2026-07-08 11:48:39 +0300 | 14f42d5 |
| v0.4.1 | 2026-07-12 00:03:27 +0300 | 310cbba |
| v0.4.2 | 2026-07-12 08:21:12 +0300 | 6b22c84 |
| v0.5.0 | 2026-07-13 11:42:16 +0300 | 5513ecf |
| v0.5.1 | 2026-07-20 15:01:53 +0300 | 1ccfec4 |
| v0.5.2 | 2026-07-20 15:15:05 +0300 | abdf011 |
| v0.6.0 | 2026-08-07 19:19:11 +0300 | e62476b |
| v0.6.1 | 2026-08-15 16:22:05 +0300 | eeca717 |
| v0.7.0 | 2026-08-19 15:30:50 +0300 | 38e6f25 |

Тегов v0.1.x/v0.2.x нет. Release notes есть для v0.5.0, v0.5.1, v0.5.2, v0.6.1, v0.7.0; для v0.3.x–v0.4.x — **НЕ НАЙДЕНО**. GitHub Releases локально недоступны — **ТРЕБУЕТ УТОЧНЕНИЯ**.

### 0.3. Версия в файлах

| Файл | Версия |
|---|---|
| `pyproject.toml:7` | `0.7.0` |
| `src/__init__.py:3` | `0.7.0` |
| `CITATION.cff:14` | `0.7.0`, date-released 2026-08-19 |
| `.zenodo.json` | `0.6.0` (расхождение) |
| `docs/user_guide.md:3` | «0.6.0» (расхождение) |

### 0.4. Объём истории

| Метрика | Значение | Команда |
|---|---|---|
| Всего коммитов в HEAD | **254** | `git rev-list --count HEAD` |
| Merge-коммитов | 30 | `git log --merges --oneline \| wc -l` |
| Первый коммит | `b30b609`, 2026-06-11 21:28:59 +0300, `init: базовая структура проекта NOM` | — |
| Период разработки | 2026-06-11 → 2026-08-19 (≈2,3 мес.) | — |
| PR, упомянутые в сообщениях | #2, #3, #5–#7, #9–#11, #13–#15, #17, #22, #27–#34, #36, #40, #47, #48, #51, #59, #60, #62, #64, #68, #69, #71, #73–#88, #96, #159–#171 | `git log --format=%s%n%b \| grep -oE "#[0-9]+"` |
| Авторы | V. Mikhaylenko 249 коммитов; Vladimir S. Mikhaylenko 29; dependabot[bot] 3; MikhaylenkoVS 2; mikhaylenovs-droid 2+1 | `git shortlog -sne --all` |

### 0.5. Статистика кода

| Метрика | Значение |
|---|---|
| Всего `.py` (src+tools+tests+external) | 128 |
| LOC `src/` | **15 898** |
| LOC `src/core` (52 файла) | 9 484 |
| LOC `src/ui` (14) | 2 636 |
| LOC `src/structures` (4) | 749 |
| LOC `src/sim` (4) | 1 504 |
| LOC `src/testing` (5) | 824 |
| LOC `src/configs` (4) | 202 |
| LOC `tests/` (33 файла) | 6 188 |
| LOC `tools/` (5) | 2 095 |
| LOC `external/` (3) | 1 523 |
| Тестов собрано pytest | 424 |
| Отслеживаемых git-файлов | 380 |

Языки: Python, JSON, Markdown, CSV, .dll, .ico, .png, .fdb. Других языков **НЕ НАЙДЕНО**.

Крупнейшие файлы: `tools/ai_workflow.py` 1 620; `src/sim/generate_test_sets.py` 820; `tests/unit/test_find_series.py` 717; `tests/integration/test_pipeline_integration.py` 584; `tests/unit/test_core_utils.py` 573; `src/core/pipeline/_run.py` 520; `src/ui/_params.py` 423.

### 0.6. Лицензии

| Компонент | Лицензия | Источник |
|---|---|---|
| Основной код | **MPL-2.0** | `LICENSE` (363 строки), `pyproject.toml:12`, `CODE_AVAILABILITY.md:33`; подтв. автор |
| Метаданные PyPI | `license={text="MPL-2.0"}`, classifier `GPL-3.0 License` (ошибка) | `pyproject.toml:12,20` |
| `external/usrednenie_spectrov_i_hromatogramm/` | **GPL-3.0** | `external/README.md:16`, `…/LICENSE.txt` |
| `thermo/*.dll` (Thermo RawFileReader v5, 4 файла) | проприетарная: некоммерческое использование, запрет распространения и реверс-инжиниринга | `THIRD_PARTY_NOTICES.md:3–25` |
| Зависимости | NumPy BSD-3, pandas BSD-3, matplotlib PSF, RDKit BSD-3, Pillow MIT-CMU, pythonnet MIT, pymzml MIT | `THIRD_PARTY_NOTICES.md:34–43` |
| Не указаны в notices | `reportlab` (BSD-3), `zstandard` (BSD/GPLv2 dual), `openpyxl` (MIT), `pytest` (MIT), `platformdirs` (MIT), `requests` (Apache-2.0) | **НЕ НАЙДЕНО** |

Артефакт: `Документация/LICENSE` — 35 823 байта (текст GNU GPLv3), тогда как корневой `LICENSE` — 15 506 байт (MPL-2.0); это копия до релицензирования.

---

<a name="этап-1"></a>
## ЭТАП 1. НАЗНАЧЕНИЕ И ПОСТАНОВКА ЗАДАЧИ

### 1.1. Заявленная задача (дословно)

`README.md:1–7`:
> «NOM-HRMS Functional-Group Analyzer — Инструмент для расшифровки масс-спектров природного органического вещества (NOM) по данным HPLC-HRMS с дериватизацией дейтерометилированием и дейтероацилированием. Определяет брутто-формулы, строит диаграммы Ван-Кревелена, находит гомологические серии и подсчитывает количество функциональных групп (-COOH, -OH) на молекулу.»

`CODE_AVAILABILITY.md:14–21`:
> «…combines selective chemical derivatization with isotope labelling — deuteromethylation of carboxyl groups (–COOH → –COOCD₃, mass increment DELTA_CD3 = 17.03448 Da per group) and deuteroacylation of hydroxyl groups (–OH → –OCOCD₃, mass increment DELTA_CD3CO = 45.02939 Da per group) — to count functional groups, assign molecular formulas in negative ion mode ([M–H]⁻), and enumerate candidate molecular structures.»

### 1.2. Задача фактически по коду

`run_pipeline()` (`_run.py:41–520`): загрузка 3 спектров → шумоподавление каждого → назначение брутто-формул CHON исходному спектру → поиск «серий» `m₀ + k·Δ` в двух дериватизированных спектрах (`n_groups` = число прореагировавших групп) → сборка таблицы `N_COOH` (ΔCD3), `N_OH` (ΔCD3CO) → опционально графики → экспорт CSV/XLSX/JSON.

### 1.3. Объекты анализа

* Тип образца — только через пресет (`soil`, `water`, `peat`, `coal`); иной химической специализации объекта в коде нет.
* Ионизация: **только отрицательная [M–H]⁻** (`chemistry.json → default_ion_mode`). Ветки `[M]+`, `[M+H]+`, `neutral` формально существуют (`_generate.py:160–178`), но недостижимы из конвейера. **Подтв. автор: положительный режим сейчас не поддерживается, будет исправлен к релизу для статьи.**
* Тип прибора в коде не различается. Для `.raw` — Thermo RawFileReader; для `.mzML` — pymzml.

### 1.4. Вход / выход

* Вход: 3 файла-спектра (`.csv/.xlsx/.xls/.json/.raw/.mzML`), столбцы `mass`/`intensity`.
* Выход: DataFrame `mass, intensity, brutto, all_candidates, N_COOH, N_OH, missing_dmet, missing_dacet` → CSV (`;`, `utf-8-sig`)/XLSX/JSON, опционально PNG и PDF.

### 1.5. Экспериментальные методики

| Методика | Поддержка |
|---|---|
| Прямой ввод / HPLC-HRMS | да (CSV/RAW/mzML; RT-окно) |
| Дейтерометилирование → –COOCD₃ | да, Δ = 17.03448 Da (`DELTA_CD3`) |
| Дейтероацилирование → –OCOCD₃ | да, Δ = 45.02939 Da (`DELTA_CD3CO`) |
| HDX (H→D) | **НЕ НАЙДЕНО** (нет константы 1.00628 и алгоритма) |
| CD₃OD/SOCl₂, CF₃COOH, иные метки | **НЕ НАЙДЕНО** |

### 1.6. «Расшифровка» vs «структурная часть»

* Назначение формул — `_assign.py` + `_generate.py`.
* Структурная часть — `src/core/chemistry/` (комбинаторика фрагментов, библиотека, сборка графа, RDKit-отрисовка) + GUI-вкладка `src/structures/`.
* Связь: `find_and_visualize_molecules(brutto, num_cooh=N_COOH, num_oh=N_OH)` (`src/ui/_structures.py:91–98`, `src/structures/tab.py:199–205`).

### 1.7. Аналоги

| Аналог | Где упомянут | Отличие |
|---|---|---|
| NOMspectra (kozelkov-ie/NOMspectra, GPLv3) | `docs/plans/nomspectra-replacement-plan.md`, `README.md:244` | Полностью удалён; собственные `Spectrum`, GMM+BIC, `assign_formulas` (коммиты `434e325`, `4d41c78`, `1bf8948`, `6da88d2`). В коде отсутствует |
| `external/usrednenie_spectrov_i_hromatogramm` (GPL-3.0) | `external/README.md`, `docs/plans/external-replacement-plan.md:12` | Не вызывается из production-кода |
| UltraMassExplorer, Transhumus, MAYGEN | **НЕ НАЙДЕНО** |
| MFAssignR, ICBM-OCEAN, Formularity, CoreMS | только в `docs/Библиография…` |
| GMM-фильтр шума | `_denoise.py` (собственная clean-room реализация EM+BIC) |

**Вывод:** заявленных числовых сравнений с внешними инструментами в репозитории **НЕ НАЙДЕНО**. **Подтв. автор: данных сравнения нет.**

---

<a name="этап-2"></a>
## ЭТАП 2. АРХИТЕКТУРА

### 2.1. Дерево каталогов (до глубины 3)

```
NOM-HRMS-FGA/
├── src/
│   ├── __init__.py            __version__ = "0.7.0"        (L1–4)
│   ├── __main__.py            python -m src → src.app.main (L1–6)
│   ├── app.py                 App(tk.Tk, 8 миксинов) + main (L1–301)
│   ├── cli.py                 headless CLI (L1–192)
│   ├── configs/
│   │   ├── chemistry.json     массы, сдвиги, ion_mode
│   │   ├── pipeline.json      параметры/пороги
│   │   ├── paths.json         пути и имена файлов
│   │   ├── loader.py          ConfigNamespace + lru_cache (L1–136)
│   │   ├── presets_loader.py  list_presets/load_preset (L1–37)
│   │   ├── constants/         noise.json, isotope.json, spectrum_load.json, formula_search.json
│   │   └── presets/           coal.json, peat.json, soil.json, water.json
│   ├── core/
│   │   ├── __init__.py        публичный API ядра (L1–51)
│   │   ├── _safety.py         safe(), _safe_df() (L15–35)
│   │   ├── batch.py           detect_sample_triples/… (L1–108)
│   │   ├── benchmark.py       прогон на real_sets (L1–64)
│   │   ├── benchmark_assign.py бенч assign+генератора (L1–71)
│   │   ├── report.py          PDF-отчёт (L1–273)
│   │   ├── statistics.py      H/C, O/C, DBE, AI, гистограммы (L1–129)
│   │   ├── timer.py           StageTimer/PipelineTimings (L1–60)
│   │   ├── van_krevelen.py    NOM_REGIONS + график (L1–354)
│   │   ├── chemistry/         _fragment, _fragment_data, _factories, _functional,
│   │   │                      fragments, fragment_combinations, rdkit_bridge, _visualize
│   │   ├── domain/            atoms.py, molecule.py, spectrum.py
│   │   ├── formula_db/        _packed, _builder, _reader, _manager, __main__
│   │   ├── io/                raw_bridge, raw_thermo_adapter, mzml_bridge
│   │   ├── pipeline/          _run, _stages, _helpers, _stats, _cache, _export,
│   │   │                      _test, _test_set, _test_verify
│   │   └── spectrum/          _constants, _chem, _generate, _assign, _denoise,
│   │                          _load, _series, _build, _visualize
│   ├── structures/            tab.py, widgets.py, rdkit_utils.py
│   ├── sim/                   generate_test_sets.py, search_pubchem_nom_like_cids.py,
│   │                          process_pubchem_candidates.py
│   ├── testing/               smoke_runner.py, artifact_export.py,
│   │                          report_models.py, structure_export.py
│   └── ui/                    _build, _config, _deps, _log, _params, _plots, _presets,
│                              _results, _run, _structures, _tabs, plots.py, theme.py
├── tests/                     conftest.py, unit/ (31 файл), integration/ (3 файла)
├── tools/                     ai_workflow.py, build_exe.py, launcher.py,
│                              run_benchmark.py, NOM_HRMS_FGA.spec
├── thermo/                    4 DLL Thermo RawFileReader
├── external/                  usrednenie_spectrov_i_hromatogramm/ (GPL-3.0)
├── data/                      ref_data/, test_sets/set_01..05/, formula_db/, real_sets/set_01 (пусто)
├── assets/                    icon.ico
├── docs/                      25 файлов .md + plans/
├── Документация/              устаревшая копия репозитория + Документация.zip
├── .github/                   workflows (6), ISSUE_TEMPLATE, CODEOWNERS, dependabot.yml
├── .ai/                       workflow.md, ADR-0001, contracts, prompts, tasks, baselines
├── .deepcode/                 SKILL.md (в т.ч. 6 скиллов проекта)
├── build/, dist/              артефакты PyInstaller (в .gitignore); dist/NOM_HRMS_FGA.exe 128 087 430 Б (2026-07-20)
├── pyproject.toml, requirements.txt, pytest.ini, .flake8, .pre-commit-config.yaml
├── LICENSE (MPL-2.0), THIRD_PARTY_NOTICES.md, CITATION.cff, .zenodo.json, CODE_AVAILABILITY.md
├── README.md, AGENTS.md, CONTRIBUTING.md, .gitignore, .aiignore
└── test_sets.zip, Документация.zip, AI_AUDIT_HANDOFF.md, deepcode_audit_triage.md
```

Неотслеживаемые локальные файлы (`git status` → `??`): `.aiignore`, `AI_AUDIT_HANDOFF.md`, `deepcode_audit_triage.md`. Локально также присутствуют `data/test_sets/set_*/report.pdf` (игнорируются `.gitignore:60`, в `main` отсутствуют).

### 2.2. Поток данных (с именами функций)

```
ВХОД (3 файла)
  src/core/io/raw_bridge.average_raw_to_json()   .raw  → JSON  (Thermo RawFileReader)
  src/core/io/mzml_bridge.mzml_to_json()         .mzML → JSON  (pymzml + ручное декодирование)
        ↓
1. _stages._load_triple()  →  spectrum._load.load_spectrum() × 3
        ↓
2a. _stages._denoise_triple() → spectrum._denoise.denoise()
        → Spectrum.noise_filter()  (domain/spectrum.py:285–319)
        → _denoise.compute_noise_threshold() → fit_gmm_1d() + bic() + gaussian_intersection()
        (src_original = src.copy() только при isotope_filter=True)
        ↓
2b. spectrum._assign.assign_formulas()
        → _generate._generate_candidate_formulas() → _generate._generate_cached() [lru_cache]
        → _chem.exact_mass_from_counts(), _chem.dbe_from_counts()
        → _generate._ion_shift() / _neutral_to_ion_mass()
        → скоринг: _chem._NOM_REGION_CENTERS, penalties, _chem._measure_m1_ratio()
        ↓
3. _stages._find_series_stage()  →  spectrum._series.find_series(src, dmet, DELTA_CD3)
4. _stages._find_series_stage()  →  spectrum._series.find_series(src, dacet, DELTA_CD3CO)
        → _series._find_peak() [ppm-поиск], _chem._counts_to_str(), parse_formula()
        ↓
5. spectrum._build.build_result_table()  (merge по mass.round(4))
        ↓
6. опц.: spectrum._visualize.visualize_series()   (только строки с пропусками)
7. опц.: van_krevelen.create_van_krevelen_plot()
8. экспорт: pipeline._export.export_result_table()
```

В тест-режиме (`test_mode=True`) — `_test._run_test_mode()` → `_test_set._run_single_test_set()` → `_test_verify._verify_series_against_annotations()`.

### 2.3. Граф зависимостей

* `src/configs` — базовый слой (stdlib), импортируется почти везде.
* `src/core/domain` ← numpy/pandas; `molecule.py` лениво импортирует rdkit и `configs.CHEM`.
* `src/core/spectrum` → `core/domain`, `core/van_krevelen` (центры NOM-областей), `configs`.
* `src/core/pipeline` → `core/spectrum`, `core/van_krevelen`, `core/timer`, `configs`.
* `src/core/chemistry` → `core/domain`; rdkit — ленивый, кроме `_visualize.py:5`.
* `src/sim` → `configs`, `core/domain`; лениво `pubchempy`, rdkit.
* `src/testing` → `core`, `configs`.
* `src/ui` → `core` через `src/ui/_deps.py` (единая точка с fallback), `configs`.
* `src/structures` → `src/ui`, `src/core` (через `..core`).
* `src/app.py` → `_deps`, 8 миксинов, `structures/tab`, `ui/theme`.
* `src/cli.py` → `presets_loader`, `core` (ленивый), `core.io.*` (ленивый).

Циклических импортов не обнаружено (все тесты и CLI запускаются).

### 2.4. Точки входа и публичный API

| Точка входа | Объявление | Что запускает |
|---|---|---|
| `nom-hrms-fga` | `pyproject.toml:47` → `src.app:main` | GUI |
| `nom-hrms-fga-cli` | `pyproject.toml:48` → `src.cli:main` | headless CLI |
| `python -m src` | `src/__main__.py:3–5` | GUI |
| `python -m src.cli` | `src/cli.py:190` | CLI |
| `python -m src.core.pipeline._test --test` | `_test.py:216–233` | тест-режим 5 наборов |
| `python -m src.core.formula_db build` | `src/core/formula_db/__main__.py` | сборка .fdb |
| `python -m src.core.benchmark <dir>` | `benchmark.py:60–64` | бенчмарк |
| `python -m src.core.benchmark_assign` | `benchmark_assign.py:65–71` | бенчмарк assign |
| `python -m src.sim.generate_test_sets` | `generate_test_sets.py:818–820` | генерация тест-сетов |
| `python tools/build_exe.py` | `build_exe.py:198` | сборка .exe |
| `python tools/ai_workflow.py` | `ai_workflow.py` | AI-workflow CLI |
| `python -m src.core.pipeline` | — | **НЕ РАБОТАЕТ** (нет `__main__`) |

Публичный API ядра — `src/core/__init__.py:1–51` (полный перечень: `Atom`, `Hybridization`, `ELEMENT_DATA`, `MoleculeFragment`, `FRAGMENT_LIBRARY`, `FUNCTIONAL_GROUPS`, `ALL_FRAGMENTS`, `find_fragment_combinations`, `assemble_all_combinations`, `assemble_molecule_from_combination`, `filter_fragments`, `find_and_visualize_molecules`, `Molecule`, `run_pipeline`, `NOM_REGIONS`, `compute_van_krevelen_data`, `create_van_krevelen_plot`, `compute_distribution_metrics`, `create_histograms_plot`, `aromaticity_index`, `dbe`, `detect_sample_triples`, `compute_sample_summary`, `build_batch_summary`, `generate_pdf_report`, `load_spectrum`, `denoise`, `find_series`, `assign_formulas`, `build_result_table`, `visualize_series`, `DELTA_CD3`, `DELTA_CD3CO`, `to_rdkit_mol`, `visualize_fragment`, `visualize_fragments_grid`, `visualize_connection_sequence`, `print_molecule_info`).

`src/core/spectrum/__init__.py:40–75` экспортирует и приватные имена: `_generate_candidate_formulas`, `_neutral_to_ion_mass`, `_ion_shift`, `_beynon_m1_ratio`, `_measure_m1_ratio`, `_nom_distance`, `_counts_to_str`, `_row_to_brutto`, `_find_peak`, `_FS_RANGES`, `_FS_ELEMENTS`, `_FORMULA_SEARCH`, `DEFAULT_BRUTTO_DICT`.

### 2.5. Модель данных

**`src/core/domain/spectrum.py`**

| Класс | Тип | Поля |
|---|---|---|
| `Peak` | `@dataclass(frozen=True, slots=True)` L23–54 | `mass: float`, `intensity: float`, `resolution`, `baseline`, `noise`, `charge`, `rt`, `scan_number` |
| `SpectrumMetadata` | `@dataclass` L62–75 | `source_path`, `sample_name`, `rt_window: tuple[float,float]\|None`, `instrument`, `ion_mode`, `file_format`, `scan_count` |
| `Spectrum` | `__slots__ = ("_peaks","_table_cache","metadata")` L83–319 | хранение `tuple[Peak,...]`; `.table` (DataFrame, свойство+сеттер), `.mass`, `.intensity`, `.n_peaks`, `.peaks`; `copy()`, `noise_filter()` |

**`src/core/spectrum/_constants.py`**: `@dataclass(slots=True) FormulaSearchConfig` L40–86 (`elements`, `ranges`, `max_hc`, `max_oc`, `max_nc`, `max_dbe`, `min_c`).

**`src/core/pipeline/_stats.py`**: `SeriesStats` (L11), `@dataclass(slots=True) PipelineStats` (L29–68), `PipelineRunResult` (L71–87: `table`, `stats`, `messages`), `TestSetResult` (L95–149: счётчики + свойства `denoise_recall`, `assign_recall`).

**`src/core/formula_db/_reader.py`**: `@dataclass(slots=True) SearchResult` L34–40.

**Итоговая таблица pandas** (`_build.py:73–88`), порядок столбцов:

| Столбец | Тип | Единицы | Обязателен |
|---|---|---|---|
| `mass` | float | Da (m/z) | да |
| `intensity` | float | у.е. | да |
| `brutto` | str | — (Hill-порядок C,H,O,N) | да (может быть пусто) |
| `all_candidates` | list[str] | — | да |
| `N_COOH` | int (из `n_groups`) | шт. | да |
| `N_OH` | int (из `n_groups`) | шт. | да |
| `missing_dmet` | list[int] | номера шагов | да |
| `missing_dacet` | list[int] | номера шагов | да |

Промежуточно `Spectrum.table` после `assign_formulas` содержит `assign: bool`.

**`find_series` результат** (`_series.py:205–215`): `mass_src`, `brutto`, `n_groups`, `steps_found`, `missing`, `series_mz`.

### 2.6. Паттерны

* **Конфигурация:** единый загрузчик `configs/loader.py` с `@lru_cache` и `ConfigNamespace`; пути резолвятся от `Path(__file__).parent` (L24, L111).
* **Предустановки:** JSON в `configs/presets/`; загрузка без схемы и валидации.
* **Плагины/мосты:** `io/raw_bridge.py` (фасад) + `io/raw_thermo_adapter.py`, `io/mzml_bridge.py`, `chemistry/rdkit_bridge.py`, `ui/_deps.py` (fallback-импорты).
* **Обработка ошибок:** `try/except Exception` с накоплением в `PipelineRunResult.messages`; каждый этап обёрнут отдельно (`_stages.py:29–79, 102–141`).
* **Логирование:** `logging.getLogger(__name__)`; в GUI — `_QueueWriter` (Tk-очередь, `src/ui/_log.py`), `_poll_log_queue`.
* **Многопоточность:** GUI запускает пайплайн в `threading.Thread(daemon=True)` (`_run.py:171–176`); структуры — в фоне (`_structures.py:44–49, 139–144`). Мультипроцессинга **НЕ НАЙДЕНО**. `concurrent.futures` — только `structure_export.py:15` (ThreadPoolExecutor, таймаут 20 с).
* **Кэширование:** `_generate_cached` (`@lru_cache(maxsize=16)`) и `_result_cache`/`PipelineCache`; ключ — `hash(tuple(параметров))`; живёт в памяти процесса.

### 2.7. GUI vs CLI

| Возможность | GUI | CLI |
|---|---|---|
| Загрузка 3 спектров | да, диалоги, RT-поля | да, `--input/--dmet/--dacet` |
| RAW/mzML | да, RT из GUI | да, RT жёстко 0.0–999.0 (`cli.py:66,70`) |
| Пресеты | выпадающий список + «Применить» | `--preset` |
| Диапазоны элементов | 8 полей → `brutto_dict` | `--element-ranges` |
| Изотопный фильтр | чекбокс | `--isotope-filter` |
| Выход | CSV/XLSX/JSON + PDF | `--output` (CSV/XLSX/JSON) |
| Визуализация | вкладки Спектры/Серии/Van Krevelen/Гистограммы, PNG/SVG | **нет** |
| Batch | вкладка Batch | **нет** |
| Структуры (RDKit) | вкладка + превью + экспорт .mol/.png | **нет** |
| PDF-отчёт | да | **нет** |
| Импорт результата из CSV/XLSX | да | — |
| Прогресс | прогрессбар из `progress_callback` | текст в stderr |
| Коды возврата | — | 0 успех / 1 ошибка |

### 2.8. Внешние исполняемые компоненты

* **Thermo RAW** (`io/raw_thermo_adapter.py`): Windows + pythonnet + 4 DLL в `thermo/` + .NET Framework ≥ 4.7.1. `is_available()` (L61–85) проверяет DLL и импорт `clr`/`System`. В PyInstaller — `sys._MEIPASS/thermo` (L31–35). Усреднение — `Extensions.AverageScansInScanRange` с `ToleranceUnits.ppm`, `Tolerance = 5.0` (L202–204). RT→скан — бинарный поиск `_scan_at_rt` (L233–256).
* **mzML** (`io/mzml_bridge.py`): pymzml только для XML; бинарные массивы декодируются вручную (`base64`+`zlib`, 32/64-бит, L29–45). Profile-режим центроидируется локальными максимумами (L48–65). Усреднение — округление m/z до 5 знаков и суммирование (L195–198).
* **Отсутствие вендорских библиотек:** `is_available()=False` + текст ошибки; GUI — `RuntimeError` с инструкцией (`_run.py:84–88`), CLI — сообщение и код 1 (`cli.py:150–152`).

---

<a name="этап-3"></a>
## ЭТАП 3. ВХОДНЫЕ ДАННЫЕ

### 3.1. Поддерживаемые форматы

Формат определяется по расширению (`_load._read_table`, L27–47):

| Расширение | Метод | Примечание |
|---|---|---|
| `.csv` | `pd.read_csv(path, sep=sep, encoding="utf-8")` | `sep` по умолчанию `,`; GUI: `\t`/`tab`/`TAB` → символ табуляции (`_params.py:346–348`) |
| `.xlsx`, `.xls` | `pd.read_excel(path)` | openpyxl |
| `.json` | `pd.read_json(path, orient="records")` | строки `{mass,intensity}` |
| `.raw` | `raw_bridge.average_raw_to_json` | Windows + DLL |
| `.mzML`/`.mzml` | `mzml_bridge.mzml_to_json` | требует pymzml |
| `.txt` | — | предлагается в GUI-диалоге (`_params.py:289`), читается как CSV — **ТРЕБУЕТ УТОЧНЕНИЯ** |

Десятичный разделитель не параметризован (`decimal='.'`). Поддержки запятой как десятичного знака **НЕ НАЙДЕНО**.

### 3.2. Столбцы и синонимы

`CSV_COLUMN_MAPPER` (`_load.py:15–24`), захардкожен:

```python
{"m/z": "mass", "M/Z": "mass", "mz": "mass", "mass": "mass",
 "Intensity": "intensity", "I": "intensity", "int": "intensity", "Int": "intensity"}
```

* Регистр/пробелы: применяется только `strip()` по краям (L101). `"MASS"`, `"m/z "` (с внутренним пробелом) не сопоставятся.
* Обязательные столбцы после переименования: `mass`, `intensity`; иначе `KeyError` (L115–121).
* Переданный `mapper` перекрывает дефолт (`_load_triple` передаёт `{"mass":"mass","intensity":"intensity"}`, L28).
* `configs/constants/spectrum_load.json` (с `resolution`, `baseline`, `noise`, `charge`, `retention_time`, `scan_number`) **не используется**: `SPECTRUM_LOAD_CFG` импортирован в `_load.py:9` и нигде не читается.

### 3.3. Специфика RAW/mzML

| Аспект | RAW | mzML |
|---|---|---|
| Диапазон RT | параметр (CLI: 0.0–999.0 мин) | аналогично |
| Выбор сканов | диапазон по RT → первый/последний скан | `ms level == 1` + RT-окно (сек) |
| Уровень MS | не фильтруется явно | только MS1 |
| Центроидирование | `HasCentroidStream` → `CentroidScan`, иначе `SegmentedScan` | profile → локальные максимумы; centroided — как есть |
| Полярность | **не фильтруется и не читается** | **не фильтруется** |
| Усреднение | `AverageScansInScanRange` (5 ppm) | sum по m/z, округлённым до 5 знаков |

### 3.4. Входные файлы режимов метки

* CLI: `--dmet` — дейтерометилированный спектр, `--dacet` — дейтероацилированный (`cli.py:87–88`). Отдельных аннотаций/флагов степени замещения во входе нет.
* Сопоставление с родительским спектром — по массе: для каждого назначенного пика ищется пик в дериватизированном на `m₀_theor + k·Δ` (`find_series`). `m₀_theor` вычисляется из брутто-формулы; при расхождении с наблюдённой > 0.001 отн. берётся наблюдённая (`_series.py:148–159`).

### 3.5. Проверки корректности входа

| Проверка | Реализована | Где |
|---|---|---|
| Пустой файл / нет столбцов | да (`KeyError`) | `_load.py:115–121` |
| Нет пиков в m/z-окне | да (`ValueError`) | `_load.py:127–131` |
| Strip заголовков | да | `_load.py:101` |
| NaN в mass/intensity | **нет** явной проверки | `_load.py:125` |
| Отрицательные интенсивности | **нет** | — |
| Дубликаты m/z | **нет** дедупликации | — |
| Неотсортированность | не требуется | `_build.py:86` |
| Неверные единицы | **нет** | — |
| Наличие файла | CLI: `Path(path).exists()` (`_run.py:167–171`); GUI: `os.path.isfile` | — |
| NaN перед расчётом ppm | проверки нет | `_assign.py:193` |

### 3.6. Примеры входных файлов

`data/test_sets/set_01..set_05` — все файлы отслеживаются git:

| Набор | original | deutermethylated | deuteroacylated | annotations | molecules |
|---|---|---|---|---|---|
| set_01 | 531 | 569 | 548 | 1648 | 31 |
| set_02 | 531 | 567 | 550 | 1648 | 31 |
| set_03 | 531 | 572 | 545 | 1648 | 31 |
| set_04 | 531 | 569 | 565 | 1665 | 31 |
| set_05 | 530 | 570 | 547 | 1647 | 30 |

(числа — строк данных без заголовка)

Размер `set_01`: `original.csv` 19 873 Б, `deutermethylated.csv` 20 859 Б, `deuteroacylated.csv` 20 317 Б, `annotations.csv` 229 196 Б, `molecules.csv` 6 140 Б; локально `report.pdf` 338 165 Б (не в git).

Формат `original.csv`: `mass,intensity` (пример: `299.20163947262529,1000`). Сигнальные пики имеют интенсивность ровно **1000**.

`molecules.csv`: `set_id, compound_id, compound_number, name, smiles, inchi, formula, charge, mode, carboxyl_count, hydroxyl_count, other_fg, nom_like_flag, comment`. `carboxyl_count` 1–4, `hydroxyl_count` 0–8; молекул с `carboxyl_count>0` — 31/31/31/31/30; с `hydroxyl_count>0` — 9/11/9/15/9.

`annotations.csv`: `set_id, spectrum_type, peak_id, mass_obs, intensity, mass_theor, exact_mass, mass_error_ppm, compound_id, compound_number, formula, derivatization_state, adduct_type, charge, assignment_confidence, is_signal`.

**Происхождение:** реальные масс-спектры в репозиторий не включены (`docs/data_sources.md:16`); `data/real_sets/set_01/` пуст. Все данные в git — синтетические (`src/sim/generate_test_sets.py`) и справочные (`ref_molecules_all_pubchem_filtered.csv`, 154 строки, PubChem; `comment` = «NOM-like candidate (random CID)»). `test_sets.zip` (505 586 Б) в git не отслеживается (`.gitignore:57`), содержимое **НЕ ПРОВЕРЕНО**.

---

<a name="этап-4"></a>
## ЭТАП 4. ПРЕДОБРАБОТКА И ФИЛЬТРАЦИЯ ШУМА

### 4.1. `denoise()` и приоритет параметров

`src/core/spectrum/_denoise.py:16–47`:
```python
def denoise(spec, *, force=2.0, intensity=None, quantile=None):
    return spec.noise_filter(force=force, intensity=intensity, quantile=quantile)
```
Docstring L32 утверждает «Default 1.5», фактическое значение — **2.0** (L19).

`Spectrum.noise_filter()` (`domain/spectrum.py:285–319`), приоритет `intensity` > `quantile` > auto:

| Режим | Порог | Где |
|---|---|---|
| `intensity=I` | `threshold = I` | L305–306 |
| `quantile=q` | `threshold = intensity.quantile(q)` | L307–308 |
| auto (GMM+BIC) | `threshold = compute_noise_threshold(...).threshold * force` | L309–316 |

Оставляются пики строго `p.intensity > threshold` (L318). При `len(intens) < 3` — копия без фильтрации (L313–314).

### 4.2. GMM-фильтр: реализация

Clean-room EM для 1-мерной смеси нормальных распределений (`_denoise.py:64–155`), без scikit-learn.

`compute_noise_threshold()` (L265–351):
1. `x = log10(intensities)`; при `n > NOISE_CFG.subsample_max_points` (=5000) — подвыборка 5000 без возврата, `rng = np.random.default_rng(42)` (L301–307).
2. Для `K = 1..min(max_components, n)` — `fit_gmm_1d`, `n_params = K*3 − 1`.
3. `BIC = −2·logL + m·log(n)` (L163–170); `K* = argmin(BIC)` (L319–321).
4. Компоненты сортируются по среднему (L331–334).
5. `K* == 1` → порог = среднее единственной компоненты (L336–338); иначе — точка пересечения двух низших по среднему гауссиан (`gaussian_intersection`, L178–235).
6. `threshold = 10^x_thr` (L345).

`gaussian_intersection` решает `π₁N(x|μ₁,σ₁²)=π₂N(x|μ₂,σ₂²)` как `A·x²+B·x+C=0`:
```
A = 1/(2σ₁²) − 1/(2σ₂²)
B = μ₂/σ₂² − μ₁/σ₁²
C = μ₁²/(2σ₁²) − μ₂²/(2σ₂²) − ln(σ₂/σ₁) − ln(π₁/π₂)
```
(L192–209). Выбирается корень между μ₁ и μ₂, иначе — ближайший к середине; при `|A| < eps` — линейное решение; при `disc < 0` — середина (L211–235).

**Параметры GMM:**

| Параметр | Значение | Комментарий |
|---|---|---|
| `eps` | `1e-15` | `constants/noise.json` |
| `max_components` | `5` в JSON — **не используется**; фактически `15` в сигнатурах `noise_filter` (L291) и `compute_noise_threshold` (L268) | расхождение |
| `max_iter` (EM) | `200` жёстко (`fit_gmm_1d`, L68); `NOISE_CFG.max_iter = 100` не используется | расхождение |
| `tol` | `1e-4` (L69) | `NOISE_CFG.tol` тоже 1e-4, но не читается |
| `random_state` | `42` (L70) | — |
| `subsample_max_points` | `5000` (L302) | JSON используется |
| Регуляризация дисперсии | `max(vars_new, 1e-6 * var(x))` (L140) | жёстко |
| Инициализация | равновероятные бины, `vars = var(x)*0.5` (L104–110) | жёстко |

Проверено grep: `NOISE_CFG.max_components`, `NOISE_CFG.max_iter`, `NOISE_CFG.tol` — обращений **НЕ НАЙДЕНО**.

### 4.3. Значения по умолчанию по контекстам

| Контекст | `force` | `intensity` | `quantile` | Источник |
|---|---|---|---|---|
| `denoise()` / `Spectrum.noise_filter()` | **2.0** | None | None | `_denoise.py:19`, `spectrum.py:288` |
| `run_pipeline()` (production) | 2.0 | None | None | `pipeline.json → run_pipeline_defaults` |
| `pipeline.json → test_mode.denoise` | 2.0 | None | None | **эталон (подтв. автор)**; используется интеграционным тестом |
| `pipeline.json → smoke_pipeline_params` | 10 | 100 | — | `smoke_runner.py:33` |
| `_run_test_mode()` сигнатура | 10.0 | 100 | None | `_test.py:33–35` (перекрывается при вызове через `run_pipeline`) |
| GUI default (авторежим) | 2.0 | — | — | `app.py:251`, `_params.py:312` |
| `test_denoise.py` | 10.0 (перекрыт) | 100 | None | `test_denoise.py:34` |

### 4.4. Фильтрация по S/N, интенсивности, m/z

* S/N-фильтра — **НЕ НАЙДЕНО**.
* Нормировка/относительная интенсивность — **НЕ НАЙДЕНО**.
* Абсолютная интенсивность — режим `intensity`; квантиль — режим `quantile`.
* m/z-окно — только при загрузке; `run_pipeline` по умолчанию 0.0–1000.0; тест-режим — original 100–1000, derivatized 100–2000 (`_test_set.py:145–183`).

### 4.5–4.6. Удаление загрязнений, рекалибровка масс

**НЕ НАЙДЕНО** (ни списков фонов/калибрантов/аддуктов, ни внутренней/внешней рекалибровки по реперным пикам).

### 4.7. Порядок операций и `ppm`-допуск

Порядок: загрузка → denoise (3×) → assign_formulas → find_series ×2 → build_result_table → визуализация → экспорт. **Нормировки интенсивностей нет ни на одном шаге.**

`ppm` — относительная ошибка, зависящая от m/z:
* `assign_formulas`: `|cand_ion − mass_obs| / mass_obs · 1e6` (`_assign.py:193`) — знаменатель — **наблюдённая** масса.
* `_find_peak`: `|mz − target_mz| / target_mz · 1e6` (`_series.py:39`) — знаменатель — **целевая (теоретическая)** масса.
* `_ppm_error`: `|observed − theoretical| / theoretical · 1e6`; при `theoretical == 0` → `inf` (`_helpers.py:16–34`).
* `_measure_m1_ratio`: `tol_da = (mass+1.00335) · ppm_tol · 1e-6` (`_chem.py:184`).

Адаптации допуска к m/z, кроме линейной относительной зависимости, **НЕ НАЙДЕНО**.

### 4.8. Измеренная статистика фильтрации

set_01, `run_pipeline` с параметрами по умолчанию (`noise_force=2.0`, `load_mass 0–1000`):

```
src_loaded=531   → src_denoised=316   (59.5 %)
dmet_loaded=569  → dmet_denoised=555
dacet_loaded=548 → dacet_denoised=482
assigned_count=119 (assigned_ratio = 0.3766)
result_rows=119, N_COOH>0: 31, N_OH>0: 10
```

Влияние параметров денойзинга на set_01 (100–1000 Da), измерено:

| Параметры | Осталось пиков | Мин. интенсивность |
|---|---|---|
| `force=2.0, intensity=None` (GMM, эталон) | 316 из 531 | 39.51 |
| `force=2.0, intensity=0` | 531 из 531 | 0.717 |
| `force=10.0, intensity=100` | 31 | 1000.0 |

---

<a name="этап-5"></a>
## ЭТАП 5. НАЗНАЧЕНИЕ МОЛЕКУЛЯРНЫХ ФОРМУЛ (ЯДРО)

### 5.1. Атомные массы и источник

`configs/chemistry.json → monoisotopic_masses` (→ `ATOMIC_MASS`, `_constants.py:28`):

| Элемент | Масса (Da) |
|---|---|
| H | 1.00782503223 |
| C | 12.0 |
| N | 14.00307400443 |
| O | 15.99491461957 |
| S | 31.9720711744 |
| P | 30.97376199842 |

`proton_mass = 1.007276466812`; `electron_mass = 0.0005485654179999688`. `atomic_mass_elements = ["H","C","N","O"]`.

Значения продублированы в `formula_db/_packed.py:15–22` в целочисленном виде с масштабом `MASS_SCALE = 1e11` и совпадают до 11-го знака. Заявлений «AME2020» или иного источника — **НЕ НАЙДЕНО**; **подтв. автор: не подтверждены**.

### 5.2. Учёт заряда и полярности

| `ion_mode` | Сдвиг `neutral → m/z` |
|---|---|
| `"neutral"`, `""`, `None` | 0.0 |
| `"[M-H]-"`, `"m-h"`, `"mh-"` | `−CHEM.proton_mass` |
| `"[M]+"`, `"m+"`, `"[m+]"` | `−CHEM.electron_mass` |
| `"[M+H]+"`, `"m+h"`, `"mh+"` | `+CHEM.proton_mass` |
| иное | `ValueError` |

Аддукты `[M+Na]+`, `[M+Cl]−`, многозарядные — **НЕ НАЙДЕНО**. В `assign_formulas` окно генерации сдвигается наоборот: `gen_min = mass_min + proton_mass` (`_assign.py:99–101`).

**Критично (код):** `run_pipeline` не передаёт `ion_mode`/`sign` в `assign_formulas` — всегда используется `CHEM.default_ion_mode`. Проверено: `run_pipeline(..., sign='+')` даёт побитово идентичную таблицу. **Подтв. автор: положительный режим сейчас не поддерживается.**

### 5.3. Алгоритм перебора

`_generate_cached()` (`_generate.py:21–115`), `@lru_cache(maxsize=16)`:
* полный перебор вложенными циклами `C → H → O → N`;
* сужение диапазонов: `mass_min_abs = mass_min*0.99`, `mass_max_abs = mass_max*1.01`, `eps = 1e-9`; для каждого C вычисляются `h_lo/h_hi`, затем `o_lo/o_hi`, затем `n_lo/n_hi`;
* жёсткие правила:
  * **Lewis:** `(h + n) % 2 != 0 → continue` (L104–107); работает только для CHON;
  * **Senior:** `h > 2*c + n + 2 → continue` (L108–111);
* возвращает `tuple` кортежей `(c, h, o, n, mass)`; строки формул строятся лениво;
* Kendrick/гомологические ряды, предварительные таблицы, бинарный поиск, векторизация, параллельность — **НЕ НАЙДЕНО**.

Отдельный модуль `src/core/formula_db/` реализует перебор `C,H,N,O,S,P` с упаковкой CNOSP в uint32 + byte-shuffle + Zstd + бинарный поиск (`_builder._enum_valid_cnosp` L64–113, `_reader.FormulaDatabaseReader.search` L126–177). **Из конвейера не вызывается**; в CI тест исключён. БД: `data/formula_db/chposp_1000_zstd9_v2.fdb` (36 232 461 Б), `formula_count = 79 576 593`, 7734 блока, `max_mass = 1000 Da`, SHA-256 `4607ec52…ab541`. **Подтв. автор: вспомогательный артефакт.**

### 5.4. Элементный алфавит и диапазоны

| Набор | C | H | O | N | Статус |
|---|---|---|---|---|---|
| `pipeline.json → formula_search.ranges` | [1, 50] | [4, 100] | [0, 20] | [0, 8] | **фактически используется** (`_FS_RANGES`, `FormulaSearchConfig`) |
| `pipeline.json → default_brutto_dict` | [0, 50] | [0, 100] | [0, 25] | [0, 10] | `DEFAULT_BRUTTO_DICT` — только в тестах |
| `configs/constants/formula_search.json` | [1, 80] | [1, 200] | [0, 40] | [0, 5] | **файл не загружается загрузчиком** → мёртвый артефакт |
| `presets/*.json → element_ranges` | см. §6.2 | | | | **игнорируются** |
| **Заявленные автором стандартные** | **C 4–40** | **H 0–100** | **O 0–12** | **N 0–12** | **в репозитории отсутствуют** |

S, P, Cl, Br, F, Na, ¹³C, ³⁴S, ²H в назначении формул не участвуют (`_FS_ELEMENTS = ("C","H","O","N")`).

### 5.5. Химические ограничения

| Ограничение | Формула в коде | Порог | Где |
|---|---|---|---|
| Чётность (Lewis) | `(h + n) % 2 == 0` | — | `_generate.py:106` |
| Senior | `h ≤ 2c + n + 2` | — | `_generate.py:110` |
| DBE (жёстко) | `max(0, 1 + C − H/2 + N/2)` | `max_dbe = 30.0` (не применяется) | `_chem.py:38–55`; `pipeline.json` |
| H/C | `H/C ≤ max_hc` | 3.0 (не применяется) | `pipeline.json` |
| O/C | `O/C ≤ max_oc` | 1.2 (не применяется) | `pipeline.json` |
| N/C | `N/C ≤ max_nc` | 1.0 (не применяется) | `pipeline.json` |
| min C | `C ≥ min_c` | 1 (не применяется) | `pipeline.json` |

В `_generate_cached` проверок отношений нет — работают только Lewis и Senior. **Подтв. автор: `max_*` должны быть мягкими фильтрами NOM, пороги брать из конфига.** Правило «семи золотых», правило азота, предельные H/C/O/C/N/C-таблицы по классам — **НЕ НАЙДЕНО**.

### 5.6. Выбор лучшего кандидата

`assign_formulas()` (`_assign.py:29–238`):

1. Массовое окно — из аргументов или `min/max` по `table["mass"]` (L85–93).
2. Генерация кандидатов в нейтральных массах со сдвигом окна на носитель заряда (L98–117).
3. Векторизация: `cand_counts (int32)`, `cand_masses_neutral`, `cand_masses_ion = neutral + _ion_shift` (L124–136).
4. Предвычисление метрик (L138–171):

```
hc_arr = H/C ; oc_arr = O/C ; nc_arr = N/C        (при C>0, иначе 0)
cand_dbe = 1 + C − H/2 + O/2                       ← ДЕФЕКТ: должно быть +N/2
ndist_arr = min_k hypot(oc − cx_k, hc − cy_k)      (центры _NOM_REGION_CENTERS); при hc<=0 → 10.0
dbe_pen   = (cand_dbe − 20) * 0.5   при cand_dbe > 20
nc_pen    = nc_arr * 2.0            при nc_arr > 0.3
n_abs_pen = (N − 3) * 2.0           при N > 3 и (O == 0 или O/N < 0.5)
base_score = nom_weight*ndist_arr + dbe_pen + nc_pen + n_abs_pen
```

5. Отбор кандидатов в ±`rel_error_ppm` (L193–194). `ppm` — **только фильтр**.
6. Изотопный фильтр (при `isotope_filter=True` и `original is not None`): `dev = |m1_real − m1_theor| / m1_theor`; при `dev > 0.20` → `+2.0` (L201–219).
7. `argmin(score)`; если все score нефинальны — кандидат с минимальным `|ppm|` (L221–226).
8. Все кандидаты сохраняются в `all_candidates`, отсортированные по `|ppm|` (L228–231).

### 5.7. Многозначность

Число сохраняемых кандидатов не ограничено: `all_candidates` — все формулы, прошедшие ppm-окно. GUI: при `len > 1` показывается «ФОРМУЛА ▾» и доступен диалог выбора (двойной клик) (`_results.py:69–73, 146–216`). Порогов «не более N кандидатов» и явного флага неоднозначности в выходной таблице **НЕ НАЙДЕНО**.

### 5.8. Изотопный фильтр

| Параметр | Значение | Источник |
|---|---|---|
| Коэффициенты Бейнона (в %) | C 1.1, H 0.015, N 0.37, O 0.04 | `constants/isotope.json` → `_BEYNON_COEFFS` |
| Формула | `Σ count_el · coeff_el / 100` | `_chem._beynon_m1_ratio` L121–137; кэш L140–142 |
| `delta_m1` | 1.00335 Da | `_DElTA_M1`, `_chem.py:118` |
| допуск поиска M+1 | 5.0 ppm | `_chem.py:159–163` |
| порог отклонения | 0.20 (20 %) | `_ISOTOPE_TOLERANCE` |
| штраф | +2.0 | `_ISOTOPE_PENALTY` |

Поддерживаемые изотопы: ¹³C, ²H, ¹⁷O, ¹⁵N (линейная аппроксимация Бейнона). ³⁴S, ³⁷Cl, ¹⁸O, биномиальное/полиномиальное распределение — **НЕ НАЙДЕНО**. При слабом сигнале (`M+1` не найден, `I(M) ≤ 0`) штраф не применяется (L191–192, 197–198, 208–209).

**Измерено:** на `set_01/original.csv` **ни один** пик не имеет измеримого M+1-спутника в пределах 5 ppm: `peaks with measurable M+1 companion: 0/531`. End-to-end: `run_pipeline(..., isotope_filter=True)` и без флага дают идентичные таблицы. Поскольку `cand_m1_theor > 0` истинно для всех кандидатов (C ≥ 1), константный штраф не меняет argmin; фильтр может менять выбор только при «промежуточных» значениях измеренного M+1/M. **Подтв. автор: точность коэффициентов не проверялась, источник неизвестен.**

### 5.9. Известные проблемы: параметры, которые не работают

| Параметр / настройка | Заявлен | Фактически |
|---|---|---|
| `run_pipeline(brutto_dict=…)` | диапазоны элементов | **игнорируется** (`_run.py:193,271` — только debug и ключ кэша); проверено: результат побитово идентичен при `C:1-1` и по умолчанию. **Подтв. автор: дефект** |
| CLI `--element-ranges` | диапазоны | → `brutto_dict` → игнорируется |
| пресеты `element_ranges` | диапазоны | → `brutto_dict` (`cli.py:40–43`) → игнорируется |
| GUI «Диапазоны элементов» | диапазоны | `_params.py:396–401` → игнорируется |
| `--sign`, GUI «Знак иона», `sign=` | `[M-H]-`/`[M+H]+` | **игнорируется** для назначения |
| `FormulaSearchConfig.max_hc/max_oc/max_nc/max_dbe/min_c` | мягкие фильтры NOM | **не применяются** и не переопределены |
| `_generate_candidate_formulas(mode=…)` | «nom_like»/«soft» | не используется (L122) |
| `default_brutto_dict` / `DEFAULT_BRUTTO_DICT` | диапазоны | только в тестах |
| `pipeline.json → test_mode.assign.mode = "simple"` | режим | **НЕ НАЙДЕНО** ни одного чтения |

### 5.10. Краши и невалидные кандидаты

* XFAIL: `tests/unit/test_spectrum_ops.py:271` — `test_empty_spectrum_no_crash`: «Known: empty spectrum raises ValueError (NaN→int in formula range calc)» — подтверждённый известный дефект.
* `tests/integration/test_pipeline_integration.py:50–53` — «assign_formulas на denoised-спектрах без явных границ масс недоназначает формулы (assign_recall ~30–50 % vs 77–90 % с границами). Явное указание mass_min=0/mass_max=1000 — осознанный workaround. См. issue #50 (IMP-10)».
* `TODO`/`FIXME`/`HACK` в `src/`, `tests/`, `tools/` — **НЕ НАЙДЕНО** (кроме `tools/ai_workflow.py:497–507` — проверка плейсхолдеров, и `.flake8:6` комментария `# TODO(#tech-debt)`).

---

<a name="этап-6"></a>
## ЭТАП 6. ПРЕДУСТАНОВКИ (PRESETS) И КОНФИГУРАЦИИ

### 6.1. Структура `src/configs`

| Файл | Загружается | Схема/валидация |
|---|---|---|
| `chemistry.json` | `load_config("chemistry")` → `CHEM` | нет |
| `pipeline.json` | `PIPELINE` | нет |
| `paths.json` | `PATHS` | нет |
| `constants/noise.json` | `NOISE_CFG` | нет |
| `constants/isotope.json` | `ISOTOPE_CFG` | нет |
| `constants/spectrum_load.json` | `SPECTRUM_LOAD_CFG` | **не используется** |
| `constants/formula_search.json` | **не грузится** (нет в `_CONFIG_FILES`) | — |
| `presets/{soil,water,peat,coal}.json` | `presets_loader.list_presets()` | нет |

`loader.py`: `ConfigNamespace`, `load_config` (lru_cache), `ConfigError` при отсутствии файла / не-JSON / не-объекте (L106–124).

Приоритет: `run_pipeline` defaults → пресет → явные CLI/GUI-флаги (перекрывают). Пользовательских конфиг-файлов, версионирования конфигов, миграций и обратной совместимости — **НЕ НАЙДЕНО**.

**Баг упаковки:** `tools/NOM_HRMS_FGA.spec:58–67` добавляет в бандл только `src/configs/*.json` и `presets/*.json`; `constants/*.json` **не добавляются**. Поскольку `loader.py` выполняет `NOISE_CFG = load_config("noise")` на уровне модуля (L133), при запуске .exe `import src.configs` должен падать с `ConfigError`. Сборка .exe не проверялась.

### 6.2. Полная таблица пресетов

| Параметр | soil | water | peat | coal |
|---|---|---|---|---|
| `name` | «Почва (soil)» | «Вода (water)» | «Торф (peat)» | «Уголь (coal)» |
| `load_mass_min` | 150.0 | 100.0 | 200.0 | 200.0 |
| `load_mass_max` | 800.0 | 1000.0 | 900.0 | 1000.0 |
| `noise_force` | 3.0 | 2.0 | 3.0 | 5.0 |
| `noise_intensity` | 500 | 1000 | 500 | 300 |
| `rel_error` | 0.5 | 0.5 | 0.5 | 0.5 |
| `ppm_tol` | 3.0 | 3.0 | 3.0 | 2.0 |
| `max_groups` | 15 | 20 | 25 | 10 |
| `element_ranges.C` | [5, 60] | [3, 70] | [7, 65] | [10, 80] |
| `element_ranges.H` | [4, 120] | [2, 140] | [4, 100] | [4, 100] |
| `element_ranges.O` | [1, 30] | [1, 35] | [2, 40] | [0, 20] |
| `element_ranges.N` | [0, 3] | [0, 4] | [0, 4] | [0, 2] |

Ключи пресета, доходящие до `run_pipeline`: `load_mass_min`, `load_mass_max`, `noise_force`, `noise_intensity`, `noise_quantile`, `rel_error`, `ppm_tol`, `max_groups`, `allow_gaps`, `sign` + `brutto_dict`. `element_ranges` → `brutto_dict` **не применяется**. Ни в одном пресете нет `allow_gaps`, `sign`, `noise_quantile`. Значения пресетов не тестируются.

### 6.3. Единая таблица настроек приложения

Легенда «применяется»: ✅ влияет на результат; ⚠️ доходит до `run_pipeline`, но не влияет; ❌ не доходит/не читается.

| # | Настройка | Тип | По умолчанию | Допустимое | Где используется | Проверка | GUI | CLI | Применяется | Исключение | Влияет на хим. валидность | Тест |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | `load_mass_min` | float | 0.0 | — | `load_spectrum` | нет | поле «m/z min» | `--mass-min` | ✅ | нет | да | интеграц. |
| 2 | `load_mass_max` | float | 1000.0 | — | `load_spectrum` | GUI: `min<max` | «m/z max» | `--mass-max` | ✅ | GUI messagebox | да | интеграц. |
| 3 | `sep` | str | `,` | `,`/`;`/`\t` | `read_csv` | нет | «Разделитель CSV» | `--sep` | ✅ | нет | — | `test_load_formats` |
| 4 | `noise_force` | float | 2.0 | >0 | auto GMM | нет | «Значение» (auto) | `--noise-force` | ✅ (если intensity/quantile = None) | нет | отсекает слабые пики | `test_denoise` |
| 5 | `noise_intensity` | float\|None | None | >0 | жёсткий порог | нет | «Значение» (intensity) | `--noise-intensity` | ✅ (приоритет) | нет | — | `test_denoise` |
| 6 | `noise_quantile` | float\|None | None | [0,1] | квантиль | нет | «Значение» (quantile) | `--noise-quantile` | ✅ | нет | — | — |
| 7 | `rel_error` | float | 1.0 (production) / 0.5 (пресеты, эталон) | >0 | ppm-окно assign | нет | «Погрешность (ppm)» | `--rel-error` | ✅ | нет | да | `test_assign_formulas` |
| 8 | `sign` | str | `-` | `-`/`+` | metadata/cache | combobox | `--sign` | ❌ | нет | — | нет |
| 9 | `assign_mass_min` | int | 0 | — | окно assign | нет | скрыто | — | ✅ | нет | — | — |
| 10 | `assign_mass_max` | int | 1000 | — | окно assign | нет | скрыто | — | ✅ | нет | — | — |
| 11 | `ppm_tol` | float | 5.0 (production) / 0.5 (эталон) | >0 | `find_series` | `ValueError` при ≤0 | «Допуск поиска (ppm)» | `--ppm-tol` | ✅ | да | да | `test_find_series` |
| 12 | `max_groups` | int | 20 | ≥1 | `find_series` | `ValueError` | «Макс. число групп» | `--max-groups` | ✅ | да | да | `test_find_series` |
| 13 | `allow_gaps` | bool | true | — | `find_series` | нет | чекбокс | `--allow-gaps` | ✅ | нет | да | `test_find_series` |
| 14 | `isotope_filter` | bool | false | — | `assign_formulas` | нет | чекбокс | `--isotope-filter` | ✅ (на тест-данных эффекта нет) | нет | да | `test_isotope_filter` |
| 15 | `brutto_dict` | dict | None | — | `run_pipeline` | нет | 8 полей элементов | `--element-ranges` | ❌ | нет | да | — |
| 16 | GUI `noise_value` (quantile) | float | `0.01` | [0,1] | — | — | «Значение» | — | ✅ | — | — | — |
| 17 | `min_series_length` | int | 1 | ≥1 | `find_series` | `ValueError` | — | — | ✅ (test_mode) | да | да | `test_find_series` |
| 18 | `max_consecutive_misses` | int | 3 | ≥1 | `find_series` | `ValueError` | — | — | ✅ | да | да | `test_find_series` |
| 19 | `nom_weight` | float | 1.0 | >0 | score assign | нет | скрыто | — | ✅ | нет | да | `test_nom_prioritize` |
| 20 | `ion_mode` | str | `[M-H]-` | 4 режима | `assign_formulas` | `ValueError` | — | — | ✅ | да | да | `test_core_utils` |
| 21 | `max_components` (GMM) | int | 15 (код) / 5 (JSON, не читается) | ≥1 | GMM | нет | — | — | ✅ (код) | нет | — | — |
| 22 | `visualize` | bool | True / False (GUI) | — | `run_pipeline` | нет | — | — | ✅ | нет | — | — |
| 23 | `output_csv` | str\|None | `result_table.csv` | — | экспорт | нет | «Выходной файл» | `--output` | ✅ | GUI messagebox | — | `test_export` |
| 24 | `use_cache` | bool | True | — | `run_pipeline` | нет | — | — | ✅ | нет | — | — |
| 25 | `test_mode` | bool | False | — | `run_pipeline` | нет | — | — | ✅ | нет | — | `test_pipeline` |
| 26 | `test_sets_root` | str\|None | None | — | автопоиск | нет | — | — | ✅ | нет | — | интеграц. |
| 27 | `van_krevelen_output` | str\|None | None | — | `create_van_krevelen_plot` | нет | кнопка PNG | — | ✅ | нет | — | — |
| 28 | `save_dmet`/`save_dacet` | str\|None | None | — | `visualize_series` | нет | — | — | ✅ | нет | — | — |
| 29 | `progress_callback` | callable\|None | None | — | все этапы | нет | GUI progressbar | — | ✅ (UI) | нет | — | — |

GUI-специфичные: `src_rt_min/max`, `dmet_rt_*`, `dacet_rt_*`, `_batch_*`, `vk_color_var`.

### 6.4. Значения по умолчанию `run_pipeline()`

`sep=","`, `load_mass_min=0.0`, `load_mass_max=1000.0`, `noise_force=2.0`, `noise_intensity=None`, `noise_quantile=None`, `brutto_dict=None`, `rel_error=1.0`, `sign="-"`, `assign_mass_min=0`, `assign_mass_max=1000`, `ppm_tol=5.0`, `max_groups=20`, `allow_gaps=True`, `visualize=True`, `isotope_filter=False`, `use_cache=True`.

---

<a name="этап-7"></a>
## ЭТАП 7. ИЗОТОПНОЕ МЕЧЕНИЕ

### 7.1. Поддерживаемые метки и константы

| Метка | Смысл | Константа | Значение (Da) | Источник |
|---|---|---|---|---|
| Дейтерометилирование | –COOH → –COOCD₃ | `DELTA_CD3` | **17.03448** | `chemistry.json`, `_constants.py:14–16` |
| Дейтероацилирование | –OH → –OCOCD₃ | `DELTA_CD3CO` | **45.02939** | `chemistry.json`, `_constants.py:17–19` |
| HDX (H→D) | — | — | **НЕ НАЙДЕНО** | — |
| Иные метки | — | — | **НЕ НАЙДЕНО** | — |

**Независимая проверка (выполнена в отчёте, не в коде):**
* D − H = 2.014101778 − 1.007825032 = 1.006276746 Da; CH₃→CD₃ = 3.018830238 Da.
* COOH → COOCD₃: Δ = (C + 3D) − H = 12 + 6.042305334 − 1.007825032 = **17.034480302 Da**. Код: 17.03448 → расхождение 3·10⁻⁷ Da (<0.02 ppm при m/z 300).
* OH → OCOCD₃: Δ = (C + O + C + 3D) − H = **45.029394922 Da**. Код: 45.02939 → расхождение 5·10⁻⁶ Da.

Константы согласованы между `chemistry.json`, `docs/CODE_AVAILABILITY.md:18–19`, `docs/data_sources.md:51–52` и читаются из `CHEM` в `generate_test_sets.py:108–121`. Единственный источник — `chemistry.json`.
Маркировки «через монодейтерированный ион» **НЕ НАЙДЕНО**.

### 7.2. Алгоритм поиска серий

`find_series(src, deriv, delta, ppm_tol=5.0, max_groups=20, allow_gaps=True, min_series_length=1, max_consecutive_misses=3, progress_callback=None)` — `_series.py:48–215`.

1. Валидация: `ppm_tol > 0`; `max_groups`, `min_series_length`, `max_consecutive_misses` ≥ 1; наличие столбцов (`ValueError`).
2. Для каждого пика с `assign == True`:
   * `counts = parse_formula(brutto)` (кэш формул, L136, L150–153);
   * `m0_theor = _neutral_to_ion_mass(exact_mass_from_counts(counts), CHEM.default_ion_mode)`; при `|m0_theor − m0_obs|/m0_obs > 0.001` используется `m0_obs` (L156–157);
   * для `step = 1..max_groups`: `target = m0_theor + step*delta`, `_find_peak(mz_deriv, target, ppm_tol)`.
3. Пропуски: `consecutive_misses`; разрыв при ≥ `max_consecutive_misses` (L175–176); при `allow_gaps=False` — стоп на первом пропуске после первого найденного шага (L177–178).
4. `n_groups = max(found_steps)`; `missing = sorted({1..n_groups} − found_steps)`; `series_mz` обрезается (L184–188).
5. Запись, если `n_groups ≥ min_series_length` (L190–200).

Окно поиска: `±ppm_tol` относительно `target`; знаменатель — `target_mz` (`_series.py:39`). Максимум — `max_groups`. Принадлежность пика: ближайший по ppm без исключения уже использованных пиков (`_find_peak`, L34–45) — один и тот же пик `deriv` может обслуживать несколько родительских. Маркировки отсутствия родительского иона — **НЕ НАЙДЕНО**. Биномиальное распределение/анализ интенсивностей серий — **НЕ НАЙДЕНО**. Обратный обмен, остатки растворителя, побочные реакции — **НЕ НАЙДЕНО** (в генераторе `conversion_yield 0.8` объявлен, но не используется).

### 7.3. Число функциональных групп

* `n_groups` — только по длине серии; число групп из формулы не используется.
* Неполная метка: `n_groups` = последний найденный шаг.
* Лабильные H: спец. учёта **НЕ НАЙДЕНО**; любые OH не различаются.
* `N_OH_total` (упомянут в docstring `_build.py:29`) в коде отсутствует — есть только `N_OH`.

### 7.4. Формат результата

`find_series` → `mass_src`, `brutto`, `n_groups`, `steps_found`, `missing`, `series_mz`.
`build_result_table` → `mass, intensity, brutto, all_candidates, N_COOH (=n_dmet), N_OH (=n_dacet), missing_dmet, missing_dacet`.
Кодов качества, флагов неоднозначности, признака неполной метки — **НЕ НАЙДЕНО**.

### 7.5. Сопоставление нескольких меток

`build_result_table(src, df_dmet, df_dacet)` (`_build.py:12–88`): база — строки `src.table` с `assign == True`; ключ — `mass.round(4)`; `left merge` с `df_dmet` и `df_dacet`; `n_dmet/n_dacet` заполняются 0 при отсутствии (L68–69); `N_COOH = n_dmet`, `N_OH = n_dacet` (L70–71). Совместной логики «CD3 + CD3CO → пересечение/разность» **НЕ НАЙДЕНО**. В генераторе `hydroxyl_count` уменьшен на `carboxyl_count` (комментарий `tests/unit/test_chemical_validity.py:17–18`).

### 7.6. Измеренная статистика по сериям

**Тест-режим с эталонными параметрами** (`force=2.0, intensity=None`, `rel_error=0.5`, `ppm_tol=0.5`):

| Set | DmetFnd | DmetOk | DacetFnd | DacetOk | Errors |
|---|---|---|---|---|---|
| set_01 | 31 | 31 | 9 | 9 | 0 |
| set_02 | 31 | 31 | 11 | 11 | 0 |
| set_03 | 31 | 31 | 9 | 9 | 0 |
| set_04 | 31 | 31 | 15 | 15 | 0 |
| set_05 | 29 | 29 | 9 | 9 | 0 |

`wrong_ratio` по каноническому определению (`_test.py:193–205`, знаменатель — `total_signals`):
`dmet`: 0.0 / 0.0 / 0.0 / 0.0 / 3.3 % → порог 0.15 пройден;
`dacet`: **71.0 / 64.5 / 71.0 / 51.6 / 70.0 %** → **порог 0.15 не пройден на всех 5 наборах**.

Интеграционный тест (знаменатель — только молекулы с `expected_len > 0`) даёт 0 % для обоих типов дериватизации.

**Вывод:** расхождение определяется различием методик, а не алгоритмом: `_test_verify._verify_series_against_annotations()` считает «не найдено серии» ошибкой и для молекул с `expected_len = 0`. **Подтв. автор: канонический знаменатель — общий, т.е. методика `_test_verify`/`_test.py` верна, а интеграционного теста — нет.**

---

<a name="этап-8"></a>
## ЭТАП 8. СТРУКТУРНЫЙ МОДУЛЬ И СИМУЛЯЦИИ

### 8.1. `src/core/chemistry`

| Файл | Содержимое |
|---|---|
| `_fragment.py` (188) | `MoleculeFragment`: тяжёлая формула, IHD, атомы, связи, точки присоединения, `connect_to()`, `get_free_attachment_points()`, `_build_adjacency()` |
| `_fragment_data.py` (273) | `FRAGMENT_LIBRARY` и `FUNCTIONAL_GROUPS` |
| `_factories.py` (322) | фабрики углеродных скелетов: methylene…anthracene (28 функций) |
| `_functional.py` (315) | гетероциклы и функциональные группы: pyrrolidine…i (37 функций) |
| `fragments.py` (153) | реэкспорт + `ALL_FRAGMENTS` |
| `fragment_combinations.py` (354) | `filter_fragments`, `find_fragment_combinations`, `assemble_molecule_from_combination`, `assemble_all_combinations` |
| `rdkit_bridge.py` (328) | `to_rdkit_mol`, `visualize_fragment`, `visualize_fragments_grid`, `visualize_connection_sequence`, `print_molecule_info`, `visualize_with_rdkit` |
| `_visualize.py` (237) | `find_and_visualize_molecules` |

Зависимости: RDKit (обязателен для `_visualize.py:5`), numpy/pandas — нет. MAYGEN и иные генераторы — **НЕ НАЙДЕНО**.

### 8.2. Генерация изомеров/кандидатных структур

`find_fragment_combinations(target_heavy_formula, target_ihd, num_cooh=0, num_oh=0, max_bases=10, first_only=False)` (`fragment_combinations.py:51–208`):
1. Резерв атомов и IHD под `num_cooh` (COOH: `{C:1,O:2}`, IHD 1) и `num_oh` (`{O:1}`, IHD 0); при перерасходе атомов — рекурсивный вызов с нулями (L104–113).
2. Усечение библиотеки (`filter_fragments`).
3. Бэктрекинг; при `first_only` ароматические фрагменты первыми (`_AROMATIC` = benzene, naphthalene, anthracene, pyridine, pyrimidine, pyrazine, pyrrole, imidazole, furan; L126–138).
4. Мультимножества, точно совпадающие по тяжёлой формуле и IHD (`1e-6`).

Ограничения: `max_bases` (GUI: 8 в предзагрузке/превью, 12 во вкладке «Структуры»; headless — 3), `first_only`. Ограничения по времени в GUI нет; в `structure_export.py:22` `STRUCTURE_TIMEOUT = 20` с ThreadPoolExecutor.
Активных фрагментов в `ALL_FRAGMENTS` — 47; закомментированы ethylene, propylene, alkyne, propynyl, cyclooctane…cyclodecapentaene, f, cl, br, i (L88–151).

### 8.3. Симуляция спектров

`src/sim/generate_test_sets.py`:
* `get_default_config()` (L69–130): mass_range 100–1000; ppm-ошибка `normal(mean=0, std=0.2)`, `max_abs=0.5`; `intensity.max_intensity=100000.0`; `noise.peak_count=500`, `intensity_fraction_max=0.1`; derivatization `deutermethyl{COOH, Δ=17.03448, yield 0.8}`, `deuteroacyl{OH, Δ=45.02939, yield 0.8}`; adducts pos `[M+H]+`, neg `[M-H]-`; rounding 8/1.
* `generate_spectra_for_set()` (L228–398): `original` — нейтральная масса, `base_intensity = 1000` (жёстко L260); пик степени 0 и по одному на каждый `carboxyl_count`/`hydroxyl_count`.
* `apply_observed_mass_to_spectra()` (L506–569): для сигналов `mass_theor = neutral − m_H`, затем `mass_obs = mass_theor·(1 + ε·1e-6)`, ε ~ N(0, 0.2), усечение ±0.5 ppm.
* `generate_noise_peaks()` (L610–670): 500 пиков равномерно по 100–1000 Da и по 0…0.1·1000 = 0…100.
* `write_*_csv()` (L454–503, L673–768).
* `random.seed(42)` (L176).

**Неиспользуемые поля конфигурации:** `intensity.max_intensity`, `conversion_yield`, `rounding.*`, `adducts`, `ppm_error.type` (кроме проверки `== "normal"`).

### 8.4. Валидация структур

* `Molecule.add_bond()` (`molecule.py:52–92`): проверки индексов, самосвязывания, дублирования, валентности; при нарушении — тихий no-op.
* `Atom.add_bond()` (`atoms.py:102–127`): возвращает bool; `ELEMENT_DATA` содержит зарядовые валентности для N, O, P, S.
* RDKit-санитизация с fallback: `SANITIZE_ALL ^ SANITIZE_PROPERTIES`, затем `SANITIZE_FINDRADICALS | SETAROMATICITY | SETCONJUGATION`; при повторной ошибке — молча пропускается (`molecule.py:213–223`, `rdkit_bridge.py:66–76`, `_visualize.py:161–171`).
* `Molecule.is_connected()` (L94–117) — DFS.
* Проверки стереохимии/таутомерии, дедупликация изомеров по каноническим SMILES, валидация ароматичности как критерия отбора — **НЕ НАЙДЕНО**.

### 8.5. Статус компонентов

| Компонент | Статус |
|---|---|
| `find_fragment_combinations`, `assemble_*` | законченная функция, тесты есть (20) |
| `find_and_visualize_molecules` | работает, прямых тестов нет |
| GUI вкладка «Структуры» | работает (только smoke) |
| `structure_export.export_structures_for_compound` | ограниченный режим (`MAX_BASES=3`, `EXPORT_PNG=False`, таймаут 20 с) |
| `src/core/formula_db/` | законченный модуль, **не подключён**, тесты исключены из CI; **подтв. автор: вспомогательный артефакт** |

---

<a name="этап-9"></a>
## ЭТАП 9. ХИМИЧЕСКИЕ ПРОЕКЦИИ И МЕТРИКИ

### 9.1. Диаграммы Ван Кревелена

`NOM_REGIONS` (`van_krevelen.py:88–119`) — **6 областей**:

| Область | Цвет | Вершины (O/C, H/C) |
|---|---|---|
| Lipids | `#E8A87C` | (0.0,1.5), (0.3,1.5), (0.3,2.2), (0.0,2.2) |
| Proteins | `#76B5D4` | (0.3,1.5), (0.55,1.5), (0.55,2.2), (0.3,2.2) |
| Carbohydrates | `#9B8EC4` | (0.6,1.5), (1.2,1.5), (1.2,2.2), (0.6,2.2) |
| Lignin | `#7BC86C` | (0.1,0.7), (0.45,0.7), (0.45,1.5), (0.1,1.5) |
| Tannins | `#F0A45A` | (0.5,0.5), (0.9,0.5), (0.9,1.5), (0.5,1.5) |
| Condensed aromatics (black carbon) | `#A0A0A0` | (0.0,0.2), (0.2,0.2), (0.2,0.7), (0.0,0.7) |

Область «Amine sugar» (из сторонних skill-документов) **НЕ НАЙДЕНО**. Полигоны пересекаются (Proteins ∪ Carbohydrates на H/C 1.5–2.2).

Параметры: `FIGURE_FIGSIZE=(10,8)`, `FIGURE_DEFAULT_DPI=300`, `X_LIM=(0,1.2)`, `Y_LIM=(0,2.5)`, `SCATTER_SIZE_MIN=50`, `SCATTER_SIZE_MAX=300`, `SCATTER_SIZE_FALLBACK=120`, размер ∝ `sqrt` нормированной интенсивности (L269–279), `alpha=0.85`, `vmin=-0.3`, `NOM_REGION_ALPHA=0.22`, шрифт 10 pt bold.

`compute_van_krevelen_data(df)` (L127–203): требует `mass, intensity, brutto, N_COOH`; отбрасывает `C=0` с `UserWarning`; при пустом результате — `ValueError`.

Центры областей для скоринга (`_chem._NOM_REGION_CENTERS`, `_chem.py:96–102`, `_generate.py:201–207`) — среднее вершин каждого полигона (6 точек).

### 9.2. Индексы: реализованные формулы

| Индекс | Формула в коде | Файл |
|---|---|---|
| DBE / IHD (ядро) | `max(0, 1 + C − H/2 + N/2)` | `_chem.py:55` |
| DBE (в скоринге) | `1 + C − H/2 + O/2` — **дефект, должно быть `+N/2`** | `_assign.py:150` |
| DBE (statistics) | `(2C + 2 + N − H)/2` (без `max(0,…)`) | `statistics.py:18–23` |
| IHD (Molecule) | `max(0, (2C + 2 − H + N − X)/2)`, X = F+Cl+Br+I | `molecule.py:147` |
| IHD (функция) | `max(0, (2C + 2 + N − H − X)/2)` | `molecule.py:280` |
| DBE (formula_db) | `max(0, (2C + 2 + N + P − H)/2)` | `_packed.py:208–219` |
| **AI (Koch & Dittmar 2006)** | `(1 + C − O − S − 0.5H)/(C − O − S − N)`; при знаменателе ≤ 0 → `None` | `statistics.py:26–40` |
| DBE-O, NOSC, Kendrick mass defect, z*, Gibbs free energy, CRAM, AI_mod | **НЕ НАЙДЕНО** | — |

Порогов классов (AI ≥ 0.5, AI ≥ 0.67) в коде нет; единственная классификация — визуальные полигоны `NOM_REGIONS` (в скоринге используются только их центры).

### 9.3. Усреднённые параметры образца

Mn, Mw, AIn, O/Cn, H/Cn — **НЕ НАЙДЕНО**. Единственные усреднения — `batch.compute_sample_summary()` (`batch.py:74–103`): `n_compounds = len(table)`, `N_COOH_total = Σ N_COOH`, `N_OH_total = Σ N_OH`, `avg_mass = round(mean(mass), 4)` (без взвешивания по интенсивности). Те же значения — в PDF-отчёте (`report.py:112–141`).

### 9.4. Сравнение образцов

* `detect_sample_triples()` (`batch.py:46–71`) — группировка тройки по маркерам имён (`src`: original/src/source/исходный/orig; `dmet`: deutermethyl/dmet/cd3/дейтерометил; `dacet`: deuteroacyl/dacet/cd3co/дейтероацил); «длинный маркер побеждает» (L33–43).
* `build_batch_summary(rows)` — `pd.DataFrame(rows)`.
* Расстояния, коэффициент Танимото, диаграммы Венна, PCA, кластеризация — **НЕ НАЙДЕНО**.

### 9.5. Графики

| График | Библиотека | Экспорт | Параметры |
|---|---|---|---|
| Van Krevelen | matplotlib | PNG (`dpi=300` в GUI; `dpi=150` в PDF) | `figsize=(10,8)` |
| Гистограммы (H/C, O/C, DBE, AI, N_COOH, N_OH) | matplotlib, 2×3 | PNG/SVG (`dpi=300`) | `figsize=(10,6)`, bins 20 (для счётчиков `range(max+2)`), цвета `#f38ba8, #a6e3a1, #89b4fa, #fab387, #cba6f7, #94e2d5` |
| Три спектра | matplotlib (GUI) | `embed_figure` | `figsize=(9,7)`, `vlines`, 3 панели |
| Серии (сетка) | matplotlib (GUI) | — | до 9 панелей 3×N, `figsize=(9, nrows*2.8)` |
| Серии с пропусками | matplotlib (`spectrum._visualize`) | `save_path`, `dpi=150` | до 15 строк, `figsize=(12, 1.4*n+1.5)` |
| Спектры (headless) | matplotlib (`testing/artifact_export`) | PNG `dpi=150` | — |
| PDF-отчёт | reportlab + matplotlib | PDF | A4, поля 2/2/1.8/1.8 см, DejaVu, таблица — первые 50 строк |

`src/ui/theme.py` — Catppuccin: `BG=#1e1e2e`, `FG=#cdd6f4`, `ACCENT=#89b4fa`, `PANEL=#313244`, `WARN=#f38ba8`, `OK=#a6e3a1` (подтверждено в `app.py:58–66`).

---

<a name="этап-10"></a>
## ЭТАП 10. ВЫВОД ДАННЫХ

### 10.1. Форматы

| Формат | Функция | Параметры |
|---|---|---|
| CSV | `_export.export_result_table` L37–38 | `index=False`, `sep=";"`, `encoding="utf-8-sig"` |
| XLSX | `_write_xlsx` L41–45 | `sheet_name="result"`, автоширина по первым 200 строкам, максимум 80 символов (L48–56), openpyxl |
| JSON | `_write_json` L59–69 | `{metadata:{version, generated_at (UTC ISO), **metadata}, data:[...]}`, `ensure_ascii=False`, `indent=2`, `default=str` |
| PDF | `report.generate_pdf_report` | A4, 5 секций |
| PNG/SVG | GUI | `savefig` |
| stdout (CLI без `--output`) | `cli.py:182` | `to_csv(sys.stdout, index=False, sep=";")` |
| stderr (CLI) | `redirect_stdout(sys.stderr)` L158 | весь вывод пайплайна |

**Столбцы CSV (ровно, в порядке):** `mass;intensity;brutto;all_candidates;N_COOH;N_OH;missing_dmet;missing_dacet`.

**Реальные строки** (CLI, set_01):
```
mass;intensity;brutto;all_candidates;N_COOH;N_OH;missing_dmet;missing_dacet
125.06081969727607;1000.0;C7H10O2;['C7H10O2'];1;0;[];
154.01457723042307;1000.0;C6H5O4N;['C6H5O4N'];1;1;[];[]
159.07748540996138;1000.0;C6H12O3N2;['C6H12O3N2'];1;0;[];
165.0556937854678;1000.0;C9H10O3;['C9H10O3'];1;1;[];[]
```
(CRLF — следствие записи в `sys.stdout` на Windows)

### 10.2. Метаданные запуска

| Что фиксируется | Где | Формат |
|---|---|---|
| Версия ПО | `_export._write_json` L63 → `src.__version__` | только JSON |
| Дата/время | `datetime.now(timezone.utc).isoformat()` | только JSON, UTC |
| Параметры запуска | `_run.py:470–490`: `rel_error_ppm, sign, noise_force, noise_intensity, noise_quantile, ppm_tol, max_groups, allow_gaps, isotope_filter, assign_mass_min/max, load_mass_min/max` | только JSON |
| Версия/дата | PDF: `version`, `datetime.now()` | PDF |
| Хэш входных файлов / версия конфигурации / время в CSV | **НЕ НАЙДЕНО** | — |
| `PipelineTimings` в результате | **НЕТ**: `PipelineRunResult` (`_stats.py:71–87`) не имеет поля `timings`; `benchmark.py:51–54` читает `getattr(res,"timings",None)` → всегда `None` | — |

### 10.3. CLI: полный список аргументов

`src/cli.py:74–116`:

| Аргумент | Тип / choices | dest | Примечание |
|---|---|---|---|
| `--input`, `-i` | str, **required** | `input` | `.csv/.xlsx/.json/.raw/.mzML` |
| `--dmet` | str | `dmet` | |
| `--dacet` | str | `dacet` | |
| `--preset` | choices `soil,water,peat,coal` | `preset` | |
| `--output`, `-o` | str | `output` | `.csv/.xlsx/.json`; по умолчанию stdout |
| `--sep` | str | `sep` | |
| `--mass-min` | float | `load_mass_min` | |
| `--mass-max` | float | `load_mass_max` | |
| `--noise-force` | float | `noise_force` | |
| `--noise-intensity` | float | `noise_intensity` | |
| `--noise-quantile` | float | `noise_quantile` | |
| `--rel-error` | float | `rel_error` | |
| `--sign` | str | `sign` | не влияет на результат |
| `--ppm-tol` | float | `ppm_tol` | |
| `--max-groups` | int | `max_groups` | |
| `--allow-gaps` | `store_true`, default None | `allow_gaps` | |
| `--isotope-filter` | `store_true`, default None | `isotope_filter` | |
| `--element-ranges` | str `'C:5-60,H:4-120,O:1-30,N:0-3'` | `element_ranges` | не влияет |
| `--version` | `action="version"` | — | `nom-hrms-fga-cli 0.7.0` |

Прогресс: `redirect_stdout(sys.stderr)` (L158). Коды возврата: `0` — успех; `1` — пресет не найден (L129), ошибка загрузки входа (L152), исключение пайплайна (L168), непустой `res.messages` (L172–173), ошибка записи (L185).

### 10.4. Производительность (измерено)

| Задача | Команда | Время |
|---|---|---|
| Полный pytest | `pytest tests/ -q` | **26.15 с** (422 passed, 1 skipped, 1 xfailed, 9 subtests) |
| Тест-режим (5 наборов) | `python -m src.core.pipeline._test --test` | **6.202 с** |
| Один `run_pipeline` на set_01 (cold) | скрипт | **1.638 с** |
| `_generate_candidate_formulas` 200–700 Da (cold) | `benchmark_assign` | **0.1040 с**, 147 061 кандидат |
| То же (cached) | `benchmark_assign` | **0.000464 с** (224×), `CacheInfo(hits=1, misses=1, maxsize=16, currsize=1)` |
| `assign_formulas` (медиана из 5) | `benchmark_assign` | **0.2822 с**, 103 назначено |
| `compute_noise_threshold` | — | отдельно не измерялось |

Память не измерялась; профилирования (cProfile/py-spy) **НЕ НАЙДЕНО**.

---

<a name="этап-11"></a>
## ЭТАП 11. ТЕСТИРОВАНИЕ И ВАЛИДАЦИЯ

### 11.1. Структура

* `tests/conftest.py` — `PROJECT_ROOT`, `TEST_SETS_ROOT`, фикстуры `project_root`, `test_sets_root`.
* `pytest.ini` и `[tool.pytest.ini_options]` — `testpaths=tests`, маркеры `slow, integration, unit, smoke`, `pythonpath = .`.
* `tests/unit/` — 31 файл, `tests/integration/` — 3 файла. **424 теста** (с параметризованными).
* Маркеры `slow`/`smoke`/`integration` в тестах не используются; `@pytest.mark.unit` стоит на **24** тестах. `pytest -m unit` → `24 passed, 400 deselected`.

### 11.2. Что проверяет каждый модуль

| Модуль | Кол-во | Что проверяется |
|---|---|---|
| `test_core_utils.py` | 75 | `exact_mass_from_counts`, `dbe_from_counts`, `_row_to_brutto`, `_neutral_to_ion_mass`, `parse_formula`, `calculate_IHD`, `add_formula`, `_ppm_error`, `_normalize_brutto`; допуски `abs(...) < 1e-9` |
| `test_formula_db.py` | 43 | pack/unpack CNOSP, `restore_h`, `build_database`, `FormulaDatabaseReader` (bin-поиск, LRU, SHA-256), download с моками |
| `test_ai_workflow.py` | 37 | `tools/ai_workflow.py` (схема task-packet, валидация) |
| `test_molecule.py` | 29 | `Molecule.add_bond` (валентность, дубли, self-loop), `is_connected`, IHD, `get_formula`, `to_smiles` |
| `test_pipeline.py` | 28 | `run_pipeline` (валидация путей, статистика, экспорт, кэш) |
| `test_spectrum_ops.py` | 27 | `assign_formulas` (колонки, bool, изотопный фильтр), `Spectrum`, `denoise`; 1 xfail |
| `test_atoms.py` | 25 | `ELEMENT_DATA`, валентности, гибридизация |
| `test_fragments.py` | 24 | библиотека фрагментов, `connect_to`, свободные точки |
| `test_fragment_combinations.py` | 20 | `filter_fragments`, `find_fragment_combinations`, сборка |
| `test_van_krevelen.py` | 17 | `NOM_REGIONS`, `compute_van_krevelen_data` (NaN, C=0, ошибки), график |
| `test_rdkit_bridge.py` | 13 | RDKit-конвертация (skipif нет rdkit) |
| `test_isotope_filter.py` | 11 | `_beynon_m1_ratio`, порог 20 %, штраф 2.0 |
| `test_find_series.py` | 10 | `find_series` (ppm, gaps, `max_consecutive_misses`, `min_series_length`) — 717 строк |
| `test_raw_bridge.py` | 6 | RAW-мост (мок), availability, ошибки |
| `test_batch.py` | 6 | `detect_sample_triples`, `compute_sample_summary` |
| `test__safety.py` | 6 | `safe`, `_safe_df` |
| `test_statistics.py` | 5 | `dbe`, `aromaticity_index`, `compute_distribution_metrics` |
| `test_denoise.py` | 5 | signal_recall ≥ 0.90, noise_retention ≤ 0.80 на set_01…05; `force=10.0, intensity=100` |
| `test_assign_formulas.py` | 5 | recall/корректность на 5 наборах; все формулы в `DEFAULT_BRUTTO_DICT`; 0.5 ppm |
| `test_pipeline_integration.py` | 5 | полный конвейер denoise→assign→series |
| `test_structural_validity.py` | 4 | заголовки CSV |
| `test_load_formats.py` | 3 | CSV/XLSX/JSON |
| `test_export.py` | 3 | CSV/XLSX/JSON экспорт |
| `test_cli.py` | 3 | `main([...])` → 0/1, stdout |
| `test_app_fallback.py` | 3 | сигнатуры `embed_figure` |
| `test_report.py` | 2 | `generate_pdf_report` |
| `test_nom_prioritize.py` | 2 | NOM-приоритизация |
| `test_generate_cache.py` | 2 | `_generate_cached` LRU |
| `test_raw_integration.py` | 2 | skipif (Windows/DLL) |
| `test_chemical_validity.py` | 1 | `carboxyl_count/hydroxyl_count ∈ [0,10]` |
| `test_annotations_consistency.py` | 1 | согласованность annotations |
| `test_app_smoke.py` | 1 | smoke через `smoke_runner` |

### 11.3. Эталонные данные

* `data/test_sets/set_01…set_05` — синтетические (`generate_test_sets.py`, `random.seed(42)`), в git. Эталон — `molecules.csv` + `annotations.csv`.
* Происхождение молекул — PubChem (`ref_molecules_all_pubchem_filtered.csv`, 154 строки). Отбор (`process_pubchem_candidates.py`): нейтральные (`charge == 0`), CHNO-only, фильтр по массе фактически отключён (`mask_mass = True`, L120), флаг NOM-like `0.2 ≤ O/C ≤ 0.7` и `0.7 ≤ H/C ≤ 1.5` (L163–167), раскладка по 5 наборам round-robin после сортировки по (O/C, H/C, mass).
* Литературных/коммерческих подтверждений эталонных данных **НЕ НАЙДЕНО** — данные синтетические.
* `test_sets.zip` в корне — не в git, содержимое не проверено.

### 11.4. Регрессионные пороги

`pipeline.json → thresholds`: `min_denoise_recall = 0.90`, `min_assign_recall = 0.90`, `max_wrong_ratio = 0.15`.
Жёстко в тестах: `test_denoise.py:60–63` — `signal_recall ≥ 0.90`, `noise_retention ≤ 0.80`. Метрики precision/recall/F1 в явном виде — **НЕ НАЙДЕНО**.

### 11.5. Результаты запуска

```
$ .venv/Scripts/python.exe -m pytest tests/ -q -p no:cacheprovider
422 passed, 1 skipped, 1 xfailed, 5 warnings, 9 subtests passed in 26.15s
```
`flake8 src/ tests/ tools/` → **0 ошибок**; `black --check src/ tests/ tools/` → «125 files would be left unchanged».
Покрытие кода **не измерено**: `pytest-cov` и `coverage` отсутствуют в окружении и не заявлены в зависимостях.

### 11.6. CI

| Workflow | Триггер | Что делает | Блокирующий |
|---|---|---|---|
| `ci.yml` | push main/dev, PR main/dev | `lint` (flake8 + black --check, Python 3.12); `test` (матрица 3.11/3.12/3.13; unit с `--ignore` для `test_formula_db.py`, `test_ai_workflow.py`, `test_raw_bridge.py`; интеграционные — `continue-on-error: true`); `ai-checks` | да (кроме интеграционных) |
| `ai-artifacts.yml` | PR по `.ai/**`, `AGENTS.md`, `tools/ai_workflow.py` | валидация task-пакетов | да |
| `benchmark.yml` | `workflow_dispatch` | `tools/run_benchmark.py <id> --task-id …` | да |
| `release-readiness.yml` | `workflow_dispatch` | check-repo, unit-тесты, версия, поиск секретов, отчёт | нет (частично) |
| `release_exe.yml` | release published / dispatch | Windows-сборка PyInstaller; ставит numpy/pandas/matplotlib/Pillow/scipy/pythonnet/pymzml/rdkit (без `reportlab`, `openpyxl`, `zstandard`); smoke-test 15 с; загрузка в Release | да |
| `security.yml` | PR/push main, cron Пн 08:00 | secret-scan (blocking, фактически только предупреждает); `pip-audit` — advisory (`continue-on-error`) | частично |

CI ставит `requests` вручную с комментарием «needed by src/core/formula_db/_manager.py (WIP)». `pytest-timeout` не используется (коммит `65e74d2`).
`.pre-commit-config.yaml`: black 24.4.2, flake8 7.0.0, локальный `pytest-smoke` (`pytest tests/ -x -q --ignore=tests/unit/test_app_fallback.py`).
`.github/dependabot.yml`: weekly, github-actions + pip.

### 11.7. Известные дефекты

| Дефект | Признак | Источник |
|---|---|---|
| Пустой спектр → `ValueError` (NaN→int) | xfail | `test_spectrum_ops.py:271–279` |
| `assign_formulas` недоназначает без явных границ масс | workaround | `test_pipeline_integration.py:50–53` |
| `dacet_wrong_ratio` 51.6–71 % при пороге 15 % | FAIL в тест-режиме | измерено |
| `smoke_runner` импортирует несуществующий `assign_formulas_simple` | `ImportError` → блок серий не выполняется | `smoke_runner.py:178–182` |
| `brutto_dict` не применяется | проверено экспериментом | `_run.py:277–285` |
| `sign` не влияет | проверено экспериментом | `_run.py` |
| `FormulaSearchConfig`-фильтры не применяются | код | `_generate.py:48–115` |
| DBE в скоринге с `+O/2` | код | `_assign.py:150` |
| Изотопный фильтр не может сработать на тест-данных (0/531) | измерено | — |
| `NOISE_CFG.max_components/max_iter/tol` не читаются | grep | — |
| `SPECTRUM_LOAD_CFG`, `_BRUTTO_DEFAULTS` не используются | grep | — |
| `constants/formula_search.json` не загружается | grep | — |
| `constants/*.json` не бандлятся в .exe | `NOM_HRMS_FGA.spec:58–67` | — |
| `openpyxl` в `excludes` .exe → XLSX-экспорт сломается | `NOM_HRMS_FGA.spec:89` | — |
| `process_pubchem_candidates`: `OUTPUT_VK_PATH == OUTPUT_FILTERED_PATH` — перезапись | `process_pubchem_candidates.py:25–26` | — |
| `generate_test_sets`: `max_intensity`, `conversion_yield`, `rounding`, `adducts` не используются | grep | — |
| CLI на Windows падает `UnicodeEncodeError` (cp1252) без `PYTHONIOENCODING=utf-8` | воспроизведено | — |

Открытые issues с метками bug локально **недоступны** → **ТРЕБУЕТ УТОЧНЕНИЯ**. Из commit-сообщений: BUG-01 (#27), BUG-04 (#30), BUG-06 (#32), BUG-07 (#31,#40,#33), BUG-08, BUG-10 (#36).

### 11.8. Сравнение с внешними инструментами

Числовых сравнений с MFAssignR/ICBM-OCEAN/Formularity/CoreMS/UltraMassExplorer **НЕ НАЙДЕНО**; есть только план замены NOMspectra. **Подтв. автор: данных сравнения нет.**

---

<a name="этап-12"></a>
## ЭТАП 12. ИСТОРИЯ РАЗРАБОТКИ

### 12.1. Хронология крупных этапов (первая родительская линия `main`)

| Дата | Коммит | Содержание |
|---|---|---|
| 2026-06-11 | `b30b609` | init: базовая структура проекта NOM (src, data, tests, tools, docs) |
| 2026-06 | `e8d336a`, `447b1fd`, `10bf531` | вынос `ui/`, `structures/`, разбор core, `__init__` |
| 2026-06 | `411024e`, `09d8478`, `ce2878d`, `9ec19a3`, `63da6dc`, `01e3cae` | первые тесты assign/denoise, выравнивание синтетических CSV |
| 2026-06 | `be8b872`, `ca8b4d7`, `e3893aa`, `97d1b27` | стабилизация интеграции, GUI ↔ тест-режим, Patch 0.3.1 |
| 2026-07-07 | `5bd961d` (v0.3.2) | план 7 новых задач |
| 2026-07-08 | `14f42d5` (v0.4.0) | базовая линия 0.4 |
| 2026-07-12 | `310cbba`, `6b22c84` (v0.4.1/0.4.2) | патчи |
| 2026-07-13 | `5513ecf` (v0.5.0) | стабилизация |
| 2026-07-20 | `1ccfec4`, `abdf011` (v0.5.1/0.5.2) | fix валентностей S/P, `print`→`logging` |
| 2026-08-07 | `e62476b` (v0.6.0) | релиз 0.6.0 |
| 2026-08-08 | `c9c9c36` | инфраструктура AI-assisted workflow, ADR-0001 |
| 2026-08-08 | `434e325` | clean-room GMM+BIC (замена GPL NOMspectra auto-mode) |
| 2026-08-08 | `4d41c78`, `37541ff`, `7a41086`, `1bf8948`, `857a6c8` | замена `nomspectra.Spectrum`, immutable Spectrum, purge nomspectra |
| 2026-08-08 | `a5aee6c`, `dcddcff` | RawFileReader .NET-мост |
| 2026-08-08 | `6d10c9f`, `f785419`, `13904bc`, `187368b`, `54fb9e4` | GMM auto по умолчанию, subsample 5k, кэш пайплайна |
| 2026-08-08 | `2739a53`, `4fd101c`, `d2e2f94` | векторизация ионных масс, `PipelineTimings`, чистка мёртвого кода |
| 2026-08-08 | `6da88d2`, `6f396e7` | relicensing GPL-3.0 → MPL-2.0 |
| 2026-08-15 | `eeca717` (v0.6.1) | патч |
| 2026-08-16 | `1656f80`, `61e0287`, `a995ea2`, `8730a75`, `ea1ddac`, `eb93f95`, `2679378`, `d1f5712`, `1530591` | рефакторинг v0.7: `spectrum_ops.py` → `spectrum/`, `pipeline.py` → `pipeline/`, вынос констант в JSON, деление `src/core` на подпакеты |
| 2026-08-17 | `bed8248`, `45c899e`, `69d6a2c` | v0.7.0 «рефакторинг, оптимизация, external-replacement» |
| 2026-08-17 | `93bc94a` (#168) | perf: оптимизация `assign_formulas` (OPT-07/08/09/10) |
| 2026-08-17 | `a0667b5` | benchmark-скрипт, CI pythonnet+pymzml |
| 2026-08-17 | `8177c15`, `84a283b` | fix/perf `find_series`, `PipelineProgress` |
| 2026-08-18–19 | `41014d3`, `65e74d2`, `0390dda`, `ac90a79`, `2e73288`, `28e97a0`, `9633105`, `4d22ea4`, `234369b`, `0634959` | CI-обновления, блокирующий lint, структурированные benchmark-отчёты |
| 2026-08-19 | `2f80a76`, `0731e9a`, `68aed80`, `17027ef`, `372e9e4`, `a3c446f` | user guide (#96), архивация задач |
| 2026-08-19 | `c3cb07e` (#160) | v0.6.1 |
| 2026-08-19 | `a2adeb5` (#161) | fix: устранение расхождений релиза (лицензия, модули >500 строк, плейсхолдер) |
| 2026-08-19 | `f8801a6` (#162) | docs: Spectralab выделен в линию v0.1–v0.4 |
| 2026-08-19 | `02d82d5` (#163) | XLSX для load/export, JSON для мостов |
| 2026-08-19 | `956acf9` (#164) | EXPORT-01: JSON с метаданными + XLSX автоширина |
| 2026-08-19 | `cb41f31` (#165) | HIST-01: гистограммы |
| 2026-08-19 | `8ef5163` (#166) | BATCH-01: пакетная обработка |
| 2026-08-19 | `1c36f9b` (#167) | fix F821 |
| 2026-08-19 | `93bc94a` (#168) | OPT-07/08/09/10 |
| 2026-08-19 | `185b8fd` (#169) | REPORT-01: компактный PDF-отчёт |
| 2026-08-19 | `9f36bc0` (#170) | release v0.7.0 |
| 2026-08-19 | `30194d6` (#171) | **CLI-01: headless CLI** (HEAD) |

### 12.2. Расшифровка идентификаторов задач

| Префикс | Назначение |
|---|---|
| BUG-01 … BUG-10 | баги аудита: BUG-01 — `[M-H]⁻` без `_subtract_one_h` (#27); BUG-04 — `MoleculeFragment.__repr__` (#30); BUG-06 — дубликат `N_OH_total` (#32); BUG-07 — `bond_types` (#33/#40); BUG-08 — DBE fix; BUG-10 — `sign → ion_mode` (#36) |
| IMP-11 | маппинг имён колонок CSV |
| REF-02 / REF-07 | удаление wildcard-импортов (#17) / рефакторинг |
| OPT-07/08/09/10 | оптимизации `assign_formulas` |
| HIST-01 | гистограммы |
| EXPORT-01 | экспорт JSON/XLSX |
| REPORT-01 | PDF-отчёт |
| BATCH-01 | пакетная обработка |
| CLI-01 | headless CLI |
| ADR-0001 | AI-assisted development workflow |
| pub-06 | унификация сдвигов дериватизации (`a9967de`) |

### 12.3. Эволюция алгоритма

* Генерация кандидатов: `24b1d08` «убраны жёсткие фильтры из генератора + синхронизация масс-окон», `ff67ac6` «диапазонно-ориентированный генератор», `187368b` «ленивые строки формул», `93bc94a` оптимизация.
* Выбор формулы: `4581740` NOM-приоритизация; `ee1f582` BUG-08; `538a9b1` BUG-10.
* Шумодав: `434e325` clean-room GMM+BIC; `f785419` субсэмплинг + `force` 1.5→2.0; `6d10c9f` GMM auto по умолчанию; `13904bc` fix отображения.
* Метки: `a9967de` унификация сдвигов; `9bfcf41` early-stop `max_consecutive_misses`; `84a283b`/`8177c15` производительность и фикс `.itertuples()`.
* Ионизация: `538a9b1`/`05cc108`; `e1553a2` удаление `_subtract_one_h`.
* Конфигурация: `7c15065`, `e0cce6e`, `91e7404` централизация; `a995ea2` вынос констант; `8730a75` formula_search.json.
* Откаты/отменённые решения: полный отказ от `nomspectra` и COM-MSFileReader; `6dc6aec` — merge локальных изменений поверх remote. Явного `git revert` **НЕ НАЙДЕНО**.

### 12.4. Использование ИИ-инструментов

* `AGENTS.md` — 13 правил (task packet, запрет push в main, научные инварианты, implementation_report).
* `.ai/`: workflow.md (роли Perplexity/DeepCode/человек), `decisions/0001-ai-assisted-development-workflow.md` (ADR-0001, accepted, 2026-08-08), contracts (JSON-схемы), prompts, tasks (active/completed/archived), templates, baselines, reports.
* `.deepcode/` — 11 скиллов (коммит `6d88486`).
* `tools/ai_workflow.py` (1 620 строк, только stdlib) — CLI: `validate-task`, `check-repo`.
* Документы: `docs/ai_workflow.md`, `docs/ai_task_lifecycle.md`, `docs/ai_review_protocol.md`, `CONTRIBUTING.md`.
* Роли: Perplexity — исследование/архитектура/review; DeepCode — код/тесты/PR; человек — merge/release и единственный, кто может пушить в `main`.

**Раскрытие в статье:** ADR-0001 указывает «Не затрагивает научную логику» и требует reference-equivalence для scientific-задач. Требование журнала к раскрытию ИИ — **ТРЕБУЕТ УТОЧНЕНИЯ**.

---

<a name="этап-13"></a>
## ЭТАП 13. ЗАВИСИМОСТИ, УСТАНОВКА, ВОСПРОИЗВОДИМОСТЬ

### 13.1. Зависимости

`pyproject.toml:11–23`: `numpy>=1.24`, `pandas>=2.0`, `openpyxl>=3.1`, `matplotlib>=3.7`, `rdkit>=2023.9`, `Pillow>=9.0`, `zstandard>=0.22`, `reportlab>=4.0`.
Опциональные: `dev = [pytest>=7.0, black>=24.0, flake8>=7.0]`, `raw = [pythonnet>=3.0]`.
`requirements.txt` — те же + `pymzml>=2.6.1` (в опциональном блоке) и комментарии про `tkinter`, `pubchempy>=1.0.4`, `ipython>=8.0`. `requires-python = ">=3.10"`.

**Незадекларированные импортируемые зависимости:**

| Пакет | Где | В pyproject/requirements |
|---|---|---|
| `requests` | `src/core/formula_db/_manager.py:18` | **НЕТ** (CI ставит вручную) |
| `platformdirs` | `src/core/formula_db/_manager.py:44` | **НЕТ** |
| `pubchempy` | `src/sim/search_pubchem_nom_like_cids.py:18` | только в комментарии |
| `scipy` | только `tools/NOM_HRMS_FGA.spec:45` | **НЕТ** (мёртвая запись) |

### 13.2. Поддерживаемые ОС и платформенная специфика

* Python ≥ 3.10 (PEP 604). Проверено на Python 3.14.6.
* `tkinter` — GUI (Linux: `apt install python3-tk`).
* RAW — только Windows + pythonnet + DLL + .NET Framework ≥ 4.7.1.
* GUI: `matplotlib.use("TkAgg")` (`app.py:33`); `ctypes.windll` для иконки (в try/except).
* CLI — без tkinter, может работать headless.
* Проблемы: на Windows без `PYTHONIOENCODING=utf-8` CLI/тест-режим падает `UnicodeEncodeError` (cp1252); `to_csv(sys.stdout)` даёт CRLF.

### 13.3. Пошаговая установка и запуск (проверено)

```bash
pip install -r requirements.txt                   # или  pip install -e ".[dev]"
python -m src.cli --version                       # nom-hrms-fga-cli 0.7.0  ✔
python -m src.cli --input data/test_sets/set_01/original.csv \
                  --dmet data/test_sets/set_01/deutermethylated.csv \
                  --dacet data/test_sets/set_01/deuteroacylated.csv   # exit 0 ✔
python -m src.core.pipeline._test --test           # 5 наборов, 6.2 с ✔ (нужен PYTHONIOENCODING=utf-8)
pytest tests/ -q                                  # 422 passed, 26.15 с ✔
python -m src                                     # GUI (не запускался — требуется дисплей)
nom-hrms-fga                                      # GUI
python tools/build_exe.py                         # не запускался
```

**Не проверено:** установка «с нуля» (`pip install git+…`), GUI-запуск, сборка .exe, RAW-путь (DLL есть, .raw-данных нет).

### 13.4. Точки входа

`nom-hrms-fga = src.app:main`, `nom-hrms-fga-cli = src.cli:main`; `python -m src` (GUI), `python -m src.cli` (CLI). Устаревший из README (не работает): `python -m src.core.pipeline`.

### 13.5. Лицензионные ограничения и атрибуции

* Thermo RawFileReader: обязательная атрибуция, некоммерческое использование, запрет распространения DLL (ограничение распространяется на `.exe`).
* `external/` — GPL-3.0, несовместимо с MPL-2.0 при линковке, но код не используется.
* Расхождение GPL-3.0 (README/classifier) и MPL-2.0 (LICENSE) — юридически значимо. **Подтв. автор: окончательная лицензия — MPL-2.0.**

### 13.6. `CODE_AVAILABILITY.md`, `CITATION.cff`, `.zenodo.json`

* `CODE_AVAILABILITY.md` (двуязычный): версия v0.7.0, дата 2026-08-19, MPL-2.0, зависимости, пример воспроизведения; DOI — «будет присвоен».
* `CITATION.cff`: version 0.7.0, date-released 2026-08-19, автор, ORCID `0000-0000-0000-0000` (плейсхолдер), `doi: "10.XXXX/zenodo.YYYYY"` (плейсхолдер), MPL-2.0.
* `.zenodo.json`: creator ORCID **0000-0001-7545-6275**, MPL-2.0, `version: "0.6.0"` (устаревшая).
* `docs/zenodo_metadata.md` — сопутствующий документ.
* **DOI не присвоен.** **Подтв. автор: DOI/ORCID появятся.**

---

<a name="этап-14"></a>
## ЭТАП 14. ДОКУМЕНТАЦИЯ И ЛИТЕРАТУРА

### 14.1. Аннотации документации и расхождения

| Документ | Объём | Расхождения |
|---|---|---|
| `README.md` | 246 | R1–R4, R14, R18, R19 |
| `src/README.md` | 45 | R3, R20 |
| `src/configs/README.md` | 76 | устаревшие пути (`core/atoms.py`, `core/fragments.py`) |
| `data/README.md` | 40 | R8, R9 |
| `docs/architecture.md` | 180 (помечен v0.5.1) | R5, R15, R20 |
| `docs/data_sources.md` | 78 | R6, R7 |
| `docs/user_guide.md` | 184 (помечен 0.6.0) | R11; таблица пресетов (L146–149) не совпадает с JSON; «Сила денойза 1.0–3.0» (L93) vs фактические 2.0/3.0/5.0 |
| `docs/test_spectra_generation.md` | 149 | не сверялось детально |
| `docs/release_checklist.md`, `docs/scientific_change_protocol.md`, `docs/ai_workflow.md`, `docs/ai_task_lifecycle.md`, `docs/ai_review_protocol.md`, `docs/github_manual_setup.md` | 46–116 | процессы |
| `docs/RELEASE_NOTES_v0.5.0/v0.5.1/v0.5.2/v0.6.1/v0.7.0.md` | 43–96 | v0.7.0: «419 passed» (фактически 422/424) |
| `docs/benchmark_report_opt_07_08_09_10.md` | 46 | — |
| `docs/отчёт_июль_2026.md` | 87 | — |
| `docs/plans/*.md` (13) | — | планы v0.4–v0.7, замена nomspectra/external, Spectralab |
| `docs/Библиография…md` | 641 | 125+ ссылок, часть с плейсхолдерами («XXXX», «10.1021/acs.analchem.3cXXXXX») |
| `docs/Классы веществ в составе гуминовых веществ…md` | 235 | классы веществ HS |
| `Документация/` + `Документация.zip` | 74 803 Б | снимок от 2026-07-13/15, содержит устаревший `LICENSE` (GPLv3, 35 823 Б) |

### 14.2. Литературные ссылки в коде

**Найдено ровно две отсылки:**
1. `src/core/statistics.py:26–31` — «Koch & Dittmar (2006) aromaticity index. `AI = (1 + C − O − S − 0.5*H) / (C − O − S − N)`».
2. `src/core/spectrum/_chem.py:104–118` — «Изотопный фильтр ¹³C (формула Бейнона)», коэффициенты ¹³C 1.1 %, ²H 0.015 %, ¹⁷O 0.04 %, ¹⁵N 0.37 % (первоисточник не указан; **подтв. автор: источник неизвестен**).

Других ссылок (автор/год/журнал/DOI) в `src/`, `tests/`, `tools/` **НЕ НАЙДЕНО**.

### 14.3. Заимствованные алгоритмы и константы

| Алгоритм/константа | Источник по коду | Комментарий |
|---|---|---|
| GMM+BIC шумодав | «clean-room GMM-based auto-mode, MPL-2.0» (`domain/spectrum.py:282`) | замена GPL-кода; первоисточник не указан |
| Коэффициенты Бейнона | `constants/isotope.json` | первоисточник не указан |
| AI (Koch & Dittmar 2006) | `statistics.py:27` | автор/год указаны |
| DBE/IHD | общехимическая формула | без ссылки |
| Сдвиг ¹³C−¹²C 1.00335 | `constants/isotope.json` | — |
| Lewis, Senior (чётность) | комментарии `_generate.py:103–110` | названия правил без ссылок |
| Van Krevelen регионы | `van_krevelen.py:88–119` | координаты заданы вручную, источник не указан |
| Термо RawFileReader API | `THIRD_PARTY_NOTICES.md` | — |

### 14.4. Ключевые литературные позиции (из `docs/Библиография…`)

| # | Ссылка | Что обосновывает |
|---|---|---|
| 1 | Hatcher & Sleighter, *Mass Spectrom. Rev.* 2018, DOI 10.1002/mas.21663 | история молекулярного анализа NOM |
| 4/5 | Koch & Dittmar, *Rapid Commun. Mass Spectrom.* 2006, DOI 10.1002/rcm.2386; Erratum 2016 DOI 10.1002/rcm.7433 | AI / AI_mod — **единственная ссылка, присутствующая и в коде** |
| 44 | Kind & Fiehn, *BMC Bioinformatics* 2007, 8:105, DOI 10.1186/1471-2105-8-105 | «семь золотых правил» |
| 43 | Stenson et al., *Anal. Chem.* 2007, DOI 10.1021/ac061949s | основы назначения формул |
| 47 | Schum et al., MFAssignR, *Environ. Res.* 2020, DOI 10.1016/j.envres.2020.110114 | аналог ПО |
| 48 | Broek et al., ICBM-OCEAN, *Anal. Chem.* 2021 | аналог ПО |
| 50 | Li et al., *Anal. Chem.* 2024, DOI 10.1021/acs.analchem.4c00489 | ложноположительные назначения |
| 63 | **Perminova et al., *Anal. Bioanal. Chem.* 2017, DOI 10.1007/s00216-017-0197-x** | **методическая основа дейтерометилирования –COOH** |
| 60 | Ohno et al., *Anal. Chem.* 2020, DOI 10.1021/acs.analchem.0c01208 | селективное мечение |
| 64 | Hertkorn et al., *Environ. Sci. Technol.* 2013, DOI 10.1021/es402400j | селективное масс-мечение |
| 81 | Hertkorn et al., *JASMS* 2024, DOI 10.1021/jasms.4c00383 | изотопная тонкая структура |
| 54 | Rivas-Ubach et al., *Anal. Chem.* 2018, DOI 10.1021/acs.analchem.8b00529 | MSCC вместо Ван Кревелена |
| 87 | Nebbioso & Piccolo, *Biomacromolecules* 2011, DOI 10.1021/bm101488e | humeomics |

Полный список — в самом файле (641 строка).

---

<a name="этап-15"></a>
## ЭТАП 15. ОГРАНИЧЕНИЯ, РИСКИ, ОТКРЫТЫЕ ВОПРОСЫ

### 15.1. Что делает не по заявленному / не поддерживает

1. Диапазоны элементов из GUI/пресетов/`--element-ranges` не применяются.
2. `--sign` / «Знак иона» не влияет — всегда `[M-H]-`.
3. Жёсткие фильтры `max_hc/max_oc/max_nc/max_dbe` не применяются.
4. Изотопный фильтр не может сработать на тестовых данных (0/531 M+1).
5. Тест-режим FAIL по `max_wrong_ratio` для дейтероацилирования (51.6–71 %).
6. Порогов «AI ≥ 0.5 / 0.67» и классификации по AI в коде нет.
7. HDX, `[M+Na]⁺`, многозарядные ионы, рекалибровка масс, S/N-фильтр, нормировка, удаление аддуктов/калибрантов — не поддерживаются.
8. `formula_db` (79.6 млн формул, включая S и P) не подключён к назначению формул.
9. Примеры API из README (`src.core.spectrum_ops`, `mode="simple"`) не работают.
10. Штатные точки входа не воспроизводят эталонную конфигурацию (R30).

### 15.2. Источники химически невалидных результатов и защита

| Источник | Защита |
|---|---|
| DBE > 30 | soft-штраф `(DBE−20)·0.5` (порог 20, не 30) |
| Высокоазотистые (N/C > 0.3) | soft-штраф `N/C·2.0`; при `N>3` без O или O/N<0.5 → `(N−3)·2.0` |
| O-избыточные | жёсткого фильтра нет (только NOM-расстояние) |
| Валентно-невозможные | Lewis (чётность), Senior (DBE ≥ 0) |
| Отрицательный DBE | `dbe_from_counts` → 0; Senior отбрасывает |
| Изотопная неадекватность | штраф +2.0 (редко влияет) |
| Множественные кандидаты | сохраняются все; в итоговой таблице — лучший; переключение в GUI |

### 15.3. Допущения в коде

* Одно-зарядные ионы; `run_pipeline` — только `[M-H]⁻`.
* Отсутствие аддуктов, фрагментации, изотопных M+2 (S, Cl).
* Только C, H, O, N в назначении формул.
* Массовый диапазон 0–1000 Da (production), 100–1000 (original) и 100–2000 (derivatized) в тест-режиме.
* Число атомов: C ≤ 50, H ≤ 100, N ≤ 8, O ≤ 20.
* Молекула — нейтральная, замкнутая оболочка (чётное число валентностей).
* Интенсивности — произвольные единицы; нормировки нет; S/N тест-данных ≥ 10.
* Для дейтероацилирования все OH эквивалентны и полностью ацилируются; выход не моделируется.

### 15.4. Что нельзя утверждать без дополнительной проверки

1. Валидацию на реальных образцах NOM/HS.
2. Корректность подсчёта –OH как метрику (канонический `wrong_ratio` = 51.6–71 %).
3. Применение настраиваемых диапазонов элементов.
4. Поддержку положительной ионизации.
5. Эффективность изотопного M+1-фильтра.
6. Выполнение порога `max_wrong_ratio = 0.15`.
7. Наличие DOI/Zenodo-архивации.
8. Лицензию GPL-3.0.
9. Числа тестов 105/318/419.
10. Работоспособность `.exe` «из коробки» (по чтению spec отсутствуют `constants/*.json`, исключён `openpyxl`).
11. Воспроизводимость эталонного прогона через штатные точки входа.

### 15.5. Недостающие данные от автора

* Реальные HPLC-HRMS спектры (исходный/dmet/dacet).
* Результаты сравнения с независимым ПО.
* Статистика ошибок масс на реальных данных.
* Источники моноизотопных масс и коэффициентов Бейнона.
* DOI Zenodo и ORCID.
* Данные о выходе реакций дериватизации и полноте мечения.

---

<a name="этап-16"></a>
## ЭТАП 16. МАТЕРИАЛЫ ДЛЯ ИЛЛЮСТРАЦИЙ

| # | Иллюстрация | Как воспроизвести | Вход | Выход |
|---|---|---|---|---|
| 1 | Схема архитектуры / поток данных | по `docs/architecture.md:1–55` (с исправлением имён модулей) | — | блок-схема |
| 2 | Блок-схема `assign_formulas` | `_assign.py:29–238` | — | блок-схема |
| 3 | Диаграмма Ван Кревелена | `create_van_krevelen_plot(...)` или `run_pipeline(..., van_krevelen_output='vk.png')` | result table | PNG 300 dpi |
| 4 | До/после шумоподавления | `load_spectrum` + `denoise` + `vlines` | `set_01/original.csv` | PNG |
| 5 | Гистограммы H/C, O/C, DBE, AI, N_COOH, N_OH | `create_histograms_plot(...)` | result table | PNG/PDF |
| 6 | Пример серии метки | `visualize_series(src, dmet, df_dmet, delta=17.03448, save_path='series.png')` | set_01 + результат | PNG 150 dpi |
| 7 | Скриншоты GUI (9 вкладок) | `nom-hrms-fga` | 3 CSV | скриншоты |
| 8 | Таблица пресетов | §6.2 | — | таблица |
| 9 | Таблица настроек | §6.3 | — | таблица |
| 10 | Таблица метрик тест-режима | Часть II, §2 | — | таблица |
| 11 | Изотопный паттерн M+1 | `_measure_m1_ratio` | реальные спектры | график |
| 12 | Диаграмма сборки структуры | `find_and_visualize_molecules('C20H28O2', 1, 0)` + `visualize_fragments_grid` | формула | PNG |

**Уже измерено/получено в отчёте:** таблицы метрик, реальные строки CSV, замеры времени, доказательства неэффективности `brutto_dict`/`sign`/`isotope_filter`, оценка влияния исправления DBE.

---

<a name="сводка-числа"></a>
## СВОДНАЯ ТАБЛИЦА ЧИСЛОВЫХ ПАРАМЕТРОВ И КОНСТАНТ

| Имя | Значение | Единицы | Файл (строка) |
|---|---|---|---|
| `monoisotopic_masses.H` | 1.00782503223 | Da | `configs/chemistry.json` |
| `monoisotopic_masses.C` | 12.0 | Da | — |
| `monoisotopic_masses.N` | 14.00307400443 | Da | — |
| `monoisotopic_masses.O` | 15.99491461957 | Da | — |
| `monoisotopic_masses.S` | 31.9720711744 | Da | — |
| `monoisotopic_masses.P` | 30.97376199842 | Da | — |
| `proton_mass` | 1.007276466812 | Da | `chemistry.json`; `_assign.py:100` |
| `electron_mass` | 0.0005485654179999688 | Da | `chemistry.json`; `_generate.py:171` |
| `derivatization_shifts.delta_cd3` / `DELTA_CD3` | 17.03448 | Da | `chemistry.json`; `_constants.py:14` |
| `derivatization_shifts.delta_cd3co` / `DELTA_CD3CO` | 45.02939 | Da | `chemistry.json`; `_constants.py:17` |
| `default_ion_mode` | `"[M-H]-"` | — | `chemistry.json`; `_assign.py:36` |
| `load_spectrum_defaults.mass_min/max` | 100.0 / 800.0 | Da | `pipeline.json` |
| `default_brutto_dict` | C[0,50] H[0,100] O[0,25] N[0,10] | атомы | `pipeline.json` |
| `formula_search.elements` | `["C","H","O","N"]` | — | `pipeline.json` |
| `formula_search.ranges` | C[1,50] H[4,100] O[0,20] N[0,8] | атомы | `pipeline.json` |
| `formula_search.max_hc` | 3.0 | H/C | `pipeline.json` (не применяется) |
| `formula_search.max_oc` | 1.2 | O/C | `pipeline.json` (не применяется) |
| `formula_search.max_nc` | 1.0 | N/C | `pipeline.json` (не применяется) |
| `formula_search.max_dbe` | 30.0 | — | `pipeline.json` (не применяется) |
| `formula_search.min_c` | 1 | атомы | `pipeline.json` (не применяется) |
| `run_pipeline_defaults.sep` | `","` | — | `pipeline.json` |
| `run_pipeline_defaults.load_mass_min/max` | 0.0 / 1000.0 | Da | `pipeline.json` |
| `run_pipeline_defaults.noise_force` | 2.0 | множитель | `pipeline.json`; `_denoise.py:19`; `spectrum.py:288` |
| `run_pipeline_defaults.noise_intensity` | null | у.е. | `pipeline.json` |
| `run_pipeline_defaults.rel_error` | 1.0 | ppm | `pipeline.json` |
| `run_pipeline_defaults.sign` | `"-"` | — | `pipeline.json` (не влияет) |
| `run_pipeline_defaults.assign_mass_min/max` | 0 / 1000 | Da | `pipeline.json` |
| `run_pipeline_defaults.ppm_tol` | 5.0 | ppm | `pipeline.json` |
| `run_pipeline_defaults.max_groups` | 20 | шт. | `pipeline.json` |
| `run_pipeline_defaults.allow_gaps` | true | — | `pipeline.json` |
| `test_mode.load.original_mass_min/max` | 100.0 / 1000.0 | Da | `pipeline.json` |
| `test_mode.load.derivatized_mass_min/max` | 100.0 / 2000.0 | Da | `pipeline.json` |
| `test_mode.denoise.force/intensity/quantile` | 2.0 / null / null | — | `pipeline.json` (**эталон**) |
| `test_mode.assign.rel_error_ppm` | 0.5 | ppm | `pipeline.json` (**эталон**) |
| `test_mode.series.ppm_tol/max_groups/min_series_length` | 0.5 / 20 / 1 | ppm/шт./шт. | `pipeline.json` (**эталон**) |
| `test_mode.match_ppm` | 0.5 | ppm | `pipeline.json`; `_test.py:28` |
| `thresholds.min_denoise_recall` | 0.90 | доля | `pipeline.json`; `_test.py:178` |
| `thresholds.min_assign_recall` | 0.90 | доля | `pipeline.json`; `_test.py:179` |
| `thresholds.max_wrong_ratio` | 0.15 | доля | `pipeline.json`; `_test.py:180` |
| `smoke_pipeline_params.noise_force/noise_intensity` | 10 / 100 | — | `pipeline.json`; `smoke_runner.py:33` |
| `smoke_pipeline_params.rel_error/ppm_tol` | 0.5 / 0.5 | ppm | `pipeline.json` |
| `paths.json.num_test_sets` | 5 | шт. | `paths.json` |
| `paths.json.default_output_csv` | `"result_table.csv"` | — | `paths.json` |
| `constants/noise.eps` | 1e-15 | — | `constants/noise.json` |
| `constants/noise.max_components` | 5 | шт. | `constants/noise.json` (не используется) |
| `constants/noise.max_iter` | 100 | итерации | `constants/noise.json` (не используется; в коде 200) |
| `constants/noise.tol` | 1e-4 | — | `constants/noise.json` (не используется) |
| `constants/noise.subsample_max_points` | 5000 | точки | `constants/noise.json`; `_denoise.py:302` |
| `constants/isotope.delta_m1` | 1.00335 | Da | `constants/isotope.json`; `_chem.py:118` |
| `constants/isotope.beynon_coefficients` | C 1.1, H 0.015, N 0.37, O 0.04 | % | `constants/isotope.json`; `_chem.py:109` |
| `constants/isotope.tolerance` | 0.20 | доля | `constants/isotope.json`; `_chem.py:112` |
| `constants/isotope.penalty` | 2.0 | score | `constants/isotope.json`; `_chem.py:115` |
| `_nom_distance` при `hc ≤ 0` | 10.0 | — | `_chem.py:217` |
| `_measure_m1_ratio` `ppm_tol` | 5.0 | ppm | `_chem.py:162` |
| dbe_pen порог/коэф. | 20 / 0.5 | — | `_assign.py:162` |
| nc_pen порог/коэф. | 0.3 / 2.0 | — | `_assign.py:163` |
| n_abs_pen порог/коэф. | N>3, O/N<0.5 / 2.0 | — | `_assign.py:164–168` |
| порог перехода серии на наблюдённую массу | 0.001 | отн. | `_series.py:156` |
| `find_series` defaults | ppm_tol 5.0, max_groups 20, allow_gaps True, min_series_length 1, max_consecutive_misses 3 | — | `_series.py:52–56` |
| сравнение IHD в комбинаторике | 1e-6 | — | `fragment_combinations.py:148,154` |
| округление ключа merge | 4 | знака | `_build.py:44,56` |
| FIGURE_FIGSIZE / DPI (VK) | (10, 8) / 300 | дюймы/dpi | `van_krevelen.py:39–40` |
| X_LIM / Y_LIM | (0.0,1.2) / (0.0,2.5) | — | `van_krevelen.py:43–44` |
| SCATTER_SIZE_MIN/MAX/FALLBACK | 50 / 300 / 120 | pt² | `van_krevelen.py:66–69` |
| scatter `vmin` | −0.3 | — | `van_krevelen.py:323` |
| NOM_REGION_ALPHA | 0.22 | — | `van_krevelen.py:75` |
| histogram bins | 20 (или `range(max+2)`) | — | `statistics.py:116–118` |
| `report._MAX_ROWS` / `_PAGE_W` / dpi | 50 / 17.0 см / 150 | — | `report.py:47–48,73` |
| `_visualize_series` max_rows/figsize/dpi | 15 / (12, 1.4·n) / 150 | — | `_visualize.py:24–25,172` |
| окна отрисовки серий | `ppm_tol*10`, `ppm_tol*2` | ppm | `_visualize.py:99,105` |
| `formula_db.MASS_SCALE` | 100 000 000 000 (1e11) | — | `_packed.py:12` |
| `formula_db.BIN_WIDTH_U` | 10 000 000 000 (1e10) | — | `_packed.py:13` |
| `formula_db.RECORD_SIZE` | 4 | байта | `_packed.py:26` |
| `formula_db` битовые поля | C 7, N 7, O 6, S 5, P 6 | бит | `_packed.py:28–34` |
| `formula_db.COMPRESSION_LEVEL` | 9 | zstd | `_builder.py:35` |
| `formula_db.FORMAT_VERSION` / `DB_VERSION` | 2 / 1 | — | `_builder.py:36–37` |
| `formula_db` max_mass / bin_width | 1000.0 Da / 0.1 Da | — | `_builder.py:44,47` |
| `formula_db` est_total | 82 091 308 | формул | `_builder.py:67,121` |
| `formula_db` факт `formula_count` | 79 576 593 | формул | `manifest.json` |
| `formula_db` блоков | 7734 | — | `manifest.json` |
| `LRUBlockCache` max_blocks | 8 | — | `_reader.py:44` |
| `_start_structure_preload` max_bases | 8 | фрагментов | `_structures.py:70` |
| StructureViewerTab max_bases | 12 | фрагментов | `tabs.py:176` |
| `structure_export.MAX_BASES / TIMEOUT / EXPORT_PNG` | 3 / 20 с / False | — | `structure_export.py:21–23` |
| GUI noise suggested defaults | auto «2.0», intensity «100», quantile «0.01» | — | `_params.py:312` |
| `generate_test_sets` mass_range | 100.0–1000.0 | Da | `generate_test_sets.py:90–93` |
| `generate_test_sets` ppm_error | mean 0, std 0.2, max_abs 0.5 | ppm | `generate_test_sets.py:94–99` |
| `generate_test_sets` base_intensity | 1000 | у.е. | `generate_test_sets.py:260` |
| `generate_test_sets` noise peak_count / frac_max | 500 / 0.1 | шт./доля | `generate_test_sets.py:104–107` |
| `generate_test_sets` conversion_yield | 0.8 | доля | `generate_test_sets.py:117,119` (не используется) |
| `generate_test_sets.intensity.max_intensity` | 100000.0 | у.е. | `generate_test_sets.py:102` (не используется) |
| `generate_test_sets.random.seed` | 42 | — | `generate_test_sets.py:176` |
| PubChem CID range / attempts | 1–500 000 / `max_count*20` | — | `search_pubchem_nom_like_cids.py:55–63` |
| NOM-like критерий (PubChem) | 0.2 ≤ O/C ≤ 0.7; 0.7 ≤ H/C ≤ 1.5 | — | `process_pubchem_candidates.py:163–167` |
| Интеграционный тест: rel_error/ppm_tol/nom_weight | 0.5 / 0.5 / 5.0 | ppm/ppm/— | `test_pipeline_integration.py:22–49` |
| Интеграционный тест: assign mass_min/max | 0 / 1000 | Da | `test_pipeline_integration.py:46–47` |
| `test_denoise` порог recall/retention | 0.90 / 0.80 | доля | `test_denoise.py:61–63` |
| `test_denoise` параметры | force 10.0, intensity 100 | — | `test_denoise.py:34` |
| `test_chemical_validity` диапазон групп | [0, 10] | шт. | `test_chemical_validity.py:36,42` |
| flake8 max-line-length | 120 | символов | `.flake8:2` |
| black line-length | 88 | символов | `pyproject.toml:58` |
| `pyproject` requires-python | ≥3.10 | — | `pyproject.toml:10` |
| exe-размер (локальный артефакт) | 128 087 430 | байт | `dist/NOM_HRMS_FGA.exe` |
| **Заявленные стандартные `brutto_dict`** | **C 4–40, H 0–100, O 0–12, N 0–12** | атомы | ответ автора (в репозитории отсутствуют) |

---

<a name="сводка-настройки"></a>
## СВОДНАЯ ТАБЛИЦА ВСЕХ НАСТРОЕК

Полная таблица — §6.3 (29 позиций + GUI-специфичные). Ключевое:

* **Реально влияют:** `load_mass_min/max`, `sep`, `noise_force/intensity/quantile`, `rel_error`, `assign_mass_min/max`, `ppm_tol`, `max_groups`, `allow_gaps`, `isotope_filter` (теоретически), `nom_weight`, `ion_mode`, `min_series_length`, `max_consecutive_misses`, `visualize`, `output_csv`, `use_cache`, `test_mode`.
* **Не влияют:** `brutto_dict` (`--element-ranges`, `element_ranges` пресетов, GUI-поля), `sign`.
* **Не читаются:** `test_mode.assign.mode`, `constants/formula_search.json`, `constants/spectrum_load.json`, `NOISE_CFG.max_components/max_iter/tol`.
* **Исключения:** `ppm_tol ≤ 0`, `max_groups < 1`, `min_series_length < 1`, `max_consecutive_misses < 1` (`ValueError` из `find_series`); неизвестный `ion_mode` (`ValueError`); `mass_min ≥ mass_max` (GUI messagebox); отсутствие файла; неизвестный пресет (CLI код 1).
* Версионирование пользовательских настроек и их сохранение/загрузка (кроме JSON-пресетов) — **НЕ НАЙДЕНО**.

---

<a name="не-проверено"></a>
## ЧТО НЕ ПРОВЕРЕНО И ПОЧЕМУ

1. **Сборка `NOM_HRMS_FGA.exe`** — требует Windows + PyInstaller; долго. Вывод о неполном бандле `constants/*.json` и `excludes=openpyxl` — по чтению `NOM_HRMS_FGA.spec`.
2. **GUI-запуск и работа 9 вкладок** — требуется дисплей.
3. **RAW-путь** — DLL есть, pythonnet установлен, `.raw`-файлов нет.
4. **mzML-путь** — нет `.mzML`-файла.
5. **Покрытие кода** — `pytest-cov`/`coverage` отсутствуют и не заявлены.
6. **Память и профилирование** — не измерялись.
7. **GitHub Releases/Issues/PR-метаданные** — нет доступа к API.
8. **`test_sets.zip`, `Документация.zip`** — содержимое не распаковывалось.
9. **`external/usrednenie_spectrov_i_hromatogramm`** — детально не анализировался.
10. **Реальные образцы** — отсутствуют (`data/real_sets/set_01` пуст).
11. **`AI_AUDIT_HANDOFF.md` (202 108 Б)**, **`deepcode_audit_triage.md`** — неотслеживаемые локальные файлы, не входят в `main`.
12. **Исторические версии кода (v0.3–v0.6)** — только по сообщениям коммитов и release notes.
13. **`Документация/` vs корень** — сверка частичная (LICENSE, README).

---

<a name="вопросы"></a>
## ВОПРОСЫ К АВТОРУ ПРОЕКТА (первичный список)

1. Почему `brutto_dict` (диапазоны элементов из GUI/пресетов/CLI) не передаётся в `assign_formulas`?
2. `sign` (знак иона) игнорируется при назначении — поддерживается ли положительный режим фактически?
3. Так ли задумано, что `pipeline.json.test_mode.denoise` = `force 2.0 / intensity null`, а `_run_test_mode()` по умолчанию `force 10.0 / intensity 100`?
4. Как интерпретировать `dacet_wrong_ratio` 51.6–71 % (FAIL) при `max_wrong_ratio = 0.15`?
5. Почему фильтры `max_hc/max_oc/max_nc/max_dbe` определены, но не применяются?
6. Формула DBE в скоринге (`+O/2`) отличается от `dbe_from_counts` (`+N/2`) — это дефект?
7. Коэффициенты Бейнона — какой источник, проверялась ли точность?
8. Планируется ли применение `formula_db` в конвейере?
9. Каким источником подтверждены моноизотопные массы?
10. Какая методика расчёта `wrong_ratio` канонична?
11. Появятся ли DOI Zenodo и корректный ORCID?
12. Какая лицензия окончательная — MPL-2.0 или GPL-3.0?
13. Есть ли результаты сравнения с независимым ПО и статистика на реальных образцах?
14. Планируются ли аддукты, многозарядные ионы, HDX, рекалибровка масс?
15. Можно ли получить реальные HPLC-HRMS данные для независимой проверки?

**Ответы на эти вопросы приведены и учтены в Части II.**

---

# ЧАСТЬ II. УТОЧНЕНИЯ АВТОРА, ЭТАЛОННАЯ КОНФИГУРАЦИЯ И ПЛАН ИСПРАВЛЕНИЙ

## Ответы автора (сводка)

| № | Вопрос | Ответ автора |
|---|---|---|
| 1 | `brutto_dict` | «Настраиваемый пользователем параметр. Стандартные диапазоны — **C 4–40, H 0–100, O 0–12, N 0–12**» |
| 2 | Положительный режим | «Фактически не поддерживается, будет исправляться к релизу для статьи» |
| 3 | Эталонные параметры шумоподавления | «force = 2, intensity = **None** (где работает другой фильтр)» — т.е. активен GMM+BIC |
| 4 | `dacet_wrong_ratio` | «Скорее всего дефект метрики» |
| 5 | `max_hc/max_oc/max_nc/max_dbe` | «Должны быть мягкие фильтры для указания принадлежности к NOM. Если не используются — это ошибка, либо переопределены в другом месте» |
| 6 | DBE `+O/2` | «Дефект, везде должно быть с N» |
| 7 | Коэффициенты Бейнона | «Точность не проверялась, источник неизвестен» |
| 8 | `formula_db` | «Вспомогательный артефакт» |
| 9 | Моноизотопные массы | «Не подтверждены» |
| 10 | Канонический `wrong_ratio` | «**С общим знаменателем**» |
| 11 | DOI/ORCID | «Появятся» |
| 12 | Лицензия | «**MPL-2.0**» |
| 13 | Данные сравнения с другим ПО | «Нет» |
| 14 | Аддукты/многозарядные/HDX/рекалибровка | «Да» (планируются) |
| 15 | Реальные образцы | «Можно, но пока не сделано» |
| — | Эталонные `rel_error` / `ppm_tol` | **0.5 / 0.5** |
| — | Пороги soft-фильтров | **Сохранить из конфига** |
| — | ADR + reference-equivalence для правок 1/5/6 | **Да** |

---

## 1. Каноническая эталонная конфигурация

| Стадия | Параметр | Значение | Источник |
|---|---|---|---|
| Загрузка | `load_mass_min / load_mass_max` (original) | 100.0 / 1000.0 | `pipeline.json → test_mode.load` |
| Загрузка | `derivatized_mass_min / max` | 100.0 / 2000.0 | там же |
| Шумоподавление | `force` | **2.0** | `test_mode.denoise.force` |
| Шумоподавление | `intensity` | **None** → активен GMM+BIC, порог = `T_GMM · 2.0` | `test_mode.denoise.intensity` |
| Шумоподавление | `quantile` | None | там же |
| Назначение | `rel_error_ppm` | **0.5** | `test_mode.assign.rel_error_ppm` |
| Назначение | `mass_min / mass_max` | None / None | `test_mode.assign` |
| Назначение | `ion_mode` | `[M-H]-` | `chemistry.json` |
| Назначение | `nom_weight` | 1.0 (по умолчанию) | не задан в конфиге — см. §6 |
| Серии | `ppm_tol` | **0.5** | `test_mode.series.ppm_tol` |
| Серии | `max_groups` | 20 | `test_mode.series.max_groups` |
| Серии | `allow_gaps` | true | там же |
| Серии | `min_series_length` | 1 | там же |
| Серии | `max_consecutive_misses` | 3 (значение по умолчанию `find_series`) | `_series.py:56` |
| Сверка | `match_ppm` | 0.5 | `test_mode.match_ppm` |
| Пороги | `min_denoise_recall / min_assign_recall / max_wrong_ratio` | 0.90 / 0.90 / **0.15** | `thresholds` |
| Soft-фильтры (после исправления) | `max_hc / max_oc / max_nc / max_dbe` | **3.0 / 1.2 / 1.0 / 30.0** | `formula_search` |

**Вывод:** заявленная эталонная конфигурация **дословно совпадает** с секцией `test_mode` в `pipeline.json` (кроме `nom_weight`, которого в конфиге нет, и `max_consecutive_misses`, не вынесенного в JSON).

**Ни одна существующая точка входа её не воспроизводит:**

| Точка входа | `rel_error` | `ppm_tol` | окно assign | Соответствие эталону |
|---|---|---|---|---|
| `python -m src.core.pipeline._test --test` | **1.0** | **5.0** | 0 / 1000 | нет |
| `run_pipeline(test_mode=True)` | **1.0** | **5.0** | 0 / 1000 | нет |
| `tests/integration/test_pipeline_integration.py` | 0.5 | 0.5 | 0 / 1000, `nom_weight=5.0` | частично (метрика `wrong_ratio` неканонична) |
| `_run_test_mode(force=2, intensity=None, rel_error=0.5, ppm_tol=0.5, mass=None/None)` | 0.5 | 0.5 | None / None | **да** |
| `python -m src.cli` | 1.0 | 5.0 | 0 / 1000 | нет |

Причина — `run_pipeline` подставляет собственные defaults вместо чтения `PIPELINE.test_mode` (`_run.py:47–63` → `_test.py:31–43`). Это отдельный дефект воспроизводимости (R30).

---

## 2. Канонические метрики (финальные числа)

Прогон `_run_test_mode(noise_force=2.0, noise_intensity=None, noise_quantile=None, assign_mass_min=None, assign_mass_max=None, rel_error=0.5, sign='-', ppm_tol=0.5, max_groups=20, allow_gaps=True)`:

| Set | Signals | Denoised | D-Rec % | Assigned | A-Rec % | DmetFnd | DmetOk | DacetFnd | DacetOk | Errors |
|---|---|---|---|---|---|---|---|---|---|---|
| set_01 | 31 | 31 | 100.0 | 31 | 100.0 | 31 | 31 | 9 | 9 | 0 |
| set_02 | 31 | 31 | 100.0 | 31 | 100.0 | 31 | 31 | 11 | 11 | 0 |
| set_03 | 31 | 31 | 100.0 | 31 | 100.0 | 31 | 31 | 9 | 9 | 0 |
| set_04 | 31 | 31 | 100.0 | 31 | 100.0 | 31 | 31 | 15 | 15 | 0 |
| set_05 | 30 | 29 | 96.7 | 29 | 96.7 | 29 | 29 | 9 | 9 | 0 |

`ПРОВЕРКА ПОРОГОВ`: `min_denoise_recall 0.90` ✔ (все 5); `min_assign_recall 0.90` ✔ (все 5); `max_wrong_ratio 0.15`: dmet ✔ (0.0 / 0.0 / 0.0 / 0.0 / 3.3 %), **dacet ✘ (71.0 / 64.5 / 71.0 / 51.6 / 70.0 %)**.

Идентичные числа получены и при `intensity=0`: метрики не различают эти режимы, потому что все сигнальные пики имеют интенсивность 1000 и проходят любой порог. Различие проявляется в объёме рабочего спектра (316 пиков при GMM vs 531 при пороге 0) и, следовательно, в числе назначенных формул в итоговой таблице (119 vs больше).

**Эталонные числа для статьи:** denoise_recall = 96.7–100 %; assign_recall = 96.7–100 %; дейтерометилирование — 100 % совпадение длин серий; дейтероацилирование — 100 % совпадение длин серий для молекул с OH (9/9, 11/11, 9/9, 15/15, 9/9) при каноническом агрегированном `wrong_ratio` = 51.6–71.0 % (порог 0.15 не пройден).

---

## 3. Влияние подтверждённых дефектов

| # | Дефект | Влияние сейчас | Изменение после исправления | ADR |
|---|---|---|---|---|
| D1 | `brutto_dict` игнорируется (GUI, `--element-ranges`, пресеты) | диапазоны всегда C1–50/H4–100/O0–20/N0–8 | станут C4–40/H0–100/O0–12/N0–12 → существенное изменение (больше C и N, меньше H и O) | нет (но нужен reference-equivalence) |
| D2 | `sign`/`ion_mode` не доходят до `assign_formulas` | только `[M-H]⁻` | появится положительный режим | да |
| D3 | Soft-пороги `max_hc/max_oc/max_nc/max_dbe` не применяются | работают недокументированные пороги 20 (DBE), 0.3 (N/C), N>3 | при «из конфига» пороги станут **мягче**: DBE 20→30, N/C 0.3→1.0; добавятся H/C ≤ 3.0 и O/C ≤ 1.2 как soft-условия | да |
| D4 | DBE в скоринге `+O/2` вместо `+N/2` | **латентный**: 0 изменений формул на 492 назначенных пиках set_01–05 | ожидаемый эффект нулевой на эталонных данных; обязателен regression-тест | да |
| D5 | Канонический `wrong_ratio` не проходит для dacet | 5 FAIL | либо правка метрики (исключить `expected_len==0` из числителя), либо фиксация показателя как «ожидаемо-высокого» | да |
| D6 | `run_pipeline(test_mode=True)` не читает `PIPELINE.test_mode` | эталонный прогон через штатную точку входа даёт 1.0/5.0 | появятся канонические 0.5/0.5 и окно None/None | нет |

Измерение D4 (read-only подмена `+ o_arr/2.0` → `+ n_arr/2.0` в `_assign.py:150` через `exec` модифицированного исходника; остальное без изменений):

```
set_01: assigned_old=78  assigned_new=78  changed_formula=0
set_02: assigned_old=105 assigned_new=105 changed_formula=0
set_03: assigned_old=113 assigned_new=113 changed_formula=0
set_04: assigned_old=114 assigned_new=114 changed_formula=0
set_05: assigned_old=82  assigned_new=82  changed_formula=0
TOTAL: assigned=492, changed_by_DBE_fix=0 (0.00 %)
```

D4 — реальный, но в настоящее время ненаблюдаемый на эталонных данных дефект (порог штрафа DBE > 20 почти не достигается при `rel_error = 0.5`).

---

## 4. План работ (по правилам `AGENTS.md`)

Порядок сформирован так, чтобы reference-equivalence выполнялся на уже исправленной конфигурации метрик.

| Очередь | Задача | Тип | Обязательные артефакты |
|---|---|---|---|
| 1 | Заставить `run_pipeline(test_mode=True)` читать `PIPELINE.test_mode` | fix | task packet, implementation_report |
| 2 | Исправить канонический `wrong_ratio` (D5) и перевести `test_pipeline_integration.py` на него | fix/scientific | task packet, **ADR**, reference-equivalence на set_01–05 |
| 3 | Реализовать `brutto_dict` + прописать C4–40/H0–100/O0–12/N0–12 (D1) | scientific | task packet, ADR, reference-equivalence |
| 4 | Ввести soft-фильтры из конфига с явными весами (D3) | scientific | task packet, **ADR**, reference-equivalence, регрессия на долю высокоазотистых |
| 5 | Исправить DBE `+O/2 → +N/2` (D4) | scientific | task packet, **ADR**, regression-тест (baseline «0 изменений») |
| 6 | Положительный режим `[M+H]+` (D2) | scientific | task packet, ADR, reference-equivalence |
| 7 | Метаданные: `README`/classifier → MPL-2.0; `.zenodo.json` version; `CITATION.cff` ORCID/DOI; пересчёт числа тестов; удалить устаревший `Документация/LICENSE` | docs/packaging | task packet |
| 8 | Упаковка: `constants/*.json` в `datas`, убрать `openpyxl` из `excludes` | packaging | task packet, benchmark (smoke .exe) |
| 9 | Указать источники моноизотопных масс и коэффициентов Бейнона | docs | task packet |

---

## 5. Утверждения для статьи

**Можно утверждать:**
* Метод: CD₃-метилирование –COOH (Δ = 17.03448 Da), CD₃CO-ацилирование –OH (Δ = 45.02939 Da), режим [M–H]⁻, назначение CHON-формул полным перебором с правилами Lewis/Senior и ppm-окном 0.5 ppm.
* Эталонная конфигурация = секция `test_mode` (`force=2.0`, `intensity=None`, `rel_error_ppm=0.5`, `ppm_tol=0.5`, `max_groups=20`, `min_series_length=1`, `match_ppm=0.5`).
* Метрики на 5 собственных синтетических наборах (таблица §2).
* Архитектура, CLI, GUI, воспроизводимость тестов (424 теста, 26.15 с), лицензия MPL-2.0, Python ≥ 3.10.
* Известные ограничения и запланированные доработки (§3, §4) как раздел «Limitations / Future work».

**Нельзя утверждать:**
1. Результаты на реальных образцах NOM/HS.
2. Сравнение с независимым ПО.
3. Выполнение порога `wrong_ratio ≤ 0.15` для –OH (канонический прогон: 5 FAIL).
4. Эффективность изотопного M+1-фильтра (0/531 измеримых M+1).
5. Поддержку положительной ионизации, аддуктов, многозарядных ионов, HDX, рекалибровки масс.
6. Настраиваемость диапазонов элементов (D1).
7. Применение порогов `max_hc/max_oc/max_nc/max_dbe` из конфига (D3).
8. Источники моноизотопных масс и коэффициентов Бейнона.
9. DOI/архивацию Zenodo.
10. Воспроизводимость эталонного прогона через `python -m src.core.pipeline._test --test` (D6).
11. Числа тестов «105 / 318 / 419» из документации (фактически 424).

---

## 6. Остающиеся неопределённости

1. **Веса soft-фильтров.** «Сохранить из конфига» задаёт только пороги (`max_hc 3.0`, `max_oc 1.2`, `max_nc 1.0`, `max_dbe 30.0`). Коэффициенты/наклоны штрафов в конфиге отсутствуют — сейчас жёстко заданы `0.5`, `2.0`, `2.0`, `2.0` (`_assign.py:162–168`). Нужно добавить их в `pipeline.json → formula_search`. Переход DBE 20→30 и N/C 0.3→1.0 **ослабит** текущий неявный отбор; требуется выбрать веса так, чтобы доля высокоазотистых кандидатов не выросла.
2. **`nom_weight`.** В эталонной конфигурации не задан; фактически 1.0 в `_test_set.py`, 5.0 в `test_pipeline_integration.py`.
3. **Массовое окно assign.** В `test_mode.assign` — `null/null`, в остальных точках входа 0/1000; при `null` окно берётся из min/max наблюдённых масс (зависит от набора).
4. **`max_consecutive_misses = 3`** не вынесен в `pipeline.json`.
5. **`max_components` GMM**: код 15, `constants/noise.json` 5 (не читается).

---

## 7. Сводка изменений к отчёту после уточнений

| Раздел | Изменение |
|---|---|
| §1.3, §5.2 | ионизация — только [M–H]⁻ (подтв. автор) |
| §4.3, §7.6, §11 | эталон шумоподавления: `force=2.0, intensity=None` (GMM активен) |
| §11.4–11.5 | канонический `wrong_ratio` — с общим знаменателем; эталонный прогон = 5 FAIL для dacet |
| §5.5, §5.9 | `max_*` — soft-фильтры из конфига; сейчас не применяются и не переопределены |
| §5.6, §9.2 | DBE `+O/2` — подтверждённый дефект, латентный (0/492 изменений) |
| §6.2 | заявленные стандартные диапазоны C4–40/H0–100/O0–12/N0–12 отсутствуют в репозитории |
| §2 (R30) | штатные точки входа не воспроизводят эталонную конфигурацию |
| §15.4 | обновлён список недопустимых утверждений |
| — | добавлены каноническая конфигурация, канонические метрики и план работ с ADR/reference-equivalence |

---

# ЧАСТЬ III. ПОЛНЫЙ ПЕРЕЧЕНЬ ПРОБЛЕМ КОДА

Методика: статический анализ + запуск (см. команды в тексте), порядок приоритетов скилла `code-review-reliability-first` (стабильность → корректность → тестируемость → читаемость → производительность → стиль).
Обозначения критичности: **BLOCKER** — заявленная функция не работает или падение на штатном сценарии; **MAJOR** — неверный результат, тихая деградация, потеря функциональности; **MINOR** — краевые условия, сопровождаемость.
Всего найдено **86** проблем: 20 стабильность, 24 корректность, 11 тестируемость, 15 читаемость, 5 производительность, 11 стиль.

---

## 🔴 СТАБИЛЬНОСТЬ (20)

| ID | Крит. | Файл:строки | Проблема | Сценарий / последствие | Статус |
|---|---|---|---|---|---|
| S-01 | BLOCKER | `src/core/pipeline/_run.py:277–285` | `brutto_dict` не передаётся в `assign_formulas` | GUI-поля элементов, `--element-ranges`, `element_ranges` пресетов молча не действуют; проверено: результат идентичен при `C:1-1` и по умолчанию | подтв. автор |
| S-02 | MAJOR | `src/core/pipeline/_run.py:277–285` | `sign` не передаётся → `ion_mode` всегда `[M-H]-` | `--sign +`, GUI «Знак иона» молча не работают; проверено: таблицы побитово идентичны | подтв. автор |
| S-03 | MAJOR | `src/core/pipeline/_stages.py:102–141` | `denoise` в try/except: при исключении конвейер продолжается на **неотфильтрованном** спектре, `stats.*_denoised` не обновляется | тихая деградация качества; причина не видна в итоговой таблице | новое |
| S-04 | MAJOR | `src/core/pipeline/_stages.py:198–201` | `find_series` в try/except возвращает пустой DataFrame | все `N_COOH`/`N_OH` = 0, результат внешне «корректен», ошибка только в `messages` | новое |
| S-05 | MAJOR | `src/core/pipeline/_run.py:305–309` | исключение в `assign_formulas` → `n_assigned = 0`, конвейер продолжается | итоговая таблица пуста, причина только в логе | новое |
| S-06 | MAJOR | `src/core/spectrum/_assign.py:85–93, 188–238` | нет проверки `pd.isna(mass)` перед арифметикой | пустой спектр → `float('nan')` в окне → `ValueError: cannot convert float NaN to integer` (подтверждено xfail-тестом `test_spectrum_ops.py:271`) | код, xfail |
| S-07 | MINOR | `src/cli.py:142–143` | `_parse_element_ranges` вне try/except | `--element-ranges "C:abc"` → необработанный `ValueError` с traceback вместо сообщения об ошибке и кода 1 | измерено |
| S-08 | MAJOR | `src/cli.py:172–173` | любое непустое `res.messages` → `return 1` **до** записи результата | предупреждение визуализации лишает пользователя валидной таблицы; `messages` смешивает ошибки и warning'и | новое |
| S-09 | MINOR | `src/core/domain/spectrum.py:136–145` | `_df_to_peaks`: `int(charge.iloc[i])` / `float(rt.iloc[i])` без проверки NaN | колонка `charge`/`rt` с NaN → `ValueError` при создании `Spectrum` | новое |
| S-10 | MINOR | `src/core/spectrum/_load.py:107,123` | `df.rename(columns=mapper)` без проверки дубликатов | маппер, дающий два `mass`, → `df[["mass","intensity"]]` возвращает DataFrame → исключение далее | новое |
| S-11 | MINOR | `src/core/domain/spectrum.py:288–316` | `noise_filter`: `quantile` не валидируется (0..1); при <3 положительных интенсивностях фильтрация тихо отключается | `quantile=1.5` не даёт понятной ошибки; вырожденные спектры не фильтруются | новое |
| S-12 | MINOR | `src/core/io/mzml_bridge.py:182–183` | `reader.close()` без `hasattr`-проверки | на версиях pymzml без `close()` — `AttributeError` в `finally`, маскирующий исходную ошибку | новое |
| S-13 | MAJOR | `src/core/formula_db/_manager.py:18, 44` | `import requests` на уровне модуля; `import platformdirs` без fallback, при **незадекларированных** зависимостях | `ImportError` при импорте модуля (в `pyproject.toml`/`requirements.txt` их нет; CI ставит `requests` вручную) | измерено |
| S-14 | MINOR | `src/ui/_log.py:97–112` | `_on_close` вызывает `os._exit(0)` | пропускаются atexit-хуки и сброс буферов; Tk не завершается штатно; возможна потеря хвоста лога | новое |
| S-15 | MAJOR | `src/app.py:33` | `matplotlib.use("TkAgg")` на уровне модуля | импорт `src.app`/`src.ui` на headless-системе падает; CLI это не затрагивает только потому, что он не импортирует GUI | новое |
| S-16 | MINOR | `src/__main__.py:3–5` | вызов `main()` при импорте модуля (нет `if __name__ == "__main__"`) | `import src.__main__` запускает GUI; несовместимо с тестами/инструментами | новое |
| S-17 | MINOR | `src/ui/_run.py:185–186, 216–217` | подмена `sys.stdout/stderr` глобальна, а не thread-local | параллельный запуск пайплайна и batch-режима искажают поток вывода | новое |
| S-18 | MAJOR | `src/ui/plots.py:36–47` | `clear_canvas` вызывает `plt.close("all")` | закрывает **все** фигуры процесса, включая сохранённые в `self._vk_figure` / `self._histograms_figure`; последующее сохранение PNG падает | новое |
| S-19 | BLOCKER | `src/core/pipeline/_test.py:85` и др. `print` с кириллицей | `UnicodeEncodeError` (cp1252) на Windows | `python -m src.core.pipeline._test --test` падает до вычислений; воспроизведено; обходится только `PYTHONIOENCODING=utf-8` | измерено |
| S-20 | BLOCKER | `pyproject.toml:59–60`; `tools/NOM_HRMS_FGA.spec:58–67` | `package-data src = ["configs/*.json"]` не включает `configs/constants/*.json` и `configs/presets/*.json`; в spec — то же для `constants/` | после `pip install` / в `.exe` `import src.configs` падает с `ConfigError` (модульные `NOISE_CFG`/`ISOTOPE_CFG`), пресеты недоступны | измерено (по конфигурации) |

---

## 🟠 КОРРЕКТНОСТЬ (24)

| ID | Крит. | Файл:строки | Проблема | Последствие | Статус |
|---|---|---|---|---|---|
| K-01 | MAJOR | `src/core/spectrum/_assign.py:150` | DBE в скоринге `1 + C − H/2 + O/2` вместо `+ N/2` | неверный soft-штраф `dbe_pen`; измерено: 0 изменений на 492 пиках (латентный) | подтв. автор |
| K-02 | **BLOCKER** | `src/core/statistics.py:37–40` | **AI реализован неверно**: `(1 + C − O − S − 0.5H)/(C − O − S − N)`; по Koch & Dittmar (2006) — `(1 + C − 0.5O − S − 0.5H)/(C − 0.5O − S − N)` — кислород не поделён на 2 (и в числителе, и в знаменателе) | завышенный AI на всех O-содержащих формулах; искажены гистограмма AI и PDF-отчёт; классификация «ароматично/конденсировано» недостоверна; docstring воспроизводит ошибочную формулу | **новое** (проверено по первоисточнику) |
| K-03 | BLOCKER | `src/core/spectrum/_generate.py:48–115` | мягкие фильтры `max_hc/max_oc/max_nc/max_dbe/min_c` не применяются и нигде не переопределены | фактический отбор кандидатов не соответствует конфигу и документации | подтв. автор |
| K-04 | MAJOR | `src/core/spectrum/_assign.py:162–168` | soft-пороги захардкожены: DBE > 20, N/C > 0.3, N > 3; в конфиге — 30.0 / 1.0 | пороги в коде и в `pipeline.json` расходятся в 1.5–3 раза | подтв. автор |
| K-05 | MAJOR | `pipeline.json`; `presets/*.json` | заявленные стандартные диапазоны C 4–40 / H 0–100 / O 0–12 / N 0–12 отсутствуют в репозитории (три набора не совпадают с ними) | после починки `brutto_dict` потребуется отдельная правка конфигов | подтв. автор |
| K-06 | BLOCKER | `src/core/pipeline/_test_verify.py:68–118` | `wrong_ratio` включает молекулы с `expected_len == 0` (серия не ожидалась) | dacet 51.6–71.0 % при пороге 15 % на всех 5 наборах, при фактических 100 % совпадений длин серий для молекул с OH | подтв. автор (дефект метрики) |
| K-07 | MAJOR | `src/core/spectrum/_assign.py:201–219`; `_chem.py:159–211` | изотопный фильтр: (а) на тест-данных M+1 отсутствует (0 из 531 измеримых), (б) при несовпадении штраф +2.0 добавляется **всем** кандидатам, т.к. `cand_m1_theor > 0` всегда (C ≥ 1) | argmin не меняется; фильтр де-факто не фильтрует | измерено |
| K-08 | MAJOR | `src/core/spectrum/_series.py:34–45, 132–176` | `_find_peak` не исключает уже использованные пики deriv | один пик дериватизированного спектра засчитывается несколькими родительскими ионами → завышение `n_groups` | новое |
| K-09 | MAJOR | `src/core/spectrum/_series.py:155` | `_neutral_to_ion_mass(..., CHEM.default_ion_mode)` жёстко | при любом ином режиме ионизации длины серий считаются для `[M-H]-` | новое |
| K-10 | BLOCKER | `src/core/pipeline/_run.py:47–63`; `_test.py:31–43` | `run_pipeline(test_mode=True)` не читает `PIPELINE.test_mode` | эталонный прогон через штатную точку входа даёт `rel_error=1.0`, `ppm_tol=5.0`, окно 0/1000 вместо 0.5/0.5/None; assign_recall 96.8 % вместо 100 % | новое (каноничность подтв. автором) |
| K-11 | MINOR | `src/core/spectrum/_build.py:44, 56, 64–66` | merge по `mass.round(4)` | два пика в пределах 1e-4 дают дубликаты строк / ложные склейки серий | новое |
| K-12 | MINOR | `src/core/pipeline/_run.py:470–490` | `sign` записывается в метаданные JSON как параметр запуска | метаданные недостоверны: указан режим, который не применялся | новое |
| K-13 | MINOR | `src/core/batch.py:95–97` | `avg_mass` — невзвешенное среднее по пикам | смещение оценки при неравных интенсивностях; Mn/Mw/AIn отсутствуют | новое |
| K-14 | MAJOR | `src/sim/process_pubchem_candidates.py:25–26` | `OUTPUT_VK_PATH == OUTPUT_FILTERED_PATH` | второй `to_csv` перезаписывает файл, записанный первым → потеря промежуточного артефакта | новое |
| K-15 | MAJOR | `src/sim/process_pubchem_candidates.py:120` | `mask_mass = True` | фильтр по массе заявлен, но фактически отключён | новое |
| K-16 | MAJOR | `src/sim/generate_test_sets.py:102, 117, 119, 126–129` | `intensity.max_intensity`, `conversion_yield`, `rounding`, `adducts` не используются; все степени замещения имеют интенсивность ровно 1000 | симуляция не проверяет выход реакции, динамический диапазон и частичное мечение → валидация завышена | новое |
| K-17 | MAJOR | `src/core/formula_db/_manager.py:46, 60–99, 146` | (а) `mp.with_suffix(".manifest.json.part")` даёт `…manifest.manifest.json.part`; (б) `is_available()/get_reader()` ищут БД в `platformdirs.user_data_dir`, а поставленная БД лежит в `data/formula_db/` | скачиваемая/поставляемая БД не находится; путь `.part` не совпадает с ожидаемым | новое |
| K-18 | MAJOR | `src/configs/constants/spectrum_load.json`; `_load.py:9, 15–24` | конфигурируемый маппинг колонок не используется, работает захардкоженный `CSV_COLUMN_MAPPER` | правка JSON не влияет; синонимы `resolution/charge/rt` недоступны | новое |
| K-19 | MAJOR | `src/configs/constants/formula_search.json` | файл не входит в `loader._CONFIG_FILES` | правка диапазонов через него не даёт эффекта (мёртвый конфиг) | новое |
| K-20 | MAJOR | `src/core/spectrum/_denoise.py:68`; `constants/noise.json` | `max_iter` 200 (код) vs 100 (конфиг); `max_components` 15 (код) vs 5 (конфиг) | параметры из конфига не читаются; поведение GMM не соответствует конфигу | измерено (grep) |
| K-21 | MAJOR | `tools/NOM_HRMS_FGA.spec:89` | `openpyxl` в `excludes` | XLSX-экспорт/загрузка в `.exe` перестают работать | новое |
| K-22 | MINOR | `src/core/statistics.py:18–23` | `dbe()` не клампится, в отличие от `_chem.dbe_from_counts` | отрицательные DBE попадают в гистограмму; несогласованность API | новое |
| K-23 | MINOR | `src/core/van_krevelen.py:256–266` | при `color_by="N_OH"` без колонок `n_oh`/`n_cooh` — `KeyError` вместо понятной ошибки | падение на валидном по смыслу входе | новое |
| K-24 | MINOR | `src/core/van_krevelen.py:148–154` | обязательна колонка `N_COOH` даже при `color_by="N_OH"` | нельзя построить диаграмму только по `N_OH` | новое |

---

## 🟡 ТЕСТИРУЕМОСТЬ (11)

| ID | Крит. | Файл:строки | Проблема |
|---|---|---|---|
| T-01 | MAJOR | `tests/` (все) | `@pytest.mark.unit` стоит только на 24 из 424 тестов; маркеры `slow`/`smoke`/`integration` не используются → `pytest -m unit` = `24 passed, 400 deselected`, `-m smoke` = 0 тестов (противоречит README) |
| T-02 | MINOR | `tests/integration/test_pipeline_integration.py:248, 270, 303, 311` | хардкод `0.5` ppm и параметров вместо `PIPELINE.test_mode` |
| T-03 | MAJOR | `tests/integration/test_pipeline_integration.py:506–507, 547–548` | неканонический знаменатель `wrong_ratio` (только молекулы с ожидаемыми OH) → тест зелёный, тогда как канонический критерий даёт 5 FAIL |
| T-04 | MINOR | `tests/unit/test_assign_formulas.py:16–18, 250–261` | использование устаревшего `PIPELINE.default_brutto_dict` как критерия приёмки |
| T-05 | MAJOR | `pyproject.toml`, `requirements.txt` | покрытие кода не измеряется: `pytest-cov`/`coverage` не заявлены и отсутствуют в окружении |
| T-06 | MINOR | `src/core/spectrum/_denoise.py`, `_visualize.py`, `chemistry/_visualize.py`, `core/report.py` | без прямых тестов: `fit_gmm_1d`, `bic`, `gaussian_intersection`, `visualize_series`, `find_and_visualize_molecules`, `_verify_series_against_annotations` |
| T-07 | MINOR | `tests/integration/test_pipeline_integration.py:14` | импорт хелпера из другого тест-модуля (`from tests.unit.test_assign_formulas import normalize_brutto`) — хрупкая связность |
| T-08 | MAJOR | `tests/unit/test_denoise.py:34` | `force=10.0` фактически не тестируется (перекрыт `intensity=100`) → режим `force` без покрытия |
| T-09 | MAJOR | `src/testing/smoke_runner.py:178–182` | импорт несуществующего `assign_formulas_simple` → блок построения серий всегда падает и глушится; smoke-тест не проверяет серии |
| T-10 | MINOR | `pytest.ini` + `pyproject.toml:62–72` | дублирование конфигурации pytest в двух местах |
| T-11 | MAJOR | `tests/` | нет тестов на: `--element-ranges`, `sign`/положительный режим, пресеты (кроме `--preset soil`), GUI (кроме одного smoke), CLI `--noise-*`, XLSX/JSON-экспорт на больших таблицах |

---

## 🟢 ЧИТАЕМОСТЬ И ПОДДЕРЖИВАЕМОСТЬ (15)

| ID | Файл:строки | Проблема |
|---|---|---|
| R-01 | `src/core/spectrum/_denoise.py:32` | docstring «Default 1.5» при фактическом `force=2.0` |
| R-02 | `src/core/spectrum/_load.py:73` | docstring «Defaults 200.0 and 700.0» при фактических 100.0/800.0 |
| R-03 | `src/core/spectrum/_build.py:29–31` | docstring упоминает `N_OH_total`, которого в коде нет |
| R-04 | `src/core/spectrum/_chem.py:96–102` и `_generate.py:201–207` | `_NOM_REGION_CENTERS` продублирован; копия в `_generate.py` мёртвая |
| R-05 | `src/core/spectrum/_generate.py:209–211` | обрывок комментария без кода в конце модуля |
| R-06 | `_cache.py`, `timer.py`, `_test.py:16–27`, `_run.py:317–330`, `app.py:116`, `ui/_config.py:6`, `ui/plots.py:36` | мёртвый код: `PipelineCache`/`_pipeline_cache`/`PipelineProgress` (импортируются, но не используются), `PipelineTimings` (импортируется в `_run.py`, не используется), `_DERIV_SPECS`, `assigned_only_table`, `_BRUTTO_DEFAULTS` (×2), `clear_canvas` |
| R-07 | `src/core/benchmark.py:41, 51–54` | читается несуществующее поле `res.timings` → блок «Breakdown» никогда не выводится (`F841` скрыт в `.flake8`) |
| R-08 | `src/ui/_params.py`, `_run.py`, `_results.py`, `_plots.py`, `_presets.py`, `_structures.py`, `_tabs.py`, `_build.py`, `_log.py` | копипаст блоков импортов (12–24 неиспользуемых импорта в каждом файле); скрыто per-file-ignores |
| R-09 | `src/core/pipeline/_test.py:28` и `_test_set.py:23` | дублирование `_TEST_MATCH_PPM` |
| R-10 | `src/core/pipeline/_stats.py:8, 11, 29` | неиспользуемый `logger`; `SeriesStats` — обычный класс рядом с `@dataclass(slots=True) PipelineStats` |
| R-11 | `src/core/domain/spectrum.py:83–86, 217–221` | docstring «immutable collection», но есть публичный сеттер `.table` |
| R-12 | `.flake8:10–50` | per-file-ignores ссылаются на несуществующие пути (`src/core/spectrum_ops.py`, `src/core/pipeline.py`, `src/core/fragments.py`, `src/core/rdkit_bridge.py`, `src/simulations/*`); новые пути (`src/core/chemistry/fragments.py` и др.) не покрыты; висит `# TODO(#tech-debt)` |
| R-13 | `docs/architecture.md`, `src/README.md`, `data/README.md`, `docs/data_sources.md`, `docs/user_guide.md`, `.deepcode/skills/*` | описывают несуществующую структуру и параметры (см. R3, R5–R9, R11, R15, R22 в Части I) |
| R-14 | `src/app.py:57–68` | fallback-константы определяют `BTN`/`FONT`, которых нет в списке импорта из `theme` |
| R-15 | `src/ui/_log.py:99, 111` | локальные `import os as _os` / `import sys as _sys` внутри методов при уже импортированных модулях |

---

## ⚪ ПРОИЗВОДИТЕЛЬНОСТЬ (5)

| ID | Файл:строки | Проблема | Измерение |
|---|---|---|---|
| P-01 | `src/core/pipeline/_helpers.py:112–135`; `_test_set.py:202–212, 270–275` | `_match_row_by_mass` делает `table.copy()` на каждый вызов, вызывается в цикле по всем аннотациям → O(n·m) копий DataFrame | тест-режим 6.2 с; масштабируется линейно по числу пиков × аннотаций |
| P-02 | `src/core/spectrum/_assign.py:188–238` | на каждый пик — `np.abs((cand_masses_ion − mass_obs)/mass_obs*1e6)` по всему массиву кандидатов | 147 061 кандидат на окно 200–700 Da; `assign_formulas` 0.28 с на 531 пик |
| P-03 | `src/core/spectrum/_denoise.py:64–155` | матрица `n×K` (до 5000×15) + циклы по K внутри EM, до 200 итераций | `force=2.0` → 316 из 531 пиков; отдельный замер не делался |
| P-04 | `data/formula_db/` | 36 232 461 Б `.fdb` + 2 519 764 Б manifest в git | замедляет клонирование; модуль не используется конвейером |
| P-05 | `tools/ai_workflow.py` | 1 620 строк в одном файле вне package discovery | — |

---

## 🔵 СТИЛЬ (11)

| ID | Файл:строки | Проблема |
|---|---|---|
| L-01 | `_run.py:298, 319`, `_test.py`, `_test_set.py`, `_helpers.py:132` | 6 сравнений `== True` / `== False` (E712), скрыты `# noqa` и per-file-ignores |
| L-02 | `src/core/spectrum/__init__.py:13–76` | экспорт приватных имён (`_assign`, `_chem`, `_beyon_*`, …) — приватный API закреплён как публичный |
| L-03 | `pyproject.toml:20` | classifier `GPL-3.0 License` при `license = {text = "MPL-2.0"}` |
| L-04 | `requirements.txt:44–56` | `pymzml`, `zstandard` в блоке «опциональные», хотя `zstandard` обязателен для `formula_db` |
| L-05 | `src/core/formula_db/_packed.py:81–83` | `ceil_div`: обе ветви тернарного оператора идентичны (избыточность) |
| L-06 | `src/core/formula_db/_builder.py:38` | `PROFILE_VERSION = "dbe_nonnegative_even_p3_s2"` — строковая версия профиля без валидации |
| L-07 | `THIRD_PARTY_NOTICES.md:42` | перечислен `scipy`, отсутствующий в зависимостях и коде |
| L-08 | `.github/CODEOWNERS:2–3` | плейсхолдер-инструкция «Replace <YOUR-GITHUB-USERNAME>» |
| L-09 | `src/core/spectrum/_generate.py:1`, `_constants.py:1`, `_chem.py:1`, `_load.py:1`, `_series.py:1`, `_visualize.py:1`, `pipeline/_stages.py` и др. | заголовок «Auto-generated.» при рукописном коде |
| L-10 | `.gitignore:41–44` | игнорируются `*.csv` и `*.png`, при этом CSV/PNG отслеживаются в git → будущие добавления требуют `git add -f` |
| L-11 | `src/__init__.py` | отсутствует `__all__`; `src/__main__.py` без guard (см. S-16) |

---

## Сводка по критичности

| Критичность | Кол-во | ID |
|---|---|---|
| **BLOCKER** | 7 | S-01, S-19, S-20, K-02, K-03, K-06, K-10 |
| **MAJOR** | 44 | S-02…S-05, S-08, S-13, S-15, S-18, K-01, K-04, K-05, K-07…K-10, K-14…K-21, T-01, T-03, T-05, T-08, T-09, T-11, R-06, R-07, R-12, P-…, L-03 |
| **MINOR** | 35 | остальные |

Проблемы, подтверждённые автором как дефекты: **S-01, S-02, K-01, K-03, K-05, K-06, K-10** (каноничность).
Проблемы, обнаруженные в этом аудите и автором **не подтверждённые**: **K-02** (формула AI — проверена по первоисточнику Koch & Dittmar 2006), K-07, K-08, K-14…K-21, S-03…S-20, T-*, R-*, P-*, L-*.

---

## Проверено и НЕ является проблемой (во избежание ложных находок)

| Проверка | Результат |
|---|---|
| Bare `except:` (голый) | **0** вхождений в `src/`, `tests/`, `tools/` |
| Mutable default arguments (`def f(x=[])`) | **0** |
| `import *` | **0** |
| Согласованность `FRAGMENT_LIBRARY` (30) ↔ `FUNCTIONAL_GROUPS` (20) ↔ `ALL_FRAGMENTS` (46) | расхождений по `heavy_formula`/`ihd` — **0**; все 30 базовых фрагментов присутствуют в фабриках |
| `flake8 src/ tests/ tools/` | **0 ошибок** (exit 0) |
| `black --check src/ tests/ tools/` | 125 файлов без изменений |
| Циклические импорты | не обнаружены (все тесты и CLI запускаются) |
| `pytest tests/ -q` | 422 passed, 1 skipped, 1 xfailed за 26.15 с |

> Примечание: `FUNCTIONAL_GROUPS` содержит `f`, `cl`, `br`, `i`, которые **закомментированы** в `ALL_FRAGMENTS` (`fragments.py:148–151`) — добавление их в `FRAGMENT_LIBRARY` приведёт к `ValueError: Фрагмент '…' не найден в библиотеке` в `assemble_molecule_from_combination`. Сейчас это латентный риск, а не активный дефект.

---

*Конец документа. Часть I — фактический аудит кода `main` @ `30194d6`; Часть II — уточнения автора, эталонная конфигурация и план исправлений; Часть III — полный перечень проблем кода (86 позиций).*
