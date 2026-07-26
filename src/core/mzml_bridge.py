"""mzML → averaged CSV bridge (requires pymzml).

Provides a drop-in replacement for the averaging step of
``raw_bridge.average_raw_to_csv()`` when the user has already converted
a ``.raw`` file to ``.mzML`` with an external tool (e.g. ProteoWizard msconvert).

Usage
-----
    from src.core.mzml_bridge import mzml_to_csv

    csv_path = mzml_to_csv("sample.mzML", output_csv="averaged.csv",
                           rt_min=0.0, rt_max=30.0)
"""

from __future__ import annotations

import csv
import os
from typing import Callable, Optional

import numpy as np


def mzml_to_csv(
    mzml_path: str,
    output_csv: Optional[str] = None,
    rt_min: float = 0.0,
    rt_max: float = 999.0,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Average all MS1 spectra in *mzml_path* over [*rt_min*, *rt_max*]
    and write a ``mass,intensity`` CSV.

    Parameters
    ----------
    mzml_path : str
        Path to the ``.mzML`` file.
    output_csv : str or None, optional
        Where to write the CSV.  If ``None``, a file named
        ``<basename>_avrg.csv`` is created next to the mzML file.
    rt_min : float
        Start of retention-time window (minutes).  Default 0.0.
    rt_max : float
        End of retention-time window (minutes).  Default 999.0.
    progress_callback : callable or None, optional
        If given, called with status strings at key stages.

    Returns
    -------
    str
        Absolute path to the written CSV file.

    Raises
    ------
    RuntimeError
        If ``pymzml`` is not installed.
    ValueError
        If *rt_min* >= *rt_max*.
    FileNotFoundError
        If *mzml_path* does not exist.
    """
    try:
        from pymzml.run import Reader  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "mzML bridge requires pymzml.\n"
            f"Import error: {exc}\n\n"
            "Install it with: pip install pymzml"
        ) from exc

    if rt_min >= rt_max:
        raise ValueError(f"rt_min ({rt_min}) must be < rt_max ({rt_max})")

    if not os.path.isfile(mzml_path):
        raise FileNotFoundError(f"mzML file not found: {mzml_path}")

    # ── parse mzML ──────────────────────────────────────────────────────────
    if progress_callback:
        progress_callback("Чтение mzML…")

    reader = Reader(mzml_path)
    try:
        rt_min_sec = rt_min * 60.0
        rt_max_sec = rt_max * 60.0

        # Collect (m/z, intensity) pairs from all MS1 scans in the RT window
        all_mz: list[float] = []
        all_int: list[float] = []

        scan_count = 0
        for spec in reader:
            ms_level = spec.get("ms level", 1)
            if ms_level != 1:
                continue

            rt = spec.scan_time_in_minutes() * 60.0
            if rt < rt_min_sec or rt > rt_max_sec:
                continue

            peaks = spec.peaks("raw")  # (mz_array, intensity_array)
            if peaks is not None and len(peaks[0]) > 0:
                all_mz.extend(peaks[0].tolist())
                all_int.extend(peaks[1].tolist())
                scan_count += 1
    finally:
        reader.close()

    if scan_count == 0:
        raise ValueError(
            f"No MS1 scans found in RT window [{rt_min}, {rt_max}] min"
        )

    # ── average: group by m/z (5-decimal tolerance) and sum intensities ─────
    if progress_callback:
        progress_callback("Усреднение спектров…")

    mz_array = np.array(all_mz)
    int_array = np.array(all_int)

    rounded = np.round(mz_array, 5)
    unique_mz, inverse = np.unique(rounded, return_inverse=True)
    summed_int = np.zeros(len(unique_mz))
    np.add.at(summed_int, inverse, int_array)

    # ── write CSV ───────────────────────────────────────────────────────────
    if progress_callback:
        progress_callback("Запись CSV…")

    if output_csv is None:
        base = os.path.splitext(os.path.basename(mzml_path))[0]
        out_dir = os.path.dirname(mzml_path) or "."
        output_csv = os.path.join(out_dir, f"{base}_avrg.csv")

    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mass", "intensity"])
        for mz, intens in zip(unique_mz, summed_int):
            writer.writerow([f"{mz:.6f}", f"{intens:.2f}"])

    return os.path.abspath(output_csv)


def is_available() -> bool:
    """Check whether mzML bridge is available (pymzml importable)."""
    try:
        import pymzml  # noqa: F401
        return True
    except ImportError:
        return False


def availability_error() -> Optional[str]:
    """Return a human-readable error if mzML is unavailable, else None."""
    if is_available():
        return None
    return "pymzml is not installed. Run: pip install pymzml"
