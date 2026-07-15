"""Utility helpers for quantitative analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd


def to_dataframe(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Convert a list of dictionaries to a pandas DataFrame."""
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)
