"""Candlestick features: Body, Wick, Range, Patterns."""

import pandas as pd
import numpy as np


def candle_features(open: pd.Series, high: pd.Series, low: pd.Series, close: pd.Series) -> dict:
    """Extract candlestick-based features."""
    body = abs(close - open)
    upper_wick = high - pd.concat([open, close], axis=1).max(axis=1)
    lower_wick = pd.concat([open, close], axis=1).min(axis=1) - low
    candle_range = high - low
    body_ratio = body / candle_range.replace(0, np.nan)

    # Candle type
    bullish = (close > open).astype(int)
    bearish = (close < open).astype(int)
    doji = (abs(close - open) <= (candle_range * 0.1)).astype(int)

    return {
        "body": body,
        "upper_wick": upper_wick,
        "lower_wick": lower_wick,
        "candle_range": candle_range,
        "body_ratio": body_ratio,
        "bullish": bullish,
        "bearish": bearish,
        "doji": doji,
    }
