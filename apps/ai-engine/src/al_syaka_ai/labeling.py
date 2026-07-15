"""Label Generator — Forward-looking labeling untuk training dataset."""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class LabelConfig:
    """Configuration for label generation."""
    forward_bars: int = 12  # Look ahead bars
    tp_percent: float = 0.005  # 0.5% take profit
    sl_percent: float = 0.003  # 0.3% stop loss
    min_holding_bars: int = 3


class LabelGenerator:
    """Generate labels for supervised learning from price data."""

    def __init__(self, config: Optional[LabelConfig] = None):
        self.config = config or LabelConfig()

    def generate_labels(self, close: pd.Series, high: pd.Series, low: pd.Series) -> pd.Series:
        """Generate BUY(1)/SELL(0)/NEUTRAL(-1) labels based on forward returns."""
        labels = pd.Series(-1, index=close.index, dtype=int)

        for i in range(len(close) - self.config.forward_bars):
            entry = close.iloc[i]
            future_high = high.iloc[i + 1:i + self.config.forward_bars + 1].max()
            future_low = low.iloc[i + 1:i + self.config.forward_bars + 1].min()

            tp_hit = (future_high - entry) / entry >= self.config.tp_percent
            sl_hit = (entry - future_low) / entry >= self.config.sl_percent

            if tp_hit and not sl_hit:
                labels.iloc[i] = 1  # BUY
            elif sl_hit and not tp_hit:
                labels.iloc[i] = 0  # SELL
            else:
                # Whichever hit first or larger move
                upside = (future_high - entry) / entry
                downside = (entry - future_low) / entry
                if upside > downside:
                    labels.iloc[i] = 1
                else:
                    labels.iloc[i] = 0

        return labels

    def generate_regression_labels(self, close: pd.Series) -> pd.Series:
        """Generate regression labels — forward returns."""
        future_returns = close.shift(-self.config.forward_bars) / close - 1
        return future_returns.fillna(0)
