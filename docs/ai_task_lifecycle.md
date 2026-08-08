# Task Lifecycle

## Статусы

| Статус | Значение | Кто меняет |
|--------|---------|-----------|
| `draft` | Задача создана, ожидает проектирования | Perplexity |
| `designed` | Дизайн готов, можно передавать DeepCode | Perplexity |
| `implementation` | DeepCode реализует | DeepCode |
| `validation` | Код написан, запускаются тесты | DeepCode |
| `review` | Задача отправлена на ревью | DeepCode |
| `approved` | Ревью пройдено, ожидает merge | Человек |
| `merged` | PR слит в main | Человек |
| `completed` | Задача перенесена в completed/ | DeepCode/CLI |
| `archived` | Задача в архиве | DeepCode/CLI |

## Допустимые переходы

```
draft → designed
designed → implementation
implementation → validation
validation → review
validation → implementation  (возврат на доработку)
review → approved
review → implementation      (возврат на доработку)
approved → merged
merged → completed
completed → archived
```

## Required artifacts per task type

| Task type | design.md | acceptance.md | implementation_report.md | benchmark_report.md | rollback_plan.md | ADR |
|-----------|-----------|---------------|------------------------|--------------------|------------------|-----|
| architecture | required | required | required | — | required | required |
| scientific | required | required | required | — | required | required |
| performance | required | required | required | required | required | — |
| formula-db | required | required | required | — | required | required |
| packaging | required | required | required | — | required | — |
| security | required | required | required | — | required | — |
| feature | required | required | required | — | optional | — |
| refactor | required | required | required | — | optional | — |
| bugfix | optional | optional | required | — | high/critical only | — |
| documentation | — | — | — | — | — | — |
| test | — | — | — | — | — | — |
| maintenance | — | — | — | — | — | — |

## Примеры задач по уровню риска

### Low risk
- Добавление unit-теста на существующую функцию
- Исправление опечатки в документации
- Обновление README

### Medium risk
- Добавление нового параметра в конфигурацию
- Рефакторинг внутренней функции без изменения API
- Оптимизация отрисовки графика

### High risk
- Изменение алгоритма денойзинга
- Изменение порогов химической валидности
- Изменение формата formula database

### Critical risk
- Изменение способа расчёта масс
- Изменение схемы дериватизации
- Миграция формата данных с потерей обратной совместимости
