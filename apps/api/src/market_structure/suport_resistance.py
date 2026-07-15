"""Support & Resistance level detection."""

import pandas as pd
import numpy as np
from typing import List


class SupportResistanceDetector:
    """Detect horizontal support and resistance levels."""

    def __init__(self, n_clusters: int = 10, min_touches: int = 2):
        self.n_clusters = n_clusters
        self.min_touches = min_touches

    def detect(self, high: pd.Series, low: pd.Series, lookback: int = 100) -> dict:
        """Detect S/R levels using density-based clustering on swing points."""
        recent_high = high.iloc[-lookback:]
        recent_low = low.iloc[-lookback:]

        # Find swing points for clustering
        swing_highs = []
        swing_lows = []

        for i in range(2, len(recent_high) - 2):
            if (recent_high.iloc[i] > recent_high.iloc[i - 1]
                    and recent_high.iloc[i] > recent_high.iloc[i - 2]
                    and recent_high.iloc[i] > recent_high.iloc[i + 1]
                    and recent_high.iloc[i] > recent_high.iloc[i + 2]):
                swing_highs.append(recent_high.iloc[i])

            if (recent_low.iloc[i] < recent_low.iloc[i - 1]
                    and recent_low.iloc[i] < recent_low.iloc[i - 2]
                    and recent_low.iloc[i] < recent_low.iloc[i + 1]
                    and recent_low.iloc[i] < recent_low.iloc[i + 2]):
                swing_lows.append(recent_low.iloc[i])

        # Simple clustering: round to nearest price level and count touches
        all_points = np.array(swing_highs + swing_lows)
        if len(all_points) == 0:
            return {"resistances": [], "supports": []}

        price_range = all_points.max() - all_points.min()
        bin_size = price_range / self.n_clusters if price_range > 0 else 0.0001

        bins = np.arange(all_points.min(), all_points.max() + bin_size, bin_size)
        digitized = np.digitize(all_points, bins)

        unique, counts = np.unique(digitized, return_counts=True)
        levels = []
        for u, c in zip(unique, counts):
            if c >= self.min_touches and u < len(bins):
                level_price = bins[u - 1] + bin_size / 2
                levels.append({"price": level_price, "touches": int(c)})

        # Classify as resistance (swing highs) or support (swing lows)
        resistances = []
        supports = []
        for level in levels:
            if any(abs(level["price"] - sh) < bin_size for sh in swing_highs):
                resistances.append(level)
            if any(abs(level["price"] - sl) < bin_size for sl in swing_lows):
                supports.append(level)

        return {
            "resistances": sorted(resistances, key=lambda x: x["price"], reverse=True)[:5],
            "supports": sorted(supports, key=lambda x: x["price"])[:5],
        }
