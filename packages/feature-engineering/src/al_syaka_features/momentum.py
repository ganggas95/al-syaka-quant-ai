"""Momentum & price features."""

import pandas as pd
import numpy as np


def momentum_features(close: pd.Series, volume: pd.Series | None = None) -> dict:
    """Extract momentum-based features."""
    # Price momentum
    mom_1 = close.pct_change(1)
    mom_5 = close.pct_change(5)
    mom_10 = close.pct_change(10)
    mom_20 = close.pct_change(20)

    # Rate of Change
    roc_10 = (close / close.shift(10) - 1) * 100

    # Distance from moving averages (requires pre-computed MAs)
    # Price position relative to recent range
    highest_10 = close.rolling(10).max()
    lowest_10 = close.rolling(10).min()
    price_position = (close - lowest_10) / (highest_10 - lowest_10).replace(0, np.nan)

    result = {
        "mom_1": mom_1,
        "mom_5": mom_5,
        "mom_10": mom_10,
        "mom_20": mom_20,
        "roc_10": roc_10,
        "price_position_10": price_position,
    }

    if volume is not None:
        # Volume-weighted momentum
        vim = (close * volume).rolling(10).sum() / volume.rolling(10).sum()
        result["vim_10"] = vim

    return result
