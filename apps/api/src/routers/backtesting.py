"""API router for backtesting operations."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

import pandas as pd
from al_syaka_backtester import (BacktestConfig, BacktestEngine,
                                 BacktestOptimizer)
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from src.collectors.manager import DataCollector

router = APIRouter(prefix="/api/v1/backtesting", tags=["backtesting"])


async def _fetch_ohlc_data(symbol: str, timeframe: str, days: int):
    """Fetch and prepare OHLC data."""
    collector = DataCollector()
    end = datetime.utcnow()
    start = end - timedelta(days=days)
    data = await collector.fetch_ohlc(symbol, timeframe, start, end)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    df = pd.DataFrame([{
        "timestamp": d.timestamp, "open": d.open, "high": d.high,
        "low": d.low, "close": d.close, "volume": d.volume,
    } for d in data])
    return df, start, end


def _build_response(engine, metrics, symbol, timeframe, days, initial_balance, risk_percent):
    """Build final JSON response from backtest results."""
    monthly_returns = {}
    if metrics.monthly_returns:
        monthly_returns = {k: round(v, 2) for k, v in sorted(metrics.monthly_returns.items())}

    equity_curve = []
    curve_len = len(engine.equity_curve)
    step = max(1, curve_len // 500)
    for i in range(0, curve_len, step):
        pt = engine.equity_curve[i]
        equity_curve.append({
            "timestamp": pt["timestamp"].isoformat() if hasattr(pt["timestamp"], "isoformat") else str(pt["timestamp"]),
            "equity": round(pt["equity"], 2),
        })

    return {
        "config": {
            "symbol": symbol,
            "timeframe": timeframe,
            "period_days": days,
            "initial_balance": initial_balance,
            "risk_percent": risk_percent,
        },
        "metrics": {
            "total_trades": metrics.total_trades,
            "winning_trades": metrics.winning_trades,
            "losing_trades": metrics.losing_trades,
            "win_rate": round(metrics.win_rate * 100, 2),
            "net_profit": round(metrics.net_profit, 2),
            "profit_factor": round(metrics.profit_factor, 2),
            "avg_profit_per_trade": round(metrics.avg_profit_per_trade, 2),
            "avg_win": round(metrics.avg_win, 2),
            "avg_loss": round(metrics.avg_loss, 2),
            "max_drawdown": round(metrics.max_drawdown, 2),
            "max_drawdown_percent": round(metrics.max_drawdown_percent, 2),
            "sharpe_ratio": round(metrics.sharpe_ratio, 2),
            "sortino_ratio": round(metrics.sortino_ratio, 2),
            "calmar_ratio": round(metrics.calmar_ratio, 2),
            "max_consecutive_wins": metrics.max_consecutive_wins,
            "max_consecutive_losses": metrics.max_consecutive_losses,
            "best_trade": round(metrics.best_trade, 2),
            "worst_trade": round(metrics.worst_trade, 2),
        },
        "summary": _generate_summary(metrics),
        "equity_curve": equity_curve,
        "monthly_returns": monthly_returns,
        "regime_stats": {
            "current_regime": engine.regime_history[-1]["regime"] if engine.regime_history else "UNKNOWN",
            "total_registered": len(engine.regime_history),
        },
        "risk_metrics": {
            "max_daily_loss_hit": engine.daily_pnl <= -engine.config.max_daily_loss if engine.daily_pnl else False,
            "consecutive_losses": engine.consecutive_losses,
            "consecutive_loss_triggered": engine.consecutive_losses >= engine.config.max_consecutive_losses,
        },
        "session_breakdown": _calc_session_breakdown(engine.trades),
        "trade_attribution": _calc_trade_attribution(engine.trades),
        "trades": [
            {
                "entry_time": t.entry_time.isoformat(),
                "exit_time": t.exit_time.isoformat() if t.exit_time else None,
                "signal": t.signal,
                "direction": t.direction,
                "entry": t.entry_price,
                "exit": t.exit_price,
                "sl": t.stop_loss,
                "tp": t.take_profit,
                "result": t.result,
                "pips": t.pips,
                "profit": t.profit,
                "exit_reason": t.exit_reason,
            }
            for t in engine.trades[-50:]
        ],
    }


async def _backtest_generator(
    symbol: str, timeframe: str, days: int,
    initial_balance: float, risk_percent: float,
) -> AsyncGenerator[str, None]:
    """Generator that yields SSE events for progress + final result."""
    try:
        df, start, end = await _fetch_ohlc_data(symbol, timeframe, days)
        config = BacktestConfig(
            symbol=symbol, timeframe=timeframe,
            start_date=start, end_date=end,
            initial_balance=initial_balance,
            risk_per_trade=risk_percent / 100,
        )
        engine = BacktestEngine(config)
        queue: asyncio.Queue[int] = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def on_progress(current_step: int, total_steps: int):
            pct = int((current_step / total_steps) * 100)
            pct = min(pct, 99)
            loop.call_soon_threadsafe(queue.put_nowait, pct)

        # Run engine in a thread to avoid blocking the event loop
        task = loop.run_in_executor(None, lambda: engine.run(df, progress_callback=on_progress))

        # Stream progress events while engine runs in background
        last_pct = -1
        while not task.done():
            try:
                pct = await asyncio.wait_for(queue.get(), timeout=0.3)
                if pct != last_pct:
                    yield f"data: {json.dumps({'type': 'progress', 'percent': pct})}\n\n"
                    last_pct = pct
            except asyncio.TimeoutError:
                continue

        metrics = await task
        result = _build_response(engine, metrics, symbol, timeframe, days, initial_balance, risk_percent)

        yield f"data: {json.dumps({'type': 'progress', 'percent': 100})}\n\n"
        yield f"data: {json.dumps({'type': 'complete', 'result': result})}\n\n"

    except HTTPException as e:
        yield f"data: {json.dumps({'type': 'error', 'detail': e.detail})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'detail': str(e)})}\n\n"


@router.post("/run-stream")
async def run_backtest_stream(
    symbol: str = Query("EURUSD"),
    timeframe: str = Query("H1"),
    days: int = Query(365, le=1825),
    initial_balance: float = Query(10_000),
    risk_percent: float = Query(1.0, le=5.0),
):
    """Run backtest with SSE progress streaming."""
    return StreamingResponse(
        _backtest_generator(symbol, timeframe, days, initial_balance, risk_percent),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/run")
async def run_backtest(
    symbol: str = Query("EURUSD"),
    timeframe: str = Query("H1"),
    days: int = Query(365, le=1825, description="Days of historical data (max 5 years)"),
    initial_balance: float = Query(10_000),
    risk_percent: float = Query(1.0, le=5.0),
):
    """Run a backtest on historical data (sync)."""
    try:
        df, start, end = await _fetch_ohlc_data(symbol, timeframe, days)

        config = BacktestConfig(
            symbol=symbol,
            timeframe=timeframe,
            start_date=start,
            end_date=end,
            initial_balance=initial_balance,
            risk_per_trade=risk_percent / 100,
        )

        engine = BacktestEngine(config)
        metrics = engine.run(df)

        return _build_response(engine, metrics, symbol, timeframe, days, initial_balance, risk_percent)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _generate_summary(metrics) -> str:
    """Generate a human-readable backtest summary."""
    parts = [
        f"📊 Backtest completed: {metrics.total_trades} trades",
        f"✅ Win Rate: {metrics.win_rate * 100:.1f}%",
        f"💰 Net Profit: ${metrics.net_profit:,.2f}",
    ]
    if metrics.profit_factor != float('inf'):
        parts.append(f"📈 Profit Factor: {metrics.profit_factor:.2f}")
    parts.append(f"📉 Max Drawdown: {metrics.max_drawdown_percent:.1f}%")
    parts.append(f"⚡ Sharpe: {metrics.sharpe_ratio:.2f}")
    parts.append(f"🏆 Best Trade: ${metrics.best_trade:.2f}")
    parts.append(f"💀 Worst Trade: ${metrics.worst_trade:.2f}")
    return " | ".join(parts)


def _calc_session_breakdown(trades: list) -> dict:
    """Calculate performance breakdown by trading session."""
    sessions = {"ASIA": [], "LONDON": [], "NEWYORK": []}
    for t in trades:
        if t.result in ("WIN", "LOSS") and t.session in sessions:
            sessions[t.session].append(t)

    breakdown = {}
    for name, st in sessions.items():
        total = len(st)
        if total == 0:
            breakdown[name.lower()] = {"trades": 0}
            continue
        wins = sum(1 for t in st if t.result == "WIN")
        profit = sum(t.profit for t in st)
        avg = profit / total
        breakdown[name.lower()] = {
            "trades": total,
            "wins": wins,
            "losses": total - wins,
            "win_rate": round(wins / total * 100, 1),
            "net_profit": round(profit, 2),
            "avg_trade": round(avg, 2),
        }
    return breakdown


def _calc_trade_attribution(trades: list) -> dict:
    """Trade Attribution Analysis — breakdown by regime, strategy, exit_reason."""
    closed = [t for t in trades if t.result in ("WIN", "LOSS")]
    if not closed:
        return {
            "by_regime": {}, "by_strategy": {},
            "by_exit_reason": {}, "by_session": {},
        }

    def _group(attr: str) -> dict:
        groups = {}
        for t in closed:
            if attr == "strategy":
                key = str(t.reasons[0]) if t.reasons else "unknown"
            else:
                key = str(getattr(t, attr, "unknown") or "unknown")
            if key not in groups:
                groups[key] = {
                    "trades": 0, "wins": 0,
                    "losses": 0, "profits": [],
                }
            groups[key]["trades"] += 1
            if t.result == "WIN":
                groups[key]["wins"] += 1
            else:
                groups[key]["losses"] += 1
            groups[key]["profits"].append(t.profit)
        result = {}
        for k, v in groups.items():
            result[k] = {
                "trades": v["trades"],
                "win_rate": round(v["wins"] / v["trades"] * 100, 1)
                if v["trades"] else 0,
                "net_profit": round(sum(v["profits"]), 2),
                "avg_trade": round(sum(v["profits"]) / v["trades"], 2)
                if v["trades"] else 0,
            }
        return result

    return {
        "by_regime": _group("regime"),
        "by_strategy": _group("strategy"),
        "by_exit_reason": _group("exit_reason"),
        "by_session": _group("session"),
    }


@router.post("/optimize")
async def optimize_backtest(
    symbol: str = Query("EURUSD"),
    timeframe: str = Query("H1"),
    days: int = Query(365, le=1825),
    initial_balance: float = Query(10_000),
    risk_percent: float = Query(1.0, le=5.0),
    optimization_type: str = Query(
        "rr", pattern="^(rr|atr_sl|confidence|all)$"
    ),
    top_n: int = Query(15, le=50),
):
    """Run parameter optimization (grid search) for backtest strategy."""
    try:
        df, start, end = await _fetch_ohlc_data(symbol, timeframe, days)
        base_config = BacktestConfig(
            symbol=symbol, timeframe=timeframe,
            start_date=start, end_date=end,
            initial_balance=initial_balance,
            risk_per_trade=risk_percent / 100,
        )

        def _fetch():
            return df

        optimizer = BacktestOptimizer(_fetch, base_config)

        opt_map = {
            "rr": optimizer.optimize_rr,
            "atr_sl": optimizer.optimize_atr_sl,
            "confidence": optimizer.optimize_confidence,
            "all": optimizer.optimize_all_params,
        }
        runner = opt_map.get(optimization_type, optimizer.optimize_rr)
        results = runner()

        return {
            "config": {
                "symbol": symbol,
                "timeframe": timeframe,
                "period_days": days,
                "initial_balance": initial_balance,
                "optimization_type": optimization_type,
            },
            "summary": optimizer.summary_table(top_n),
            "best": _serialize_best(optimizer.best_result()),
            "results": [
                _serialize_opt_result(r) for r in results[:top_n]
            ],
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _serialize_opt_result(r) -> dict:
    """Serialize optimization result to JSON-safe dict."""
    pf = r.profit_factor
    return {
        "params": r.params,
        "total_trades": r.total_trades,
        "profit_factor": round(pf, 4) if pf != float('inf') else None,
        "win_rate": r.win_rate,
        "net_profit": r.net_profit,
        "max_drawdown_pct": r.max_drawdown_pct,
        "sharpe_ratio": r.sharpe_ratio,
        "expectancy": r.expectancy,
    }


def _serialize_best(r) -> Optional[dict]:
    """Serialize best result to JSON."""
    if r is None:
        return None
    return _serialize_opt_result(r)
