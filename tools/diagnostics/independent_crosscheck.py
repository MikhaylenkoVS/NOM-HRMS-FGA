"""Независимая проверка множества формул и round-trip формата.

Требование ревью: эталон не должен использовать тот же генератор/фильтры, иначе
равенство ничего не проверяет. Здесь независимая сторона:

  * массы заданы отдельными литералами (IUPAC, 12C = 12 ровно, в шкале 1e-11 Да);
  * перебор ВСЕХ кортежей элементов в границах подпространства (без формул
    «базовый профиль + подстановка»);
  * химические правила (DBE >= 0, целочисленность по Льюису, C >= 1)
    реализованы заново, а не импортируются из src;
  * отбор по массе идёт по независимо посчитанной массе.

Сравниваются множества строк формул и точность массы; дополнительно проверяется
round-trip: decode(encode(F), bin) == F, включая восстановление H по номеру бина.

Запуск:
  python tools/independent_crosscheck.py --max-mass 200 --halogen-cap 2
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import platform
import sys
import time

import numpy as np

# ── Независимые литералы масс (IUPAC/AME2020), шкала 1e-11 Да ───────────────
IU_PAC = {
    "C": 1_200_000_000_000,  # 12C = 12 Да ровно (12 * 1e11)
    "H": 100782503223,  # 1.00782503223
    "N": 1400307400443,  # 14.00307400443
    "O": 1599491461957,  # 15.99491461957
    "S": 3197207117440,  # 31.9720711744
    "P": 3097376199842,  # 30.97376199842
    "F": 1899840316273,  # 18.99840316273
    "Cl": 3496885268200,  # 34.968852682
    "Br": 7891833760000,  # 78.9183376
    "I": 12690447190000,  # 126.9044719
}
SCALE = 100_000_000_000
BIN_WIDTH = 10_000_000_000  # 0.1 Да


def dbe_ok(c, h, n, o, s, p, f, cl, br, i):
    """DBE = (2C + 2 + N + P - H - X)/2, X = F+Cl+Br+I: >= 0 и целое."""
    x = f + cl + br + i
    num = 2 * c + 2 + n + p - h - x
    return num >= 0 and num % 2 == 0


def mass_u(c, h, n, o, s, p, f, cl, br, i) -> int:
    return (
        c * IU_PAC["C"]
        + h * IU_PAC["H"]
        + n * IU_PAC["N"]
        + o * IU_PAC["O"]
        + s * IU_PAC["S"]
        + p * IU_PAC["P"]
        + f * IU_PAC["F"]
        + cl * IU_PAC["Cl"]
        + br * IU_PAC["Br"]
        + i * IU_PAC["I"]
    )


def formula_str(c, h, n, o, s, p, f, cl, br, i) -> str:
    counts = {
        "C": c,
        "H": h,
        "N": n,
        "O": o,
        "S": s,
        "P": p,
        "F": f,
        "Cl": cl,
        "Br": br,
        "I": i,
    }
    order = ["C", "H"] + sorted(e for e in counts if e not in ("C", "H"))
    return "".join(
        el + (str(counts[el]) if counts[el] > 1 else "")
        for el in order
        if counts.get(el)
    )


def independent_set(max_mass_u: int, cap: int, bounds: dict):
    """Полный перебор кортежей элементов (эталон) с отсечением по массе."""
    out = {}
    MP = IU_PAC
    for c in range(1, bounds["C"] + 1):
        m_c = c * MP["C"]
        if m_c > max_mass_u:
            break
        for h in range(0, bounds["H"] + 1):
            m_ch = m_c + h * MP["H"]
            if m_ch > max_mass_u:
                break
            for n in range(0, bounds["N"] + 1):
                m_chn = m_ch + n * MP["N"]
                if m_chn > max_mass_u:
                    break
                for o in range(0, bounds["O"] + 1):
                    m_chno = m_chn + o * MP["O"]
                    if m_chno > max_mass_u:
                        break
                    for s_ in range(0, bounds["S"] + 1):
                        m_chnos = m_chno + s_ * MP["S"]
                        if m_chnos > max_mass_u:
                            break
                        for p in range(0, bounds["P"] + 1):
                            m_base = m_chnos + p * MP["P"]
                            if m_base > max_mass_u:
                                break
                            for f in range(0, cap + 1):
                                m_f = m_base + f * MP["F"]
                                if m_f > max_mass_u:
                                    break
                                for cl in range(0, cap + 1 - f):
                                    m_cl = m_f + cl * MP["Cl"]
                                    if m_cl > max_mass_u:
                                        break
                                    for br in range(0, cap + 1 - f - cl):
                                        m_br = m_cl + br * MP["Br"]
                                        if m_br > max_mass_u:
                                            break
                                        for i in range(0, cap + 1 - f - cl - br):
                                            m = m_br + i * MP["I"]
                                            if m > max_mass_u:
                                                break
                                            if not dbe_ok(
                                                c, h, n, o, s_, p, f, cl, br, i
                                            ):
                                                continue
                                            out[
                                                formula_str(
                                                    c, h, n, o, s_, p, f, cl, br, i
                                                )
                                            ] = m
    return out


def generator_set(max_mass_u: int, cap: int):
    """Множество по модели «базовый CHNOSP-профиль + подстановка H -> X»."""
    halo = ("F", "Cl", "Br", "I")
    multisets = []
    for size in range(0, cap + 1):
        for combo in itertools.combinations_with_replacement(halo, size):
            collapsed = tuple((el, combo.count(el)) for el in halo if combo.count(el))
            if collapsed not in [c for _, c in multisets]:
                delta = sum(n * (IU_PAC[el] - IU_PAC["H"]) for el, n in collapsed)
                multisets.append((delta, collapsed))
    out = {}
    max_c = max_mass_u // IU_PAC["C"] + 1
    for c in range(1, max_c + 1):
        m_c = c * IU_PAC["C"]
        if m_c > max_mass_u:
            break
        for n in range(0, (max_mass_u - m_c) // IU_PAC["N"] + 1):
            m_cn = m_c + n * IU_PAC["N"]
            for o in range(0, (max_mass_u - m_cn) // IU_PAC["O"] + 1):
                m_cno = m_cn + o * IU_PAC["O"]
                for p in range(0, (max_mass_u - m_cno) // IU_PAC["P"] + 1):
                    m_cnop = m_cno + p * IU_PAC["P"]
                    for s in range(0, (max_mass_u - m_cnop) // IU_PAC["S"] + 1):
                        base = m_cnop + s * IU_PAC["S"]
                        if base > max_mass_u:
                            break
                        h_max = min(
                            255, 2 * c + n + p + 2, (max_mass_u - base) // IU_PAC["H"]
                        )
                        parity = (n + p) & 1
                        for h in range(parity, h_max + 1, 2):
                            fw = base + h * IU_PAC["H"]
                            if fw > max_mass_u:
                                break
                            for delta, combo in multisets:
                                x = sum(k for _, k in combo)
                                if x > h or x > cap:
                                    continue
                                m = fw + delta
                                if m > max_mass_u:
                                    continue
                                d = dict(combo)
                                out[
                                    formula_str(
                                        c,
                                        h - x,
                                        n,
                                        o,
                                        s,
                                        p,
                                        d.get("F", 0),
                                        d.get("Cl", 0),
                                        d.get("Br", 0),
                                        d.get("I", 0),
                                    )
                                ] = m
    return out


def roundtrip_check(formulas_mass: dict, cap: int) -> dict:
    """encode -> decode с восстановлением H по бину; сверка строки и массы."""
    halo = ("F", "Cl", "Br", "I")
    code_of = {}
    for size in range(0, cap + 1):
        for combo in itertools.combinations_with_replacement(halo, size):
            collapsed = tuple((el, combo.count(el)) for el in halo if combo.count(el))
            if collapsed not in code_of:
                code_of[collapsed] = len(code_of)
    bad_str = bad_mass = bad_h = 0
    checked = 0
    for fstr, m in formulas_mass.items():
        counts = parse(fstr)
        x_counts = {el: counts.get(el, 0) for el in halo}
        combo = tuple((el, k) for el, k in x_counts.items() if k)
        x = sum(k for _, k in combo)
        c, n, o, s, p = (
            counts.get("C", 0),
            counts.get("N", 0),
            counts.get("O", 0),
            counts.get("S", 0),
            counts.get("P", 0),
        )
        # код без H: C, N, O, S, P, x, код композиции
        code = (
            c
            | (n << 8)
            | (o << 15)
            | (s << 22)
            | (p << 28)
            | (x << 34)
            | ((code_of[combo] + 1) << 37)
        )
        # декодирование
        dc = code & 0xFF
        dn = (code >> 8) & 0x7F
        do = (code >> 15) & 0x7F
        ds = (code >> 22) & 0x3F
        dp = (code >> 28) & 0x3F
        dxc = ((code >> 37) & 0x7F) - 1
        combo_back = list(code_of.keys())[list(code_of.values()).index(dxc)]
        base = (
            dc * IU_PAC["C"]
            + dn * IU_PAC["N"]
            + do * IU_PAC["O"]
            + ds * IU_PAC["S"]
            + dp * IU_PAC["P"]
            + sum(k * IU_PAC[el] for el, k in combo_back)
        )
        bin_index = m // BIN_WIDTH
        lo = bin_index * BIN_WIDTH
        h_rec = -(-(lo - base) // IU_PAC["H"])
        if not (lo <= base + h_rec * IU_PAC["H"] < lo + BIN_WIDTH):
            bad_h += 1
        d = dict(combo_back)
        got = formula_str(
            dc,
            h_rec,
            dn,
            do,
            ds,
            dp,
            d.get("F", 0),
            d.get("Cl", 0),
            d.get("Br", 0),
            d.get("I", 0),
        )
        if got != fstr:
            bad_str += 1
        if base + h_rec * IU_PAC["H"] != m:
            bad_mass += 1
        checked += 1
    return {
        "checked": checked,
        "bad_string": bad_str,
        "bad_mass": bad_mass,
        "bad_h": bad_h,
    }


def parse(fstr: str) -> dict:
    import re

    out = {}
    for el, num in re.findall(r"([A-Z][a-z]?)(\d*)", fstr):
        if not el:
            continue
        out[el] = int(num) if num else 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-mass", type=float, default=200.0)
    ap.add_argument("--halogen-cap", type=int, default=2)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    max_mass_u = int(a.max_mass * SCALE)
    cap = a.halogen_cap
    bounds = {
        "C": int(a.max_mass // 12) + 1,
        "H": int(a.max_mass) + 4,
        "N": int(a.max_mass // 14) + 1,
        "O": int(a.max_mass // 16) + 1,
        "S": int(a.max_mass // 32) + 1,
        "P": int(a.max_mass // 31) + 1,
    }
    t0 = time.perf_counter()
    ref = independent_set(max_mass_u, cap, bounds)
    t_ref = time.perf_counter() - t0
    t0 = time.perf_counter()
    gen = generator_set(max_mass_u, cap)
    t_gen = time.perf_counter() - t0

    only_ref = sorted(set(ref) - set(gen))
    only_gen = sorted(set(gen) - set(ref))
    mass_diff = [abs(ref[f] - gen[f]) for f in set(ref) & set(gen) if ref[f] != gen[f]]
    rt = roundtrip_check(ref, cap)

    print(f"подпространство: масса <= {a.max_mass:.0f} Да, галогенов <= {cap}")
    print(f"независимый перебор (все кортежи): {len(ref):,} формул за {t_ref:.1f} c")
    print(f"модель «базовый профиль + подстановка»: {len(gen):,} за {t_gen:.1f} c")
    print(f"только в эталоне: {len(only_ref)}; только в модели: {len(only_gen)}")
    if only_ref:
        print("   примеры (эталон):", only_ref[:5])
    if only_gen:
        print("   примеры (модель):", only_gen[:5])
    print(f"расхождений по массе: {len(mass_diff)}")
    print(
        f"round-trip: проверено {rt['checked']:,}; ошибок строк {rt['bad_string']}, "
        f"массы {rt['bad_mass']}, восстановления H {rt['bad_h']}"
    )

    if a.json:
        payload = {
            "env": {
                "python": sys.version.split()[0],
                "numpy": np.__version__,
                "platform": platform.platform(),
            },
            "params": {"max_mass": a.max_mass, "halogen_cap": cap, "bounds": bounds},
            "independent_count": len(ref),
            "generator_count": len(gen),
            "only_in_reference": only_ref[:50],
            "only_in_generator": only_gen[:50],
            "mass_mismatches": len(mass_diff),
            "roundtrip": rt,
        }
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
        print(f"результаты записаны: {a.json}")


if __name__ == "__main__":
    main()
