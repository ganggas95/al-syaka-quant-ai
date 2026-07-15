"""MT5 Data Models — OrderRequest, OrderResult, AccountInfo."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class AccountInfo:
    """MT5 account information."""
    login: int = 0
    server: str = ""
    balance: float = 0.0
    equity: float = 0.0
    margin: float = 0.0
    margin_free: float = 0.0
    margin_level: float = 0.0
    currency: str = "USD"
    name: str = ""
    leverage: int = 100
    connected: bool = False


@dataclass
class OrderRequest:
    """Order request to be sent to MT5."""
    symbol: str
    order_type: str  # BUY, SELL, BUY_LIMIT, SELL_LIMIT, BUY_STOP, SELL_STOP
    volume: float  # Lot size
    price: float  # Entry price (0 for market orders)
    sl: float = 0.0  # Stop Loss
    tp: float = 0.0  # Take Profit
    deviation: int = 10  # Slippage in points
    comment: str = ""
    magic: int = 202401  # Expert Advisor ID
    signal_id: Optional[str] = None


@dataclass
class OrderResult:
    """Result of an order execution."""
    order_id: Optional[int] = None
    ticket: Optional[int] = None
    filled_volume: float = 0.0
    price: float = 0.0
    status: str = ""  # FILLED, PARTIAL, REJECTED, ERROR
    error_message: str = ""
    request: Optional[OrderRequest] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Position:
    """Open position from MT5."""
    ticket: int
    symbol: str
    type: str  # BUY, SELL
    volume: float
    price_open: float
    price_current: float
    sl: float
    tp: float
    profit: float
    swap: float
    comment: str
    magic: int
    open_time: datetime


@dataclass
class OrderHistory:
    """Historical order record."""
    ticket: int
    symbol: str
    type: str
    volume: float
    price: float
    profit: float
    commission: float
    swap: float
    comment: str
    open_time: datetime
    close_time: datetime
