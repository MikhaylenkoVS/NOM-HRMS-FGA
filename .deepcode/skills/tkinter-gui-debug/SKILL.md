---
name: tkinter-gui-debug
description: >
  Диагностика, доработка и отладка GUI-приложения на tkinter: `src/app.py`
  (82K), `src/ui/`, `src/structures/`, debug-режим через logging, test-mode
  в GUI, сборка .exe через PyInstaller (tools/build_exe.py,
  tools/NOM_HRMS_FGA.spec). Активировать когда пользователь говорит «GUI»,
  «интерфейс», «окно», «tkinter», «app.py», «вкладка», «кнопка», «отладка»,
  «debug», «test-mode», «exe», «PyInstaller», «сборка», «launcher»,
  «StructureViewer», «embed_figure»; либо при редактировании app.py, ui/,
  structures/, tools/build_exe.py.
---

# Tkinter GUI Debug — диагностика и доработка интерфейса

Скилл для работы с графическим интерфейсом NOM-HRMS-FGA. Приложение на tkinter,
многовкладочное, со встроенными графиками matplotlib. Текущее состояние: app.py
— монолит, подлежит декомпозиции в отдельных скриптах (вкладки → модули).

## Архитектура GUI

```
src/
├── app.py            # Главное приложение: окна, вкладки, логика запуска (82K)
├── ui/
│   ├── theme.py      # Тема: цвета (BG, FG, ACCENT, PANEL, WARN, OK), шрифты, стили ttk
│   └── plots.py      # embed_figure(): встраивание matplotlib Figure в tkinter
├── structures/
│   ├── tab.py        # StructureViewerTab — вкладка просмотра молекул (RDKit)
│   ├── widgets.py    # Виджеты: карточки молекул, диалоги
│   └── rdkit_utils.py  # Утилиты RDKit: рендеринг, экспорт
└── configs/
    └── presets_loader.py  # Загрузка пресетов (soil, water, peat, coal)
```

### Точка входа

```python
# pyproject.toml:
# [project.scripts]
# nom-hrms-fga = "src.app:main"
#
# tools/launcher.py — crash-safe лаунчер для .exe
```

### Вкладки GUI (определены в app.py)

| Вкладка | Назначение | Ключевые виджеты |
|---------|-----------|-----------------|
| Параметры | Загрузка CSV/RAW, настройка параметров | file dialogs, presets dropdown |
| Спектры | Отображение трёх спектров (original, dmet, dacet) | matplotlib Figure через embed_figure |
| Ван-Кревелен | Диаграмма Ван-Кревелена | matplotlib |
| Серии | Визуализация гомологических серий —COOH/—OH | matplotlib |
| Результаты | Итоговая таблица, экспорт | ttk.Treeview / scrolledtext |
| Структуры | 3D/2D молекулы-кандидаты | StructureViewerTab |

## Debug-режимы

### Текущее состояние (v0.4.2)

Единственный debug-механизм — **logging**:

```python
# src/core/pipeline.py:
def _debug(msg: str) -> None:
    logger.debug(msg)
```

Сообщения выводятся только при `logging.basicConfig(level=logging.DEBUG)`.

**Чего нет (запланировано на дальнюю перспективу):**
- Специального debug-окна в GUI.
- Сохранения промежуточных спектров (после денойзинга, после assign).
- Пошагового режима прохода по пикам.
- Визуализации кандидатов для конкретного пика.

### test_mode в GUI (v1)

```python
# pipeline.json -> test_mode: параметры для тестового прогона
# Запуск из GUI: кнопка/галочка "Тестовый режим" → run_pipeline(test_mode=True)
```

**Надо реализовать:**
- Флажок «Тестовый режим» на вкладке Параметры.
- Автоматическая подстановка путей к `data/test_sets/set_01`.
- Вывод TestSetResult (denoise_recall, assign_recall, wrong_ratio) в GUI.
- Возможность выбора конкретного набора (set_01..set_05).

## Обработка ошибок в GUI

### Fallback-цепочка в app.py

1. Импорт `src.ui` → при ошибке: fallback-константы (BG, FG, ACCENT…),
   `embed_figure()` заменяется минимальной реализацией через
   `FigureCanvasTkAgg`.
2. Импорт `StructureViewerTab` → при ошибке (нет RDKit): `StructureViewerTab = None`,
   вкладка Структуры скрывается.
3. Импорт pipeline → при ошибке: сообщение пользователю, GUI остаётся
   функциональным для загрузки CSV.

### Crash-safe лаунчер (tools/launcher.py)

Используется в собранном .exe. Перехватывает исключения и показывает их
в messagebox перед падением.

## Сборка .exe (PyInstaller)

```bash
python tools/build_exe.py           # Сборка (~120 MB)
python tools/build_exe.py --clean   # Очистка build/ + сборка
python tools/build_exe.py --test    # Сборка + smoke-тест
```

Конфигурация: `tools/NOM_HRMS_FGA.spec`. CI: `.github/workflows/release_exe.yml`.

### Что проверять при сборке:

- [ ] `import tkinter` работает (python3-tk на Linux).
- [ ] `matplotlib` бекенд — TkAgg.
- [ ] RDKit импортируется (CoordGen включён).
- [ ] `python-io` хук для Pillow (изображения в Structures).
- [ ] Размер .exe ≤ 150 MB.
- [ ] SmartScreen на Windows — пользователь предупреждён в README.

## Алгоритм доработки GUI

### 1. Диагностика проблемы

- Определи, на каком уровне ошибка: импорт → GUI → pipeline → визуализация.
- Если GUI не запускается — проверь fallback-цепочку: `python -c "from src.ui.theme import BG; print(BG)"`.
- Если вкладка пустая — проверь `embed_figure()`: создаётся ли Figure, привязан ли canvas.

### 2. Декомпозиция app.py (средняя перспектива)

Текущий монолит (82K) предлагается разделить на:
- `src/ui/tabs/parameters.py` — вкладка Параметры.
- `src/ui/tabs/spectra.py` — вкладка Спектры.
- `src/ui/tabs/van_krevelen.py` — вкладка Ван-Кревелен.
- `src/ui/tabs/series.py` — вкладка Серии.
- `src/ui/tabs/results.py` — вкладка Результаты.
- `src/ui/main_window.py` — главное окно, оркестрация вкладок.
- `src/app.py` — остаётся точкой входа.

При рефакторинге: **сохранить обратную совместимость сигнатур**, не ломать
fallback-цепочку.

### 3. Добавление test_mode в GUI

- Добавить `tk.BooleanVar` в app.py.
- Передать как `test_mode=self.test_mode_var.get()` в `run_pipeline()`.
- Вывести результат в scrolledtext на вкладке Результаты.

### 4. Проверка после изменений

```bash
# Запуск GUI (интерактивный — вручную)
python -m src

# Smoke-тест GUI (без запуска окна):
pytest tests/integration/test_app_smoke.py -v

# Проверка импортов:
python -c "from src.ui.theme import _style; from src.structures.tab import StructureViewerTab; print('OK')"
```

### Проверочный список:

- [ ] Fallback-цепочка не сломана (импорт ui/structures опционален).
- [ ] Новые виджеты используют тему из `src/ui/theme.py`, не хардкод цветов.
- [ ] `embed_figure()` вызывается с `toolbar=True` для графиков.
- [ ] Длинные операции (pipeline) запускаются в `threading.Thread`, не блокируют GUI.
- [ ] Для вывода результатов используется `queue.Queue` (потокобезопасно).
- [ ] Сборка .exe протестирована (`python tools/build_exe.py --test`).
- [ ] `test_mode` в GUI задокументирован для пользователя (подсказка/tooltip).

## Типичные ошибки

1. **GUI зависает:** pipeline.run() в главном потоке. → вынести в threading.Thread.
2. **TclError при обновлении из потока:** `tkinter` не потокобезопасен. →
   использовать `queue.Queue` + `root.after()`.
3. **Цвета не из темы:** хардкод `bg="white"` вместо `BG` из theme.py.
4. **Размер Figure не задан:** график обрезается → `fig.set_size_inches(IMG_W/100, IMG_H/100)`.
5. **RDKit не найден в .exe:** не включён в hidden-imports в .spec → добавить.

## Связанные скиллы

- `code-review-reliability-first` — общий ревью (thread safety, error handling).
- `config-safety-audit` — аудит параметров test_mode в pipeline.json.
- `deepcode-github-mcp-pr` — PR для изменений GUI.
