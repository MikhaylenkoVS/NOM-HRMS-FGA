"""Проверка собранной базы формул v3 (CHNOSPHal): структура и корректность.

Проверки:
  1. файлы на месте, размер индекса кратен 24, бины уникальны и упорядочены;
  2. смещения блоков непрерывны, сумма сжатых размеров = размер .fdb;
  3. случайные блоки декодируются: число записей, строгое возрастание кодов;
  4. для каждой записи восстанавливается H, масса попадает в бин, чётность
     замкнутой оболочки верна, DBE целое и >= 0, H >= числа галогенов;
  5. НЕЗАВИСИМАЯ перепроверка нескольких бинов: полный перебор формул бина
     отдельной реализацией и сравнение множеств (C,N,O,S,P,H,X) поэлементно.

Запуск:
  python tools/diagnostics/verify_formula_db_v3.py --prefix /path/db --sample 30 --bins 3
"""

from __future__ import annotations

import argparse
import itertools
import struct
from pathlib import Path

import numpy as np
import zstandard as zstd

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
H_U = MASS_U["H"]
HALO = ("F", "Cl", "Br", "I")


def multisets(cap: int):
    """(Δ, код, x, состав) — независимая реализация таблицы подстановок."""
    out = [(0, 0, 0, ())]
    for size in range(1, cap + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            if collapsed in (c for _, _, _, c in out):
                continue
            delta = sum(n * (MASS_U[el] - H_U) for el, n in collapsed)
            out.append((delta, len(out), size, collapsed))
    return out


MS = multisets(5)
X_OF = {xc: xx for _, xc, xx, _ in MS}
DELTA_OF = {xc: dd for dd, xc, _, _ in MS}


def decode_block(blob: bytes, count: int) -> np.ndarray:
    raw = zstd.ZstdDecompressor().decompress(blob)
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, count).T
    padded = np.zeros((count, 8), dtype=np.uint8)
    padded[:, :6] = arr
    return np.cumsum(padded.view(np.uint64).reshape(count))


def read_index(prefix: str):
    idx = Path(prefix + ".idx").read_bytes()
    assert len(idx) % 24 == 0, "размер индекса не кратен 24"
    return [struct.unpack_from("<IQIII", idx, i * 24) for i in range(len(idx) // 24)]


def brute_force_bin(bi: int, cap: int, max_mass_u: int) -> set[tuple]:
    """Независимый перебор бина: все (C,N,O,S,P,H,X-код).

    Отличие от сборщика: H не перебирается циклом, а решается арифметически
    (для данного состава в 0.1 Да-бин попадает не более одного H, так как
    масса H больше ширины бина). Циклы ограничены массой.
    """
    lo_u = bi * BIN_WIDTH_U
    hi_u = lo_u + BIN_WIDTH_U
    out: set[tuple] = set()
    for delta, xcode, x, _comp in multisets(cap):
        fw_hi = hi_u - delta
        fw_lo = lo_u - delta
        if fw_hi <= 0:
            continue
        for c in range(1, fw_hi // MASS_U["C"] + 1):
            mc = c * MASS_U["C"]
            for nv in range(0, (fw_hi - mc) // MASS_U["N"] + 1):
                mn = mc + nv * MASS_U["N"]
                for o in range(0, (fw_hi - mn) // MASS_U["O"] + 1):
                    mo = mn + o * MASS_U["O"]
                    for pv in range(0, (fw_hi - mo) // MASS_U["P"] + 1):
                        mp = mo + pv * MASS_U["P"]
                        for sv in range(0, (fw_hi - mp) // MASS_U["S"] + 1):
                            fw_base = mp + sv * MASS_U["S"]
                            # h — водород ФРЕЙМВОРКА: масса =
                            # fw_base + h*H_U + delta; h >= x (есть что
                            # замещать), h ≡ N+P (mod 2), h <= 2C+2+N+P.
                            # ВАЖНО: fw_lo/fw_hi уже сдвинуты на Δ, поэтому
                            # вычитать delta здесь нельзя.
                            h_lo = -(-(fw_lo - fw_base) // H_U)
                            h_hi = (fw_hi - 1 - fw_base) // H_U
                            for h in range(max(0, h_lo), h_hi + 1):
                                mass_u = fw_base + h * H_U + delta
                                if mass_u > max_mass_u or h < x:
                                    continue
                                if (h - (nv + pv)) % 2:
                                    continue
                                dbe2 = 2 * c + 2 + nv + pv - h
                                if dbe2 < 0:
                                    continue
                                out.add((c, nv, o, sv, pv, h, xcode))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--sample", type=int, default=30, help="блоков на round-trip")
    ap.add_argument("--bins", type=int, default=3, help="бинов на полный перебор")
    ap.add_argument("--cap", type=int, default=5)
    ap.add_argument("--max-mass", type=float, default=1000.0)
    a = ap.parse_args()

    prefix = a.prefix
    fdb_path = Path(prefix + ".fdb")
    entries = read_index(prefix)
    size = fdb_path.stat().st_size
    max_mass_u = int(a.max_mass * MASS_SCALE)
    fails: list[str] = []

    print(f"блоков: {len(entries)}, .fdb: {size / 1e6:.1f} МБ")
    records = sum(e[4] for e in entries)

    # 1-2. структура и покрытие файла блоками
    bins = [e[0] for e in entries]
    ok_struct = bins == sorted(set(bins))
    # Блоки пишутся по мере готовности, поэтому в индексе (отсортированном по
    # бинам) смещения не обязаны возрастать. Инвариант: интервалы
    # [offset, offset + comp) не пересекаются и ровно покрывают файл.
    ok_offsets = True
    expected = 0
    for lo, hi in sorted((e[1], e[1] + e[2]) for e in entries):
        if lo != expected:
            ok_offsets = False
            fails.append(f"блоки не покрывают файл: ожидалось {expected}, есть {lo}")
            break
        expected = hi
    if expected != size:
        ok_offsets = False
        fails.append(f"блоки покрывают {expected} байт, файл {size} байт")
    print(
        f"структура индекса: {'OK' if ok_struct else 'ОШИБКА'}; "
        f"смещения: {'OK' if ok_offsets else 'ОШИБКА'}"
    )
    print(f"записей всего: {records:,}".replace(",", " "))

    # 3-4. round-trip случайных блоков
    rng = np.random.default_rng(42)
    sample_idx = rng.choice(
        len(entries), size=min(a.sample, len(entries)), replace=False
    )
    fdb = open(fdb_path, "rb")
    checked = 0
    for i in sample_idx:
        bi, o, comp, raw, cnt = entries[int(i)]
        fdb.seek(o)
        codes = decode_block(fdb.read(comp), cnt)
        if len(codes) != cnt:
            fails.append(f"бин {bi}: записей {len(codes)} вместо {cnt}")
            continue
        if cnt > 1 and np.any(np.diff(codes.astype(np.int64)) <= 0):
            fails.append(f"бин {bi}: коды не возрастают")
            continue
        lo_u = bi * BIN_WIDTH_U
        for code in codes[rng.choice(cnt, size=min(200, cnt), replace=False)]:
            c = int(code & 0xFF)
            nv = int((code >> 8) & 0x7F)
            oo = int((code >> 15) & 0x7F)
            sv = int((code >> 22) & 0x3F)
            pv = int((code >> 28) & 0x7F)
            xcode = int((code >> 35) & 0x7F)
            x = X_OF.get(xcode)
            delta = DELTA_OF.get(xcode)
            if x is None or delta is None:
                fails.append(f"бин {bi}: неизвестный код подстановки {xcode}")
                continue
            fw_base = (
                c * MASS_U["C"]
                + nv * MASS_U["N"]
                + oo * MASS_U["O"]
                + pv * MASS_U["P"]
                + sv * MASS_U["S"]
            )
            lo_u = bi * BIN_WIDTH_U
            hi_u = lo_u + BIN_WIDTH_U
            found = False
            for h in range(
                max(0, (lo_u - fw_base - delta) // H_U),
                (hi_u - fw_base - delta) // H_U + 2,
            ):
                m = fw_base + h * H_U + delta
                if not (lo_u <= m < hi_u) or m > max_mass_u:
                    continue
                if h < x or (h - (nv + pv)) % 2 or 2 * c + 2 + nv + pv - h < 0:
                    continue
                found = True
                break
            if not found:
                fails.append(f"бин {bi}: не восстанавливается (код {code})")
        checked += 1
    print(f"round-trip: проверено блоков {checked}, ошибок {len(fails)}")

    # 5. независимый перебор нескольких бинов
    if a.bins > 0:
        cand = [e for e in entries if e[4] < 400_000]
        pick = rng.choice(len(cand), size=min(a.bins, len(cand)), replace=False)
        for i in pick:
            bi, o, comp, raw, cnt = cand[int(i)]
            fdb.seek(o)
            codes = decode_block(fdb.read(comp), cnt)
            got = set()
            for code in codes:
                c = int(code & 0xFF)
                nv = int((code >> 8) & 0x7F)
                oo = int((code >> 15) & 0x7F)
                sv = int((code >> 22) & 0x3F)
                pv = int((code >> 28) & 0x7F)
                xcode = int((code >> 35) & 0x7F)
                x = {xc: xx for _, xc, xx, _ in multisets(a.cap)}[xcode]
                delta = {xc: dd for dd, xc, _, _ in multisets(a.cap)}[xcode]
                fw_base = (
                    c * MASS_U["C"]
                    + nv * MASS_U["N"]
                    + oo * MASS_U["O"]
                    + pv * MASS_U["P"]
                    + sv * MASS_U["S"]
                )
                lo_u = bi * BIN_WIDTH_U
                h = None
                for cand_h in range(0, 256):
                    m = fw_base + cand_h * H_U + delta
                    if lo_u <= m < lo_u + BIN_WIDTH_U and m <= max_mass_u:
                        h = cand_h
                        break
                got.add((c, nv, oo, sv, pv, h, xcode))
            ref = brute_force_bin(bi, a.cap, max_mass_u)
            only_db = got - ref
            only_ref = ref - got
            status = "OK" if not only_db and not only_ref else "РАСХОЖДЕНИЕ"
            print(
                f"бин {bi} ({bi / 10:.1f} Да): записей {cnt}, эталон {len(ref)}, "
                f"{status} (лишних {len(only_db)}, пропущено {len(only_ref)})"
            )
            if only_db:
                fails.append(f"бин {bi}: {len(only_db)} лишних записей")
            if only_ref:
                fails.append(f"бин {bi}: {len(only_ref)} пропущенных записей")

    print()
    if fails:
        print(f"ИТОГ: ОШИБКИ ({len(fails)})")
        for f in fails[:10]:
            print("  -", f)
        raise SystemExit(1)
    print("ИТОГ: все проверки пройдены")


if __name__ == "__main__":
    main()
