"""API router for signal endpoints — real-time signal generation & history."""

import json
from datetime import datetime, timedelta, timezone

import pandas as pd
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import Signal
from al_syaka_indicators import IndicatorCalculator
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.collectors.manager import DataCollector
from src.signal_service import SignalGenerator


def _safe_json_load(value: str | None) -> list:
    """Safely parse a JSON string, returning empty list on failure."""
    if not value or not isinstance(value, str) or not value.strip():
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []


router = APIRouter(prefix="/api/v1/signals", tags=["signals"])


async def _get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session


@router.get("/{symbol}")
async def get_signal(
    symbol: str,
    timeframe: str = Query("H1", description="M1, M5, M15, M30, H1, H4, D1"),
    account_balance: float = Query(10_000, description="Account balance for position sizing"),
    persist: bool = Query(True, description="Save signal to database"),
):
    """Generate a complete trading signal for a symbol."""
    try:
        collector = DataCollector()
        end = datetime.utcnow()
        days_map = {"M1": 1, "M5": 1, "M15": 2, "M30": 3, "H1": 7, "H4": 30, "D1": 200}
        days = days_map.get(timeframe.upper(), 7)
        start = end - timedelta(days=days)

        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")

        # Build OHLC dict
        df = pd.DataFrame([{
            "timestamp": d.timestamp, "open": d.open, "high": d.high,
            "low": d.low, "close": d.close, "volume": d.volume,
        } for d in data])

        ohlc = {
            "open": df["open"].tolist(),
            "high": df["high"].tolist(),
            "low": df["low"].tolist(),
            "close": df["close"].tolist(),
            "volume": df["volume"].tolist(),
        }

        # Compute indicators
        calc = IndicatorCalculator({
            "open": df["open"], "high": df["high"],
            "low": df["low"], "close": df["close"],
            "volume": df["volume"],
        })
        ind = calc.compute_all()
        indicators = {k: (v.fillna(0).tolist() if hasattr(v, 'tolist') else v) for k, v in ind.items()}

        # Market structure (simplified)
        from src.market_structure import (MarketStructureDetector,
                                          SupportResistanceDetector,
                                          detect_fvg, detect_liquidity_sweep)
        detector = MarketStructureDetector()
        structure = detector.analyze(df["high"], df["low"])
        sr = SupportResistanceDetector().detect(df["high"], df["low"])
        fvg_list = detect_fvg(df["high"], df["low"], df["close"])
        sweeps = detect_liquidity_sweep(df["high"], df["low"], df["close"])

        market_structure_data = {
            **structure,
            "fair_value_gaps": fvg_list,
            "liquidity_sweeps": sweeps,
            "support_resistance": sr,
        }

        # Generate signal
        generator = SignalGenerator(account_balance=account_balance)
        signal = generator.generate(
            symbol=symbol,
            timeframe=timeframe,
            ohlc=ohlc,
            indicators=indicators,
            market_structure=market_structure_data,
        )

        # Persist to database
        if persist:
            try:
                async with async_session_factory() as session:
                    db_signal = Signal(
                        symbol=signal.symbol,
                        timeframe=timeframe,
                        signal=signal.signal,
                        confidence=signal.confidence,
                        entry_price=signal.entry_price,
                        stop_loss=signal.stop_loss,
                        take_profit=signal.take_profit,
                        risk_reward=signal.risk_reward_ratio,
                        risk_level=signal.risk_level,
                        reasons=json.dumps(signal.reasons or []),
                        indicators_used=json.dumps(
                            signal.indicators_used or [],
                        ),
                        h1_signal=None,
                        h4_signal=None,
                        d1_signal=None,
                        created_at=datetime.now(timezone.utc),
                    )
                    session.add(db_signal)
                    await session.commit()
            except Exception:
                pass  # Non-critical — don't fail if DB write fails

        return {
            "symbol": signal.symbol,
            "timeframe": signal.timeframe,
            "timestamp": signal.timestamp.isoformat(),
            "signal": signal.signal,
            "confidence": signal.confidence,
            "entry": signal.entry_price,
            "stop_loss": signal.stop_loss,
            "take_profit": signal.take_profit,
            "risk_reward": signal.risk_reward_ratio,
            "lot_size": signal.lot_size,
            "risk_level": signal.risk_level,
            "trade_quality": signal.trade_quality,
            "reasons": signal.reasons,
            "indicators_used": signal.indicators_used,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{symbol}/history")
async def get_signal_history(
    symbol: str,
    timeframe: str = Query("H1"),
    limit: int = Query(50, ge=1, le=200),
):
    """Get historical signals for a symbol from database."""
    try:
        async with async_session_factory() as session:
            stmt = (
                select(Signal)
                .where(Signal.symbol == symbol)
                .order_by(desc(Signal.created_at))
                .limit(limit)
            )
            result = await session.execute(stmt)
            signals = result.scalars().all()

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(signals),
            "signals": [
                {
                    "id": s.id,
                    "signal": s.signal,
                    "confidence": s.confidence,
                    "entry_price": float(s.entry_price) if s.entry_price else None,
                    "stop_loss": float(s.stop_loss) if s.stop_loss else None,
                    "take_profit": float(s.take_profit) if s.take_profit else None,
                    "risk_reward": float(s.risk_reward) if s.risk_reward else None,
                    "risk_level": s.risk_level,
                    "reasons": _safe_json_load(s.reasons),
                    "indicators_used": _safe_json_load(s.indicators_used),
                    "outcome_result": s.outcome_result,
                    "outcome_profit": float(s.outcome_profit) if s.outcome_profit else None,
                    "created_at": s.created_at.isoformat() if s.created_at else None,
                }
                for s in signals
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_signals():
    return {
        "message": "Use /api/v1/signals/{symbol}?timeframe=H1 to get a signal",
        "examples": [
            "/api/v1/signals/EURUSD?timeframe=H1",
            "/api/v1/signals/GBPUSD?timeframe=M15",
        ],
    }
