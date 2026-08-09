# Human Decisions: DOC-01 — Черновик user guide

| # | Статус | Вопрос | Решение / требуемое решение | Обоснование |
|---:|---|---|---|---|
| 1 | Proposed | Язык руководства | Русский; точные UI labels сохраняются в исходной форме | Issue и аудитория русскоязычные |
| 2 | Proposed | Целевая аудитория | Химик/аналитик с базовым пониманием HRMS, без требования знания Python | Это user guide, а не developer guide |
| 3 | Proposed | Формат v0.6 | Один Markdown-файл `docs/user_guide.md` | Легко версионировать и ревьюить |
| 4 | Pending | Нужны ли screenshots в v0.6? | По умолчанию нет; добавлять только после отдельного решения и сверки с release UI | Screenshots быстро устаревают |
| 5 | Pending | Какой installer/EXE описывать? | Проверить release workflow и фактические release artifacts | Нельзя угадывать установочный сценарий |
| 6 | Pending | Поддерживается ли user-facing pip installation? | Добавить только после воспроизводимой проверки | Developer и end-user сценарии могут отличаться |
| 7 | Pending | Минимальные CSV колонки | Определить по reader-коду и тестовым CSV | Нельзя выводить schema из общего знания HRMS |
| 8 | Pending | Порядок загрузки трёх спектров | Определить по UI и smoke test | Issue не фиксирует интерфейсный workflow |
| 9 | Pending | Назначение presets | Проверить JSON settings и реальный запуск | Нужно избежать неподтверждённых рекомендаций |
| 10 | Required before merge | Release target guide | Указать version/tag/commit | Документ должен относиться к проверяемой версии |
| 11 | Required before merge | Manual walkthrough | Указать исполнителя, дату, dataset и версию | Доказательство воспроизводимости инструкции |
