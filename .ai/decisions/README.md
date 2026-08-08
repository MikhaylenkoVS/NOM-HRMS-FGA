# Architecture Decision Records

Архитектурные решения для NOM-HRMS-FGA.

## Структура

- `template.md` — шаблон ADR
- `index.md` — индекс всех ADR
- `NNNN-short-title.md` — конкретная запись

## Статусы

| Статус | Значение |
|--------|---------|
| `proposed` | Решение предложено, обсуждается |
| `accepted` | Решение утверждено и действует |
| `superseded` | Решение заменено более новым |
| `deprecated` | Решение устарело, не используется |

## Создание ADR

1. Скопировать `template.md` → `NNNN-short-title.md`
2. Заполнить все разделы
3. Добавить в `index.md`
4. Указать ссылку в `task.json` → `links.adr`

## Требования

- ADR обязателен для задач класса `architecture`, `scientific`, `formula-db`
- ADR создаётся человеком или Perplexity
- DeepCode может предложить ADR, но не утверждает его самостоятельно
- При superseding/deprecating старый ADR остаётся в истории
