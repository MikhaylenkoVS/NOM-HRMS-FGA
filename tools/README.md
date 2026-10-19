# tools/ — сборка и вспомогательные утилиты

## Назначение

Сборка автономного `.exe` (Windows) через PyInstaller.

## Состав

| Файл | Назначение |
|------|------------|
| `build_exe.py` | Сценарий сборки `NOM_HRMS_FGA.exe`: установка зависимостей, PyInstaller, smoke-тест |
| `launcher.py` | Crash-safe точка входа для `.exe`: перехват ошибок, диалог диагностики |
| `NOM_HRMS_FGA.spec` | Конфигурация PyInstaller: onefile, windowed, collect_all для rdkit/matplotlib/scipy |

## Использование

```bash
python tools/build_exe.py          # сборка
python tools/build_exe.py --clean  # очистка + сборка
python tools/build_exe.py --test   # сборка + smoke-тест
```

Результат: `dist/NOM_HRMS_FGA.exe` (~120 МБ, автономный).

## Связь с общим конвейером

`launcher.py` импортирует `src.app.main()` — это единственная точка входа для
PyInstaller-сборки. Сам конвейер и GUI находятся в `src/`.

## Правила размещения вспомогательного кода

Чтобы не проводить чистку повторно, новый код кладём сразу по назначению:

| Что за код | Куда | Почему |
|---|---|---|
| Готовит материалы для статьи: рисунки, графики, таблицы (XLSX), таблицы-картинки | `tools/article_report.py` | Одна точка сборки всего, что попадает в статью. Отчёты — только изображения и таблицы, без текстовых файлов |
| Может понадобиться другому разработчику: проверки, замеры, бенчмарки, оценка размеров, сборка БД | `tools/diagnostics/` (см. `tools/diagnostics/README.md`) | Воспроизводимые проверки и измерения, запускаются из корня проекта |
| Одноразовый скрипт, эксперимент, «посмотреть цифры» | `tools/_scratch/` (папка в `.gitignore`) | Не переносится другим разработчикам и не попадает в репозиторий |
| Сборка, запуск, инфраструктура | `tools/` (как есть: `launcher.py`, `build_exe.py`, `ai_workflow.py`, `NOM_HRMS_FGA.spec`) | Нужно для сборки и сопровождения |
| Часть приложения (GUI, пайплайн, ядро) | `src/` | Работает в пользовательской версии и проверяется тестами |

Правило проверки: если код не вызывается из `src/` и не нужен для сборки, он не должен
лежать в `src/`. Аудит таких модулей — `python tools/diagnostics/audit_unused_code.py`.

## Материалы для статьи

```bash
python -m tools.article_report --result result.xlsx --outdir reports/article     --original orig.csv --dmet cd3.csv --dacet cd3co.csv
```

В GUI то же самое — кнопка «🖼 Материалы для статьи» в панели результатов.
Результат: `fig_01_spectra.png`, `fig_02_van_krevelen.png`, `fig_03_histograms.png`,
`fig_04_groups.png`, `fig_05_isotope_status.png`, `fig_06_technical.png`
(таблица технических характеристик картинкой), а также `table_01_results.xlsx`,
`table_02_technical.xlsx`, `table_03_groups.xlsx`.
