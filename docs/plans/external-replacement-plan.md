# Задачи по замене external/ GPL-кода на собственный

> **Создан:** 2026-07-26 | **Статус:** 🟢 завершён | **Закрыт:** 2026-08-07
> **Принцип:** clean-room реализация — чтение документации ThermoFisher (RawFileReader SDK, mzML spec),
> написание с нуля без просмотра GPL-исходников `pymsfilereader.py`.

## Анализ использования

| Файл в external/ | Используется проектом? | Действие |
|------------------|----------------------|----------|
| `pymsfilereader.py` (618 строк) | ✅ Да, через `raw_bridge.py` | Написать замену с нуля |
| `gmm_filter.py` (477 строк) | ❌ Нет | Удалить из production |
| `app.py` (428 строк) | ❌ Нет (отдельный GUI-инструмент) | Удалить из production |

---

## Фаза 1: Замена pymsfilereader → raw_thermo_adapter

> **Цель:** свой модуль `src/core/raw_thermo_adapter.py`, использующий RawFileReader
> (.NET DLL) вместо MSFileReader COM. Тот же API, что у `raw_bridge.py`.

### 1.1. Изучить API RawFileReader (без просмотра GPL-кода)

- [x] Скачан (DLL в thermo/)