# Design — PACKAGING-01: работоспособность установки (wheel/sdist) и сборки .exe

## Контекст (факты аудита)

Задача возникла из фактологического аудита `main` @ `30194d6` (см. отчёт
`NOM-HRMS-FGA_factual_report.md`, проблемы **S-20**, **K-21**, **L-03**, **L-04**, **L-07**).

Ключевое измерение: `python -m pip wheel . --no-deps --no-build-isolation` даёт
`nom_hrms_fga-0.7.0-py3-none-any.whl`, в котором присутствуют только
`src/configs/{__init__.py, chemistry.json, paths.json, pipeline.json, loader.py,
presets_loader.py}` и пустой пакет `src/configs/presets/__init__.py`.

* `src/configs/constants/` — **отсутствует полностью**;
* `src/configs/presets/*.json` — **отсутствуют**.

`src/configs/loader.py:130–135` выполняет загрузку на уровне модуля:

```python
NOISE_CFG = load_config("noise")
ISOTOPE_CFG = load_config("isotope")
```

поэтому после `pip install` вызов `import src.configs` завершается `ConfigError`
(файл `constants/noise.json` не найден). Тот же дефект воспроизводится в
PyInstaller-сборке: `tools/NOM_HRMS_FGA.spec:58–67` добавляет в `datas` только
`src/configs/*.json` и `src/configs/presets/*.json`.

Причина: `[tool.setuptools.package-data]` объявляет `src = ["configs/*.json"]`
(`pyproject.toml:59–60`). Шаблон `configs/*.json` не покрывает подкаталоги.

## Решение

### 1. `pyproject.toml`, секция `[tool.setuptools.package-data]`

```toml
[tool.setuptools.package-data]
src = [
    "configs/*.json",
    "configs/constants/*.json",
    "configs/presets/*.json",
]
```

Почему так, а не `include-package-data`/`MANIFEST.in`-only: `package-data`
детерминированно управляет составом колеса; `MANIFEST.in` дополняет его для
sdist (см. п. 2). Записи разнесены по строкам, чтобы будущие подкаталоги
добавлялись одной строкой.

Дополнительно: `src/configs/constants/` не является пакетом (нет
`__init__.py`), поэтому он не подхватывается механизмом packages — данные
попадают в колесо исключительно через `package-data`. Это осознанно:
`__init__.py` в каталоге данных не нужен.

### 2. `MANIFEST.in` (новый файл)

```
include LICENSE
include README.md
include THIRD_PARTY_NOTICES.md
recursive-include src/configs *.json
recursive-include thermo *.dll      # не включается: проприетарные — см. ниже
```

Итоговое содержимое — без `thermo/`: сырые DLL Thermo RawFileReader
не распространяются (THIRD_PARTY_NOTICES), поэтому в sdist они не попадают.

### 3. `tools/NOM_HRMS_FGA.spec`

* в блок «Data files: config JSONs» добавить подкаталог `constants/`;
* из `_excludes` удалить `"openpyxl"`.

`openpyxl` используется `src/core/pipeline/_export.py` (XLSX) и
`src/core/spectrum/_load.py` (`.xlsx`), то есть его исключение ломает
заявленную функциональность экспорта/импорта.

### 4. Лицензионные упоминания

* `pyproject.toml`: classifier `License :: OSI Approved :: GPL-3.0 License`
  → `License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)`
  (согласовано с `license = {text = "MPL-2.0"}` и файлом `LICENSE`);
* `README.md:34` — «открыт (GPL-3.0)» → MPL-2.0;
* `README.md:239` — «Основной код — **GPL-3.0**» → MPL-2.0; упоминание
  `external/README.txt` исправляется на фактическое имя `external/README.md`;
* строка `README.md:224` («Стороннее ПО (GPL-3.0)») **не меняется** — она
  корректна для каталога `external/`.

### 5. `requirements.txt`

`zstandard>=0.22` переносится из блока «Опциональные зависимости» в основные
(он импортируется `src/core/formula_db/_packed.py`, а не только в редком
сценарии). `pymzml>=2.6.1` остаётся в опциональном блоке с корректным
комментарием (mzML-мост).

### 6. `THIRD_PARTY_NOTICES.md`

Удаляется строка таблицы `| scipy | BSD-3-Clause |` — `scipy` отсутствует в
`pyproject.toml`/`requirements.txt` и не импортируется в коде (единственное
упоминание — мёртвая запись `collect_all("scipy")` в spec, которая будет
удалена вместе с проверкой упаковки, если не нужна: **оставляем**, так как
изменение списка `_collect_packages` влияет на состав сборки и не относится к
данной задаче; фиксируется как отдельная задача).

## Границы задачи

* `src/`, `tests/`, `data/`, `docs/`, `.github/` — **не изменяются**;
* научные константы не затрагиваются;
* версия пакета (`0.7.0`) не меняется;
* новые зависимости не добавляются.

## Риски

| Риск | Оценка | Митигация |
|---|---|---|
| Расширение колеса меняет состав дистрибутива | низкий | проверка содержимого колеса до/после |
| Ошибка в синтаксисе `package-data` | низкий | сборка колеса как обязательная проверка |
| Правка README нарушает форматирование | низкий | `black`/`flake8` не покрывают md; проверка глазами + CI `check-repo` |
| Полная сборка `.exe` не выполняется (долго) | средний | верифицируется список `datas` из spec + отдельная задача по smoke-сборке |

## Проверка результата

1. `python -m pip wheel . --no-deps --no-build-isolation -w /tmp/wh` → в архиве
   присутствуют `src/configs/constants/{noise,isotope,spectrum_load,formula_search}.json`
   и `src/configs/presets/*.json`.
2. Распаковка колеса в чистый каталог → `python -c "import src.configs"` без
   ошибок (с `sys.path`, указывающим на распакованный каталог вперёд
   editable-установки).
3. `python -m build --sdist` либо `python setup.py sdist`/`pip wheel` и проверка
   состава sdist по `MANIFEST.in`.
4. Побайтовое сравнение результата конвейера на `set_01` с базовой линией
   (md5 `33cde0049db29f91dfeab2c71d13b77e`).
5. `pytest tests/ -q` — 422 passed, 1 skipped, 1 xfailed.
