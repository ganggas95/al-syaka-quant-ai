"""API router for technical indicators and feature engineering."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
import pandas as pd

from al_syaka_indicators import IndicatorCalculator
from al_syaka_features import FeaturePipeline

from src.collectors.manager import DataCollector

router = APIRouter(prefix="/api/v1/indicators", tags=["indicators"])


@router.get("/{symbol}")
async def get_indicators(
    symbol: str,
    timeframe: str = Query("H1", description="Timeframe: M1, M5, M15, M30, H1, H4, D1"),
    limit: int = Query(200, le=1000),
):
    """Compute all technical indicators for a symbol."""
    try:
        collector = DataCollector()
        end = datetime.utcnow()
        start = end - timedelta(days=_timeframe_to_days(timeframe, limit))

        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        # Convert to pandas
        df = pd.DataFrame([{
            "timestamp": d.timestamp,
            "open": d.open,
            "high": d.high,
            "low": d.low,
            "close": d.close,
            "volume": d.volume,
        } for d in data])

        # Compute indicators
        calc = IndicatorCalculator({
            "open": df["open"],
            "high": df["high"],
            "low": df["low"],
            "close": df["close"],
            "volume": df["volume"],
        })
        indicators = calc.compute_all()

        # Convert Series to lists for JSON response
        result = {}
        for name, series in indicators.items():
            if isinstance(series, pd.Series):
                result[name] = series.fillna(0).tolist()
            elif isinstance(series, dict):
                result[name] = {k: v.tolist() if isinstance(v, pd.Series) else v for k, v in series.items()}

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamps": df["timestamp"].dt.isoformat().tolist(),
            "ohlc": {
                "open": df["open"].tolist(),
                "high": df["high"].tolist(),
                "low": df["low"].tolist(),
                "close": df["close"].tolist(),
                "volume": df["volume"].tolist(),
            },
            "indicators": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{symbol}/features")
async def get_features(
    symbol: str,
    timeframe: str = Query("H1"),
    limit: int = Query(200, le=1000),
):
    """Compute feature engineering for a symbol."""
    try:
        collector = DataCollector()
        end = datetime.utcnow()
        start = end - timedelta(days=_timeframe_to_days(timeframe, limit))

        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        df = pd.DataFrame([{
            "timestamp": d.timestamp,
            "open": d.open,
            "high": d.high,
            "low": d.low,
            "close": d.close,
            "volume": d.volume,
        } for d in data])

        pipeline = FeaturePipeline()
        features = pipeline.compute(
            open=df["open"],
            high=df["high"],
            low=df["low"],
            close=df["close"],
            volume=df["volume"],
            timestamps=df["timestamp"],
        )

        result = {}
        for col in features.columns:
            result[col] = features[col].fillna(0).tolist()

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "timestamps": df["timestamp"].dt.isoformat().tolist(),
            "features": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _timeframe_to_days(timeframe: str, limit: int) -> int:
    """Estimate number of days needed to get `limit` candles of `timeframe`."""
    mapping = {
        "M1": 1, "M5": 1, "M15": 2, "M30": 3,
        "H1": 7, "H4": 30, "D1": limit,
    }
    return mapping.get(timeframe.upper(), 30) * (limit // 100 + 1)
