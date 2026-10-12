# Acceptance — GUI-02

## Критерии приёмки

| # | Критерий | Метод проверки | Ожидаемый результат |
|---|---|---|---|
| A1 | RAW/mzML-конвертация не в главном потоке | чтение кода: `average_raw_to_json` / `_mzml_to_json` вызываются только внутри `_run_worker` | подтверждено |
| A2 | Чтение CSV спектров не в главном потоке | чтение кода: `pd.read_csv` в `_plot_spectra_worker` | подтверждено |
| A3 | Нет вызовов tkinter из воркеров | grep `self._log\|self.progress\|self._set_status\|_clear_frame` в `_*worker` | отсутствуют (только queue) |
| A4 | Очередь обрабатывает новые события | `_poll_log_queue` содержит `paths_resolved`, `spectra_data`, `spectra_error` | подтверждено |
| A5 | Ошибки RAW/CSV показываются пользователю | код: `("error", ...)` / `("spectra_error", ...)` → messagebox | подтверждено |
| A6 | Прогресс-бар работает для RAW | `("progress", ...)` из воркера | подтверждено |
| A7 | Импорты GUI валидны | `python -c "from src.ui._run import RunMixin; from src.ui._plots import PlotsMixin"` | OK |
| A8 | Тесты | `pytest tests/ -q` | 0 новых падений (допустимы pre-existing `test_report.py` без reportlab) |
| A9 | Task packet валиден | `python tools/ai_workflow.py validate-task gui-02-async-raw-plots` | 0 errors |

## Стоп-факторы

- Изменение `src/core/` или `src/configs/`.
- Изменение сигнатур `run_pipeline`, `load_spectrum`, мостов RAW/mzML.
- Потеря существующих сообщений об ошибках/статусов.

## Definition of Done

1. A1–A9 выполнены.
2. Коммит в ветке `fix/gui-02-async-raw-plots`.
3. PR/merge — только по явной команде человека.
