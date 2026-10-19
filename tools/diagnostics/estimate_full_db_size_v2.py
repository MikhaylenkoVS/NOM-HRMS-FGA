"""Итоговая оценка размера базы по измеренной кривой (обновление).

Изменения против предыдущей версии:
  * добавлены измерения тяжёлых бинов (999.6 и 997.6 Да, 2.48 и 2.45 млн записей);
  * гистограмма бинов считается по подбинам 0.01 Да (точность раскладки Δ),
    поэтому распределение больше не смещено на ±1 бин;
  * убран мусорный блок by_x (двойной подсчёт);
  * в оценку добавлены накладные расходы индекса.

Запуск: python tools/estimate_full_db_size_v2.py
"""

from __future__ import annotations

import bisect
import itertools
import math
import time
from collections import Counter

MASS_SCALE = 100_000_000_000
BIN_WIDTH_U = 10_000_000_000  # бин 0.1 Да
SUB_WIDTH_U = 1_000_000_000  # подбин 0.01 Да (для точности раскладки Δ)
MASS_U = {
    "C": 1_200_000_000_000,
    "H": 100_782_503_223,
    "N": 1_400_307_400_443,
    "O": 1_599_491_461_957,
    "S": 3_197_207_117_440,
    "P": 3_097_376_199_842,
    "F": 1_899_840_316_273,
    "Cl": 3_496_885_268_200,
    "Br": 7_891_833_760_000,
    "I": 12_690_447_190_000,
}
HALO = ("F", "Cl", "Br", "I")
H_U = MASS_U["H"]
MAX_ATOMS = 5
INDEX_BYTES_PER_BLOCK = 24

# ── Измерено в tools/bin_full_benchmark.py (конечная масса в бине) ──────────
#   бин 300.05: 3 056; 500.05: 39 741; 700.05: 228 193;
#   999.60: 2 482 549; 997.60: 2 450 230 записей.
MEASURED = {
    "uint48 без H, shuffle, zstd9": [
        (3056, 6.00),
        (39741, 3.55),
        (228193, 2.38),
        (2482549, 2.12),
        (2450230, 2.13),
    ],
    "ранги+дельта, shuffle, zstd19": [
        (3056, 5.30),
        (39741, 2.24),
        (228193, 1.31),
        (2482549, 0.83),
        (2450230, 0.84),
    ],
    "uint64 c H, shuffle, zstd9": [
        (3056, 8.31),
        (39741, 4.59),
        (228193, 3.73),
        (2482549, 3.31),
        (2450230, 3.32),
    ],
}


def multiset_deltas():
    out = []
    for size in range(0, MAX_ATOMS + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            if any(c == collapsed for _, c in out):
                continue
            delta = sum(n * (MASS_U[el] - H_U) for el, n in collapsed)
            out.append((delta, collapsed))
    out.sort()
    return out


DELTAS = multiset_deltas()
DELTA_VALUES = [d for d, _ in DELTAS]


def fit(points):
    """Кусочно-линейная интерполяция бит/формула по ln(n) с плавным низом."""
    pts = sorted(points)
    xs = [math.log(n) for n, _ in pts]
    ys = [b for _, b in pts]

    def f(n: float) -> float:
        x = math.log(max(n, 2))
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            slope = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
            return max(0.30, ys[-1] + slope * (x - xs[-1]))
        i = bisect.bisect_right(xs, x) - 1
        t = (x - xs[i]) / (xs[i + 1] - xs[i])
        return ys[i] + t * (ys[i + 1] - ys[i])

    return f


def main() -> None:
    max_mass_u = 1000 * MASS_SCALE
    n_bins = max_mass_u // BIN_WIDTH_U + 1
    t0 = time.perf_counter()

    # группы: (подбин 0.01 Да, число H с капом) -> количество фреймворков
    groups: Counter = Counter()
    for c in range(1, max_mass_u // MASS_U["C"] + 1):
        m_c = c * MASS_U["C"]
        if m_c > max_mass_u:
            break
        for nv in range(min(127, (max_mass_u - m_c) // MASS_U["N"]) + 1):
            m_cn = m_c + nv * MASS_U["N"]
            for o in range(min(63, (max_mass_u - m_cn) // MASS_U["O"]) + 1):
                m_cno = m_cn + o * MASS_U["O"]
                for pv in range(min(63, (max_mass_u - m_cno) // MASS_U["P"]) + 1):
                    m_cnop = m_cno + pv * MASS_U["P"]
                    for sv in range(min(31, (max_mass_u - m_cnop) // MASS_U["S"]) + 1):
                        base = m_cnop + sv * MASS_U["S"]
                        if base > max_mass_u:
                            break
                        h_cap = min(
                            255, 2 * c + nv + pv + 2, (max_mass_u - base) // H_U
                        )
                        parity = (nv + pv) & 1
                        for h in range(parity, h_cap + 1, 2):
                            mass_u = base + h * H_U
                            if mass_u > max_mass_u:
                                break
                            groups[(mass_u // SUB_WIDTH_U, min(h, MAX_ATOMS))] += 1
    print(
        f"групп (подбин 0.01 Да × H): {len(groups):,} ({time.perf_counter()-t0:.1f} c)"
    )

    # раскладка по бинам 0.1 Да с точным учётом Δ
    bin_counts = [0] * n_bins
    for (sub, x_cap), n_group in groups.items():
        center = sub * SUB_WIDTH_U + SUB_WIDTH_U // 2
        k = bisect.bisect_right(DELTA_VALUES, max_mass_u - center)
        for d in DELTA_VALUES[:k]:
            nb = (center + d) // BIN_WIDTH_U
            if nb < n_bins:
                bin_counts[nb] += n_group
    total = sum(bin_counts)
    nz = [x for x in bin_counts if x]
    nz_sorted = sorted(nz)
    print(f"всего записей: {total:,}; занятых бинов: {len(nz):,}")
    print(
        f"записей на бин: медиана {nz_sorted[len(nz_sorted)//2]:,}, "
        f"p95 {nz_sorted[int(0.95*len(nz_sorted))]:,}, максимум {max(nz):,}"
    )
    print(
        "максимум по точному генератору (бин 999.6 Да): 2 482 549 "
        "(расхождение с гистограммой — точность раскладки Δ)"
    )

    # накладные расходы индекса
    index_mb = len(nz) * INDEX_BYTES_PER_BLOCK / 1e6
    print(f"\nиндекс: {len(nz)} блоков × {INDEX_BYTES_PER_BLOCK} Б = {index_mb:.2f} МБ")

    print("\nоценка размера (взвешенная по гистограмме, измеренная кривая):")
    for name, points in MEASURED.items():
        gb = sum(cnt * fit(points)(cnt) for cnt in nz) / 8 / 1e9
        print(f"  {name:28s}: {gb:6.3f} ГБ + индекс {index_mb:.2f} МБ")
    print(f"  {'наивно uint64':28s}: {total*8/1e9:6.3f} ГБ")
    print("\nоговорка: кривая измерена на бинах 3.1 тыс. … 2.48 млн записей;")
    print("для бинов вне этого диапазона — экстраполяция по последнему наклону.")


if __name__ == "__main__":
    main()
