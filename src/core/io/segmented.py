"""RT-segmented averaging facade.

Provides a single entry point that averages RAW / mzML files inside each RT
segment, and treats CSV / XLSX / JSON files (which have no retention-time
axis) as a single segment with ``rt_start=None`` / ``rt_end=None``.
"""

from __future__ import annotations

import pandas as pd

from ._rt_aggregate import aggregate_scans, build_rt_segments  # noqa: F401
from src.core.spectrum import CSV_COLUMN_MAPPER


def average_segments(
    path: str,
    segments: list[tuple[float, float]],
    sep: str = ",",
    progress_callback=None,
) -> list[dict]:
    """Average *path* inside each RT segment.

    Parameters
    ----------
    path : str
        Path to a ``.raw``, ``.mzml``, ``.csv``, ``.xlsx``/``.xls`` or
        ``.json`` spectrum file.
    segments : list of (float, float)
        RT segments (minutes) used for RAW/mzML averaging.
    sep : str, optional
        CSV field separator (used only for ``.csv`` inputs).
    progress_callback : callable or None
        Optional status callback ``(message) -> None``.

    Returns
    -------
    list of dict
        One dict per segment::

            {"df": DataFrame(mass, intensity),
             "rt_start": float | None,
             "rt_end": float | None}

        For RAW/mzML the number of items equals ``len(segments)``.  For
        CSV/XLSX/JSON there is exactly one item with ``rt_start=None``,
        ``rt_end=None``.
    """
    lower = str(path).lower()
    if lower.endswith(".raw"):
        from src.core.io.raw_thermo_adapter import average_raw_segments

        dfs = average_raw_segments(path, segments, progress_callback)
        return [
            {"df": df, "rt_start": s, "rt_end": e}
            for df, (s, e) in zip(dfs, segments)
        ]

    if lower.endswith(".mzml") or lower.endswith(".mzml".lower()):
        from src.core.io.mzml_bridge import mzml_segments_to_dfs

        dfs = mzml_segments_to_dfs(path, segments, progress_callback)
        return [
            {"df": df, "rt_start": s, "rt_end": e}
            for df, (s, e) in zip(dfs, segments)
        ]

    # No retention-time axis → one segment.
    df = _read_table_without_rt(path, sep)
    return [{"df": df, "rt_start": None, "rt_end": None}]


def _read_table_without_rt(path: str, sep: str) -> pd.DataFrame:
    """Read a CSV/XLSX/JSON table and normalize to mass/intensity columns."""
    lower = str(path).lower()
    if lower.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    elif lower.endswith(".json"):
        df = pd.read_json(path, orient="records")
    else:
        df = pd.read_csv(path, sep=sep or ",", encoding="utf-8")

    df.columns = [c.strip() for c in df.columns]
    df = df.rename(columns=CSV_COLUMN_MAPPER)
    missing = [c for c in ("mass", "intensity") if c not in df.columns]
    if missing:
        raise ValueError(
            f"Колонки {missing} не найдены после переименования. "
            f"Доступны: {list(df.columns)}"
        )
    return df[["mass", "intensity"]].copy()
