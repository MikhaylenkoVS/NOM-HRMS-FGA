# DeepCode Audit Triage — результат проверки `AI_AUDIT_HANDOFF.md`

- **Дата триажа:** 2026-08-27
- **Источник:** `AI_AUDIT_HANDOFF.md` (LLM-аудит, 120 карточек модулей, 253 риска)
- **Область проверки:** все P0/P1-кандидаты (R1–R4, B1–B3). P2/P3-бэклог (B4–B256) в этой итерации **построчно не верифицировался** и остаётся неподтверждённым бэклогом.
- **Метод:** чтение актуального кода и метаданных, поиск по тестам, проверка открытых/закрытых GitHub Issues через `gh`.
- **Исходники не изменялись, коммиты не делались, Issues не создавались.**

---

## 1. Дедуплицированная очередь после проверки

| ID | Приоритет | Статус | Краткое название |
|----|-----------|--------|------------------|
| LIC-01 | **P2** | Подтверждена (human-verification) | Остаточные упоминания GPL-3.0 в README и pyproject после перехода на MPL-2.0 |
| LIC-02 | **P3** | Опционально (не обязательная) | SPDX-заголовки `# SPDX-License-Identifier: MPL-2.0` в ключевых `.py`-файлах |

- **P0:** подтверждённых нет.
- **P1:** подтверждённых нет. Все 7 P1-кандидатов аудита (R1–R4, B1–B3) отклонены или понижены (см. раздел 3).
- **P2:** 1 подтверждённая задача — LIC-01.
- **P3:** LIC-02 — опциональная; остальные P2/P3-кандидаты из handoff остаются неподтверждённым бэклогом.

---

## 2. Подтверждённые задачи

### LIC-01 — Остаточные упоминания GPL-3.0 после перелицензирования в MPL-2.0

- **GitHub Issue title (предлагаемый):**
  `docs: привести лицензионные метаданные к MPL-2.0 (README, pyproject classifier)`
- **Priority:** P2
- **Suggested labels:** `licensing`, `docs`
- **Problem:**
  Проект был перелицензирован GPL-3.0 → MPL-2.0 (закрытая задача #137), однако часть метаданных осталась в старом состоянии:
  - `README.md` в трёх местах всё ещё заявляет GPL-3.0 для основного кода;
  - `pyproject.toml` содержит ошибочный классификатор `License :: OSI Approved :: GPL-3.0 License` при `license = {text = "MPL-2.0"}`;
  - `README.md:239` ссылается на несуществующий файл `external/README.txt`.
- **Impact:**
  Читатели, журнал (ACS) и автоматические индексаторы видят противоречивую лицензионную информацию: `LICENSE` = MPL-2.0, а README/классификатор = GPL-3.0. Это искажает условия использования, создаёт юридическую неопределённость и снижает качество публикационного пакета (открытые задачи #11 PUB-03, #126 ACS-01).
  Замечание: это задача проверки метаданных человеком, а не юридический вывод. Фактический статус подтверждён только как «несоответствие текста».
- **Exact source evidence (файл и строки):**
  - `README.md:34` — «Приложение безопасно — исходный код открыт (GPL-3.0) и доступен в этом репозитории.»
  - `README.md:224` — «`external/               # Стороннее ПО (GPL-3.0)`» (в дереве структуры).
  - `README.md:239` — «Основной код — **GPL-3.0**. Сторонний код в `external/` — **GPL-3.0** (см. `external/README.txt`).»
  - `pyproject.toml:18` — `"License :: OSI Approved :: GPL-3.0 License",`
  - Эталон согласованности: `LICENSE:1` — Mozilla Public License Version 2.0; `pyproject.toml:10` — `license = {text = "MPL-2.0"}`; `CITATION.cff:22` — `license: "MPL-2.0"`; `.zenodo.json:11` — `"license": "MPL-2.0"`.
  - Несуществующая ссылка: `README.md:239` → `external/README.txt` (фактически: `external/README.md` и `external/README_LEGACY.md`).
- **Verification plan:**
  1. `grep -rn "GPL-3.0" README.md pyproject.toml docs/ src/` — зафиксировать все остаточные вхождения.
  2. Человек (автор) подтверждает корректную формулировку для основного кода (MPL-2.0) и для `external/` (legacy, GPL-3.0, вне сборки).
  3. После правок прогнать smoke: `pytest tests/ -q -m unit` (или `pytest tests/ -q`) и `python -m build` / `python -m src` для проверки, что метаданные не сломали сборку.
  4. Повторный `grep -rn "GPL-3.0" README.md pyproject.toml` — в README GPL-3.0 допустим только при корректном описании `external/` как legacy-кода с собственной лицензией.
- **Definition of Done:**
  - `README.md` во всех местах описания лицензии **основного** кода указывает MPL-2.0 (строки 34, 239).
  - Раздел про `external/` ссылается на актуальные файлы (`external/README.md` / `external/README_LEGACY.md`) и описывает его как legacy GPL-3.0, исключённый из сборки.
  - `pyproject.toml:18` заменён на классификатор MPL-2.0 (например, `License :: OSI Approved :: Mozilla Public License 2.0 (MPL-2.0)`).
  - `grep` не находит противоречивых упоминаний GPL-3.0 для основного кода.
  - Тесты и сборка проходят.
- **Dependency / blocking issue:**
  - Является follow-up закрытой #137 («chore: перелицензировать проект GPL-3.0 → MPL-2.0»), которая была закрыта с не полностью применёнными правками README/классификатора.
  - Связанные открытые: #11 (PUB-03, Data & Code Availability), #126 (ACS-01, пакет для подачи в журнал) — LIC-01 следует закрыть до/в рамках этих задач.
  - Блокирующих зависимостей нет.

### LIC-02 — SPDX-заголовки в ключевых `.py`-файлах (опционально)

- **GitHub Issue title (предлагаемый):**
  `chore: добавить SPDX-заголовки MPL-2.0 в ключевые .py-файлы (опционально)`
- **Priority:** P3
- **Suggested labels:** `licensing`, `chore`
- **Problem:** План закрытой #137 включал «Добавить SPDX-заголовки в ключевые `.py`-файлы», но `grep -rn "SPDX" src/` не находит ни одного заголовка; часть файлов содержит упоминание MPL-2.0 в docstring (`src/core/domain/spectrum.py:3`, `src/core/io/raw_bridge.py:1`, `src/core/io/raw_thermo_adapter.py:1`, `src/core/pipeline/_export.py:1`), остальные — нет.
- **Impact:** Низкий. MPL-2.0 **не требует** per-file заголовков; корневой `LICENSE` покрывает весь проект. Задача — только для единообразия и явной машиночитаемой маркировки.
- **Exact source evidence:** отсутствие `SPDX-License-Identifier` в `src/**`; план в закрытой #137.
- **Verification plan:** `grep -rn "SPDX-License-Identifier" src/` до/после; `pytest tests/ -q -m unit`.
- **Definition of Done:** ключевые модули (`src/core/**`, `src/structures/**`, `src/ui/**`, `src/configs/**`) содержат строку `# SPDX-License-Identifier: MPL-2.0`; тесты проходят.
- **Dependency / blocking issue:** follow-up закрытой #137; не блокирует ничего.

---

## 3. Rejected or insufficient evidence — отклонённые и пониженные находки

Все P1-кандидаты handoff — лицензионные. Проверка показала, что `LICENSE` в корне существует (MPL-2.0), поэтому исходные формулировки не подтверждаются.

| Находка | Файл | Решение | Причина отклонения/понижения |
|---------|------|---------|------------------------------|
| R1 [P1] «No license information» | `src/core/chemistry/__init__.py` | **Отклонена** | Файл содержит только docstring `"""src.core.chemistry package."""`; в корне есть `LICENSE` (MPL-2.0). MPL-2.0 не требует per-file заголовков. Отсутствие заголовка — не дефект. Частично поглощена LIC-01 (в части согласованности метаданных). |
| R2 [P1] «No license information» | `src/core/domain/__init__.py` | **Отклонена** | Аналогично R1: docstring + корневой `LICENSE` MPL-2.0. |
| R3 [P1] «No license information» | `src/core/io/__init__.py` | **Отклонена** | Аналогично R1: docstring + корневой `LICENSE` MPL-2.0. |
| R4 [P1] «File contains a license note, unclear if compliant» | `src/sim/__init__.py` | **Отклонена (ложное срабатывание)** | Утверждение аудита ложно: файл содержит только docstring `"""R&D utilities: ..."""`, никакой лицензионной заметки в нём нет. |
| B1 [P1] «Add LICENSE file» | `src/core/domain/__init__.py` | **Отклонена** | `LICENSE` уже добавлен и перелицензирован в MPL-2.0 (закрытые #10, #137). Дубль завершённой работы. |
| B2 [P1] «Add LICENSE file» | `src/core/chemistry/__init__.py` | **Отклонена** | То же. |
| B3 [P1] «Add license information to `src/core/io/__init__.py`» | `src/core/io/__init__.py` | **Отклонена** | Per-file лицензионная заметка не требуется; корневой `LICENSE` покрывает пакет. |
| B4 [P2] «Add LICENSE file» | `src/__init__.py` | **Отклонена** | `LICENSE` существует (MPL-2.0). |
| B31 [P2] «Document license requirements» | `src/sim/__init__.py` | **Поглощена LIC-01** | Реальная потребность — согласовать метаданные, а не «задокументировать требования» в этом файле. |
| B125 [P3] «Document RDKit usage and licensing» | `tests/unit/test_rdkit_bridge.py` | **Понижена / вне scope** | RDKit (BSD-3-Clause) уже отражён в `THIRD_PARTY_NOTICES.md:39`. Отдельная задача не требуется. |

Итог: **P1-очередь после триажа пуста**. Все исходные P1-кандидаты не подтвердились по актуальному коду; вместо них выделена одна подтверждённая P2-задача LIC-01 (несоответствие метаданных, оставшееся после закрытой #137).

---

## 4. Potential duplicates — проверка существующих GitHub Issues

Открытые Issues (28 шт., проверено через `gh issue list --state open`): **аналогов LIC-01 нет**. Связанные закрытые:

| Issue | Статус | Связь |
|-------|--------|-------|
| #10 «PUB-02: Добавить файл лицензии проекта (LICENSE)» | CLOSED | `LICENSE` добавлен; находки B1/B2/B4 — дубли этой завершённой работы. |
| #137 «chore: перелицензировать проект GPL-3.0 → MPL-2.0» | CLOSED | Первопричина LIC-01: правки README/классификатора были в плане, но применены не полностью. LIC-01 — follow-up. |
| #139 «docs: RawFileReader license compliance» | CLOSED | Не дубль; касается сторонних DLL (`THIRD_PARTY_NOTICES.md`). |
| #142 «cleanup: документировать external/ как legacy» | CLOSED | Связана: `external/README_LEGACY.md` создан, но README главного репозитория не обновлён (строка 239). |

Связанные открытые, но не дубли: #11 (PUB-03), #126 (ACS-01) — LIC-01 рекомендуется закрыть в их рамках.

---

## 5. Созданные GitHub Issues

> Статус: Issues созданы 2026-08-27 по явному подтверждению пользователя.

1. **LIC-01** — создан: [#172](https://github.com/MikhaylenkoVS/NOM-HRMS-FGA/issues/172)
   - Title: `docs: привести лицензионные метаданные к MPL-2.0 (README, pyproject classifier)`
   - Priority: **P2**; labels: `licensing`, `docs`, `priority-medium`
   - Полное описание, evidence, verification plan и DoD — в разделе 2.
   - Не дублируется открытыми Issues; является follow-up закрытой #137.

2. **LIC-02** (опционально) — создан: [#173](https://github.com/MikhaylenkoVS/NOM-HRMS-FGA/issues/173)
   - Title: `chore: добавить SPDX-заголовки MPL-2.0 в ключевые .py-файлы (опционально)`
   - Priority: **P3**; labels: `licensing`, `chore`, `optional`, `priority-low`
   - MPL-2.0 не требует per-file заголовков; задача для явной машиночитаемой маркировки файлов.

---

## 6. Примечания по процессу

- Рабочая ветка: `test_ai_orchestrator`. `AI_AUDIT_HANDOFF.md` и `.aiignore` — untracked.
- Изменения в исходники не вносились; `git commit` не выполнялся; файлы не удалялись.
- P2/P3-бэклог handoff (B5–B256, 249 кандидатов) в этой итерации не верифицировался построчно; при необходимости может быть разобран отдельной итерацией триажа.
- Найденные при проверке факты (существование `LICENSE` MPL-2.0, `THIRD_PARTY_NOTICES.md`, закрытые #10/#137/#139/#142) учтены выше.
