# План веб-миграции «СпектраЛаб» (tkinter → FastAPI + HTMX)

> **Создан:** 2026-08-12 | **Статус:** 🔴 в работе | **Дедлайн:** поэтапно (см. milestones)

## Сводка

Перевод текущего tkinter-интерфейса NOM-HRMS-FGA в веб-интерфейс «СпектраЛаб» по
упрощённому стеку: Python 3.11 + FastAPI, Jinja2 + HTMX, uPlot, SQLite, локальная
папка `./data`. Ядро `src/core` подключается как модуль **без переписывания**.
Веб-версия на любом этапе остаётся **опциональной надстройкой** над рабочим
десктоп-инструментом, а не заменой, до полного подтверждения эквивалентности
результатов на наборах `set_01`–`set_05`.

Приоритет: **надёжность → читаемость → оптимизация**. Научные инварианты не
меняются без ADR и регрессионных тестов.

## Версионная привязка (важно)

- Ядро NOM-HRMS-FGA продолжает линейку версий **v0.6.1 → v0.7 → v0.8 → v0.9 → v1.0**
  (milestones GitHub ядра: «Инструменты пользователя», «Научная полнота»,
  «Публикационная готовность», «Релиз»).
- Реструктуризация каталогов и рефакторинг (`docs/plans/v0.7-directory-restructure.md`,
  `docs/plans/v0.7-refactoring-plan.md`) фактически вошли в v0.6.0.
- «СпектраЛаб» — **отдельная линейка версий** `v0.1 → v0.2 → v0.3 → v0.4`, не
  пересекается с линейкой ядра.

## Контекст и допущения (зафиксированы по фактическому коду)

1. Реальный пайплайн — тройной NOM-анализ, а не «SNIP → SG → нормализация → пики»:
   `src/core/pipeline/_run.py::run_pipeline(src_path, dmet_path, dacet_path, ...)`
   выполняет `load → denoise (адаптивный порог шума) → assign_formulas →
   find_series → build_result_table` по **трём** спектрам (original +
   дейтерометилированный + дейтероацилированный). Поэтому `POST /spectra` — загрузка
   одного CSV, а `POST /process` принимает **тройку** `spectrum_id`. Черновой
   API-контракт сохранён по именам, расширен под тройку (требование домена).
2. `src/core/spectrum_ops.py` не существует — код в пакете `src/core/spectrum/`.
   tkinter в `src/core/` отсутствует (только `src/app.py` и `src/ui/`). Но
   `src/core/__init__.py` **жадно** импортирует RDKit и matplotlib — проблема для
   headless-сервера (см. SPECTRALAB-01).
3. Тест-наборы — `data/test_sets/set_01`…`set_05` (не `set01`), каждый с файлами
   `original.csv`, `deutermethylated.csv`, `deuteroacylated.csv`, `annotations.csv`,
   `molecules.csv`.
4. Chemical-validity тесты лежат в `tests/unit/test_chemical_validity.py`
   (не в `src/testing/`). `src/testing/` — smoke_runner, artifact_export,
   report_models, structure_export. HTTP-тесты размещаем в `tests/integration/`.
5. Интеграция с GitHub MCP в текущем окружении недоступна — issues оформлены как
   готовые markdown-блоки для ручной вставки.

## Milestones

| Milestone | Название | Срок | Тип |
|-----------|----------|------|-----|
| `v0.1` | СпектраЛаб MVP-каркас | недели 1–3 (до ~2026-08-28) | релизный трек |
| `v0.2` | СпектраЛаб обработка и экспорт | недели 3–5 (до ~2026-09-11) | релизный трек |
| `v0.3` | СпектраЛаб удобства | по необходимости, недели 6+ | опционально |
| `v0.4` | СпектраЛаб путь роста | без жёсткого срока | по потребности |

## Конвенции labels

- `spectralab/v0.1`, `spectralab/v0.2`, `spectralab/v0.3`, `spectralab/v0.4`
- `type/feature`, `type/refactor`, `type/test`, `type/infra`, `type/docs`
- область: `spectralab`

---

# Milestone: `v0.1` — СпектраЛаб MVP-каркас (недели 1–3)

## SPECTRALAB-01 — Выделить `src/core` в переиспользуемый пакет без tkinter и с лёгким импортом

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/refactor` `spectralab`

**Описание.** `src/core/` уже не зависит от tkinter (зависимость только в `src/app.py`
и `src/ui/`). Но `src/core/__init__.py` при импорте жадно тянет RDKit и matplotlib,
что нежелательно для headless-сервера и замедляет холодный старт. Нужно гарантировать
чистый и лёгкий импорт вычислительного ядра.

**Инструкция.**
1. Подтвердить отсутствие tkinter: `grep -rn "tkinter" src/core/` → пусто (зафиксировать в PR).
2. Сделать импорт RDKit ленивым в `src/core/chemistry/rdkit_bridge.py` и
   `fragment_combinations.py` (перенести `import rdkit`/`from rdkit...` внутрь функций),
   а matplotlib — ленивым в `src/core/van_krevelen.py` и `src/core/spectrum/_visualize.py`.
3. Добавить лёгкую точку входа (например `src/core/lite.py` или «ленивый»
   `src/core/__init__.py`), реэкспортирующую `run_pipeline`, `load_spectrum`,
   `denoise`, `assign_formulas`, `find_series`, `build_result_table` **без** тяжёлых зависимостей.
4. **Не менять научную логику** — только способ импорта.

**Definition of Done.**
- `python -c "from src.core.pipeline import run_pipeline"` выполняется без tkinter и без импорта RDKit/matplotlib.
- `pytest tests/unit/test_pipeline.py tests/unit/test_van_krevelen.py -q` зелёные.
- Результаты на `set_01` идентичны эталонным (без регрессий).

---

## SPECTRALAB-02 — Инициализировать структуру веб-проекта `spectralab/`

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/infra` `spectralab`

**Описание.** Создать скелет веб-приложения по упрощённому стеку: FastAPI + Jinja2/HTMX
+ SQLite + локальные файлы. Один процесс, минимум компонентов, комфортная поддержка
одним Python-разработчиком.

**Инструкция.**
1. Создать каталоги: `spectralab/app/{main.py,core/,templates/,static/}`,
   `spectralab/data/` (создаётся автоматически), `spectralab/static/{uplot.min.js,app.js}`.
2. Создать `spectralab/requirements.txt`: `fastapi`, `uvicorn[standard]`, `jinja2`,
   `python-multipart`, `sqlmodel` (или чистый `sqlite3`), плюс уже имеющиеся
   `numpy`, `scipy`, `pandas`.
3. Создать `spectralab/run.py` (`uvicorn app.main:app --host 0.0.0.0 --port 8000`).
4. Опционально — `spectralab/Dockerfile` (только если понадобится, не блокирует MVP).
5. Ядро **подключать как модуль** через `sys.path`/`PYTHONPATH` к `src/`, не копировать
   и не переписывать `src/core`.

**Definition of Done.**
- `python run.py` из `spectralab/` поднимает uvicorn.
- Структура соответствует схеме из ТЗ; ядро импортируется из `src/core`, а не дублируется.

---

## SPECTRALAB-03 — Создать FastAPI-каркас с health-check и Jinja2

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/feature` `spectralab`

**Описание.** Минимальное приложение FastAPI с health-check, подключением
Jinja2Templates и базовым шаблоном, чтобы «прогнать» весь стек до бизнес-логики.

**Инструкция.**
1. В `app/main.py` создать `FastAPI(title="СпектраЛаб")`, `lifespan` (инициализация БД
   и папки `data/spectra/`).
2. Добавить `GET /healthz` → `{"status": "ok", "version": ...}`.
3. Подключить `Jinja2Templates(directory="app/templates")`, создать `templates/base.html`
   и `templates/index.html`.
4. Добавить `templates/spectrum.html` как заглушку (HTMX-фрагмент).

**Definition of Done.**
- `GET /healthz` → 200.
- Swagger UI (`/docs`) доступен.
- Тест через `fastapi.testclient.TestClient` проходит (см. SPECTRALAB-14).

---

## SPECTRALAB-04 — Реализовать `POST /spectra` (загрузка CSV) + сохранение файла

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/feature` `spectralab`

**Описание.** Приём одного CSV-спектра через multipart, валидация и сохранение в
`./data/spectra/`, возврат `spectrum_id`.

**Инструкция.**
1. В `app/main.py` (или `app/routes/spectra.py`) добавить `POST /spectra`
   (`UploadFile` + `File`).
2. Валидировать колонки через `src.core.spectrum.CSV_COLUMN_MAPPER` (столбцы
   `m/z`/`mass` и `intensity`); некорректный файл → 422.
3. Генерировать `spectrum_id` (uuid4), сохранить файл как `data/spectra/<id>.csv`.
4. Записать метаданные в SQLite (имя, размер, sha256, дата).

**Definition of Done.**
- Загрузка через Swagger/TestClient возвращает `spectrum_id`.
- Файл присутствует на диске; метаданные в БД.
- Кривой CSV (без `intensity`) → 422, файл не сохраняется.

---

## SPECTRALAB-05 — Ввести SQLite-хранилище метаданных и истории

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/infra` `spectralab`

**Описание.** Локальная БД `data/spectralab.db` для метаданных спектров и истории
обработок. Использовать SQLModel или чистый `sqlite3` — что проще для одного разработчика.

**Инструкция.**
1. Создать `app/db.py` с `init_db()` (`CREATE TABLE IF NOT EXISTS`).
2. Таблицы: `spectra(id, filename, checksum, size, created_at)`;
   `tasks(id, original_id, dmet_id, dacet_id, status, progress, params_json,
   result_csv, error, created_at, finished_at)`.
3. CRUD-хелперы (`create_spectrum`, `get_spectrum`, `list_spectra`, `create_task`,
   `update_task`, `get_task`).
4. Без миграций на этом этапе (schema-on-create).

**Definition of Done.**
- `data/spectralab.db` создаётся автоматически при старте.
- Хелперы покрыты unit-тестом.

---

## SPECTRALAB-06 — Реализовать `GET /spectra` и `GET /spectra/{id}` (+ `?downsample=N`)

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/feature` `spectralab`

**Описание.** Список загруженных спектров и метаданные конкретного спектра с
опциональной децимацией точек для рендера.

**Инструкция.**
1. `GET /spectra` → JSON-список метаданных.
2. `GET /spectra/{id}` → метаданные; при `?downsample=N` вернуть равномерно прореженные
   точки (m/z, intensity) через pandas/numpy (не переписывать `load_spectrum`, а вызвать
   её и проредить).
3. 404 при несуществующем `id`.

**Definition of Done.**
- Список и метаданные корректны.
- `downsample=1000` возвращает ≤1000 точек без искажения формы спектра.
- Покрыто HTTP-тестом.

---

## SPECTRALAB-07 — Базовый шаблон списка спектров (HTMX)

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/feature` `spectralab`

**Описание.** Стартовая страница показывает загруженные спектры и обновляется через
HTMX (частичное обновление без JS-фреймворка).

**Инструкция.**
1. `templates/index.html` — таблица/список спектров, форма загрузки (`hx-post` на `/spectra`).
2. HTMX-фрагмент `templates/_spectra_list.html` для swap после загрузки.
3. Подключить HTMX (CDN или `static/htmx.min.js`).

**Definition of Done.**
- После загрузки файла список обновляется без перезагрузки страницы.
- Никакого JS-фреймворка; вручную проверить в браузере.

---

## SPECTRALAB-08 — Документировать запуск (README: pip install, run.py, systemd/ярлык)

**Milestone:** `v0.1` · **Метки:** `spectralab/v0.1` `type/docs` `spectralab`

**Описание.** Инструкция по развёртыванию СпектраЛаб: от чистой установки до автозапуска
сервисом/ярлыком.

**Инструкция.**
1. `spectralab/README.md`: создание venv, `pip install -r requirements.txt`, `python run.py`.
2. Пример systemd-юнита (`spectralab.service`) и пример ярлыка запуска.
3. Отметить, что веб-версия — опциональная надстройка, десктоп-инструмент продолжает работать.

**Definition of Done.**
- Инструкция воспроизводится на чистом venv.
- Ссылки только на реальные команды/файлы репозитория.

---

# Milestone: `v0.2` — СпектраЛаб обработка и экспорт (недели 3–5)

## SPECTRALAB-09 — Реализовать `POST /process` (синхронный запуск пайплайна)

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/feature` `spectralab`

**Описание.** Запуск существующего `run_pipeline` по тройке спектров через API.
В MVP — синхронно (создаёт задачу, выполняет, возвращает `task_id`).

**Инструкция.**
1. `POST /process` с телом `{original_id, dmet_id, dacet_id, params}`; резолвить
   `spectrum_id` → путь файла.
2. **Не переписывать `src/core`** — вызвать
   `run_pipeline(src_path=..., dmet_path=..., dacet_path=..., output_csv=<data/results/<task_id>.csv>, progress_callback=<обновление task.progress>, **params)`.
3. Создать запись `task` со статусом `queued → running → done/error`, сохранить путь к
   `result_table.csv`.
4. Синхронно выполнить; ошибки ловить и писать в `task.error` (санитизировать трейсбек).
5. Прогресс обновлять через `progress_callback` (в `run_pipeline` уже есть поддержка).

**Definition of Done.**
- Обработка тройки `set_01` → `task_id` со статусом `done`, создан `result_table.csv`.
- Прогресс реально обновляется (0→100).
- Ошибка (битый CSV) → статус `error` + сообщение.

---

## SPECTRALAB-10 — Реализовать `GET /tasks/{id}` (статус и прогресс)

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/feature` `spectralab`

**Описание.** Опрос статуса задачи: `queued/running/done/error` + прогресс `%`.

**Инструкция.**
1. `GET /tasks/{id}` → `{status, progress, error, result_url}`.
2. Читать из таблицы `tasks` (SPECTRALAB-05).
3. 404 при неизвестном `id`.

**Definition of Done.**
- Возвращает корректный статус на каждом этапе.
- Покрыто HTTP-тестом.

---

## SPECTRALAB-11 — Вьюер спектра на uPlot + HTMX (зум, тултипы, таблица пиков)

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/feature` `spectralab`

**Описание.** Единственное место с «настоящим» JS — график на uPlot: отрисовка спектра,
зум/пан, тултип, таблица найденных пиков.

**Инструкция.**
1. `templates/spectrum.html` — канвас для uPlot + таблица пиков (HTMX-фрагменты).
2. `static/app.js` — инициализация uPlot, зум/пан, тултип (m/z, intensity); загрузка
   данных через `fetch` (`GET /spectra/{id}?downsample=N` и `GET /spectra/{id}/peaks`).
3. `static/uplot.min.js` — локальная копия библиотеки.
4. Отрисовка: исходный + денойзованный спектр (оверлей), пики маркерами.

**Definition of Done.**
- Спектр рендерится, зум/пан работают, тултип показывает m/z+intensity.
- Таблица пиков заполняется.
- Вручную проверить в браузере; без JS-фреймворка.

---

## SPECTRALAB-12 — Реализовать `GET /spectra/{id}/peaks` (m/z, интенсивность, С/Ш)

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/feature` `spectralab`

**Описание.** Список найденных пиков спектра с соотношением сигнал/шум, вычисляемым ядром.

**Инструкция.**
1. Вызвать `src.core.spectrum.denoise` + `compute_noise_threshold` (даёт
   `NoiseThresholdResult` — порог шума).
2. Сформировать пики: m/z, интенсивность, С/Ш (интенсивность/порог).
3. Вернуть JSON-массив.

**Definition of Done.**
- JSON с `m/z`, `intensity`, `snr`.
- Числа совпадают с десктоп-денойзом на `set_01`.
- Покрыто HTTP-тестом.

---

## SPECTRALAB-13 — Реализовать `GET /tasks/{id}/export?fmt=csv|json` (CSV минимум)

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/feature` `spectralab`

**Описание.** Выгрузка результата обработки (`result_table`), минимум CSV.

**Инструкция.**
1. Читать сохранённый `result_table.csv` задачи (или генерировать через `build_result_table`).
2. `fmt=csv` → `FileResponse`/`StreamingResponse` с `Content-Disposition`; `fmt=json` → JSON.
3. Столбцы как у `build_result_table`: `mass, intensity, brutto, all_candidates,
   N_COOH, N_OH, missing_*`.

**Definition of Done.**
- CSV скачивается и открывается в Excel/pandas.
- Колонки совпадают с десктоп-экспортом.
- Покрыто HTTP-тестом.

---

## SPECTRALAB-14 — Интеграционные HTTP-тесты через FastAPI TestClient

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/test` `spectralab`

**Описание.** Отдельный набор HTTP-тестов для веб-слоя — независимо от chemical-validity
тестов в `tests/unit/test_chemical_validity.py`.

**Инструкция.**
1. Новый файл `tests/integration/test_web_api.py`.
2. Фикстура: TestClient + временная `data/` (tmp_path), чтобы не трогать репозиторные данные.
3. Покрыть: `healthz`, загрузку, список, метаданные+downsample, `process`, `tasks/{id}`,
   `peaks`, `export`.

**Definition of Done.**
- `pytest tests/integration/test_web_api.py -q` зелёный.
- Не изменяет файлы в `data/` репозитория (изоляция через tmp_path).

---

## SPECTRALAB-15 — Регрессия: веб-пайплайн идентичен десктопу на `set_01`–`set_05`

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/test` `spectralab`

**Описание.** Ключевой научный инвариант: результаты веб-версии должны совпадать с
десктоп-версией на всех эталонных наборах.

**Инструкция.**
1. Тест `tests/integration/test_web_equivalence.py`.
2. Для каждого `data/test_sets/set_0{1..5}`: прогнать `run_pipeline` напрямую (эталон) и
   через HTTP (`POST /process`).
3. Сравнить `result_table` (mass, intensity, brutto, N_COOH, N_OH) с `pytest.approx`/
   порогами из `src/configs/pipeline.json` и `ref_data`.
4. Использовать существующие фикстуры `project_root`, `test_sets_root` из `tests/conftest.py`.

**Definition of Done.**
- Тест проходит на всех 5 наборах; расхождения в пределах допуска.
- Любое расхождение — блокер релиза (веб-версия не считается готовой).

---

## SPECTRALAB-16 — Страница результата: таблица result_table (HTMX)

**Milestone:** `v0.2` · **Метки:** `spectralab/v0.2` `type/feature` `spectralab`

**Описание.** После обработки показывать итоговую таблицу результатов (формулы, N_COOH,
N_OH) на отдельной странице/фрагменте.

**Инструкция.**
1. `templates/result.html` — таблица result_table (данные из `GET /tasks/{id}/export?fmt=json`).
2. HTMX-фрагмент для частичного обновления после завершения задачи.
3. Простая сортировка по массе (серверная, без JS-фреймворка).

**Definition of Done.**
- Таблица результатов рендерится после обработки.
- Вручную проверить на `set_01`.

---

# Milestone: `v0.3` — СпектраЛаб удобства (по необходимости, недели 6+)

> Все issues ниже — опциональные, создаются/выполняются по мере реальной потребности,
> не блокируют MVP.

## SPECTRALAB-17 — Импорт mzML через pymzML

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/feature` `spectralab`

**Описание.** Приём `.mzML` в `POST /spectra` наравне с CSV (через `pymzml`), конвертация
во внутреннее представление.

**Инструкция.** Добавить зависимость `pymzml`; детектор формата по расширению/сигнатуре;
переиспользовать `src/core/io/mzml_bridge.py`, если подходит. Обработка ошибок некорректного mzML.

**Definition of Done.** `.mzML` загружается и обрабатывается; результат совпадает с
CSV-эквивалентом в пределах допуска.

---

## SPECTRALAB-18 — Van Krevelen-диаграмма в результатах

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/feature` `spectralab`

**Описание.** Отрисовка диаграммы Ван-Кревелена для результата обработки.

**Инструкция.** Использовать `src.core.van_krevelen.create_van_krevelen_plot`; рендерить
серверно в PNG (matplotlib, без `TkAgg`) и встраивать в шаблон, либо строить на клиенте.
Убедиться, что используется `matplotlib.use("Agg")`, а не `TkAgg` (как в `src/app.py`).

**Definition of Done.** Диаграмма рендерится на headless-сервере без GUI-бэкенда;
соответствует десктоп-версии.

---

## SPECTRALAB-19 — Сравнение и наложение спектров

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/feature` `spectralab`

**Описание.** Оверлей нескольких спектров в вьюере для визуального сравнения.

**Инструкция.** Расширить `spectrum.html`/`app.js` (uPlot несколько серий);
`GET /spectra/{id}?downsample=N` уже есть — использовать для нескольких id.

**Definition of Done.** Несколько спектров отображаются в одном графике с легендой.

---

## SPECTRALAB-20 — Библиотека спектров / поиск по массе

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/feature` `spectralab`

**Описание.** Возможность помечать спектры и искать по диапазону масс/имени (поверх SQLite).

**Инструкция.** Индекс по m/z-диапазону в `spectra`; простой поиск через
`GET /spectra?q=...` или `?mass_min=&mass_max=`.

**Definition of Done.** Поиск по имени/массе возвращает корректный список.

---

## SPECTRALAB-21 — Лёгкая авторизация: один пароль + cookie-сессия

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/feature` `spectralab`

**Описание.** Опциональный вход по одному паролю для случаев выхода сервера за пределы
локальной машины.

**Инструкция.** `itsdangerous`-подписанная cookie-сессия; пароль из env-переменной;
middleware для защиты маршрутов. Без OAuth/JWT (это — «путь роста»).

**Definition of Done.** Неавторизованный доступ к защищённым маршрутам → 401/redirect;
пароль задаётся из окружения.

---

## SPECTRALAB-22 — Docker-контейнер + volume

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/infra` `spectralab`

**Описание.** Опциональная упаковка в один контейнер с volume для `./data`.

**Инструкция.** `Dockerfile` (python:3.11-slim, `pip install -r requirements.txt`);
`docker run -v ./data:/app/data -p 8000:8000`.

**Definition of Done.** Контейнер собирается и обслуживает `/healthz`; данные сохраняются в volume.

---

## SPECTRALAB-23 — Руководство пользователя веб-версии

**Milestone:** `v0.3` · **Метки:** `spectralab/v0.3` `type/docs` `spectralab`

**Описание.** Документация по работе в СпектраЛаб (загрузка тройки, запуск, просмотр, экспорт).

**Инструкция.** `spectralab/docs/user_guide.md` (или раздел в `docs/`); скриншоты ключевых
экранов; отличие от десктоп-интерфейса.

**Definition of Done.** Новый пользователь по инструкции проходит путь
«загрузка → обработка → экспорт» без подсказок.

---

# Milestone: `v0.4` — СпектраЛаб путь роста (без жёсткого срока)

> Issues создаются только при появлении **конкретной причины** (нагрузка, число
> пользователей, батчи). Не блокируют MVP.

## SPECTRALAB-24 — Перейти на асинхронную обработку: BackgroundTasks → Celery + Redis

**Milestone:** `v0.4` · **Метки:** `spectralab/v0.4` `type/feature` `spectralab`

**Описание.** Для длительных/батч-задач. Сначала `FastAPI BackgroundTasks`, затем
Celery + Redis. WebSocket-прогресс `WS /ws/tasks/{id}`.

**Инструкция.** Вводить ступенчато: (1) BackgroundTasks для выноса `run_pipeline` из
request-потока; (2) при реальных батчах — Celery+Redis, тот же `task_id`;
(3) WS-канал прогресса. API `POST /process` не менять (тот же контракт, асинхронное исполнение).

**Definition of Done.** `POST /process` возвращает `task_id` немедленно, статус
опрашивается; долгая задача не блокирует другие запросы. **Триггер:** реальные батч-сценарии.

---

## SPECTRALAB-25 — Многопользовательская авторизация (OAuth2/JWT)

**Milestone:** `v0.4` · **Метки:** `spectralab/v0.4` `type/feature` `spectralab`

**Описание.** Только при появлении нескольких пользователей/ролей. Заменяет
SPECTRALAB-21 (один пароль) на OAuth2/JWT.

**Инструкция.** Перейти на JWT; при необходимости — внешний IdP.
**Триггер:** многопользовательский сценарий, разграничение прав.

**Definition of Done.** Несколько учёток, разграничение доступа.
**Триггер:** реальные пользователи >1.

---

## SPECTRALAB-26 — Миграция SQLite → PostgreSQL (метаданные)

**Milestone:** `v0.4` · **Метки:** `spectralab/v0.4` `type/infra` `spectralab`

**Описание.** Только при многопользовательском сценарии/конкуренции за БД.
SQLModel облегчает переход.

**Инструкция.** Сменить URL БД, миграция данных.
**Триггер:** конкурентные записи, несколько инстансов.

**Definition of Done.** Приложение работает на PostgreSQL без изменений бизнес-логики.

---

## SPECTRALAB-27 — Вынос файлов в MinIO/S3

**Milestone:** `v0.4` · **Метки:** `spectralab/v0.4` `type/infra` `spectralab`

**Описание.** Хранение `.csv`/`.mzML` в объектном хранилище вместо локальной папки.

**Инструкция.** Абстракция файлового слоя (локальный → S3).
**Триггер:** большие объёмы, несколько серверов.

**Definition of Done.** Файлы читаются/пишутся через S3; локальный режим остаётся для десктопа.

---

## SPECTRALAB-28 — Точечная миграция HTMX-компонентов на React/Vite

**Milestone:** `v0.4` · **Метки:** `spectralab/v0.4` `type/feature` `spectralab`

**Описание.** Только когда HTMX-интерфейс станет слишком сложным. Мигрировать **точечно**
(отдельные компоненты), не переписывая всё и не трогая API.

**Инструкция.** Внедрить Vite-сборку для конкретного сложного экрана (например,
интерактивный вьюер), сохранив остальное на HTMX.
**Триггер:** неудобство поддержки HTMX-вьюверов.

**Definition of Done.** Отдельный компонент на React работает рядом с HTMX-страницами;
API-контракт неизменен.

---

## SPECTRALAB-29 — Roadmap: рост системы (backlog-заметка)

**Milestone:** `v0.4` · **Метки:** `spectralab/v0.4` `type/docs` `spectralab`

**Описание.** Финальная заметка-бэклог с пунктами полного стека **без** отдельной
детальной инструкции, пока для них нет обоснованной необходимости.

**Инструкция.** Зафиксировать в одном месте как «не-сейчас»: Keycloak + RBAC, Kubernetes,
Nginx + TLS, Sentry, GitHub Actions CI/CD для веб-версии — каждый пункт с одной строкой
«когда понадобится».

**Определение риска (Plan B — Pyodide/WASM).** Отметить: запуск Python-ядра в браузере
через Pyodide/WASM **практически нереализуем** для этого проекта, поскольку ядро использует
RDKit (C++-биндинги, несовместимы с Pyodide). Не планировать до появления
Pyodide-совместимого RDKit.

**Definition of Done.** Бэклог зафиксирован; пункты не разворачиваются в задачи до
появления реальной потребности.

---

## Сводная таблица milestones

| Milestone | Срок | Issues | Ключевой результат |
|-----------|------|--------|--------------------|
| `v0.1` MVP-каркас | недели 1–3 (~2026-08-28) | 01–08 | FastAPI+Jinja2, лёгкий импорт core, upload+SQLite, healthz, README |
| `v0.2` Обработка и экспорт | недели 3–5 (~2026-09-11) | 09–16 | `POST /process`, вьюер uPlot, peaks, экспорт CSV, HTTP-тесты, регрессия set_01–05 |
| `v0.3` Удобства | недели 6+ (по необходимости) | 17–23 | mzML, Van Krevelen, сравнение, библиотека, пароль, Docker, гайд |
| `v0.4` Путь роста | без срока | 24–29 | Celery, OAuth2, PostgreSQL, S3, React, roadmap-бэклог |

## Итог

- **29 issues**, разбиты по 4 milestones, каждый с метками `release/*` + `type/*` + `spectralab`.
- Релизный трек (v0.1, v0.2) строится на упрощённом стеке; «путь роста» (v0.4) —
  опциональный, по реальной потребности.
- Веб-версия на любом этапе остаётся надстройкой, не заменой, до подтверждения
  эквивалентности на `set_01`–`set_05`.
