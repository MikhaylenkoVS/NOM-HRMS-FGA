# Reference Validation — GUI-01

Сравнение результатов на `data/test_sets/set_01` до и после изменений.

## Baseline (до изменений)

- Команда: `python -m src.cli --input data/test_sets/set_01/original.csv --dmet data/test_sets/set_01/deutermethylated.csv --dacet data/test_sets/set_01/deuteroacylated.csv -o <out.csv>`
- md5: `33cde0049db29f91dfeab2c71d13b77e`

## После изменений

| Параметр | md5 / результат | Статус |
|----------|-----------------|--------|
| дефолт (`sign="-"`, без `--element-ranges`) | `33cde0049db29f91dfeab2c71d13b77e` (побайтовое совпадение) | PASS |
| `sign="+"` (через run_pipeline) | таблица 52 строки против 78 у `"-"` | PASS (настройка влияет) |
| `brutto_dict={"C":(1,3),...}` (через run_pipeline) | таблица 2 строки против 78; все формулы C≤3 | PASS (настройка влияет) |
| `brutto_dict={"C":(40,60),...}` (через run_pipeline) | таблица 47 строк | PASS (настройка влияет) |

## Вывод

Дефолтный научный результат не изменился (md5 совпал). Недефолтные
настройки теперь честно влияют на результат.
