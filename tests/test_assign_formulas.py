import pandas as pd
import pytest
from pathlib import Path

from src.core.spectrum_ops import load_spectrum, assign_formulas  # здесь должен быть твой фасад


THIS_DIR = Path(__file__).resolve().parent          # .../AnaliticsSpectra/tests
PROJECT_ROOT = THIS_DIR.parent                 # .../AnaliticsSpectra
TEST_SETS_ROOT = PROJECT_ROOT / "data" / "test_sets"  # .../AnaliticsSpectra/data/test_sets


TEST_SETS = [
    PROJECT_ROOT / "data" / "test_sets" / "set_01",
    PROJECT_ROOT / "data" / "test_sets" / "set_02",
    PROJECT_ROOT / "data" / "test_sets" / "set_03",
    PROJECT_ROOT / "data" / "test_sets" / "set_04",
    PROJECT_ROOT / "data" / "test_sets" / "set_05",
]

@pytest.mark.parametrize("set_dir", TEST_SETS)
def test_assign_formulas_original_in_all_sets(set_dir: Path):
    src_path = set_dir / "original.csv"
    ann_path = set_dir / "annotations.csv"
    mol_path = set_dir / "molecules.csv"

    assert src_path.exists(), f"Нет original.csv в {set_dir}"
    assert ann_path.exists(), f"Нет annotations.csv в {set_dir}"
    assert mol_path.exists(), f"Нет molecules.csv в {set_dir}"

    src = load_spectrum(src_path, mass_min=100, mass_max=1000)

    mol = pd.read_csv(mol_path)
    assert "formula" in mol.columns
    formulas = sorted(mol["formula"].dropna().unique())

    rel_error_ppm = 1.0

    src = assign_formulas(
        src,
        mode="simple",
        formulas=formulas,
        rel_error_ppm=rel_error_ppm,
        mass_min=None,
        mass_max=None,
    )

    src_df = src.table.copy()
    assert "assign" in src_df.columns
    assert "brutto" in src_df.columns

    assigned = src_df[src_df["assign"] == True].copy()

    ann = pd.read_csv(ann_path)
    ann_orig = ann[(ann["spectrum_type"] == "original") & (ann["is_signal"])].copy()

    n_assigned = len(assigned)
    n_signals = len(ann_orig)

    assert n_signals > 0, f"{set_dir.name}: нет сигнальных пиков для 'original'"
    assert n_assigned > 0, f"{set_dir.name}: assign_formulas(simple) не назначил ни одной формулы"

    mismatches = []
    matches = 0

    for _, row in ann_orig.iterrows():
        mass_obs = row["mass_obs"]
        formula_true = row["formula"]

        diff_ppm = (assigned["mass"] - mass_obs) / mass_obs * 1e6
        candidates = assigned[diff_ppm.abs() <= rel_error_ppm + 1e-6]

        if candidates.empty:
            mismatches.append(
                {"mass_obs": mass_obs, "formula_true": formula_true, "status": "NO_PEAK_IN_ASSIGNED"}
            )
            continue

        if any(candidates["brutto"] == formula_true):
            matches += 1
        else:
            mismatches.append(
                {
                    "mass_obs": mass_obs,
                    "formula_true": formula_true,
                    "status": "WRONG_BRUTTO",
                    "candidates_brutto": list(candidates["brutto"].unique())[:5],
                }
            )

    match_ratio = matches / n_signals if n_signals > 0 else 0.0

    print(f"\n[{set_dir.name}] Назначено формул: {n_assigned}")
    print(f"[{set_dir.name}] Сигнальных пиков (original): {n_signals}")
    print(f"[{set_dir.name}] Совпадений: {matches}/{n_signals} (доля {match_ratio:.3f})")
    print(f"[{set_dir.name}] Мисматчей: {len(mismatches)}")

    assert match_ratio > 0.9, (
        f"{set_dir.name}: слишком мало совпадений формул для original: "
        f"{matches}/{n_signals} (доля {match_ratio:.3f})"
    )