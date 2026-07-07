"""Безопасные обёртки для Optional-типов.

Избавляет от необходимости повторять ``if df is not None:`` перед каждым
вызовом DataFrame-методов и устраняет warning'и PyCharm о NoneType.
"""

from __future__ import annotations

import pandas as pd
from typing import TypeVar

_T = TypeVar("_T")


def safe(obj: _T | None, default: _T) -> _T:
    """Вернуть *obj* если не None, иначе *default*.

    Компактная замена повторяющегося guard-паттерна::

        # Было:
        if df is None:
            return
        vals = df[col].dropna()

        # Стало:
        vals = safe(df, pd.DataFrame())[col].dropna()

    Для атрибутов класса с Optional-типом используйте ``_safe_df``.
    """
    return obj if obj is not None else default


def _safe_df(df: pd.DataFrame | None) -> pd.DataFrame:
    """Вернуть *df* если не None, иначе пустой DataFrame."""
    return df if df is not None else pd.DataFrame()
