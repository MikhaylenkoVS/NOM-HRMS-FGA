---
name: deepcode-github-mcp-pr
description: >
  Оформление Pull Request и Issue на GitHub через GitHub MCP с учётом
  контекста проекта: ветвление (feat/fix/docs/refactor/chore/cleanup),
  code-change-protocol, защита main/stable, шаблоны PR и связь с TODO-листом
  проекта. Активировать когда пользователь говорит «PR», «pull request»,
  «issue», «GitHub», «MCP», «открыть PR», «создать issue», «задача»,
  «тикет», «оформить», «шаблон», «workflow», «CI»; либо после завершения
  feature-ветки по code-change-protocol.
---

# DeepCode GitHub MCP PR — интеграция с GitHub

Скилл для взаимодействия с GitHub через MCP (Model Context Protocol):
оформление PR, создание Issue, проверка CI, работа с релизами. Все операции
выполняются с учётом code-change-protocol и защиты веток main/stable.

## Правила ветвления (code-change-protocol, раздел 7)

| Префикс | Назначение | Пример |
|---------|-----------|--------|
| `feat/` | Новая функциональность | `feat/raw-import` |
| `fix/` | Исправление багов | `fix/encoding-cp1252` |
| `docs/` | Документация | `docs/architecture-update` |
| `refactor/` | Переработка без изменения поведения | `refactor/denoise-params` |
| `chore/` | Инфраструктура, CI, зависимости | `chore/update-pytest` |
| `cleanup/` | Удаление мёртвого кода | `cleanup/root-files` |

**Защита веток:**
- `main`: ❌ нельзя трогать без явного согласования.
- `stable`: 🚫 абсолютный запрет — только вручную пользователем.
- Все изменения — в feature-ветках от `main` или `dev`.

## Шаблон PR

При создании PR использовать следующий шаблон:

```markdown
## Описание
Краткое описание changeset'а (1–2 предложения).

## Связанные issues
Closes #N, Related #M

## Тип изменений
- [ ] feat: новая функциональность
- [ ] fix: исправление бага
- [ ] docs: документация
- [ ] refactor: переработка кода
- [ ] chore: инфраструктура
- [ ] cleanup: удаление мёртвого кода

## Затронутые модули
- `src/core/...` — что изменено
- `src/configs/...` — что изменено
- `tests/...` — какие тесты

## Проверка
- [ ] `pytest tests/ -q` — все тесты зелёные
- [ ] `pytest tests/integration/ -q` — интеграционные тесты зелёные
- [ ] `flake8 src/` — без новых ошибок
- [ ] Изменения в `chemistry.json` проверены на точность
- [ ] Для новых фич — добавлены тесты
- [ ] `python -m src` — GUI запускается без ошибок

## Метрики (если применимо)
- denoise_recall: X.XX (было X.XX)
- assign_recall: X.XX (было X.XX)
- wrong_ratio: X.XX (было X.XX)

## Скриншоты (для GUI-изменений)
<!-- Приложить скриншоты до/после -->
```

## Шаблон Issue

```markdown
## Описание проблемы
Чёткое описание бага или запроса.

## Ожидаемое поведение
Что должно происходить.

## Фактическое поведение
Что происходит сейчас.

## Как воспроизвести
1. Запустить `python -m src.core.pipeline --test`
2. ...
3. Ошибка: ...

## Окружение
- ОС: Windows 10 / macOS 14 / Ubuntu 24.04
- Python: 3.12
- Версия: v0.4.2
- Зависимости: `pip list`

## Логи / трейсбек
```
(вставить stack trace)
```

## Метки (labels)
- `bug` / `enhancement` / `documentation`
- Приоритет: `critical` / `high` / `medium` / `low`
```

## Алгоритм создания PR

### 1. Проверить состояние

```bash
git branch --show-current      # не main/stable!
git status                     # нет незакоммиченных изменений
git fetch --all --prune        # актуальный remote
git log origin/main..HEAD      # что пойдёт в PR
```

### 2. Создать PR через MCP

- Заголовок: `<префикс>: краткое описание` (например, `fix: encoding cp1252 in raw_bridge`).
- Тело: по шаблону выше.
- Base: `main` или `dev` (уточнить у пользователя).
- Labels: по типу изменений.

### 3. Связать с Issues

Если PR закрывает issue — добавить `Closes #N` в описание.

### 4. Запросить review

- Назначить reviewer'а (если настроен CODEOWNERS).
- Связать с milestone (если есть).

## Проверка CI

После создания PR — дождаться завершения GitHub Actions:

```bash
# Проверить статус последнего run'а
gh run list --limit 1
```

### Workflows проекта:

| Workflow | Файл | Когда запускается |
|----------|------|-------------------|
| Автосборка .exe | `.github/workflows/release_exe.yml` | При создании релиза |

**Если CI красный:**
1. Прочитать лог ошибки.
2. Локально воспроизвести: `pytest tests/ -q`.
3. Исправить.
4. `git push` — CI перезапустится.

## Подготовка релиза

При готовности к релизу:

1. Обновить версию в `pyproject.toml` (`version = "x.y.z"`).
2. Обновить `CODE_AVAILABILITY.md` (актуальная версия, дата).
3. Обновить `CITATION.cff` (версия, дата).
4. Создать PR с меткой `release`.
5. После мёрджа — создать Release на GitHub:
   - Tag: `vX.Y.Z`.
   - Название: `vX.Y.Z — <краткое описание>`.
   - Приложить собранный `.exe` (автоматически через release_exe workflow).
   - В описании: CHANGELOG (ключевые изменения).

## Интеграция с планом (plan-tracker)

При создании PR/Issue — обновить соответствующий план в `docs/plans/`:
- Связать issue с задачей плана.
- Отметить прогресс.

## Проверочный список

- [ ] Текущая ветка — feature (не main, не stable).
- [ ] Все изменения закоммичены и запушены.
- [ ] `pytest tests/ -q` — зелёный перед PR.
- [ ] Шаблон PR заполнен (метрики, скриншоты, checklist).
- [ ] Labels проставлены.
- [ ] Связанные issues указаны.
- [ ] CI-воркфлоу запущен, проверен статус.

## Связанные скиллы

- `code-change-protocol` (существующий) — правила коммитов и веток.
- `plan-tracker` (существующий) — синхронизация с планом.
- `code-review-reliability-first` — ревью перед PR.
- `mass-spec-report-writer` — отчёт для релиза.
