"""ThermoRAW → averaged CSV bridge (facade over RawFileReader .NET), MPL-2.0.

Delegates to ``src.core.raw_thermo_adapter`` which uses Thermo Fisher's
RawFileReader .NET library via ``pythonnet``.
"""

from __future__ import annotations

import pandas as pd

from src.core.raw_thermo_adapter import (
    is_available,
    availability_error,
    average_raw_to_csv as _average_raw_to_csv,
)

__all__ = [
    "is_available",
    "availability_error",
    "average_raw_to_csv",
    "average_raw_to_df",
]


def average_raw_to_csv(*args, **kwargs):
    """Average a ThermoRAW file over [rt_min, rt_max] and write a CSV.

    See ``src.core.raw_thermo_adapter.average_raw_to_csv`` for full docs.
    """
    return _average_raw_to_csv(*args, **kwargs)


def average_raw_to_df(raw_path: str, rt_min: float, rt_max: float) -> pd.DataFrame:
    """Average a ThermoRAW file → DataFrame with mass, intensity columns."""
    csv_path = average_raw_to_csv(raw_path, rt_min, rt_max)
    return pd.read_csv(csv_path)
