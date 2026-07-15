"""Market Structure Detector — HH, HL, LH, LL, BOS, CHOCH."""

import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SwingPoint:
    index: int
    price: float
    type: str  # "high" or "low"
    label: Optional[str] = None  # HH, HL, LH, LL


class MarketStructureDetector:
    """Detects market structure swing points and patterns."""

    def __init__(self, swing_lookback: int = 5):
        self.swing_lookback = swing_lookback

    def find_swing_highs(self, high: pd.Series) -> List[SwingPoint]:
        """Find swing high points (local maxima)."""
        swings = []
        for i in range(self.swing_lookback, len(high) - self.swing_lookback):
            left = high.iloc[i - self.swing_lookback:i].max()
            right = high.iloc[i + 1:i + self.swing_lookback + 1].max()
            if high.iloc[i] > left and high.iloc[i] > right:
                swings.append(SwingPoint(i, high.iloc[i], "high"))
        return swings

    def find_swing_lows(self, low: pd.Series) -> List[SwingPoint]:
        """Find swing low points (local minima)."""
        swings = []
        for i in range(self.swing_lookback, len(low) - self.swing_lookback):
            left = low.iloc[i - self.swing_lookback:i].min()
            right = low.iloc[i + 1:i + self.swing_lookback + 1].min()
            if low.iloc[i] < left and low.iloc[i] < right:
                swings.append(SwingPoint(i, low.iloc[i], "low"))
        return swings

    def classify_swing_points(self, swing_highs: List[SwingPoint], swing_lows: List[SwingPoint]) -> tuple:
        """Classify swing points as HH/HL/LH/LL based on sequence."""
        # Classify highs
        for i in range(len(swing_highs)):
            if i == 0:
                swing_highs[i].label = "UNKNOWN"
            elif swing_highs[i].price > swing_highs[i - 1].price:
                swing_highs[i].label = "HH"  # Higher High
            else:
                swing_highs[i].label = "LH"  # Lower High

        # Classify lows
        for i in range(len(swing_lows)):
            if i == 0:
                swing_lows[i].label = "UNKNOWN"
            elif swing_lows[i].price > swing_lows[i - 1].price:
                swing_lows[i].label = "HL"  # Higher Low
            else:
                swing_lows[i].label = "LL"  # Lower Low

        return swing_highs, swing_lows

    def detect_bos(self, swing_highs: List[SwingPoint], swing_lows: List[SwingPoint]) -> List[dict]:
        """Detect Break of Structure (BOS)."""
        breaks = []
        for i in range(1, len(swing_highs)):
            if swing_highs[i].label == "HH" and swing_highs[i].price > swing_highs[i - 1].price:
                breaks.append({
                    "type": "BOS_HIGH",
                    "index": swing_highs[i].index,
                    "price": swing_highs[i].price,
                    "broken_level": swing_highs[i - 1].price,
                })
        for i in range(1, len(swing_lows)):
            if swing_lows[i].label == "LL" and swing_lows[i].price < swing_lows[i - 1].price:
                breaks.append({
                    "type": "BOS_LOW",
                    "index": swing_lows[i].index,
                    "price": swing_lows[i].price,
                    "broken_level": swing_lows[i - 1].price,
                })
        return breaks

    def detect_choch(self, swing_highs: List[SwingPoint], swing_lows: List[SwingPoint]) -> List[dict]:
        """Detect Change of Character (CHOCH)."""
        choch_signals = []
        for i in range(1, min(len(swing_highs), len(swing_lows))):
            # Uptrend → Downtrend: Last HH not broken, then breaks last HL
            if (swing_highs[i].label == "LH" and swing_lows[i].label == "LL"
                    and i >= 2 and swing_highs[i - 1].label == "HH"):
                choch_signals.append({
                    "type": "CHOCH_DOWN",
                    "index": swing_lows[i].index,
                    "price": swing_lows[i].price,
                })
            # Downtrend → Uptrend: Last LL not broken, then breaks last LH
            if (swing_lows[i].label == "HL" and swing_highs[i].label == "HH"
                    and i >= 2 and swing_lows[i - 1].label == "LL"):
                choch_signals.append({
                    "type": "CHOCH_UP",
                    "index": swing_highs[i].index,
                    "price": swing_highs[i].price,
                })
        return choch_signals

    def analyze(self, high: pd.Series, low: pd.Series) -> dict:
        """Run full market structure analysis."""
        swing_highs = self.find_swing_highs(high)
        swing_lows = self.find_swing_lows(low)
        swing_highs, swing_lows = self.classify_swing_points(swing_highs, swing_lows)
        bos = self.detect_bos(swing_highs, swing_lows)
        choch = self.detect_choch(swing_highs, swing_lows)

        return {
            "swing_highs": [{"index": s.index, "price": s.price, "label": s.label} for s in swing_highs],
            "swing_lows": [{"index": s.index, "price": s.price, "label": s.label} for s in swing_lows],
            "break_of_structure": bos,
            "change_of_character": choch,
            "current_trend": self._determine_trend(swing_highs, swing_lows),
        }

    def _determine_trend(self, swing_highs, swing_lows) -> str:
        """Determine current trend based on recent swing points."""
        recent_sh = [s for s in swing_highs if s.label in ("HH", "LH")][-3:]
        recent_sl = [s for s in swing_lows if s.label in ("HL", "LL")][-3:]

        if not recent_sh or not recent_sl:
            return "NEUTRAL"

        hh_count = sum(1 for s in recent_sh if s.label == "HH")
        hl_count = sum(1 for s in recent_sl if s.label == "HL")

        if hh_count >= 2 and hl_count >= 2:
            return "BULLISH"
        elif hh_count <= 1 and hl_count <= 1:
            return "BEARISH"
        return "NEUTRAL"
