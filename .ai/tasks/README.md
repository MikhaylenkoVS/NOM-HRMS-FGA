# Tasks

| Директория | Описание |
|-----------|----------|
| `active/` | Задачи в работе |
| `completed/` | Завершённые и merged задачи |
| `archived/` | Архив старых задач |

## Task packet

Каждая задача — директория с `task.json` и набором артефактов.
См. [.ai/templates/](../templates/) и [.ai/contracts/task.schema.json](../contracts/task.schema.json).

## Создание задачи

```bash
python tools/ai_workflow.py new-task <task-id> --title "..." --type <type> --risk <level>
```
