"""Полнота структурного представления + итоговая оценка размера (быстрая версия).

1. Полнота проверяется двумя способами:
   а) аналитически: при подстановке H -> X числитель DBE
      (2C + 2 + N + P - H - X) инвариантен, поэтому «родитель» (H + x, без
      галогенов) всегда проходит профиль базовой CHNOSP-БД, если конечная
      формула химически допустима;
   б) эмпирически на окне 300–320 Да (полный перебор): считаем родителей вне
      профиля и неоднозначные пары (родитель, подстановка).

2. Оценка размера: точная гистограмма заполнения бинов 0.1 Да (та же схема,
   что в estimate_halogen_db_v2) + измеренная в bin_benchmark.py зависимость
   «бит/формула от числа записей в бине».

Запуск: python tools/estimate_full_db_size.py
"""

from __future__ import annotations

import bisect
import itertools
import math
import time
from collections import Counter

MASS_SCALE = 100_000_000_000
BIN_WIDTH_U = 10_000_000_000
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


def base_profile_ok(c, h, n, o, s, p) -> bool:
    if c < 1 or min(h, n, o, s, p) < 0:
        return False
    if h > 255 or n > 127 or o > 63 or s > 31 or p > 63:
        return False
    num = 2 * c + 2 + n + p - h
    return num >= 0 and num % 2 == 0


def fit_bits_per_record(points):
    xs = [math.log(n) for n, _ in points]
    ys = [b for _, b in points]

    def f(n: float) -> float:
        x = math.log(max(n, 2))
        if x <= xs[0]:
            return ys[0]
        if x >= xs[-1]:
            slope = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2])
            return max(0.35, ys[-1] + slope * (x - xs[-1]))
        i = bisect.bisect_right(xs, x) - 1
        t = (x - xs[i]) / (xs[i + 1] - xs[i])
        return ys[i] + t * (ys[i + 1] - ys[i])

    return f


MEASURED = {
    "ранги+дельта, zstd19": [(3095, 4.89), (39741, 2.24), (228193, 1.39)],
    "uint48 без H, zstd9": [(3095, 6.00), (39741, 3.55), (228193, 2.62)],
}


def check_completeness(lo_da: float, hi_da: float) -> None:
    """Полный перебор окна: родители и неоднозначность."""
    lo_u, hi_u = int(lo_da * MASS_SCALE), int(hi_da * MASS_SCALE)
    bad = amb = total = 0
    seen: dict[tuple, int] = {}
    for c in range(1, hi_u // MASS_U["C"] + 1):
        m_c = c * MASS_U["C"]
        if m_c >= hi_u:
            break
        for nv in range(min(127, (hi_u - m_c) // MASS_U["N"]) + 1):
            m_cn = m_c + nv * MASS_U["N"]
            if m_cn >= hi_u:
                break
            for o in range(min(63, (hi_u - m_cn) // MASS_U["O"]) + 1):
                m_cno = m_cn + o * MASS_U["O"]
                if m_cno >= hi_u:
                    break
                for pv in range(min(63, (hi_u - m_cno) // MASS_U["P"]) + 1):
                    m_cnop = m_cno + pv * MASS_U["P"]
                    if m_cnop >= hi_u:
                        break
                    for sv in range(min(31, (hi_u - m_cnop) // MASS_U["S"]) + 1):
                        base = m_cnop + sv * MASS_U["S"]
                        if base >= hi_u:
                            break
                        h_cap = min(255, 2 * c + nv + pv + 2, (hi_u - 1 - base) // H_U)
                        parity = (nv + pv) & 1
                        for h in range(parity, h_cap + 1, 2):
                            fw_u = base + h * H_U
                            if fw_u >= hi_u:
                                break
                            if fw_u < lo_u - DELTA_VALUES[-1]:
                                continue
                            for delta, combo in DELTAS:
                                x = sum(n for _, n in combo)
                                if x > h:
                                    continue
                                mass = fw_u + delta
                                if not (lo_u <= mass < hi_u):
                                    continue
                                total += 1
                                if not base_profile_ok(c, h, nv, o, sv, pv):
                                    bad += 1
                                key = (c, h - x, nv, o, sv, pv, combo)
                                if key in seen and seen[key] != mass:
                                    amb += 1
                                seen[key] = mass
    print(
        f"полнота на окне {lo_da:.0f}–{hi_da:.0f} Да: конечных формул {total:,}; "
        f"родителей вне профиля {bad}; неоднозначных {amb}"
    )


def main() -> None:
    print("─" * 70)
    print("1. Полнота структурного представления")
    check_completeness(300.0, 320.0)
    print("   аналитически: числитель DBE инвариантен при H -> X, поэтому")
    print("   родитель всегда проходит базовый профиль (следствие, не гипотеза)")

    print("─" * 70)
    print("2. Точная гистограмма заполнения бинов")
    t0 = time.perf_counter()
    max_mass_u = 1000 * MASS_SCALE
    n_bins = max_mass_u // BIN_WIDTH_U + 1
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
                            groups[(mass_u // BIN_WIDTH_U, min(h, MAX_ATOMS))] += 1
    bin_counts = [0] * n_bins
    for (bi, x_cap), n_g in groups.items():
        center = bi * BIN_WIDTH_U
        k = bisect.bisect_right(DELTA_VALUES, max_mass_u - center)
        for d in DELTA_VALUES[:k]:
            bin_counts[(center + d) // BIN_WIDTH_U] += n_g
    nz = [x for x in bin_counts if x]
    total = sum(nz)
    print(
        f"   всего записей: {total:,}; занятых бинов: {len(nz):,} "
        f"({time.perf_counter()-t0:.1f} c)"
    )
    print(f"   медиана {sorted(nz)[len(nz)//2]:,}; максимум {max(nz):,}")

    print("─" * 70)
    print("3. Оценка размера по измеренной кривой бит/формула")
    for name, points in MEASURED.items():
        f = fit_bits_per_record(points)
        gb = sum(cnt * f(cnt) for cnt in nz) / 8 / 1e9
        print(f"   {name:26s}: {gb:6.3f} ГБ")
    print(f"   {'наивно uint64':26s}: {total*8/1e9:6.3f} ГБ")


if __name__ == "__main__":
    main()
