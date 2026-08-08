"""run_pipeline — main pipeline entry point."""

import logging, traceback, os, time
import pandas as pd
from pathlib import Path
from typing import Optional
from src.configs import CHEM, PIPELINE, PATHS
from ._cache import _pipeline_cache, _result_cache, PipelineProgress
from ._helpers import _debug, _normalize_brutto, _ppm_error
from ._stats import PipelineStats, PipelineRunResult, SeriesStats
from ._test import _run_test_mode
from src.core.timer import PipelineTimings

# ---------------------------------------------------------------------------
try:
    from src.core.spectrum import (
        Spectrum,
        load_spectrum,
        denoise,
        assign_formulas,
        find_series,
        build_result_table,
        visualize_series,
        DELTA_CD3,
        DELTA_CD3CO,
    )

    _IMPORT_ERROR: Optional[str] = None
except Exception as _e:
    _IMPORT_ERROR = str(_e)
    logger.error(
        f"[PIPELINE] CRITICAL: не удалось импортировать spectrum_ops: {_e}",
    )
logger = logging.getLogger(__name__)


def _make_sub_progress(progress_callback, base_pct, range_pct, label_tpl):
    """Create a per-step callback that maps ``(step, total)`` → absolute %.

    Parameters
    ----------
    progress_callback : callable or None
        Outer callback ``(label, pct) → None``.
    base_pct : int
        Starting percentage for this sub-stage.
    range_pct : int
        Width of the percentage range allocated to this sub-stage.
    label_tpl : str
        Template string with ``{0}`` = step, ``{1}`` = total.
    """
    if not progress_callback:
        return None

    def cb(step, total):
        pct = base_pct + int(step / max(total, 1) * range_pct)
        progress_callback(label_tpl.format(step, total), pct)

    return cb


def run_pipeline(
    src_path=None,
    dmet_path=None,
    dacet_path=None,
    *,
    # Загрузка (defaults: pipeline.json -> run_pipeline_defaults)
    sep=PIPELINE.run_pipeline_defaults["sep"],
    load_mass_min: float = PIPELINE.run_pipeline_defaults["load_mass_min"],
    load_mass_max: float = PIPELINE.run_pipeline_defaults["load_mass_max"],
    # Шумоподавление
    noise_force=PIPELINE.run_pipeline_defaults["noise_force"],
    noise_intensity=PIPELINE.run_pipeline_defaults["noise_intensity"],
    noise_quantile=None,
    # Назначение формул
    brutto_dict=None,
    rel_error: float = PIPELINE.run_pipeline_defaults["rel_error"],
    sign: str = PIPELINE.run_pipeline_defaults["sign"],
    assign_mass_min: float = PIPELINE.run_pipeline_defaults["assign_mass_min"],
    assign_mass_max: float = PIPELINE.run_pipeline_defaults["assign_mass_max"],
    # Поиск серий
    ppm_tol: float = PIPELINE.run_pipeline_defaults["ppm_tol"],
    max_groups: int = PIPELINE.run_pipeline_defaults["max_groups"],
    allow_gaps: bool = PIPELINE.run_pipeline_defaults["allow_gaps"],
    # Визуализация
    visualize: bool = True,
    save_dmet=None,
    save_dacet=None,
    # Van Krevelen диаграмма
    van_krevelen_output: str | None = None,
    # Выходной файл
    output_csv=None,
    # Тест-режим
    test_mode: bool = False,
    test_sets_root=None,
    # Изотопный фильтр
    isotope_filter: bool = False,
    use_cache: bool = True,
    progress_callback=None,
):
    """Run the full -COOH / -OH quantification pipeline.

    Executes the sequence load -> denoise -> assign formulas -> find series
    -> build result table on a triple of spectra (original, deuteromethylated,
    deuteroacylated), counting carboxyl and hydroxyl groups per compound.

    Parameters
    ----------
    src_path, dmet_path, dacet_path : str or None
        Paths to the original, deuteromethylated and deuteroacylated spectrum
        CSVs. Ignored when ``test_mode=True``.
    sep : str, keyword-only, optional
        CSV field separator. Default ``","``.
    load_mass_min, load_mass_max : float, keyword-only, optional
        m/z window applied at load time (Da). Defaults 0.0 and 1000.0.
    noise_force, noise_intensity, noise_quantile : optional
        Denoising parameters forwarded to :func:`denoise`.
    brutto_dict : dict or None, keyword-only, optional
        Per-element ranges for formula assignment.
    rel_error : float, keyword-only, optional
        Mass tolerance (ppm) for formula assignment. Default 1.0.
    sign : {'-', '+'}, keyword-only, optional
        Ionization sign; ``'-'`` = [M-H]-. Default ``'-'``.
    assign_mass_min, assign_mass_max : float, keyword-only, optional
        m/z window for assignment. Defaults 0 and 1000.
    ppm_tol : float, keyword-only, optional
        Tolerance (ppm) for series matching. Default 5.0.
    max_groups : int, keyword-only, optional
        Maximum functional groups per molecule to probe. Default 20.
    allow_gaps : bool, keyword-only, optional
        Whether to tolerate gaps within a series. Default ``True``.
    visualize : bool, keyword-only, optional
        Whether to render series plots. Default ``True``.
    save_dmet, save_dacet : optional
        Paths to save the -COOH / -OH series figures.
    output_csv : str or None, keyword-only, optional
        If given, the result table is written to this CSV path.
    test_mode : bool, keyword-only, optional
        If ``True``, ignore the path arguments and run the bundled test sets
        instead. Default ``False``.
    test_sets_root : str or None, keyword-only, optional
        Root directory of the test sets used when ``test_mode=True``.
    progress_callback : callable or None, keyword-only, optional
        If given, called as ``progress_callback(stage_name, pct)`` at each
        pipeline stage (0–100).  Stage names use Russian labels matching
        the GUI status bar.

    Returns
    -------
    PipelineRunResult or list of TestSetResult
        A :class:`PipelineRunResult` for a normal run, or a list of
        :class:`TestSetResult` when ``test_mode=True``.
    """

    # -----------------------------------------------------------------------
    # Проверка импорта
    # -----------------------------------------------------------------------
    if _IMPORT_ERROR:
        msg = f"[PIPELINE] Импорт spectrum_ops не удался: {_IMPORT_ERROR}"
        logger.error(msg)
        if not test_mode:
            stats = PipelineStats()
            return PipelineRunResult(table=pd.DataFrame(), stats=stats, messages=[msg])

    # -----------------------------------------------------------------------
    # ТЕСТ-РЕЖИМ
    # -----------------------------------------------------------------------
    if test_mode:
        return _run_test_mode(
            test_sets_root=test_sets_root,
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

    # -----------------------------------------------------------------------
    # Валидация путей
    # -----------------------------------------------------------------------
    messages: list[str] = []
    for label, path in [("src", src_path), ("dmet", dmet_path), ("dacet", dacet_path)]:
        if path is None:
            messages.append(f"[PIPELINE] ОШИБКА: путь '{label}' не задан")
        elif not Path(path).exists():
            messages.append(f"[PIPELINE] ОШИБКА: файл не найден: {path}")
    if messages:
        for m in messages:
            logger.error(m)
        return PipelineRunResult(
            table=pd.DataFrame(), stats=PipelineStats(), messages=messages
        )

    stats = PipelineStats()

    # ── Кэш: не перевыполнять при тех же параметрах ──
    _cache_key = hash(
        (
            src_path,
            dmet_path,
            dacet_path,
            sep,
            load_mass_min,
            load_mass_max,
            noise_force,
            noise_intensity,
            noise_quantile,
            str(brutto_dict),
            rel_error,
            sign,
            assign_mass_min,
            assign_mass_max,
            ppm_tol,
            max_groups,
            allow_gaps,
            output_csv,
            isotope_filter,
        )
    )
    if use_cache and _cache_key in _result_cache:
        _debug("Кэш: параметры не изменились — возвращаю сохранённый результат")
        return _result_cache[_cache_key]

    # -----------------------------------------------------------------------
    # ШАГ 1: Загрузка спектров
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("ШАГ 1: Загрузка спектров")
    print("=" * 60)
    _debug(f"src_path  = {src_path}")
    _debug(f"dmet_path = {dmet_path}")
    _debug(f"dacet_path= {dacet_path}")
    _debug(f"load_mass_min={load_mass_min}, load_mass_max={load_mass_max}")

    if progress_callback:
        progress_callback("Загрузка src…", 2)
    _mapper = {"mass": "mass", "intensity": "intensity"}
    try:
        src = load_spectrum(
            src_path,
            mapper=_mapper,
            sep=sep,
            mass_min=load_mass_min,
            mass_max=load_mass_max,
            metadata={"name": "src"},
        )
        stats.src_loaded = len(src.table) if hasattr(src, "table") else 0
        _debug(f"src загружен: {stats.src_loaded} пиков")
        if progress_callback:
            progress_callback("Загрузка dmet…", 5)
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА загрузки src: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        return PipelineRunResult(table=pd.DataFrame(), stats=stats, messages=[msg])

    try:
        dmet = load_spectrum(
            dmet_path,
            mapper=_mapper,
            sep=sep,
            mass_min=load_mass_min,
            mass_max=load_mass_max,
            metadata={"name": "dmet"},
        )
        stats.dmet_loaded = len(dmet.table) if hasattr(dmet, "table") else 0
        _debug(f"dmet загружен: {stats.dmet_loaded} пиков")
        if progress_callback:
            progress_callback("Загрузка dacet…", 8)
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА загрузки dmet: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        return PipelineRunResult(table=pd.DataFrame(), stats=stats, messages=[msg])

    try:
        dacet = load_spectrum(
            dacet_path,
            mapper=_mapper,
            sep=sep,
            mass_min=load_mass_min,
            mass_max=load_mass_max,
            metadata={"name": "dacet"},
        )
        stats.dacet_loaded = len(dacet.table) if hasattr(dacet, "table") else 0
        _debug(f"dacet загружен: {stats.dacet_loaded} пиков")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА загрузки dacet: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        return PipelineRunResult(table=pd.DataFrame(), stats=stats, messages=[msg])

    print(
        f"  Загружено пиков:  src={stats.src_loaded},  dmet={stats.dmet_loaded},  dacet={stats.dacet_loaded}"
    )
    if progress_callback:
        progress_callback("Загрузка завершена", 10)

    # -----------------------------------------------------------------------
    # ШАГ 2a: Шумоподавление
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 2a: Шумоподавление")
    print("=" * 60)
    _debug(
        f"noise_force={noise_force}, noise_intensity={noise_intensity}, noise_quantile={noise_quantile}"
    )

    try:
        # Сохранить копию до денойза для изотопного фильтра
        src_original = src.copy() if isotope_filter else None
        if progress_callback:
            progress_callback("Шумоподавление src…", 12)
        src = denoise(
            src, force=noise_force, intensity=noise_intensity, quantile=noise_quantile
        )
        stats.src_denoised = len(src.table) if hasattr(src, "table") else 0
        _debug(f"src после денойса: {stats.src_denoised} пиков")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА денойса src: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    try:
        if progress_callback:
            progress_callback("Шумоподавление dmet…", 15)
        dmet = denoise(
            dmet, force=noise_force, intensity=noise_intensity, quantile=noise_quantile
        )
        stats.dmet_denoised = len(dmet.table) if hasattr(dmet, "table") else 0
        _debug(f"dmet после денойса: {stats.dmet_denoised} пиков")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА денойса dmet: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    try:
        if progress_callback:
            progress_callback("Шумоподавление dacet…", 18)
        dacet = denoise(
            dacet, force=noise_force, intensity=noise_intensity, quantile=noise_quantile
        )
        stats.dacet_denoised = len(dacet.table) if hasattr(dacet, "table") else 0
        _debug(f"dacet после денойса: {stats.dacet_denoised} пиков")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА денойса dacet: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    print(
        f"  После шумоподавления: src={stats.src_denoised},  dmet={stats.dmet_denoised},  dacet={stats.dacet_denoised}"
    )
    if progress_callback:
        progress_callback("Шумоподавление завершено", 20)

    # -----------------------------------------------------------------------
    # ШАГ 2b: Назначение брутто-формул
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 2b: Назначение брутто-формул исходному спектру")
    print("=" * 60)
    _debug(
        f"assign_formulas: rel_error={rel_error}, sign={sign}, "
        f"mass_min={assign_mass_min}, mass_max={assign_mass_max}"
    )
    _debug(f"brutto_dict={'default' if brutto_dict is None else brutto_dict}")

    try:
        if progress_callback:
            progress_callback("Генерация формул-кандидатов…", 22)
        _assign_cb = _make_sub_progress(progress_callback, 23, 28, "Формула {0}/{1}…")
        src = assign_formulas(
            src,
            rel_error_ppm=rel_error,
            mass_min=assign_mass_min,
            mass_max=assign_mass_max,
            isotope_filter=isotope_filter,
            original=src_original,
            progress_callback=_assign_cb,
        )
        n_assigned = int(src.table.get("assign", pd.Series(dtype=bool)).sum())
        stats.assigned_count = n_assigned
        stats.assigned_ratio = (
            n_assigned / stats.src_denoised if stats.src_denoised else 0.0
        )
        _debug(
            f"assign_formulas результат: {n_assigned}/{stats.src_denoised} пиков назначено "
            f"({stats.assigned_ratio:.1%})"
        )
        _debug(f"Колонки src.table после assign: {list(src.table.columns)}")
        # Превью первых 5 назначенных
        assigned_mask = src.table.get("assign", pd.Series(False, index=src.table.index))
        assigned_preview = src.table.loc[assigned_mask == True].head(5)  # noqa: E712
        if not assigned_preview.empty:
            _debug(
                f"Первые назначенные пики:\n{assigned_preview.to_string(index=False)}"
            )
        else:
            _debug("ВНИМАНИЕ: назначенных пиков нет!")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА assign_formulas: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)
        n_assigned = 0

    print(f"  Назначено формул: {n_assigned} из {stats.src_denoised} пиков")

    if progress_callback:
        progress_callback("Назначение формул завершено", 52)

    # Строим копию только с назначенными пиками
    try:
        assigned_only_table = (
            src.table.loc[src.table["assign"] == True].reset_index(drop=True).copy()
        )  # noqa: E712
        _debug(
            f"assigned_only: {len(assigned_only_table)} строк, колонки: {list(assigned_only_table.columns)}"
        )
        if assigned_only_table.empty:
            _debug(
                "КРИТИЧНО: assigned_only пуст – find_series вернёт пустой результат!"
            )
    except Exception as e:
        _debug(f"ОШИБКА при создании assigned_only: {e}")
        assigned_only_table = pd.DataFrame()

    # -----------------------------------------------------------------------
    # ШАГ 3: Серии CD3 (N_COOH)
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 3: Серии дейтерометилирования (-> N_COOH)")
    print("=" * 60)
    _debug(
        f"find_series: delta={DELTA_CD3:.5f}, ppm_tol={ppm_tol}, max_groups={max_groups}, allow_gaps={allow_gaps}"
    )

    df_dmet = pd.DataFrame()
    try:
        _cd3_cb = _make_sub_progress(progress_callback, 53, 13, "Серия CD3 {0}/{1}…")
        df_dmet = find_series(
            src,
            dmet,
            delta=DELTA_CD3,
            ppm_tol=ppm_tol,
            max_groups=max_groups,
            allow_gaps=allow_gaps,
            progress_callback=_cd3_cb,
        )
        stats.dmet.rows = len(df_dmet)
        if not df_dmet.empty:
            stats.dmet.max_groups = (
                int(df_dmet["n_groups"].max()) if "n_groups" in df_dmet.columns else 0
            )
            if "missing" in df_dmet.columns:
                stats.dmet.missing_total = int(df_dmet["missing"].apply(len).sum())
        _debug(
            f"find_series(dmet): {len(df_dmet)} строк, колонки={list(df_dmet.columns) if not df_dmet.empty else '[]'}"
        )
        if not df_dmet.empty:
            _debug(
                f"  max_groups={stats.dmet.max_groups}, missing_total={stats.dmet.missing_total}"
            )
            _debug(f"Превью df_dmet:\n{df_dmet.head(3).to_string(index=False)}")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА find_series(dmet): {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    print(f"  Соединений с сериями CD3: {len(df_dmet)}")
    if not df_dmet.empty:
        print(f"  Макс. N_COOH = {stats.dmet.max_groups}")
        if stats.dmet.missing_total:
            print(
                f"  ВНИМАНИЕ: Внутренних пропусков в сериях: {stats.dmet.missing_total}"
            )
    if progress_callback:
        progress_callback("Поиск серий CD3 завершён", 67)

    # -----------------------------------------------------------------------
    # ШАГ 4: Серии CD3CO (N_OH)
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 4: Серии дейтероацилирования (-> N_OH)")
    print("=" * 60)
    _debug(
        f"find_series: delta={DELTA_CD3CO:.5f}, ppm_tol={ppm_tol}, max_groups={max_groups}, allow_gaps={allow_gaps}"
    )

    df_dacet = pd.DataFrame()
    try:
        _cd3co_cb = _make_sub_progress(
            progress_callback, 68, 13, "Серия CD3CO {0}/{1}…"
        )
        df_dacet = find_series(
            src,
            dacet,
            delta=DELTA_CD3CO,
            ppm_tol=ppm_tol,
            max_groups=max_groups,
            allow_gaps=allow_gaps,
            progress_callback=_cd3co_cb,
        )
        stats.dacet.rows = len(df_dacet)
        if not df_dacet.empty:
            stats.dacet.max_groups = (
                int(df_dacet["n_groups"].max()) if "n_groups" in df_dacet.columns else 0
            )
            if "missing" in df_dacet.columns:
                stats.dacet.missing_total = int(df_dacet["missing"].apply(len).sum())
        _debug(f"find_series(dacet): {len(df_dacet)} строк")
        if not df_dacet.empty:
            _debug(
                f"  max_groups={stats.dacet.max_groups}, missing_total={stats.dacet.missing_total}"
            )
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА find_series(dacet): {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    print(f"  Соединений с сериями CD3CO: {len(df_dacet)}")
    if not df_dacet.empty:
        print(f"  Макс. N_OH = {stats.dacet.max_groups}")
        if stats.dacet.missing_total:
            print(
                f"  ВНИМАНИЕ: Внутренних пропусков в сериях: {stats.dacet.missing_total}"
            )
    if progress_callback:
        progress_callback("Поиск серий CD3CO завершён", 82)

    # -----------------------------------------------------------------------
    # ШАГ 5: Итоговая таблица
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 5: Итоговая таблица N_COOH / N_OH")
    print("=" * 60)
    result = pd.DataFrame()
    try:
        result = build_result_table(src, df_dmet, df_dacet)
        stats.result_rows = len(result)
        if not result.empty:
            if "N_COOH" in result.columns:
                stats.result_n_cooh_gt0 = int((result["N_COOH"] > 0).sum())
            if "N_OH" in result.columns:
                stats.result_n_oh_gt0 = int((result["N_OH"] > 0).sum())
        _debug(f"build_result_table: {stats.result_rows} строк")
        _debug(f"Колонки результата: {list(result.columns)}")
        if not result.empty:
            _debug(f"Превью результата:\n{result.head(5).to_string(index=False)}")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА build_result_table: {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    print(f"  Строк в таблице: {stats.result_rows}")
    if not result.empty:
        print(f"  Соединений с N_COOH > 0: {stats.result_n_cooh_gt0}")
        print(f"  Соединений с N_OH   > 0: {stats.result_n_oh_gt0}")
    if progress_callback:
        progress_callback("Сборка итоговой таблицы…", 90)

    # -----------------------------------------------------------------------
    # ШАГ 6: Визуализация
    # -----------------------------------------------------------------------
    if visualize:
        print()
        print("=" * 60)
        print("ШАГ 6: Визуализация пропущенных пиков")
        print("=" * 60)
        try:
            if progress_callback:
                progress_callback("Визуализация CD3…", 92)
            visualize_series(
                src,
                dmet,
                df_dmet,
                delta=DELTA_CD3,
                label="дейтерометилирования",
                ppm_tol=ppm_tol,
                save_path=save_dmet,
            )
        except Exception as e:
            msg = f"[PIPELINE] ОШИБКА visualize dmet: {e}"
            logger.error(msg)
            messages.append(msg)
        try:
            if progress_callback:
                progress_callback("Визуализация CD3CO…", 94)
            visualize_series(
                src,
                dacet,
                df_dacet,
                delta=DELTA_CD3CO,
                label="дейтероацилирования",
                ppm_tol=ppm_tol,
                save_path=save_dacet,
            )
        except Exception as e:
            msg = f"[PIPELINE] ОШИБКА visualize dacet: {e}"
            logger.error(msg)
            messages.append(msg)

    # -----------------------------------------------------------------------
    # Сохранение CSV
    # -----------------------------------------------------------------------
    if output_csv and not result.empty:
        try:
            if progress_callback:
                progress_callback("Сохранение CSV…", 96)
            result.to_csv(output_csv, index=False, sep=";", encoding="utf-8-sig")
            print(f"\nИтоговая таблица сохранена: {output_csv}")
            _debug(f"CSV сохранён в {output_csv}, строк={len(result)}")
        except Exception as e:
            msg = f"[PIPELINE] ОШИБКА сохранения CSV: {e}"
            logger.error(msg)
            messages.append(msg)

    # -----------------------------------------------------------------------
    # ШАГ 7: Van Krevelen диаграмма (опционально)
    # -----------------------------------------------------------------------
    if van_krevelen_output and not result.empty:
        print()
        print("=" * 60)
        print("ШАГ 7: Van Krevelen диаграмма")
        print("=" * 60)
        try:
            if progress_callback:
                progress_callback("Van Krevelen диаграмма…", 98)
            create_van_krevelen_plot(result, output_path=van_krevelen_output)
        except Exception as e:
            msg = f"[PIPELINE] ОШИБКА Van Krevelen: {e}\n{traceback.format_exc()}"
            logger.error(msg)
            messages.append(msg)

    result_obj = PipelineRunResult(table=result, stats=stats, messages=messages)
    if use_cache:
        _result_cache[_cache_key] = result_obj
    if progress_callback:
        progress_callback("Готово", 100)
    return result_obj
