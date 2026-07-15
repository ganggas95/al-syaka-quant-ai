"""Data collector manager — orchestrates all connectors with smart routing & fallback."""

from datetime import datetime
from typing import Optional

from al_syaka_common.config import settings

from .base import OHLCData
from .massive import MassiveConnector
from .polygon import PolygonConnector
from .yahoo import YahooFinanceConnector


class DataCollector:
    """Orchestrates data fetching with smart connector routing.

    Routing logic:
    - XAUUSD, XAGUSD → Polygon.io (spot price, accurate)
    - Other forex/crypto → Yahoo Finance (free, reliable)
    - Fallback: if primary fails, try secondary provider
    """

    def __init__(self):
        self.yahoo = YahooFinanceConnector()
        self.polygon = PolygonConnector(api_key=settings.polygon_api_key or "")
        self.massive = MassiveConnector(api_key=getattr(settings, "massive_api_key", None) or "")
        self.connectors = [self.yahoo, self.polygon, self.massive]

    async def fetch_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        provider: Optional[str] = None,
    ) -> list[OHLCData]:
        """Fetch OHLC data with smart connector routing and fallback."""
        start = start or datetime(2020, 1, 1)
        end = end or datetime.utcnow()

        # Determine primary provider
        if provider:
            connectors_to_try = [self._get_connector(provider)]
        else:
            connectors_to_try = self._get_preferred_connectors(symbol)

        errors = []
        for connector in connectors_to_try:
            try:
                return await connector.fetch_ohlc(symbol, timeframe, start, end)
            except Exception as e:
                errors.append(f"{connector.__class__.__name__}: {e}")
                continue

        raise ValueError(f"All data sources failed for {symbol}: {'; '.join(errors)}")

    def _get_preferred_connectors(self, symbol: str) -> list:
        """Get ordered list of connectors for a symbol (primary first)."""
        # NOTE: Polygon free tier only provides previous day close (T+1).
        # Yahoo Finance provides live data matching TradingView.
        # Massive can be used as an optional premium provider when configured.
        # Priority: Yahoo (live) → Polygon (fallback) → Massive (if configured)
        preferred = [self.yahoo, self.polygon]
        if getattr(settings, "massive_api_key", None):
            preferred.append(self.massive)
        return preferred

    def _get_connector(self, name: str):
        """Get connector by name."""
        if name == "yahoo":
            return self.yahoo
        elif name == "polygon":
            return self.polygon
        elif name == "massive":
            return self.massive
        raise ValueError(f"Unknown connector: {name}")

    async def check_all_connectors(self) -> dict:
        """Check health of all connectors."""
        results = {}
        for connector in self.connectors:
            name = connector.__class__.__name__
            try:
                healthy = await connector.health_check()
                results[name] = "healthy" if healthy else "unhealthy"
            except Exception as e:
                results[name] = f"error: {str(e)}"
        return results
