"""Yahoo Finance data connector."""

from datetime import datetime
from typing import Optional
import yfinance as yf

from .base import BaseConnector, OHLCData


TIMEFRAME_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "30m": "30m",
    "1h": "60m",
    "4h": "60m",  # Yahoo doesn't have 4h directly
    "1d": "1d",
    "1wk": "1wk",
}


SYMBOL_MAP = {
    "XAUUSD": "GC=F",   # Gold Futures
    "XAGUSD": "SI=F",   # Silver Futures
    "US30": "^DJI",     # Dow Jones
    "NAS100": "^IXIC",  # Nasdaq
    "SPX500": "^GSPC",  # S&P 500
    "BTCUSD": "BTC-USD",
    "ETHUSD": "ETH-USD",
}


class YahooFinanceConnector(BaseConnector):
    """Connector for Yahoo Finance."""

    async def fetch_ohlc(
        self,
        symbol: str,
        timeframe: str,
        start: datetime,
        end: datetime,
    ) -> list[OHLCData]:
        # Map symbol to Yahoo Finance format
        if symbol in SYMBOL_MAP:
            yf_symbol = SYMBOL_MAP[symbol]
        elif len(symbol) == 6 and symbol.isalpha():
            yf_symbol = f"{symbol}=X"  # Forex: EURUSD -> EURUSD=X
        else:
            yf_symbol = symbol

        ticker = yf.Ticker(yf_symbol)
        yf_tf = TIMEFRAME_MAP.get(timeframe, "1h")

        # Yahoo Finance has a bug with start/end dates for futures (GC=F, SI=F):
        # they don't return today's data. Use period parameter whenever possible.
        days_needed = (end - start).days
        if days_needed <= 30:
            period_map = {"1m": "1d", "5m": "1d", "15m": "5d", "30m": "5d",
                          "1h": "5d", "4h": "1mo", "1d": "3mo", "1wk": "3mo"}
            period = period_map.get(timeframe, "5d")
            df = ticker.history(period=period, interval=yf_tf)
        else:
            df = ticker.history(
                interval=yf_tf,
                start=start.strftime("%Y-%m-%d"),
                end=end.strftime("%Y-%m-%d"),
            )

        results = []
        for idx, row in df.iterrows():
            results.append(OHLCData(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=idx.to_pydatetime(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=int(row["Volume"]),
            ))
        return results

    async def health_check(self) -> bool:
        try:
            ticker = yf.Ticker("EURUSD=X")
            df = ticker.history(period="1d", interval="1m")
            return not df.empty
        except Exception:
            return False
