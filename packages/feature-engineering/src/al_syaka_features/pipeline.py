"""Feature Pipeline — orchestrates all feature extraction."""

import pandas as pd
import numpy as np

from al_syaka_indicators import (
    sma, ema, rsi, atr, bollinger_bands,
)
from .candlestick import candle_features
from .momentum import momentum_features
from .volatility import volatility_features as vol_features
from .session import session_features


class FeaturePipeline:
    """Orchestrates extraction of all features from OHLC data."""

    def __init__(self):
        self.features = {}

    def compute(
        self,
        open: pd.Series,
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series | None = None,
        timestamps: pd.Series | None = None,
    ) -> pd.DataFrame:
        """Compute all features and return as a single DataFrame."""
        result = pd.DataFrame(index=close.index)

        # Candlestick features
        candle = candle_features(open, high, low, close)
        result = pd.concat([result, pd.DataFrame(candle, index=close.index)], axis=1)

        # Momentum features
        mom = momentum_features(close, volume)
        result = pd.concat([result, pd.DataFrame(mom, index=close.index)], axis=1)

        # Volatility features
        vol = vol_features(high, low, close)
        result = pd.concat([result, pd.DataFrame(vol, index=close.index)], axis=1)

        # Session features
        if timestamps is not None:
            sess = session_features(timestamps)
            result = pd.concat([result, pd.DataFrame(sess, index=close.index)], axis=1)

        # Key indicators
        result["sma_20"] = sma(close, 20)
        result["sma_50"] = sma(close, 50)
        result["ema_20"] = ema(close, 20)
        result["ema_50"] = ema(close, 50)
        result["rsi_14"] = rsi(close)
        result["atr_14"] = atr(high, low, close)

        # EMA Distance
        result["ema_distance_20"] = (close - result["ema_20"]) / close * 100
        result["ema_distance_50"] = (close - result["ema_50"]) / close * 100

        bb = bollinger_bands(close)
        result["bb_upper"] = bb["upper"]
        result["bb_lower"] = bb["lower"]
        result["bb_position"] = (close - bb["lower"]) / (bb["upper"] - bb["lower"]).replace(0, np.nan)

        self.features = result
        return result
