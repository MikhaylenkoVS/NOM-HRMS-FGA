"""Почему в базе CHNOSPHal v3 есть пустые бины: разбор по данным.

1) корректная гистограмма заполненности по массам (бин = 0.1 Да);
2) структура «дыр» в нижней области масс;
3) независимая проверка: для выборки пустых бинов полный перебор по модели
   (свой код, не сборщик) должен дать ноль формул.
"""

from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path("tools/diagnostics")))
from verify_formula_db_v3 import brute_force_bin  # независимая реализация

IDX = Path("D:/Temp/User/formula_db_v3/chorsphal_1000_v3.idx")
BIN_WIDTH_U = 10_000_000_000  # 0.1 Да в единицах 1e-11
TOTAL = 10001

blob = IDX.read_bytes()
bins = {}
for i in range(len(blob) // 24):
    bi, off, c, raw, cnt = struct.unpack_from("<IQIII", blob, i * 24)
    bins[bi] = cnt

empty = [b for b in range(TOTAL) if b not in bins]


def da(b: int) -> float:
    return b * BIN_WIDTH_U / 1e11


print("=== 1. Заполненность по массам (бин = 0.1 Да) ===")
for lo in range(0, 1000, 100):
    hi = lo + 100
    tot = sum(1 for b in range(TOTAL) if lo <= da(b) < hi)
    emp = sum(1 for b in empty if lo <= da(b) < hi)
    fill = 100 * (tot - emp) / tot if tot else 0
    print(
        f"  {lo:4d}–{hi:4d} Да: бинов {tot:5d}, пустых {emp:5d}, заполнено {fill:6.1f}%"
    )

print()
print("=== 2. Нижняя область: где именно дыры ===")
for lo, hi in (
    (0, 12),
    (12, 30),
    (30, 60),
    (60, 100),
    (100, 150),
    (150, 200),
    (200, 300),
):
    tot = sum(1 for b in range(TOTAL) if lo <= da(b) < hi)
    emp = sum(1 for b in empty if lo <= da(b) < hi)
    print(f"  {lo:4d}–{hi:4d} Да: пустых {emp:4d} из {tot:4d}")
print(f"  всего пустых ниже 150 Да: {sum(1 for b in empty if da(b) < 150)}")
print(f"  всего пустых ниже 300 Да: {sum(1 for b in empty if da(b) < 300)}")
print(f"  всего пустых: {len(empty)}")

print()
print("=== 3. Сколько масс приходится на один непустой бин (плотность) ===")
for lo, hi in ((100, 200), (200, 400), (400, 700), (700, 1000)):
    sel = [b for b in bins if lo <= da(b) < hi]
    if sel:
        cnt = sum(bins[b] for b in sel)
        print(
            f"  {lo:4d}–{hi:4d} Да: формул {cnt:,} на {len(sel)} бинов "
            f"(в среднем {cnt / len(sel):,.0f} на бин)".replace(",", " ")
        )

print()
print("=== 4. Независимая проверка пустых бинов (полный перебор моделью) ===")
samples = []
for target in (15.0, 25.0, 40.0, 60.0, 90.0, 120.0, 200.0):
    b = int(round(target / 0.1))
    if b not in bins:
        samples.append(b)
for b in samples:
    found = brute_force_bin(b, cap=5, max_mass_u=10**14)
    print(
        f"  бин {b} ({da(b):.1f} Да): перебор нашёл {len(found)} формул — "
        f"{'ПУСТО подтверждено' if not found else 'ЕСТЬ ФОРМУЛЫ (ошибка базы!)'}"
    )

print()
print("=== 5. Ближайшие к пустому бину формулы (пример 40.1 Да) ===")
b0 = 401
found = brute_force_bin(b0, cap=5, max_mass_u=10**14)
print(f"  бин {b0} ({da(b0):.1f} Да): {len(found)} формул")
for b in range(b0 - 6, b0 + 7):
    f = brute_force_bin(b, cap=5, max_mass_u=10**14)
    mark = "пусто" if not f else f"{len(f)} формул, напр. {sorted(f)[0]}"
    print(f"    бин {b} ({da(b):.1f} Да): {mark}")
