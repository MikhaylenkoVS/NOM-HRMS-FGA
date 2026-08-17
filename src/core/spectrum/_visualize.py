"""Auto-generated."""

import logging
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
from ._chem import _nom_distance
from ._constants import FormulaSearchConfig
from ._assign import assign_formulas
from ._series import _find_peak
from src.core.domain.molecule import parse_formula
from src.core.van_krevelen import NOM_REGIONS

logger = logging.getLogger(__name__)


def visualize_series(
    src,
    deriv,
    df_series,
    delta,
    label="series",
    max_rows=15,
    figsize_per_row=(12, 1.4),
    ppm_tol=5.0,
    save_path=None,
):
    """Plot detected series, highlighting missing (gap) peaks.

    For each compound a ladder of expected peaks is drawn: blue = source
    peak ``m_0``, green = found series peak, dashed red = missing expected
    peak.

    Parameters
    ----------
    src : Spectrum
        Source spectrum.
    deriv : Spectrum
        Derivatized-sample spectrum.
    df_series : pandas.DataFrame
        ``find_series`` output to visualize.
    delta : float
        Series step (Da).
    label : str, optional
        Title label. Default ``"series"``.
    max_rows : int, optional
        Maximum number of compounds to display. Default 15.
    figsize_per_row : tuple of (float, float), optional
        Per-row ``(width, height)`` in inches. Default ``(12, 1.4)``.
    ppm_tol : float, optional
        Search tolerance (ppm). Default 5.0.
    save_path : str or None, optional
        If given, the figure is saved to this path; otherwise it is shown.

    Returns
    -------
    None
        Only rows containing gaps are plotted; if none exist the function
        returns after printing a message.
    """
    if df_series.empty:
        logger.info("[%s] Серии не найдены.", label)
        return

    has_missing = df_series[df_series["missing"].apply(len) > 0]
    display_df = has_missing.head(max_rows)

    if display_df.empty:
        logger.info("[%s] Пропущенных пиков в сериях нет.", label)
        return

    n_rows = len(display_df)
    fig, axes = plt.subplots(
        n_rows,
        1,
        figsize=(figsize_per_row[0], figsize_per_row[1] * n_rows + 1.5),
        squeeze=False,
    )
    fig.suptitle(
        f"Серии {label} с пропущенными пиками "
        f"(delta_m = {delta:.5f} Da, допуск {ppm_tol} ppm)",
        fontsize=11,
        fontweight="bold",
    )

    mz_src = src.table["mass"].values
    int_src = src.table["intensity"].values
    mz_deriv = deriv.table["mass"].values
    int_deriv = deriv.table["intensity"].values

    for ax_idx, (_, row) in enumerate(display_df.iterrows()):
        ax = axes[ax_idx][0]
        m0 = row["mass_src"]
        n_groups = row["n_groups"]
        missing = set(row["missing"])
        series = row["series_mz"]

        idx_s = _find_peak(mz_src, m0, ppm_tol * 10)
        i0 = float(int_src[idx_s]) if idx_s is not None else 1.0

        max_i = i0
        for mz_step in series:
            if mz_step is not None:
                idx_d = _find_peak(mz_deriv, mz_step, ppm_tol * 2)
                if idx_d is not None:
                    max_i = max(max_i, float(int_deriv[idx_d]))

        bar_w = delta * 0.08
        ax.bar(m0, i0, width=bar_w, color="steelblue", alpha=0.85)

        for step, mz_step in enumerate(series, start=1):
            expected = m0 + step * delta
            if step in missing or mz_step is None:
                ax.axvline(
                    x=expected,
                    color="crimson",
                    linestyle="--",
                    linewidth=1.0,
                    alpha=0.75,
                )
                ax.text(
                    expected,
                    max_i * 0.55,
                    f"n={step}",
                    color="crimson",
                    fontsize=7,
                    ha="center",
                    va="bottom",
                )
            else:
                idx_d = _find_peak(mz_deriv, float(mz_step), ppm_tol * 2)
                i_step = float(int_deriv[idx_d]) if idx_d is not None else max_i * 0.1
                ax.bar(mz_step, i_step, width=bar_w, color="forestgreen", alpha=0.8)
                ax.text(
                    mz_step,
                    i_step + max_i * 0.02,
                    f"n={step}",
                    color="darkgreen",
                    fontsize=7,
                    ha="center",
                    va="bottom",
                )

        ax.set_xlim(m0 - delta * 0.5, m0 + (n_groups + 1) * delta)
        ax.set_ylim(0, max_i * 1.25)
        ax.set_ylabel("I", fontsize=8)
        ax.set_title(
            f"{row['brutto']}   m/z={m0:.4f}   "
            f"серия 1..{n_groups}   пропущено: {sorted(missing)}",
            fontsize=9,
        )
        ax.tick_params(labelsize=7)

    fig.legend(
        handles=[
            mpatches.Patch(color="steelblue", label="Исходный пик"),
            mpatches.Patch(color="forestgreen", label="Найденный пик серии"),
            mpatches.Patch(
                color="crimson", label="Пропущенный пик (ожидаемая позиция)"
            ),
        ],
        loc="lower center",
        ncol=3,
        fontsize=9,
        frameon=True,
        bbox_to_anchor=(0.5, 0),
    )
    plt.tight_layout(rect=[0, 0.05, 1, 0.96])

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        logger.info("[%s] График сохранён: %s", label, save_path)
    else:
        plt.show()
    plt.close(fig)
