"""Fair Value Gap (FVG) detection."""

import pandas as pd
import numpy as np
from typing import List


def detect_fvg(high: pd.Series, low: pd.Series, close: pd.Series, min_gap_pips: float = 0.0001) -> List[dict]:
    """Detect Fair Value Gaps (imbalance between consecutive candles)."""
    fvg_list = []

    for i in range(1, len(high) - 1):
        # Bullish FVG: current low > previous high (gap up)
        if low.iloc[i] > high.iloc[i - 1]:
            gap_top = low.iloc[i]
            gap_bottom = high.iloc[i - 1]
            if gap_top - gap_bottom >= min_gap_pips:
                # Check if gap is filled
                filled = close.iloc[i + 1] < gap_top if i + 1 < len(close) else False
                fvg_list.append({
                    "type": "BULLISH_FVG",
                    "index": i,
                    "gap_high": gap_top,
                    "gap_low": gap_bottom,
                    "filled": filled,
                })

        # Bearish FVG: current high < previous low (gap down)
        if high.iloc[i] < low.iloc[i - 1]:
            gap_top = low.iloc[i - 1]
            gap_bottom = high.iloc[i]
            if gap_top - gap_bottom >= min_gap_pips:
                filled = close.iloc[i + 1] > gap_bottom if i + 1 < len(close) else False
                fvg_list.append({
                    "type": "BEARISH_FVG",
                    "index": i,
                    "gap_high": gap_top,
                    "gap_low": gap_bottom,
                    "filled": filled,
                })

    return fvg_list
