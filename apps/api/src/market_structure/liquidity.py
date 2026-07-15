"""Liquidity Sweep detection."""

import pandas as pd
import numpy as np
from typing import List


def detect_liquidity_sweep(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    lookback: int = 20,
    sweep_threshold: float = 0.0002,
) -> List[dict]:
    """Detect liquidity sweeps (price piercing recent high/low then reversing)."""
    sweeps = []

    for i in range(lookback, len(close)):
        recent_high = high.iloc[i - lookback:i].max()
        recent_low = low.iloc[i - lookback:i].min()

        # Sweep high (liquidity above)
        if high.iloc[i] > recent_high and close.iloc[i] < high.iloc[i]:
            sweeps.append({
                "type": "SWEEP_HIGH",
                "index": i,
                "swept_level": recent_high,
                "high_reached": high.iloc[i],
                "close": close.iloc[i],
            })

        # Sweep low (liquidity below)
        if low.iloc[i] < recent_low and close.iloc[i] > low.iloc[i]:
            sweeps.append({
                "type": "SWEEP_LOW",
                "index": i,
                "swept_level": recent_low,
                "low_reached": low.iloc[i],
                "close": close.iloc[i],
            })

    return sweeps
