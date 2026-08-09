# Implementation Report: User Guide

**Task:** 96-user-guide
**Date:** 2026-08-09
**Implemented by:** DeepCode

## Summary
Created user guide draft: installation, data prep, analysis,
results interpretation, presets, FAQ and troubleshooting.

## Changes made

| File | Change type | Description |
|------|-------------|-------------|
| docs/user_guide.md | add | Full user guide (184 lines, 6 sections) |
| README.md | modify | Added link to user guide |

## Structure
1. Установка — .exe, pip, разработчики
2. Подготовка данных — CSV формат, колонки, ThermoRAW
3. Запуск анализа — загрузка, параметры, пресеты
4. Интерпретация результатов — таблица, VK, серии
5. Пресеты — soil, peat, coal, water
6. Частые ошибки — Python PATH, CSV формат, RawFileReader, Linux

## Validation

```bash
python tools/ai_workflow.py validate-task 96-user-guide  # PASSED
```
