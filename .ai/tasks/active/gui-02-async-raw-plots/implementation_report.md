# Implementation Report — GUI-02

## Изменённые файлы

| Файл | Суть изменения |
|------|----------------|
| `src/ui/_run.py` | `_run` больше не конвертирует RAW/mzML в главном потоке; `_resolve_path` переписан в потокобезопасный вариант (лог/прогресс через `_log_queue`); `_run_worker` принимает сырые пути, разрешает их в фоне и запускает пайплайн; добавлены `_on_paths_resolved` и `_on_run_error_message` |
| `src/ui/_plots.py` | `_plot_spectra` запускает фоновый `_plot_spectra_worker` для чтения CSV; добавлены `_on_spectra_data` (построение графика в главном потоке) и `_on_spectra_error` |
| `src/ui/_log.py` | `_poll_log_queue` обрабатывает новые события: `run_error`, `paths_resolved`, `spectra_data`, `spectra_error` |

## Результаты проверок

| Проверка | Результат |
|----------|-----------|
| `python -c "from src.ui._run import RunMixin; from src.ui._plots import PlotsMixin"` | OK |
| `pytest tests/unit/test_app_fallback.py tests/integration/test_app_smoke.py -q` | 4 passed |
| `pytest tests/ -q` (полный) | 455 passed, 1 skipped; 2 pre-existing failures `test_report.py` (отсутствует `reportlab`) |
| `validate-task gui-02-async-raw-plots` | VALIDATION PASSED |

## Отклонения от design

- Для ошибок подготовки входных файлов добавлено отдельное событие
  `run_error` с понятным сообщением (без длинного traceback) — сохраняет
  прежний UX `messagebox.showerror("Ошибка", ...)`.
