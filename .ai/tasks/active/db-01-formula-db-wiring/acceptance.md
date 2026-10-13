# DB-01 — критерии приёмки

## Функциональные

- [x] `open_formula_db()` находит и открывает базу (проект и `sys._MEIPASS`).
- [x] `db_candidates()` возвращает кандидатов CHNOSP в окне ±ppm.
- [x] Галогенный слой добавляет F/Cl/Br/I-формулы при `include_halogens=True`.
- [x] Гейт по M+2: слой включается при M+2/M ≥ 5 % или пустом CHNOSP-наборе.
- [x] Пайплайн открывает базу один раз и закрывает её; при отсутствии — откат на
      перебор без ошибок.
- [x] `isotope_variants` проброшен в `run_pipeline`, `run_pipeline_segmented`,
      GUI (галочка) и CLI (`--isotope-variants`).
- [x] Колонка `iso_variants` в отчёте содержит совпавшие варианты
      (`13C 0.077/0.076`).
- [x] Сателлиты помечаются (`iso_satellite_of`, `iso_satellite_label`) и
      исключаются из отчёта.
- [x] Изотопный фильтр и поиск вариантов включены по умолчанию.
- [x] Кнопка «Список изотопов…» открывает отдельное окно с таблицей
      элемент/изотоп/масса/распространённость (30 строк на 10 элементов).
- [x] Баг `mass_u` в строке формулы и в `SearchResult.counts` исправлен.
- [x] База и `zstandard` попадают в `.exe` (spec datas + hiddenimports).

## Нефункциональные

- [x] Скорость: set_01 (316 пиков) — ~11 с против ~66 с в v0.8.0.
- [x] Точность на эталонных тест-сетах не ухудшена (интеграционные тесты
      проходят).
- [x] Никаких изменений в `data/formula_db/*` (пересборка не требовалась).

## Проверочные команды

```bash
python -c "from src.core.spectrum._formula_source import open_formula_db; print(bool(open_formula_db()))"
python -m src.cli --input data/test_sets/set_01/original.csv \
  --dmet data/test_sets/set_01/deutermethylated.csv \
  --dacet data/test_sets/set_01/deuteroacylated.csv --sep , -o result.xlsx
pytest tests/ -q
```

## Открытые вопросы

* Галогенный слой по умолчанию — до одного атома (`db_halogen_atoms=1`).
  Больше атомов — параметром, но дороже по времени.
* Чистый фтор не даёт M+2-свидетельства: F-формулы находятся, только если
  CHNOSP-кандидатов в окне нет.
