# Rollback Plan: DOC-01 — Черновик user guide

## Признаки проблемы
- Инструкции не соответствуют UI.
- Пользователь не может пройти первый сценарий.
- CSV format описан неверно.
- Есть неподтверждённые scientific claims.
- README ссылается на отсутствующий или устаревший guide.

## Быстрый откат
```bash
git revert <documentation-commit-sha>
```

Для выборочного восстановления:
```bash
git checkout <known-good-commit> -- docs/user_guide.md
```

Если добавлялась навигационная ссылка, восстановить также `README.md` или `docs/README.md`.

## После отката
1. Проверить Markdown links.
2. Создать follow-up GitHub Issue.
3. Исправить guide в отдельной ветке.
4. Повторить manual walkthrough.
5. При необходимости добавить lesson в `.ai/lessons/`.

## Полномочия
Rollback и повторная публикация выполняются человеком после review. DeepCode может подготовить исправление в отдельной ветке, но не меняет main самостоятельно.
