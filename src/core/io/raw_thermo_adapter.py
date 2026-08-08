"""ThermoRAW → averaged CSV bridge via RawFileReader (.NET), MPL-2.0.

Replaces the GPL-3.0 COM bridge with a clean-room
implementation using Thermo Fisher's RawFileReader .NET library and
``pythonnet``.

Requirements (Windows only):
    * ``pythonnet>=3.0``
    * RawFileReader v5 DLLs in ``thermo/`` (4 files).
    * .NET Framework 4.7.1 or later.
"""

from __future__ import annotations

import os
import sys
from typing import Callable

import numpy as np
import pandas as pd

# ── Lazy state ───────────────────────────────────────────────────────────────

_RAW_AVAILABLE: bool | None = None  # None = not probed yet
_RAW_ERROR: str | None = None


# ── DLL resolution ────────────────────────────────────────────────────────────


def _thermo_dll_dir() -> str:
    """Path to the directory containing the RawFileReader .NET DLLs."""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "thermo")
    return os.path.join(os.path.dirname(__file__), "..", "..", "..", "thermo")


_REQUIRED_DLLS = [
    "ThermoFisher.CommonCore.Data.dll",
    "ThermoFisher.CommonCore.RawFileReader.dll",
    "ThermoFisher.CommonCore.BackgroundSubtraction.dll",
    "ThermoFisher.CommonCore.MassPrecisionEstimator.dll",
]


def _check_dlls() -> tuple[bool, str | None]:
    """Verify all required DLLs are present."""
    dll_dir = _thermo_dll_dir()
    missing = []
    for name in _REQUIRED_DLLS:
        if not os.path.isfile(os.path.join(dll_dir, name)):
            missing.append(name)
    if missing:
        return False, f"Missing RawFileReader DLLs in {dll_dir}: {', '.join(missing)}"
    return True, None


# ── Public API ────────────────────────────────────────────────────────────────


def is_available() -> bool:
    """Check whether ThermoRAW processing is available on this machine."""
    global _RAW_AVAILABLE, _RAW_ERROR
    if _RAW_AVAILABLE is not None:
        return _RAW_AVAILABLE

    # 1. DLL presence
    ok, err = _check_dlls()
    if not ok:
        _RAW_ERROR = err
        _RAW_AVAILABLE = False
        return False

    # 2. pythonnet + CLR probe
    try:
        import clr  # noqa: F401
        import System  # noqa: F401
    except Exception as exc:
        _RAW_ERROR = f"pythonnet / CLR not available: {exc}"
        _RAW_AVAILABLE = False
        return False

    _RAW_AVAILABLE = True
    _RAW_ERROR = None
    return True


def availability_error() -> str | None:
    """Return a human-readable error if RAW support is unavailable, else None."""
    if _RAW_AVAILABLE is None:
        is_available()  # probe
    return _RAW_ERROR


# ── Core: average RAW → CSV ───────────────────────────────────────────────────


def average_raw_to_csv(
    raw_path: str,
    rt_min: float,
    rt_max: float,
    output_csv: str | None = None,
    progress_callback: Callable[[str], None] | None = None,
) -> str:
    """Average a ThermoRAW file over [rt_min, rt_max] and write a CSV.

    Parameters
    ----------
    raw_path : str
        Path to the ``.raw`` file.
    rt_min, rt_max : float
        Retention-time window (minutes).
    output_csv : str or None
        Target path; auto-generated from *raw_path* when ``None``.
    progress_callback : callable or None
        Called with status messages during processing.

    Returns
    -------
    str
        Absolute path to the written CSV.
    """
    if not is_available():
        raise RuntimeError(f"RawFileReader not available: {_RAW_ERROR}")

    if rt_min >= rt_max:
        raise ValueError(f"rt_min ({rt_min}) must be < rt_max ({rt_max})")

    if not os.path.isfile(raw_path):
        raise FileNotFoundError(f"RAW file not found: {raw_path}")

    _log(progress_callback, f"Opening {raw_path} …")

    df = average_raw_to_df(raw_path, rt_min, rt_max, progress_callback)

    if output_csv is None:
        base = os.path.splitext(os.path.basename(raw_path))[0]
        output_csv = os.path.join(
            os.path.dirname(raw_path) or ".", f"{base}_averaged.csv"
        )

    output_csv = os.path.abspath(output_csv)
    df.to_csv(output_csv, index=False, float_format="%.6f")
    _log(progress_callback, f"Written {len(df)} peaks → {output_csv}")
    return output_csv


def average_raw_to_df(
    raw_path: str,
    rt_min: float,
    rt_max: float,
    progress_callback: Callable[[str], None] | None = None,
) -> pd.DataFrame:
    """Average a ThermoRAW file over [rt_min, rt_max] → DataFrame.

    Columns: ``mass``, ``intensity``.
    """
    if not is_available():
        raise RuntimeError(f"RawFileReader not available: {_RAW_ERROR}")

    import clr

    dll_dir = _thermo_dll_dir()
    sys.path.insert(0, dll_dir)

    clr.AddReference("ThermoFisher.CommonCore.Data")
    clr.AddReference("ThermoFisher.CommonCore.RawFileReader")
    clr.AddReference("ThermoFisher.CommonCore.BackgroundSubtraction")
    clr.AddReference("ThermoFisher.CommonCore.MassPrecisionEstimator")

    from ThermoFisher.CommonCore.Data import ToleranceUnits, Extensions
    from ThermoFisher.CommonCore.Data.Business import Device
    from ThermoFisher.CommonCore.Data.Interfaces import IScanFilter
    from ThermoFisher.CommonCore.RawFileReader import RawFileReaderAdapter

    _log(progress_callback, "Connecting to RawFileReader …")

    raw_file = RawFileReaderAdapter.FileFactory(raw_path)
    try:
        if not raw_file.IsOpen or raw_file.IsError:
            raise RuntimeError(f"Cannot open RAW file: {raw_file.FileError}")

        raw_file.SelectInstrument(Device.MS, 1)

        first_scan = raw_file.RunHeaderEx.FirstSpectrum
        last_scan = raw_file.RunHeaderEx.LastSpectrum
        _log(
            progress_callback,
            f"Scans: {first_scan}–{last_scan}, RT window: {rt_min:.2f}–{rt_max:.2f} min",
        )

        # Find scan range for the RT window
        start_scan = _scan_at_rt(raw_file, rt_min, first_scan, last_scan, "first")
        end_scan = _scan_at_rt(raw_file, rt_max, first_scan, last_scan, "last")
        _log(progress_callback, f"RT → scans {start_scan}–{end_scan}")

        if start_scan > end_scan:
            raise ValueError(
                f"No scans in RT window [{rt_min:.2f}, {rt_max:.2f}]. "
                f"File RT range: [{raw_file.RunHeaderEx.StartTime:.4f}, {raw_file.RunHeaderEx.EndTime:.4f}]"
            )

        # Average using the built-in method
        options = Extensions.DefaultMassOptions(raw_file)
        options.ToleranceUnits = ToleranceUnits.ppm
        options.Tolerance = 5.0

        scan_filter = IScanFilter(raw_file.GetFilterForScanNumber(start_scan))

        _log(progress_callback, f"Averaging {end_scan - start_scan + 1} scans …")

        avg_scan = Extensions.AverageScansInScanRange(
            raw_file, start_scan, end_scan, scan_filter, options
        )

        if avg_scan.HasCentroidStream:
            masses = np.array(list(avg_scan.CentroidScan.Masses), dtype=float)
            intensities = np.array(list(avg_scan.CentroidScan.Intensities), dtype=float)
            _log(progress_callback, f"Averaged centroid spectrum: {len(masses)} peaks")
        else:
            masses = np.array(list(avg_scan.SegmentedScan.Positions), dtype=float)
            intensities = np.array(
                list(avg_scan.SegmentedScan.Intensities), dtype=float
            )
            _log(progress_callback, f"Averaged segmented spectrum: {len(masses)} peaks")
    finally:
        raw_file.Dispose()

    return pd.DataFrame({"mass": masses, "intensity": intensities})


# ── Helpers ────────────────────────────────────────────────────────────────────


def _scan_at_rt(raw_file, target_rt: float, first: int, last: int, mode: str) -> int:
    """Binary-search for the scan closest to *target_rt* minutes.

    Parameters
    ----------
    mode : ``"first"``
        Return the first scan ≥ target_rt.
    mode : ``"last"``
        Return the last scan ≤ target_rt.
    """
    lo, hi = first, last
    while lo < hi:
        mid = (lo + hi) // 2
        rt = raw_file.RetentionTimeFromScanNumber(mid)
        if rt < target_rt:
            lo = mid + 1
        else:
            hi = mid
    if mode == "last":
        while lo > first and raw_file.RetentionTimeFromScanNumber(lo) > target_rt:
            lo -= 1
        while lo < last and raw_file.RetentionTimeFromScanNumber(lo + 1) <= target_rt:
            lo += 1
    return lo


def _log(cb: Callable[[str], None] | None, msg: str) -> None:
    if cb:
        cb(msg)
