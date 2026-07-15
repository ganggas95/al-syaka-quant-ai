"""API router for MT5 Bridge — connection, orders, auto trading, safety."""

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime

from al_syaka_mt5 import (
    MT5SimulationConnector, OrderManager, AutoTradingEngine, SafetySystem,
    OrderRequest,
)

router = APIRouter(prefix="/api/v1/mt5", tags=["mt5"])

# Global state
connector = MT5SimulationConnector()
safety = SafetySystem(initial_balance=10_000)
order_mgr = OrderManager(connector)
auto_trader = AutoTradingEngine(connector, order_mgr, safety)

connector.initialize(login=123456, server="ICMarkets-Demo", password="demo")


@router.post("/connect")
async def connect(
    login: int = Query(123456),
    server: str = Query("ICMarkets-Demo"),
    password: str = Query("demo"),
):
    """Connect to MT5 (simulation mode on macOS)."""
    success = connector.initialize(login, server, password)
    return {"connected": success, "mode": "simulation"}


@router.post("/disconnect")
async def disconnect():
    """Disconnect from MT5."""
    connector.shutdown()
    return {"connected": False}


@router.get("/account")
async def get_account():
    """Get MT5 account info."""
    info = connector.get_account_info()
    if not info:
        raise HTTPException(503, "Not connected")
    return {
        "login": info.login,
        "server": info.server,
        "balance": info.balance,
        "equity": info.equity,
        "margin": info.margin,
        "margin_free": info.margin_free,
        "margin_level": info.margin_level,
        "currency": info.currency,
        "leverage": info.leverage,
        "connected": info.connected,
    }


@router.get("/positions")
async def get_positions():
    """Get all open positions."""
    return order_mgr.get_open_positions()


@router.post("/orders/place")
async def place_order(
    symbol: str = Query("EURUSD"),
    order_type: str = Query("BUY", pattern="^(BUY|SELL)$"),
    volume: float = Query(0.1),
    price: float = Query(0.0),
    sl: float = Query(0.0),
    tp: float = Query(0.0),
    signal_id: str = Query(""),
):
    """Place an order with validation."""
    request = OrderRequest(
        symbol=symbol.upper(),
        order_type=order_type,
        volume=volume,
        price=price,
        sl=sl,
        tp=tp,
        signal_id=signal_id or None,
    )
    result = order_mgr.execute_order(request)
    return {
        "ticket": result.ticket,
        "status": result.status,
        "price": result.price,
        "filled_volume": result.filled_volume,
        "error": result.error_message or None,
    }


@router.post("/positions/close/{ticket}")
async def close_position(ticket: int):
    """Close a position by ticket."""
    success = order_mgr.close_position_safely(ticket)
    return {"closed": success}


@router.post("/auto/start")
async def start_auto_trading():
    """Start auto trading engine."""
    auto_trader.config.enabled = True
    auto_trader.start()
    return {"auto_trading": True}


@router.post("/auto/stop")
async def stop_auto_trading():
    """Stop auto trading engine."""
    auto_trader.config.enabled = False
    auto_trader.stop()
    return {"auto_trading": False}


@router.get("/auto/status")
async def auto_trading_status():
    """Get auto trading status."""
    return {
        "enabled": auto_trader.config.enabled,
        "running": auto_trader.is_running(),
        "daily_trades": auto_trader.daily_trades,
        "max_daily": auto_trader.config.max_daily_trades,
        "min_confidence": auto_trader.config.min_confidence,
        "allowed_symbols": auto_trader.config.allowed_symbols,
    }


@router.get("/safety")
async def safety_status():
    """Get safety system status."""
    return safety.get_status()


@router.post("/safety/kill-switch")
async def engage_kill_switch(engage: bool = Query(True)):
    """Engage or disengage kill switch."""
    if engage:
        safety.engage_kill_switch()
        auto_trader.stop()
    else:
        safety.disengage_kill_switch()
    return {"kill_switch": safety.config.kill_switch_engaged}


@router.post("/signal/execute")
async def execute_signal(
    symbol: str = Query("EURUSD"),
    signal: str = Query("BUY"),
    confidence: float = Query(75.0),
    entry: float = Query(0.0),
    stop_loss: float = Query(0.0),
    take_profit: float = Query(0.0),
):
    """Execute a trading signal through the auto trader."""
    signal_data = {
        "symbol": symbol.upper(),
        "signal": signal,
        "confidence": confidence,
        "entry": entry,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
    }
    result = auto_trader.process_signal(signal_data)
    return result


@router.get("/executed-signals")
async def executed_signals():
    """Get history of executed signals."""
    return {"signals": auto_trader.executed_signals[-20:]}
