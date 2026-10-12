# Design — GUI-02: асинхронные RAW/mzML и подготовка спектров

## Проблема

Аудит по коммитам показал, что запуск анализа и batch уже вынесены в
фоновые потоки, но два места всё ещё блокируют главный поток (и,
следовательно, `mainloop`):

1. `RunMixin._run` вызывает `_resolve_path()` в главном потоке. Для
   `.raw`/`.mzML` внутри выполняется тяжёлое усреднение/конвертация
   (`average_raw_to_json`, `mzml_to_json`) — GUI подвисает до её
   завершения.
2. `PlotsMixin._plot_spectra` читает три CSV и строит график в главном
   потоке — на больших файлах окно «замерзает».

## Решение

Общий принцип: **тяжёлая работа — в фоне, tkinter — только из главного
потока через `queue.Queue` + `_poll_log_queue`.**

### 1. RAW/mzML в фоне

- `_run()` в главном потоке только читает значения `StringVar` (быстро),
  проверяет незаполненные поля и запускает воркер с **сырыми** путями.
- `_resolve_path()` переписывается в потокобезопасный вариант:
  - `self._log` → `self._log_queue.put(("log", ...))`;
  - `self._set_status` / `self.progress` → `("progress", (stage, pct))`;
  - `self.update_idletasks()` удаляется (в фоне не нужен);
  - `spec_var.set(path)` убирается из воркера.
- Воркер разрешает пути, затем сразу запускает `run_pipeline` в том же
  потоке (как и раньше).
- После успешного разрешения воркер кладёт в очередь `("paths_resolved",
  (src, dmet, dacet))`; обработчик в главном потоке обновляет
  `src_var`/`dmet_var`/`dacet_var`.
- Ошибки разрешения/конвертации попадают в `("error", {"traceback": tb})`
  и показываются существующим `_on_run_error_data`.

### 2. Подготовка спектров в фоне

- `_plot_spectra()` в главном потоке читает пути и `sep`, проверяет
  существование файлов, очищает canvas и запускает
  `_plot_spectra_worker(paths, sep)`.
- Воркер читает CSV, переименовывает колонки через `CSV_COLUMN_MAPPER`,
  валидирует `mass`/`intensity` и кладёт в очередь
  `("spectra_data", {"dfs": {...}})`.
- Обработчик в главном потоке строит matplotlib-фигуру из готовых
  DataFrame и вызывает `embed_figure` (создание Tk-canvas — только в
  главном потоке).
- Ошибки чтения → `("spectra_error", {"message": ...})` → лог +
  `messagebox.showerror`.

### 3. Обработчики в `_poll_log_queue`

Добавляются ветки `paths_resolved`, `spectra_data`, `spectra_error`.
Существующие `log`/`success`/`error`/`progress`/`batch_done` не меняются.

## Карта изменений

| Файл | Изменение |
|------|-----------|
| `src/ui/_run.py` | `_run` читает входы и стартует воркер; `_resolve_path` потокобезопасен; `_run_worker` принимает сырые входы |
| `src/ui/_plots.py` | `_plot_spectra` запускает воркер; добавлен `_plot_spectra_worker` и построение графика по данным |
| `src/ui/_log.py` | `_poll_log_queue` обрабатывает `paths_resolved`, `spectra_data`, `spectra_error` |
| `src/ui/_config.py` | без изменений |

## Не меняется

- `src/core/` и научная логика не затрагиваются.
- Сигнатуры `run_pipeline`, `load_spectrum`, `average_raw_to_json`,
  `mzml_to_json` не меняются.
- Сообщения об ошибках и статусы сохраняются по смыслу.
