---
name: spectrum-denoise-review
description: >
  Код-ревью и доработка алгоритмов шумоподавления спектров HRMS: `denoise()`,
  параметры `force`, `intensity`, `quantile`, целевые пороги recall/precision,
  smoke-тесты шумоподавления. Активировать когда пользователь говорит
  «шумоподавление», «denoise», «noise filter», «force», «noise_force»,
  «noise_intensity», «noise_quantile», «denoise_recall», «убрать шум»,
  «очистить спектр»; либо при изменении denoise() в spectrum_ops.py,
  test_mode.denoise или thresholds в pipeline.json, test_denoise.py.
---

# Spectrum Denoise Review — шумоподавление спектров

Рецензирование кода и настройка параметров шумоподавления масс-спектров.
На текущий момент наиболее нестабильный участок: режим `intensity` протестирован,
режимы `force` и `quantile` — недостаточно. Требуется систематическая валидация.

## Источники истины

| Файл | Что содержит |
|------|-------------|
| `src/core/spectrum_ops.py:288–319` | `denoise()` — основная функция |
| `src/core/pipeline.py:349–351` | Параметры денойзинга в `run_pipeline()` |
| `src/configs/pipeline.json:26–39` | `run_pipeline_defaults` (noise_force=10, noise_intensity=100) |
| `src/configs/pipeline.json:47–51` | `test_mode.denoise` (force=10, intensity=100, quantile=null) |
| `src/configs/pipeline.json:66–70` | `thresholds` (min_denoise_recall=0.90) |
| `tests/unit/test_denoise.py` | Модульные тесты денойзинга |
| `tests/integration/test_pipeline_integration.py:36–38` | Интеграционные тесты с порогами |

## Сигнатура и параметры

```python
def denoise(spec, *, force=1.5, intensity=None, quantile=None):
```

- `spec` — объект `nomspectra.spectrum.Spectrum` (содержит `.table` с колонками mass, intensity).
- `force` — множитель к автоопределённому уровню шума. По умолчанию 1.5.
  В production (run_pipeline) — 10. **Разница в 6.7× требует объяснения.**
- `intensity` — жёсткий порог интенсивности. Имеет высший приоритет.
- `quantile` — квантиль интенсивности (0–1). Используется, если `intensity` не задан.

**Приоритет параметров:** `intensity` > `quantile` > `force`.

## Режимы шумоподавления (статус тестирования)

| Режим | Параметр | Статус | Рекомендация |
|-------|----------|--------|-------------|
| `intensity` | `intensity=100` | ✅ Протестирован на тест-сетах | Использовать как основной |
| `force` | `force=10.0` | ⚠️ Слабо протестирован | Оптимизировать под тест-сеты |
| `quantile` | `quantile=0.1` | ❌ Не протестирован | Провести валидацию |

**Контекст:** `noise_force=10` в `run_pipeline_defaults` передаётся как
`force=10` в `denoise()`. При `force=10` автоопределённый уровень шума
умножается на 10 — это очень агрессивный порог, который может отсечь
слабые, но реальные пики. Вероятно, `intensity=100` перекрывает `force`
(имеет приоритет), поэтому на тест-сетах всё работает. **Необходимо**
протестировать `force` независимо (при `intensity=None`).

## Целевые метрики качества

Из `pipeline.json → thresholds`:

| Метрика | Порог | Формула |
|---------|-------|---------|
| `min_denoise_recall` | 0.90 | `denoised_kept / total_signals` (доля сигналов, сохранённых после денойзинга) |
| `min_assign_recall` | 0.90 | `assigned_ok / total_signals` (доля правильно назначенных формул) |
| `max_wrong_ratio` | 0.15 | `dmet_wrong / dmet_found` (доля неверно определённых серий) |

**Важно:** это ориентировочные пороги («на глаз»), не утверждённые. Допускается
временное снижение при рефакторинге, но должно отслеживаться.

## Алгоритм code-review шумоподавления

### При добавлении нового метода денойзинга:

1. **Прочитай существующий `denoise()`** — это тонкая обёртка над
   `Spectrum.noise_filter()`. Новые методы могут:
   - Заменить обёртку (если метод принципиально иной).
   - Добавиться как альтернативный параметр (например, `method="wavelet"`).

2. **Определи источник шума для тестов:**
   - Синтетические тест-сеты (set_01–set_05) генерируются с известным уровнем
     шума. Параметры генерации — в `src/simulations/generate_test_sets.py`.
   - Для реальных спектров: шум оценивается по областям без пиков (m/z за
     пределами хроматографического пика).

3. **Проверь метрики на всех 5 наборах:**
   ```bash
   python -m src.core.pipeline --test
   ```
   Или выборочно:
   ```bash
   pytest tests/unit/test_denoise.py -v
   pytest tests/integration/test_pipeline_integration.py -v -k denoise
   ```

4. **Сравни recall/precision ДО и ПОСЛЕ:**
   - denoise_recall: должен быть ≥ 0.90 на каждом из 5 наборов.
   - Если новый метод улучшает recall на set_01, но ухудшает на set_03 —
     это НЕ improvement, ищи проблему.

5. **Визуализируй:** наложи исходный, зашумлённый и очищенный спектры.
   Проверь визуально, что слабые пики на краях массового диапазона не потеряны.

### Checks перед коммитом:

- [ ] `pytest tests/unit/test_denoise.py` — pass.
- [ ] `pytest tests/integration/test_pipeline_integration.py` — denoise_recall ≥ 0.90.
- [ ] Новый параметр добавлен в `run_pipeline()` с значением по умолчанию в `pipeline.json`.
- [ ] Параметр не влияет на другие этапы пайплайна (assign, find_series).
- [ ] Нет хардкода порогов — всё в `PIPELINE`.
- [ ] Визуальная проверка на 1–2 наборах (спектры не «пересушены»).

## Типичные ошибки

1. **Приоритет параметров нарушен:** `force` передан, но `intensity` не None —
   `force` молча игнорируется. Документировать! Или логгировать warning.
2. **Потеря слабых пиков:** агрессивный `force` (≥10) при `intensity=None`
   может вырезать реальные пики на краях динамического диапазона.
3. **Применение денойзинга к derivatized-спектрам с теми же параметрами:**
   дейтерометилированные/дейтероацилированные молекулы могут иметь другую
   интенсивность.
4. **NaN в intensity:** `intensity` колонка с NaN → `noise_filter` падает.
   Проверять входные данные.

## Связанные скиллы

- `pytest-regression-nom` — написание тестов метрик.
- `config-safety-audit` — аудит порогов в pipeline.json.
- `code-review-reliability-first` — общий ревью с приоритетом надёжности.
