---
name: hrms-formula-assignment
description: >
  Правила присвоения брутто-формул CHON по точным массам в режиме [M–H]⁻.
  Активировать когда пользователь говорит «назначить формулы», «assign formulas»,
  «brutto», «брутто-формула», «формула по массе», «ppm», «CHON enumeration»,
  «FormulaSearchConfig», «assign_formulas», «exact_mass_from_counts»,
  «нейтральная масса», «ion mode», «[M-H]-»; либо при изменении кода в
  spectrum_ops.py (строки 607–812), pipeline.json (секции formula_search,
  default_brutto_dict), chemistry.json (monoisotopic_masses, proton_mass,
  default_ion_mode).
---

# HRMS Formula Assignment — присвоение брутто-формул

Назначение брутто-формул CₓHₓOₓNₓ методом полного перебора (brute-force CHON
enumeration) по точной массе моноизотопного пика в режиме [M–H]⁻. Скилл
описывает все параметры, источники истины и порядок действий при внесении
изменений в эту часть конвейера.

## Источники истины (читать в первую очередь)

| Файл | Что содержит |
|------|-------------|
| `src/core/spectrum_ops.py:607–812` | `assign_formulas()` — основная реализация |
| `src/core/spectrum_ops.py:68–113` | `FormulaSearchConfig` — dataclass с диапазонами и порогами |
| `src/core/spectrum_ops.py:115–153` | `exact_mass_from_counts()`, `dbe_from_counts()` |
| `src/core/spectrum_ops.py:332–450` | `_generate_candidate_formulas()` — генератор кандидатов |
| `src/core/spectrum_ops.py:457–497` | `_neutral_to_ion_mass()` — конверсия neutral↔ion |
| `src/core/spectrum_ops.py:526–597` | `_beynon_m1_ratio()`, `_measure_m1_ratio()` — изотопный фильтр |
| `src/core/spectrum_ops.py:600–605` | `_nom_distance()` — NOM-расстояние |
| `src/configs/chemistry.json` | Моноизотопные массы, proton_mass, ΔCD3, ΔCD3CO, default_ion_mode |
| `src/configs/pipeline.json` | `formula_search`, `default_brutto_dict`, `run_pipeline_defaults` |
| `src/core/pipeline.py:339–418` | `run_pipeline()` — параметры `rel_error`, `sign`, `assign_mass_min/max` |

## Параметры и их значения по умолчанию

### Моноизотопные массы элементов (chemistry.json → `ATOMIC_MASS`)

```
H  = 1.00782503223
C  = 12.0
N  = 14.00307400443
O  = 15.99491461957
S  = 31.9720711744
P  = 30.97376199842
proton_mass  = 1.007276466812
electron_mass = 0.0005485654179999688
```

**КРИТИЧЕСКИ:** ни одна цифра не должна меняться без экспертного подтверждения.
Изменение моноизотопной массы элемента на 1 ppm сдвигает все формулы.

### Диапазоны элементов — два набора (не перепутать!)

| Источник | C | H | O | N | Где используется |
|----------|---|---|---|---|-----------------|
| `formula_search.ranges` | [1, 50] | [4, 100] | [0, 20] | [0, 8] | `FormulaSearchConfig` — **основной**, жёсткие лимиты перебора |
| `default_brutto_dict` | [0, 50] | [0, 100] | [0, 25] | [0, 10] | `DEFAULT_BRUTTO_DICT` — устаревший/вспомогательный, **не для перебора** |

При изменениях: `default_brutto_dict` считается устаревшим. Новые ограничения —
только в `formula_search.ranges`. Если меняешь одно — проверь, не используется
ли второе в вызывающем коде.

### Химические фильтры (pipeline.json → formula_search)

| Параметр | Значение | Смысл |
|----------|----------|-------|
| `max_hc` | 3.0 | H/C ≤ 3 — отсекает алканы и экзотику |
| `max_oc` | 1.2 | O/C ≤ 1.2 — отсекает углеводы/кислоты с избытком O |
| `max_nc` | 1.0 | N/C ≤ 1.0 — отсекает высокоазотистые |
| `max_dbe` | 30.0 | DBE ≤ 30 — отсекает нереально конденсированные |
| `min_c` | 1 | Минимум один углерод |

### Параметры assign_formulas()

```python
def assign_formulas(
    src,                              # Spectrum — входной спектр (масс-лист)
    rel_error_ppm: float = 1.0,       # ppm-окно допуска для кандидата
    mass_min: float | None = None,    # Нижняя граница нейтральной массы
    mass_max: float | None = None,    # Верхняя граница нейтральной массы
    search_config: FormulaSearchConfig | None = None,  # Конфиг перебора
    brutto_generation_mode: str = "nom_like",  # Устарел — игнорируется
    ion_mode: str = "[M-H]-",         # Режим ионизации
    nom_weight: float = 1.0,          # Вес NOM-расстояния в скоре
    isotope_filter: bool = False,     # Изотопный M+1 фильтр Бейнона
    original=None,                    # Исходный (pre-denoise) спектр для M+1
    **kwargs,                         # Обратная совместимость (mode, nom_prioritize…)
)
```

Важно:
- `mode`, `nom_prioritize`, `brutto_dict`, `sign`, `rel_error`, `formulas` —
  извлекаются из **kwargs и игнорируются**. Это обратная совместимость, будет
  удалено в v1.
- `brutto_generation_mode` — игнорируется (оставлен для совместимости), также
  подлежит удалению в v1.
- `assign_formulas_nomspectra()` (строка 813) — **не используется**, тупиковая ветвь.

### Параметры run_pipeline(), влияющие на assign

```python
rel_error: float = PIPELINE.run_pipeline_defaults["rel_error"]    # 1.0 ppm
sign: str = PIPELINE.run_pipeline_defaults["sign"]                # "-" → [M-H]-
assign_mass_min: float = 0.0
assign_mass_max: float = 1000.0
isotope_filter: bool = False
```

Конверсия `sign="-"` → `ion_mode="[M-H]-"` происходит внутри `run_pipeline()`.

## Алгоритм назначения (пошагово)

### Шаг 1: Определение массового окна
- Если `mass_min`/`mass_max` не заданы — берутся min/max из `src.table["mass"]`.
- Массовое окно **сдвигается** на массу носителя заряда: для [M–H]⁻ к наблюдаемой
  массе добавляется `proton_mass` (1.007276466812), чтобы окно было в нейтральных массах.
- К окну добавляется запас ±1% для компенсации ошибок округления.

### Шаг 2: Генерация кандидатов (`_generate_candidate_formulas`)
- Полный перебор C×H×O×N в заданных диапазонах.
- Оптимизация: предвычисленные min/max массы для каждого элемента исключают
  заведомо неподходящие комбинации.
- Для каждого кандидата вычисляется точная нейтральная масса (`exact_mass_from_counts`).
- Кандидаты, чья масса выходит за окно — отбрасываются.

### Шаг 3: Жёсткие фильтры
- DBE ≤ max_dbe (30.0)
- H/C ≤ max_hc (3.0)
- O/C ≤ max_oc (1.2)
- N/C ≤ max_nc (1.0)
- min_c ≥ 1

### Шаг 4: Конверсия нейтральная → ионная масса
`_neutral_to_ion_mass()` — прибавляет или вычитает массу протона/электрона
в зависимости от `ion_mode`. Только [M–H]⁻ поддерживается полноценно.

### Шаг 5: Отбор кандидатов в ppm-окно
- Для каждого наблюдаемого пика: кандидаты, чья ионная масса попадает
  в `±rel_error_ppm` от наблюдаемой массы.
- Ppm используется **только для фильтрации**, не для ранжирования.

### Шаг 6: Ранжирование (soft scoring)
- `_nom_distance(hc, oc)` — евклидово расстояние от точки (O/C, H/C) до
  центров NOM-областей Ван-Кревелена (берутся из `NOM_REGIONS` в van_krevelen.py).
- Score = `nom_weight * nom_distance + penalties`.
- penalties включают:
  - Штраф за несовпадение изотопного паттерна M+1/M (если `isotope_filter=True`),
    порог расхождения 20% (`_ISOTOPE_TOLERANCE = 0.20`), штраф +2.0.

### Шаг 7: Выбор лучшего
- Для каждого пика выбирается кандидат с минимальным score.
- Если кандидатов нет — `brutto = None`, `assign = False`.
- В `table["all_candidates"]` сохраняется список строк-формул всех кандидатов
  (только для режима отладки).

## Обработка изотопных меток

Изотопные метки ΔCD3 и ΔCD3CO **не обрабатываются** на этапе assign_formulas —
они используются на этапе find_series. См. скилл `nom-chemical-validity`.

Однако в `assign_formulas` есть **изотопный фильтр Бейнона** (`isotope_filter=True`):
1. Для каждого кандидата вычисляется теоретическое отношение (M+1)/M через
   `_beynon_m1_ratio()` с коэффициентами ¹³C:1.1%, ²H:0.015%, ¹⁷O:0.04%, ¹⁵N:0.37%.
2. В исходном (pre-denoise) спектре измеряется реальное отношение M+1/M
   через `_measure_m1_ratio()` — поиск пика на массе `mass + 1.00335` Da.
3. Если |реальное − теоретическое| / теоретическое > 20%, кандидат получает
   штраф +2.0 к score.

## Проверочный список перед изменениями

- [ ] Изменения в `chemistry.json` (массы, сдвиги, Δ) не затронули значащие цифры?
- [ ] Изменения в `pipeline.json` (диапазоны, пороги) синхронизированы с
      `FormulaSearchConfig` (значения по умолчанию в dataclass)?
- [ ] Не используется ли `default_brutto_dict` вместо `formula_search.ranges`
      в новом коде?
- [ ] Не сломан ли `assign_formulas_nomspectra()` (если он ещё не удалён)?
- [ ] Нет ли хардкода ppm/диапазонов/масс в обход `src/configs/`?
- [ ] Запущены `pytest tests/unit/test_assign_formulas.py` и
      `pytest tests/unit/test_core_utils.py` — все зелёные?
- [ ] Запущены `pytest tests/integration/test_pipeline_integration.py` — denoise_recall
      ≥ 0.90, assign_recall ≥ 0.90?
- [ ] При добавлении новых элементов (S, P) — обновлены `atomic_mass_elements`,
      `monoisotopic_masses`, диапазоны в `formula_search.ranges`, и
      `_generate_candidate_formulas()`?
- [ ] Параметр `mode` / `brutto_generation_mode` не добавляется в новые вызовы?

## Типичные ошибки (что ловить при ревью)

1. **Хардкод массы:** `proton_mass = 1.0078` вместо `CHEM.proton_mass`.
2. **Забыт сдвиг neutral→ion:** генерация кандидатов в нейтральных массах,
   сравнение с ионными без конверсии.
3. **Ppm вместо ранжирования:** выбор формулы с минимальным |ppm|, а не с
   минимальным NOM-distance. Ppm — только фильтр!
4. **Выход за границы диапазонов:** C=0 (min_c=1 должен отсечь), H=0.
5. **NaN в mass:** не проверяется `pd.isna(mass)` перед вычислением ppm.
6. **Изотопный фильтр без original:** `isotope_filter=True`, но `original=None`
   → AttributeError при доступе к `original.table`.

## Связанные скиллы

- `nom-chemical-validity` — подробно о DBE, H/C, O/C, N/C, NOM-расстоянии.
- `config-safety-audit` — аудит pipeline.json/chemistry.json.
- `pytest-regression-nom` — написание тестов для assign.
