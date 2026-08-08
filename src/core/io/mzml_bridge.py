"""mzML → averaged CSV bridge (requires pymzml for XML parsing only).

Handles both centroided and profile-mode mzML files by decoding the
binary data arrays directly (bypassing pymzml's ``peaks()`` method,
which silently loses data on large profile spectra).

Usage
-----
    from src.core.io.mzml_bridge import mzml_to_csv

    csv_path = mzml_to_csv("sample.mzML", output_csv="averaged.csv",
                           rt_min=0.0, rt_max=30.0)
"""

from __future__ import annotations

import base64
import csv
import os
import zlib
from typing import Callable, Optional

import numpy as np

# mzML XML namespace
_NS = "{http://psi.hupo.org/ms/mzml}"


def _decode_binary(binary_elem) -> np.ndarray:
    """Decode a ``<binaryDataArray>`` element into a numpy float64 array."""
    encoded = binary_elem.find(f"{_NS}binary")
    if encoded is None or not encoded.text:
        return np.array([], dtype=np.float64)

    raw_bytes = base64.b64decode(encoded.text)

    # Detect compression
    params = {cp.get("accession") for cp in binary_elem.findall(f"{_NS}cvParam")}
    if "MS:1000574" in params:  # zlib compression
        raw_bytes = zlib.decompress(raw_bytes)

    # Detect precision
    if "MS:1000521" in params:  # 32-bit float
        return np.frombuffer(raw_bytes, dtype=np.float32).astype(np.float64)
    return np.frombuffer(raw_bytes, dtype=np.float64)


def _centroid_profile(mz_array, int_array, min_intensity=0.0):
    """Extract peaks from profile-mode data via local-maximum detection.

    A data point is kept as a peak if:
    * its intensity > *min_intensity*
    * it is a local maximum (greater than both neighbours)
    """
    mask = int_array > min_intensity
    if not np.any(mask):
        return np.array([]), np.array([])

    greater_left = np.zeros_like(mask, dtype=bool)
    greater_right = np.zeros_like(mask, dtype=bool)
    greater_left[1:] = int_array[1:] > int_array[:-1]
    greater_right[:-1] = int_array[:-1] > int_array[1:]
    is_peak = mask & greater_left & greater_right

    return mz_array[is_peak], int_array[is_peak]


def _spectrum_is_profile(spec_elem) -> bool:
    """Check whether the spectrum element represents a profile spectrum."""
    return any(
        cp.get("accession") == "MS:1000128" for cp in spec_elem.findall(f"{_NS}cvParam")
    )


def mzml_to_csv(
    mzml_path: str,
    output_csv: Optional[str] = None,
    rt_min: float = 0.0,
    rt_max: float = 999.0,
    min_intensity: float = 0.0,
    progress_callback: Optional[Callable[[str], None]] = None,
) -> str:
    """Average all MS1 spectra in *mzml_path* over [*rt_min*, *rt_max*]
    and write a ``mass,intensity`` CSV.

    Parameters
    ----------
    mzml_path : str
        Path to the ``.mzML`` file.
    output_csv : str or None
        Where to write the CSV.  Default: ``<basename>_avrg.csv`` next to mzML.
    rt_min : float
        Start of retention-time window (minutes).  Default 0.0.
    rt_max : float
        End of retention-time window (minutes).  Default 999.0.
    min_intensity : float
        Intensity threshold for profile-mode centroiding.
    progress_callback : callable or None
        Status callback.

    Returns
    -------
    str
        Absolute path to the CSV file.
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
    rt_min_sec = rt_min * 60.0
    rt_max_sec = rt_max * 60.0

    all_mz: list[float] = []
    all_int: list[float] = []

    scan_count = 0
    try:
        for spec in reader:
            # MS level filter
            ms_level = spec.get("ms level", 1)
            if ms_level != 1:
                continue

            # RT filter
            rt_sec = spec.scan_time_in_minutes() * 60.0
            if rt_sec < rt_min_sec or rt_sec > rt_max_sec:
                continue

            # ── manual binary decode (bypass pymzml's buggy peaks()) ────────
            spec_elem = spec.element
            is_profile = _spectrum_is_profile(spec_elem)
            binary_arrays = spec_elem.findall(
                f"{_NS}binaryDataArrayList/{_NS}binaryDataArray"
            )

            mz_arr = None
            int_arr = None

            for ba in binary_arrays:
                array_type = None
                for cp in ba.findall(f"{_NS}cvParam"):
                    acc = cp.get("accession", "")
                    if acc == "MS:1000514":
                        array_type = "mz"
                    elif acc == "MS:1000515":
                        array_type = "intensity"

                if array_type == "mz":
                    mz_arr = _decode_binary(ba)
                elif array_type == "intensity":
                    int_arr = _decode_binary(ba)

            if mz_arr is None or int_arr is None or len(mz_arr) == 0:
                continue

            if is_profile:
                mz_cent, int_cent = _centroid_profile(mz_arr, int_arr, min_intensity)
                if len(mz_cent) > 0:
                    all_mz.extend(mz_cent.tolist())
                    all_int.extend(int_cent.tolist())
            else:
                all_mz.extend(mz_arr.tolist())
                all_int.extend(int_arr.tolist())

            scan_count += 1
    finally:
        reader.close()

    if scan_count == 0:
        raise ValueError(f"No MS1 scans found in RT window [{rt_min}, {rt_max}] min")

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
        for mz, ints in zip(unique_mz, summed_int):
            writer.writerow([f"{mz:.6f}", f"{ints:.2f}"])

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
