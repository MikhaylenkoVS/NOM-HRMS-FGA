---
name: deepcode-orchestrator
description: >
  Мета-скилл — оркестратор всех скиллов проекта NOM-HRMS-FGA. Определяет,
  какой скилл активировать под задачу пользователя, в каком порядке вызывать
  скиллы для комплексных сценариев (релиз, рефакторинг, отладка, полный цикл
  проверки). Активировать в начале каждой сессии для определения контекста
  и при сложных многошаговых запросах («полный цикл», «подготовить релиз»,
  «проверить всё», «комплексная проверка», «от и до»).
allowed-tools: [AskUserQuestion, Bash, Read, Write, Edit, UpdatePlan]
---

# DeepCode Orchestrator — оркестратор скиллов

Мета-скилл верхнего уровня. Не выполняет конкретную работу, а определяет
**какой скилл активировать** в зависимости от задачи пользователя. Для
комплексных сценариев выстраивает цепочку вызовов скиллов в правильном порядке.

## Карта скиллов проекта

| Скилл | За что отвечает | Ключевые файлы |
|-------|----------------|---------------|
| `hrms-formula-assignment` | Присвоение брутто-формул по массам | `spectrum_ops.py`, `pipeline.json` |
| `nom-chemical-validity` | Хим. валидность формул (DBE, H/C, O/C, N/C) | `spectrum_ops.py:499–605`, `van_krevelen.py` |
| `spectrum-denoise-review` | Шумоподавление спектров | `spectrum_ops.py:288–319`, `denoise()` |
| `pytest-regression-nom` | Написание/запуск тестов | `tests/`, `pytest.ini` |
| `tkinter-gui-debug` | Диагностика GUI, сборка .exe | `app.py`, `ui/`, `structures/`, `tools/` |
| `config-safety-audit` | Аудит конфигурации, поиск хардкода | `configs/`, все `src/**/*.py` |
| `mass-spec-report-writer` | Генерация научного отчёта | Результаты pipeline |
| `code-review-reliability-first` | Главный code review | Все `src/`, `tests/` |
| `test-set-generator` | Генерация синтетических наборов | `simulations/`, `ref_data/` |
| `deepcode-github-mcp-pr` | GitHub PR/Issue/Release | `.github/`, git |

Плюс существующие скиллы (не пересоздавались):
| Скилл | Назначение |
|-------|-----------|
| `code-review-assistant` | Универсальный ревьюер (переопределён `code-review-reliability-first`) |
| `code-change-protocol` | Протокол коммитов, защита веток |
| `plan-tracker` | Планы в `docs/plans/` |
| `auto-model-select` | Выбор модели DeepSeek |

## Таблица маршрутизации: запрос пользователя → скилл(ы)

### Простые запросы (1 скилл)

| Запрос пользователя | Активировать |
|---------------------|-------------|
| «Назначь формулы», «почему этот пик — C7H6O2?» | `hrms-formula-assignment` |
| «Проверь DBE», «какой порог H/C?», «почему высокоазотистые проходят?» | `nom-chemical-validity` |
| «Денойз спектра», «какой force выбрать?» | `spectrum-denoise-review` |
| «Напиши тест для X», «запусти pytest» | `pytest-regression-nom` |
| «Почини GUI», «добавь кнопку», «собери .exe» | `tkinter-gui-debug` |
| «Найди хардкод», «проверь конфиг» | `config-safety-audit` |
| «Напиши отчёт», «подготовь экспериментальную секцию» | `mass-spec-report-writer` |
| «Сделай ревью этого diff», «проверь PR» | `code-review-reliability-first` |
| «Сгенерируй set_06», «новый тестовый набор» | `test-set-generator` |
| «Создай PR», «открой issue» | `deepcode-github-mcp-pr` |

### Комплексные сценарии (цепочка скиллов)

#### Сценарий A: «Полный цикл проверки перед PR»

```
1. config-safety-audit       # Проверить хардкоды
2. pytest-regression-nom     # Запустить тесты
3. code-review-reliability-first  # Ревью кода
4. deepcode-github-mcp-pr    # Оформить PR
```

#### Сценарий B: «Подготовка релиза vX.Y.Z»

```
1. config-safety-audit       # Аудит конфигурации
2. pytest-regression-nom     # Полный прогон тестов
3. spectrum-denoise-review   # Проверить метрики denoise/assign
4. tkinter-gui-debug         # Проверить сборку .exe
5. mass-spec-report-writer   # Обновить CODE_AVAILABILITY.md
6. deepcode-github-mcp-pr    # Создать Release
```

#### Сценарий C: «Новый тестовый набор»

```
1. test-set-generator        # Сгенерировать set_06
2. nom-chemical-validity     # Проверить молекулы на NOM-like
3. pytest-regression-nom     # Интегрировать в тесты
4. config-safety-audit       # Обновить paths.json (num_test_sets)
```

#### Сценарий D: «Рефакторинг denoise»

```
1. config-safety-audit       # Проверить настройки denoise
2. spectrum-denoise-review   # Code review алгоритмов
3. code-review-reliability-first  # Общий review
4. pytest-regression-nom     # Обновить/расширить тесты
```

#### Сценарий E: «Отладка падения GUI»

```
1. tkinter-gui-debug         # Диагностика GUI
2. config-safety-audit       # Проверить test_mode параметры
3. pytest-regression-nom     # Smoke-тест app_smoke
```

#### Сценарий F: «Добавление нового химического фильтра»

```
1. nom-chemical-validity     # Спроектировать фильтр
2. hrms-formula-assignment   # Интегрировать в assign_formulas
3. config-safety-audit       # Добавить порог в pipeline.json
4. code-review-reliability-first  # Ревью
5. pytest-regression-nom     # Тесты с новым фильтром
6. test-set-generator        # (опционально) новый набор для проверки фильтра
```

## Алгоритм оркестратора

### При старте сессии

1. Определить, есть ли активная задача (из предыдущего контекста или
   `docs/plans/`).
2. Если задача продолжается — активировать соответствующий скилл.
3. Если задача новая — классифицировать запрос (см. таблицу маршрутизации).
4. Для комплексных сценариев — вывести план в `UpdatePlan` и запросить
   подтверждение пользователя.

### При неясном запросе

Если запрос не соответствует ни одному скиллу из таблицы — задать
уточняющий вопрос через `AskUserQuestion`, предложив 2–3 наиболее
вероятных скилла.

### Предложить оптимальный порядок

Для комплексных сценариев важен порядок:
- Сначала аудит (config-safety-audit, code-review).
- Потом тесты (pytest-regression-nom).
- Потом интеграция (GitHub, отчёты).

Это минимизирует итерации: если аудит находит хардкод, тесты запускать рано.

## Правила взаимодействия скиллов

- Скиллы **не вызывают друг друга автоматически**. Оркестратор сообщает
  пользователю, какой скилл нужен следующим, и ждёт подтверждения.
- Результат одного скилла может быть входом для другого (например, метрики
  из `pytest-regression-nom` → в `mass-spec-report-writer`).
- Скилл `code-review-reliability-first` имеет приоритет над
  `code-review-assistant` для всего кода проекта.

## Проверочный список оркестратора

- [ ] Запрос классифицирован по таблице маршрутизации.
- [ ] Для комплексного сценария — выведен план с порядком скиллов.
- [ ] Пользователь подтвердил план (или скорректировал).
- [ ] Каждый шаг выполняется с активированным соответствующим скиллом.
- [ ] После завершения цепочки — итоговая сводка в чате.
- [ ] Все созданные файлы/коммиты соответствуют code-change-protocol.
