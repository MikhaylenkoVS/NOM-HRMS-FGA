# ELEM-01 — отчёт о реализации

## Что сделано

| Файл | Изменение |
|---|---|
| `src/configs/chemistry.json` | добавлены моноизотопные массы F, Cl, Br, I; `atomic_mass_elements` = 10 элементов |
| `src/configs/constants/formula_search.json` | `elements` = C, H, O, N, S, P, F, Cl, Br, I; диапазоны (S,P 0–5; F,Cl 0–5; Br,I 0–3); лимиты S/C, P/C, X/C; штрафы и бонус |
| `src/configs/constants/isotope.json` | таблица изотопов (масса + распространённость) на 10 элементов; `pattern_max_shift`, `variant_min_probability`, `m2_tolerance` |
| `src/core/spectrum/_isotopes.py` | **новый модуль**: `pattern`, `m1_ratio`, `m2_ratio`, `variants`, `measure_pattern`, `find_isotope_variants`, `isotope_variant_masses` |
| `src/core/spectrum/_constants.py` | `HALOGENS`, `ELEMENT_VALENCES`, обобщённый `FormulaSearchConfig` (лимиты отношений, штрафы), `_fs_get` |
| `src/core/spectrum/_generate.py` | переписан: общий набор элементов, DFS с отсечением по массе, DBE/чётность/лимиты, параметр `slack`, `ranges_key`/`limits_key` |
| `src/core/spectrum/_assign.py` | переписан: генерация под каждый пик (±ppm, кэш по сетке 0.001 Да), векторный скоринг, **исправлен DBE** (был O вместо N), изотопные штрафы M+1/M+2 и бонус за M+2, колонка `iso_variants` |
| `src/core/spectrum/_chem.py` | `_counts_to_str(*counts, element_order=…)` — элемент-агностично; `FORMULA_ELEMENT_ORDER` |
| `src/app.py`, `src/ui/_params.py` | диапазоны элементов строятся из конфига (`self.el_vars`), валидация по всем элементам |
| `tests/unit/test_generate_cache.py` | тесты под новый API + проверка химических правил |
| `.ai/decisions/0004-elements-and-isotopes.md` | ADR |

## Замеры

### Изотопная арифметика (модуль `_isotopes`)

| Формула | Теоретически (модуль) | Ожидание |
|---|---|---|
| C7H6O2 | M+1 = 7.72 % | ≈7.5–7.9 % |
| CHCl3 | M+2 = 95.99 % | ≈96 % (3 : 1) |
| CHBr | M+2 = 97.28 % | ≈97 % |
| C10H8S2 | M+2 = 9.66 % | ≈9.7 % |
| C6H12O6 | M+1 = 6.86 % | ≈6.9 % |

### Время перебора (окно ±5 ppm, `slack=0`)

| Набор/лимиты | m/z 400 | m/z 600 | m/z 800 |
|---|---|---|---|
| X/C 0.5, S/C 0.5, P/C 0.5 | 434 канд. / 70 мс | 4 737 / 782 мс | 21 114 / **3.87 с** |
| X/C 0.1, S/C 0.2, P/C 0.1 | 57 / 10 мс | 574 / 87 мс | 2 437 / 452 мс |
| X/C 0.05, S/C 0.1, P/C 0.05 | 13 / 2.6 мс | 102 / 22 мс | 213 / 85 мс |

Отсюда — умеренные дефолты (X/C 0.1, S/C 0.2, P/C 0.1) с пояснением в конфиге.
Широкие диапазоны требуют этапа 4 (поиск по сжатой базе формул).

### End-to-end (CLI, set_01)

```
Назначено формул: 226 из 316 пиков
Соединений с сериями CD3: 32; CD3CO: 11
Строк в таблице: 226
```
Время прогона ≈ 66 с (до изменения ≈ 2 с) — цена перебора в Python.

### Точность

Интеграционный тест
`tests/integration/test_pipeline_integration.py::test_pipeline_denoise_assign_find_series_on_existing_sets[set_01]`
— **passes**. Промежуточная версия скоринга давала 77.4 % совпадений с эталонными
формулами (галогенные формулы перебивали CHNO); после введения штрафов по атомам
и бонуса за M+2 тест снова проходит.

## Известные ограничения

1. Скорость: перебор на пик в Python; для спектров с ~20 000 пиков нужен этап 4.
2. Широкие лимиты X/C, S/C, P/C не годятся для перебора (см. таблицу).
3. `iso_variants` заполняется только при `isotope_variants=True` (по умолчанию
   выключено, чтобы не замедлять массовые прогоны).

## Follow-up

* Этап 4: сжатая база с галогенами (формат uint64) + подключение базы к
  назначению; после этого можно поднять лимиты до широких.
* GUI: вынести `penalty_*`/`bonus_isotope_m2` в редактируемые параметры (сейчас
  из конфига).
