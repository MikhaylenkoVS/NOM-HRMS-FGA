"""Build result table."""

import logging
import pandas as pd
import numpy as np
from ._chem import _counts_to_str
from src.core.domain.molecule import parse_formula

logger = logging.getLogger(__name__)


def build_result_table(src, df_dmet, df_dacet):
    """Assemble the final -COOH / -OH count table per brutto formula.

    Parameters
    ----------
    src : Spectrum
        Source spectrum with assigned formulas.
    df_dmet : pandas.DataFrame
        ``find_series`` output for deuteromethylation (CD3 series,
        ``delta = DELTA_CD3``); its ``n_groups`` becomes ``N_COOH``.
    df_dacet : pandas.DataFrame
        ``find_series`` output for deuteroacylation (CD3CO series,
        ``delta = DELTA_CD3CO``); its ``n_groups`` becomes ``N_OH``.

    Returns
    -------
    pandas.DataFrame
        Columns ``mass``, ``intensity``, ``brutto``, ``N_COOH``,
        ``N_OH_total``, ``N_OH``, ``missing_dmet``, ``missing_dacet``,
        sorted by mass. Peaks without a series get a count of 0.

    Notes
    -----
    Source and series peaks are joined on m/z rounded to 4 decimals.
    """
    base = (
        src.table.loc[
            src.table.get("assign", pd.Series(False, index=src.table.index)) == True
        ][["mass", "intensity", "brutto", "all_candidates"]]
        .copy()
        .reset_index(drop=True)
    )
    base["mass_key"] = base["mass"].round(4)

    def _enrich(df, prefix):
        if df.empty:
            return pd.DataFrame(
                {
                    "mass_key": pd.Series(dtype="float64"),
                    f"n_{prefix}": pd.Series(dtype="int64"),
                    f"missing_{prefix}": pd.Series(dtype="object"),
                }
            )
        tmp = df[["mass_src", "n_groups", "missing"]].copy()
        tmp["mass_key"] = tmp["mass_src"].round(4)
        return tmp.rename(
            columns={
                "n_groups": f"n_{prefix}",
                "missing": f"missing_{prefix}",
            }
        )[["mass_key", f"n_{prefix}", f"missing_{prefix}"]]

    result = base.merge(_enrich(df_dmet, "dmet"), on="mass_key", how="left").merge(
        _enrich(df_dacet, "dacet"), on="mass_key", how="left"
    )

    result["n_dmet"] = result["n_dmet"].fillna(0).astype(int)
    result["n_dacet"] = result["n_dacet"].fillna(0).astype(int)
    result["N_COOH"] = result["n_dmet"]
    result["N_OH"] = result["n_dacet"]

    return (
        result[
            [
                "mass",
                "intensity",
                "brutto",
                "all_candidates",
                "N_COOH",
                "N_OH",
                "missing_dmet",
                "missing_dacet",
            ]
        ]
        .sort_values("mass")
        .reset_index(drop=True)
    )


# ===========================================================================
# Визуализация серий с пропущенными пиками
# ===========================================================================
