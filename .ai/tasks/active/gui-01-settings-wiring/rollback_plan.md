# Rollback Plan — GUI-01

## Когда откатывать

- Если md5 результата set_01 при дефолтных параметрах изменился.
- Если падение тестов указывает на изменение научного поведения в
  дефолтном режиме.
- Если GUI не запускается (ошибка импорта/атрибута после правок).

## Как откатить

1. Откат коммитов:

```bash
git checkout dev -- src/core/pipeline src/core/spectrum src/ui src/app.py tests
git checkout dev -- .ai/decisions .ai/tasks/active/gui-01-settings-wiring
```

2. Либо revert последнего коммита в ветке:

```bash
git revert HEAD
```

3. Проверить восстановление:

```bash
python -c "from src.core import run_pipeline; print('OK')"
pytest tests/unit/test_pipeline.py -q
```

## Ручные шаги (если откат кода выполнен, но артефакты остались)

- Удалить `.ai/tasks/active/gui-01-settings-wiring/` только после
  подтверждения человека.
- Убрать строку ADR-0002 из `.ai/decisions/index.md`.

## Что не требуется

- Восстановление ветки из удалённого репозитория: изменения локальны до PR.
- Правка конфигов: `src/configs/*.json` не затрагиваются.
