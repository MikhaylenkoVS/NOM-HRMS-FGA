# /test_denoise.py
from pathlib import Path
from src.configs import PATHS
import pandas as pd
import pytest
from src.core.spectrum import load_spectrum, denoise

THIS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = THIS_DIR.parent

TEST_SETS = [
    PROJECT_ROOT / PATHS.test_sets_dir / "set_01",
    PROJECT_ROOT / PATHS.test_sets_dir / "set_02",
    PROJECT_ROOT / PATHS.test_sets_dir / "set_03",
    PROJECT_ROOT / PATHS.test_sets_dir / "set_04",
    PROJECT_ROOT / PATHS.test_sets_dir / "set_05",
]


@pytest.mark.parametrize("set_dir", TEST_SETS)
def test_denoise_original_preserves_signals_and_reduces_noise(set_dir: Path):
    src_path = set_dir / PATHS.spectrum_files["original"]
    ann_path = set_dir / PATHS.spectrum_files["annotations"]

    src = load_spectrum(src_path, mass_min=100, mass_max=1000)
    ann = pd.read_csv(ann_path)

    ann_orig = ann[ann["spectrum_type"] == "original"].copy()
    ann_signal = ann_orig[ann_orig["is_signal"]].copy()
    ann_noise = ann_orig[~ann_orig["is_signal"]].copy()

    rel_error_ppm = 0.5

    denoised = denoise(src, force=10.0, intensity=100, quantile=None)  # denoise wrapper
    den_df = denoised.table.copy()

    # 1. recall по сигналам
    kept_signals = 0
    for _, row in ann_signal.iterrows():
        mass_obs = row["mass_obs"]
        diff_ppm = (den_df["mass"] - mass_obs) / mass_obs * 1e6
        if any(diff_ppm.abs() <= rel_error_ppm + 1e-6):
            kept_signals += 1

    signal_recall = kept_signals / len(ann_signal)

    # 2. retention по шуму
    kept_noise = 0
    for _, row in ann_noise.iterrows():
        mass_obs = row["mass_obs"]
        diff_ppm = (den_df["mass"] - mass_obs) / mass_obs * 1e6
        if any(diff_ppm.abs() <= rel_error_ppm + 1e-6):
            kept_noise += 1

    noise_retention = kept_noise / len(ann_noise)

    print(f"[{set_dir.name}] signal_recall={signal_recall:.3f}")
    print(f"[{set_dir.name}] noise_retention={noise_retention:.3f}")

    assert (
        signal_recall >= 0.90
    ), f"{set_dir.name}: denoise удаляет слишком много сигналов"
    assert noise_retention <= 0.80, f"{set_dir.name}: denoise слишком слабо чистит шум"


# ── Режимы denoise: force / intensity / quantile ──────────────────────────────


def _synthetic_spectrum():
    """Детерминированный спектр: 300 шумовых пиков (1–10) + 20 сигналов (1000)."""
    import numpy as np
    from src.core.spectrum import Spectrum

    rng = np.random.default_rng(7)
    intensities = np.concatenate([rng.uniform(1.0, 10.0, 300), np.full(20, 1000.0)])
    masses = np.arange(len(intensities), dtype=float) + 100.0
    return Spectrum(table=pd.DataFrame({"mass": masses, "intensity": intensities}))


@pytest.mark.parametrize("force", [1.0, 2.0, 4.0, 8.0, 16.0])
def test_force_mode_is_applied_to_gmm_threshold(force: float):
    """force умножает порог GMM, когда intensity/quantile не заданы.

    Проверяется именно режим `force`, который раньше не был покрыт: в
    test_denoise_original_* вызов идёт с intensity=100, а он имеет приоритет
    и полностью перекрывает force.
    """
    spec = _synthetic_spectrum()

    denoised = denoise(spec, force=force, intensity=None, quantile=None)

    kept = denoised.table
    assert 0 < len(kept) <= len(spec.table)
    # все 20 «сигнальных» пиков (I = 1000) обязаны выжить при любом force
    assert int((kept["intensity"] >= 1000.0).sum()) == 20


def test_force_is_monotone_and_actually_filters():
    """Рост force не увеличивает число оставшихся пиков и реально отсекает шум."""
    spec = _synthetic_spectrum()

    counts = [
        len(denoise(spec, force=f, intensity=None, quantile=None).table)
        for f in (1.0, 2.0, 4.0, 8.0, 16.0)
    ]

    assert counts == sorted(counts, reverse=True), f"немонотонно по force: {counts}"
    assert counts[0] > counts[-1], f"force не влияет на результат: {counts}"


def test_intensity_has_priority_over_force():
    """При заданном intensity множитель force игнорируется."""
    spec = _synthetic_spectrum()

    low = denoise(spec, force=1.0, intensity=50.0, quantile=None)
    high = denoise(spec, force=100.0, intensity=50.0, quantile=None)

    assert len(low.table) == len(high.table)
    assert (low.table["intensity"] > 50.0).all()


def test_quantile_mode_returns_subset_of_input():
    """Квантильный режим отдаёт подмножество исходных пиков."""
    spec = _synthetic_spectrum()

    denoised = denoise(spec, force=1.0, intensity=None, quantile=0.9)

    assert 0 < len(denoised.table) <= len(spec.table)
