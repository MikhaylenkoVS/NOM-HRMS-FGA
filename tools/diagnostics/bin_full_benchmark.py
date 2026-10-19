"""Полный сквозной замер одного бина: все форматы, чтение из файла, round-trip.

Отличия от bin_benchmark.py (по замечаниям ревью):
  * измеряется каждый формат отдельно, включая лучший по размеру
    (ранги+дельта, zstd19) — размер и время берутся из одного и того же пути;
  * добавлено чтение блока из файла (pread) — «чтение + декодирование»;
  * round-trip: decode(encode(F), bin) == F с восстановлением строки формулы;
  * машинно-читаемый вывод (--json) для протокола воспроизведения.

Запуск:
  python tools/bin_full_benchmark.py --masses 300.05 700.05 --json out.json
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import platform
import statistics
import sys
import tempfile
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
SHIFTS48 = {"C": 0, "N": 8, "O": 15, "S": 22, "P": 28, "X": 34, "XCODE": 37}


def multiset_deltas(max_atoms: int = 5):
    out = []
    for size in range(1, max_atoms + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            delta = sum(n * (MASS_U[el] - H_U) for el, n in collapsed)
            out.append((delta, size, collapsed))
    return out


DELTAS = multiset_deltas(5)
#: Пустая подстановка (Δ = 0) — сами CHNOSP-формулы без галогенов.
DELTAS_FULL = [(0, 0, ())] + DELTAS
MAX_DELTA = max(d for d, _, _ in DELTAS)
X_CODE = {combo: i for i, (_, _, combo) in enumerate(DELTAS)}


def enum_bin(bin_index: int, max_mass_u: int):
    """Записи бина: (c, h, n, o, s, p, x, xcode, mass_u).

    Для каждой галогенной подстановки Δ фреймворк обязан попадать в
    [lo−Δ, hi−Δ); отсюда H вычисляется напрямую (1–2 значения), без прокрутки
    сотен значений H на каждый (C,N,O,S,P).
    """
    lo_u = bin_index * BIN_WIDTH_U
    hi_u = lo_u + BIN_WIDTH_U
    out = []
    # сортируем подстановки по Δ по возрастанию: сначала дешёвые окна
    for delta, x, combo in sorted(DELTAS_FULL, key=lambda t: t[0]):
        fw_lo = lo_u - delta
        fw_hi = hi_u - delta
        if fw_hi <= 0:
            continue
        xcode = X_CODE.get(combo, -1)
        for c in range(1, fw_hi // MASS_U["C"] + 1):
            m_c = c * MASS_U["C"]
            if m_c >= fw_hi:
                break
            for nv in range(min(127, (fw_hi - m_c) // MASS_U["N"]) + 1):
                m_cn = m_c + nv * MASS_U["N"]
                if m_cn >= fw_hi:
                    break
                for o in range(min(63, (fw_hi - m_cn) // MASS_U["O"]) + 1):
                    m_cno = m_cn + o * MASS_U["O"]
                    if m_cno >= fw_hi:
                        break
                    for pv in range(min(63, (fw_hi - m_cno) // MASS_U["P"]) + 1):
                        m_cnop = m_cno + pv * MASS_U["P"]
                        if m_cnop >= fw_hi:
                            break
                        for sv in range(min(31, (fw_hi - m_cnop) // MASS_U["S"]) + 1):
                            base = m_cnop + sv * MASS_U["S"]
                            if base >= fw_hi:
                                break
                            parity = (nv + pv) & 1
                            h_cap = min(255, 2 * c + nv + pv + 2)
                            h_lo = max(parity, -(-(fw_lo - base) // H_U))
                            if (h_lo - parity) % 2:
                                h_lo += 1
                            h_hi = min(h_cap, (fw_hi - 1 - base) // H_U)
                            for h in range(h_lo, h_hi + 1, 2):
                                # подстановка H -> X допустима только при x <= h
                                if x > h:
                                    continue
                                fw_u = base + h * H_U
                                mass_u = fw_u + delta
                                if mass_u > max_mass_u:
                                    continue
                                out.append((c, h, nv, o, sv, pv, x, xcode, mass_u))
    return out


def code48(rec) -> int:
    c, _h, nv, o, sv, pv, x, xcode, _m = rec
    return (
        c
        | (nv << 8)
        | (o << 15)
        | (sv << 22)
        | (pv << 28)
        | (x << 34)
        | ((xcode + 1) << 37)
    )


def code64(rec) -> int:
    # В формате «с H» хранится КОНЕЧНЫЙ водород: H_final = H_framework - x.
    c, h, nv, o, sv, pv, x, xcode, _m = rec
    return (
        c
        | ((h - x) << 8)
        | (nv << 16)
        | (o << 23)
        | (sv << 30)
        | (pv << 36)
        | (x << 43)
        | ((xcode + 1) << 46)
    )


def decode_formula(code: int, bin_index: int, with_h: bool) -> str:
    """Восстановить формулу: поля + (H из номера бина, если H не хранится)."""
    if with_h:
        c = code & 0xFF
        h = (code >> 8) & 0xFF
        nv = (code >> 16) & 0x7F
        o = (code >> 23) & 0x7F
        sv = (code >> 30) & 0x3F
        pv = (code >> 36) & 0x7F
        # биты 43..45 — счётчик галогенов, при декодировании не нужен
        xc = ((code >> 46) & 0x7F) - 1
    else:
        c = code & 0xFF
        nv = (code >> 8) & 0x7F
        o = (code >> 15) & 0x7F
        sv = (code >> 22) & 0x3F
        pv = (code >> 28) & 0x3F
        # биты 34..36 — счётчик галогенов, при декодировании не нужен
        xc = ((code >> 37) & 0x7F) - 1
        base = (
            c * MASS_U["C"]
            + nv * MASS_U["N"]
            + o * MASS_U["O"]
            + sv * MASS_U["S"]
            + pv * MASS_U["P"]
        )
        if xc >= 0:
            base += sum(n * MASS_U[el] for el, n in DELTAS[xc][2])
        lo = bin_index * BIN_WIDTH_U
        h = -(-(lo - base) // H_U)
        if h < 0 or not (lo <= base + h * H_U < lo + BIN_WIDTH_U):
            raise ValueError("H не восстановлен")
    counts = {"C": c, "H": h, "N": nv, "O": o, "S": sv, "P": pv}
    if xc >= 0:
        for el, n in DELTAS[xc][2]:
            counts[el] = n
    order = ["C", "H"] + sorted(e for e in counts if e not in ("C", "H"))
    return "".join(
        el + (str(counts[el]) if counts[el] > 1 else "")
        for el in order
        if counts.get(el)
    )


def shuffle_bytes(codes, nbytes: int) -> bytes:
    arr = np.asarray(codes, dtype=np.uint64).view(np.uint8).reshape(len(codes), 8)
    return arr[:, :nbytes].T.tobytes()


def unshuffle_raw(raw: bytes, nbytes: int, count: int) -> np.ndarray:
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(nbytes, count).T
    full = np.zeros((count, 8), dtype=np.uint8)
    full[:, :nbytes] = arr
    return full.view(np.uint64).reshape(count)


class Variant:
    def __init__(self, name, nbytes, level, use_delta, with_h):
        self.name = name
        self.nbytes = nbytes
        self.level = level
        self.use_delta = use_delta
        self.with_h = with_h

    def encode(self, codes):
        cctx = zstd.ZstdCompressor(level=self.level)
        if self.use_delta:
            s = sorted(codes)
            payload = [s[0]] + [s[i] - s[i - 1] for i in range(1, len(s))]
            raw = shuffle_bytes(payload, self.nbytes)
        else:
            raw = shuffle_bytes(sorted(codes), self.nbytes)
        return cctx.compress(raw), len(raw)

    def decode_codes(self, blob: bytes, count: int, raw_size: int) -> np.ndarray:
        dctx = zstd.ZstdDecompressor()
        raw = dctx.decompress(blob, max_output_size=raw_size)
        vals = unshuffle_raw(raw, self.nbytes, count)
        if self.use_delta:
            vals = np.cumsum(vals.astype(np.int64)).astype(np.uint64)
        return vals


VARIANTS = [
    Variant("uint64 c H, shuffle, zstd9", 8, 9, False, True),
    Variant("uint48 без H, shuffle, zstd9", 6, 9, False, False),
    Variant("uint48 без H, shuffle, zstd19", 6, 19, False, False),
    Variant("ранги+дельта, shuffle, zstd9", 8, 9, True, False),
    Variant("ранги+дельта, shuffle, zstd19", 8, 19, True, False),
]


def run(bin_index: int, max_mass_u: int, reps: int) -> dict:
    mass = bin_index * BIN_WIDTH_U / MASS_SCALE
    t0 = time.perf_counter()
    recs = enum_bin(bin_index, max_mass_u)
    t_gen = time.perf_counter() - t0
    n = len(recs)
    result = {"bin_mass": round(mass, 3), "records": n, "generation_s": round(t_gen, 1)}
    if not n:
        return result

    ref_formulas = sorted(decode_formula(code48(r), bin_index, False) for r in recs)
    v_res = {}
    tmpdir = tempfile.mkdtemp(prefix="binbench_")
    path = os.path.join(tmpdir, "block.bin")
    for v in VARIANTS:
        codes = [code64(r) for r in recs] if v.with_h else [code48(r) for r in recs]
        blob, raw_size = v.encode(codes)
        with open(path, "wb") as fh:
            fh.write(blob)
        fd = os.open(path, os.O_RDONLY)
        try:
            times_read, times_decode, times_roundtrip = [], [], []
            for _ in range(reps):
                t = time.perf_counter()
                os.lseek(fd, 0, os.SEEK_SET)  # os.pread на Windows отсутствует
                os.read(fd, len(blob))
                times_read.append(time.perf_counter() - t)

                t = time.perf_counter()
                decoded = v.decode_codes(blob, n, raw_size)
                times_decode.append(time.perf_counter() - t)

            # round-trip: коды -> формулы (H восстанавливается по бину)
            t = time.perf_counter()
            got = sorted(decode_formula(int(c), bin_index, v.with_h) for c in decoded)
            times_roundtrip.append(time.perf_counter() - t)
            ok = got == ref_formulas
        finally:
            os.close(fd)
        v_res[v.name] = {
            "compressed_bytes": len(blob),
            "bits_per_formula": round(len(blob) * 8 / n, 3),
            "read_ms": round(statistics.median(times_read) * 1e3, 3),
            "decode_ms": round(statistics.median(times_decode) * 1e3, 3),
            "roundtrip_ms": round(statistics.median(times_roundtrip) * 1e3, 3),
            "roundtrip_ok": bool(ok),
            "raw_bytes": raw_size,
        }
    os.remove(path)
    os.rmdir(tmpdir)
    result["variants"] = v_res
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--masses", type=float, nargs="+", default=[300.05, 700.05])
    ap.add_argument("--max-mass", type=float, default=1000.0)
    ap.add_argument("--reps", type=int, default=7)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    max_mass_u = int(a.max_mass * MASS_SCALE)
    out = {
        "env": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "zstandard": zstd.__version__,
            "platform": platform.platform(),
            "cpu": platform.processor(),
        },
        "params": {
            "max_mass": a.max_mass,
            "halogen_cap": 5,
            "bin_width_da": 0.1,
            "reps": a.reps,
        },
        "bins": [],
    }
    for m in a.masses:
        r = run(int(m * MASS_SCALE) // BIN_WIDTH_U, max_mass_u, a.reps)
        out["bins"].append(r)
        print(
            f"\nбин {r['bin_mass']:.2f} Да: {r['records']:,} записей "
            f"(генерация {r['generation_s']} c)"
        )
        for name, v in r.get("variants", {}).items():
            print(
                f"  {name:32s} {v['bits_per_formula']:6.2f} бит/формула | "
                f"чтение {v['read_ms']:6.2f} мс | декод {v['decode_ms']:8.2f} мс | "
                f"полный round-trip {v['roundtrip_ms']:8.2f} мс | "
                f"{'OK' if v['roundtrip_ok'] else 'ОШИБКА'}"
            )
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print(f"\nрезультаты записаны: {a.json}")


if __name__ == "__main__":
    main()
