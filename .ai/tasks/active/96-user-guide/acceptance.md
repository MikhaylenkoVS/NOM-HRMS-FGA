# Acceptance Criteria: DOC-01 — Черновик user guide

## Must have
- [ ] Создан `docs/user_guide.md`.
- [ ] Руководство рассчитано на химика-пользователя, а не Python-разработчика.
- [ ] Описаны Windows executable и, только если подтверждено, Python/pip-installation.
- [ ] CSV schema описана по фактическому reader-коду и тестовым данным.
- [ ] Описаны обязательные колонки и распространённые ошибки CSV.
- [ ] Есть воспроизводимый сценарий загрузки и анализа трёх спектров.
- [ ] Все UI labels сверены с актуальным приложением.
- [ ] Описаны таблица результатов, Van Krevelen plot и гистограммы.
- [ ] Описаны presets `coal`, `peat`, `soil`, `water`.
- [ ] Указано, что preset — стартовая точка, а не гарантия правильного результата.
- [ ] Есть troubleshooting минимум с пятью практическими случаями.
- [ ] Явно описаны научные ограничения автоматической интерпретации.
- [ ] В README или docs README добавлена ссылка на user guide.
- [ ] Первый сценарий вручную пройден на тестовой или реальной тройке спектров.
- [ ] Нет неподтверждённой функциональности, абсолютных путей, secrets или placeholder-маркеров.

## Must not
- [ ] Не изменяются source code, алгоритмы, presets или CSV format.
- [ ] Не утверждается, что формула доказывает структуру.
- [ ] Не утверждается, что preset универсален.
- [ ] Не используются screenshots другой версии приложения.

## Manual validation
- [ ] Открыть guide в чистом checkout/release package.
- [ ] Пройти installation/start scenario.
- [ ] Подготовить CSV по инструкции.
- [ ] Выполнить загрузку трёх спектров.
- [ ] Сверить UI labels.
- [ ] Проверить ссылки и Markdown rendering.

## Suggested validation commands
```bash
python tools/ai_workflow.py validate-task 96-user-guide
python tools/ai_workflow.py check-repo
pytest tests/ -q -m smoke
```
