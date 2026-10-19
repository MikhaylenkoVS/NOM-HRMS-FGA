"""Уплотнить сжатую базу формул: убрать неиндексированный префикс файла.

Зачем: если сборка запускалась несколько раз, в .fdb мог остаться «хвост»
предыдущего запуска, на который индекс не ссылается (сборка теперь
возобновляемая, но файл мог открыться на дозапись). Данные при этом целы —
индекс покрывает их непрерывно, — однако файл толще необходимого, и проверка
покрытия (сумма блоков == размер файла) не проходит.

Скрипт:
  1. читает индекс и проверяет, что он покрывает файл без дырок;
  2. если есть неиндексированный префикс — переписывает блоки подряд в новый
     файл, сдвигая смещения, и пишет новый индекс;
  3. обновляет манифест (размеры, число блоков, пометка об уплотнении);
  4. проверяет: сумма блоков == размер нового файла.

Запуск:
  python tools/diagnostics/compact_formula_db.py \
      --prefix D:/Temp/User/formula_db_v3/chorsphal_1000_v3
"""

from __future__ import annotations

import argparse
import json
import shutil
import struct
from pathlib import Path

REC = 24  # <IQIII>: bin, offset, comp, raw, count


def read_index(path: Path) -> list[tuple[int, int, int, int, int]]:
    blob = path.read_bytes()
    n = len(blob) // REC
    return [struct.unpack_from("<IQIII", blob, i * REC) for i in range(n)]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prefix", required=True, help="путь без расширения (.fdb/.idx)")
    ap.add_argument("--keep-backup", action="store_true", default=True)
    a = ap.parse_args()

    fdb = Path(a.prefix + ".fdb")
    idx = Path(a.prefix + ".idx")
    man = Path(a.prefix + ".manifest.json")
    if not (fdb.is_file() and idx.is_file()):
        raise SystemExit("нет .fdb или .idx")

    entries = read_index(idx)
    size = fdb.stat().st_size
    comp = sum(e[2] for e in entries)
    first = min(e[1] for e in entries)
    last = max(e[1] + e[2] for e in entries)
    print(f"блоков: {len(entries):,}; сумма блоков: {comp:,} Б; файл: {size:,} Б")
    print(f"первый offset: {first:,}; конец данных: {last:,}")
    if first == 0 and last == size:
        print("уплотнение не требуется: файл ровно покрыт индексом")
        return

    print(f"неиндексированный префикс: {first:,} Б ({first / 1e6:.1f} МБ) — уплотняю")

    tmp = Path(str(fdb) + ".compact")
    new_entries: list[tuple[int, int, int, int, int]] = []
    with open(fdb, "rb") as src, open(tmp, "wb") as dst:
        offset = 0
        for bi, off, c, raw, cnt in sorted(entries, key=lambda e: e[1]):
            src.seek(off)
            blob = src.read(c)
            if len(blob) != c:
                raise SystemExit(f"блок {bi}: прочитано {len(blob)} вместо {c}")
            dst.write(blob)
            new_entries.append((bi, offset, c, raw, cnt))
            offset += c
        new_size = offset

    assert new_size == comp, (new_size, comp)

    if a.keep_backup:
        bak = Path(str(fdb) + ".with_prefix.bak")
        if not bak.exists():
            shutil.copy2(fdb, bak)
            print(f"резервная копия исходного файла: {bak}")

    tmp.replace(fdb)
    new_entries.sort(key=lambda e: e[0])
    with open(idx, "wb") as ih:
        for e in new_entries:
            ih.write(struct.pack("<IQIII", *e))

    if man.is_file():
        m = json.loads(man.read_text(encoding="utf-8"))
        m["fdb_bytes"] = new_size
        m["index_bytes"] = idx.stat().st_size
        m["blocks"] = len(new_entries)
        m["compacted"] = {
            "removed_prefix_bytes": first,
            "note": "удалён неиндексированный префикс предыдущего запуска; "
            "смещения блоков пересчитаны",
        }
        man.write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")

    # контроль: сумма блоков нового индекса == размер файла
    check = read_index(idx)
    assert (
        sum(e[2] for e in check)
        == fdb.stat().st_size
        == max(e[1] + e[2] for e in check)
    )
    print(f"готово: {fdb.stat().st_size:,} Б; блоков {len(check):,}; покрытие точное")


if __name__ == "__main__":
    main()
