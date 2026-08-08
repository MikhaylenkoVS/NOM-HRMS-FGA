# AI Review Protocol

## Виды ревью

### 1. Implementation Review (DeepCode self-check + Perplexity)

Проверяет:
- [ ] Соответствие кода task packet
- [ ] Отсутствие scope creep
- [ ] Корректность типов и обработки ошибок
- [ ] Читаемость и поддерживаемость
- [ ] Стиль соответствует `.flake8` и `black`

### 2. Architecture Review (Perplexity)

Проверяет:
- [ ] Соответствие diff → task packet scope
- [ ] Нет scope creep
- [ ] API совместимость сохранена
- [ ] Новые зависимости обоснованы
- [ ] Воспроизводимость результатов
- [ ] Риски потери данных
- [ ] Научные инварианты не нарушены
- [ ] Безопасность
- [ ] Возможность отката
- [ ] Покрытие тестами
- [ ] Валидность benchmark (если применимо)

### 3. Scientific Review (Perplexity + Человек)

Проверяет:
- [ ] Сформулирован scientific invariant
- [ ] Reference dataset определён
- [ ] Candidate-set equivalence подтверждена
- [ ] Риски false positives/false negatives описаны
- [ ] Изменение обратимо
- [ ] Метод/конфигурация версионированы
- [ ] Human approval получен

### 4. Performance Review (Perplexity)

Проверяет:
- [ ] Baseline зафиксирован в `.ai/baselines/`
- [ ] Benchmark methodology корректен
- [ ] Результаты сопоставимы
- [ ] Нет скрытых регрессий
- [ ] Trade-offs документированы

### 5. Security Review (Perplexity)

Проверяет:
- [ ] Нет секретов в коде
- [ ] Нет unsafe file operations
- [ ] Нет injection vectors
- [ ] Минимальные permissions в CI
- [ ] Зависимости проверены (pip-audit)

### 6. Release Review (Perplexity + Человек)

Проверяет:
- [ ] Версия консистентна
- [ ] Все тесты проходят
- [ ] CHANGELOG обновлён
- [ ] Formula DB совместима
- [ ] .exe собирается
- [ ] Нет tracked secrets
- [ ] Release notes готовы

## Процесс ревью

```
DeepCode: implementation_report.md
  ↓
Perplexity: architecture review → review_request.md
  ↓
DeepCode: fixes → обновление implementation_report.md
  ↓
Человек: final approval → merge
```
