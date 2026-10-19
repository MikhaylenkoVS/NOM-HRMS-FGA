"""Замер сжатия и стоимости запроса на отдельных бинах 0.1 Да.

Генерирует содержимое одного бина (формулы, чья КОНЕЧНАЯ масса попадает в бин),
и измеряет:
  * размер при разных представлениях (uint64 c H / uint48 без H / ранги+дельта);
  * разбор стоимости запроса по этапам: запись+чтение, декомпрессия,
    обратный shuffle, распаковка, восстановление H, расчёт массы, фильтр.

Запуск: python tools/bin_benchmark.py --masses 300.05 500.05 700.05 900.05
"""

from __future__ import annotations

import argparse
import itertools
import statistics
import time
import zstandard as zstd

import numpy as np

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


def multiset_deltas(max_atoms: int):
    out = []
    for size in range(1, max_atoms + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            delta = sum(n * (MASS_U[el] - H_U) for el, n in collapsed)
            out.append((delta, size))
    return out


DELTAS = multiset_deltas(5)
MAX_DELTA = max(d for d, _ in DELTAS)


def enum_bin(bin_index: int, max_mass_u: int):
    """Записи (c,h,n,o,s,p,halogen_size,halogen_code,mass_u) для бина."""
    lo_u = bin_index * BIN_WIDTH_U
    hi_u = lo_u + BIN_WIDTH_U
    out = []
    c_max = hi_u // MASS_U["C"]
    for c in range(1, c_max + 1):
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
                        base_u = m_cnop + sv * MASS_U["S"]
                        if base_u >= hi_u:
                            break
                        h_cap = min(
                            255, 2 * c + nv + pv + 2, (max_mass_u - base_u) // H_U
                        )
                        parity = (nv + pv) & 1
                        # нужны фреймворки, которые с добавкой Δ попадают в бин
                        for h in range(parity, h_cap + 1, 2):
                            fw_u = base_u + h * H_U
                            if fw_u >= hi_u:
                                break
                            if fw_u < lo_u - MAX_DELTA:
                                continue
                            for delta, x in DELTAS:
                                if x > h:
                                    continue
                                mass_u = fw_u + delta
                                if lo_u <= mass_u < hi_u and mass_u <= max_mass_u:
                                    out.append((c, h, nv, o, sv, pv, x, mass_u))
                            if (lo_u - fw_u) <= 0:
                                # фреймворк уже в бине (x = 0)
                                out.append((c, h, nv, o, sv, pv, 0, fw_u))
    return out


def pack_v1(rec) -> int:
    c, h, n, o, s, p, _, _ = rec
    return c | (h << 8) | (n << 16) | (o << 23) | (s << 30) | (p << 36)


def shuffle_bytes(codes, nbytes: int) -> bytes:
    arr = np.asarray(codes, dtype=np.uint64).view(np.uint8).reshape(len(codes), 8)
    return arr[:, :nbytes].T.tobytes()


def unshuffle(blob: bytes, nbytes: int, count: int) -> np.ndarray:
    arr = np.frombuffer(blob, dtype=np.uint8).reshape(nbytes, count).T
    full = np.zeros((count, 8), dtype=np.uint8)
    full[:, :nbytes] = arr
    return full.view(np.uint64).reshape(count)


def bench_bin(bin_index: int, max_mass_u: int, reps: int = 20) -> None:
    mass = bin_index * BIN_WIDTH_U / MASS_SCALE
    t0 = time.perf_counter()
    recs = enum_bin(bin_index, max_mass_u)
    t_gen = time.perf_counter() - t0
    n = len(recs)
    if not n:
        print(f"бин {mass + 0.05:.2f} Да: пусто")
        return

    # ключ без H: (c, n, o, s, p, x) — как в uint48-представлении
    codes48 = []
    for c, _h, nv, o, sv, pv, x, _m in recs:
        codes48.append(c | (nv << 8) | (o << 15) | (sv << 22) | (pv << 28) | (x << 34))
    codes64 = [pack_v1(r) for r in recs]
    ranks = sorted(codes48)
    deltas = [ranks[0]] + [ranks[i] - ranks[i - 1] for i in range(1, n)]

    cctx9 = zstd.ZstdCompressor(level=9)
    cctx19 = zstd.ZstdCompressor(level=19)
    comp = {
        "uint64 c H, shuffle, zstd9": len(
            cctx9.compress(shuffle_bytes(sorted(codes64), 8))
        ),
        "uint48 без H, shuffle, zstd9": len(cctx9.compress(shuffle_bytes(ranks, 6))),
        "uint48 без H, shuffle, zstd19": len(cctx19.compress(shuffle_bytes(ranks, 6))),
        "ранги+дельта, shuffle, zstd9": len(cctx9.compress(shuffle_bytes(deltas, 8))),
        "ранги+дельта, shuffle, zstd19": len(cctx19.compress(shuffle_bytes(deltas, 8))),
    }
    print(f"\nбин {mass + 0.05:.2f} Да: {n:,} записей (генерация {t_gen:.1f} c)")
    for name, size in comp.items():
        print(f"   {name:34s} {size/1e3:9.1f} КБ = {size*8/n:6.2f} бит/формула")

    # ── Стоимость запроса: по этапам ───────────────────────────────────────
    blob = cctx9.compress(shuffle_bytes(ranks, 6))
    stages = {
        "декомпрессия": [],
        "обратный shuffle": [],
        "распаковка+H+масса": [],
        "фильтр ppm": [],
    }
    dctx = zstd.ZstdDecompressor()
    lo_u = bin_index * BIN_WIDTH_U
    target_u = lo_u + BIN_WIDTH_U // 2  # «наблюдаемая» масса в центре бина
    tol_u = int(target_u * 5e-6)  # 5 ppm
    for _ in range(reps):
        t = time.perf_counter()
        raw = dctx.decompress(blob, max_output_size=n * 6)
        stages["декомпрессия"].append(time.perf_counter() - t)

        t = time.perf_counter()
        arr = np.frombuffer(raw, dtype=np.uint8).reshape(6, n).T
        full = np.zeros((n, 8), dtype=np.uint8)
        full[:, :6] = arr
        codes = full.view(np.uint64).reshape(n)
        stages["обратный shuffle"].append(time.perf_counter() - t)

        t = time.perf_counter()
        c = (codes & 0xFF).astype(np.int64)
        nv = ((codes >> 8) & 0x7F).astype(np.int64)
        o = ((codes >> 15) & 0x7F).astype(np.int64)
        s = ((codes >> 22) & 0x3F).astype(np.int64)
        p = ((codes >> 28) & 0x3F).astype(np.int64)
        x = ((codes >> 34) & 0x7).astype(np.int64)
        base = (
            c * MASS_U["C"]
            + nv * MASS_U["N"]
            + o * MASS_U["O"]
            + s * MASS_U["S"]
            + p * MASS_U["P"]
        )
        h = np.ceil((lo_u - base) / H_U).astype(np.int64)
        mass = base + h * H_U
        stages["распаковка+H+масса"].append(time.perf_counter() - t)

        t = time.perf_counter()
        sel = np.abs(mass - target_u) <= tol_u
        stages["фильтр ppm"].append(time.perf_counter() - t)

    print("   стоимость одного запроса по этапам (мс, медиана):")
    for name, vals in stages.items():
        print(f"      {name:24s} {statistics.median(vals)*1e3:8.2f}")
    total_ms = sum(statistics.median(v) for v in stages.values()) * 1e3
    print(f"      {'ИТОГО':24s} {total_ms:8.2f}")
    print(f"   кандидатов после ppm-фильтра: {int(sel.sum()):,}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--masses", type=float, nargs="+", default=[300.05, 500.05, 700.05, 900.05]
    )
    ap.add_argument("--max-mass", type=float, default=1000.0)
    ap.add_argument("--reps", type=int, default=20)
    a = ap.parse_args()
    max_mass_u = int(a.max_mass * MASS_SCALE)
    for m in a.masses:
        bench_bin(int(m * MASS_SCALE) // BIN_WIDTH_U, max_mass_u, a.reps)


if __name__ == "__main__":
    main()
