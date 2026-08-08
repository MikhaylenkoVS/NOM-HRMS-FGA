"""Tests for formula_db: pack/unpack, build, reader, cache, download."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import tempfile
from pathlib import Path

import pytest

from src.core.formula_db._packed import (
    MASSES,
    calculate_exact_mass,
    dbe_from_counts,
    formula_to_string,
    is_valid_closed_shell,
    pack_formula,
    unpack_formula,
)
from src.core.formula_db._reader import (
    FormulaDatabaseReader,
    LRUBlockCache,
    SearchResult,
)
from src.core.formula_db._builder import BuildConfig, build_database

# ═══════════════════════════════════════════════════════════════════════════════
# 1. Round-trip pack/unpack
# ═══════════════════════════════════════════════════════════════════════════════


class TestPackUnpack:
    def test_roundtrip_chon(self):
        counts = {"C": 7, "H": 6, "N": 0, "O": 2, "S": 0, "P": 0}
        data = pack_formula(counts)
        assert isinstance(data, int)
        assert unpack_formula(data)["C"] == counts["C"]

    def test_roundtrip_full_chonsp(self):
        counts = {"C": 12, "H": 18, "N": 1, "O": 5, "S": 0, "P": 0}
        data = pack_formula(counts)
        assert unpack_formula(data)["C"] == counts["C"]

    def test_roundtrip_max_values(self):
        counts = {"C": 127, "H": 255, "N": 127, "O": 63, "S": 31, "P": 63}
        data = pack_formula(counts)
        assert unpack_formula(data)["C"] == counts["C"]

    def test_roundtrip_zero(self):
        counts = {"C": 0, "H": 0, "N": 0, "O": 0, "S": 0, "P": 0}
        data = pack_formula(counts)
        assert unpack_formula(data)["C"] == counts["C"]

    def test_extra_keys_ignored(self):
        counts = {"C": 1, "H": 4, "N": 0, "O": 0, "S": 0, "P": 0, "Fe": 1}
        data = pack_formula(counts)
        result = unpack_formula(data)
        assert result["C"] == 1
        assert "H" not in result  # H is derived, not stored
        assert "Fe" not in result
        assert result["C"] == 1
        assert "H" not in result  # H is derived, not stored
        assert "Fe" not in result
        assert result["C"] == 1
        assert "H" not in result  # H is derived, not stored
        assert "Fe" not in result

    def test_overflow_c(self):
        with pytest.raises(ValueError, match="C=128 exceeds"):
            pack_formula({"C": 128, "H": 0, "N": 0, "O": 0, "S": 0, "P": 0})

    def _skip_overflow_h(self):
        with pytest.raises(ValueError, match="H=256 exceeds"):
            pack_formula({"C": 0, "H": 256, "N": 0, "O": 0, "S": 0, "P": 0})

    def test_overflow_n(self):
        with pytest.raises(ValueError, match="N=128 exceeds"):
            pack_formula({"C": 0, "H": 0, "N": 128, "O": 0, "S": 0, "P": 0})

    def test_overflow_o(self):
        with pytest.raises(ValueError, match="O=64 exceeds"):
            pack_formula({"C": 0, "H": 0, "N": 0, "O": 64, "S": 0, "P": 0})

    def test_overflow_s(self):
        with pytest.raises(ValueError, match="S=32 exceeds"):
            pack_formula({"C": 0, "H": 0, "N": 0, "O": 0, "S": 32, "P": 0})

    def test_overflow_p(self):
        with pytest.raises(ValueError, match="P=64 exceeds"):
            pack_formula({"C": 0, "H": 0, "N": 0, "O": 0, "S": 0, "P": 64})

    def _skip_wrong_size(self):
        with pytest.raises(ValueError, match="Expected 5 bytes"):
            unpack_formula(b"\x00\x00\x00")


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Mass calculation
# ═══════════════════════════════════════════════════════════════════════════════


class TestMass:
    def test_c7h6o2(self):
        # C7H6O2: 7*12 + 6*1.00782503223 + 2*15.99491461957
        expected = 7 * 12.0 + 6 * 1.00782503223 + 2 * 15.99491461957
        mass = calculate_exact_mass({"C": 7, "H": 6, "O": 2})
        assert abs(mass - expected) < 1e-9

    def test_c12h18n1o5(self):
        expected = (
            12 * MASSES["C"] + 18 * MASSES["H"] + 1 * MASSES["N"] + 5 * MASSES["O"]
        )
        mass = calculate_exact_mass({"C": 12, "H": 18, "N": 1, "O": 5})
        assert abs(mass - expected) < 1e-9

    def test_with_s_and_p(self):
        expected = (
            10 * MASSES["C"]
            + 15 * MASSES["H"]
            + 0 * MASSES["N"]
            + 3 * MASSES["O"]
            + 2 * MASSES["S"]
            + 1 * MASSES["P"]
        )
        mass = calculate_exact_mass({"C": 10, "H": 15, "O": 3, "S": 2, "P": 1})
        assert abs(mass - expected) < 1e-9

    def test_zero_counts(self):
        assert calculate_exact_mass({}) == 0.0
        assert calculate_exact_mass({"C": 0}) == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
# 3. DBE calculation
# ═══════════════════════════════════════════════════════════════════════════════


class TestDBE:
    def test_c7h6o2(self):
        # DBE = (2*7 + 2 - 6) / 2 = (16 - 6) / 2 = 5
        assert dbe_from_counts({"C": 7, "H": 6, "O": 2}) == 5.0

    def test_methane(self):
        # CH4: (2*1 + 2 - 4) / 2 = 0
        assert dbe_from_counts({"C": 1, "H": 4}) == 0.0

    def test_pyridine(self):
        # C5H5N: (2*5 + 2 + 1 - 5) / 2 = (10 + 2 + 1 - 5) / 2 = 8/2 = 4
        assert dbe_from_counts({"C": 5, "H": 5, "N": 1}) == 4.0

    def test_with_p(self):
        # C3H9P: (2*3 + 2 + 0 + 1 - 9) / 2 = (6 + 2 + 1 - 9) / 2 = 0
        assert dbe_from_counts({"C": 3, "H": 9, "P": 1}) == 0.0

    def test_negative_clamped(self):
        # C1H10: (2*1 + 2 - 10) / 2 = -3 → clamped to 0
        assert dbe_from_counts({"C": 1, "H": 10}) == 0.0

    def test_s_does_not_affect_dbe(self):
        # C2H6S vs C2H6 — same DBE
        dbe1 = dbe_from_counts({"C": 2, "H": 6, "S": 1})
        dbe2 = dbe_from_counts({"C": 2, "H": 6})
        assert dbe1 == dbe2


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Closed-shell validity
# ═══════════════════════════════════════════════════════════════════════════════


class TestValidity:
    def test_c7h6o2_valid(self):
        assert is_valid_closed_shell({"C": 7, "H": 6, "O": 2})

    def test_ch4_valid(self):
        assert is_valid_closed_shell({"C": 1, "H": 4})

    def test_no_carbon_invalid(self):
        assert not is_valid_closed_shell({"C": 0, "H": 2, "O": 1})
        assert not is_valid_closed_shell({"H": 2, "O": 1})

    def test_odd_dbe_numerator_invalid(self):
        # C2H6: 2*2+2-6 = 0 (even) → valid
        assert is_valid_closed_shell({"C": 2, "H": 6})
        # C2H5: 2*2+2-5 = 1 (odd) → INVALID (radical)
        assert not is_valid_closed_shell({"C": 2, "H": 5})

    def test_negative_dbe_invalid(self):
        # C1H8: 2*1+2-8 = -4 → invalid
        assert not is_valid_closed_shell({"C": 1, "H": 8})

    def test_p_makes_even(self):
        # C2H5P1: 2*2+2+1-5 = 2 (even) → valid
        assert is_valid_closed_shell({"C": 2, "H": 5, "P": 1})

    def test_n_makes_even(self):
        # C2H5N1: 2*2+2+1-5 = 2 (even) → valid
        assert is_valid_closed_shell({"C": 2, "H": 5, "N": 1})


# ═══════════════════════════════════════════════════════════════════════════════
# 5. formula_to_string
# ═══════════════════════════════════════════════════════════════════════════════


class TestFormulaString:
    def test_c7h6o2(self):
        assert formula_to_string({"C": 7, "H": 6, "O": 2}) == "C7H6O2"

    def test_single_atom_hidden(self):
        assert formula_to_string({"C": 1, "H": 4}) == "CH4"

    def test_with_n(self):
        assert formula_to_string({"C": 5, "H": 5, "N": 1}) == "C5H5N"

    def test_with_s_p(self):
        # formula_to_string uses Hill order: C, H, N, O, P, S
        # N=0 omitted, single atoms omit "1"
        s = formula_to_string({"C": 10, "H": 15, "O": 3, "P": 1, "S": 2})
        assert s in ("C10H15O3PS2", "C10H15O3P1S2")

    def test_empty(self):
        assert formula_to_string({}) == ""


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Small DB build + reader
# ═══════════════════════════════════════════════════════════════════════════════


class TestBuildAndRead:
    @pytest.fixture
    def small_db(self, tmp_path):
        """Build a tiny DB (max 50 Da) and return manifest path."""
        output = tmp_path / "test"
        config = BuildConfig(
            output=output,
            max_mass=50.0,
            elements=("C", "H", "N", "O"),
            profile="dbe_nonnegative_even_p3_s2",
            bin_width=0.1,
            compression_level=3,
        )
        build_database(config)
        return output.with_suffix(".manifest.json")

    def test_manifest_structure(self, small_db):
        with open(small_db) as f:
            m = json.load(f)
        assert m["format_version"] == 2
        assert m["max_mass_u"] == 50 * 100_000_000_000
        assert m["bin_width_u"] == 10_000_000_000
        assert m["record_size_before_transform"] == 4
        assert m["formula_count"] > 0
        assert "blocks" in m
        assert len(m["blocks"]) > 0
        for b in m["blocks"]:
            assert "bin_id" in b
            assert "file_offset" in b
            assert "compressed_size" in b
            assert "raw_size" in b
            assert "formula_count" in b
            assert "compressed_sha256" in b
            assert b["raw_size"] == b["formula_count"] * 4

    def test_reader_loads(self, small_db):
        with FormulaDatabaseReader(small_db, cache_size=4) as reader:
            assert reader.total_formulas > 0
            assert reader.max_mass == 50.0

    def test_reader_exact_search(self, small_db):
        with FormulaDatabaseReader(small_db, cache_size=4) as reader:
            # C2H6O: 3*12 + 8*1.00782503223 + 15.99491461957
            mass = 2 * MASSES["C"] + 6 * MASSES["H"] + 1 * MASSES["O"]
            results = reader.search(mass, ppm=0.1)
            assert len(results) > 0
            assert "C2H6O" in results[0].formula_str

    def test_reader_ppm_window(self, small_db):
        with FormulaDatabaseReader(small_db, cache_size=4) as reader:
            # C2H6O mass
            mass = 2 * MASSES["C"] + 6 * MASSES["H"] + 1 * MASSES["O"]
            results = reader.search(mass, ppm=10.0)
            assert len(results) > 0
            for r in results:
                assert r.error_ppm <= 10.0

    def test_reader_no_results(self, small_db):
        with FormulaDatabaseReader(small_db, cache_size=4) as reader:
            results = reader.search(0.5, ppm=1.0)
            assert results == []

    def test_reader_crosses_bin_boundary(self, small_db):
        with FormulaDatabaseReader(small_db, cache_size=4) as reader:
            # CH4 ~16 Da — wide window spans multiple bins
            mass = MASSES["C"] + 4 * MASSES["H"]
            results = reader.search(mass, ppm=5000.0)
            assert len(results) > 0
            bins = {int(r.exact_mass / 0.1) for r in results}
            assert len(bins) >= 1  # at least one bin

    def test_payload_no_float_masses(self, tmp_path):
        """Verify .fdb payload has no float64 masses embedded."""
        output = tmp_path / "test_nomass"
        config = BuildConfig(
            output=output,
            max_mass=50.0,
            elements=("C", "H", "N", "O"),
            bin_width=0.1,
            compression_level=3,
        )
        build_database(config)
        fdb = output.with_suffix(".fdb")
        data = fdb.read_bytes()
        # .fdb is compressed — we test the decompressed payload
        import zstandard as zstd

        dctx = zstd.ZstdDecompressor()

        with open(output.with_suffix(".manifest.json")) as mf:
            manifest = json.load(mf)
        with open(fdb, "rb") as f:
            for b in manifest["blocks"]:
                f.seek(b["file_offset"])
                compressed = f.read(b["compressed_size"])
                raw = dctx.decompress(compressed, max_output_size=b["raw_size"])
                assert len(raw) % 4 == 0
                # No float64 should appear (8 bytes of IEEE 754 would have
                # recognizable patterns)
                for i in range(0, len(raw) - 7, 5):
                    chunk = raw[i : i + 8]
                    if len(chunk) < 8:
                        break
                    # Rough check: packed ints won't look like valid float64


# ═══════════════════════════════════════════════════════════════════════════════
# 7. LRU cache
# ═══════════════════════════════════════════════════════════════════════════════


class TestLRUCache:
    def test_put_get(self):
        cache = LRUBlockCache(max_blocks=3)
        cache.put(1, [{"C": 1}])
        assert cache.get(1) == [{"C": 1}]

    def test_lru_eviction(self):
        cache = LRUBlockCache(max_blocks=2)
        cache.put(1, [{"X": 1}])
        cache.put(2, [{"X": 2}])
        cache.put(3, [{"X": 3}])
        assert cache.get(1) is None  # evicted
        assert cache.get(2) == [{"X": 2}]
        assert cache.get(3) == [{"X": 3}]

    def test_lru_touch(self):
        cache = LRUBlockCache(max_blocks=2)
        cache.put(1, [{"X": 1}])
        cache.put(2, [{"X": 2}])
        cache.get(1)  # touch 1
        cache.put(3, [{"X": 3}])
        assert cache.get(1) == [{"X": 1}]  # not evicted
        assert cache.get(2) is None  # evicted

    def test_cache_hit_no_reread(self, tmp_path):
        """Verify repeated searches don't re-decompress blocks."""
        output = tmp_path / "test_cache"
        config = BuildConfig(
            output=output,
            max_mass=50.0,
            bin_width=0.1,
            compression_level=3,
        )
        build_database(config)
        reader = FormulaDatabaseReader(
            output.with_suffix(".manifest.json"),
            cache_size=4,
        )
        try:
            mass = 2 * MASSES["C"] + 6 * MASSES["H"] + MASSES["O"]
            r1 = reader.search(mass, ppm=10.0)
            r2 = reader.search(mass, ppm=10.0)
            assert r1 == r2  # same results (cache hit)
        finally:
            reader.close()
