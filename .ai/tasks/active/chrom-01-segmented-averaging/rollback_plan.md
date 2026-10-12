# Rollback Plan — CHROM-01

## Когда откатывать

- Сегментный режим падает или даёт некорректные результаты.
- Обычный `run_pipeline` / GUI / CLI сломались.
- Референс-эквивалентность на CSV не выполняется.

## Как откатить

```bash
git revert HEAD
# или
git checkout dev -- src/core/io src/core/pipeline src/core/spectrum src/cli.py src/ui src/app.py tests
```

Проверка:

```bash
python -c "from src.core import run_pipeline; print('OK')"
pytest tests/unit/test_pipeline.py -q
```

## Что не требуется

- Правка конфигов не выполнялась.
