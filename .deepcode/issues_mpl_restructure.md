# GitHub Issues — MPL-2.0 + RawFileReader реструктуризация

Каждый блок = один issue. Копировать в GitHub Issues репозитория `MikhaylenkoVS/NOM-HRMS-FGA`.

---

## Issue 1: Удалить зависимость raw_bridge.py от external GPL-обёртки

**Заголовок:** `refactor: отвязать raw_bridge.py от external/pymsfilereader.py (GPL)`

**Метки:** `refactor`, `licensing`, `blocked`

**Описание:**

`src/core/raw_bridge.py` сейчас импортирует GPL-обёртку `external/usrednenie_spectrov_i_hromatogramm/src/pymsfilereader.py` через `sys.path.insert`. Это создаёт GPL combined work при любом использовании RAW.

**Что сделать:**
- Удалить `import pymsfilereader` и `sys.path.insert` из `raw_bridge.py`
- Удалить всё, что ссылается на `_msfr` в коде модуля
- Перевести `is_available()` и `availability_error()` на проверку наличия RawFileReader DLL вместо MSFileReader
- Убедиться, что модуль НЕ импортирует ничего из `external/`

**Критерий приёмки:**
- `raw_bridge.py` не содержит `pymsfilereader`, `_msfr`, `sys.path.insert`
- `pip install comtypes` больше не требуется для работы raw-функций
- Тесты обновлены

---

## Issue 2: Исключить external GPL-репозиторий из production-сборки

**Заголовок:** `build: исключить external/ из .exe и production-сборок`

**Метки:** `build`, `licensing`

**Описание:**

`external/usrednenie_spectrov_i_hromatogramm/` — GPL-3.0 код, который больше не используется в production. Его нужно:
- Исключить из PyInstaller `.spec` (убрать строки, добавленные для бандлинга external)
- Добавить в `.gitignore` для dist/ (если ещё нет)
- Опционально: переместить в `external/_legacy_reference/` с README, поясняющим, что это историческая справка, не часть продукта

**Не удалять из репозитория полностью** — оставить как reference для разработки.

**Критерий приёмки:**
- `NOM_HRMS_FGA.spec` не содержит упоминаний `external/usrednenie_spectrov_i_hromatogramm`
- Собранный `.exe` не содержит `pymsfilereader.py` в бандле
- Папка `external/` документирована как legacy

---

## Issue 3: Написать raw_thermo_adapter.py (RawFileReader bridge)

**Заголовок:** `feat: raw_thermo_adapter.py — чтение .raw через RawFileReader (.NET DLL)`

**Метки:** `feat`, `raw`, `core`

**Описание:**

Новый модуль `src/core/raw_thermo_adapter.py`, который:
- Использует `pythonnet` (CLR bridge) для вызова RawFileReader .NET DLL
- Предоставляет тот же API, что и старый raw_bridge:
  - `average_raw_to_csv(raw_path, rt_min, rt_max, output_csv, progress_callback) -> str`
  - `average_raw_to_df(raw_path, rt_min, rt_max) -> pd.DataFrame`
  - `is_available() -> bool`
  - `availability_error() -> str | None`
- Читает: m/z, intensity, retention time, scan number, resolution, baseline, noise, charge (все 6+ полей)
- Экспорт: CSV с колонками `mass,intensity` (совместимость с `load_spectrum()`)

**DLL-зависимости (4 файла):**
- `ThermoFisher.CommonCore.Data.dll`
- `ThermoFisher.CommonCore.RawFileReader.dll`
- `ThermoFisher.CommonCore.MassPrecisionEstimator.dll`
- `ThermoFisher.CommonCore.BackgroundSubtraction.dll`

**Технические заметки:**
- `pythonnet` должен быть в зависимостях (pyproject.toml, requirements.txt)
- RawFileReader DLL должны лежать в известной директории (рядом с .exe или в `thermo/`)
- Путь к DLL определяется: `sys._MEIPASS` если frozen, иначе `os.path.dirname(__file__)/../../thermo/`
- .NET Framework уже есть в Windows 10/11, дополнительный рантайм не требуется

**Критерий приёмки:**
- `raw_thermo_adapter.py` открывает `.raw` и возвращает CSV/DataFrame
- CLI-тест: `python -c "from src.core.raw_thermo_adapter import average_raw_to_csv; average_raw_to_csv('test.raw', 0, 10)"`
- Старый `raw_bridge.py` удалён или заменён тонкой обёрткой над raw_thermo_adapter

---

## Issue 4: Перелицензировать проект GPL-3.0 → MPL-2.0

**Заголовок:** `chore: перелицензировать проект GPL-3.0 → MPL-2.0`

**Метки:** `chore`, `licensing`

**Описание:**

**Что сделать:**
- `pyproject.toml`: `license = {text = "MPL-2.0"}`
- `LICENSE` → заменить текст на полный текст MPL-2.0
- `CITATION.cff`: обновить поле license
- Добавить SPDX-заголовки в ключевые `.py`-файлы: `# SPDX-License-Identifier: MPL-2.0`
- Обновить `README.md`: badges, раздел License

**Проверить:**
- Все permissive-зависимости (numpy BSD, pandas BSD, matplotlib PSF, rdkit BSD, Pillow MIT) совместимы с MPL-2.0
- В проекте не осталось файлов под GPL (кроме legacy-референсов, исключённых из сборки)

**Критерий приёмки:**
- `pyproject.toml` показывает `MPL-2.0`
- `LICENSE` содержит текст MPL-2.0
- `README.md` отражает новую лицензию

---

## Issue 5: Лицензионная инфраструктура для RawFileReader (ThermoFisher)

**Заголовок:** `docs: RawFileReader license compliance — THIRD_PARTY_NOTICES, About, EULA`

**Метки:** `docs`, `licensing`

**Описание:**

Требования лицензии ThermoFisher к редистрибуции RawFileReader DLL:

**A. Файл `THIRD_PARTY_NOTICES.md` (или `RawFileReaderLicense.md`):**
- Перечислить 4 DLL файла
- Указать копирайт: `Copyright © 2016 by Thermo Fisher Scientific, Inc. All rights reserved.`
- Указать условия: некоммерческое использование, запрет редистрибуции DLL пользователями, запрет реверс-инжиниринга, as-is без гарантий

**B. Окно About в приложении:**
- Добавить строку: `RawFileReader reading tool. Copyright © 2016 by Thermo Fisher Scientific, Inc. All rights reserved.`
- Ссылка на `THIRD_PARTY_NOTICES.md`

**C. EULA для конечных пользователей (`EULA.txt`):**
- Условие: пользователь не имеет права отдельно распространять RawFileReader DLL
- Условие: запрет реверс-инжиниринга DLL
- Ссылка на полный текст лицензии ThermoFisher

**D. `.spec` и сборка:**
- Убедиться, что 4 DLL включены в бандл
- DLL должны лежать в поддиректории `thermo/` внутри бандла

**Критерий приёмки:**
- `THIRD_PARTY_NOTICES.md` существует и корректен
- Окно About содержит строку ThermoFisher
- `EULA.txt` содержит ограничения для пользователя
- Собранный .exe включает DLL и notices

---

## Issue 6: CI/CD — сборка с RawFileReader + pythonnet

**Заголовок:** `ci: обновить release_exe.yml под RawFileReader + pythonnet`

**Метки:** `ci`, `build`

**Описание:**

Обновить `.github/workflows/release_exe.yml`:

- `pip install pythonnet` (вместо comtypes, который был для MSFileReader)
- Скачать RawFileReader DLL (4 файла) в `thermo/` — либо через curl с известного URL, либо закоммитить в LFS
- `.spec` должен включать `thermo/*.dll` как binaries/datas
- Убрать `comtypes` из `_collect_packages` в .spec (если он был только для MSFileReader)

**Открытый вопрос:** откуда брать DLL в CI?
- Вариант A: закоммитить в репозиторий (5-15 MB)
- Вариант B: скачивать из GitHub Releases репозитория RawFileReader
- Вариант C: NuGet restore

**Критерий приёмки:**
- CI собирает .exe с RawFileReader DLL внутри
- Smoke test: .exe запускается, `is_available()` возвращает True

---

## Зависимости между issues

```
Issue 1 ──┐
           ├──> Issue 3 ──> Issue 6
Issue 2 ──┘
           
Issue 4 ──> Issue 5
```

- Issues 1-3: технические, можно параллельно (1 и 2 — удаление старого, 3 — написание нового)
- Issue 3 зависит от 1 (raw_thermo_adapter знает, что raw_bridge уже не ссылается на GPL)
- Issue 6 зависит от 3 (CI собирает то, что уже работает локально)
- Issues 4-5: лицензионные, независимы от технических
- Issue 5 частично зависит от 4 (ссылается на финальную лицензию)
