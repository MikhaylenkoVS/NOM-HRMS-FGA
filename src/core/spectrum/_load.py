"""Auto-generated."""

import logging
import pandas as pd
import warnings
import numpy as np
from src.core.domain.spectrum import Spectrum
from src.configs import PIPELINE
from src.configs.loader import SPECTRUM_LOAD_CFG
from ._constants import _FORMULA_SEARCH, _FS_RANGES, _FS_ELEMENTS

logger = logging.getLogger(__name__)

# load_spectrum() и app.py
CSV_COLUMN_MAPPER = {
    "m/z": "mass",
    "M/Z": "mass",
    "mz": "mass",
    "mass": "mass",
    "Intensity": "intensity",
    "I": "intensity",
    "int": "intensity",
    "Int": "intensity",
}


def _read_table(path, sep):
    """Read a spectrum table from CSV, XLSX or JSON (detected by extension).

    Parameters
    ----------
    path : str or path-like
        Path to the data file.
    sep : str
        Field separator for CSV input.

    Returns
    -------
    pandas.DataFrame
        The loaded table.
    """
    p = str(path).lower()
    if p.endswith((".xlsx", ".xls")):
        return pd.read_excel(path)
    if p.endswith(".json"):
        return pd.read_json(path, orient="records")
    return pd.read_csv(path, sep=sep, encoding="utf-8")


def load_spectrum(
    path,
    mapper=None,
    sep=",",
    mass_min=PIPELINE.load_spectrum_defaults["mass_min"],
    mass_max=PIPELINE.load_spectrum_defaults["mass_max"],
    metadata=None,
):
    """Load a mass spectrum from a CSV / XLSX / JSON file into a Spectrum object.

    The format is detected by file extension: ``.csv``, ``.xlsx`` / ``.xls``
    or ``.json``.

    Parameters
    ----------
    path : str or path-like
        Path to the file with mass and intensity columns.
    mapper : dict, optional
        Extra column-rename rules merged over the built-in defaults
        (which map ``m/z``, ``mz``, ``I`` etc. to ``mass``/``intensity``).
    sep : str, optional
        Field separator. Empty/``None`` falls back to ``","``. Default ``","``.
    mass_min, mass_max : float, optional
        Inclusive m/z window (Da) to keep. Defaults 200.0 and 700.0.
    metadata : optional
        Metadata forwarded to the ``Spectrum`` constructor.

    Returns
    -------
    Spectrum
        Spectrum whose table has ``mass`` and ``intensity`` columns,
        filtered to the requested window.

    Raises
    ------
    ValueError
        If the file cannot be read or no peaks fall within the m/z window.
    KeyError
        If ``mass``/``intensity`` columns are absent after renaming.
    """

    _sep = sep or ","

    try:
        df = _read_table(path, _sep)
    except Exception as e:
        # Логируем на уровне core для разработчика
        logger.exception("Ошибка чтения файла %r", path)
        # Поднимаем дальше осмысленное исключение
        raise ValueError(f"Не удалось прочитать файл '{path}': {e}") from e

    df.columns = [c.strip() for c in df.columns]

    _default_mapper = CSV_COLUMN_MAPPER.copy()
    if mapper:
        _default_mapper.update(mapper)

    df = df.rename(columns=_default_mapper)

    logger.debug(
        "Файл %r: колонки после rename: %r",
        path,
        df.columns.tolist(),
    )

    required = ["mass", "intensity"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(
            f"Колонки {missing} не найдены после переименования. "
            f"Доступные: {df.columns.tolist()}"
        )

    df = df[["mass", "intensity"]].copy()

    df = df[(df["mass"] >= mass_min) & (df["mass"] <= mass_max)].reset_index(drop=True)

    if len(df) == 0:
        raise ValueError(
            f"Для файла '{path}' не найдено ни одного пика "
            f"в диапазоне {mass_min}–{mass_max} Da"
        )

    sp = Spectrum(table=df, metadata=metadata)
    return sp


# ===========================================================================
# Шумоподавление
# ===========================================================================
