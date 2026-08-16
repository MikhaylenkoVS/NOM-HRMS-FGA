"""Result-table export helpers (CSV / XLSX / JSON), MPL-2.0.

The format is chosen by file extension:

* ``.csv``  — semicolon-separated CSV (``utf-8-sig``)
* ``.xlsx`` / ``.xls`` — Excel with auto-fitted column widths
* ``.json`` — machine-readable, with a ``metadata`` block (version, params, date)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd


def export_result_table(df: pd.DataFrame, path, metadata: dict | None = None) -> None:
    """Write a result DataFrame to CSV / XLSX / JSON (format by extension).

    Parameters
    ----------
    df : pandas.DataFrame
        The result table to export.
    path : str or path-like
        Target path; extension selects the format.
    metadata : dict or None, optional
        Extra fields merged into the JSON ``metadata`` block (e.g. ``params``).
    """
    p = str(path)
    lower = p.lower()

    if lower.endswith((".xlsx", ".xls")):
        _write_xlsx(df, p)
    elif lower.endswith(".json"):
        _write_json(df, p, metadata)
    else:
        df.to_csv(p, index=False, sep=";", encoding="utf-8-sig")


def _write_xlsx(df: pd.DataFrame, path: str) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="result")
        worksheet = writer.sheets["result"]
        _autofit_columns(worksheet, df)


def _autofit_columns(worksheet, df: pd.DataFrame) -> None:
    """Set each column's width to fit its content (header + first 200 rows)."""
    from openpyxl.utils import get_column_letter

    for idx, col in enumerate(df.columns, start=1):
        lengths = [len(str(col))]
        lengths.extend(len(str(v)) for v in df[col].head(200))
        width = min(max(lengths) + 2, 80)
        worksheet.column_dimensions[get_column_letter(idx)].width = width


def _write_json(df: pd.DataFrame, path: str, metadata: dict | None) -> None:
    payload = {
        "metadata": {
            "version": _get_version(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            **((metadata or {})),
        },
        "data": df.to_dict(orient="records"),
    }
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)


def _get_version() -> str | None:
    """Return the package version, resolved lazily to avoid circular imports."""
    try:
        from src import __version__

        return __version__
    except Exception:
        return None
