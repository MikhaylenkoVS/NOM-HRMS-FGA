"""Тесты читателя сжатой базы формул формата v3 (CHNOSPHal).

Часть тестов работает на синтетической мини-базе (кодек повторяется в тесте —
это защищает от «зеркальных» ошибок в сборщике и читателе), часть — на реальной
собранной базе, если она доступна (сверка с независимым перебором).
"""

from __future__ import annotations

import itertools
import json
import struct
import sys
from pathlib import Path

import numpy as np
import pytest
import zstandard as zstd

from src.core.formula_db._reader_v3 import (
    BIN_WIDTH_U,
    FORMULA_ELEMENT_ORDER,
    HALO,
    MASS_SCALE,
    MASS_U,
    H_U,
    FormulaDatabaseReaderV3,
    format_formula,
)

# ── Синтетическая база ─────────────────────────────────────────────────────

REAL_MANIFEST = Path("D:/Temp/User/formula_db_v3/chorsphal_1000_v3.manifest.json")
REPO_CHNOSP = Path("data/formula_db/chposp_1000_zstd9_v2.manifest.json")


def _halogen_table(cap: int) -> list[tuple[tuple[str, int], ...]]:
    """Таблица комбинаций галогенов в порядке кодов (как в сборщике)."""
    out: list[tuple[tuple[str, int], ...]] = [()]
    for size in range(1, cap + 1):
        for combo in itertools.combinations_with_replacement(HALO, size):
            collapsed = tuple((el, combo.count(el)) for el in HALO if combo.count(el))
            if collapsed not in out:
                out.append(collapsed)
    return out


def _code_of(c: int, n: int, o: int, s: int, p: int, xcode: int) -> int:
    """Код записи (та же раскладка битов, что в сборщике)."""
    return c | (n << 8) | (o << 15) | (s << 22) | (p << 28) | (xcode << 35)


def _mass_u(
    c: int, n: int, o: int, s: int, p: int, xcode: int, h: int, cap: int
) -> int:
    """Порядок аргументов совпадает с порядком в RECORDS."""
    table = _halogen_table(cap)[xcode]
    delta = sum(cnt * (MASS_U[el] - H_U) for el, cnt in table)
    return (
        c * MASS_U["C"]
        + n * MASS_U["N"]
        + o * MASS_U["O"]
        + s * MASS_U["S"]
        + p * MASS_U["P"]
        + h * H_U
        + delta
    )


def _write_db(tmp_path: Path, records: list[tuple[int, ...]], cap: int = 1) -> Path:
    """Записать мини-базу: records = [(c, n, o, s, p, xcode, h), …]."""
    by_bin: dict[int, list[int]] = {}
    for c, n, o, s, p, xcode, h in records:
        mass_u = _mass_u(c, n, o, s, p, xcode, h, cap)
        by_bin.setdefault(mass_u // BIN_WIDTH_U, []).append(
            _code_of(c, n, o, s, p, xcode)
        )

    fdb = tmp_path / "mini.fdb"
    idx = tmp_path / "mini.idx"
    index_entries = []
    with open(fdb, "wb") as fh:
        for bin_id in sorted(by_bin):
            codes = sorted(by_bin[bin_id])
            payload = [codes[0]] + [
                codes[i] - codes[i - 1] for i in range(1, len(codes))
            ]
            arr = (
                np.asarray(payload, dtype=np.uint64)
                .view(np.uint8)
                .reshape(len(payload), 8)
            )
            raw = arr[:, :6].T.tobytes()
            blob = zstd.ZstdCompressor(level=3).compress(raw)
            offset = fh.tell()
            fh.write(blob)
            index_entries.append((bin_id, offset, len(blob), len(raw), len(codes)))
    with open(idx, "wb") as ih:
        for entry in index_entries:
            ih.write(struct.pack("<IQIII", *entry))

    manifest = tmp_path / "mini.manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "format_version": 3,
                "halogen_cap": cap,
                "records": sum(e[4] for e in index_entries),
                "range_da": [0.0, 1000.0],
                "fdb": str(fdb),
                "idx": str(idx),
            }
        ),
        encoding="utf-8",
    )
    return manifest


# Набор записей: без галогенов, один галоген и комбинация (при cap=2).
# Все записи обязаны удовлетворять модели, иначе читатель справедливо их
# отбросит: h ≡ N+P (mod 2), h ≤ 2C+2+N+P, h ≥ x.
RECORDS = [
    (7, 6, 0, 0, 1, 0, 1),  # C7HN6P     (N+P = 7, поэтому h нечётный)
    (5, 0, 2, 3, 0, 0, 12),  # C5H12O2S3
    (4, 2, 4, 0, 0, 1, 8),  # C4H8O4N2F  (код 1 = F)
    (6, 0, 1, 0, 0, 2, 10),  # C6H10OCl   (код 2 = Cl)
]


class TestSyntheticDb:
    @pytest.fixture()
    def reader(self, tmp_path):
        manifest = _write_db(tmp_path, RECORDS, cap=2)
        r = FormulaDatabaseReaderV3(manifest, cache_size=4)
        yield r
        r.close()

    def test_total_formulas(self, reader):
        assert reader.total_formulas == len(RECORDS)

    def test_format_version(self, reader):
        assert reader.format_version == 3
        assert reader.has_halogens is True

    def test_search_returns_theoretical_masses(self, reader):
        # Читатель возвращает ФАКТИЧЕСКИЙ водород (h − x): в базе хранится
        # каркасный h, а каждый галоген заместил один водород. Масса при этом
        # считается с учётом замещения (в Δ входит −x·m(H)).
        for c, n, o, s, p, xcode, h in RECORDS:
            x_total = sum(count for el, count in _halogen_table(2)[xcode])
            mass = _mass_u(c, n, o, s, p, xcode, h, cap=2) / MASS_SCALE
            hits = reader.search(mass, ppm=0.5, max_results=10)
            assert hits, f"не найдено для {(c, n, o, s, p, xcode, h)}"
            best = min(hits, key=lambda r: abs(r.exact_mass - mass))
            assert abs(best.exact_mass - mass) < 1e-6
            assert best.counts["C"] == c
            assert best.counts["H"] == h - x_total
            assert best.counts["N"] == n
            assert best.counts["O"] == o
            assert best.counts.get("S", 0) == s
            assert best.counts.get("P", 0) == p

    def test_halogen_counts_from_code(self, reader):
        mass = _mass_u(4, 2, 4, 0, 0, 1, 8, cap=2) / MASS_SCALE
        hit = reader.search(mass, ppm=0.2, max_results=1)[0]
        assert hit.counts.get("F", 0) == 1
        assert hit.counts.get("Cl", 0) == 0

    def test_ppm_window_excludes_far(self, reader):
        mass = _mass_u(7, 6, 0, 0, 1, 0, 1, cap=2) / MASS_SCALE
        assert reader.search(mass, ppm=0.01, max_results=5)  # своя масса попадает
        far = reader.search(mass + 5.0, ppm=1.0, max_results=5)
        assert all(abs(h.exact_mass - (mass + 5.0)) < 1e-4 for h in far)

    def test_element_filter(self, reader):
        mass = _mass_u(5, 0, 2, 3, 0, 0, 12, cap=2) / MASS_SCALE
        # без фильтра нужная формула находится
        plain = reader.search(mass, ppm=0.5, max_results=5)
        assert any(h.formula == "C5H12O2S3" for h in plain)
        # фильтр «S = 0» исключает её (в окне остаются только формулы без серы)
        no_sulfur = reader.search(
            mass, ppm=0.5, element_filter={"S": (0, 0)}, max_results=5
        )
        assert all(h.counts["S"] == 0 for h in no_sulfur)
        assert all(h.formula != "C5H12O2S3" for h in no_sulfur)
        # фильтр «S ≥ 3» оставляет её и отбрасывает формулы без серы
        with_sulfur = reader.search(
            mass, ppm=0.5, element_filter={"S": (3, 5)}, max_results=5
        )
        assert any(h.formula == "C5H12O2S3" for h in with_sulfur)
        assert all(h.counts["S"] >= 3 for h in with_sulfur)

    def test_missing_bin_is_empty(self, reader):
        # 500 Да в мини-базе нет вовсе — читатель обязан вернуть пусто, не падать
        assert reader.bin_data(5000) is None
        assert reader.search(500.0, ppm=5.0, max_results=5) == []

    def test_bin_ids_and_bin_data(self, reader):
        assert len(reader.bin_ids(0.0, 1000.0)) == len(RECORDS)
        data = reader.bin_data(reader.bin_ids(0.0, 1000.0)[0])
        assert data is not None and data.mass_u.size >= 1

    def test_manifest_without_version_rejected(self, tmp_path):
        bad = tmp_path / "bad.manifest.json"
        bad.write_text(json.dumps({"halogen_cap": 1, "records": 0}), encoding="utf-8")
        with pytest.raises(ValueError):
            FormulaDatabaseReaderV3(bad)


class TestFormatting:
    def test_hill_like_order(self):
        assert format_formula({"C": 2, "H": 6, "O": 1}) == "C2H6O"
        assert format_formula({"C": 1, "H": 4}) == "CH4"
        assert format_formula({"C": 6, "H": 9, "O": 1, "Cl": 1}) == "C6H9OCl"

    def test_element_order_is_documented(self):
        assert FORMULA_ELEMENT_ORDER == (
            "C",
            "H",
            "O",
            "N",
            "S",
            "P",
            "F",
            "Cl",
            "Br",
            "I",
        )


class TestReaderSelection:
    def test_v3_manifest_selects_v3_reader(self, tmp_path):
        from src.core.spectrum._formula_source import _open_reader_for_manifest

        manifest = _write_db(tmp_path, RECORDS[:2], cap=1)
        reader = _open_reader_for_manifest(manifest)
        assert isinstance(reader, FormulaDatabaseReaderV3)
        reader.close()

    @pytest.mark.skipif(not REPO_CHNOSP.is_file(), reason="нет базовой CHNOSP-базы")
    def test_v2_manifest_still_v2(self):
        from src.core.formula_db._reader import FormulaDatabaseReader
        from src.core.spectrum._formula_source import _open_reader_for_manifest

        reader = _open_reader_for_manifest(REPO_CHNOSP)
        assert isinstance(reader, FormulaDatabaseReader)
        reader.close()


@pytest.mark.skipif(not REAL_MANIFEST.is_file(), reason="нет собранной базы CHNOSPHal")
class TestRealDb:
    """Сверка с независимой реализацией перебора по модели."""

    BINS = (2000, 5112, 7454)

    @pytest.fixture(scope="class")
    @classmethod
    def reader(cls):
        r = FormulaDatabaseReaderV3(REAL_MANIFEST, cache_size=4)
        yield r
        r.close()

    def test_bins_match_brute_force(self, reader):
        tools = Path(__file__).resolve().parents[2] / "tools" / "diagnostics"
        sys.path.insert(0, str(tools))
        from verify_formula_db_v3 import brute_force_bin  # независимый код

        table = _halogen_table(5)
        for bin_id in self.BINS:
            data = reader.bin_data(bin_id)
            mine = set()
            if data is not None:
                for row in data.counts:
                    mine.add(tuple(int(v) for v in row))
            ref = set()
            for c, n, o, s, p, h, xcode in brute_force_bin(
                bin_id, cap=5, max_mass_u=10**14
            ):
                halo = {el: 0 for el in HALO}
                x_total = 0
                for el, cnt in table[xcode]:
                    halo[el] = cnt
                    x_total += cnt
                # перебор отдаёт каркасный h; у читателя фактический H = h − x
                row = {
                    "C": c,
                    "H": h - x_total,
                    "O": o,
                    "N": n,
                    "S": s,
                    "P": p,
                    **halo,
                }
                ref.add(tuple(int(row[el]) for el in FORMULA_ELEMENT_ORDER))
            assert mine == ref, f"бин {bin_id}: расхождение с перебором"

    def test_search_finds_known_formula(self, reader):
        hits = reader.search(200.0, ppm=5.0, max_results=50)
        formulas = {h.formula for h in hits}
        assert "C7HN6P" in formulas
        assert "C5H12O2S3" in formulas

    def test_empty_bin_at_low_mass(self, reader):
        # ниже 12 Да формул нет по модели (см. tools/diagnostics/empty_bins_report.py)
        assert reader.search(5.0, ppm=1000.0, max_results=5) == []
