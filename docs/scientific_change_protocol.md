# Scientific Change Protocol

## Обязательные требования

Любое изменение, влияющее на научные результаты, требует:

### 1. Scientific invariant

Явно сформулировать, какой научный инвариант сохраняется:

```markdown
**Invariant:** Candidate-set equivalence — для всех молекул из reference
dataset набор кандидатов-формул должен совпадать с точностью до N формул.
```

### 2. Reference dataset или reference implementation

Указать, на каких данных проверяется эквивалентность:

- `data/test_sets/set_01/` — синтетический набор (известен ground truth)
- `data/ref_data/` — эталонные молекулы

### 3. Candidate-set equivalence

Для изменений в `assign_formulas` или `spectrum_ops`:

- Запустить на всех test_sets
- Сравнить набор кандидатов до и после изменения
- Допустимое отклонение должно быть указано явно

### 4. False positives / False negatives

Описать риски:

```markdown
**FP risk:** Новый фильтр DBE > 0.5 может исключить валидные
серосодержащие молекулы с низким DBE.
**FN risk:** Без фильтра DBE проходят физически невозможные формулы.
```

### 5. Reversible change

Изменение должно быть обратимым:

- Конфигурация через `pipeline.json` (можно переключить порог)
- Git revert возможен без потери данных
- Старая formula DB остаётся совместимой

### 6. Versioned method/configuration

- Версия метода в `chemistry.json` или `pipeline.json`
- Комментарий в коде с датой изменения и автором
- ADR с описанием причин изменения

### 7. Human approval

- **Человек утверждает** все изменения scientific-класса
- DeepCode не может самостоятельно менять научные инварианты
- Perplexity выполняет scientific review, но не утверждает

## Процесс

```
1. Сформулировать scientific invariant
2. Выбрать reference dataset
3. Запустить baseline measurements
4. Внести изменение
5. Проверить candidate-set equivalence
6. Задокументировать риски FP/FN
7. Создать ADR
8. Получить human approval
9. Merge
```

## Пример

```markdown
**Задача:** Добавить фильтр H/C ratio для исключения не-NOM-like молекул.

**Invariant:** Все молекулы из reference dataset (set_01..set_05)
должны остаться в candidate set.

**Reference:** data/ref_data/ref_molecules_all_pubchem_filtered.csv

**FP risk:** Исключение серосодержащих молекул с H/C < 0.3
**FN risk:** — (фильтр не добавляет новые формулы)

**Validation:** pytest tests/unit/test_chemical_validity.py
```
