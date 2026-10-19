# Отчёт о реализации

Изменено: `src/core/spectrum/_series.py` (`max_gaps`, обрыв по бюджету,
`allow_gaps` как синоним), `src/core/pipeline/_stages.py`, `_cache.py`, `_run.py`
(параметр, ключ кэша, test-mode, метаданные), `src/configs/pipeline.json`
(`max_gaps: 1` в трёх блоках), GUI (`max_gaps_var`, поле «Пропусков в серии»),
`src/cli.py` (`--max-gaps`, `--no-allow-gaps`).

Тесты: `tests/unit/test_find_series.py::TestMaxGaps` (8 тестов) — проходят.
