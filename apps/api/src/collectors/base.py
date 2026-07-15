"""Market Data Collector — Base connector interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OHLCData:
    """Standardized OHLC data point."""
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    spread: Optional[int] = None


class BaseConnector(ABC):
    """Abstract base class for all data connectors."""

    @abstractmethod
    async def fetch_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[OHLCData]:
        """Fetch OHLC data from provider."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the connector is operational."""
        ...
