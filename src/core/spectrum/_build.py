"""Assembly of the final -COOH / -OH count table."""

import logging
import pandas as pd

logger = logging.getLogger(__name__)


def build_result_table(src, df_dmet, df_dacet, drop_isotope_satellites: bool = True):
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
    drop_isotope_satellites : bool, optional
        Убирать из отчёта пики, помеченные как изотопные сателлиты другого
        пика (``iso_satellite_of``): они не самостоятельные соединения.
        Default True.

    Returns
    -------
    pandas.DataFrame
        Columns ``mass``, ``intensity``, ``brutto``, ``all_candidates``,
        ``iso_variants``, ``iso_satellite_of``, ``iso_satellite_label``,
        ``N_COOH``, ``N_OH``, ``missing_dmet``, ``missing_dacet``,
        sorted by mass. Peaks without a series get a count of 0.

    Notes
    -----
    Source and series peaks are joined on m/z rounded to 4 decimals.
    """
    assign_mask = src.table.get("assign", pd.Series(False, index=src.table.index))
    base_cols = ["mass", "intensity", "brutto", "all_candidates"]
    for extra in ("iso_variants", "iso_satellite_of", "iso_satellite_label"):
        if extra in src.table.columns:
            base_cols.append(extra)
    base = src.table.loc[assign_mask][base_cols].copy().reset_index(drop=True)

    # Изотопные сателлиты — не самостоятельные соединения: помечаем
    # (для прозрачности) и убираем из отчёта.
    if "iso_satellite_of" not in base.columns:
        base["iso_satellite_of"] = None
    if "iso_satellite_label" not in base.columns:
        base["iso_satellite_label"] = None
    if "iso_variants" not in base.columns:
        base["iso_variants"] = ""

    def _fmt_variants(items) -> str:
        """Компактная строка: только совпавшие варианты (метка измер/теор)."""
        if not isinstance(items, (list, tuple)):
            return ""
        parts = []
        for v in items:
            if not isinstance(v, dict) or not v.get("ok"):
                continue
            meas = v.get("ratio_measured")
            theor = v.get("ratio_theor") or 0.0
            if meas is None:
                parts.append(f"{v.get('label', '?')}")
            else:
                parts.append(f"{v.get('label', '?')} {meas:.2f}/{theor:.2f}")
        return "; ".join(parts)

    base["iso_variants"] = base["iso_variants"].apply(_fmt_variants)

    if drop_isotope_satellites:
        base = base[base["iso_satellite_of"].isna()].copy()

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

    out_cols = [
        "mass",
        "intensity",
        "brutto",
        "all_candidates",
        "iso_variants",
        "iso_satellite_of",
        "iso_satellite_label",
        "N_COOH",
        "N_OH",
        "missing_dmet",
        "missing_dacet",
    ]
    out_cols = [c for c in out_cols if c in result.columns]
    return result[out_cols].sort_values("mass").reset_index(drop=True)


# ===========================================================================
# Визуализация серий с пропущенными пиками
# ===========================================================================
