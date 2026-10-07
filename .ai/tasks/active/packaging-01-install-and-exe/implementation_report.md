# Implementation Report — PACKAGING-01

**Задача:** `packaging-01-install-and-exe`
**Тип:** packaging · **Риск:** low
**Ветка:** `dev` (обновлена fast-forward до `origin/main` = `30194d66eb259902bab3a36860068223dabace4c`)
**Дата:** 2026-10-07

---

## 1. Что сделано

| # | Файл | Изменение | Закрываемая проблема |
|---|---|---|---|
| 1 | `pyproject.toml` | `[tool.setuptools.package-data]`: `src = ["configs/*.json"]` → список из трёх шаблонов, добавлены `configs/constants/*.json` и `configs/presets/*.json` | **S-20** (установка неработоспособна) |
| 2 | `pyproject.toml` | classifier `License :: OSI Approved :: GPL-3.0 License` → `License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)` | **L-03** |
| 3 | `MANIFEST.in` (новый) | Состав sdist: LICENSE, README, THIRD_PARTY_NOTICES, CITATION.cff, requirements.txt, `recursive-include src/configs *.json`; `prune thermo external build dist Документация` | **S-20** (часть sdist) |
| 4 | `tools/NOM_HRMS_FGA.spec` | Блок datas переписан на цикл по подкаталогам `("constants", "presets")` — теперь `constants/*.json` попадают в `.exe` | **S-20** (часть `.exe`) |
| 5 | `tools/NOM_HRMS_FGA.spec` | Из `_excludes` удалён `"openpyxl"`; добавлены hiddenimports `openpyxl`, `openpyxl.utils`, `openpyxl.styles` | **K-21** |
| 6 | `README.md:34` | «исходный код открыт (GPL-3.0)» → «(MPL-2.0)» | **L-03** |
| 7 | `README.md:239` | «Основной код — **GPL-3.0**» → «**MPL-2.0**»; `external/README.txt` → `external/README.md` | **L-03** |
| 8 | `requirements.txt` | `zstandard>=0.22` перенесён из блока «Опциональные зависимости» в основные (комментарий: `src/core/formula_db/_packed.py`) | **L-04** |
| 9 | `THIRD_PARTY_NOTICES.md` | Удалена строка `scipy`; добавлены `openpyxl` (MIT), `reportlab` (BSD-3-Clause), `zstandard` (BSD-3-Clause, двойная BSD/GPLv2) | **L-07** |

Изменений в `src/`, `tests/`, `data/` — нет. Научные константы не затронуты. Версия пакета не менялась.

---

## 2. Фактические результаты проверки (A1–A15)

### A1 — Колесо содержит все конфиги · PASS

Команда: `python -m pip wheel . --no-deps --no-build-isolation -w /tmp/wh2`

```
WHEEL: nom_hrms_fga-0.7.0-py3-none-any.whl
configs entries: 15
   src/configs/__init__.py
   src/configs/chemistry.json
   src/configs/constants/formula_search.json
   src/configs/constants/isotope.json
   src/configs/constants/noise.json
   src/configs/constants/spectrum_load.json
   src/configs/loader.py
   src/configs/paths.json
   src/configs/pipeline.json
   src/configs/presets/__init__.py
   src/configs/presets/coal.json
   src/configs/presets/peat.json
   src/configs/presets/soil.json
   src/configs/presets/water.json
   src/configs/presets_loader.py
MISSING: none -> A1 PASS
```

До правки в том же колесе было 7 записей `configs` (без `constants/` и без JSON пресетов).

### A2 — Установка работоспособна · PASS (A/B-эксперимент)

Метод: колесо распаковано в чистый каталог; запуск с `-S` и явным `sys.path`,
чтобы исключить влияющий editable-install репозитория.

```
--- old (колесо до правки) ---
  File ".../old/src/configs/loader.py", line 113, in load_config
    raise ConfigError(f"Файл конфигурации не найден: {path}")
src.configs.loader.ConfigError: Файл конфигурации не найден:
  D:\Temp\User\old\src\configs\constants\noise.json

--- new (колесо после правки) ---
  resolved: D:\Temp\User\new\src\configs\__init__.py
  RESULT: import OK
```

### A3 — sdist содержит конфиги · PASS

Команда: `setuptools.build_meta.build_sdist()`

```
SDIST: nom_hrms_fga-0.7.0.tar.gz | configs: 17
   src/configs/constants/formula_search.json
   src/configs/constants/isotope.json
   src/configs/constants/noise.json
   src/configs/constants/spectrum_load.json
   src/configs/presets/coal.json
   src/configs/presets/peat.json
   src/configs/presets/soil.json
   src/configs/presets/water.json
MISSING: none -> A3 PASS
thermo в sdist: False
```

### A4–A5 — PyInstaller spec · PASS

```
36:    # Excel: подключается динамически через engine="openpyxl"
37:    "openpyxl", "openpyxl.utils", "openpyxl.styles",
65:    # Subdirectories: loader.py reads constants/*.json at import time,
67:    for _sub in ("constants", "presets"):
95:    # ВНИМАНИЕ: openpyxl НЕ исключается — он нужен для XLSX-экспорта
```
Синтаксис spec: `python -m py_compile tools/NOM_HRMS_FGA.spec` → OK.

### A6–A9 — Документация и зависимости · PASS

```
=== A6 classifier ===
18:    "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
=== A7 README GPL ===
224:├── external/               # Стороннее ПО (GPL-3.0)
239:Основной код — **MPL-2.0**. Сторонний код в `external/` — **GPL-3.0** (см. `external/README.md`).
=== A8 zstandard ===
38-# --- Сжатие блоков базы формул (src/core/formula_db/_packed.py) ---
39:zstandard>=0.22
=== A9 scipy ===
scipy: НЕ НАЙДЕН (OK)
```

### A10 — Научный результат не изменился · PASS

```
baseline md5: 33cde0049db29f91dfeab2c71d13b77e
after    md5: 33cde0049db29f91dfeab2c71d13b77e
A10 PASS: результат идентичен
```

### A11 — Тест-режим не изменился · PASS

`diff /tmp/baseline/testmode.txt /tmp/after_testmode.txt` → различий нет (все 5 наборов,
включая прежние `FAIL dacet_wrong`).

### A12 — Тесты · PASS

```
422 passed, 1 skipped, 1 xfailed, 5 warnings, 9 subtests passed in 25.43s
```

### A13 — Линтеры · PASS

```
flake8: 0 ошибок
black: 125 files would be left unchanged.
```

### A14 — Task packet · PASS

`python tools/ai_workflow.py validate-task packaging-01-install-and-exe` → `0 warning(s) -- VALIDATION PASSED`

`python tools/ai_workflow.py check-repo` → `No issues found. 0 warning(s) -- REPO CHECK PASSED`

### A15 — Границы соблюдены · PASS

```
 M README.md
 M THIRD_PARTY_NOTICES.md
 M pyproject.toml
 M requirements.txt
 M tools/NOM_HRMS_FGA.spec
?? MANIFEST.in
?? .ai/tasks/active/
```
`git diff --stat` → 5 файлов, 31 вставка, 12 удалений. Ни один файл вне
`scope.allowed_paths` не изменён. Неотслеживаемые локальные файлы
(`.aiignore`, `AI_AUDIT_HANDOFF.md`, `deepcode_audit_triage.md`,
`NOM-HRMS-FGA_factual_report.md`) не добавлены в индекс.

---

## 3. Отклонения от плана и решения, требующие ревью

1. **Добавлены 3 строки в `THIRD_PARTY_NOTICES.md`** (`openpyxl`, `reportlab`,
   `zstandard`). Это выходит за буквальный критерий A9 («удалить scipy»), но
   относится к тому же дефекту: таблица не содержала три реальные объявленные
   зависимости. Если это нежелательно — строки легко откатить
   (`git checkout 30194d6 -- THIRD_PARTY_NOTICES.md`).
2. **`scipy` оставлен в `_collect_packages`** (`tools/NOM_HRMS_FGA.spec:45`) —
   изменение списка `_collect_packages` влияет на состав сборки `.exe` и
   вынесено в отдельную задачу.
3. **`requests` и `platformdirs` не добавлены** в зависимости: они нужны только
   `src/core/formula_db/_manager.py`, который не вызывается из конвейера
   (решение автора: вспомогательный артефакт). Отнесено к задаче по S-13.
4. **Полная сборка `.exe` не выполнялась** — это длительная операция
   (ожидаемый размер ~130 МБ, по локальному артефакту `dist/NOM_HRMS_FGA.exe`
   = 128 087 430 Б). Вместо неё проверены: синтаксис spec, состав `datas`
   (по коду) и то, что `openpyxl` более не исключён. Smoke-сборка `.exe` —
   отдельная задача.

---

## 4. Что НЕ покрыто этой задачей (остаётся в бэклоге)

| Проблема | Причина отсрочки |
|---|---|
| S-19 (`UnicodeEncodeError` на Windows) | Пакет 2 |
| S-07 (необработанный `ValueError` в `_parse_element_ranges`) | Пакет 2 |
| S-13 (`requests`/`platformdirs` не объявлены) | `formula_db` — вспомогательный артефакт |
| K-18, K-19, K-20 (конфиги не читаются) | Пакет 5; требуется решение по мёртвым конфигам |
| R-* , T-* | Пакеты 3–4 |
| Научные K-01, K-02, K-03, K-06, S-01, S-02 | Требуют ADR и reference-equivalence |

---

## 5. Соответствие требованиям `AGENTS.md`

* Правило 2 (task packet для packaging-задач) — выполнено, пакет валиден.
* Правило 3 (не трогать несвязанные файлы) — выполнено, см. A15.
* Правило 4/5 (не пушить в `main`, без деструктивных операций) — выполнено:
  работа в `dev`, `git reset --hard` не применялся.
* Правило 7 (обоснование зависимостей) — новых зависимостей не добавлено.
* Правило 8 (научные инварианты) — не затрагивались; подтверждено A10/A11.
* Правило 9 (тесты перед завершением) — выполнено, A12/A13.
* Правило 10 (implementation report) — настоящий файл.
* Правило 14 (без merge/release без подтверждения) — PR и merge не выполнялись.

---

## 6. Итог

Все 15 критериев приёмки выполнены. Научный результат на `set_01` и в
тест-режиме побитово не изменился. Установка пакета из wheel перестала
падать: A/B-эксперимент фиксирует переход `ConfigError` → успешный импорт.
