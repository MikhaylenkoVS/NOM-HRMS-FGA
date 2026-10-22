# tests/test_pipeline_denoise_assign_find_series.py

from pathlib import Path
import re

import pandas as pd
import pytest

from src.core.spectrum import (
    Spectrum,
    load_spectrum,
    denoise,
    assign_formulas,
    find_series,
)
from src.configs import CHEM, PIPELINE, PATHS

# -------------------
# Константы и пути — единый источник src/configs/
# -------------------

REL_ERROR_PPM = 1.2
MATCH_PPM = 1.2
ASSIGN_MATCH_PPM = 0.1

DELTA_DEUTEROMETHYLATED = CHEM.derivatization_shifts["delta_cd3"]
DELTA_DEUTEROACYLATED = CHEM.derivatization_shifts["delta_cd3co"]

THIS_DIR = Path(__file__).resolve().parents[1]
PROJECT_ROOT = THIS_DIR.parent

TEST_SETS_ROOT = PROJECT_ROOT / PATHS.test_sets_dir
TEST_SETS = sorted([p for p in TEST_SETS_ROOT.glob("set_*") if p.is_dir()])

_SF = PATHS.spectrum_files
DERIV_SPECS = [
    (_SF["deutermethylated"], DELTA_DEUTEROMETHYLATED, "deutermethylated"),
    (_SF["deuteroacylated"], DELTA_DEUTEROACYLATED, "deuteroacylated"),
]

# Порог из твоих тестов find_series был 0.07, оставим те же границы
MAX_SERIES_PROBLEM_RATIO = 0.07

# Порог для денуаза и assign возьмём по смыслу: denoise >= 0.90, assign >= 0.8
MIN_DENOISE_RECALL = 0.90
MIN_ASSIGN_RECALL = 0.80

DEBUG_PREVIEW_ROWS = 5

# -------------------
# Вспомогательные функции
# -------------------


def _debug(msg: str) -> None:
    print(f"[DEBUG] {msg}")


def _build_pipeline_log(
    set_name: str,
    deriv_name: str,
    total_signals: int,
    denoised_kept: int,
    assigned_ok: int,
    result_count: int,
    matched_series: int,
    wrong_count: int,
) -> str:
    denoise_cov = denoised_kept / total_signals if total_signals else 0.0
    assign_cov = assigned_ok / total_signals if total_signals else 0.0
    series_cov = matched_series / total_signals if total_signals else 0.0
    wrong_ratio = wrong_count / total_signals if total_signals else 0.0

    return (
        f"{set_name:<8} | "
        f"{deriv_name:<18} | "
        f"signals={total_signals:>3} | "
        f"denoise={denoised_kept:>3} ({denoise_cov:>6.1%}) | "
        f"assign={assigned_ok:>3} ({assign_cov:>6.1%}) | "
        f"series={result_count:>3} | "
        f"matched={matched_series:>3} ({series_cov:>6.1%}) | "
        f"wrong={wrong_count:>3} ({wrong_ratio:>6.1%})"
    )


def _print_pipeline_log(
    set_name: str,
    deriv_name: str,
    total_signals: int,
    denoised_kept: int,
    assigned_ok: int,
    result_count: int,
    matched_series: int,
    wrong_count: int,
) -> None:
    print(
        "\n"
        + _build_pipeline_log(
            set_name=set_name,
            deriv_name=deriv_name,
            total_signals=total_signals,
            denoised_kept=denoised_kept,
            assigned_ok=assigned_ok,
            result_count=result_count,
            matched_series=matched_series,
            wrong_count=wrong_count,
        )
    )


def _ppm_error(observed: float, theoretical: float) -> float:
    return abs(observed - theoretical) / theoretical * 1e6


FORMULA_RE = re.compile(r"([A-Z][a-z]?)(\d*)")


def normalize_brutto(formula: str) -> str:
    """
    Та же нормализация, что в test_assign_formulas.
    """
    if formula is None or not isinstance(formula, str):
        return formula

    tokens = re.findall(r"([A-Z][a-z]*)(\d*)", formula)
    if not tokens:
        return formula

    counts = {}
    for elem, num_str in tokens:
        count = int(num_str) if num_str else 1
        counts[elem] = counts.get(elem, 0) + count

    parts = []
    for elem in sorted(counts.keys()):
        cnt = counts[elem]
        parts.append(elem if cnt == 1 else f"{elem}{cnt}")
    return "".join(parts)


def _match_table_row_by_mass(
    table: pd.DataFrame,
    mass_obs: float,
    ppm_tol: float,
    mass_col: str = "mass",
):
    if table.empty or mass_col not in table.columns:
        return None

    work = table.copy()
    work["_ppm"] = (
        work[mass_col]
        .astype(float)
        .apply(lambda x: _ppm_error(float(x), float(mass_obs)))
    )
    work = work.loc[work["_ppm"] <= ppm_tol].copy()

    if work.empty:
        return None

    return work.sort_values("_ppm").iloc[0]


def _match_result_row_by_mass(
    result: pd.DataFrame,
    mass_src: float,
    ppm_tol: float,
):
    if result.empty:
        return None

    diffs_ppm = result["mass_src"].apply(
        lambda x: _ppm_error(float(x), float(mass_src))
    )
    matched = result.loc[diffs_ppm <= ppm_tol]
    if matched.empty:
        return None

    return matched.sort_values("mass_src").iloc[0]


def _load_molecules_map(set_dir: Path) -> pd.DataFrame:
    molecules = pd.read_csv(set_dir / PATHS.spectrum_files["molecules"])

    required_cols = {"compound_number", "carboxyl_count", "hydroxyl_count"}
    missing = required_cols - set(molecules.columns)
    assert (
        not missing
    ), f"{set_dir.name}/molecules.csv: отсутствуют колонки {sorted(missing)}"

    return molecules


def _expected_series_length(
    deriv_filename: str,
    molecule_row: pd.Series,
) -> int:
    if deriv_filename == PATHS.spectrum_files["deutermethylated"]:
        return int(molecule_row["carboxyl_count"])
    if deriv_filename == PATHS.spectrum_files["deuteroacylated"]:
        return int(molecule_row["hydroxyl_count"])

    raise AssertionError(f"Неизвестный тип дериватизации: {deriv_filename}")


def _prepare_assigned_original_from_annotations(
    set_dir: Path,
    ppm_tol: float,
) -> Spectrum:
    """
    Ровно тот же подход, что в _prepare_assigned_original из test_find_series_on_existing_sets:
    - берём original.csv,
    - по mass_obs из annotations расставляем brutto/assign,
    - отфильтровываем только совпавшие по mass.
    """
    src = load_spectrum(
        set_dir / PATHS.spectrum_files["original"], mass_min=100, mass_max=1000
    )
    ann = pd.read_csv(set_dir / PATHS.spectrum_files["annotations"])

    ann_orig_signal = ann[
        (ann["spectrum_type"] == "original") & (ann["is_signal"] == True)
    ].copy()

    table = src.table.copy()

    if "brutto" not in table.columns:
        table["brutto"] = None
    if "assign" not in table.columns:
        table["assign"] = False

    ann_masses = ann_orig_signal["mass_obs"].astype(float).tolist()
    ann_formulas = ann_orig_signal["formula"].tolist()

    matched_rows = set()

    for i, mz in enumerate(table["mass"].astype(float)):
        best_j = None
        best_ppm = None

        for j, ann_mz in enumerate(ann_masses):
            err = _ppm_error(mz, ann_mz)
            if err <= ppm_tol and (best_ppm is None or err < best_ppm):
                best_j = j
                best_ppm = err

        if best_j is not None:
            formula = ann_formulas[best_j]
            if pd.notna(formula) and str(formula).strip():
                table.at[i, "brutto"] = str(formula).strip()
                table.at[i, "assign"] = True
                matched_rows.add(i)

    table = table.loc[sorted(matched_rows)].reset_index(drop=True).copy()

    filtered = src.copy()
    filtered.table = table
    return filtered


def _filter_to_signal_original_peaks(
    src: Spectrum,
    annotations: pd.DataFrame,
    ppm_tol: float,
) -> Spectrum:
    ann_orig_signal = annotations[
        (annotations["spectrum_type"] == "original")
        & (annotations["is_signal"] == True)
    ].copy()

    signal_masses = ann_orig_signal["mass_obs"].astype(float).tolist()

    table = src.table.copy()
    keep_mask = [
        any(_ppm_error(float(mz), signal_mz) <= ppm_tol for signal_mz in signal_masses)
        for mz in table["mass"]
    ]

    filtered_table = table.loc[keep_mask].reset_index(drop=True)
    return Spectrum(table=filtered_table)


def _preview_table(df: pd.DataFrame, name: str) -> None:
    _debug(f"{name}: shape={df.shape}, columns={list(df.columns)}")
    if not df.empty:
        print(df.head(DEBUG_PREVIEW_ROWS).to_string(index=False))


# -------------------
# Основной тест
# -------------------


@pytest.mark.parametrize("set_dir", TEST_SETS, ids=lambda p: p.name)
def test_pipeline_denoise_assign_find_series_on_existing_sets(set_dir: Path):
    assert TEST_SETS_ROOT.exists(), f"Не найдена папка test_sets: {TEST_SETS_ROOT}"

    _debug(f"=== START SET {set_dir.name} ===")

    ann = pd.read_csv(set_dir / PATHS.spectrum_files["annotations"])
    molecules = _load_molecules_map(set_dir)

    required_ann_cols = {
        "spectrum_type",
        "is_signal",
        "mass_obs",
        "compound_number",
        "formula",
    }
    missing_ann_cols = required_ann_cols - set(ann.columns)
    assert not missing_ann_cols, (
        f"{set_dir.name}/annotations.csv: отсутствуют колонки "
        f"{sorted(missing_ann_cols)}"
    )

    ann_orig_signal = ann[
        (ann["spectrum_type"] == "original") & (ann["is_signal"] == True)
    ].copy()
    assert (
        not ann_orig_signal.empty
    ), f"{set_dir.name}: в annotations.csv нет signal-пиков original"

    total_signals = len(ann_orig_signal)
    _debug(f"{set_dir.name}: total original signals={total_signals}")

    # -------------------
    # Шаг 1: denoise (как в test_denoise)
    # -------------------
    src = load_spectrum(
        set_dir / PATHS.spectrum_files["original"], mass_min=100, mass_max=1000
    )
    _preview_table(src.table, f"{set_dir.name} original")

    denoised = denoise(src, force=10.0, intensity=100, quantile=None)
    assert isinstance(
        denoised, Spectrum
    ), f"{set_dir.name}: denoise должен возвращать Spectrum"
    assert not denoised.table.empty, f"{set_dir.name}: после denoise спектр пуст"
    _preview_table(denoised.table, f"{set_dir.name} denoised")

    denoised_kept = 0
    denoise_missing_cases = []

    for _, ann_row in ann_orig_signal.iterrows():
        mass_obs = float(ann_row["mass_obs"])
        row = _match_table_row_by_mass(
            denoised.table,
            mass_obs,
            ppm_tol=0.5,  # тот же tol, что и в test_denoise
            mass_col="mass",
        )
        if row is None:
            denoise_missing_cases.append(
                {
                    "mass_obs": mass_obs,
                    "compound_number": int(ann_row["compound_number"]),
                }
            )
        else:
            denoised_kept += 1

    denoise_recall = denoised_kept / total_signals if total_signals else 0.0
    _debug(
        f"{set_dir.name}: denoised_kept={denoised_kept}/{total_signals} "
        f"({denoise_recall:.3f})"
    )
    if denoise_missing_cases:
        _debug(
            f"{set_dir.name}: first denoise_missing_cases: "
            f"{denoise_missing_cases[:3]}"
        )

    assert denoise_recall >= MIN_DENOISE_RECALL, (
        f"{set_dir.name}: denoise удаляет слишком много сигналов "
        f"({denoised_kept}/{total_signals}, {denoise_recall:.3f})"
    )

    # -------------------
    # Шаг 2: assign_formulas(simple) (как в test_assign_formulas)
    # -------------------
    rel_error_assign_ppm = 0.5

    assigned_src = assign_formulas(
        denoised,
        rel_error_ppm=rel_error_assign_ppm,
        mass_min=0,
        mass_max=1000,
        nom_weight=20.0,
    )

    assigned_df = assigned_src.table.copy()
    assert "assign" in assigned_df.columns
    assert "brutto" in assigned_df.columns

    _preview_table(assigned_df, f"{set_dir.name} assigned (simple)")

    assigned_ok = 0
    assign_missing_cases = []
    wrong_brutto_cases = []

    for _, ann_row in ann_orig_signal.iterrows():
        mass_obs = float(ann_row["mass_obs"])
        formula_true = normalize_brutto(str(ann_row["formula"]))

        diff_ppm = (assigned_df["mass"] - mass_obs) / mass_obs * 1e6
        candidates = assigned_df[diff_ppm.abs() <= rel_error_assign_ppm + 1e-6]

        if candidates.empty:
            assign_missing_cases.append(
                {
                    "mass_obs": mass_obs,
                    "formula_true": formula_true,
                }
            )
            continue

        cand_norm = candidates["brutto"].apply(normalize_brutto)
        if any(cand_norm == formula_true):
            assigned_ok += 1
        else:
            wrong_brutto_cases.append(
                {
                    "mass_obs": mass_obs,
                    "formula_true": formula_true,
                    "candidates_brutto": list(cand_norm.unique())[:5],
                }
            )

    assign_recall = assigned_ok / total_signals if total_signals else 0.0
    _debug(
        f"{set_dir.name}: assigned_ok={assigned_ok}/{total_signals} "
        f"({assign_recall:.3f})"
    )

    if assign_missing_cases:
        _debug(
            f"{set_dir.name}: first assign_missing_cases: "
            f"{assign_missing_cases[:3]}"
        )
    if wrong_brutto_cases:
        _debug(
            f"{set_dir.name}: first wrong_brutto_cases: " f"{wrong_brutto_cases[:3]}"
        )

    assert assign_recall >= MIN_ASSIGN_RECALL, (
        f"{set_dir.name}: assign_formulas(simple) даёт слишком мало совпадений "
        f"с аннотациями: {assigned_ok}/{total_signals} ({assign_recall:.3f})"
    )

    # -------------------
    # Шаг 3: find_series на "идеальных" src (как в test_find_series)
    # -------------------
    src_true = _prepare_assigned_original_from_annotations(
        set_dir,
        ppm_tol=ASSIGN_MATCH_PPM,
    )
    src_true = _filter_to_signal_original_peaks(src_true, ann, ppm_tol=MATCH_PPM)

    assert (
        not src_true.table.empty
    ), f"{set_dir.name}: после фильтрации не осталось signal-пиков original"

    _preview_table(src_true.table, f"{set_dir.name} src_true for find_series")

    # две строки лога на сет: одна для deutermethylated, одна для deuteroacylated
    for deriv_filename, delta, deriv_label in DERIV_SPECS:
        _debug(
            f"{set_dir.name}: START find_series deriv={deriv_filename}, delta={delta}"
        )

        deriv = load_spectrum(set_dir / deriv_filename, mass_min=100, mass_max=2000)
        assert isinstance(
            deriv, Spectrum
        ), f"{set_dir.name}/{deriv_filename}: load_spectrum не вернул Spectrum"
        assert (
            not deriv.table.empty
        ), f"{set_dir.name}/{deriv_filename}: deriv спектр пуст"

        _preview_table(deriv.table, f"{set_dir.name} {deriv_label} deriv")

        result = find_series(
            src=src_true,
            deriv=deriv,
            delta=delta,
            ppm_tol=REL_ERROR_PPM,
            max_groups=20,
            allow_gaps=True,
        )

        assert (
            not result.empty
        ), f"{set_dir.name}/{deriv_filename}: find_series не нашел ни одной серии"

        expected_columns = [
            "mass_src",
            "brutto",
            "n_groups",
            "steps_found",
            "missing",
            "series_mz",
            # статистическая значимость длины серии (ADR-0009)
            "p_value",
            "significant",
            # профиль интенсивностей продуктов (опциональный критерий)
            "profile_ok",
            "max_jump",
            "int_corr",
        ]
        assert list(result.columns) == expected_columns, (
            f"{set_dir.name}/{deriv_filename}: неожиданные колонки результата: "
            f"{list(result.columns)}"
        )

        _preview_table(result, f"{set_dir.name} {deriv_label} result")

        matched_series = 0
        wrong_length_cases = []
        missing_series_cases = []
        total_with_series = 0

        for _, ann_row in ann_orig_signal.iterrows():
            mass_obs = float(ann_row["mass_obs"])
            compound_number = int(ann_row["compound_number"])

            molecule_match = molecules.loc[
                molecules["compound_number"] == compound_number
            ]
            assert not molecule_match.empty, (
                f"{set_dir.name}: compound_number={compound_number} из annotations.csv "
                f"не найден в molecules.csv"
            )
            assert len(molecule_match) == 1, (
                f"{set_dir.name}: compound_number={compound_number} не уникален "
                f"в molecules.csv"
            )

            molecule_row = molecule_match.iloc[0]
            expected_len = _expected_series_length(deriv_filename, molecule_row)

            # Если у молекулы нет целевых групп (expected_len = 0),
            # то серия не ожидается — пропускаем эту молекулу.
            if expected_len == 0:
                continue

            total_with_series += 1

            row = _match_result_row_by_mass(result, mass_obs, MATCH_PPM)
            if row is None:
                missing_series_cases.append(
                    {
                        "mass_obs": mass_obs,
                        "compound_number": compound_number,
                        "expected_len": expected_len,
                    }
                )
                continue

            matched_series += 1

            assert isinstance(
                row["steps_found"], list
            ), f"{set_dir.name}/{deriv_filename}: steps_found должен быть list"
            assert isinstance(
                row["missing"], list
            ), f"{set_dir.name}/{deriv_filename}: missing должен быть list"
            assert isinstance(
                row["series_mz"], list
            ), f"{set_dir.name}/{deriv_filename}: series_mz должен быть list"

            if int(row["n_groups"]) != expected_len:
                wrong_length_cases.append(
                    {
                        "mass_obs": mass_obs,
                        "compound_number": compound_number,
                        "expected_len": expected_len,
                        "actual_len": int(row["n_groups"]),
                        "steps_found": row["steps_found"],
                        "missing": row["missing"],
                    }
                )

        wrong_count = len(missing_series_cases) + len(wrong_length_cases)
        _total_series = total_with_series if total_with_series else total_signals
        wrong_ratio = wrong_count / _total_series if _total_series else 0.0

        _debug(
            f"{set_dir.name}/{deriv_label}: matched_series={matched_series}/{total_with_series}, "
            f"wrong_count={wrong_count}/{_total_series} ({wrong_ratio:.3f})"
        )

        if missing_series_cases:
            _debug(
                f"{set_dir.name}/{deriv_label}: first missing_series_cases: "
                f"{missing_series_cases[:3]}"
            )
        if wrong_length_cases:
            _debug(
                f"{set_dir.name}/{deriv_label}: first wrong_length_cases: "
                f"{wrong_length_cases[:3]}"
            )

        assert wrong_ratio <= MAX_SERIES_PROBLEM_RATIO, (
            f"{set_dir.name}/{deriv_filename}: слишком много пиков с неправильной длиной серии "
            f"или без серии: {wrong_count}/{total_signals} ({wrong_ratio:.1%}). "
            f"Примеры: NO_SERIES={missing_series_cases[:3] if missing_series_cases else 'нет'}; "
            f"BAD_LEN={wrong_length_cases[:3] if wrong_length_cases else 'нет'}"
        )

        _print_pipeline_log(
            set_name=set_dir.name,
            deriv_name=deriv_label,
            total_signals=total_signals,
            denoised_kept=denoised_kept,
            assigned_ok=assigned_ok,
            result_count=len(result),
            matched_series=matched_series,
            wrong_count=wrong_count,
        )

    _debug(f"=== END SET {set_dir.name} ===")


# ===================================================================
# Unit tests for max_consecutive_misses (early-stop optimisation)
# ===================================================================


def _make_src_spectrum(masses, assign=True, brutto="C7H6O2"):
    """Helper: build a minimal source Spectrum with assign/brutto columns."""
    df = pd.DataFrame(
        {
            "mass": masses,
            "brutto": brutto,
            "assign": assign,
        }
    )
    return Spectrum(table=df)


def _make_deriv_spectrum(masses, intensities=None):
    """Helper: build a minimal derivatized Spectrum."""
    if intensities is None:
        intensities = [1000.0] * len(masses)
    df = pd.DataFrame(
        {
            "mass": masses,
            "intensity": intensities,
        }
    )
    return Spectrum(table=df)


class TestMaxConsecutiveMisses:
    """Tests for the early-stop optimisation (issue #3)."""

    DELTA = 17.03448

    def test_default_value_is_three(self):
        """Default max_consecutive_misses should be 3."""
        import inspect

        sig = inspect.signature(find_series)
        default = sig.parameters["max_consecutive_misses"].default
        assert default == 3

    def test_value_below_one_raises(self):
        """max_consecutive_misses < 1 raises ValueError."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([117.03448])
        with pytest.raises(ValueError, match="max_consecutive_misses"):
            find_series(src, deriv, self.DELTA, max_consecutive_misses=0)

    def test_early_stop_prevents_wasteful_loops(self):
        """Series with many gaps stops early at max_consecutive_misses."""
        # 1 found peak, then 5 consecutive misses
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([117.03448])  # step 1 only
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=10,
            max_consecutive_misses=3,
        )
        assert not result.empty
        # n_groups should be 1 (only step 1 found, then 3 misses stops)
        assert int(result.iloc[0]["n_groups"]) == 1

    def test_internal_gap_does_not_break_series(self):
        """A gap inside the series does NOT trigger early-stop."""
        # steps 1 and 3 found, step 2 missing → series length 3
        src = _make_src_spectrum([100.0])
        # step 1: 117.03448, step 2: miss, step 3: 151.10344
        step3_mz = 100.0 + 3 * self.DELTA
        deriv = _make_deriv_spectrum([117.03448, step3_mz])
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=5,
            max_gaps=1,
            max_consecutive_misses=3,
        )
        assert not result.empty
        row = result.iloc[0]
        assert int(row["n_groups"]) == 3
        assert row["missing"] == [2]

    def test_early_stop_does_not_affect_dense_series(self):
        """A complete series without gaps is unaffected by early-stop."""
        src = _make_src_spectrum([100.0])
        # 5 steps, all present
        mz_list = [100.0 + i * self.DELTA for i in range(1, 6)]
        deriv = _make_deriv_spectrum(mz_list)
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=10,
            max_consecutive_misses=3,
        )
        assert not result.empty
        assert int(result.iloc[0]["n_groups"]) == 5
        assert result.iloc[0]["missing"] == []


class TestMaxGaps:
    """Правило проекта: в серии допускается не более 1 пропуска."""

    DELTA = 17.03448

    def test_default_value_is_zero(self):
        """По умолчанию пропуски запрещены."""
        import inspect

        sig = inspect.signature(find_series)
        assert sig.parameters["max_gaps"].default == 0

    def test_negative_raises(self):
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([117.03448])
        with pytest.raises(ValueError, match="max_gaps"):
            find_series(src, deriv, self.DELTA, max_gaps=-1)

    def test_one_gap_allowed_by_default(self):
        """Ступени 1 и 3 (пропуск 2) — серия принимается: пропуск ровно один."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([100.0 + self.DELTA, 100.0 + 3 * self.DELTA])
        result = find_series(src, deriv, self.DELTA, max_groups=5, max_gaps=1)
        assert not result.empty
        row = result.iloc[0]
        assert int(row["n_groups"]) == 3
        assert row["missing"] == [2]

    def test_second_gap_truncates_series(self):
        """Ступени 1, 3, 5 — уже два пропуска: серия обрывается перед вторым."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum(
            [100.0 + self.DELTA, 100.0 + 3 * self.DELTA, 100.0 + 5 * self.DELTA]
        )
        result = find_series(src, deriv, self.DELTA, max_groups=6, max_gaps=1)
        assert not result.empty
        row = result.iloc[0]
        # обрыв на последней найденной ступени до исчерпания бюджета
        assert int(row["n_groups"]) == 3
        assert row["missing"] == [2]

    def test_zero_gaps_disabled(self):
        """max_gaps=0 — пропуски запрещены: серия обрывается на первом пропуске."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([100.0 + self.DELTA, 100.0 + 3 * self.DELTA])
        result = find_series(src, deriv, self.DELTA, max_groups=5, max_gaps=0)
        assert not result.empty
        row = result.iloc[0]
        assert int(row["n_groups"]) == 1
        assert row["missing"] == []

    def test_allow_gaps_false_is_alias_for_zero(self):
        """Устаревший allow_gaps=False эквивалентен max_gaps=0."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([100.0 + self.DELTA, 100.0 + 3 * self.DELTA])
        result = find_series(src, deriv, self.DELTA, max_groups=5, allow_gaps=False)
        assert int(result.iloc[0]["n_groups"]) == 1
        assert result.iloc[0]["missing"] == []

    def test_user_can_widen_budget(self):
        """Пользователь может разрешить больше пропусков (например, 2)."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum(
            [100.0 + self.DELTA, 100.0 + 3 * self.DELTA, 100.0 + 5 * self.DELTA]
        )
        result = find_series(src, deriv, self.DELTA, max_groups=6, max_gaps=2)
        row = result.iloc[0]
        assert int(row["n_groups"]) == 5
        assert row["missing"] == [2, 4]

    def test_budget_is_never_exceeded(self):
        """Инвариант: len(missing) <= max_gaps для любой серии."""
        src = _make_src_spectrum([100.0, 200.0])
        deriv = _make_deriv_spectrum(
            [
                100.0 + self.DELTA,
                100.0 + 3 * self.DELTA,
                100.0 + 5 * self.DELTA,
                200.0 + self.DELTA,
                200.0 + 4 * self.DELTA,
            ]
        )
        for budget in (0, 1, 2):
            result = find_series(src, deriv, self.DELTA, max_groups=6, max_gaps=budget)
            for _, row in result.iterrows():
                assert len(row["missing"]) <= budget, (budget, row["missing"])


class TestRequireFirstStep:
    """Точность прежде полноты: без первой ступени серия не считается."""

    DELTA = 17.03448

    def test_default_is_true(self):
        import inspect

        sig = inspect.signature(find_series)
        assert sig.parameters["require_first_step"].default is False

    def test_series_without_first_step_is_rejected(self):
        """Ступени 2,3,4 без ступени 1 — случайные совпадения, не серия."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum(
            [100.0 + 2 * self.DELTA, 100.0 + 3 * self.DELTA, 100.0 + 4 * self.DELTA]
        )
        result = find_series(
            src, deriv, self.DELTA, max_groups=6, require_first_step=True
        )
        assert result.empty

    def test_series_without_first_step_kept_when_disabled(self):
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum(
            [100.0 + 2 * self.DELTA, 100.0 + 3 * self.DELTA, 100.0 + 4 * self.DELTA]
        )
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=6,
            max_gaps=1,
            require_first_step=False,
        )
        assert not result.empty
        row = result.iloc[0]
        assert int(row["n_groups"]) == 4
        assert row["missing"] == [1]

    def test_first_three_missing_rejected_even_if_disabled(self):
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([100.0 + n * self.DELTA for n in (4, 5, 6)])
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=8,
            max_gaps=3,
            require_first_step=False,
        )
        assert result.empty

    def test_first_step_present_with_internal_gap_is_kept(self):
        """Ступени 1 и 3 (один пропуск) — серия подтверждена первой ступенью."""
        src = _make_src_spectrum([100.0])
        deriv = _make_deriv_spectrum([100.0 + self.DELTA, 100.0 + 3 * self.DELTA])
        result = find_series(src, deriv, self.DELTA, max_groups=5, max_gaps=1)
        assert not result.empty
        row = result.iloc[0]
        assert int(row["n_groups"]) == 3
        assert row["missing"] == [2]


class TestIntensityProfile:
    """Опциональный критерий профиля интенсивностей продуктов (по умолчанию выкл.)."""

    DELTA = 17.03448

    def _spec_with_intensities(self, intensities):
        masses = [100.0 + (i + 1) * self.DELTA for i in range(len(intensities))]
        return _make_deriv_spectrum(masses, intensities=intensities)

    def test_default_is_off(self):
        import inspect

        sig = inspect.signature(find_series)
        assert sig.parameters["profile_check"].default is False

    def test_big_jump_accepted_when_disabled(self):
        src = _make_src_spectrum([100.0])
        deriv = self._spec_with_intensities([1.0, 1000.0])
        result = find_series(src, deriv, self.DELTA, max_groups=5)
        assert not result.empty

    def test_big_jump_rejected_when_enabled(self):
        src = _make_src_spectrum([100.0])
        deriv = self._spec_with_intensities([1.0, 1000.0])
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=5,
            profile_check=True,
            profile_max_jump=10.0,
        )
        assert not result.empty
        row = result.iloc[0]
        assert bool(row["profile_ok"]) is False
        assert any(
            "intensity_profile" in d.get("penalties", {}) for d in row["step_details"]
        )

    def test_smooth_profile_accepted(self):
        src = _make_src_spectrum([100.0])
        deriv = self._spec_with_intensities([1000.0, 700.0, 400.0, 150.0])
        result = find_series(src, deriv, self.DELTA, max_groups=5, profile_check=True)
        assert not result.empty
        row = result.iloc[0]
        assert bool(row["profile_ok"]) is True
        assert float(row["max_jump"]) <= 10.0

    def test_growing_intensities_rejected_by_correlation(self):
        src = _make_src_spectrum([100.0])
        deriv = self._spec_with_intensities([10.0, 100.0, 1000.0])
        result = find_series(
            src,
            deriv,
            self.DELTA,
            max_groups=5,
            profile_check=True,
            profile_max_jump=None,
            profile_max_corr=0.5,
        )
        assert not result.empty
        row = result.iloc[0]
        assert bool(row["profile_ok"]) is False
        assert any(
            "intensity_profile" in d.get("penalties", {}) for d in row["step_details"]
        )


class TestSeriesPolicy:
    """O-лимит, confirmed/ambiguous и причины в step_details."""

    DELTA = 17.03448
    DELTA_CO = 45.02939

    def _src(self, masses, brutto="C7H6O2", assigns=None, iso_status=None):
        df = pd.DataFrame(
            {
                "mass": masses,
                "brutto": [brutto] * len(masses),
                "assign": assigns or [True] * len(masses),
            }
        )
        if iso_status is not None:
            df["iso_status"] = [iso_status] * len(masses)
        return Spectrum(table=df)

    def test_cd3_o_limit_is_half_oxygen(self):
        src = self._src([100.0])
        deriv = _make_deriv_spectrum([100.0 + n * self.DELTA for n in (1, 2, 3)])
        row = find_series(src, deriv, self.DELTA, max_groups=5).iloc[0]
        assert row["o_limit"] == 1
        assert row["confirmed_length"] == 1
        assert row["ambiguous_length"] == 3
        assert row["display_length"] == "1(3)"
        reasons = row["step_details"][1]["reasons"]
        assert any("кислород" in r for r in reasons)

    def test_cd3co_o_limit_is_oxygen(self):
        src = self._src([100.0])
        deriv = _make_deriv_spectrum([100.0 + n * self.DELTA_CO for n in (1, 2, 3)])
        row = find_series(src, deriv, self.DELTA_CO, max_groups=5).iloc[0]
        assert row["o_limit"] == 2
        assert row["confirmed_length"] == 2
        assert row["ambiguous_length"] == 3
        assert row["display_length"] == "2(3)"

    def test_source_overlap_makes_step_ambiguous(self):
        src = self._src([100.0, 100.0 + self.DELTA], assigns=[True, False])
        deriv = _make_deriv_spectrum([100.0 + n * self.DELTA for n in (1, 2, 3)])
        row = find_series(src, deriv, self.DELTA, max_groups=5).iloc[0]
        assert row["confirmed_length"] == 0
        assert row["ambiguous_length"] == 3
        assert row["display_length"] == "0(3)"
        assert row["step_details"][0]["n_src"] == 1
        assert any("исходного" in r for r in row["step_details"][0]["reasons"])

    def test_isotope_inconsistent_is_penalized(self):
        src = self._src([100.0], iso_status="inconsistent")
        deriv = _make_deriv_spectrum([100.0 + n * self.DELTA for n in (1, 2)])
        row = find_series(src, deriv, self.DELTA, max_groups=5).iloc[0]
        assert row["confirmed_length"] == 0
        assert row["step_details"][0]["confidence"] <= 70
        assert any("изотоп" in r for r in row["step_details"][0]["reasons"])

    def test_conflict_without_previous_step_is_penalized(self):
        src = self._src([100.0, 100.0 + self.DELTA])
        deriv = _make_deriv_spectrum(
            [
                100.0 + self.DELTA,
                100.0 + 2 * self.DELTA,
                100.0 + 3 * self.DELTA,
            ]
        )
        result = find_series(src, deriv, self.DELTA, max_groups=5, max_gaps=1)
        assert not result.empty
        # Якорь 117.03448: его шаг 1 — это шаг 2 якоря 100. У него нет
        # предыдущей ступени, поэтому должен быть дополнительный штраф.
        row_b = result[result["mass_src"].round(5) == round(100.0 + self.DELTA, 5)]
        assert not row_b.empty
        details = row_b.iloc[0]["step_details"]
        assert any("conflict_no_prev" in d.get("penalties", {}) for d in details)

    def test_gap_has_reason_and_confidence(self):
        src = self._src([100.0])
        deriv = _make_deriv_spectrum([100.0 + self.DELTA, 100.0 + 3 * self.DELTA])
        row = find_series(src, deriv, self.DELTA, max_groups=5, max_gaps=1).iloc[0]
        gap = row["step_details"][1]
        assert gap["status"] == "gap"
        assert gap["confidence"] == 85.0
        assert gap["reasons"] == ["пропуск шага"]
