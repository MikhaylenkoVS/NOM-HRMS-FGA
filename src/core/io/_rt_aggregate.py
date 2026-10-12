"""Pure helpers for RT-segmented chromatogram averaging.

These functions have no external dependencies (numpy/pandas only) so they
can be unit-tested without pymzml or pythonnet.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

#: m/z rounding tolerance used when aggregating scans inside a segment.
_MZ_ROUND_DECIMALS = 5


def build_rt_segments(
    rt_min: float, rt_max: float, segment_width: float
) -> list[tuple[float, float]]:
    """Split ``[rt_min, rt_max]`` into half-open ``(start, end)`` segments.

    Parameters
    ----------
    rt_min : float
        Start of the retention-time range (minutes).
    rt_max : float
        End of the retention-time range (minutes).
    segment_width : float
        Width of each segment (minutes).  Must be > 0.

    Returns
    -------
    list of (float, float)
        Segments covering the range, e.g. ``(0, 2), (2, 4), ...``.  The
        last segment is truncated to ``rt_max``.
    """
    if segment_width <= 0:
        raise ValueError(f"segment_width must be > 0, got {segment_width}")
    if rt_min >= rt_max:
        raise ValueError(f"rt_min ({rt_min}) must be < rt_max ({rt_max})")

    segments: list[tuple[float, float]] = []
    start = float(rt_min)
    while start < rt_max:
        end = min(start + float(segment_width), float(rt_max))
        segments.append((start, end))
        start = end
    return segments


def _segment_index(rt: float, segments: list[tuple[float, float]]) -> int | None:
    """Return the index of the segment containing *rt*, or ``None``."""
    for idx, (start, end) in enumerate(segments):
        if start <= rt < end:
            return idx
    return None


def aggregate_scans(scans, segments: list[tuple[float, float]]) -> list[pd.DataFrame]:
    """Aggregate scans into per-segment ``mass,intensity`` tables.

    Parameters
    ----------
    scans : iterable of (mz_array, intensity_array, rt_minutes)
        One tuple per MS1 scan.  ``rt_minutes`` assigns the scan to a
        segment; scans outside all segments are ignored.
    segments : list of (float, float)
        RT segments from :func:`build_rt_segments`.

    Returns
    -------
    list of pandas.DataFrame
        One DataFrame per segment with columns ``mass`` and ``intensity``.
        Intensities of scans with the same m/z (rounded to 5 decimals)
        are summed inside each segment.  Segments without scans produce an
        empty DataFrame.
    """
    buckets: list[list[float]] = [[[], []] for _ in segments]

    for mz_arr, int_arr, rt in scans:
        idx = _segment_index(float(rt), segments)
        if idx is None:
            continue
        mz = np.asarray(mz_arr, dtype=float).ravel()
        inten = np.asarray(int_arr, dtype=float).ravel()
        if len(mz) == 0:
            continue
        buckets[idx][0].extend(mz.tolist())
        buckets[idx][1].extend(inten.tolist())

    result: list[pd.DataFrame] = []
    for mz_list, int_list in buckets:
        if not mz_list:
            result.append(pd.DataFrame({"mass": [], "intensity": []}))
            continue
        mz_array = np.array(mz_list, dtype=float)
        int_array = np.array(int_list, dtype=float)
        rounded = np.round(mz_array, _MZ_ROUND_DECIMALS)
        unique_mz, inverse = np.unique(rounded, return_inverse=True)
        summed_int = np.zeros(len(unique_mz))
        np.add.at(summed_int, inverse, int_array)
        result.append(
            pd.DataFrame(
                {
                    "mass": unique_mz.astype(float),
                    "intensity": summed_int,
                }
            )
        )
    return result
