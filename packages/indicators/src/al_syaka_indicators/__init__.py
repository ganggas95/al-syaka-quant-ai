"""Al-Syaka Indicators — Pure Python technical indicators."""

__version__ = "0.1.0"

from .trend import sma, ema, macd, adx, ichimoku, supertrend, pivot_points
from .oscillators import rsi, stochastic, cci, williams_r
from .volatility import atr, bollinger_bands
from .volume import vwap, volume_profile, obv

__all__ = [
    "sma", "ema", "macd", "adx", "ichimoku", "supertrend", "pivot_points",
    "rsi", "stochastic", "cci", "williams_r",
    "atr", "bollinger_bands",
    "vwap", "volume_profile", "obv",
]


class IndicatorCalculator:
    """Unified calculator that computes all indicators for a given OHLC dataset."""

    def __init__(self, ohlc: dict | None = None):
        """
        Args:
            ohlc: dict with keys 'open', 'high', 'low', 'close', 'volume' as pandas Series
        """
        self.ohlc = ohlc

    def set_data(self, ohlc: dict):
        self.ohlc = ohlc

    def compute_all(self) -> dict:
        """Compute all indicators at once and return as a flat dict."""
        if self.ohlc is None:
            raise ValueError("OHLC data not set. Call set_data() first.")

        high = self.ohlc["high"]
        low = self.ohlc["low"]
        close = self.ohlc["close"]
        volume = self.ohlc.get("volume")

        result = {}

        # Trend
        result["sma_20"] = sma(close, 20)
        result["sma_50"] = sma(close, 50)
        result["sma_200"] = sma(close, 200)
        result["ema_12"] = ema(close, 12)
        result["ema_20"] = ema(close, 20)
        result["ema_50"] = ema(close, 50)

        macd_result = macd(close)
        result.update({f"macd_{k}": v for k, v in macd_result.items()})

        adx_result = adx(high, low, close)
        result.update({f"adx_{k}": v for k, v in adx_result.items()})

        ichi = ichimoku(high, low, close)
        result.update({f"ichimoku_{k}": v for k, v in ichi.items()})

        st = supertrend(high, low, close)
        result["supertrend"] = st["supertrend"]
        result["supertrend_direction"] = st["direction"]

        piv = pivot_points(high, low, close)
        result.update({f"pivot_{k}": v for k, v in piv.items()})

        # Oscillators
        result["rsi_14"] = rsi(close)

        stoch = stochastic(high, low, close)
        result.update({f"stoch_{k}": v for k, v in stoch.items()})

        result["cci_20"] = cci(high, low, close)
        result["williams_r_14"] = williams_r(high, low, close)

        # Volatility
        result["atr_14"] = atr(high, low, close)
        bb = bollinger_bands(close)
        result.update({f"bb_{k}": v for k, v in bb.items()})

        # Volume
        if volume is not None:
            result["vwap"] = vwap(high, low, close, volume)
            result["obv"] = obv(close, volume)

        return result
