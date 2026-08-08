# AI Workflow

## Роли

| Роль | Исполнитель | Ответственность |
|------|------------|-----------------|
| **Planner / Researcher** | Perplexity | Исследование, декомпозиция, архитектурные решения, review |
| **Implementer** | DeepCode | Код, тесты, benchmark, commit, PR |
| **Approver** | Человек | Приоритеты, утверждение архитектурных решений, merge, релизы |

## Полный цикл задачи

```
Perplexity research/design
  ↓
task packet создан (.ai/tasks/active/<task-id>/)
  ↓
DeepCode: feature branch создана
  ↓
DeepCode: реализация + тесты + implementation report
  ↓
Perplexity: архитектурное ревью
  ↓
DeepCode: исправления по замечаниям
  ↓
Человек: утверждение
  ↓
PR merge (человек)
  ↓
complete-task → .ai/tasks/completed/<task-id>/
  ↓
archive-task → .ai/tasks/archived/<task-id>/
```

## Статусы задачи

```
draft → designed → implementation → validation → review → approved → merged → completed → archived
```

## Команды CLI

```bash
python tools/ai_workflow.py new-task <id> --title "..." --type <type> --risk <level>
python tools/ai_workflow.py validate-task <id>
python tools/ai_workflow.py collect-context <id>
python tools/ai_workflow.py render-handoff <id>
python tools/ai_workflow.py task-status <id>
python tools/ai_workflow.py complete-task <id>
python tools/ai_workflow.py archive-task <id>
python tools/ai_workflow.py check-repo
python tools/run_benchmark.py <benchmark-id> --task-id <id>
```

## Benchmark execution policy

- Benchmarks run only via registered IDs in `tools/run_benchmark.py` allowlist
- Arbitrary shell commands are NEVER accepted
- New benchmark IDs require human-approved PR
- Unknown benchmark IDs produce blocking failure
- `validate-task` must pass before benchmark runs

## Когда нужен task packet

Обязателен для типов: `architecture`, `scientific`, `performance`, `formula-db`, `packaging`, `security`.

Рекомендован для: `feature`, `refactor`, `bugfix` (high/critical).

Не требуется для: `documentation` (тривиальные правки), `maintenance` (мелкие исправления), `test` (добавление тестов без изменения логики).
