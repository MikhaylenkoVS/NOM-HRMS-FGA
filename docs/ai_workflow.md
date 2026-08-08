# AI Workflow — Полная схема

## Роли

| Роль | Исполнитель | Ответственность |
|------|------------|-----------------|
| **Planner / Researcher** | Perplexity | Исследование, декомпозиция, архитектурные решения, review |
| **Implementer** | DeepCode | Код, тесты, benchmark, commit, PR |
| **Approver** | Человек | Приоритеты, утверждение архитектурных решений, merge, релизы |

## Полный цикл задачи

```
1. Perplexity research & design
   ├── Исследование проблемы
   ├── Проектирование архитектуры
   ├── Определение acceptance criteria
   └── Заполнение task packet: design.md, acceptance.md, constraints.md, risks.md

2. Task packet создан (.ai/tasks/active/<task-id>/)
   ├── task.json (machine-readable)
   ├── context.md, design.md, acceptance.md
   ├── constraints.md, risks.md
   ├── human_decisions.md, rollback_plan.md
   └── Статус: draft → designed

3. Handoff Perplexity → DeepCode
   └── python tools/ai_workflow.py render-handoff <task-id>

4. DeepCode implementation
   ├── Изучение существующего кода
   ├── Создание feature branch (руками или через --create-branch)
   ├── Реализация в соответствии со scope
   ├── Добавление тестов
   ├── Запуск validation commands
   └── Заполнение implementation_report.md

5. DeepCode validation
   └── python tools/ai_workflow.py validate-task <task-id>

6. Perplexity review
   ├── Проверка scope alignment
   ├── Проверка научных инвариантов
   ├── Проверка безопасности
   └── Замечания → review_request.md

7. DeepCode fixes
   ├── Исправление только подтверждённых замечаний
   ├── Повторный запуск тестов
   └── Обновление implementation_report.md

8. Human approval
   ├── Проверка implementation report
   ├── Проверка benchmark (если применимо)
   ├── Проверка ADR (если применимо)
   └── Утверждение PR

9. PR merge (человек)
   └── Merge в main через GitHub UI

10. Завершение задачи
    ├── python tools/ai_workflow.py complete-task <task-id>
    └── python tools/ai_workflow.py archive-task <task-id>
```

## Статусы задачи

```
draft
  ↓ (Perplexity заполнил design, acceptance, constraints, risks)
designed
  ↓ (DeepCode начал реализацию)
implementation
  ↓ (Код написан, тесты добавлены)
validation
  ↓ (Тесты пройдены, validate-task успешен)
review
  ↓ (Perplexity проверил)
approved
  ↓ (Человек утвердил PR)
merged
  ↓ (complete-task)
completed
  ↓ (archive-task)
archived
```

## Команды CLI

| Команда | Назначение |
|---------|-----------|
| `new-task <id>` | Создать task packet |
| `validate-task <id>` | Проверить task packet |
| `collect-context <id>` | Собрать контекст |
| `render-handoff <id>` | Создать handoff для DeepCode |
| `task-status <id>` | Показать статус задачи |
| `complete-task <id>` | Завершить задачу |
| `archive-task <id>` | Архивировать задачу |
| `check-repo` | Проверить репозиторий |

## Когда task packet обязателен

| Task type | Task packet | ADR | Benchmark | Scientific validation |
|-----------|------------|-----|-----------|----------------------|
| architecture | required | required | — | — |
| scientific | required | required | — | required |
| performance | required | — | required | — |
| formula-db | required | required | — | — |
| packaging | required | — | — | — |
| security | required | — | — | — |
| feature | recommended | optional | optional | optional |
| refactor | recommended | optional | — | — |
| bugfix | high/critical only | optional | — | — |
| documentation | not required | — | — | — |
| test | not required | — | — | — |
| maintenance | not required | — | — | — |
