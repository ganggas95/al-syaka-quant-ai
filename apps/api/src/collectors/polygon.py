"""Polygon.io data connector — Forex, Crypto, and Metals (spot XAUUSD, XAGUSD)."""

from datetime import datetime, timezone
from typing import Optional
import httpx

from .base import BaseConnector, OHLCData


# Polygon ticker mapping
TICKER_MAP = {
    "XAUUSD": "C:XAUUSD",
    "XAGUSD": "C:XAGUSD",
    "BTCUSD": "X:BTCUSD",
    "ETHUSD": "X:ETHUSD",
}

# Polygon only supports these resolutions
TIMEFRAME_MAP = {
    "1m": {"multiplier": 1, "timespan": "minute"},
    "5m": {"multiplier": 5, "timespan": "minute"},
    "15m": {"multiplier": 15, "timespan": "minute"},
    "30m": {"multiplier": 30, "timespan": "minute"},
    "1h": {"multiplier": 1, "timespan": "hour"},
    "4h": {"multiplier": 4, "timespan": "hour"},
    "1d": {"multiplier": 1, "timespan": "day"},
}


class PolygonConnector(BaseConnector):
    """Connector for Polygon.io — accurate spot prices for forex, metals, crypto."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.polygon.io"
        self._request_count = 0
        self._last_reset = datetime.utcnow()

    async def fetch_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[OHLCData]:
        ticker = TICKER_MAP.get(symbol, f"C:{symbol}")
        tf = TIMEFRAME_MAP.get(timeframe, {"multiplier": 1, "timespan": "hour"})

        # Rate limit: free tier = 5 calls/min
        self._check_rate_limit()

        url = (
            f"{self.base_url}/v2/aggs/ticker/{ticker}/range"
            f"/{tf['multiplier']}/{tf['timespan']}"
            f"/{start.strftime('%Y-%m-%d')}"
            f"/{end.strftime('%Y-%m-%d')}"
            f"?adjusted=true&sort=asc&limit=5000&apiKey={self.api_key}"
        )

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url)
            self._request_count += 1
            data = resp.json()

        if data.get("status") != "OK":
            raise ValueError(f"Polygon API error: {data.get('error', 'unknown')}")

        results = []
        for bar in data.get("results", []):
            ts_ms = bar["t"]  # Unix timestamp in milliseconds
            ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)

            results.append(OHLCData(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=ts,
                open=float(bar["o"]),
                high=float(bar["h"]),
                low=float(bar["l"]),
                close=float(bar["c"]),
                volume=int(bar.get("v", 0)),
                spread=None,
            ))

        return results

    async def health_check(self) -> bool:
        """Check if Polygon API is reachable."""
        try:
            url = f"{self.base_url}/v2/aggs/ticker/C:EURUSD/prev?adjusted=true&apiKey={self.api_key}"
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(url)
                data = resp.json()
            return data.get("status") == "OK"
        except Exception:
            return False

    def _check_rate_limit(self):
        """Simple rate limiter: max 4 calls/min (free tier = 5)."""
        now = datetime.utcnow()
        if (now - self._last_reset).seconds >= 60:
            self._request_count = 0
            self._last_reset = now
        if self._request_count >= 4:
            import time
            time.sleep(5)  # Short pause before next call

    @staticmethod
    def handles_symbol(symbol: str) -> bool:
        """Check if this connector should handle the symbol."""
        return symbol in TICKER_MAP or symbol in ("XAUUSD", "XAGUSD")
