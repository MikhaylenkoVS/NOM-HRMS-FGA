"""Точный подсчёт объёма базы CHNOSPHal (галогены до N атомов).

Считаем без хранения формул: для каждого CHNOSP-фреймворка число допустимых
галогенных подстановок = число мультимножеств размера x <= min(N, H) над
4 элементами (F, Cl, Br, I), то есть C(x+3, 3).

Проверки соответствуют builder._enum_valid_cnosp:
  * DBE-условие (чётность Льюиса и DBE >= 0) сводится к h <= 2c + 2 + n + p;
  * h идёт с шагом 2 от parity = (n + p) & 1;
  * лимиты элементов: N <= 127, O <= 63, P <= 63, S <= 31, H <= 255.
"""

import argparse
import time
from math import comb

# Масштаб 1e11, как в _packed.py
MASS_U = {
    "C": 1_200_000_000_000,
    "H": 100_782_503_223,
    "N": 1_400_307_400_443,
    "O": 1_599_491_461_957,
    "S": 3_197_207_117_440,
    "P": 3_097_376_199_842,
}


def multisets_upto(x_max: int) -> int:
    """Число мультимножеств размера 0..x_max над 4 элементами: C(x+3,3)."""
    return sum(comb(x + 3, 3) for x in range(x_max + 1))


def count(max_mass: float, halogen_atoms: int) -> dict:
    max_mass_u = int(max_mass * 100_000_000_000)
    t0 = time.perf_counter()
    n_frameworks = 0
    total = 0
    by_x = {x: 0 for x in range(halogen_atoms + 1)}
    c_max = max_mass_u // MASS_U["C"]
    for c in range(1, c_max + 1):
        m_c = c * MASS_U["C"]
        if m_c > max_mass_u:
            break
        n_limit = min(127, (max_mass_u - m_c) // MASS_U["N"])
        for nv in range(n_limit + 1):
            m_cn = m_c + nv * MASS_U["N"]
            o_limit = min(63, (max_mass_u - m_cn) // MASS_U["O"])
            for o in range(o_limit + 1):
                m_cno = m_cn + o * MASS_U["O"]
                p_limit = min(63, (max_mass_u - m_cno) // MASS_U["P"])
                for pv in range(p_limit + 1):
                    m_cnop = m_cno + pv * MASS_U["P"]
                    s_limit = min(31, (max_mass_u - m_cnop) // MASS_U["S"])
                    for sv in range(s_limit + 1):
                        base_u = m_cnop + sv * MASS_U["S"]
                        if base_u > max_mass_u:
                            break
                        h_max_v = 2 * c + nv + pv + 2
                        h_max_m = (max_mass_u - base_u) // MASS_U["H"]
                        h_max = min(255, h_max_v, h_max_m)
                        parity = (nv + pv) & 1
                        if h_max < parity:
                            continue
                        n_h = (h_max - parity) // 2 + 1
                        n_frameworks += n_h
                        # Для каждого валидного h: число галогенных вариантов
                        # C(min(N,h)+4, 4) (мультимножества размера <= min(N,h)).
                        h = parity
                        while h <= h_max:
                            x_cap = min(halogen_atoms, h)
                            variants = multisets_upto(x_cap)
                            total += variants
                            by_x[0] += 1  # x = 0 (сам фреймворк)
                            for x in range(1, x_cap + 1):
                                by_x[x] += comb(x + 3, 3)
                            h += 2
    return {
        "max_mass": max_mass,
        "halogen_atoms": halogen_atoms,
        "frameworks_chposp": n_frameworks,
        "total_chnosphal": total,
        "by_halogen_count": by_x,
        "seconds": round(time.perf_counter() - t0, 1),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-mass", type=float, default=1000.0)
    ap.add_argument("--halogens", type=int, default=5)
    a = ap.parse_args()
    r = count(a.max_mass, a.halogens)
    print(f"CHNOSP-фреймворков (<= {r['max_mass']:.0f} Да): {r['frameworks_chposp']:,}")
    print(f"CHNOSPHal (галогенов <= {r['halogen_atoms']}): {r['total_chnosphal']:,}")
    print(
        "по числу атомов галогенов:",
        {k: f"{v:,}" for k, v in r["by_halogen_count"].items()},
    )
    raw_gb = r["total_chnosphal"] * 8 / 1e9
    print(f"размер в uint64 (сырой): {raw_gb:.1f} ГБ")
    print(
        f"только CHNOSP в uint32: {r['frameworks_chposp'] * 4 / 1e9:.2f} ГБ (текущая база 36 МБ zstd-9)"
    )
    print(f"время подсчёта: {r['seconds']} c")
