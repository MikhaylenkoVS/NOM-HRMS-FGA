"""Прототип сборки базы CHNOSPHal: uint48 без H + ранги/дельта + shuffle + zstd.

Собирает диапазон масс [--mass-min, --mass-max) при заданном капе галогенов,
параллельно (multiprocessing по диапазонам масс), и печатает ИЗМЕРЕННЫЙ размер
(а не оценку), число записей и время.

Формат (см. docs/formula_db_format_v3_draft.md):
  * запись — 47-битный код без H (C8 | N7 | O7 | S6 | P7 | X_code7), 6 байт;
  * H не хранится, восстанавливается по номеру бина и составу (§3 док.);
  * внутри бина коды сортируются, пишутся первый + разности (дельта);
  * кадр zstd на бин, byte-shuffle перед сжатием;
  * индекс — 24 байта на блок: bin_id u32, offset u64, comp u32, raw u32, count u32.

Запуск:
  python tools/build_halogen_db.py --mass-min 0 --mass-max 300 --halogen-cap 5 \
         --out /d/Temp/User/halodb_test --workers 12
"""

from __future__ import annotations

import argparse
import itertools
import os
import struct
import time
from multiprocessing import Pool
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
HALO = ("F", "Cl", "Br", "I")
H_U = MASS_U["H"]


def multiset_table(cap: int):
    """126 мультимножеств с ≤ cap атомов: (Δ, код 1..125, размер x)."""
    out = [(0, 0, 0)]  # код 0 = без галогенов
    for size in range(1, cap + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            if any(c == collapsed for _, _, c in out):
                continue
            delta = sum(n * (MASS_U[el] - H_U) for el, n in collapsed)
            out.append((delta, len(out), size))
    return out


DELTAS = multiset_table(5)  # (Δ, код, x), код 0 = без галогенов
DELTA_SORTED = sorted(DELTAS, key=lambda t: t[0])
DELTA_BY_CODE = {xcode: delta for delta, xcode, _x in DELTAS}


def bin_codes(bin_index: int, max_mass_u: int, cap: int):
    """Коды (uint64, до 47 бит) всех формул, чья конечная масса в бине."""
    lo_u = bin_index * BIN_WIDTH_U
    hi_u = lo_u + BIN_WIDTH_U
    codes = []
    for delta, xcode, x in DELTA_SORTED:
        if x > cap:
            continue
        fw_hi = hi_u - delta
        fw_lo = lo_u - delta
        if fw_hi <= 0:
            continue
        for c in range(1, fw_hi // MASS_U["C"] + 1):
            m_c = c * MASS_U["C"]
            if m_c >= fw_hi:
                break
            for nv in range(min(127, (fw_hi - m_c) // MASS_U["N"]) + 1):
                m_cn = m_c + nv * MASS_U["N"]
                if m_cn >= fw_hi:
                    break
                for o in range(min(127, (fw_hi - m_cn) // MASS_U["O"]) + 1):
                    m_cno = m_cn + o * MASS_U["O"]
                    if m_cno >= fw_hi:
                        break
                    for pv in range(min(127, (fw_hi - m_cno) // MASS_U["P"]) + 1):
                        m_cnop = m_cno + pv * MASS_U["P"]
                        if m_cnop >= fw_hi:
                            break
                        for sv in range(min(63, (fw_hi - m_cnop) // MASS_U["S"]) + 1):
                            base = m_cnop + sv * MASS_U["S"]
                            if base >= fw_hi:
                                break
                            # h — водород ФРЕЙМВОРКА (до замещения), поэтому
                            # чётность и предел берутся без учёта x:
                            # DBE = (2C+2+N+P-h)/2 целое => h ≡ N+P (mod 2),
                            # DBE >= 0 => h <= 2C+2+N+P.
                            parity = (nv + pv) & 1
                            h_cap = min(255, 2 * c + nv + pv + 2)
                            h_lo = max(parity, -(-(fw_lo - base) // H_U))
                            if (h_lo - parity) % 2:
                                h_lo += 1
                            h_hi = min(h_cap, (fw_hi - 1 - base) // H_U)
                            for h in range(h_lo, h_hi + 1, 2):
                                if x > h:
                                    continue
                                mass_u = base + h * H_U + delta
                                if mass_u > max_mass_u:
                                    continue
                                codes.append(
                                    c
                                    | (nv << 8)
                                    | (o << 15)
                                    | (sv << 22)
                                    | (pv << 28)
                                    | (xcode << 35)
                                )
    return bin_index, codes


def encode_block(codes: list[int], level: int) -> tuple[bytes, int, int]:
    """Дельта по отсортированным кодам, shuffle, zstd. Возвращает (blob, raw, count)."""
    s = sorted(codes)
    if not s:
        return b"", 0, 0
    payload = [s[0]] + [s[i] - s[i - 1] for i in range(1, len(s))]
    arr = np.asarray(payload, dtype=np.uint64).view(np.uint8).reshape(len(payload), 8)
    raw = arr[:, :6].T.tobytes()
    return zstd.ZstdCompressor(level=level).compress(raw), len(raw), len(s)


def decode_block(blob: bytes, count: int) -> np.ndarray:
    """Декодировать блок: 6 байт/запись, дельта по возрастанию."""
    if count == 0:
        return np.zeros(0, dtype=np.uint64)
    raw = zstd.ZstdDecompressor().decompress(blob)
    arr = np.frombuffer(raw, dtype=np.uint8).reshape(-1, count).T  # (count, 6)
    padded = np.zeros((count, 8), dtype=np.uint8)
    padded[:, :6] = arr
    deltas = padded.view(np.uint64).reshape(count)
    return np.cumsum(deltas)


def split_code(code: int) -> tuple[int, int, int, int, int, int]:
    """Код → (C, N, O, S, P, X-код)."""
    return (
        int(code & 0xFF),
        int((code >> 8) & 0x7F),
        int((code >> 15) & 0x7F),
        int((code >> 22) & 0x3F),
        int((code >> 28) & 0x7F),
        int((code >> 35) & 0x7F),
    )


def verify_block(bi: int, blob: bytes, count: int, max_mass_u: int) -> str | None:
    """Проверить один блок (модель: h — водород фреймворка, h >= x)."""
    try:
        codes = decode_block(blob, count)
    except Exception as exc:  # pragma: no cover
        return f"блок {bi}: не декодируется ({exc})"
    if len(codes) != count:
        return f"блок {bi}: записей {len(codes)}, в индексе {count}"
    if count > 1 and np.any(np.diff(codes.astype(np.int64)) <= 0):
        return f"блок {bi}: коды не строго возрастают"
    lo_u = bi * BIN_WIDTH_U
    hi_u = lo_u + BIN_WIDTH_U
    x_of = {xcode: x for _, xcode, x in DELTAS}
    step = max(1, count // 200)
    for code in codes[::step]:
        c, nv, o, sv, pv, xcode = split_code(int(code))
        x = x_of.get(xcode, 0)
        delta = DELTA_BY_CODE.get(xcode, 0)
        fw_base = (
            c * MASS_U["C"]
            + nv * MASS_U["N"]
            + o * MASS_U["O"]
            + pv * MASS_U["P"]
            + sv * MASS_U["S"]
        )
        # h — водород фреймворка: масса = fw_base + h*H_U + delta
        h_lo = -(-(lo_u - fw_base - delta) // H_U)
        h_hi = (hi_u - 1 - fw_base - delta) // H_U
        cands = [h for h in (h_lo, h_lo + 1, h_hi) if h_lo <= h <= h_hi]
        ok = False
        for h in cands:
            if h < 0 or h > 255:
                continue
            mass_u = fw_base + h * H_U + delta
            if not (lo_u <= mass_u < hi_u) or mass_u > max_mass_u:
                continue
            if h < x:
                continue
            if (h - (nv + pv)) % 2:
                continue
            if 2 * c + 2 + nv + pv - h < 0:
                continue
            ok = True
            break
        if not ok:
            return (
                f"блок {bi}: запись не восстанавливается (код {code}: C{c} N{nv} "
                f"O{o} S{sv} P{pv} x{x}, кандидаты H={cands})"
            )
    return None


def build(
    mass_min: float,
    mass_max: float,
    cap: int,
    out_prefix: str,
    workers: int,
    level: int,
    *,
    progress_every: int = 50,
    verify_every: int = 25,
    resume: bool = False,
) -> dict:
    """Собрать базу. Блоки и индекс пишутся сразу — обрыв не теряет прогресс.

    При ``resume=True`` уже собранные бины (по существующему .idx) пропускаются,
    данные дописываются в тот же файл.
    """
    max_mass_u = int(mass_max * MASS_SCALE)
    first_bin = int(mass_min * MASS_SCALE) // BIN_WIDTH_U
    last_bin = max_mass_u // BIN_WIDTH_U
    bins = list(range(first_bin, last_bin + 1))

    t0 = time.perf_counter()
    fdb_path = out_prefix + ".fdb"
    idx_path = out_prefix + ".idx"
    total_records = 0
    total_comp = 0
    blocks_written = 0
    skipped = 0
    verified = 0
    errors: list[str] = []
    pending: list[tuple[int, int, int, int]] = []
    done_bins: set[int] = set()

    # ── Возобновление: читаем уже собранные бины ──────────────────────────
    if resume and Path(idx_path).is_file() and Path(fdb_path).is_file():
        blob = Path(idx_path).read_bytes()
        for i in range(len(blob) // 24):
            bi, off, comp, raw, cnt = struct.unpack_from("<IQIII", blob, i * 24)
            pending.append((bi, off, comp, raw, cnt))
            done_bins.add(bi)
            total_records += cnt
            total_comp += comp
            blocks_written += 1
        print(
            f"  возобновление: уже собранных бинов {len(done_bins)}, "
            f"записей {total_records:,}".replace(",", " "),
            flush=True,
        )
        # Защита от «мусорного» префикса: если файл длиннее, чем покрывают
        # блоки индекса (следы предыдущего запуска), обрезаем его до данных.
        covered = max(off + comp for _, off, comp, _, _ in pending)
        actual = Path(fdb_path).stat().st_size
        if actual > covered:
            with open(fdb_path, "r+b") as fh:
                fh.truncate(covered)
            print(
                f"  ВНИМАНИЕ: файл был длиннее индекса ({actual:,} > {covered:,}); "
                f"лишние {actual - covered:,} Б обрезаны".replace(",", " "),
                flush=True,
            )
        fdb_mode, idx_mode = "ab", "ab"
    else:
        fdb_mode, idx_mode = "wb", "wb"

    first_bin = max(0, int(mass_min * MASS_SCALE) // BIN_WIDTH_U)
    last_bin = max_mass_u // BIN_WIDTH_U
    bins = [b for b in range(first_bin, last_bin + 1) if b not in done_bins]
    print(f"  бинов к сборке: {len(bins):,}".replace(",", " "), flush=True)

    with (
        open(fdb_path, fdb_mode) as fh,
        open(idx_path, idx_mode) as ih,
        Pool(workers) as pool,
    ):
        jobs = [(b, max_mass_u, cap, level) for b in bins]
        for done, (bi, blob, raw_size, count) in enumerate(
            pool.imap_unordered(_bin_worker, jobs, chunksize=4), start=1
        ):
            if not count:
                skipped += 1
            else:
                offset = fh.tell()
                fh.write(blob)
                fh.flush()
                # Индекс пишем сразу: если процесс оборвётся, прогресс не
                # потеряется — смещения останутся валидными (файл append-only).
                ih.write(struct.pack("<IQIII", bi, offset, len(blob), raw_size, count))
                ih.flush()
                pending.append((bi, offset, len(blob), raw_size, count))
                total_records += count
                total_comp += len(blob)
                blocks_written += 1
                if verify_every and blocks_written % verify_every == 0:
                    err = verify_block(bi, blob, count, max_mass_u)
                    verified += 1
                    if err:
                        errors.append(err)
                        print(f"  [ОШИБКА ПРОВЕРКИ] {err}", flush=True)

            if progress_every and done % progress_every == 0:
                el = time.perf_counter() - t0
                rate = total_records / el if el else 0
                left = len(bins) - done
                eta = left / (done / el) if done and el else 0
                print(
                    f"  бинов {done}/{len(bins)} ({done / len(bins) * 100:.1f}%) | "
                    f"записей {total_records:,} | .fdb {fh.tell() / 1e6:.1f} МБ | "
                    f"{rate:,.0f} зап/с | осталось ~{eta / 60:.1f} мин".replace(
                        ",", " "
                    ),
                    flush=True,
                )

    # Сортируем индекс по бину (данные остаются на своих местах).
    pending.sort(key=lambda t: t[0])
    with open(idx_path, "wb") as ih2:
        for bi, offset, comp, raw_size, count in pending:
            ih2.write(struct.pack("<IQIII", bi, offset, comp, raw_size, count))

    elapsed = time.perf_counter() - t0
    result = {
        #: Схема формата (читатель проверяет format_version).
        "format_version": 3,
        "bin_width_u": 10000000000,
        "mass_scale": 100000000000,
        "record_bytes": 6,
        "index_record_bytes": 24,
        "h_derived_from_block": True,
        "elements": ["C", "N", "O", "S", "P", "F", "Cl", "Br", "I"],
        "h_model": "framework H: DBE=(2C+2+N+P-H)/2 >= 0, H = N+P (mod 2), H >= x",
        "index_layout": "<IQIII>: bin, offset, compressed_size, raw_size, records",
        "range_da": [mass_min, mass_max],
        "halogen_cap": cap,
        "blocks": blocks_written,
        "bins_empty": skipped,
        "records": total_records,
        "compressed_bytes": total_comp,
        "index_bytes": os.path.getsize(idx_path),
        "fdb_bytes": os.path.getsize(fdb_path),
        "bits_per_formula": (
            round(total_comp * 8 / total_records, 3) if total_records else 0
        ),
        "seconds": round(elapsed, 1),
        "records_per_second": round(total_records / elapsed, 0) if elapsed else 0,
        "blocks_verified": verified,
        "verification_errors": errors,
        "fdb": fdb_path,
        "idx": idx_path,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    import json

    manifest = out_prefix + ".manifest.json"
    with open(manifest, "w", encoding="utf-8") as mf:
        json.dump(result, mf, ensure_ascii=False, indent=2)
    result["manifest"] = manifest
    return result


def _bin_worker(args):
    """Воркер: собрать и сжать один бин."""
    bi, max_mass_u, cap, level = args
    _, codes = bin_codes(bi, max_mass_u, cap)
    if not codes:
        return bi, b"", 0, 0
    blob, raw_size, count = encode_block(codes, level)
    return bi, blob, raw_size, count


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mass-min", type=float, default=0.0)
    ap.add_argument("--mass-max", type=float, default=300.0)
    ap.add_argument("--halogen-cap", type=int, default=5)
    ap.add_argument("--out", default="halodb_proto")
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--level", type=int, default=9)
    ap.add_argument("--progress-every", type=int, default=50)
    ap.add_argument("--verify-every", type=int, default=25)
    ap.add_argument("--resume", action="store_true", help="продолжить сборку")
    a = ap.parse_args()
    r = build(
        a.mass_min,
        a.mass_max,
        a.halogen_cap,
        a.out,
        a.workers,
        a.level,
        progress_every=a.progress_every,
        verify_every=a.verify_every,
        resume=a.resume,
    )
    print(f"собрано {r['records']:,} записей, блоков {r['blocks']:,}")
    print(
        f"размер .fdb: {r['fdb_bytes']/1e6:.2f} МБ; индекс: {r['index_bytes']/1e3:.1f} КБ"
    )
    print(f"бит/формула: {r['bits_per_formula']:.2f}")
    print(
        f"время: {r['seconds']} c; скорость: {r['records_per_second']:,.0f} записей/с"
    )
    print(
        f"проверено блоков: {r['blocks_verified']}, ошибок: {len(r['verification_errors'])}"
    )
    print(f"манифест: {r['manifest']}")


if __name__ == "__main__":
    main()
