"""Strategy primitives for signal generation and backtesting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pandas as pd


@dataclass
class Signal:
    """Simple signal object used by strategies."""

    symbol: str
    action: str
    confidence: float
    reason: str | None = None


class BaseStrategy:
    """Base class for all quantitative strategies."""

    def __init__(self, symbol: str = "EURUSD") -> None:
        self.symbol = symbol

    def generate(self, df: pd.DataFrame) -> list[Signal]:
        """Generate trading signals from a DataFrame."""
        raise NotImplementedError


class MeanReversionStrategy(BaseStrategy):
    """A simple mean-reversion strategy using moving averages."""

    def __init__(self, symbol: str = "EURUSD", window: int = 20) -> None:
        super().__init__(symbol=symbol)
        self.window = window

    def generate(self, df: pd.DataFrame) -> list[Signal]:
        if df.empty:
            return []

        data = df.copy()
        data["ma"] = data["close"].rolling(self.window).mean()
        data["signal"] = 0
        data.loc[data["close"] > data["ma"], "signal"] = -1
        data.loc[data["close"] < data["ma"], "signal"] = 1

        signals: list[Signal] = []
        for _, row in data.tail(3).iterrows():
            action = "buy" if row["signal"] == 1 else "sell"
            confidence = min(0.95, max(0.55, abs(row["close"] - row["ma"]) / max(row["ma"], 1e-6)))
            signals.append(
                Signal(
                    symbol=self.symbol,
                    action=action,
                    confidence=float(confidence),
                    reason="mean-reversion vs rolling average",
                )
            )
        return signals


class RsiStrategy(BaseStrategy):
    """A simple RSI-based strategy for momentum."""

    def __init__(self, symbol: str = "EURUSD", period: int = 14, oversold: int = 30, overbought: int = 70) -> None:
        super().__init__(symbol=symbol)
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def generate(self, df: pd.DataFrame) -> list[Signal]:
        if df.empty:
            return []

        data = df.copy()
        delta = data["close"].diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(self.period).mean()
        avg_loss = loss.rolling(self.period).mean()
        rs = avg_gain / avg_loss.replace(0, pd.NA)
        rsi = 100 - (100 / (1 + rs))
        data["rsi"] = rsi.fillna(50)

        signals: list[Signal] = []
        for _, row in data.tail(3).iterrows():
            if row["rsi"] <= self.oversold:
                action = "buy"
                confidence = 0.8
            elif row["rsi"] >= self.overbought:
                action = "sell"
                confidence = 0.8
            else:
                action = "hold"
                confidence = 0.5
            signals.append(
                Signal(
                    symbol=self.symbol,
                    action=action,
                    confidence=float(confidence),
                    reason="RSI threshold crossing",
                )
            )
        return signals


class BreakoutStrategy(BaseStrategy):
    """A breakout strategy based on recent highs and lows."""

    def __init__(self, symbol: str = "EURUSD", window: int = 20) -> None:
        super().__init__(symbol=symbol)
        self.window = window

    def generate(self, df: pd.DataFrame) -> list[Signal]:
        if df.empty:
            return []

        data = df.copy()
        data["recent_high"] = data["close"].rolling(self.window).max().shift(1)
        data["recent_low"] = data["close"].rolling(self.window).min().shift(1)

        signals: list[Signal] = []
        for _, row in data.tail(3).iterrows():
            if row["close"] > row["recent_high"]:
                action = "buy"
                confidence = 0.8
            elif row["close"] < row["recent_low"]:
                action = "sell"
                confidence = 0.8
            else:
                action = "hold"
                confidence = 0.5
            signals.append(
                Signal(
                    symbol=self.symbol,
                    action=action,
                    confidence=float(confidence),
                    reason="breakout vs recent range",
                )
            )
        return signals
