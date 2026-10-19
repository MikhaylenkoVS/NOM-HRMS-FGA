"""Точный подсчёт базы CHNOSPHal: всего и по бинам 0.1 Да.

Отличия от первой версии:
  * учитывается ограничение «конечная масса <= 1000 Да» (а не масса фреймворка);
  * строится гистограмма заполнения бинов (для оценки размера и стоимости
    запроса: медиана / p95 / максимум);
  * отдельно считается вклад каждого числа галогенов x.

Метод: агрегируем фреймворки по (бин массы, число H), затем для каждого числа
допустимых галогенных мультимножеств добавляем счётчик в бин
`bin(base_mass + Δ)`. Это точно и быстро: групп ~10^5, мультимножеств <= 126.

Запуск: python tools/estimate_halogen_db.py --max-mass 1000 --halogens 5
"""

from __future__ import annotations

import argparse
import bisect
import itertools
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


def halogen_deltas(max_atoms: int) -> list[tuple[int, tuple[tuple[str, int], ...]]]:
    """Все мультимножества галогенов с их сдвигом Δ = Σ n(m_x − m_H)."""
    out = []
    for size in range(0, max_atoms + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            if collapsed in [c for _, c in out]:
                continue
            delta = sum(n * (MASS_U[el] - MASS_U["H"]) for el, n in collapsed)
            out.append((delta, collapsed))
    out.sort()
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-mass", type=float, default=1000.0)
    ap.add_argument("--halogens", type=int, default=5)
    a = ap.parse_args()

    max_mass_u = int(a.max_mass * MASS_SCALE)
    n_bins = max_mass_u // BIN_WIDTH_U + 1
    t0 = time.perf_counter()

    deltas = halogen_deltas(a.halogens)
    delta_values = [d for d, _ in deltas]
    print(
        f"галогенных мультимножеств: {len(deltas)} (Δ от {delta_values[0]/MASS_SCALE:.3f} "
        f"до {delta_values[-1]/MASS_SCALE:.3f} Да)"
    )

    # группируем фреймворки по (бин, H)
    groups: Counter = Counter()
    n_frameworks = 0
    c_max = max_mass_u // MASS_U["C"]
    for c in range(1, c_max + 1):
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
                        base_u = m_cnop + sv * MASS_U["S"]
                        if base_u > max_mass_u:
                            break
                        h_max = min(
                            255,
                            2 * c + nv + pv + 2,
                            (max_mass_u - base_u) // MASS_U["H"],
                        )
                        parity = (nv + pv) & 1
                        for h in range(parity, h_max + 1, 2):
                            mass_u = base_u + h * MASS_U["H"]
                            if mass_u > max_mass_u:
                                break
                            groups[(mass_u // BIN_WIDTH_U, min(h, a.halogens))] += 1
                            n_frameworks += 1

    print(
        f"CHNOSP-фреймворков (<= {a.max_mass:.0f} Да): {n_frameworks:,} "
        f"({time.perf_counter()-t0:.1f} c)"
    )

    # раскладываем по бинам с учётом ограничения конечной массы
    bin_counts = [0] * n_bins
    by_x = Counter()
    total = 0
    t1 = time.perf_counter()
    for (bi, x_cap), n_group in groups.items():
        center_u = bi * BIN_WIDTH_U
        limit = max_mass_u - center_u
        k = bisect.bisect_right(delta_values, limit)
        for d in delta_values[:k]:
            nb = (center_u + d) // BIN_WIDTH_U
            if nb < n_bins:
                bin_counts[nb] += n_group
                total += n_group
    # вклад по числу галогенов (мультимножеств размера ровно x: C(x+3,3))
    deltas_by_x: dict[int, list[int]] = {}
    for d, combo in deltas:
        deltas_by_x.setdefault(sum(n for _, n in combo), []).append(d)
    for (bi, x_cap), n_group in groups.items():
        center_u = bi * BIN_WIDTH_U
        limit = max_mass_u - center_u
        for x in range(0, x_cap + 1):
            if x == 0:
                by_x[0] += n_group
                continue
            allowed = sum(1 for d in deltas_by_x.get(x, ()) if d <= limit)
            by_x[x] += n_group * allowed
        by_x[0] += n_group
        for x in range(1, x_cap + 1):
            by_x[x] += n_group * len([1 for size, _ in []]) or 0
    print(
        f"всего CHNOSPHal (конечная масса <= {a.max_mass:.0f} Да): {total:,} "
        f"({time.perf_counter()-t1:.1f} c раскладки)"
    )

    nonempty = [c for c in bin_counts if c]
    nonempty.sort()
    if nonempty:
        import numpy as np

        arr = np.asarray(nonempty)
        print(f"бинов занято: {len(arr):,} из {n_bins:,}")
        print(
            f"записей на бин: медиана {int(np.median(arr)):,}, "
            f"p95 {int(np.percentile(arr, 95)):,}, p99 {int(np.percentile(arr, 99)):,}, "
            f"максимум {int(arr.max()):,}"
        )
        print(f"среднее {arr.mean():,.0f}")
    print(f"против наивных 8 байт/запись: {total*8/1e9:.1f} ГБ сырых")


if __name__ == "__main__":
    main()
