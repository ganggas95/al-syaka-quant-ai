"""Volatility features."""

import pandas as pd
import numpy as np


def volatility_features(high: pd.Series, low: pd.Series, close: pd.Series, open: pd.Series | None = None) -> dict:
    """Extract volatility-based features."""
    # True Range based
    tr = pd.concat([
        (high - low).abs(),
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)

    atr_5 = tr.rolling(5).mean()
    atr_10 = tr.rolling(10).mean()
    atr_20 = tr.rolling(20).mean()

    # Normalized volatility
    volatility_10 = close.pct_change().rolling(10).std()
    volatility_20 = close.pct_change().rolling(20).std()

    # Gap features
    gap = None
    if open is not None:
        gap = open - close.shift(1)

    result = {
        "tr": tr,
        "atr_5": atr_5,
        "atr_10": atr_10,
        "atr_20": atr_20,
        "volatility_10": volatility_10,
        "volatility_20": volatility_20,
    }
    if gap is not None:
        result["gap"] = gap

    return result
