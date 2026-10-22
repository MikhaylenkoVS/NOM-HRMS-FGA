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
    for extra in (
        "iso_variants",
        "iso_satellite_of",
        "iso_satellite_label",
        "iso_status",
        "iso_dev",
        "iso_halogen_unconfirmed",
    ):
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
    if "iso_status" not in base.columns:
        base["iso_status"] = ""
    if "iso_dev" not in base.columns:
        base["iso_dev"] = float("nan")
    if "iso_halogen_unconfirmed" not in base.columns:
        base["iso_halogen_unconfirmed"] = False

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
        base_cols = {
            "mass_key": pd.Series(dtype="float64"),
            f"n_{prefix}": pd.Series(dtype="int64"),
            f"missing_{prefix}": pd.Series(dtype="object"),
            f"confirmed_{prefix}": pd.Series(dtype="int64"),
            f"ambiguous_{prefix}": pd.Series(dtype="int64"),
            f"display_{prefix}": pd.Series(dtype="object"),
            f"conf_{prefix}": pd.Series(dtype="float64"),
            f"details_{prefix}": pd.Series(dtype="object"),
        }
        if df.empty:
            return pd.DataFrame(base_cols)
        cols = ["mass_src", "n_groups", "missing"]
        for extra in (
            "p_value",
            "significant",
            "confirmed_length",
            "ambiguous_length",
            "display_length",
            "confidence",
            "step_details",
        ):
            if extra in df.columns:
                cols.append(extra)
        tmp = df[cols].copy()
        tmp["mass_key"] = tmp["mass_src"].round(4)
        rename = {
            "n_groups": f"n_{prefix}",
            "missing": f"missing_{prefix}",
            "p_value": f"p_{prefix}",
            "significant": f"sig_{prefix}",
            "confirmed_length": f"confirmed_{prefix}",
            "ambiguous_length": f"ambiguous_{prefix}",
            "display_length": f"display_{prefix}",
            "confidence": f"conf_{prefix}",
            "step_details": f"details_{prefix}",
        }
        out_cols = [
            "mass_key",
            f"n_{prefix}",
            f"missing_{prefix}",
            f"confirmed_{prefix}",
            f"ambiguous_{prefix}",
            f"display_{prefix}",
            f"conf_{prefix}",
            f"details_{prefix}",
        ]
        if "p_value" in tmp.columns:
            out_cols.append(f"p_{prefix}")
        if "significant" in tmp.columns:
            out_cols.append(f"sig_{prefix}")
        return tmp.rename(columns=rename)[out_cols]

    result = base.merge(_enrich(df_dmet, "dmet"), on="mass_key", how="left").merge(
        _enrich(df_dacet, "dacet"), on="mass_key", how="left"
    )

    result["n_dmet"] = result["n_dmet"].fillna(0).astype(int)
    result["n_dacet"] = result["n_dacet"].fillna(0).astype(int)

    # Основное число — подтверждённая reliable-длина; ambiguous выводится
    # отдельно (в GUI — в скобках). n_groups остаётся как «сырая» длина.
    for prefix, col in (("dmet", "N_COOH"), ("dacet", "N_OH")):
        result[f"confirmed_{prefix}"] = (
            result[f"confirmed_{prefix}"].fillna(0).astype(int)
        )
        result[f"ambiguous_{prefix}"] = (
            result[f"ambiguous_{prefix}"].fillna(0).astype(int)
        )
        result[f"display_{prefix}"] = (
            result[f"display_{prefix}"].fillna("0").astype(str)
        )
        result[f"conf_{prefix}"] = result[f"conf_{prefix}"].fillna(100.0)
        result[col] = result[f"confirmed_{prefix}"]
        result[f"{col}_raw"] = result[f"n_{prefix}"]
        result[f"{col}_ambiguous"] = result[f"ambiguous_{prefix}"]
        result[f"{col}_display"] = result[f"display_{prefix}"]
        result[f"{col}_confidence"] = result[f"conf_{prefix}"]
        result[f"{col}_details"] = result[f"details_{prefix}"]
        result[f"{col}_confirmed"] = result[col]

    out_cols = [
        "mass",
        "intensity",
        "brutto",
        "iso_status",
        "iso_dev",
        "iso_halogen_unconfirmed",
        "all_candidates",
        "iso_variants",
        "iso_satellite_of",
        "iso_satellite_label",
        "N_COOH",
        "N_OH",
        "N_COOH_display",
        "N_OH_display",
        "N_COOH_ambiguous",
        "N_OH_ambiguous",
        "N_COOH_confidence",
        "N_OH_confidence",
        "N_COOH_details",
        "N_OH_details",
        "N_COOH_raw",
        "N_OH_raw",
        "N_COOH_confirmed",
        "N_OH_confirmed",
        "missing_dmet",
        "missing_dacet",
    ]
    out_cols = [c for c in out_cols if c in result.columns]
    return result[out_cols].sort_values("mass").reset_index(drop=True)


# ===========================================================================
# Визуализация серий с пропущенными пиками
# ===========================================================================
