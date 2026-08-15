"""Series-verification helpers for the pipeline test mode."""

from src.configs import PATHS
from src.core.spectrum import DELTA_CD3, DELTA_CD3CO
from ._helpers import _debug


def _verify_series_against_annotations(
    set_dir, ann_orig, molecules, df_dmet_res, df_dacet_res, res, match_ppm
):
    """Compare detected dmet/dacet series against ground-truth annotations."""
    _sf = PATHS.spectrum_files
    # ── Сверка серий с annotations ───────────────────────────────────────
    _dm_file = _sf["deutermethylated"]
    _da_file = _sf["deuteroacylated"]
    for (
        deriv_file,
        delta,
        deriv_label,
        sp_result,
        res_found_attr,
        res_matched_attr,
        res_wrong_attr,
    ) in [
        (
            _dm_file,
            DELTA_CD3,
            "dmet",
            df_dmet_res,
            "dmet_found",
            "dmet_matched",
            "dmet_wrong",
        ),
        (
            _da_file,
            DELTA_CD3CO,
            "dacet",
            df_dacet_res,
            "dacet_found",
            "dacet_matched",
            "dacet_wrong",
        ),
    ]:
        if sp_result.empty:
            _debug(f"{set_dir.name} {deriv_label}: результат пустой, сверка невозможна")
            continue

        # Проверяем обязательные колонки
        expected_cols = {
            "mass_src",
            "brutto",
            "n_groups",
            "steps_found",
            "missing",
            "series_mz",
        }
        actual_cols = set(sp_result.columns)
        missing_result_cols = expected_cols - actual_cols
        if missing_result_cols:
            msg = f"{deriv_label} result: отсутствуют колонки {sorted(missing_result_cols)}, есть {sorted(actual_cols)}"
            print(f"  [WARN] {msg}")
            res.errors.append(msg)

        matched_series = 0
        wrong_length = []
        missing_series = []

        for _, ann_row in ann_orig.iterrows():
            mass_obs = float(ann_row["mass_obs"])
            compound_num = int(ann_row["compound_number"])

            # Ожидаемая длина серии из molecules.csv
            expected_len = None
            if not molecules.empty and "compound_number" in molecules.columns:
                mol_match = molecules.loc[molecules["compound_number"] == compound_num]
                if not mol_match.empty:
                    mol_row = mol_match.iloc[0]
                    if deriv_file == _dm_file and "carboxyl_count" in mol_row:
                        expected_len = int(mol_row["carboxyl_count"])
                    elif deriv_file == _da_file and "hydroxyl_count" in mol_row:
                        expected_len = int(mol_row["hydroxyl_count"])

            # Ищем строку в результате
            if "mass_src" not in sp_result.columns:
                continue
            diff = (sp_result["mass_src"] - mass_obs).abs()
            tol_da = mass_obs * match_ppm * 1e-6
            candidates = sp_result.loc[diff <= tol_da]
            if candidates.empty:
                missing_series.append(
                    {
                        "mass_obs": mass_obs,
                        "compound_number": compound_num,
                        "expected_len": expected_len,
                    }
                )
                continue

            matched_series += 1
            result_row = candidates.iloc[0]

            if expected_len is not None and "n_groups" in result_row:
                actual_len = int(result_row["n_groups"])
                if actual_len != expected_len:
                    wrong_length.append(
                        {
                            "mass_obs": mass_obs,
                            "compound_number": compound_num,
                            "expected": expected_len,
                            "actual": actual_len,
                        }
                    )

        setattr(res, res_matched_attr, matched_series)
        wrong_count = len(missing_series) + len(wrong_length)
        setattr(res, res_wrong_attr, wrong_count)

        wrong_ratio = wrong_count / res.total_signals if res.total_signals else 0.0
        _debug(
            f"{set_dir.name} {deriv_label}: "
            f"matched={matched_series}/{res.total_signals}, "
            f"missing={len(missing_series)}, wrong_len={len(wrong_length)}, "
            f"wrong_ratio={wrong_ratio:.3f}"
        )
        if missing_series:
            _debug(f"  missing_series (первые 3): {missing_series[:3]}")
        if wrong_length:
            _debug(f"  wrong_length (первые 3): {wrong_length[:3]}")
        print(
            f"  {deriv_label}: found={getattr(res, res_found_attr)}, "
            f"matched={matched_series}/{res.total_signals}, "
            f"wrong={wrong_count} ({wrong_ratio:.1%})"
        )
