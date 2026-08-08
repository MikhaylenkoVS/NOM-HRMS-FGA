# План для следующей сессии — formula_db: база формул + бенчмарк

> **Создан:** 2026-08-08 | **Статус:** 🟡 formula_db код готов, нужна интеграция в UI/pipeline

---

## ✅ Уже сделано

### formula_db — база формул (CNOSP uint32 + byte shuffle + Zstd)

| Файл | Назначение |
|------|-----------|
| `src/core/formula_db/__init__.py` | Публичное API |
| `src/core/formula_db/__main__.py` | CLI: `python -m src.core.formula_db build` |
| `src/core/formula_db/_packed.py` | CNOSP uint32 pack/unpack, byte shuffle, H restoration, ceil_div |
| `src/core/formula_db/_builder.py` | Integer-only генератор, byte shuffle + Zstd, progress bar |
| `src/core/formula_db/_reader.py` | Runtime: decompress → unshuffle → uint32 → restore H → search |
| `src/core/formula_db/_manager.py` | Download/verify менеджер |
| `tests/unit/test_formula_db.py` | 43 теста |

### Готовая база данных

```
data/formula_db/chposp_1000_zstd9_v2.fdb            35 MB
data/formula_db/chposp_1000_zstd9_v2.manifest.json  2.5 MB
```

- **79,576,593 формулы** (CHNOSP, до 1000 Da, closed-shell)
- Формат v2: CNOSP uint32 (4 байта, без H) + byte shuffle + Zstd level 9
- H восстанавливается детерминированно из CNOSP + массовых границ блока
- Сжатие: 318 MB raw → 35 MB (8.8×, благодаря byte shuffle)

### Benchmark итог

| Вариант | Размер |
|---------|:---:|
| v1 (CHNOSP 5B, без shuffle, zstd9) | 316 MB |
| v1 (CHNOSP 5B, без shuffle, zstd22) | 291 MB |
| v2 (CNOSP 4B + byte shuffle, zstd9) | **35 MB** ✓ |
| v2 (CNOSP 4B + byte shuffle, zstd22) | 30 MB |

### Все тесты: 361 passed

---

## ⬜ Что осталось сделать

### 1. Интеграция formula_db в assign_formulas и pipeline

- Адаптировать `src/core/spectrum/_assign.py`:
  - проверять наличие `FormulaDatabaseReader`
  - если база найдена → использовать `reader.search()` с ppm-окном
  - если нет → fallback на старый `_generate_candidate_formulas()`
- Интегрировать `DatabaseManager` для проверки/скачивания базы
- Передавать `element_filter` (из `FormulaSearchConfig.ranges`) в `reader.search()`

### 2. Интеграция в GUI

- При старте: проверить наличие базы через `DatabaseManager.is_available()`
- Если нет → кнопка «скачать базу» с индикацией версии/размера
- UI-прогресс при загрузке
- Выбор локального файла `.manifest.json` вручную

### 3. Интеграция в PyInstaller / installer

- Добавить `zstandard` в hidden imports (`.spec`)
- Не встраивать 35 MB базу в executable
- База — отдельная опция установки (Inno Setup / NSIS)

### 4. Документация

- Как собрать базу разработчику
- Где лежит база у пользователя (platformdirs: `user_data_dir("NOM-HRMS-FGA")`)
- Как проверить SHA-256
- Формат manifest
- Ограничения химического профиля (P trivalent, S divalent)

---

## Ключевые API (для интеграции)

```python
# Упаковка
from src.core.formula_db import pack_c_n_o_s_p, unpack_c_n_o_s_p

# Поиск
from src.core.formula_db import FormulaDatabaseReader
reader = FormulaDatabaseReader("path/to/chposp_1000_zstd9_v2.manifest.json")
results = reader.search(target_mass=122.0368, ppm=1.0, element_filter={"C": (1,50)})
# → list[SearchResult] (formula_str, counts, exact_mass, error_ppm, dbe)

# Менеджер загрузок
from src.core.formula_db import DatabaseManager
mgr = DatabaseManager()
if not mgr.is_available():
    mgr.download(progress_callback=my_cb)
reader = mgr.get_reader()
```

---

## Быстрый старт

```bash
cd C:\Users\mvs\PycharmProjects\NOM-HRMS-FGA
python -m pytest tests/ -q    # 361 passed

# Полная пересборка базы (25 мин)
python -m src.core.formula_db build --output data/formula_db/chposp_1000_zstd9_v2 --max-mass 1000
```
