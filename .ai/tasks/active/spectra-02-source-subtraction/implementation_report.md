# Отчёт о реализации

Реализовано: `src/core/spectrum/_overlap.py`, опции `denoise_derivatives` /
`subtract_source` / `subtract_ppm` в `run_pipeline` и `_denoise_triple`,
счётчики `dmet_overlap_removed` / `dacet_overlap_removed` в `PipelineStats`,
ключи CLI (`--subtract-source`, `--subtract-ppm`) и чекбоксы GUI.

Тесты: `tests/unit/test_overlap.py` — 9 тестов, проходят.
Сквозная проверка на set_01: удалено 32/405 (7.9 %) из dmet и 32/481 (6.7 %) из
dacet; серии находятся (CD3 32, CD3CO 11), таблица 157 строк.
