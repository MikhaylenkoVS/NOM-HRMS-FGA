"""Контролируемый бенчмарк сжатия: одинаковые формулы, бины, порядок, схема блоков.

Отвечает на замечания к предыдущему отчёту:
  * один и тот же набор формул и одинаковое разбиение на бины 0.1 Да;
  * сравниваются только варианты кодирования (H явно/неявно, ширина записи,
    per-bin vs единый поток, shuffle, уровень zstd);
  * проверяются: число уникальных формул, отсутствие дублей, обратимость
    декодирования, статистика числа записей на бин (median/p95/max).

Запуск: python tools/compression_benchmark.py --lo 300 --hi 320
"""

from __future__ import annotations

import argparse
import sys
import time
import zstandard as zstd

sys.path.insert(0, "tools")
sys.path.insert(0, ".")

import numpy as np  # noqa: E402

from compression_experiment import enum_window, pack_v1, pack_v2, rank_v2  # noqa: E402

BIN_WIDTH_U = 10_000_000_000
MASS_U_H = 100_782_503_223


def shuffle_fixed(codes: list[int], nbytes: int) -> bytes:
    arr = np.asarray(codes, dtype=np.uint64).view(np.uint8).reshape(len(codes), 8)
    return arr[:, :nbytes].T.tobytes()


def unshuffle_fixed(blob: bytes, nbytes: int, count: int) -> np.ndarray:
    arr = np.frombuffer(blob, dtype=np.uint8).reshape(nbytes, count).T
    full = np.zeros((count, 8), dtype=np.uint8)
    full[:, :nbytes] = arr
    return full.view(np.uint64).reshape(count)


def fmt_size(n: int) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024 or unit == "ГБ":
            return f"{n:.2f} {unit}" if unit != "Б" else f"{n} Б"
        n /= 1024
    return f"{n:.2f} ГБ"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lo", type=float, default=300.0)
    ap.add_argument("--hi", type=float, default=320.0)
    ap.add_argument("--halogens", type=int, default=5)
    a = ap.parse_args()

    t0 = time.perf_counter()
    rows = enum_window(a.lo, a.hi, a.halogens)
    print(
        f"окно {a.lo:.0f}–{a.hi:.0f} Да: {len(rows):,} записей "
        f"({time.perf_counter()-t0:.1f} c генерации)"
    )

    # ── Контроль качества набора ───────────────────────────────────────────
    full = {(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in rows}
    print(f"уникальных полных формул: {len(full):,} (дублей: {len(rows)-len(full):,})")

    by_bin: dict[int, list] = {}
    for r in rows:
        by_bin.setdefault(r[7] // BIN_WIDTH_U, []).append(r)
    counts = np.array([len(v) for v in by_bin.values()])
    print(
        f"бинов занято: {len(by_bin):,}; записей на бин: медиана {int(np.median(counts)):,}, "
        f"p95 {int(np.percentile(counts, 95)):,}, максимум {int(counts.max()):,}"
    )

    # уникодубли внутри бина для 6-байтового представления (без H)
    dup_in_bin = 0
    for bi, lst in by_bin.items():
        codes = [pack_v2(r) for r in lst]
        if len(set(codes)) != len(codes):
            dup_in_bin += len(codes) - len(set(codes))
    print(f"дублей кода без H внутри бина: {dup_in_bin}")

    # ── Варианты кодирования (одинаковые формулы и бины) ───────────────────
    v2_codes = [pack_v2(r) for r in rows]

    def per_bin_size(codes_by_bin: dict, nbytes: int, level: int, order: str = "code"):
        total = 0
        cctx = zstd.ZstdCompressor(level=level)
        for bi, lst in sorted(codes_by_bin.items()):
            if order == "code":
                lst = sorted(lst)
            elif order == "rank":
                lst = sorted(lst, key=lambda c: None)  # заглушка
            blob = shuffle_fixed(lst, nbytes)
            total += len(cctx.compress(blob))
        return total

    # бины: одинаковые записи, только разное кодирование
    v1_by_bin = {bi: [pack_v1(r) for r in lst] for bi, lst in by_bin.items()}
    v2_by_bin = {bi: [pack_v2(r) for r in lst] for bi, lst in by_bin.items()}
    rank_by_bin = {bi: [rank_v2(r) for r in lst] for bi, lst in by_bin.items()}
    delta_by_bin = {}
    for bi, lst in rank_by_bin.items():
        s = sorted(lst)
        delta_by_bin[bi] = [s[0]] + [s[i] - s[i - 1] for i in range(1, len(s))]

    n = len(rows)
    variants = [
        (
            "1. uint64 c H, per-bin, shuffle, zstd9  (текущая архитектура)",
            per_bin_size(v1_by_bin, 8, 9),
            n,
        ),
        ("2. uint48 без H, per-bin, shuffle, zstd9", per_bin_size(v2_by_bin, 6, 9), n),
        (
            "3. uint48 без H, ЕДИНЫЙ поток, shuffle, zstd9",
            len(zstd.ZstdCompressor(level=9).compress(shuffle_fixed(v2_codes, 6))),
            n,
        ),
        (
            "4. uint48 без H, per-bin, shuffle, zstd19",
            per_bin_size(v2_by_bin, 6, 19),
            n,
        ),
        (
            "5. uint64 c H, per-bin, БЕЗ shuffle, zstd9",
            sum(
                len(
                    zstd.ZstdCompressor(level=9).compress(
                        np.asarray(sorted(lst), dtype=np.uint64)
                        .view(np.uint8)
                        .tobytes()
                    )
                )
                for lst in v1_by_bin.values()
            ),
            n,
        ),
        (
            "6. ранги+дельта, per-bin, shuffle, zstd9",
            per_bin_size(delta_by_bin, 8, 9),
            n,
        ),
        (
            "7. uint48 c H (8 байт), per-bin, shuffle, zstd9",
            per_bin_size(
                {bi: [pack_v1(r) for r in lst] for bi, lst in by_bin.items()}, 8, 9
            ),
            n,
        ),
    ]

    print(f"\n{'вариант':58s} {'байт':>12s} {'бит/формула':>12s}")
    res = {}
    for name, size, cnt in variants:
        bits = size * 8 / cnt
        res[name[0]] = (size, bits)
        print(f"{name:58s} {size:12,d} {bits:12.2f}")

    # ── Обратимость декодирования (вариант 2) ──────────────────────────────
    bad = 0
    checked = 0
    for bi, lst in list(by_bin.items())[:200]:
        blob = shuffle_fixed(sorted([pack_v2(r) for r in lst]), 6)
        dec = unshuffle_fixed(blob, 6, len(lst))
        src = sorted([pack_v2(r) for r in lst])
        if list(dec) != src:
            bad += 1
        checked += 1
    print(
        f"\nобратимость shuffle/unshuffle (uint48): проверено бинов {checked}, "
        f"ошибок {bad}"
    )

    # ── Проверка восстановления H (все записи) ─────────────────────────────
    bad_h = 0
    for r in rows:
        code = pack_v2(r)
        bi = r[7] // BIN_WIDTH_U
        c = code & 0xFF
        nv = (code >> 8) & 0x7F
        o = (code >> 15) & 0x7F
        s = (code >> 22) & 0x3F
        p = (code >> 28) & 0x3F
        f = (code >> 34) & 0x7
        cl = (code >> 37) & 0x7
        br = (code >> 40) & 0x7
        i = (code >> 43) & 0x7
        base = (
            c * 1_200_000_000_000
            + nv * 1_400_307_400_443
            + o * 1_599_491_461_957
            + s * 3_197_207_117_440
            + p * 3_097_376_199_842
            + f * 1_899_840_316_273
            + cl * 3_496_885_268_200
            + br * 7_891_833_760_000
            + i * 12_690_447_190_000
        )
        lo = bi * BIN_WIDTH_U
        h_calc = -(-(lo - base) // MASS_U_H)  # ceil
        if (
            h_calc < 0
            or not (lo <= base + h_calc * MASS_U_H < lo + BIN_WIDTH_U)
            or h_calc != r[1]
        ):
            bad_h += 1
    print(f"восстановление H по всем {n:,} записям: ошибок {bad_h}")


if __name__ == "__main__":
    main()
