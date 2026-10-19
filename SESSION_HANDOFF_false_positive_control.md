# Handoff: контроль ложных назначений в сериях дериватизации

Дата: 2026-10-19. Ветка: `feat/series-precision-and-derivative-subtraction`
(запушена; PR не создан — `gh` не авторизован, ссылка:
https://github.com/MikhaylenkoVS/NOM-HRMS-FGA/pull/new/feat/series-precision-and-derivative-subtraction).

## Текущие умолчания (`src/configs/pipeline.json`)

`denoise_derivatives=true`, `subtract_source=false`, `subtract_ppm=2.0`,
`ppm_tol=2.0`, `require_first_step=true`, `significance_level=0.95`,
`max_gaps=1`, `profile_check=false`, `formula_check=false`,
`drop_ambiguous=false`, `series_anchor="theoretical"`, `anchor_ppm=10.0`.

## Что реализовано (всё опционально)

| Модуль | Что делает |
|---|---|
| `src/core/spectrum/_decoy.py` | ансамбль decoy-сдвигов (`DECOY_SEED=42`), FDR по порогам, q-value |
| `src/core/spectrum/_conflicts.py` | конфликт = спорен только **последний** шаг серии; **правило цепочки**: если ровно один претендент имеет предыдущую ступень, пик его; сравнение только внутри одной производной |
| `src/core/spectrum/_formula_check.py` | химия продукта CD3/CD3CO: состав, DBE, `n ≤ O` |
| `src/core/spectrum/_validate.py` | `attach_fdr`, `attach_formula_check`, `attach_last_steps`, `trim_to_confirmed_last`, `add_status`, `summarize` |
| `src/core/io/raw_profile.py` | персистентность по 16 сканам, локальный S/N, FWHM, флаг `multi` (наложение) |
| `find_series` | опции `formula_check`, `drop_ambiguous`, `profile_check`, `significance_level`, `anchor_column` |
| `tools/diagnostics/ablation_f16.py` | ablation всех опций за один прогон (~10 мин) |
| `tools/diagnostics/grid_series_f16.py` | сетка денойз × вычитание × окно (~10 мин, 27 конфигураций) |

Тесты: `pytest -q tests/unit/test_validation_pipeline.py tests/unit/test_find_series.py -k "not pipeline_denoise"`
— 38+ зелёных. Lint: `python -m black -q src tools tests && python -m flake8 src tests tools`.

## Полученные результаты (F16, денойз 2.0, окно 2 ppm, без вычитания)

База: 32 195 назначено; CD3 **15 039** серий (ср. 4.195, значимых 5 248),
CD3CO **15 868** (4.211, 5 120). Decoy K=20: фон 5 883 / 7 094 (ср. 2.03 / 2.12).

| Проверка | CD3: n / ср. / значимых | CD3CO: n / ср. / значимых |
|---|---|---|
| формула | 12 385 / 3.92 / 3 629 | 12 038 / 3.53 / 2 395 |
| конфликты (правило последней ступени) | 5 275 / 3.96 / 1 507 | 4 263 / 3.29 / 781 |
| **FDR q≤0.05** | **6 218 / 6.61 / 4 787** | **5 022 / 7.27 / 4 693** |
| профиль (все шаги, до перехода на последнюю) | 4 762 / 2.54 / 519 | 3 931 / 1.99 / 64 |
| персистентность (min ≥ 0.5) | 309 / 2.44 / 28 | 265 / 2.18 / 3 |

Сетка: лучший вариант — денойз 2.0, **без вычитания**, окно 2 ppm (сигнал над
фоном 1.43; с профилем +0.36). Вычитание 2 ppm вредит (значимых 5 248 → 1 297).

Результаты на диске: `/d/Temp/User/ablation_f16{,_v2,_v3,_v4}.json`,
`grid_f16{,_profile}.json`, `subtract_f16.json`, `neg_control_f16.json`,
`defaults_f16.json`, `grid_f16_profile.json`. **`ablation_f16_v4.json` — новейший
(профиль только по последней ступени + правило цепочки), ещё не прочитан.**

## Что делать дальше (по порядку)

1. Прочитать `ablation_f16_v4.json`: строки `profile_last`, `trimmed`,
   `no_overlap`, `statuses`; сравнить с v3.
2. Проверка конфликтов: гистограмма `Δm0/Δ` по конфликтным парам
   (дериватизат-дериватизат; ожидаются пики на целых значениях — Δ-лестницы).
   Написать `tools/diagnostics/conflict_pairs_f16.py` (один прогон ~10 мин).
3. Агрегация профиля долей: `shape_frac ≥ 0.7`, `persistence_frac ≥ 0.5`,
   строго — только последняя ступень (сейчас `attach_last_steps`/`trim_to_confirmed_last`
   уже смотрят 2 последние ступени, но пороги одиночные).
4. Проброс опций в CLI/GUI (`--formula-check`, `--drop-ambiguous`, `--fdr`,
   `--profile`) — сейчас доступны на уровне API/ablation.
5. Прогон лучшей конфигурации на SRFA и F14.

## Ловушки (проверено на практике)

* Python запускать с `PYTHONIOENCODING=utf-8` — иначе `UnicodeEncodeError` на кириллице.
* Не использовать heredoc в bash-инструменте (ломает `\n`); писать скрипты файлом.
* Полный прогон F16 ≈ 9–10 мин, доминирует assign; не перезапускать на каждую
  опцию — использовать `ablation_f16.py` (все проверки как пост-обработка) и
  `grid_series_f16.py` (переиспользование assign и вариантов спектров).
* `data/real_sets/` (2.7 ГБ RAW) и `data/formula_db/chorsphal_*` (538 МБ) —
  в `.gitignore`; для прогонов файлы должны лежать на месте.
* `gh` не авторизован (HTTP 401) — PR только по ссылке или после `gh auth login`.
* Пайплайн требует все три спектра (src/dmet/dacet); режима «только исходник» пока нет.
* Дейтериевые метки: наложение производных с природными соединениями практически
  исключено (нужно 3n атомов D), поэтому конфликты — дериватизат-дериватизат.
