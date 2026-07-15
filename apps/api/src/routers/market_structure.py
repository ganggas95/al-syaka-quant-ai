"""API router for market structure analysis."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
import pandas as pd

from src.market_structure import (
    MarketStructureDetector,
    detect_fvg,
    detect_liquidity_sweep,
    SupportResistanceDetector,
)
from src.collectors.manager import DataCollector

router = APIRouter(prefix="/api/v1/market-structure", tags=["market-structure"])


@router.get("/{symbol}")
async def get_market_structure(
    symbol: str,
    timeframe: str = Query("H1"),
    limit: int = Query(200, le=1000),
):
    """Run full market structure analysis on a symbol."""
    try:
        collector = DataCollector()
        end = datetime.utcnow()
        start = end - timedelta(days=_tf_to_days(timeframe, limit))

        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        df = pd.DataFrame([{
            "timestamp": d.timestamp,
            "open": d.open,
            "high": d.high,
            "low": d.low,
            "close": d.close,
        } for d in data])

        # Market structure analysis
        detector = MarketStructureDetector(swing_lookback=5)
        structure = detector.analyze(df["high"], df["low"])

        # FVG detection
        fvg = detect_fvg(df["high"], df["low"], df["close"])

        # Liquidity sweeps
        sweeps = detect_liquidity_sweep(df["high"], df["low"], df["close"])

        # S/R levels
        sr_detector = SupportResistanceDetector()
        sr_levels = sr_detector.detect(df["high"], df["low"])

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "current_trend": structure["current_trend"],
            "swing_highs": structure["swing_highs"],
            "swing_lows": structure["swing_lows"],
            "break_of_structure": structure["break_of_structure"],
            "change_of_character": structure["change_of_character"],
            "fair_value_gaps": fvg,
            "liquidity_sweeps": sweeps,
            "support_resistance": sr_levels,
            "timestamps": df["timestamp"].dt.isoformat().tolist(),
            "ohlc": {
                "open": df["open"].tolist(),
                "high": df["high"].tolist(),
                "low": df["low"].tolist(),
                "close": df["close"].tolist(),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _tf_to_days(timeframe: str, limit: int) -> int:
    mapping = {"M1": 1, "M5": 1, "M15": 2, "M30": 3, "H1": 7, "H4": 30, "D1": limit}
    return mapping.get(timeframe.upper(), 30) * (limit // 100 + 1)
