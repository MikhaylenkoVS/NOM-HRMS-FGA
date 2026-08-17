"""Distribution metrics (H/C, O/C, DBE, AI) and histogram plotting for NOM results.

Provides per-formula distribution metrics plus a ready-made matplotlib figure
with the six standard NOM distribution histograms. Mirrors the split used in
``src.core.van_krevelen`` (computation + plotting in one module).
"""

from __future__ import annotations

import warnings

import matplotlib.pyplot as plt
import pandas as pd

from src.core.domain.molecule import parse_formula


def dbe(counts: dict) -> float:
    """Double-bond equivalents (DBE / IHD): ``(2*C + 2 + N - H) / 2``."""
    c = counts.get("C", 0)
    h = counts.get("H", 0)
    n = counts.get("N", 0)
    return (2 * c + 2 + n - h) / 2


def aromaticity_index(counts: dict) -> float | None:
    """Koch & Dittmar (2006) aromaticity index.

    ``AI = (1 + C - O - S - 0.5*H) / (C - O - S - N)``.
    Returns ``None`` when the denominator is non-positive.
    """
    c = counts.get("C", 0)
    h = counts.get("H", 0)
    o = counts.get("O", 0)
    n = counts.get("N", 0)
    s = counts.get("S", 0)
    denom = c - o - s - n
    if denom <= 0:
        return None
    return (1 + c - o - s - 0.5 * h) / denom


def compute_distribution_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Compute H/C, O/C, DBE, AI, N_COOH, N_OH for each formula in a result table.

    Parameters
    ----------
    df : pandas.DataFrame
        Result table with at least a ``brutto`` column; ``N_COOH`` / ``N_OH``
        are optional and default to 0 when absent.

    Returns
    -------
    pandas.DataFrame
        Columns: ``brutto``, ``mass``, ``intensity``, ``h_c``, ``o_c``,
        ``dbe``, ``ai``, ``n_cooh``, ``n_oh``.
    """
    rows = []
    skipped = 0
    for _, row in df.iterrows():
        brutto = str(row.get("brutto", "") or "")
        if not brutto or brutto.lower() in ("nan", "none"):
            continue
        counts = parse_formula(brutto)
        c = counts.get("C", 0)
        if c == 0:
            skipped += 1
            continue
        rows.append(
            {
                "brutto": brutto,
                "mass": row.get("mass"),
                "intensity": row.get("intensity"),
                "h_c": counts.get("H", 0) / c,
                "o_c": counts.get("O", 0) / c,
                "dbe": dbe(counts),
                "ai": aromaticity_index(counts),
                "n_cooh": row.get("N_COOH", 0),
                "n_oh": row.get("N_OH", 0),
            }
        )
    if skipped:
        warnings.warn(f"{skipped} row(s) skipped (zero carbon).", stacklevel=2)
    return pd.DataFrame(rows)


#: (column, axis label, colour) for each histogram panel.
HISTOGRAM_METRICS: list[tuple[str, str, str]] = [
    ("h_c", "H/C", "#f38ba8"),
    ("o_c", "O/C", "#a6e3a1"),
    ("dbe", "DBE", "#89b4fa"),
    ("ai", "AI", "#fab387"),
    ("n_cooh", "N_COOH", "#cba6f7"),
    ("n_oh", "N_OH", "#94e2d5"),
]


def create_histograms_plot(df: pd.DataFrame, figsize=(10, 6)) -> plt.Figure:
    """Build a 2x3 grid of distribution histograms for a result table.

    Returns
    -------
    matplotlib.figure.Figure
        The figure; the caller is responsible for closing it.
    """
    metrics = compute_distribution_metrics(df)
    if metrics.empty:
        raise ValueError("No valid formulas to build histograms.")

    fig, axes = plt.subplots(2, 3, figsize=figsize)
    fig.patch.set_facecolor("white")
    for ax, (col, label, color) in zip(axes.flat, HISTOGRAM_METRICS):
        vals = metrics[col].dropna()
        if col in ("n_cooh", "n_oh"):
            vals = vals.astype(int)
            bins = range(int(vals.max()) + 2) if not vals.empty else 1
        else:
            bins = 20
        ax.hist(
            vals, bins=bins, color=color, alpha=0.85, edgecolor="white", rwidth=0.85
        )
        ax.set_xlabel(label, fontsize=9)
        ax.set_ylabel("Кол-во", fontsize=8)
        ax.set_title(label, fontsize=10, color="#333333")
        ax.set_facecolor("white")
        ax.grid(True, alpha=0.3)
    fig.suptitle("Распределения", fontsize=12, color="#333333", weight="bold")
    fig.tight_layout()
    return fig
