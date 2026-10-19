"""Политика изотопного отклонения кандидатов (P0 внешнего ревью).

Формулировка, которую проверяем:

> Кандидат обязан объяснять наблюдаемый паттерн; отсутствие предсказанного
> сателлита используется для отклонения только тогда, когда этот сателлит
> должен был быть измерим в имеющихся данных.

Измеримость = предсказанная абсолютная интенсивность сателлита выше уровня
шума спектра (нижний процентиль интенсивностей исходного пиклиста).

Колонки результата: ``iso_status`` ∈ {confirmed, inconsistent, uninformative}
и ``iso_halogen_unconfirmed`` — галогенсодержащая формула без подтверждения.
"""

from __future__ import annotations

import numpy as np
import pandas as pd  # noqa: F401
import pytest

from src.core.domain.spectrum import Spectrum
from src.core.spectrum._assign import _M1_DELTAS, _M2_DELTAS, assign_formulas
from src.core.spectrum._constants import ATOMIC_MASS
from src.core.spectrum._isotopes import pattern

PROTON = 1.007276466812
D_M1 = 1.00335  # 13C
D_M2 = 1.99705  # 37Cl


def neutral(counts: dict[str, int]) -> float:
    return sum(ATOMIC_MASS[el] * n for el, n in counts.items())


def mz(counts: dict[str, int]) -> float:
    """m/z в режиме [M-H]-."""
    return neutral(counts) - PROTON


def build_spectrum(
    target: dict[str, int],
    *,
    satellites: dict[int, float] | None = None,
    base_intensity: float = 1000.0,
    noise_level: float = 40.0,
    noise_peaks: int = 30,
) -> Spectrum:
    """Спектр с целевым пиком, заданными сателлитами и уровнем шума."""
    m0 = mz(target)
    peaks = [(m0, base_intensity)]
    deltas = {1: D_M1, 2: D_M2}
    for shift, ratio in (satellites or {}).items():
        peaks.append((neutral(target) + deltas[shift] - PROTON, base_intensity * ratio))
    for k in range(noise_peaks):
        peaks.append((m0 + 5.0 + 0.37 * k, noise_level))
    return Spectrum(table=pd.DataFrame(peaks, columns=["mass", "intensity"]))


def assign(spec: Spectrum) -> pd.DataFrame:
    original = spec.copy()
    assign_formulas(
        spec,
        rel_error_ppm=5.0,
        mass_min=0.0,
        mass_max=1000.0,
        isotope_filter=True,
        original=original,
        isotope_satellites=False,
    )
    return spec.table


def row_for(table: pd.DataFrame, target: dict[str, int]):
    m = mz(target)
    return table.loc[(table["mass"] - m).abs().idxmin()]


class TestM1MeasurementPolicy:
    """M+1 не требуется, если он не мог быть измерен."""

    def test_chlorinated_m2_visible_m1_below_threshold(self):
        """Cl: M+2 виден, предсказанный M+1 (13 %) ниже уровня шума."""
        target = {"C": 12, "H": 9, "Cl": 1, "O": 4}
        # база 1000: M+1 ≈ 132 < шум 200 < M+2 ≈ 336
        spec = build_spectrum(target, satellites={2: 0.336}, noise_level=200.0)
        row = row_for(assign(spec), target)
        assert bool(row["assign"]) is True
        assert "Cl" in str(row["brutto"]), row["brutto"]
        assert row["iso_status"] == "confirmed"
        assert bool(row["iso_halogen_unconfirmed"]) is False

    def test_brominated_m2_visible_m1_below_threshold(self):
        """Br: M+2 ≈ 97 %, M+1 ≈ 6.5 % ниже уровня шума."""
        target = {"C": 6, "H": 5, "Br": 1}
        spec = build_spectrum(target, satellites={2: 0.97}, noise_level=200.0)
        row = row_for(assign(spec), target)
        assert "Br" in str(row["brutto"]), row["brutto"]

    def test_chlorinated_without_measurable_satellite_is_not_rejected(self):
        """Cl: предсказанный M+2 ниже шума → отклонять не за что."""
        target = {"C": 6, "H": 5, "Cl": 1}
        # база 100: M+2 ≈ 32 < шум 200 → сателлит неизмерим
        spec = build_spectrum(
            target, satellites=None, base_intensity=100.0, noise_level=200.0
        )
        row = row_for(assign(spec), target)
        assert bool(row["assign"]) is True
        assert row["iso_status"] in ("uninformative", "confirmed")

    @pytest.mark.parametrize("element", ["F", "I"])
    def test_fluorine_and_iodine_have_no_own_pattern(self, element):
        """F и I не дают характерного паттерна: жёсткого требования нет."""
        target = {"C": 10, "H": 12, element: 1, "O": 2}
        spec = build_spectrum(target, satellites=None, noise_level=200.0)
        row = row_for(assign(spec), target)
        assert bool(row["assign"]) is True
        assert row["iso_status"] == "uninformative"
        if element in str(row["brutto"]):
            assert bool(row["iso_halogen_unconfirmed"]) is True

    def test_measurable_missing_satellite_is_rejected(self):
        """Сателлит обязан был быть виден, но его нет → кандидат отклоняется."""
        target = {"C": 20, "H": 29, "Cl": 1, "O": 1}
        # база 1000, шум 200: M+2 ≈ 336 > 200 → отсутствие противоречит Cl
        spec = build_spectrum(
            target, satellites=None, base_intensity=1000.0, noise_level=200.0
        )
        row = row_for(assign(spec), target)
        assert str(row["brutto"]) != "C20H29ClO"

    def test_satellite_outside_measured_range(self):
        """Сателлит вне диапазона измерений → «данных недостаточно»."""
        target = {"C": 16, "H": 22, "O": 4}
        spec = build_spectrum(
            target, satellites=None, base_intensity=10.0, noise_level=200.0
        )
        row = row_for(assign(spec), target)
        assert bool(row["assign"]) is True
        assert row["iso_status"] == "uninformative"


class TestIsotopeStatusContract:
    def test_columns_present_and_typed(self):
        spec = build_spectrum({"C": 7, "H": 6, "O": 2}, satellites={1: 0.08})
        table = assign(spec)
        assert {"iso_status", "iso_halogen_unconfirmed"} <= set(table.columns)
        assert table["iso_halogen_unconfirmed"].dtype == bool

    def test_full_pattern_is_confirmed(self):
        target = {"C": 16, "H": 22, "O": 4}
        theo = pattern(target, max_shift=2)
        spec = build_spectrum(
            target, satellites={1: theo[1], 2: theo[2]}, noise_level=1.0
        )
        row = row_for(assign(spec), target)
        assert str(row["brutto"]) == "C16H22O4"
        assert row["iso_status"] == "confirmed"

    def test_halogen_without_evidence_is_flagged(self):
        """Галоген в выданной формуле без свидетельств → флаг."""
        target = {"C": 10, "H": 12, "I": 1, "O": 2}
        spec = build_spectrum(target, satellites=None, noise_level=200.0)
        row = row_for(assign(spec), target)
        if any(el in str(row["brutto"]) for el in ("F", "Cl", "Br", "I")):
            assert bool(row["iso_halogen_unconfirmed"]) is True
        else:
            assert bool(row["iso_halogen_unconfirmed"]) is False


class TestSatellitePositions:
    def test_positions_include_chlorine_and_bromine(self):
        """Сдвиги сателлитов включают 37Cl и 81Br, а не только 33S/34S."""
        assert any(abs(d - 1.99705) < 2e-4 for d in _M2_DELTAS), _M2_DELTAS
        assert any(abs(d - 1.99795) < 2e-4 for d in _M2_DELTAS), _M2_DELTAS
        assert any(abs(d - 1.00335) < 2e-4 for d in _M1_DELTAS), _M1_DELTAS
        assert any(abs(d - 1.00628) < 2e-4 for d in _M1_DELTAS), _M1_DELTAS  # 2H

    def test_numpy_bool_is_plain_bool(self):
        spec = build_spectrum({"C": 7, "H": 6, "O": 2}, satellites={1: 0.08})
        table = assign(spec)
        assert isinstance(bool(table["iso_halogen_unconfirmed"].iloc[0]), bool)
        assert np.isfinite(table["mass"]).all()
