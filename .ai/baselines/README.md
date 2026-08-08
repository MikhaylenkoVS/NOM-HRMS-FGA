# Baselines

Эталонные измерения производительности для benchmark-задач.

## Структура

Каждый baseline — отдельный файл с метаданными и числовыми значениями.

## Формат

```markdown
# Baseline: <name>

- **Date:** YYYY-MM-DD
- **Hardware:** [CPU, RAM, OS]
- **Python:** [version]
- **Commit:** [commit SHA]
- **Command:** [exact command]

## Results

| Metric | Value |
|--------|-------|
| | |
```

## Обновление

Baseline обновляется ТОЛЬКО человеком после успешного benchmark.

DeepCode может предложить обновление через `benchmark_report.md`, но не
перезаписывает baseline автоматически.
