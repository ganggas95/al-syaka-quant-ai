"""Simple backtesting helpers for quant strategies."""

from __future__ import annotations

from typing import Any

import pandas as pd

from .strategies import BaseStrategy, Signal


def run_backtest(strategy: BaseStrategy, df: pd.DataFrame) -> dict[str, Any]:
    """Run a simple backtest and return a summary dictionary."""
    signals = strategy.generate(df)
    return {
        "strategy": strategy.__class__.__name__,
        "symbol": getattr(strategy, "symbol", "unknown"),
        "signal_count": len(signals),
        "signals": [signal.__dict__ for signal in signals],
    }
