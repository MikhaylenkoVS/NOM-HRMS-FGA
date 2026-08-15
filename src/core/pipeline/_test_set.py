"""Single test-set execution for the pipeline test mode."""

import traceback
from pathlib import Path

import pandas as pd

from src.configs import PIPELINE, PATHS
from src.core.spectrum import (
    load_spectrum,
    denoise,
    assign_formulas,
    find_series,
    build_result_table,
    DELTA_CD3,
    DELTA_CD3CO,
)
from ._stats import TestSetResult
from ._helpers import _debug, _match_row_by_mass, _normalize_brutto
from ._test_verify import _verify_series_against_annotations

#: Tolerance (ppm) used to match annotation masses against detected peaks/series.
_TEST_MATCH_PPM = PIPELINE.test_mode["match_ppm"]


def _run_single_test_set(
    set_dir: Path,
    noise_force,
    noise_intensity,
    noise_quantile,
    assign_mass_min,
    assign_mass_max,
    rel_error,
    sign,
    ppm_tol,
    max_groups,
    allow_gaps,
) -> TestSetResult:
    """Run the full pipeline on a single test-set directory.

    Parameters
    ----------
    set_dir : pathlib.Path
        Directory of one test set containing ``original.csv``,
        ``deutermethylated.csv``, ``deuteroacylated.csv`` and ground-truth
        annotations.
    noise_force, noise_intensity, noise_quantile : optional
        Denoising parameters.
    assign_mass_min, assign_mass_max : float or None
        Mass window for formula assignment.
    rel_error : float
        Mass tolerance (ppm) for assignment.
    sign : {'-', '+'}
        Ionization sign.
    ppm_tol : float
        Series-matching tolerance (ppm).
    max_groups : int
        Maximum functional groups probed per molecule.
    allow_gaps : bool
        Whether to tolerate gaps within a series.

    Returns
    -------
    TestSetResult
        Validation metrics for the set. Never raises; errors are captured in
        the result's ``errors`` list.
    """

    res = TestSetResult(set_name=set_dir.name)
    sep_line = "─" * 60

    print(sep_line)
    print(f"  SET: {set_dir.name}  ({set_dir})")
    print(sep_line)

    # ── загрузка annotations ──────────────────────────────────────────────
    _sf = PATHS.spectrum_files
    ann_path = set_dir / _sf["annotations"]
    molecules_path = set_dir / _sf["molecules"]
    original_path = set_dir / _sf["original"]
    dmet_path = set_dir / _sf["deutermethylated"]
    dacet_path = set_dir / _sf["deuteroacylated"]

    # Проверяем наличие файлов
    for fpath, label in [
        (ann_path, _sf["annotations"]),
        (molecules_path, _sf["molecules"]),
        (original_path, _sf["original"]),
        (dmet_path, _sf["deutermethylated"]),
        (dacet_path, _sf["deuteroacylated"]),
    ]:
        if not fpath.exists():
            msg = f"файл не найден: {fpath}"
            print(f"  [ERROR] {msg}")
            res.errors.append(msg)

    if res.errors:
        print(f"  Пропускаем {set_dir.name} из-за отсутствующих файлов")
        return res

    # ── читаем annotations ───────────────────────────────────────────────
    try:
        ann = pd.read_csv(ann_path)
        _debug(
            f"{set_dir.name} annotations: {len(ann)} строк, колонки={list(ann.columns)}"
        )
        required_cols = {
            "spectrum_type",
            "is_signal",
            "mass_obs",
            "compound_number",
            "formula",
        }
        missing_cols = required_cols - set(ann.columns)
        if missing_cols:
            msg = f"annotations.csv: отсутствуют колонки {sorted(missing_cols)}"
            print(f"  [ERROR] {msg}")
            res.errors.append(msg)
            return res
        ann_orig = ann[
            (ann["spectrum_type"] == "original")
            & (ann["is_signal"] == True)  # noqa: E712
        ].copy()  # noqa: E712
        _debug(f"{set_dir.name} ann_orig (original+is_signal): {len(ann_orig)} строк")
        res.total_signals = len(ann_orig)
    except Exception as e:
        msg = f"ошибка чтения annotations: {e}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        return res

    # ── читаем molecules ─────────────────────────────────────────────────
    molecules = pd.DataFrame()
    try:
        molecules = pd.read_csv(molecules_path)
        _debug(
            f"{set_dir.name} molecules: {len(molecules)} строк, колонки={list(molecules.columns)}"
        )
    except Exception as e:
        msg = f"ошибка чтения molecules: {e}"
        print(f"  [WARN] {msg}")
        res.errors.append(msg)

    # ── загружаем спектры ────────────────────────────────────────────────
    _load_cfg = PIPELINE.test_mode["load"]
    try:
        src = load_spectrum(
            original_path,
            mass_min=_load_cfg["original_mass_min"],
            mass_max=_load_cfg["original_mass_max"],
        )
        _debug(f"{set_dir.name} original loaded: {len(src.table)} строк")
    except Exception as e:
        msg = f"load_spectrum original: {e}\n{traceback.format_exc()}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        return res

    try:
        dmet_sp = load_spectrum(
            dmet_path,
            mass_min=_load_cfg["derivatized_mass_min"],
            mass_max=_load_cfg["derivatized_mass_max"],
        )
        _debug(f"{set_dir.name} dmet loaded: {len(dmet_sp.table)} строк")
    except Exception as e:
        msg = f"load_spectrum dmet: {e}\n{traceback.format_exc()}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        dmet_sp = None

    try:
        dacet_sp = load_spectrum(
            dacet_path,
            mass_min=_load_cfg["derivatized_mass_min"],
            mass_max=_load_cfg["derivatized_mass_max"],
        )
        _debug(f"{set_dir.name} dacet loaded: {len(dacet_sp.table)} строк")
    except Exception as e:
        msg = f"load_spectrum dacet: {e}\n{traceback.format_exc()}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        dacet_sp = None

    # ── денойс ──────────────────────────────────────────────────────────
    try:
        src_d = denoise(
            src, force=noise_force, intensity=noise_intensity, quantile=noise_quantile
        )
        _debug(
            f"{set_dir.name} denoised: {len(src_d.table)} строк (было {len(src.table)})"
        )
    except Exception as e:
        msg = f"denoise: {e}\n{traceback.format_exc()}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        src_d = src

    # Проверяем, сколько сигналов из annotations сохранилось после денойса
    denoised_kept = 0
    denoise_missing = []
    for _, row in ann_orig.iterrows():
        mass_obs = float(row["mass_obs"])
        match = _match_row_by_mass(
            src_d.table, mass_obs, ppm_tol=_TEST_MATCH_PPM, require_assigned=False
        )
        if match is None:
            denoise_missing.append(
                {"mass_obs": mass_obs, "compound_number": row.get("compound_number")}
            )
        else:
            denoised_kept += 1
    res.denoised_kept = denoised_kept
    denoise_recall = denoised_kept / res.total_signals if res.total_signals else 0.0
    _debug(
        f"{set_dir.name} denoise recall: {denoised_kept}/{res.total_signals} = {denoise_recall:.3f}"
    )
    if denoise_missing:
        _debug(f"{set_dir.name} denoise missing (первые 3): {denoise_missing[:3]}")

    # ── assign_formulas ─────────────────────────────────────────────────
    try:
        src_a = assign_formulas(
            src_d,
            rel_error_ppm=rel_error,
            mass_min=assign_mass_min,
            mass_max=assign_mass_max,
        )
        _debug(f"{set_dir.name} assign_formulas: колонки={list(src_a.table.columns)}")
        if "assign" not in src_a.table.columns:
            msg = "assign_formulas не создала колонку 'assign'"
            print(f"  [ERROR] {msg}")
            res.errors.append(msg)
            return res
        if "brutto" not in src_a.table.columns:
            msg = "assign_formulas не создала колонку 'brutto'"
            print(f"  [ERROR] {msg}")
            res.errors.append(msg)
            return res
    except Exception as e:
        msg = f"assign_formulas: {e}\n{traceback.format_exc()}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        return res

    # assigned_only: только назначенные
    try:
        assigned_only = (
            src_a.table.loc[src_a.table["assign"] == True]  # noqa: E712
            .reset_index(drop=True)
            .copy()  # noqa: E712
        )  # noqa: E712
        _debug(f"{set_dir.name} assigned_only: {len(assigned_only)} строк")
        if assigned_only.empty:
            msg = "assigned_only пуст – find_series не найдёт серий!"
            print(f"  [WARN] {msg}")
            res.errors.append(msg)
    except Exception as e:
        msg = f"assigned_only: {e}"
        print(f"  [ERROR] {msg}")
        res.errors.append(msg)
        assigned_only = pd.DataFrame()

    res.assigned_only = assigned_only

    # Считаем assign_recall по annotations
    assigned_ok = 0
    assign_missing = []
    wrong_brutto = []
    for _, row in ann_orig.iterrows():
        mass_obs = float(row["mass_obs"])
        formula_true = _normalize_brutto(str(row["formula"]))
        match = _match_row_by_mass(
            src_a.table, mass_obs, ppm_tol=_TEST_MATCH_PPM, require_assigned=True
        )
        if match is None:
            assign_missing.append(
                {"mass_obs": mass_obs, "compound_number": row.get("compound_number")}
            )
            continue
        brutto_found = _normalize_brutto(match.get("brutto"))
        if brutto_found != formula_true:
            wrong_brutto.append(
                {
                    "mass_obs": mass_obs,
                    "compound_number": row.get("compound_number"),
                    "expected": formula_true,
                    "actual": brutto_found,
                }
            )
            continue
        assigned_ok += 1

    res.assigned_ok = assigned_ok
    assign_recall = assigned_ok / res.total_signals if res.total_signals else 0.0
    _debug(
        f"{set_dir.name} assign recall: {assigned_ok}/{res.total_signals} = {assign_recall:.3f}"
    )
    if assign_missing:
        _debug(f"{set_dir.name} assign missing (первые 3): {assign_missing[:3]}")
    if wrong_brutto:
        _debug(f"{set_dir.name} wrong brutto (первые 3): {wrong_brutto[:3]}")

    print(
        f"  denoise recall: {denoised_kept}/{res.total_signals} = {denoise_recall:.1%}"
    )
    print(f"  assign  recall: {assigned_ok}/{res.total_signals} = {assign_recall:.1%}")

    # ── Создаём Spectrum для assigned_only ───────────────────────────────
    # Нужен для find_series (передаём весь src_a, а не только assigned)
    # find_series берёт только назначенные пики по логике внутри себя
    # Но если у нас есть отдельный объект с assigned_only – используем его

    # Оборачиваем assigned_only в Spectrum
    try:
        src_assigned_only_sp = src_a.copy()
        src_assigned_only_sp.table = assigned_only
    except Exception as e:
        _debug(
            f"{set_dir.name} не удалось создать assigned_only Spectrum: {e}, используем src_a"
        )
        src_assigned_only_sp = src_a

    # ── find_series: dmet ────────────────────────────────────────────────
    _min_series_len = PIPELINE.test_mode["series"]["min_series_length"]
    df_dmet_res = pd.DataFrame()
    if dmet_sp is not None and not assigned_only.empty:
        try:
            df_dmet_res = find_series(
                src_assigned_only_sp,
                dmet_sp,
                delta=DELTA_CD3,
                ppm_tol=ppm_tol,
                max_groups=max_groups,
                allow_gaps=allow_gaps,
                min_series_length=_min_series_len,
            )
            res.dmet_found = len(df_dmet_res)
            _debug(f"{set_dir.name} find_series(dmet): {len(df_dmet_res)} строк")
            _debug(
                f"  Колонки: {list(df_dmet_res.columns) if not df_dmet_res.empty else '[]'}"
            )
            if not df_dmet_res.empty:
                _debug(f"Превью df_dmet:\n{df_dmet_res.head(3).to_string(index=False)}")
        except Exception as e:
            msg = f"find_series(dmet): {e}\n{traceback.format_exc()}"
            print(f"  [ERROR] {msg}")
            res.errors.append(msg)
    else:
        if dmet_sp is None:
            _debug(f"{set_dir.name} dmet_sp=None, пропускаем find_series(dmet)")
        if assigned_only.empty:
            _debug(f"{set_dir.name} assigned_only пуст, пропускаем find_series(dmet)")

    # ── find_series: dacet ───────────────────────────────────────────────
    df_dacet_res = pd.DataFrame()
    if dacet_sp is not None and not assigned_only.empty:
        try:
            df_dacet_res = find_series(
                src_assigned_only_sp,
                dacet_sp,
                delta=DELTA_CD3CO,
                ppm_tol=ppm_tol,
                max_groups=max_groups,
                allow_gaps=allow_gaps,
                min_series_length=_min_series_len,
            )
            res.dacet_found = len(df_dacet_res)
            _debug(f"{set_dir.name} find_series(dacet): {len(df_dacet_res)} строк")
        except Exception as e:
            msg = f"find_series(dacet): {e}\n{traceback.format_exc()}"
            print(f"  [ERROR] {msg}")
            res.errors.append(msg)

    # ── Сверка серий с annotations ───────────────────────────────────────
    _verify_series_against_annotations(
        set_dir, ann_orig, molecules, df_dmet_res, df_dacet_res, res, _TEST_MATCH_PPM
    )
    # ── итоговая таблица для сета ────────────────────────────────────────
    result_table = pd.DataFrame()
    try:
        result_table = build_result_table(src_a, df_dmet_res, df_dacet_res)
        res.result_table = result_table
        _debug(f"{set_dir.name} build_result_table: {len(result_table)} строк")
    except Exception as e:
        msg = f"build_result_table: {e}"
        print(f"  [WARN] {msg}")
        res.errors.append(msg)

    # Итог по сету
    print(
        f"  ИТОГ {set_dir.name}: "
        f"denoise={denoise_recall:.1%}, assign={assign_recall:.1%}, "
        f"errors={len(res.errors)}"
    )
    if res.errors:
        print(f"  ОШИБКИ ({len(res.errors)}):")
        for err in res.errors:
            short = err[:200].replace("\n", " | ")
            print(f"    • {short}")
    print()

    return res
