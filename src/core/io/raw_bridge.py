"""ThermoRAW → averaged JSON bridge (facade over RawFileReader .NET), MPL-2.0.

Delegates to ``src.core.io.raw_thermo_adapter`` which uses Thermo Fisher's
RawFileReader .NET library via ``pythonnet``.
"""

from __future__ import annotations

import pandas as pd

from src.core.io.raw_thermo_adapter import (
    is_available,
    availability_error,
    average_raw_to_json as _average_raw_to_json,
)

__all__ = [
    "is_available",
    "availability_error",
    "average_raw_to_json",
    "average_raw_to_df",
]


def average_raw_to_json(*args, **kwargs):
    """Average a ThermoRAW file over [rt_min, rt_max] and write a JSON table.

    See ``src.core.io.raw_thermo_adapter.average_raw_to_json`` for full docs.
    """
    return _average_raw_to_json(*args, **kwargs)


def average_raw_to_df(raw_path: str, rt_min: float, rt_max: float) -> pd.DataFrame:
    """Average a ThermoRAW file → DataFrame with mass, intensity columns."""
    json_path = average_raw_to_json(raw_path, rt_min, rt_max)
    return pd.read_json(json_path, orient="records")
