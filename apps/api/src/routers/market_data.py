"""API router for market data endpoints."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select

from src.collectors.manager import DataCollector
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import Symbol

router = APIRouter(prefix="/api/v1/market", tags=["market-data"])

collector = DataCollector()


@router.get("/symbols")
async def list_symbols(active_only: bool = Query(True)):
    """List all available trading symbols."""
    async with async_session_factory() as session:
        query = select(Symbol)
        if active_only:
            query = query.where(Symbol.is_active == True)
        query = query.order_by(Symbol.name)
        result = await session.execute(query)
        symbols = result.scalars().all()
        return {
            "count": len(symbols),
            "symbols": [
                {
                    "id": s.id,
                    "name": s.name,
                    "base": s.base_currency,
                    "quote": s.quote_currency,
                    "pip_size": float(s.pip_size),
                    "contract_size": s.contract_size,
                    "active": s.is_active,
                }
                for s in symbols
            ],
        }


@router.get("/ticker")
async def get_ticker():
    """Get current prices for all active symbols."""
    async with async_session_factory() as session:
        result = await session.execute(
            select(Symbol).where(Symbol.is_active == True)
        )
        symbols = result.scalars().all()

    ticker_data = []
    for sym in symbols:
        try:
            data = await collector.fetch_ohlc(sym.name, "H1", 
                datetime.utcnow() - timedelta(hours=2), datetime.utcnow())
            if data:
                last = data[-1]
                prev = data[-2] if len(data) > 1 else last
                change = ((last.close - prev.close) / prev.close * 100) if prev.close else 0
                ticker_data.append({
                    "symbol": sym.name,
                    "bid": float(last.close),
                    "ask": float(last.close),
                    "high": float(last.high),
                    "low": float(last.low),
                    "change": round(float(change), 2),
                    "volume": int(last.volume),
                })
        except Exception:
            pass

    return {"tickers": ticker_data, "count": len(ticker_data)}


@router.get("/health")
async def collector_health():
    """Check health of all data connectors."""
    return await collector.check_all_connectors()


@router.get("/ohlc/{symbol}")
async def get_ohlc(
    symbol: str,
    timeframe: str = Query("H1", description="M1, M5, M15, M30, H1, H4, D1"),
    limit: int = Query(100, le=1000),
):
    """Fetch OHLC data for a symbol."""
    end = datetime.utcnow()
    days_map = {"M1": 1, "M5": 1, "M15": 2, "M30": 3, "H1": 7, "H4": 30, "D1": limit * 2}
    days = days_map.get(timeframe.upper(), 30)
    start = end - timedelta(days=days)

    try:
        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(data),
            "data": [
                {
                    "timestamp": d.timestamp.isoformat(),
                    "open": d.open,
                    "high": d.high,
                    "low": d.low,
                    "close": d.close,
                    "volume": d.volume,
                }
                for d in data
            ],
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
