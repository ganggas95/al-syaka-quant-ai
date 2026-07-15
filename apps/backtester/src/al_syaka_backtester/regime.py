"""Market Regime Classifier — Mendeteksi regime pasar dan memilih strategi adaptif.

Menggabungkan analisis teknikal (ADX, ATR, BB, Supertrend, RSI)
dengan konteks fundamental (economic calendar) untuk menentukan:
  - TRENDING      → Pakai EMA crossover (momentum following)
  - SIDEWAYS      → Pakai Mean Reversion (RSI + BB)
  - HIGH_VOLATILITY → Pakai ATR Breakout
  - NEWS_DAY      → WAIT (skip trading)
"""

from datetime import datetime
from enum import Enum
from typing import Optional


class MarketRegime(Enum):
    """Market regime classification."""
    TRENDING = "TRENDING"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    NEWS_DAY = "NEWS_DAY"


# Trading sessions (UTC)
SESSION_LONDON = (7, 15)     # 07:00 - 15:00 UTC
SESSION_NEWYORK = (12, 20)   # 12:00 - 20:00 UTC
SESSION_ASIA = (0, 7)        # 00:00 - 07:00 UTC


def is_valid_session(timestamp: datetime, sessions: list[tuple[int, int]]) -> bool:
    """Check if timestamp falls within valid trading sessions."""
    hour = timestamp.hour
    for start, end in sessions:
        if start <= hour < end:
            return True
    return False


def is_news_day(timestamp: datetime, economic_provider=None) -> bool:
    """Check if today has a major economic event."""
    if economic_provider is None:
        return False
    risk = economic_provider.get_event_risk_score(from_date=timestamp.date())
    return risk.get("has_major_event_soon", False)


class MarketRegimeClassifier:
    """Market regime classifier + adaptive strategy selector.

    Menggabungkan ADX (trend strength), ATR (volatility),
    dan economic calendar untuk mengklasifikasikan regime pasar.
    """

    def __init__(
        self,
        adx_trending: float = 25,
        adx_sideways: float = 20,
        atr_volatility_ratio: float = 1.5,
        use_session_filter: bool = True,
        valid_sessions: Optional[list[tuple[int, int]]] = None,
        economic_provider=None,
    ):
        self.adx_trending = adx_trending
        self.adx_sideways = adx_sideways
        self.atr_volatility_ratio = atr_volatility_ratio
        self.use_session_filter = use_session_filter
        self.valid_sessions = valid_sessions or [SESSION_LONDON, SESSION_NEWYORK]
        self.economic_provider = economic_provider

    def detect(self, indicators: dict, timestamp: datetime) -> MarketRegime:
        """Detect current market regime berdasarkan indikator."""
        # 1. Session filter — skip di luar jam trading aktif
        if self.use_session_filter and not is_valid_session(timestamp, self.valid_sessions):
            return MarketRegime.SIDEWAYS  # Treat as sideways (low probability trades)

        # 2. News day — prioritas tertinggi
        if is_news_day(timestamp, self.economic_provider):
            return MarketRegime.NEWS_DAY

        try:
            adx_val = indicators.get("adx_adx")
            bb_upper = indicators.get("bb_upper")
            bb_lower = indicators.get("bb_lower")
            bb_middle = indicators.get("bb_middle")

            # Get last values
            adx_last = float(adx_val.iloc[-1]) if adx_val is not None and len(adx_val) > 0 else 0

            # 3. High Volatility — ATR vs BB width
            if bb_upper is not None and bb_lower is not None:
                bb_width = float(bb_upper.iloc[-1] - bb_lower.iloc[-1])
                bb_mid_val = float(bb_middle.iloc[-1]) if bb_middle is not None else 1
                bb_width_pct = bb_width / bb_mid_val if bb_mid_val > 0 else 0

                # If BB width > 2x normal (very wide bands = high volatility)
                if bb_width_pct > 0.15:  # 15% width = extreme volatility
                    return MarketRegime.HIGH_VOLATILITY

            # 4. Trend strength via ADX
            if adx_last >= self.adx_trending:
                return MarketRegime.TRENDING
            elif adx_last < self.adx_sideways:
                return MarketRegime.SIDEWAYS
            else:
                # ADX 20-25: transition zone — check supertrend
                st_dir = indicators.get("supertrend_direction")
                if st_dir is not None and len(st_dir) > 0:
                    st_last = float(st_dir.iloc[-1])
                    if st_last > 0:
                        return MarketRegime.TRENDING
                return MarketRegime.SIDEWAYS

        except (KeyError, IndexError, TypeError, AttributeError):
            return MarketRegime.SIDEWAYS  # Default safe

    def get_strategy_for_regime(self, regime: MarketRegime) -> str:
        """Pilih strategi berdasarkan regime."""
        mapping = {
            MarketRegime.TRENDING: "trend_following",
            MarketRegime.SIDEWAYS: "mean_reversion",
            MarketRegime.HIGH_VOLATILITY: "atr_breakout",
            MarketRegime.NEWS_DAY: "wait",
        }
        return mapping.get(regime, "wait")

    def get_regime_description(self, regime: MarketRegime) -> str:
        """Deskripsi regime."""
        descriptions = {
            MarketRegime.TRENDING: "Strong trend detected (ADX ≥ 25). Using trend following strategy with EMA crossover.",
            MarketRegime.SIDEWAYS: "Sideways / ranging market (ADX < 20). Using mean reversion strategy with RSI + Bollinger Bands.",
            MarketRegime.HIGH_VOLATILITY: "Extreme volatility detected (BB width > 15%). Using ATR breakout strategy.",
            MarketRegime.NEWS_DAY: "Major economic event incoming (FOMC/NFP/CPI). Strategy: WAIT — avoid trading during news.",
        }
        return descriptions.get(regime, "Unknown regime")
