# Reference Validation — CHROM-01

## Метод

Сравнение `run_pipeline_segmented` (CSV-входы, один сегмент) с обычным
`run_pipeline` на `data/test_sets/set_01`. Оба прогона с параметрами
`load_mass_min=100`, `load_mass_max=1000`, `rel_error=0.5`,
`noise_force=2.0`, `ppm_tol=0.5`, `sign="-"`.

## Результаты

| Проверка | Результат | Статус |
|----------|-----------|--------|
| общие колонки mass/brutto/N_COOH/N_OH | идентичны (`DataFrame.equals` → True) | PASS |
| число строк | 78 = 78 | PASS |
| `rt_start`/`rt_end` для CSV | все `None` (один сегмент без RT) | PASS |
| CLI `--segment-width 2` на CSV | exit 0; таблица с колонками `rt_start`/`rt_end` | PASS |

## Вывод

Сегментный режим на данных без RT (CSV) воспроизводит обычный пайплайн —
научный результат не изменился; RT-колонки добавлены корректно.
