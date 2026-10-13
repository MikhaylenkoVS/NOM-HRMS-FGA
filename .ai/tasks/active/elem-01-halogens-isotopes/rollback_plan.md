# ELEM-01 — план отката

## Уровень 1: отключить новые элементы (без отката кода)

Правка `src/configs/constants/formula_search.json`:

```json
"elements": ["C", "H", "O", "N"],
"ranges": {"C": [1, 50], "H": [4, 100], "O": [0, 20], "N": [0, 8]}
```

Генератор и назначение читают конфиг, поэтому этого достаточно, чтобы вернуться
к CHNO-поведению. Далее перезапустить анализ.

## Уровень 2: вернуть мягкие изотопные проверки

В `src/configs/constants/formula_search.json`:

```json
"penalty_s": 0.0,
"penalty_p": 0.0,
"penalty_halogen": 0.0,
"bonus_isotope_m2": 0.0
```

Это уберёт влияние изотопного паттерна на ранжирование (оставит только
диагностику в `iso_variants`).

## Уровень 3: полный откат коммита

```bash
git revert --no-edit <commit_sha>
```

или возврат файлов из тега предыдущего релиза:

```bash
git checkout v0.7.0 -- \
  src/core/spectrum/_assign.py \
  src/core/spectrum/_generate.py \
  src/core/spectrum/_constants.py \
  src/core/spectrum/_chem.py \
  src/configs/chemistry.json \
  src/configs/constants/formula_search.json \
  src/configs/constants/isotope.json \
  src/app.py src/ui/_params.py
rm src/core/spectrum/_isotopes.py
```

## Пост-откат

* `pytest tests/ -q` — убедиться, что набор зелёный.
* `python -m src.cli --input data/test_sets/set_01/original.csv ...` — проверить
  эталонные числа set_01.
* Пересобрать exe (`python -m PyInstaller tools/NOM_HRMS_FGA.spec --noconfirm`).

## Данные

Изменения не касаются `data/` и `data/formula_db/` — откат данных не требуется.
