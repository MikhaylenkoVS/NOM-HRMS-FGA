# Rollback Plan — PACKAGE-05

## Характер изменения

Задача средней рискованности: перекладывание конфигурации (без изменения
значений), исправление контракта ошибок и краевых случаев. Научные константы
`chemistry.json` не затрагиваются.

## Точка возврата

База — `origin/main` = `30194d66eb259902bab3a36860068223dabace4c`. Работа
ведётся в `dev`; перед задачей `dev` уже содержал коммиты пакетов 1–4
(PACKAGING-01, encoding/CLI, cleanup, tests/markers). Точка возврата
непосредственно перед пакетом 5 — вершина `dev` на момент старта задачи.

## Полный откат

```bash
git checkout dev
git reset --hard PACKAGE05_BASE_SHA   # только по явной команде владельца
```

> `git reset --hard` на общей ветке запрещён без письменного согласования
> (`AGENTS.md`, правило 5; `code-change-protocol`, раздел 4).

## Точечный откат

Работа разбита на логические коммиты; откат — обратными коммитами:

```bash
git revert SHA    # для каждого коммита пакета, в обратном порядке
```

## Откат по подзадачам

| Подзадача | Что вернуть |
|---|---|
| Единый конфиг | `git checkout PACKAGE05_BASE_SHA -- src/configs/ src/core/spectrum/_constants.py src/core/spectrum/_generate.py src/ui/_config.py src/app.py tests/unit/test_assign_formulas.py` |
| `test_mode` из `PIPELINE.test_mode` | `git checkout PACKAGE05_BASE_SHA -- src/core/pipeline/_run.py` |
| Параметры GMM | `git checkout PACKAGE05_BASE_SHA -- src/core/spectrum/_denoise.py src/core/domain/spectrum.py` |
| Контракт ошибок | `git checkout PACKAGE05_BASE_SHA -- src/core/pipeline/_run.py src/core/pipeline/_stages.py src/core/pipeline/_stats.py src/cli.py` |
| Краевые случаи | `git checkout PACKAGE05_BASE_SHA -- src/core/spectrum/_assign.py src/core/spectrum/_load.py src/core/domain/spectrum.py src/core/statistics.py tests/unit/test_edge_guards.py tests/unit/test_spectrum_ops.py` |
| `--cov-fail-under` | `git checkout PACKAGE05_BASE_SHA -- .github/workflows/ci.yml` |

## Быстрый частичный откат только порога GMM

Если изменение порога шумоподавления окажется нежелательным, обратимая правка —
вернуть значение в конфиге (код при этом остаётся конфиг-управляемым):

```json
// src/configs/constants/noise.json
"max_components": 15
```

## Условия, при которых откат обязателен

1. Изменился md5 результата на `set_01` для подзадач 1–2 (не должны влиять).
2. Упал хотя бы один тест из `pytest tests/ -q`.
3. `python -c "import src.configs"` завершается ошибкой.
4. Пропал публичный атрибут `PipelineRunResult.messages`.

## Остаточные риски

Нет: откат возвращает систему в состояние, соответствующее базовому SHA
(или, для точечного отката, — к состоянию до конкретной подзадачи).
