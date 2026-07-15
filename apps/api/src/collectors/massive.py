"""Massive API data connector for OHLC and market snapshots."""

from datetime import datetime, timezone
from typing import Optional

import httpx

from .base import BaseConnector, OHLCData


class MassiveConnector(BaseConnector):
    """Connector for Massive market data REST API.

    This implementation uses the documented aggregate-bars endpoint for OHLC data.
    It supports a configurable API key and can be used as an optional provider
    alongside Yahoo Finance and Polygon.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.massive.com"):
        self.api_key = (api_key or "").strip()
        self.base_url = base_url.rstrip("/")

    async def fetch_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[OHLCData]:
        if not self.api_key:
            raise ValueError("Massive API key is not configured")

        url, headers, params = self._build_request(symbol, timeframe, start, end)

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            payload = response.json()

        if payload.get("status") != "OK":
            raise ValueError(f"Massive API error: {payload.get('error', 'unknown')}")

        results = []
        for bar in payload.get("results", []):
            ts_ms = bar["t"]
            ts = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
            results.append(
                OHLCData(
                    symbol=symbol,
                    timeframe=timeframe,
                    timestamp=ts,
                    open=float(bar["o"]),
                    high=float(bar["h"]),
                    low=float(bar["l"]),
                    close=float(bar["c"]),
                    volume=int(bar.get("v", 0)),
                    spread=None,
                )
            )

        return results

    async def health_check(self) -> bool:
        try:
            url, headers, params = self._build_request("AAPL", "1d", datetime(2024, 1, 1), datetime(2024, 1, 2))
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                payload = response.json()
            return payload.get("status") == "OK"
        except Exception:
            return False

    def _build_request(self, symbol: str, timeframe: str, start: datetime, end: datetime):
        multiplier, timespan = self._timeframe_to_massive(timeframe)
        url = (
            f"{self.base_url}/v2/aggs/ticker/{symbol}/range/"
            f"{multiplier}/{timespan}/{start.strftime('%Y-%m-%d')}/{end.strftime('%Y-%m-%d')}"
        )
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        params = {"adjusted": "false", "sort": "asc", "limit": "5000"}
        if self.api_key:
            params["apiKey"] = self.api_key
        return url, headers, params

    @staticmethod
    def _timeframe_to_massive(timeframe: str) -> tuple[int, str]:
        mapping = {
            "1m": (1, "minute"),
            "5m": (5, "minute"),
            "15m": (15, "minute"),
            "30m": (30, "minute"),
            "1h": (1, "hour"),
            "4h": (4, "hour"),
            "1d": (1, "day"),
            "1wk": (1, "week"),
        }
        return mapping.get(timeframe, (1, "hour"))
