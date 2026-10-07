"""Регрессионные тесты на краевые случаи входных данных (PACKAGE-05).

Покрывают: S-06 (пустой спектр и NaN-массы в assign_formulas), S-09 (NaN в
необязательных колонках Spectrum), S-10 (дубликаты колонок в load_spectrum),
S-11 (некорректный quantile в denoise), K-22 (согласованность двух реализаций
DBE).
"""

import numpy as np
import pandas as pd
import pytest

from src.core.domain.spectrum import Spectrum
from src.core.spectrum import assign_formulas, denoise, load_spectrum


def _spectrum(pairs) -> Spectrum:
    return Spectrum(
        table=pd.DataFrame(
            {
                "mass": [p[0] for p in pairs],
                "intensity": [p[1] for p in pairs],
            }
        )
    )


# ── S-06: пустой спектр и нечисловые массы ────────────────────────────────────


def test_assign_empty_spectrum_returns_empty_result():
    """Пустой спектр не должен падать (ранее — ValueError из-за NaN в окне)."""
    result = assign_formulas(_spectrum([]), rel_error_ppm=5.0)

    assert len(result.table) == 0
    assert list(result.table.columns[-3:]) == ["brutto", "assign", "all_candidates"]


def test_assign_skips_nan_and_negative_masses():
    """Пики с NaN/отрицательной массой остаются без назначения, прогон идёт."""
    sp = Spectrum(
        table=pd.DataFrame(
            {
                "mass": [np.nan, 137.024, -5.0],
                "intensity": [10.0, 1000.0, 10.0],
            }
        )
    )

    result = assign_formulas(sp, rel_error_ppm=5.0)

    assert result.table["assign"].tolist() == [False, True, False]
    assert result.table["all_candidates"].tolist()[0] == []
    assert result.table["all_candidates"].tolist()[2] == []


# ── S-09: NaN в необязательных колонках ──────────────────────────────────────


def test_df_to_peaks_maps_nan_optional_columns_to_none():
    """NaN в необязательных колонках → None, а не исключение при int()/float()."""
    sp = Spectrum(
        table=pd.DataFrame(
            {
                "mass": [100.0, 200.0],
                "intensity": [1.0, 2.0],
                "resolution": [np.nan, 50000.0],
                "baseline": [np.nan, np.nan],
                "charge": [np.nan, 1.0],
                "rt": [np.nan, 1.5],
                "scan_number": [np.nan, 7.0],
            }
        )
    )

    first, second = sp.peaks

    assert first.resolution is None
    assert first.charge is None
    assert first.rt is None
    assert first.scan_number is None
    assert first.baseline is None

    assert second.resolution == 50000.0
    assert second.charge == 1
    assert second.rt == 1.5
    assert second.scan_number == 7


# ── S-10: дубликаты колонок после переименования ─────────────────────────────


def test_load_spectrum_reports_duplicate_columns(tmp_path):
    """CSV с двумя колонками массы должен давать понятную ошибку."""
    path = tmp_path / "dup.csv"
    path.write_text("m/z,mass,intensity\n100.0,101.0,1.0\n", encoding="utf-8")

    with pytest.raises(ValueError) as excinfo:
        load_spectrum(str(path))

    assert "дубликат" in str(excinfo.value)


def test_load_spectrum_accepts_single_mass_column(tmp_path):
    """Контроль: обычный файл по-прежнему читается (регресс на S-10)."""
    path = tmp_path / "ok.csv"
    path.write_text("m/z,intensity\n100.0,1.0\n101.0,2.0\n", encoding="utf-8")

    sp = load_spectrum(str(path), mass_min=0, mass_max=1000)

    assert len(sp.table) == 2


# ── S-11: валидация quantile ─────────────────────────────────────────────────


@pytest.mark.parametrize("bad", [-0.1, 1.5, 2.0])
def test_denoise_rejects_quantile_outside_unit_interval(bad):
    """quantile вне [0, 1] — ошибка вызывающего, а не молчаливый результат."""
    spec = _spectrum([(100.0, 1.0), (101.0, 2.0), (102.0, 3.0)])

    with pytest.raises(ValueError) as excinfo:
        denoise(spec, quantile=bad)

    assert "quantile" in str(excinfo.value)


def test_denoise_accepts_valid_quantile():
    """Контроль: корректный quantile работает."""
    spec = _spectrum([(100.0, 1.0), (101.0, 2.0), (102.0, 3.0)])

    result = denoise(spec, quantile=0.5)

    assert 0 < len(result.table) <= len(spec.table)


# ── K-22: согласованность реализаций DBE ─────────────────────────────────────


def test_statistics_dbe_matches_core_dbe_for_negative_values():
    """Обе реализации DBE клампят отрицательные значения к нулю."""
    from src.core.spectrum._chem import dbe_from_counts
    from src.core.statistics import dbe

    counts = {"C": 1, "H": 10, "N": 0, "O": 0}

    assert dbe(counts) == 0.0
    assert dbe(counts) == dbe_from_counts(counts)


def test_statistics_dbe_unchanged_for_typical_formula():
    """Контроль: для обычной формулы значение не изменилось."""
    from src.core.spectrum._chem import dbe_from_counts
    from src.core.statistics import dbe

    counts = {"C": 7, "H": 6, "O": 2, "N": 0}

    assert dbe(counts) == 5.0
    assert dbe(counts) == dbe_from_counts(counts)
