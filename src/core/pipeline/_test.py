"""Pipeline test mode."""

import logging, traceback
from pathlib import Path
import pandas as pd
from src.configs import PIPELINE, PATHS, CHEM
from src.core.spectrum import (
    load_spectrum,
    denoise,
    assign_formulas,
    find_series,
    build_result_table,
    DELTA_CD3,
    DELTA_CD3CO,
)
from ._stats import TestSetResult, PipelineStats
from ._helpers import _debug, _match_row_by_mass, _normalize_brutto

logger = logging.getLogger(__name__)

#: Конфигурация дериватизации для тест-режима:
#: имена файлов из paths.json, сдвиги масс из chemistry.json.
_DERIV_SPECS = [
    (
        PATHS.spectrum_files["deutermethylated"],
        DELTA_CD3,
        "deutermethylated",
    ),
    (
        PATHS.spectrum_files["deuteroacylated"],
        DELTA_CD3CO,
        "deuteroacylated",
    ),
]
_TEST_MATCH_PPM = PIPELINE.test_mode["match_ppm"]


def _run_test_mode(
    test_sets_root=None,
    noise_force=10.0,
    noise_intensity=100,
    noise_quantile=None,
    assign_mass_min=None,
    assign_mass_max=None,
    rel_error=0.5,
    sign="-",
    ppm_tol=0.5,
    max_groups=20,
    allow_gaps=True,
) -> list[TestSetResult]:
    """Run the pipeline over every ``set_0N`` and print detailed statistics.

    Parameters
    ----------
    test_sets_root : str, path-like or None, optional
        Root directory holding the ``set_0*`` folders. If ``None``, it is
        auto-detected relative to the repository, falling back to
        ``<cwd>/data/test_sets``.
    noise_force, noise_intensity, noise_quantile : optional
        Denoising parameters.
    assign_mass_min, assign_mass_max : float or None, optional
        Mass window for formula assignment.
    rel_error : float, optional
        Mass tolerance (ppm) for assignment. Default 0.5.
    sign : {'-', '+'}, optional
        Ionization sign. Default ``'-'``.
    ppm_tol : float, optional
        Series-matching tolerance (ppm). Default 0.5.
    max_groups : int, optional
        Maximum functional groups probed per molecule. Default 20.
    allow_gaps : bool, optional
        Whether to tolerate gaps within a series. Default ``True``.

    Returns
    -------
    list of TestSetResult
        One result per test set; empty if the root or sets are missing.
    """

    # Resolve roots
    if test_sets_root is None:
        # Автоопределение: ищем через paths.json относительно текущего файла
        candidate = Path(__file__).resolve().parents[2] / PATHS.test_sets_dir
        if candidate.exists():
            test_sets_root = candidate
        else:
            # fallback: текущая рабочая директория
            test_sets_root = Path.cwd() / PATHS.test_sets_dir
    test_sets_root = Path(test_sets_root)

    print("=" * 70)
    print("ТЕСТ-РЕЖИМ pipeline.py")
    print(f"  test_sets_root = {test_sets_root}")
    print(f"  exists         = {test_sets_root.exists()}")
    print("=" * 70)

    if not test_sets_root.exists():
        logger.error(
            f"[TEST] ОШИБКА: директория тест-сетов не найдена: {test_sets_root}",
        )
        return []

    test_sets = sorted(p for p in test_sets_root.glob("set_0*") if p.is_dir())
    if not test_sets:
        logger.error(
            f"[TEST] ОШИБКА: не найдено ни одного set* в {test_sets_root}",
        )
        return []

    print(f"  Найдено сетов: {len(test_sets)} → {[p.name for p in test_sets]}")
    print()

    results: list[TestSetResult] = []
    all_errors: list[str] = []

    for set_dir in test_sets:
        res = _run_single_test_set(
            set_dir=set_dir,
            noise_force=noise_force,
            noise_intensity=noise_intensity,
            noise_quantile=noise_quantile,
            assign_mass_min=assign_mass_min,
            assign_mass_max=assign_mass_max,
            rel_error=rel_error,
            sign=sign,
            ppm_tol=ppm_tol,
            max_groups=max_groups,
            allow_gaps=allow_gaps,
        )
        results.append(res)
        if res.errors:
            all_errors.extend([f"[{res.set_name}] {e}" for e in res.errors])

    # -----------------------------------------------------------------------
    # Итоговая сводная статистика
    # -----------------------------------------------------------------------
    print()
    print("=" * 70)
    print("ИТОГОВАЯ СВОДНАЯ СТАТИСТИКА (тест-режим)")
    print("=" * 70)
    header = (
        f"{'Set':<8}"
        f"{'Signals':>8}"
        f"{'Denoised':>10}"
        f"{'D-Rec%':>8}"
        f"{'Assigned':>10}"
        f"{'A-Rec%':>8}"
        f"{'DmetFnd':>9}"
        f"{'DmetOk':>8}"
        f"{'DacetFnd':>10}"
        f"{'DacetOk':>9}"
        f"{'Errors':>7}"
    )
    print(header)
    print("-" * 97)
    for r in results:
        dr = r.denoise_recall * 100
        ar = r.assign_recall * 100
        errs = len(r.errors)
        print(
            f"{r.set_name:<8}"
            f"{r.total_signals:>8}"
            f"{r.denoised_kept:>10}"
            f"{dr:>7.1f}%"
            f"{r.assigned_ok:>10}"
            f"{ar:>7.1f}%"
            f"{r.dmet_found:>9}"
            f"{r.dmet_matched:>8}"
            f"{r.dacet_found:>10}"
            f"{r.dacet_matched:>9}"
            f"{errs:>7}"
        )
    print("-" * 97)

    if all_errors:
        print()
        print(f"НАКОПЛЕННЫЕ ОШИБКИ ({len(all_errors)} шт.):")
        for e in all_errors:
            print(f"  {e}")

    # Проверки на пороги
    print()
    print("ПРОВЕРКА ПОРОГОВ:")
    # Pass/fail thresholds (single source of truth: pipeline.json -> thresholds).
    MIN_DENOISE_RECALL = PIPELINE.thresholds["min_denoise_recall"]
    MIN_ASSIGN_RECALL = PIPELINE.thresholds["min_assign_recall"]
    MAX_WRONG_RATIO = PIPELINE.thresholds["max_wrong_ratio"]
    any_fail = False
    for r in results:
        if r.denoise_recall < MIN_DENOISE_RECALL:
            print(
                f"  FAIL denoise  {r.set_name}: {r.denoise_recall:.3f} < {MIN_DENOISE_RECALL}"
            )
            any_fail = True
        if r.assign_recall < MIN_ASSIGN_RECALL:
            print(
                f"  FAIL assign   {r.set_name}: {r.assign_recall:.3f} < {MIN_ASSIGN_RECALL}"
            )
            any_fail = True
        total = r.total_signals
        dmet_wrong_ratio = r.dmet_wrong / total if total else 0
        dacet_wrong_ratio = r.dacet_wrong / total if total else 0
        if dmet_wrong_ratio > MAX_WRONG_RATIO:
            print(
                f"  FAIL dmet_wrong {r.set_name}: {dmet_wrong_ratio:.3f} > {MAX_WRONG_RATIO}"
            )
            any_fail = True
        if dacet_wrong_ratio > MAX_WRONG_RATIO:
            print(
                f"  FAIL dacet_wrong {r.set_name}: {dacet_wrong_ratio:.3f} > {MAX_WRONG_RATIO}"
            )
            any_fail = True
    if not any_fail:
        print("  Все пороги пройдены ✓")

    return results


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
            (ann["spectrum_type"] == "original") & (ann["is_signal"] == True)
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
            src_a.table.loc[src_a.table["assign"] == True].reset_index(drop=True).copy()
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
            tol_da = mass_obs * _TEST_MATCH_PPM * 1e-6
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


# ---------------------------------------------------------------------------
# Точка входа командной строки
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="pipeline.py – анализ масс-спектров гуминовых веществ"
    )
    parser.add_argument(
        "--test", action="store_true", help="Запустить тест-режим по set_01..set_05"
    )
    parser.add_argument(
        "--sets-root", type=str, default=None, help="Путь к директории с тест-сетами"
    )
    args = parser.parse_args()

    if args.test:
        run_pipeline(test_mode=True, test_sets_root=args.sets_root)
    else:
        print(
            "Используйте --test для запуска тест-режима, или импортируйте run_pipeline() из кода."
        )
