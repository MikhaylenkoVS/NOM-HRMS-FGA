# Lessons Learned

Опыт, извлечённый из завершённых задач.

## Формат

Каждый урок — отдельный markdown-файл с датой и тегами.

## Пример

```markdown
# 2026-08-08: Always pin RDKit version

**Tags:** dependencies, reproducibility
**Context:** RDKit 2024 broke API for MolToImage()
**Lesson:** Pin RDKit to >=2023.9,<2024 in pyproject.toml
```
