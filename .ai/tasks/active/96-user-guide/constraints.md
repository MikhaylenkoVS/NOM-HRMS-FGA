# Constraints: DOC-01 — Черновик user guide

## Functional constraints
- Основной результат: `docs/user_guide.md`.
- Руководство отражает только подтверждённую функциональность release target.
- Все утверждения о UI, CSV, параметрах и presets проверяются по коду, конфигурации и ручному запуску.
- Неясности фиксируются в `human_decisions.md`.

## Technical constraints
- Не менять source code, scientific algorithms, JSON presets, тестовые данные или зависимости.
- Не добавлять secrets, credentials, персональные пути или большие бинарные screenshots.
- Использовать GitHub-compatible Markdown и относительные ссылки.

## Allowed paths
```text
docs/user_guide.md
docs/README.md
README.md
.ai/tasks/active/96-user-guide/
```

## Forbidden paths
```text
src/
tests/
data/
tools/
external/
thermo/
.github/
pyproject.toml
requirements.txt
src/configs/presets/
```

## Non-goals
Полная API-документация, учебник по Python/Git/RDKit, полная теория NOM/HRMS, изменение UI ради документации, новый installer или поддержка неподтверждённых форматов.
