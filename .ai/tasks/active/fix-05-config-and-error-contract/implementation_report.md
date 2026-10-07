# Implementation Report — PACKAGE-05

**Задача:** `fix-05-config-and-error-contract`
**Ветка:** `dev` (база — `origin/main` = `30194d66eb259902bab3a36860068223dabace4c`)
**Статус:** реализовано, проверено, ожидает ревью человеком
**Дата:** 2026-10-07

## Что сделано (по коммитам)

| Коммит | Содержание | Пункты аудита |
|---|---|---|
| `81ef71b` | Единый источник конфигурации: подключены мёртвые `constants/formula_search.json` и `constants/spectrum_load.json`, из `pipeline.json` удалены дублирующие `formula_search` и `default_brutto_dict` | K-18, K-19, K-21 |
| `3abd2fe` | `run_pipeline(test_mode=True)` читает `PIPELINE.test_mode`; параметры GMM читаются из `constants/noise.json` | K-10, K-20 |
| `881bbf7` | Разделены ошибки и предупреждения, код возврата CLI определяется ошибками; включён `--cov-fail-under=25` | S-03, S-04, S-05, S-08, T-05 |
| `1c53a0e` | Guard'ы краевых случаев: пустой/NaN спектр, NaN в необязательных колонках, дубликаты колонок, диапазон quantile, согласованность DBE | S-06, S-09, S-10, S-11, K-22 |

## Изменённые файлы

```
src/configs/constants/formula_search.json   (подключён, стал единым источником)
src/configs/constants/spectrum_load.json    (добавлен блок synonyms)
src/configs/pipeline.json                   (удалены дубли formula_search/default_brutto_dict)
src/configs/loader.py                       (formula_search в _CONFIG_FILES, FORMULA_SEARCH_CFG)
src/configs/__init__.py                     (экспорт всех синглтонов)
src/configs/README.md                       (документация состава конфигов)
src/core/spectrum/_constants.py             (диапазоны из FORMULA_SEARCH_CFG)
src/core/spectrum/_generate.py              (DEFAULT_BRUTTO_DICT из FORMULA_SEARCH_CFG)
src/core/spectrum/_load.py                  (CSV_COLUMN_MAPPER из конфига; guard дубликатов)
src/core/spectrum/_denoise.py               (GMM-параметры из NOISE_CFG)
src/core/spectrum/_assign.py                (guard пустого/NaN спектра)
src/core/domain/spectrum.py                 (max_components из NOISE_CFG; NaN→None; проверка quantile)
src/core/statistics.py                      (dbe клампится к нулю)
src/core/pipeline/_test.py                  (эталонные дефолты из PIPELINE.test_mode)
src/core/pipeline/_run.py                   (test_mode из конфига; errors/ok)
src/core/pipeline/_stats.py                 (PipelineRunResult.errors, .ok)
src/cli.py                                  (код возврата по ошибкам)
src/ui/_config.py, src/app.py               (диапазоны из FORMULA_SEARCH_CFG)
tests/unit/test_cli.py                      (+3 теста контракта)
tests/unit/test_edge_guards.py              (новый файл, 12 тестов)
tests/unit/test_spectrum_ops.py             (снят xfail)
tests/unit/test_assign_formulas.py          (источник default_brutto_dict)
.github/workflows/ci.yml                    (--cov-fail-under=25)
```

## Отклонения от проектных допущений

1. **Значения мёртвого `formula_search.json` отброшены.** В файле лежали
   `C[1,80] H[1,200] O[0,40] N[0,5]`, в действующей конфигурации —
   `C[1,50] H[4,100] O[0,20] N[0,8]`. Задача — устранить дублирование, а не
   менять науку, поэтому в новый единый источник перенесены **действующие**
   значения. Прежние значения файла зафиксированы как расхождение и требуют
   решения владельца: они никогда не применялись.
2. **Параметры GMM изменены конфигом** (`max_components` 15 → 5,
   `max_iter` 200 → 100). Значения взяты из `constants/noise.json`; измеренное
   влияние — см. `reference_validation.md` (порог совпадает на 4 наборах из 5,
   на set_02 отличие 3.42/3.36). Если владелец предпочтёт прежнее поведение,
   правка делается в JSON (`max_components: 15`), код при этом остаётся
   конфиг-управляемым.
3. **`messages` сохранён как объединённый журнал** (ошибки + предупреждения),
   чтобы не ломать существующих потребителей, включая
   `tests/unit/test_pipeline.py`. Новое поле `errors` и свойство `ok` добавлены
   аддитивно.
4. **Правило приоритета в тест-режиме.** Значение, переданное вызывающим и
   отличающееся от production-дефолта, переопределяет эталонное; иначе
   побеждает `test_mode`. Правило задокументировано в docstring `run_pipeline`.
5. **`--cov-fail-under=25`** выбран с запасом относительно измеренных 32 %
   (CI-эквивалент). Значение легко поднять по мере роста покрытия.
6. **Не сделано (вне объёма, зафиксировано):** K-11 (предупреждение о коллизии
   округлённых масс в `build_result_table`), K-24 (`N_COOH` требуется
   безусловно в `compute_van_krevelen_data`). K-23 оказался уже закрыт —
   функция поднимает `ValueError` с перечнем обязательных колонок.

## Проверка (фактические прогоны)

| Проверка | Команда | Результат |
|---|---|---|
| Валидация packet | `python tools/ai_workflow.py validate-task fix-05-config-and-error-contract` | см. ниже |
| Тесты | `pytest tests/ -q` | **457 passed, 1 skipped, 0 xfailed** |
| Линтер | `flake8 src/ tests/ tools/` | 0 ошибок |
| Формат | `black --check src/ tests/ tools/` | 128 файлов без изменений |
| Импорт конфигов | `python -c "from src.configs import FORMULA_SEARCH_CFG"` | OK, значения совпадают с действовавшими |
| A10 (production) | CLI на set_01, md5 | `33cde0049db29f91dfeab2c71d13b77e` — не изменился |
| A11 (test-mode) | `python -m src.core.pipeline._test --test` | изменился только за счёт K-10 (assign recall 96.8 → 100 %) |
| Порог покрытия | CI-эквивалент `tests/unit/` минус 3 файла | 32 % ≥ 25 % |
| Согласованность репо | `python tools/ai_workflow.py check-repo` | REPO CHECK PASSED |

## Соответствие AGENTS.md

| Правило | Статус |
|---|---|
| 1. Read before write | выполнено: прочитаны конфиги, потребители, тесты до правок |
| 2. Task packet | выполнен: `.ai/tasks/active/fix-05-config-and-error-contract/` |
| 3. Не трогать несвязанное | выполнено: изменения только в `scope.allowed_paths` |
| 4. Не пушить в main | выполнено: работа в `dev`, push не выполнялся |
| 5. Безопасные git-операции | выполнено: только `add`/`commit`, force/reset не применялись |
| 6. Без секретов | выполнено: в изменениях нет путей, ключей и персональных данных |
| 7. Обоснование зависимостей | новых зависимостей нет (pytest-cov добавлен в пакете 4) |
| 8. Научные инварианты | не тронуты: `chemistry.json` не изменялся, значения перенесены «как есть»; поведение скоринга не менялось |
| 9. Тесты перед завершением | выполнено: 457 passed |
| 10. Implementation report | этот файл |
| 11. Benchmark для performance | не применимо (не performance-задача) |
| 12. Reference equivalence | выполнен: `reference_validation.md` |
| 13. Документировать неоднозначности | выполнено: пп. 1–2 «Отклонений» |
| 14. Без merge/release без человека | выполнено: merge, PR, push, release не выполнялись |

## Что требуется от владельца

1. Подтвердить отказ от значений мёртвого `formula_search.json`
   (`C[1,80] H[1,200] O[0,40] N[0,5]`) — они никогда не применялись.
2. Подтвердить перевод GMM на `constants/noise.json`
   (`max_components=5`, `max_iter=100`) либо вернуть 15/200 в JSON.
3. Согласовать порог покрытия `--cov-fail-under=25` (измерено 32 %).
4. Подтвердить, что дефект OH-серий (`dacet_wrong` 51.6–71.0 %) передаётся в
   пакет 6 как научная правка с ADR.
