# Rollback Plan — GUI-02

## Когда откатывать

- GUI не запускается или вкладка «Спектры» перестала строить графики.
- RAW/mzML-запуск стал падать с ошибками, которых не было раньше.
- Тесты GUI (smoke/fallback) упали.

## Как откатить

```bash
git revert HEAD
# или
git checkout dev -- src/ui/_run.py src/ui/_plots.py src/ui/_log.py
```

Проверка:

```bash
python -c "from src.ui._run import RunMixin; from src.ui._plots import PlotsMixin; print('OK')"
pytest tests/unit/test_app_fallback.py -q
```

## Что не требуется

- Правка `src/core/` не выполнялась, откат научного кода не нужен.
