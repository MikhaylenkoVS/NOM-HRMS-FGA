# Acceptance — PACKAGING-01

## Критерии приёмки (проверяемые)

| # | Критерий | Команда / метод проверки | Ожидаемый результат |
|---|---|---|---|
| A1 | Колесо содержит все конфиги | `python -m pip wheel . --no-deps --no-build-isolation -w /tmp/wh` затем список содержимого архива | присутствуют `src/configs/constants/{noise,isotope,spectrum_load,formula_search}.json` и `src/configs/presets/{coal,peat,soil,water}.json` |
| A2 | Установка работоспособна | распаковка колеса в чистый каталог; `python -c "import src.configs"` с приоритетом распакованного пути | импорт без исключений (до правки — `ConfigError`) |
| A3 | sdist содержит конфиги | сборка sdist + просмотр архива | `src/configs/constants/*.json` и `src/configs/presets/*.json` в архиве |
| A4 | PyInstaller spec включает constants | чтение `tools/NOM_HRMS_FGA.spec`, блок datas | добавлен подкаталог `constants` |
| A5 | `openpyxl` не исключён из .exe | чтение `_excludes` | `"openpyxl"` отсутствует |
| A6 | Classifier лицензии | чтение `pyproject.toml` | `License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)` |
| A7 | README не содержит GPL-3.0 для основного кода | `grep -n "GPL" README.md` | остаётся только строка про `external/` (GPL-3.0 стороннего ПО) |
| A8 | `zstandard` в обязательных зависимостях | чтение `requirements.txt` | в основном блоке, не в «опциональных» |
| A9 | `scipy` отсутствует в notices | `grep -n "scipy" THIRD_PARTY_NOTICES.md` | нет совпадений |
| A10 | **Научный результат не изменился** | прогон CLI на `set_01` + `md5sum` | md5 выходного CSV == `33cde0049db29f91dfeab2c71d13b77e` (базовая линия) |
| A11 | Тест-режим не изменился | `python -m src.core.pipeline._test --test` | вывод побайтово совпадает с базовой линией `/tmp/baseline/testmode.txt` |
| A12 | Тесты зелёные | `pytest tests/ -q` | 422 passed, 1 skipped, 1 xfailed |
| A13 | Линтеры чистые | `flake8 src/ tests/ tools/` + `black --check src/ tests/ tools/` | 0 ошибок, 125 файлов без изменений |
| A14 | Task packet валиден | `python tools/ai_workflow.py validate-task packaging-01-install-and-exe` | 0 errors |
| A15 | Границы соблюдены | `git status --short` + `git diff --stat` | изменены только файлы из `scope.allowed_paths` |

## Критерии «не сделано» (стоп-факторы)

* Любое изменение в `src/` или `tests/` — нарушение границ задачи.
* Изменение md5 результата на `set_01`.
* Падение любого теста из `pytest tests/ -q`.
* Появление новых зависимостей в `pyproject.toml`.
* Изменение версии пакета.

## Не входит в приёмку (отдельные задачи)

* Полная сборка `NOM_HRMS_FGA.exe` и smoke-тест (длительная операция; проверяется отдельной задачей, либо вручную).
* Удаление `scipy` из `_collect_packages` в spec.
* Подключение/удаление мёртвых конфигов `constants/formula_search.json` и `constants/spectrum_load.json`.
* Добавление `requests`/`platformdirs` в зависимости (`formula_db` — вспомогательный артефакт).

## Definition of Done

1. Все A1–A15 выполнены.
2. `implementation_report.md` заполнен фактическими выводами команд.
3. Изменения закоммичены в `dev` (по подзадачам, отдельными коммитами).
4. Сводный отчёт по форме §6 `code-change-protocol` выдан пользователю.
5. PR не создаётся и merge не выполняется без явной команды человека.
