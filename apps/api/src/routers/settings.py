"""API router for Settings — platform configuration & system management."""

from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from sqlalchemy import text
from sqlalchemy import inspect

from al_syaka_common.database import async_session_factory

router = APIRouter(prefix="/api/v1/settings", tags=["settings"])

# In-memory settings store (in production, use DB or Redis)
_settings_store: dict = {
    "api_keys": {
        "polygon": "",
        "alpha_vantage": "",
        "massive": "",
        "mt5_account": "",
        "mt5_password": "",
        "mt5_server": "",
    },
    "preferences": {
        "default_symbol": "EURUSD",
        "default_timeframe": "H1",
        "account_balance": 10_000,
        "theme": "dark",
    },
    "risk": {
        "default_risk_percent": 1.0,
        "max_position_size": 1.0,
        "max_drawdown_percent": 10.0,
        "max_daily_loss": 500.0,
    },
    "data_sources": {
        "priority": ["yahoo", "alpha_vantage", "polygon"],
        "yahoo_enabled": True,
    },
    "auto_trade": {
        "enabled": False,
        "min_confidence": 65,
        "max_daily_trades": 5,
        "allowed_symbols": ["EURUSD", "GBPUSD", "USDJPY"],
    },
}


# ==================== API KEYS ====================

@router.get("/keys")
async def get_api_keys():
    """Get API keys (masked for security)."""
    masked = {}
    for k, v in _settings_store["api_keys"].items():
        masked[k] = v[:4] + "****" + v[-4:] if len(v) > 8 else v
    return {"keys": masked}


@router.post("/keys")
async def save_api_keys(
    polygon: str = Query(""),
    alpha_vantage: str = Query(""),
    massive: str = Query(""),
    mt5_account: str = Query(""),
    mt5_password: str = Query(""),
    mt5_server: str = Query(""),
):
    """Save API keys."""
    _settings_store["api_keys"] = {
        "polygon": polygon,
        "alpha_vantage": alpha_vantage,
        "massive": massive,
        "mt5_account": mt5_account,
        "mt5_password": mt5_password,
        "mt5_server": mt5_server,
    }
    return {"status": "saved"}


# ==================== TRADING PREFERENCES ====================

@router.get("/preferences")
async def get_preferences():
    """Get trading preferences."""
    return _settings_store["preferences"]


@router.post("/preferences")
async def save_preferences(
    default_symbol: str = Query("EURUSD"),
    default_timeframe: str = Query("H1"),
    account_balance: float = Query(10_000),
    theme: str = Query("dark"),
):
    """Save trading preferences."""
    _settings_store["preferences"] = {
        "default_symbol": default_symbol.upper(),
        "default_timeframe": default_timeframe,
        "account_balance": account_balance,
        "theme": theme,
    }
    return {"status": "saved"}


# ==================== RISK DEFAULTS ====================

@router.get("/risk")
async def get_risk_defaults():
    """Get risk management defaults."""
    return _settings_store["risk"]


@router.post("/risk")
async def save_risk_defaults(
    default_risk_percent: float = Query(1.0, ge=0.1, le=5.0),
    max_position_size: float = Query(1.0, ge=0.01, le=10.0),
    max_drawdown_percent: float = Query(10.0, ge=1.0, le=50.0),
    max_daily_loss: float = Query(500.0, ge=50),
):
    """Save risk management defaults."""
    _settings_store["risk"] = {
        "default_risk_percent": default_risk_percent,
        "max_position_size": max_position_size,
        "max_drawdown_percent": max_drawdown_percent,
        "max_daily_loss": max_daily_loss,
    }
    return {"status": "saved"}


# ==================== DATA SOURCES ====================

@router.get("/data-sources")
async def get_data_sources():
    """Get data source configuration."""
    return _settings_store["data_sources"]


@router.post("/data-sources")
async def save_data_sources(
    priority: str = Query("yahoo,alpha_vantage,polygon"),
    yahoo_enabled: bool = Query(True),
):
    """Save data source configuration."""
    _settings_store["data_sources"] = {
        "priority": [s.strip() for s in priority.split(",")],
        "yahoo_enabled": yahoo_enabled,
    }
    return {"status": "saved"}


# ==================== AUTO TRADE ====================

@router.get("/auto-trade")
async def get_auto_trade_config():
    """Get auto trading configuration."""
    return _settings_store["auto_trade"]


@router.post("/auto-trade")
async def save_auto_trade_config(
    enabled: bool = Query(False),
    min_confidence: int = Query(65, ge=50, le=100),
    max_daily_trades: int = Query(5, ge=1, le=20),
    allowed_symbols: str = Query("EURUSD,GBPUSD,USDJPY"),
):
    """Save auto trading configuration."""
    _settings_store["auto_trade"] = {
        "enabled": enabled,
        "min_confidence": min_confidence,
        "max_daily_trades": max_daily_trades,
        "allowed_symbols": [s.strip() for s in allowed_symbols.split(",")],
    }
    return {"status": "saved"}


# ==================== SYSTEM INFO ====================

@router.get("/system-info")
async def get_system_info():
    """Get system information."""
    return {
        "version": "0.3.0",
        "sprint": "Sprint 6 — MT5 Bridge & Auto Trading",
        "python_version": "3.12",
        "uptime": "N/A",
        "platform": "Al-Syaka Quant AI",
        "description": "AI-powered Market Intelligence & Trading Signal Platform",
    }


@router.get("/db-status")
async def get_db_status():
    """Get database table statistics."""
    try:
        async with async_session_factory() as session:
            tables = {}
            for table_name in ["symbols", "ohlc", "ticks", "news"]:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                tables[table_name] = count
            return {"tables": tables, "connected": True}
    except Exception as e:
        return {"tables": {}, "connected": False, "error": str(e)}
