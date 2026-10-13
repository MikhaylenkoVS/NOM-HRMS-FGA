# DB-01 — план отката

## Уровень 1: вернуться к перебору (без откатов кода)

```python
from src.core import run_pipeline
run_pipeline(..., use_formula_db=False)      # кандидаты снова перебором
```

или убрать базу из сборки (spec: `data/formula_db` datas) — при отсутствии файла
`open_formula_db()` вернёт `None`, и назначение автоматически уйдёт на перебор.

## Уровень 2: отключить изотопные проверки

```python
run_pipeline(..., isotope_filter=False, isotope_variants=False)
```

или в GUI снять галочки «Изотопный фильтр» и «Искать изотопные варианты».

## Уровень 3: полный откат коммита

```bash
git revert --no-edit <commit_sha>
```

или вернуть файлы из тега v0.8.0:

```bash
git checkout v0.8.0 -- \
  src/core/spectrum/_assign.py \
  src/core/spectrum/_build.py \
  src/core/pipeline/_run.py \
  src/core/pipeline/_segments.py \
  src/core/formula_db/_reader.py \
  src/core/formula_db/_packed.py \
  src/configs/constants/isotope.json \
  src/ui/_params.py src/app.py src/cli.py tools/NOM_HRMS_FGA.spec
rm src/core/spectrum/_formula_source.py
```

## Пост-откат

* `pytest tests/integration -q` — эталонные тесты зелёные.
* `python -m src.cli --input data/test_sets/set_01/original.csv ...` — сверить
  число назначенных формул (ожидается 226 при полном переборе).
* Пересобрать exe: `python -m PyInstaller tools/NOM_HRMS_FGA.spec --noconfirm`.

## Данные

`data/formula_db/*` не изменялись (правки только в читателе). Пересборка базы
для откатa не требуется.
