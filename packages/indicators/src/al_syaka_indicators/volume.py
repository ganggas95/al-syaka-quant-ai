"""Volume indicators: Volume Profile, VWAP, OBV."""

import pandas as pd
import numpy as np


def vwap(high: pd.Series, low: pd.Series, close: pd.Series, volume: pd.Series) -> pd.Series:
    """Volume Weighted Average Price (intraday)."""
    typical_price = (high + low + close) / 3
    return (typical_price * volume).cumsum() / volume.cumsum()


def volume_profile(
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    num_bins: int = 12,
) -> dict:
    """Volume Profile — distribusi volume berdasarkan level harga."""
    price_range = pd.concat([high, low], axis=1).max(axis=1) - pd.concat([high, low], axis=1).min(axis=1)
    bin_size = price_range.mean() / num_bins if price_range.mean() > 0 else price_range.max() / num_bins

    all_prices = pd.concat([high, low], axis=1).values.flatten()
    price_min = all_prices.min()
    price_max = all_prices.max()
    bins = np.linspace(price_min, price_max, num_bins + 1)

    volume_by_price = pd.DataFrame(index=range(num_bins), columns=["price_level", "volume"])
    volume_by_price["price_level"] = (bins[:-1] + bins[1:]) / 2
    volume_by_price["volume"] = 0

    for i in range(len(high)):
        for j in range(num_bins):
            if low.iloc[i] <= volume_by_price["price_level"].iloc[j] <= high.iloc[i]:
                volume_by_price["volume"].iloc[j] += volume.iloc[i]

    poc_idx = volume_by_price["volume"].idxmax()
    return {
        "volume_by_price": volume_by_price,
        "point_of_control": volume_by_price["price_level"].iloc[poc_idx],
        "value_area_high": volume_by_price.loc[volume_by_price["volume"] >= volume_by_price["volume"].quantile(0.3), "price_level"].max(),
        "value_area_low": volume_by_price.loc[volume_by_price["volume"] >= volume_by_price["volume"].quantile(0.3), "price_level"].min(),
    }


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume."""
    direction = np.sign(close.diff()).fillna(0)
    return (direction * volume).cumsum()
