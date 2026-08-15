"""Pipeline stage helpers (load / denoise) extracted from ``run_pipeline``."""

import traceback

import pandas as pd

from src.core.spectrum import load_spectrum, denoise, find_series
from ._helpers import _debug, _make_sub_progress

import logging

logger = logging.getLogger(__name__)


def _load_triple(
    src_path,
    dmet_path,
    dacet_path,
    sep,
    load_mass_min,
    load_mass_max,
    stats,
    progress_callback,
):
    """Load the original / dmet / dacet spectra; return (src, dmet, dacet, err)."""
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
        return None, None, None, msg

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
        return None, None, None, msg

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
        return None, None, None, msg

    print(
        f"  Загружено пиков:  src={stats.src_loaded},  dmet={stats.dmet_loaded},  dacet={stats.dacet_loaded}"
    )
    if progress_callback:
        progress_callback("Загрузка завершена", 10)
    return src, dmet, dacet, None


def _denoise_triple(
    src,
    dmet,
    dacet,
    noise_force,
    noise_intensity,
    noise_quantile,
    isotope_filter,
    stats,
    messages,
    progress_callback,
):
    """Denoise the three spectra in place; return (src, dmet, dacet, src_original)."""
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
    return src, dmet, dacet, src_original


def _find_series_stage(
    src,
    deriv,
    delta,
    ppm_tol,
    max_groups,
    allow_gaps,
    series_stats,
    deriv_label,
    series_label,
    max_label,
    base_pct,
    range_pct,
    end_pct,
    messages,
    progress_callback,
):
    """Run ``find_series`` for one derivatization and update ``series_stats``."""
    df = pd.DataFrame()
    try:
        cb = _make_sub_progress(
            progress_callback, base_pct, range_pct, f"Серия {series_label} {{0}}/{{1}}…"
        )
        df = find_series(
            src,
            deriv,
            delta=delta,
            ppm_tol=ppm_tol,
            max_groups=max_groups,
            allow_gaps=allow_gaps,
            progress_callback=cb,
        )
        series_stats.rows = len(df)
        if not df.empty:
            series_stats.max_groups = (
                int(df["n_groups"].max()) if "n_groups" in df.columns else 0
            )
            if "missing" in df.columns:
                series_stats.missing_total = int(df["missing"].apply(len).sum())
        _debug(
            f"find_series({deriv_label}): {len(df)} строк, колонки={list(df.columns) if not df.empty else '[]'}"
        )
        if not df.empty:
            _debug(
                f"  max_groups={series_stats.max_groups}, missing_total={series_stats.missing_total}"
            )
            _debug(f"Превью df_{deriv_label}:\n{df.head(3).to_string(index=False)}")
    except Exception as e:
        msg = f"[PIPELINE] ОШИБКА find_series({deriv_label}): {e}\n{traceback.format_exc()}"
        logger.error(msg)
        messages.append(msg)

    print(f"  Соединений с сериями {series_label}: {len(df)}")
    if not df.empty:
        print(f"  Макс. {max_label} = {series_stats.max_groups}")
        if series_stats.missing_total:
            print(
                f"  ВНИМАНИЕ: Внутренних пропусков в сериях: {series_stats.missing_total}"
            )
    if progress_callback:
        progress_callback(f"Поиск серий {series_label} завершён", end_pct)
    return df
