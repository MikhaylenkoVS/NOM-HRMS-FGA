# DB-01 — отчёт о реализации

## Что сделано

| Файл | Изменение |
|---|---|
| `src/core/spectrum/_formula_source.py` | **новый**: `open_formula_db`, `db_candidates`, `halogen_combos`, `_passes_filters`, `find_manifest` |
| `src/core/spectrum/_assign.py` | источник кандидатов (база/перебор), кэш окон с учётом галогенов, гейт по M+2, проброс `isotope_variants`, атрибуция сателлитов, допуск `variant_ppm_tol` |
| `src/core/spectrum/_isotopes.py` | (без изменений API) используется для вариантов и паттерна |
| `src/core/spectrum/_build.py` | колонки `iso_variants`, `iso_satellite_of`, `iso_satellite_label`; исключение сателлитов из отчёта |
| `src/core/formula_db/_packed.py` | исправлен `formula_to_string` (игнор служебных ключей) |
| `src/core/formula_db/_reader.py` | `SearchResult.counts` без `mass_u` |
| `src/core/pipeline/_run.py` | `isotope_filter=True`, `isotope_variants=True`, `use_formula_db=True`; открытие/закрытие базы; проброс в `assign_formulas` |
| `src/core/pipeline/_segments.py` | то же для сегментного режима |
| `src/configs/constants/isotope.json` | `variant_ppm_tol`, `satellite_tolerance`, `halogen_m2_evidence` |
| `src/ui/_params.py`, `src/app.py` | галочка «Искать изотопные варианты», кнопка «Список изотопов…» + окно с таблицей, изотопные проверки включены по умолчанию |
| `src/cli.py` | флаг `--isotope-variants` |
| `tools/NOM_HRMS_FGA.spec` | data-файлы `data/formula_db/*`, hidden-импорты `src.core.formula_db._reader/_packed`, `zstandard` |
| `.github/workflows/*.yml` | установка `zstandard` при сборке exe |

## Замеры

### Скорость (set_01, 316 пиков после шумоподавления, полный CLI)

| Вариант | Время | Назначено формул |
|---|---|---|
| v0.8.0 (перебор) | ~66 с | 226 |
| База + галогенный слой всегда | ~31 с | 204 |
| База + гейт по M+2 (принято) | **~11 с** | 204 |

### База: скорость читателя

| Запрос | Время |
|---|---|
| `search(300 Да, 5 ppm)` | 5.5 мс |
| `search(500 Да, 5 ppm)` | 28.6 мс |
| `search(800 Да, 5 ppm)` | 184 мс |
| 100 случайных пиков 200–800 Да | 11.9 мс/пик |

### Изотопы (проверка на синтетике)

* C7H6O2 + сателлит 13C: вариант найден, измер. 0.0772 против теор. 0.0757
  (`ok=True`), пик-сателлит помечен `13C` с родителем 121.0295.
* C6H5Cl2O: 37Cl — теор. 0.6399 / измер. 0.6438, 13C — 0.0649 / 0.0659.

### Тест-сеты

Синтетические тест-сеты не содержат изотопных сателлитов (ближайший пик к M+1
на 50–1000 мДа), поэтому `iso_variants` и `iso_satellite_of` там пусты — это
ожидаемое поведение, а не ошибка. Функциональность подтверждена на синтетике и
на реальных данных (где паттерн присутствует).

## Известные ограничения

1. Галогенный слой — до одного атома по умолчанию; больше через
   `db_halogen_atoms` (дороже).
2. Фтор не даёт M+2-свидетельства → находится только при отсутствии
   CHNOSP-вариантов.
3. Сателлиты исключаются из отчёта целиком (без отдельной колонки-«сироты»):
   если нужно сохранять — `build_result_table(drop_isotope_satellites=False)`.
4. База добавляет ~39 МБ к размеру exe.
