# ADR-0002: Проброс знака иона и диапазонов элементов в научные стадии

- **Status:** proposed
- **Date:** 2026-10-12
- **Owners:** deepcode (требует утверждения человеком)
- **Related task:** gui-01-settings-wiring
- **Related issue/PR:** none
- **Supersedes:** none
- **Superseded by:** none

## Context

Аудит GUI выявил, что настройки «Знак иона» (`sign`) и «Диапазоны
элементов» (`brutto_dict`) передаются в `run_pipeline`, но не доходят до
научных стадий: `assign_formulas` всегда использует
`CHEM.default_ion_mode` (`[M-H]-`) и дефолтный `FormulaSearchConfig()` из
конфига. В результате пользователь меняет настройки, а результат не
меняется. `find_series` также жёстко использует `CHEM.default_ion_mode`
при расчёте теоретической m/z.

Необходимо решить, как интерпретировать знак «+» в GUI/CLI, поскольку
форма `[M+H]+` и `[M]+` дают разный сдвиг масс.

## Decision

1. Маппинг знака иона в режим ионизации:
   - `"-"` → `"[M-H]-"`
   - `"+"` → `"[M+H]+"` (протонированная молекула; стандарт для ESI(+))
   - любое другое/пустое значение → `CHEM.default_ion_mode` (fallback)
2. `run_pipeline` передаёт полученный `ion_mode` в `assign_formulas`
   (параметр `ion_mode`) и в `find_series` (новый необязательный параметр
   `ion_mode=None`, при `None` — `CHEM.default_ion_mode`).
3. `brutto_dict` из GUI/CLI конвертируется в `FormulaSearchConfig(ranges=...)`
   и передаётся в `assign_formulas(search_config=...)`; при `brutto_dict=None`
   используется дефолтный конфиг (поведение не меняется).
4. Неиспользуемый параметр `sign` в `assign_formulas` удаляется.

## Alternatives considered

| Alternative | Pros | Cons | Reason rejected |
|------------|------|------|-----------------|
| `"+"` → `[M]+` | поддержан в `_ion_shift` | радикал-катион редок для NOM; пользователи обычно подразумевают протонирование | менее вероятная научная интерпретация |
| Не чинить `sign` | нет риска | настройка остаётся фиктивной; вводит пользователя в заблуждение | противоречит цели GUI-аудита |
| Хранить маппинг в chemistry.json | единый источник | расширяет конфиг ради 2 пар; риск опечатки в JSON | маппинг фиксирован научным правилом, держим в коде с ADR |

## Consequences

### Positive

- Настройки GUI и CLI начинают реально влиять на результат.
- Устраняется мёртвый код (`sign` в `assign_formulas`,
  `noise_force_var`/`noise_int_var`).

### Negative

- Результаты для `sign="+"` и нестандартных диапазонов элементов изменятся
  по сравнению с прежним (игнорирующим) поведением — это ожидаемое
  исправление.

### Risks

- Пользователь, ранее запускавший `sign="+"` и получавший `[M-H]-`,
  увидит другие формулы. Митигация: поведение по умолчанию (`sign="-"`)
  не меняется; изменение задокументировано в отчёте.

## Validation and rollback

- Регрессионные тесты на синтетических m/z: `sign="+"` даёт иные формулы,
  чем `sign="-"`.
- Референсная эквивалентность: md5 результата set_01 при дефолтных
  параметрах должен остаться `33cde0049db29f91dfeab2c71d13b77e`.
- Rollback: `git revert` коммитов ветки `fix/gui-01-settings-wiring`
  (см. `rollback_plan.md`).

## Scientific/reproducibility impact

- Дефолтный режим (`[M-H]-`, диапазоны из `formula_search.json`)
  воспроизводим без изменений.
- Недефолтные режимы теперь честно применяют запрошенную ионизацию и
  диапазоны элементов.

## References

- `src/core/spectrum/_assign.py` — логика `ion_mode`/`search_config`.
- `src/core/spectrum/_generate.py` — `_ion_shift` и поддержка `[M+H]+`.
- `src/configs/chemistry.json` — `default_ion_mode`.
