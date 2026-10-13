"""Segmented chromatogram pipeline.

Averages each input file inside RT segments, denoises and assigns formulas
per segment, and searches derivatized peaks across **all** segments (the
derivatized retention time is not kept or matched).
"""

from __future__ import annotations

import pandas as pd

from src.configs import CHEM, PIPELINE
from src.core.domain.spectrum import Spectrum
from src.core.spectrum import (
    DELTA_CD3,
    DELTA_CD3CO,
    FormulaSearchConfig,
    assign_formulas,
    build_result_table,
    denoise,
    find_series,
)
from src.core.spectrum._formula_source import open_formula_db
from src.core.io.segmented import average_segments, build_rt_segments
from src.core.pipeline._helpers import _debug
from src.core.pipeline._stats import PipelineRunResult, PipelineStats

import logging

logger = logging.getLogger(__name__)


def _ion_mode_for_sign(sign: str | None) -> str:
    """Map GUI/CLI ionization sign to an ion-mode string."""
    if sign == "+":
        return "[M+H]+"
    if sign == "-":
        return "[M-H]-"
    return CHEM.default_ion_mode


def _search_config_from_brutto(brutto_dict: dict | None) -> FormulaSearchConfig | None:
    """Build a FormulaSearchConfig from per-element ranges, if supplied."""
    if not brutto_dict:
        return None
    ranges = {el: (int(lo), int(hi)) for el, (lo, hi) in brutto_dict.items()}
    for el, rng in FormulaSearchConfig().ranges.items():
        ranges.setdefault(el, rng)
    return FormulaSearchConfig(ranges=ranges)


def _spectrum_from_df(
    df: pd.DataFrame,
    mass_min: float,
    mass_max: float,
    name: str,
) -> Spectrum:
    """Filter a segment table to the m/z window and wrap it in a Spectrum."""
    table = df[["mass", "intensity"]].copy()
    table = table[
        (table["mass"] >= mass_min) & (table["mass"] <= mass_max)
    ].reset_index(drop=True)
    return Spectrum(table=table, metadata={"name": name})


def _merge_spectra(specs: list[Spectrum]) -> Spectrum:
    """Merge several denoised segment spectra into one, summing intensities."""
    frames = [s.table for s in specs if s is not None and len(s.table)]
    if not frames:
        return Spectrum(
            table=pd.DataFrame({"mass": [], "intensity": []}),
            metadata={"name": "deriv_all"},
        )
    full = pd.concat(frames, ignore_index=True)
    full["_mz"] = full["mass"].round(5)
    agg = (
        full.groupby("_mz", as_index=False)["intensity"]
        .sum()
        .rename(columns={"_mz": "mass"})
    )
    return Spectrum(table=agg[["mass", "intensity"]], metadata={"name": "deriv_all"})


def run_pipeline_segmented(
    src_path=None,
    dmet_path=None,
    dacet_path=None,
    *,
    segment_width: float = 2.0,
    rt_min: float = 0.0,
    rt_max: float = 20.0,
    # Загрузка
    sep: str = PIPELINE.run_pipeline_defaults["sep"],
    load_mass_min: float = PIPELINE.run_pipeline_defaults["load_mass_min"],
    load_mass_max: float = PIPELINE.run_pipeline_defaults["load_mass_max"],
    # Шумоподавление (применяется внутри каждого отрезка)
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
    # Прочее
    isotope_filter: bool = True,
    isotope_variants: bool = True,
    use_formula_db: bool = True,
    progress_callback=None,
):
    """Run the -COOH/-OH pipeline over RT-segmented chromatograms.

    Source peaks keep the RT of their segment (``rt_start`` / ``rt_end``).
    Derivatized spectra are averaged over the same segments, but series
    search uses all segments combined (derivatized RT is not kept or
    matched).  CSV / XLSX / JSON inputs are treated as one segment with
    ``rt_start=None`` / ``rt_end=None``.

    Returns
    -------
    PipelineRunResult
        ``table`` contains ``mass, rt_start, rt_end, intensity, brutto,
        all_candidates, N_COOH, N_OH, missing_dmet, missing_dacet``.
    """
    messages: list[str] = []
    errors: list[str] = []

    def _fail(msg: str) -> None:
        messages.append(msg)
        errors.append(msg)

    for label, path in [("src", src_path), ("dmet", dmet_path), ("dacet", dacet_path)]:
        if path is None:
            _fail(f"[PIPELINE] ОШИБКА: путь '{label}' не задан")
        else:
            import os

            if not os.path.exists(path):
                _fail(f"[PIPELINE] ОШИБКА: файл не найден: {path}")
    if errors:
        return PipelineRunResult(
            table=pd.DataFrame(),
            stats=PipelineStats(),
            messages=messages,
            errors=errors,
        )

    segments = build_rt_segments(rt_min, rt_max, segment_width)
    _debug(f"segments: {segments}")

    if progress_callback:
        progress_callback("Усреднение сегментов…", 5)

    src_segments = average_segments(src_path, segments, sep=sep)
    dmet_segments = average_segments(dmet_path, segments, sep=sep)
    dacet_segments = average_segments(dacet_path, segments, sep=sep)

    stats = PipelineStats()

    ion_mode = _ion_mode_for_sign(sign)
    search_config = _search_config_from_brutto(brutto_dict)

    # Источник формул: сжатая база формул (общая для всех отрезков)
    formula_db = open_formula_db() if use_formula_db else None

    src_specs: list[Spectrum] = []
    dmet_specs: list[Spectrum] = []
    dacet_specs: list[Spectrum] = []

    n_segments = len(src_segments)
    for idx, seg in enumerate(src_segments, 1):
        rt_start = seg["rt_start"]
        rt_end = seg["rt_end"]

        if progress_callback:
            progress_callback(
                f"Обработка отрезка {idx}/{n_segments}…",
                10 + int(50 * idx / max(n_segments, 1)),
            )

        src_spec = _spectrum_from_df(
            seg["df"], load_mass_min, load_mass_max, f"src_seg{idx}"
        )
        stats.src_loaded += len(src_spec.table)

        # Копия до денойза нужна для изотопного фильтра и поиска вариантов
        # (как в обычном пайплайне).
        src_original = src_spec.copy() if (isotope_filter or isotope_variants) else None

        try:
            src_spec = denoise(
                src_spec,
                force=noise_force,
                intensity=noise_intensity,
                quantile=noise_quantile,
            )
            stats.src_denoised += len(src_spec.table)
        except Exception as e:  # noqa: BLE001
            _fail(f"[PIPELINE] ОШИБКА денойса src сегмента {idx}: {e}")
            continue

        try:
            src_spec = assign_formulas(
                src_spec,
                rel_error_ppm=rel_error,
                mass_min=assign_mass_min,
                mass_max=assign_mass_max,
                search_config=search_config,
                ion_mode=ion_mode,
                isotope_filter=isotope_filter,
                isotope_variants=isotope_variants,
                original=src_original,
                formula_db=formula_db,
            )
            stats.assigned_count += int(
                src_spec.table.get("assign", pd.Series(dtype=bool)).sum()
            )
        except Exception as e:  # noqa: BLE001
            _fail(f"[PIPELINE] ОШИБКА assign сегмента {idx}: {e}")
            continue

        src_spec.table["rt_start"] = rt_start
        src_spec.table["rt_end"] = rt_end
        src_specs.append(src_spec)

    if not src_specs:
        if not errors:
            _fail(
                "[PIPELINE] ОШИБКА: после обработки сегментов не осталось исходных пиков"
            )
        return PipelineRunResult(
            table=pd.DataFrame(), stats=stats, messages=messages, errors=errors
        )

    # Дериватизованные сегменты: шумоподавление внутри отрезка,
    # затем объединение всех отрезков (RT не сохраняется).
    for idx, seg in enumerate(dmet_segments, 1):
        spec = _spectrum_from_df(
            seg["df"], load_mass_min, load_mass_max, f"dmet_seg{idx}"
        )
        try:
            spec = denoise(
                spec,
                force=noise_force,
                intensity=noise_intensity,
                quantile=noise_quantile,
            )
        except Exception as e:  # noqa: BLE001
            _fail(f"[PIPELINE] ОШИБКА денойса dmet сегмента {idx}: {e}")
            continue
        dmet_specs.append(spec)

    for idx, seg in enumerate(dacet_segments, 1):
        spec = _spectrum_from_df(
            seg["df"], load_mass_min, load_mass_max, f"dacet_seg{idx}"
        )
        try:
            spec = denoise(
                spec,
                force=noise_force,
                intensity=noise_intensity,
                quantile=noise_quantile,
            )
        except Exception as e:  # noqa: BLE001
            _fail(f"[PIPELINE] ОШИБКА денойса dacet сегмента {idx}: {e}")
            continue
        dacet_specs.append(spec)

    dmet_all = _merge_spectra(dmet_specs)
    dacet_all = _merge_spectra(dacet_specs)

    if progress_callback:
        progress_callback("Поиск серий по всем отрезкам…", 70)

    result_frames: list[pd.DataFrame] = []
    for idx, src_spec in enumerate(src_specs, 1):
        rt_start = src_spec.table["rt_start"].iloc[0]
        rt_end = src_spec.table["rt_end"].iloc[0]

        df_dmet = pd.DataFrame()
        df_dacet = pd.DataFrame()
        try:
            df_dmet = find_series(
                src_spec,
                dmet_all,
                delta=DELTA_CD3,
                ppm_tol=ppm_tol,
                max_groups=max_groups,
                allow_gaps=allow_gaps,
            )
        except Exception as e:  # noqa: BLE001
            _fail(f"[PIPELINE] ОШИБКА find_series dmet сегмента {idx}: {e}")
        try:
            df_dacet = find_series(
                src_spec,
                dacet_all,
                delta=DELTA_CD3CO,
                ppm_tol=ppm_tol,
                max_groups=max_groups,
                allow_gaps=allow_gaps,
            )
        except Exception as e:  # noqa: BLE001
            _fail(f"[PIPELINE] ОШИБКА find_series dacet сегмента {idx}: {e}")

        tbl = build_result_table(src_spec, df_dmet, df_dacet)
        if not tbl.empty:
            tbl["rt_start"] = rt_start
            tbl["rt_end"] = rt_end
            result_frames.append(tbl)

    if result_frames:
        result = pd.concat(result_frames, ignore_index=True)
    else:
        result = pd.DataFrame()

    stats.result_rows = len(result)
    if not result.empty:
        if "N_COOH" in result.columns:
            stats.result_n_cooh_gt0 = int((result["N_COOH"] > 0).sum())
        if "N_OH" in result.columns:
            stats.result_n_oh_gt0 = int((result["N_OH"] > 0).sum())
    stats.assigned_ratio = (
        stats.assigned_count / stats.src_denoised if stats.src_denoised else 0.0
    )

    if progress_callback:
        progress_callback("Готово", 100)

    if formula_db is not None:
        formula_db.close()

    return PipelineRunResult(
        table=result, stats=stats, messages=messages, errors=errors
    )
