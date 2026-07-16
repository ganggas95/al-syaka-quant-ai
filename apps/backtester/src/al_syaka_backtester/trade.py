"""Trade Record — Data class untuk setiap trade dalam backtest."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


def get_session_name(timestamp: datetime) -> str:
    """Determine trading session from timestamp (UTC)."""
    h = timestamp.hour
    if 0 <= h < 7:
        return "ASIA"
    if 7 <= h < 12:
        return "LONDON"
    if 12 <= h < 20:
        return "NEWYORK"
    return "ASIA"  # 20-24 → back to Asia


@dataclass
class TradeRecord:
    """Single trade record from backtest."""
    entry_time: datetime
    exit_time: Optional[datetime] = None
    signal: str = ""  # BUY/SELL
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    stop_loss: float = 0.0
    take_profit: float = 0.0
    lot_size: float = 0.01
    direction: str = ""  # LONG/SHORT
    result: str = ""  # WIN/LOSS/PENDING
    pips: float = 0.0
    profit: float = 0.0
    profit_percent: float = 0.0
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    exit_reason: str = ""  # TP_HIT, SL_HIT, MANUAL
    session: str = ""  # ASIA, LONDON, NEWYORK
    regime: str = ""  # TRENDING, SIDEWAYS, etc.
    partial_closed: bool = False  # True after partial close executed
    # Trailing stop state (Iteration 007)
    trailing_active: bool = False  # True after trailing is activated
    peak_price: float = 0.0        # Highest (LONG) or lowest (SHORT) price since trailing
    # Trade Attribution metadata (captured at entry time)
    adx_at_entry: float = 0.0
    atr_at_entry: float = 0.0
    volatility_at_entry: str = ""  # HIGH, MEDIUM, LOW
    macro_bias: str = ""  # Bullish, Bearish, Neutral
    composite_score: float = 0.0
    strategy: str = ""  # trend_following, mean_reversion, atr_breakout
