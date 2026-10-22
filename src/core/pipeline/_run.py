"""run_pipeline — main pipeline entry point."""

from __future__ import annotations

import os
import logging
import traceback
import pandas as pd
from pathlib import Path
from typing import Optional
from src.configs import PIPELINE
from ._cache import _result_cache
from ._helpers import _debug, _ion_mode_from_sign, _make_sub_progress
from ._stats import PipelineStats, PipelineRunResult
from ._test import _run_test_mode
from ._stages import _load_triple, _denoise_triple, _find_series_stage
from ._export import export_result_table
from src.core.van_krevelen import create_van_krevelen_plot

logger = logging.getLogger(__name__)


def _file_signature(path) -> tuple:
    """Быстрый признак содержимого файла для ключа кэша: (mtime_ns, size).

    Без него перезапись файла с тем же именем возвращала бы старый результат.
    """
    try:
        st = os.stat(path)
        return (int(st.st_mtime_ns), int(st.st_size))
    except OSError:
        return (0, 0)


def _search_config_from_brutto(
    brutto_dict: Optional[dict],
) -> Optional[FormulaSearchConfig]:
    """Build a :class:`FormulaSearchConfig` from GUI/CLI element ranges.

    ``brutto_dict`` uses the shape ``{"C": (min, max), ...}`` produced by
    the GUI parameter parser and the CLI ``--element-ranges`` parser.
    Returns ``None`` when no ranges were supplied so ``assign_formulas``
    falls back to its configured default ranges.
    """
    if not brutto_dict:
        return None
    ranges = {el: (int(lo), int(hi)) for el, (lo, hi) in brutto_dict.items()}
    # FormulaSearchConfig requires a range for every enumerated element
    # (C, H, O, N).  Partially specified ranges (e.g. CLI ``--element-ranges
    # C:1-3``) are completed from the configured defaults.
    for el, rng in FormulaSearchConfig().ranges.items():
        ranges.setdefault(el, rng)
    return FormulaSearchConfig(ranges=ranges)


# ---------------------------------------------------------------------------
try:
    from src.core.spectrum import (
        assign_formulas,
        build_result_table,
        visualize_series,
        DELTA_CD3,
        DELTA_CD3CO,
        FormulaSearchConfig,
    )
    from src.core.spectrum._formula_source import open_formula_db

    _IMPORT_ERROR: Optional[str] = None
except Exception as _e:
    _IMPORT_ERROR = str(_e)
    logger.error(
        f"[PIPELINE] CRITICAL: не удалось импортировать src.core.spectrum: {_e}",
    )


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
    # Правило по умолчанию: не более 1 пропуска в серии (0 — без пропусков)
    max_gaps: int = PIPELINE.run_pipeline_defaults.get("max_gaps", 1),
    # Устаревший синоним: allow_gaps=False эквивалентно max_gaps=0
    allow_gaps: bool | None = None,
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
    # Изотопный фильтр и поиск изотопных вариантов (включены по умолчанию:
    # паттерн M+1/M+2 учитывается при выборе формулы, а для найденных формул
    # ищутся изотопные варианты и помечаются пики-сателлиты).
    isotope_filter: bool = True,
    isotope_variants: bool = True,
    # Источник формул-кандидатов: сжатая база формул (если файл доступен)
    use_formula_db: bool = True,
    # Шумоподавление спектров дериватизатов (по умолчанию выключено:
    # пики продуктов низкоинтенсивные и теряются вместе с шумом)
    denoise_derivatives: bool = PIPELINE.run_pipeline_defaults.get(
        "denoise_derivatives", True
    ),
    # Шумоподавление исходного спектра: можно отключить, если пиклист уже
    # отфильтрован прибором/исследователем (пункт 11).
    denoise_source: bool = True,
    # Точность прежде полноты: без подтверждённой первой ступени серия
    # не считается (см. ADR-0008).
    require_first_step: bool = PIPELINE.run_pipeline_defaults.get(
        "require_first_step", False
    ),
    significance_level: float = PIPELINE.run_pipeline_defaults.get(
        "significance_level", 0.95
    ),
    # Сдвиг ступеней: "theoretical" (от брутто) или "observed" (от
    # наблюдаемого пика того же соединения в производном спектре).
    series_anchor: str = PIPELINE.run_pipeline_defaults.get(
        "series_anchor", "theoretical"
    ),
    anchor_ppm: float = PIPELINE.run_pipeline_defaults.get("anchor_ppm", 10.0),
    # Профиль интенсивностей продуктов (опционально, по умолчанию выключен).
    profile_check: bool = PIPELINE.run_pipeline_defaults.get("profile_check", False),
    profile_max_jump: float | None = PIPELINE.run_pipeline_defaults.get(
        "profile_max_jump", 10.0
    ),
    profile_max_corr: float | None = PIPELINE.run_pipeline_defaults.get(
        "profile_max_corr", 0.5
    ),
    # Пользовательский фильтр X/C = (F+Cl+Br+I)/C. None — фильтр выключен
    # (по умолчанию); значение задаётся в GUI/CLI.
    max_xc: float | None = None,
    ratios_enabled: bool = True,
    nom_dbe_enabled: bool = True,
    # Предельное число атомов галогенов в брутто-формуле (пользовательский
    # предел, по умолчанию 5).
    halogen_max_atoms: int = 5,
    #: Полный перебор комбинаций галогенов (галочка в GUI, заметно медленнее).
    halogen_exhaustive: bool = True,
    #: Число комбинаций в обычном режиме; выбираются по приоритету:
    #: сначала варианты с большим числом атомов одного галогена.
    halogen_max_combinations: int = 16,
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
    max_gaps : int, keyword-only, optional
        Максимальное число пропущенных ступеней внутри серии. По умолчанию
        **1** (правило проекта); ``0`` — без пропусков. Default 1.
    allow_gaps : bool or None, keyword-only, optional
        Устаревший синоним: ``False`` эквивалентно ``max_gaps=0``. Default ``None``.
    visualize : bool, keyword-only, optional
        Whether to render series plots. Default ``True``.
    save_dmet, save_dacet : optional
        Paths to save the -COOH / -OH series figures.
    output_csv : str or None, keyword-only, optional
        If given, the result table is written to this path. The format is
        chosen by extension: ``.xlsx`` / ``.xls`` → Excel, otherwise CSV.
    test_mode : bool, keyword-only, optional
        If ``True``, ignore the path arguments and run the bundled test sets
        instead. Default ``False``. Эталонные параметры берутся из
        ``pipeline.json -> test_mode``; явно переданное значение, отличное от
        production-дефолта, переопределяет эталонное.
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
    # Правило по умолчанию: не более 1 пропуска в серии (0 — без пропусков).
    # Устаревший синоним allow_gaps=False означает «пропуски запрещены».
    # -----------------------------------------------------------------------
    if allow_gaps is False:
        max_gaps = 0
    if max_gaps < 0:
        raise ValueError(f"max_gaps должно быть >= 0, получено {max_gaps}")

    # -----------------------------------------------------------------------
    # Проверка импорта
    # -----------------------------------------------------------------------
    if _IMPORT_ERROR:
        msg = f"[PIPELINE] Импорт src.core.spectrum не удался: {_IMPORT_ERROR}"
        logger.error(msg)
        if not test_mode:
            stats = PipelineStats()
            return PipelineRunResult(
                table=pd.DataFrame(), stats=stats, messages=[msg], errors=[msg]
            )

    # -----------------------------------------------------------------------
    # ТЕСТ-РЕЖИМ
    # -----------------------------------------------------------------------
    if test_mode:
        # В тест-режиме эталонные параметры берутся из pipeline.json -> test_mode
        # (единый источник истины). Значение, явно заданное вызывающим и
        # отличающееся от production-дефолта, имеет приоритет — это сохраняет
        # возможность разовых экспериментов без правки конфига.
        tm = PIPELINE.test_mode
        prod = PIPELINE.run_pipeline_defaults

        def _reference(test_value, passed, prod_default):
            return passed if passed != prod_default else test_value

        return _run_test_mode(
            test_sets_root=test_sets_root,
            noise_force=_reference(
                tm["denoise"]["force"], noise_force, prod["noise_force"]
            ),
            noise_intensity=_reference(
                tm["denoise"]["intensity"], noise_intensity, prod["noise_intensity"]
            ),
            noise_quantile=_reference(tm["denoise"]["quantile"], noise_quantile, None),
            assign_mass_min=_reference(
                tm["assign"]["mass_min"], assign_mass_min, prod["assign_mass_min"]
            ),
            assign_mass_max=_reference(
                tm["assign"]["mass_max"], assign_mass_max, prod["assign_mass_max"]
            ),
            rel_error=_reference(
                tm["assign"]["rel_error_ppm"], rel_error, prod["rel_error"]
            ),
            sign=sign,
            ppm_tol=_reference(tm["series"]["ppm_tol"], ppm_tol, prod["ppm_tol"]),
            max_groups=_reference(
                tm["series"]["max_groups"], max_groups, prod["max_groups"]
            ),
            max_gaps=_reference(
                tm["series"].get("max_gaps", 1), max_gaps, prod.get("max_gaps", 1)
            ),
        )

    # -----------------------------------------------------------------------
    # Валидация путей
    # -----------------------------------------------------------------------
    messages: list[str] = []
    errors: list[str] = []

    def _fail(msg: str) -> None:
        """Зафиксировать ошибку этапа.

        Ошибка попадает и в ``messages`` (полный журнал прогона), и в
        ``errors`` — последний определяет ``PipelineRunResult.ok`` и код
        возврата CLI.
        """
        messages.append(msg)
        errors.append(msg)

    for label, path in [("src", src_path), ("dmet", dmet_path), ("dacet", dacet_path)]:
        if path is None:
            _fail(f"[PIPELINE] ОШИБКА: путь '{label}' не задан")
        elif not Path(path).exists():
            _fail(f"[PIPELINE] ОШИБКА: файл не найден: {path}")
    if errors:
        for m in errors:
            logger.error(m)
        return PipelineRunResult(
            table=pd.DataFrame(),
            stats=PipelineStats(),
            messages=messages,
            errors=errors,
        )

    stats = PipelineStats()

    # ── Кэш: не перевыполнять при тех же параметрах ──
    _cache_key = hash(
        (
            src_path,
            dmet_path,
            dacet_path,
            # Содержимое файлов: перезапись с тем же именем должна
            # инвалидировать кэш.
            _file_signature(src_path),
            _file_signature(dmet_path),
            _file_signature(dacet_path),
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
            max_gaps,
            output_csv,
            isotope_filter,
            isotope_variants,
            use_formula_db,
            denoise_derivatives,
            denoise_source,
            require_first_step,
            significance_level,
            series_anchor,
            anchor_ppm,
            profile_check,
            profile_max_jump,
            profile_max_corr,
            max_xc,
            bool(ratios_enabled),
            bool(nom_dbe_enabled),
            halogen_max_atoms,
            halogen_exhaustive,
            halogen_max_combinations,
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

    src, dmet, dacet, _load_err = _load_triple(
        src_path,
        dmet_path,
        dacet_path,
        sep,
        load_mass_min,
        load_mass_max,
        stats,
        progress_callback,
    )
    if _load_err:
        logger.error(_load_err)
        return PipelineRunResult(
            table=pd.DataFrame(),
            stats=stats,
            messages=[_load_err],
            errors=[_load_err],
        )

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

    src, dmet, dacet, src_original = _denoise_triple(
        src,
        dmet,
        dacet,
        noise_force,
        noise_intensity,
        noise_quantile,
        # Копия до денойза нужна и для фильтра, и для поиска изотопных вариантов
        isotope_filter or isotope_variants,
        stats,
        messages,
        progress_callback,
        denoise_derivatives,
        denoise_source,
        series_anchor,
        anchor_ppm,
    )

    # -----------------------------------------------------------------------
    # ШАГ 2b: Назначение брутто-формул
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 2b: Назначение брутто-формул исходному спектру")
    print("=" * 60)
    ion_mode = _ion_mode_from_sign(sign)
    search_config = _search_config_from_brutto(brutto_dict)
    if search_config is not None:
        # X/C — пользовательская настройка (None = выключен)
        search_config.max_xc = max_xc
        search_config.ratios_enabled = bool(ratios_enabled)
        search_config.nom_dbe_enabled = bool(nom_dbe_enabled)
    elif max_xc is not None or not ratios_enabled or not nom_dbe_enabled:
        search_config = FormulaSearchConfig(
            max_xc=max_xc,
            ratios_enabled=bool(ratios_enabled),
            nom_dbe_enabled=bool(nom_dbe_enabled),
        )
    _debug(
        f"assign_formulas: rel_error={rel_error}, sign={sign}, "
        f"ion_mode={ion_mode}, mass_min={assign_mass_min}, mass_max={assign_mass_max}"
    )
    _debug(f"brutto_dict={'default' if brutto_dict is None else brutto_dict}")

    try:
        if progress_callback:
            progress_callback("Генерация формул-кандидатов…", 22)
        _assign_cb = _make_sub_progress(progress_callback, 23, 28, "Формула {0}/{1}…")
        # Источник формул: сжатая база (быстро, если файл доступен) или перебор
        formula_db = open_formula_db() if use_formula_db else None
        try:
            src = assign_formulas(
                src,
                rel_error_ppm=rel_error,
                mass_min=assign_mass_min,
                mass_max=assign_mass_max,
                search_config=search_config,
                ion_mode=ion_mode,
                isotope_filter=isotope_filter,
                isotope_variants=isotope_variants,
                original=src_original,
                progress_callback=_assign_cb,
                formula_db=formula_db,
                db_halogen_atoms=halogen_max_atoms,
                db_halogen_exhaustive=halogen_exhaustive,
                db_halogen_max_combinations=halogen_max_combinations,
            )
        finally:
            if formula_db is not None:
                formula_db.close()
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
        _fail(msg)
        n_assigned = 0

    print(f"  Назначено формул: {n_assigned} из {stats.src_denoised} пиков")

    if progress_callback:
        progress_callback("Назначение формул завершено", 52)

    # -----------------------------------------------------------------------
    # Колонка наблюдаемых «якорей» (режим series_anchor="observed")
    if str(series_anchor).lower() == "observed":
        _anchor_col, _anchor_col2 = "anchor_mz_dmet", "anchor_mz_dacet"
    else:
        _anchor_col, _anchor_col2 = None, None

    # ШАГ 3: Серии CD3 (N_COOH)
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 3: Серии дейтерометилирования (-> N_COOH)")
    print("=" * 60)
    _debug(
        f"find_series: delta={DELTA_CD3:.5f}, ppm_tol={ppm_tol}, max_groups={max_groups}, max_gaps={max_gaps}"
    )

    df_dmet = _find_series_stage(
        src,
        dmet,
        DELTA_CD3,
        ppm_tol,
        max_groups,
        max_gaps,
        require_first_step,
        significance_level,
        _anchor_col,
        profile_check,
        profile_max_jump,
        profile_max_corr,
        ion_mode,
        stats.dmet,
        "dmet",
        "CD3",
        "N_COOH",
        53,
        13,
        67,
        messages,
        progress_callback,
        raw_path=src_path,
    )

    # -----------------------------------------------------------------------
    # ШАГ 4: Серии CD3CO (N_OH)
    # -----------------------------------------------------------------------
    print()
    print("=" * 60)
    print("ШАГ 4: Серии дейтероацилирования (-> N_OH)")
    print("=" * 60)
    _debug(
        f"find_series: delta={DELTA_CD3CO:.5f}, ppm_tol={ppm_tol}, max_groups={max_groups}, max_gaps={max_gaps}"
    )

    df_dacet = _find_series_stage(
        src,
        dacet,
        DELTA_CD3CO,
        ppm_tol,
        max_groups,
        max_gaps,
        require_first_step,
        significance_level,
        _anchor_col2,
        profile_check,
        profile_max_jump,
        profile_max_corr,
        ion_mode,
        stats.dacet,
        "dacet",
        "CD3CO",
        "N_OH",
        68,
        13,
        82,
        messages,
        progress_callback,
        raw_path=src_path,
    )

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
        _fail(msg)

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
    # Сохранение результата (CSV / XLSX / JSON по расширению)
    # -----------------------------------------------------------------------
    if output_csv and not result.empty:
        try:
            if progress_callback:
                progress_callback("Сохранение результата…", 96)
            export_result_table(
                result,
                output_csv,
                metadata={
                    "params": {
                        "rel_error_ppm": rel_error,
                        "sign": sign,
                        "noise_force": noise_force,
                        "noise_intensity": noise_intensity,
                        "noise_quantile": noise_quantile,
                        "ppm_tol": ppm_tol,
                        "max_groups": max_groups,
                        "max_gaps": max_gaps,
                        "isotope_filter": isotope_filter,
                        "isotope_variants": isotope_variants,
                        "assign_mass_min": assign_mass_min,
                        "assign_mass_max": assign_mass_max,
                        "load_mass_min": load_mass_min,
                        "load_mass_max": load_mass_max,
                    }
                },
            )
            print(f"\nИтоговая таблица сохранена: {output_csv}")
            _debug(f"Результат сохранён в {output_csv}, строк={len(result)}")
        except Exception as e:
            msg = f"[PIPELINE] ОШИБКА сохранения результата: {e}"
            logger.error(msg)
            _fail(msg)

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

    result_obj = PipelineRunResult(
        table=result, stats=stats, messages=messages, errors=errors
    )
    if use_cache and not errors:
        # Результат с ошибками этапов не кэшируем: иначе повторный запуск
        # «прилипает» к неполной таблице.
        _result_cache[_cache_key] = result_obj
    if progress_callback:
        progress_callback("Готово", 100)
    return result_obj
