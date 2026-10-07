# Design — PACKAGE-05: единый источник конфигурации и контракт ошибок

## Контекст

Аудит `main` @ `30194d6` выявил две группы дефектов.

**1. Конфигурация (требование заказчика: «константы нигде не вписаны в код,
а загружаются только из единых конфигов»):**

| Файл | Состояние |
|---|---|
| `src/configs/constants/formula_search.json` | **не загружается вообще** (`loader._CONFIG_FILES` его не содержит); его блок `default` дублирует `pipeline.json → default_brutto_dict`, но с другими значениями (C[1,80] H[1,200] O[0,40] N[0,5] против C[0,50] H[0,100] O[0,25] N[0,10]) |
| `src/configs/constants/spectrum_load.json` | загружается в `SPECTRUM_LOAD_CFG`, но **не используется**: колонки маппит захардкоженный `CSV_COLUMN_MAPPER` (`_load.py:15–24`) |
| `pipeline.json → formula_search`, `→ default_brutto_dict` | второй (третий) источник тех же величин |

**2. Контракт ошибок и краевые случаи:** `run_pipeline(test_mode=True)` не читает
`PIPELINE.test_mode`; ошибки этапов глушатся и конвейер продолжается с
недостоверным результатом; CLI возвращает 1 при предупреждениях; пустой спектр
падает с `ValueError` (xfail в тестах).

## Решение

### 2.1. Единый источник конфигурации

**`constants/formula_search.json`** становится единственным источником
параметров генерации формул. В него переносятся ключи, ранее лежавшие в
`pipeline.json`, и добавляется `default_brutto_dict`:

```json
{
  "_description": "Formula generation defaults (single source of truth)",
  "elements": ["C", "H", "O", "N"],
  "ranges": {"C": [1, 50], "H": [4, 100], "O": [0, 20], "N": [0, 8]},
  "max_hc": 3.0, "max_oc": 1.2, "max_nc": 1.0, "max_dbe": 30.0, "min_c": 1,
  "default_brutto_dict": {"C": [0, 50], "H": [0, 100], "O": [0, 25], "N": [0, 10]}
}
```

Значения **синхронизированы с фактически действующими**: `ranges` берутся из
`pipeline.json → formula_search.ranges`, `default_brutto_dict` — из
`pipeline.json → default_brutto_dict`. Это осознанное решение: цель — убрать
дубликаты, а не изменить науку. Прежние значения мёртвого файла (C[1,80] и др.)
**отбрасываются** и фиксируются в отчёте как расхождение.

Из `pipeline.json` ключи `formula_search` и `default_brutto_dict` удаляются.

Загрузчик: в `_CONFIG_FILES` добавляется `"formula_search":
"constants/formula_search.json"`, экспортируется `FORMULA_SEARCH_CFG`.

Потребители переводятся на новый источник:

| Файл | Было | Стало |
|---|---|---|
| `src/core/spectrum/_constants.py:29` | `PIPELINE.formula_search` | `FORMULA_SEARCH_CFG` |
| `src/core/spectrum/_generate.py:14` | `PIPELINE.default_brutto_dict` | `FORMULA_SEARCH_CFG["default_brutto_dict"]` |
| `src/app.py:114`, `src/ui/_config.py:6` | `_PIPE_CFG.formula_search["ranges"]` | `FORMULA_SEARCH_CFG["ranges"]` |
| `tests/unit/test_assign_formulas.py:17` | `PIPELINE.default_brutto_dict` | `FORMULA_SEARCH_CFG["default_brutto_dict"]` |

**`constants/spectrum_load.json`** становится источником маппинга колонок.
Чтобы не потерять синонимы (`m/z`, `M/Z`, `mz`, `I`, `int`, `Int`), они
переносятся в тот же JSON отдельным блоком `synonyms`; `_load.py` собирает
итоговый словарь как `{**default, **synonyms}`. Результирующий маппинг
побитово совпадает с прежним `CSV_COLUMN_MAPPER`.

### 2.2. `run_pipeline(test_mode=True)` читает `PIPELINE.test_mode`

Область применения — только ветка `test_mode`. Значения берутся из
`PIPELINE.test_mode` (`load`, `denoise`, `assign`, `series`, `match_ppm`).
Production-ветка (`test_mode=False`) не затрагивается.

Практический эффект: эталонный прогон (`force=2.0, intensity=None,
rel_error_ppm=0.5, ppm_tol=0.5`) становится воспроизводимым штатной точкой
входа `python -m src.core.pipeline._test --test`; ранее она подставляла
`rel_error=1.0`, `ppm_tol=5.0`, окно 0/1000.

### 2.3. Параметры GMM из `constants/noise.json`

`Spectrum.noise_filter`, `compute_noise_threshold` и `fit_gmm_1d` перестают
использовать литералы `max_components=15`, `max_iter=200`, `tol=1e-4` как
значения по умолчанию. Берутся `NOISE_CFG.max_components`, `NOISE_CFG.max_iter`,
`NOISE_CFG.tol`; `NOISE_CFG.subsample_max_points` уже используется.

Внимание: `max_components` в конфиге равно 5 (в коде было 15). Это меняет
число компонент GMM, а значит — порог шумоподавления. Влияние измеряется и
фиксируется в `reference_validation.md`.

### 2.4. Контракт ошибок

`PipelineRunResult` получает раздельные поля: `messages` (предупреждения) и
`errors` (ошибки). Правила:

* ошибка загрузки/назначения/серий → запись в `errors`, признак
  `result.ok = False`;
* ошибка визуализации → запись в `messages`, `ok` не меняется;
* CLI возвращает код 1 только при `not res.ok` (или исключении), а не при
  любом непустом `messages`.

Сохранение совместимости: свойство `messages` остаётся и содержит объединение
ошибок и предупреждений (чтобы существующие вызовы не сломались), но код
возврата опирается на `ok`.

### 2.5. Краевые случаи (по списку аудита)

| ID | Правка |
|---|---|
| S-06 | `assign_formulas`: отбрасывать пики с `NaN`/неположительной массой; при пустом спектре возвращать пустой результат без исключения; снять `xfail` |
| S-09 | `Spectrum._df_to_peaks`: `NaN` в необязательных колонках → `None`, а не исключение |
| S-10 | `load_spectrum`: проверка дубликатов колонок после `rename` |
| S-11 | `noise_filter`: валидация `quantile ∈ [0, 1]` |
| K-11 | `build_result_table`: предупреждение при коллизии округлённых масс |
| K-22 | `statistics.dbe`: клампинг `max(0, ...)` для согласованности с `_chem.dbe_from_counts` |
| K-23 | `van_krevelen`: понятная ошибка вместо `KeyError` при отсутствии колонок |
| K-24 | `van_krevelen`: `N_COOH` требуется только при `color_by="N_COOH"` |

## Границы задачи

* **Не меняются** научные константы (`chemistry.json` целиком запрещён к правке).
* **Не меняется** поведение скоринга: пороги 20 / 0.3 / N>3 и веса 0.5 / 2.0 —
  это K-04, задача пакета 6 (требует ADR, так как затрагивает отбор кандидатов).
* Формат выходной таблицы не меняется.
* `--cov-fail-under` включается в CI.

## Риски

| Риск | Оценка | Митигация |
|---|---|---|
| Перенос ключей в JSON ломает потребителя, которого не нашли | средний | grep по всем потребителям; проверка `python -c "import src.configs"`; полный прогон тестов |
| Смена `max_components` 15 → 5 меняет порог GMM | средний | измерить влияние на set_01…05, зафиксировать в `reference_validation.md` |
| Введение `errors` меняет контракт `run_pipeline` | средний | `messages` сохранено; `ok` добавлено аддитивно |
| Ошибка в guard'ах ломает разбор реальных данных | низкий | краевые случаи покрываются тестами |

## Критерий «поведение не изменилось»

Раздел 2.1–2.2 не должны менять ни одну строку результата: A10 (md5 таблицы на
set_01 = `33cde0049db29f91dfeab2c71d13b77e`) и A11 (сводка тест-режима).
Раздел 2.3 (GMM) изменение допускает — оно измеряется отдельно, и в этом
случае требуется явное подтверждение владельца.
