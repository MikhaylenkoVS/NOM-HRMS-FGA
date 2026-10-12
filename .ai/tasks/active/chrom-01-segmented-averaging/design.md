# Design — CHROM-01: сегментное усреднение хроматограмм

## Проблема

Сейчас усреднение RAW/mzML даёт один спектр на весь RT-диапазон, RT
теряется, а поиск серий исходный↔дериватизованный идёт только по m/z.
Пользователь хочет:

1. разбить RT-диапазон на настраиваемые отрезки (по умолчанию 2 мин);
2. усреднять **только внутри отрезка**;
3. шумоподавление применять **внутри отрезка**;
4. для исходного спектра сохранять RT отрезка у каждого пика;
5. дериватизованные спектры усреднять по тем же отрезкам, но при поиске
   серий использовать **все** отрезки (RT производных не сохранять и не
   сопоставлять — производное не обязано иметь то же время удерживания);
6. CSV/JSON/XLSX без RT — обрабатывать как один сегмент.

## Решение

### 1. Core: сегменты и усреднение (`src/core/io/segmented.py`)

- `build_rt_segments(rt_min, rt_max, segment_width)` → список
  `(start, end)` от `rt_min` до `rt_max` с шагом `segment_width`.
- `aggregate_scan_lists(mz_list, int_list, rt_list, segments)` — чистая
  функция: раскладывает сканы по сегментам, внутри сегмента группирует
  m/z с округлением до 5 знаков и суммирует интенсивности. Тестируется
  без pymzml/pythonnet.
- `average_segments(path, segments, sep=",", progress_callback=None)` →
  `list[DataFrame]` (колонки `mass`, `intensity`):
  - `.raw` → `raw_thermo_adapter.average_raw_segments()` (одно открытие
    файла, `AverageScansInScanRange` по каждому сегменту);
  - `.mzml` → однопроходное чтение mzML и `aggregate_scan_lists()`;
  - CSV/JSON/XLSX → один сегмент `[df]` (RT не сохраняется).

### 2. Core: сегментный пайплайн (`src/core/pipeline/_segments.py`)

`run_pipeline_segmented(src_path, dmet_path, dacet_path, *,
segment_width=2.0, rt_min=0.0, rt_max=999.0, ...обычные параметры)`:

1. `segments = build_rt_segments(rt_min, rt_max, segment_width)`.
2. Для каждого файла `average_segments()` → сегментные DataFrame.
3. Для каждого сегмента k:
   - `src_k`: фильтр `load_mass_min/max` → `Spectrum` → `denoise` →
     `assign_formulas` → в таблицу добавляются `rt_start`, `rt_end`.
   - `dmet_k`, `dacet_k`: фильтр → `Spectrum` → `denoise` (только внутри
     сегмента).
4. Все `dmet_k` объединяются в один `Spectrum` (суммирование интенсивностей
   по совпадающим m/z); аналогично `dacet`.
5. Для каждого исходного сегмента k:
   - `find_series(src_k, dmet_all, DELTA_CD3, ...)` и
     `find_series(src_k, dacet_all, DELTA_CD3CO, ...)`;
   - `build_result_table(src_k, ...)` (внутри сегмента массы уникальны);
   - в результат добавляются `rt_start`/`rt_end` сегмента.
6. Конкатенация таблиц сегментов → итоговая таблица:
   `mass, rt_start, rt_end, intensity, brutto, all_candidates, N_COOH,
   N_OH, missing_dmet, missing_dacet`.
7. Возвращается `PipelineRunResult` (table = итоговая таблица,
   stats = агрегированные счётчики, errors/messages).

### 3. CLI (`src/cli.py`)

Новые флаги:

- `--segment-width FLOAT` — включает сегментный режим (ширина отрезка, мин);
- `--rt-min FLOAT`, `--rt-max FLOAT` — RT-диапазон (по умолчанию 0.0, 999.0).

При `--segment-width` вызывается `run_pipeline_segmented`; CSV-файлы
обрабатываются как один сегмент. Вывод — та же таблица CSV.

### 4. GUI (`src/ui/_params.py`, `_run.py`, `app.py`)

- На подвкладке «📏 Обработка»: галочка «Сегментный анализ по RT» и поле
  «Ширина отрезка, мин» (по умолчанию `2.0`).
- RT-диапазон берётся из существующих полей исходного файла
  (`src_rt_min`/`src_rt_max`), как в batch.
- `_run_worker` при включённом режиме вызывает `run_pipeline_segmented`
  с `segment_width`, `rt_min`, `rt_max`.

## Карта изменений

| Файл | Изменение |
|------|-----------|
| `src/core/io/segmented.py` | новый модуль: `build_rt_segments`, `aggregate_scan_lists`, `average_segments` |
| `src/core/io/raw_thermo_adapter.py` | `average_raw_segments()` |
| `src/core/io/mzml_bridge.py` | однопроходная сегментация (или вызов из segmented.py) |
| `src/core/pipeline/_segments.py` | `run_pipeline_segmented()` |
| `src/core/pipeline/__init__.py` | экспорт `run_pipeline_segmented` |
| `src/core/__init__.py` | экспорт `run_pipeline_segmented` |
| `src/cli.py` | флаги `--segment-width`, `--rt-min`, `--rt-max` |
| `src/ui/_params.py` | виджеты сегментного режима |
| `src/ui/_run.py` | ветка сегментного запуска в воркере |
| `src/app.py` | новые `StringVar`/`BooleanVar` |
| `src/ui/_deps.py` | импорт `run_pipeline_segmented` |
| `tests/` | юниты сегментов + референс-эквивалентность |

## Не меняется

- `src/configs/chemistry.json` и научные константы.
- Обычный `run_pipeline` и его выходной формат.
- Скоринг NOM, пороги, веса.
