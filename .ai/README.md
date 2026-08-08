# .ai/ — AI Workflow Infrastructure

Директория для совместной работы Perplexity (исследование, архитектура, review),
DeepCode (реализация, тесты, commit/PR) и человека (приоритеты, утверждение, merge, релизы).

## Структура

| Директория | Назначение |
|-----------|-------------|
| `tasks/active/` | Активные task packet'ы |
| `tasks/completed/` | Завершённые (merged) задачи |
| `tasks/archived/` | Архив выполненных задач |
| `templates/` | Шаблоны файлов task packet |
| `contracts/` | JSON Schemas для валидации |
| `decisions/` | Architecture Decision Records (ADR) |
| `prompts/` | Prompt registry для AI-агентов |
| `reports/` | Сводные отчёты по проекту |
| `lessons/` | Lessons learned |
| `baselines/` | Benchmark baselines |

## Быстрый старт

```bash
# Создать новую задачу
python tools/ai_workflow.py new-task <task-id> --title "..." --type feature --risk medium

# Валидировать task packet
python tools/ai_workflow.py validate-task <task-id>

# Проверить репозиторий
python tools/ai_workflow.py check-repo
```

## Ссылки

- [AGENTS.md](../AGENTS.md) — правила для AI-агентов
- [docs/ai_workflow.md](../docs/ai_workflow.md) — схема рабочего процесса
- [docs/ai_task_lifecycle.md](../docs/ai_task_lifecycle.md) — жизненный цикл задачи
- [docs/ai_review_protocol.md](../docs/ai_review_protocol.md) — протокол ревью
