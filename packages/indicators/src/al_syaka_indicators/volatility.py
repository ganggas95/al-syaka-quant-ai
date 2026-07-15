"""Volatility indicators: ATR, Bollinger Bands, Keltner Channels."""

import pandas as pd
import numpy as np


def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
    """Average True Range."""
    high = high.astype(float)
    low = low.astype(float)
    close = close.astype(float)

    tr = pd.concat([
        (high - low).abs(),
        (high - close.shift()).abs(),
        (low - close.shift()).abs(),
    ], axis=1).max(axis=1)

    return tr.ewm(span=period, adjust=False).mean()


def bollinger_bands(
    close: pd.Series,
    period: int = 20,
    std_dev: float = 2.0,
) -> dict:
    """Bollinger Bands."""
    middle = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = middle + (std * std_dev)
    lower = middle - (std * std_dev)
    return {
        "upper": upper,
        "middle": middle,
        "lower": lower,
    }
