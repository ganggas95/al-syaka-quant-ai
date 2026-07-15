"""API router for Paper Trading — virtual trading, journal, analytics."""

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime

from src.paper_trading import (
    VirtualAccount,
    PositionManager,
    TradeJournal,
    PerformanceAnalytics,
    SignalTracker,
)

router = APIRouter(prefix="/api/v1/paper-trading", tags=["paper-trading"])

# Global state (in-memory for now, persists during server uptime)
account = VirtualAccount(initial_balance=10_000)
position_mgr = PositionManager()
journal = TradeJournal()
signal_tracker = SignalTracker()


@router.get("/account")
async def get_account():
    """Get virtual account summary."""
    return {
        **account.summary(),
        "open_pnl": position_mgr.get_open_pnl(),
        "realized_pnl": position_mgr.get_total_realized_pnl(),
    }


@router.post("/positions/open")
async def open_position(
    symbol: str = Query(...),
    direction: str = Query(..., pattern="^(LONG|SHORT)$"),
    entry_price: float = Query(...),
    stop_loss: float = Query(...),
    take_profit: float = Query(...),
    lot_size: float = Query(0.01),
    signal: str = Query("BUY"),
    confidence: float = Query(0.0),
    reasons: str = Query(""),
    tags: str = Query(""),
):
    """Open a new paper trading position."""
    pos = position_mgr.open_position(
        symbol=symbol.upper(),
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        lot_size=lot_size,
    )

    # Record in journal
    j_entry = journal.add_entry(
        position_id=pos.id,
        symbol=pos.symbol,
        direction=pos.direction,
        entry_price=pos.entry_price,
        lot_size=pos.lot_size,
        signal=signal,
        confidence=confidence,
        reasons=reasons.split(";") if reasons else [],
        tags=tags.split(",") if tags else [],
    )

    # Record signal
    sig = signal_tracker.record_signal(
        symbol=pos.symbol,
        signal=signal,
        confidence=confidence,
        reasons=j_entry.reasons,
    )

    account.record_snapshot(
        equity=account.balance + position_mgr.get_open_pnl(),
        open_positions=len(position_mgr.open_positions),
    )

    return {
        "position_id": pos.id,
        "journal_id": j_entry.id,
        "signal_id": sig.signal_id,
        "symbol": pos.symbol,
        "direction": pos.direction,
        "entry_price": pos.entry_price,
        "stop_loss": pos.stop_loss,
        "take_profit": pos.take_profit,
        "lot_size": pos.lot_size,
        "entry_time": pos.entry_time.isoformat(),
    }


@router.post("/positions/close")
async def close_position(
    position_id: str = Query(...),
    exit_price: float = Query(...),
    exit_reason: str = Query("MANUAL_CLOSE"),
    notes: str = Query(""),
):
    """Close an open position."""
    pos = position_mgr.close_position(position_id, exit_price, exit_reason)
    if not pos:
        raise HTTPException(status_code=404, detail=f"Position {position_id} not found")

    # Update account
    account.apply_trade_result(pos.profit)

    # Update journal
    journal.close_entry(position_id, exit_price, exit_reason, notes)

    # Resolve signal
    if pos.signal_id:
        signal_tracker.resolve_signal(pos.signal_id, pos.profit)

    account.record_snapshot(
        equity=account.balance + position_mgr.get_open_pnl(),
        open_positions=len(position_mgr.open_positions),
    )

    return {
        "position_id": pos.id,
        "profit": pos.profit,
        "profit_pips": pos.profit_pips,
        "exit_reason": pos.exit_reason,
        "new_balance": account.balance,
    }


@router.post("/positions/update-prices")
async def update_prices():
    """Update all open positions with current market data (simplified)."""
    # In production, this would fetch real prices
    return {"open_positions": len(position_mgr.open_positions)}


@router.get("/positions")
async def list_positions(include_closed: bool = Query(False)):
    """List all positions."""
    return position_mgr.summary()


@router.get("/journal")
async def get_journal(limit: int = Query(20)):
    """Get recent journal entries."""
    entries = journal.get_recent_entries(limit)
    return {
        "total_entries": len(journal.entries),
        "entries": [
            {
                "id": e.id,
                "symbol": e.symbol,
                "direction": e.direction,
                "signal": e.signal,
                "entry_price": e.entry_price,
                "exit_price": e.exit_price,
                "profit": e.profit,
                "result": e.result,
                "reasons": e.reasons,
                "tags": e.tags,
                "notes": e.notes,
                "entry_time": e.entry_time.isoformat() if e.entry_time else None,
                "exit_time": e.exit_time.isoformat() if e.exit_time else None,
            }
            for e in entries
        ],
    }


@router.get("/analytics")
async def get_analytics():
    """Get comprehensive performance analytics."""
    analytics = PerformanceAnalytics(journal.entries, account.equity_history)
    return {
        "overall": analytics.overall_stats(),
        "by_pair": analytics.win_rate_by_pair(),
        "by_session": analytics.win_rate_by_session(),
        "drawdown": analytics.drawdown_analysis(),
        "monthly_returns": analytics.monthly_returns(),
        "equity_curve": analytics.equity_curve(),
    }


@router.get("/signal-performance")
async def get_signal_performance():
    """Get signal tracking performance (confusion matrix)."""
    return signal_tracker.summary()


@router.post("/reset")
async def reset_account(initial_balance: float = Query(10_000)):
    """Reset the paper trading account."""
    global account, position_mgr, journal, signal_tracker
    account = VirtualAccount(initial_balance=initial_balance)
    position_mgr = PositionManager()
    journal = TradeJournal()
    signal_tracker = SignalTracker()
    return {"status": "reset", "initial_balance": initial_balance}
