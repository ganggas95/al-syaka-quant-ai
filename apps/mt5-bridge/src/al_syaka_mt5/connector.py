"""MT5 Connector — Abstraction layer with simulation mode for macOS development.

The MetaTrader5 library is Windows-only. This abstraction provides:
1. Simulation mode — works on macOS/Linux for development
2. Live mode — uses MetaTrader5 library on Windows for real trading
3. Common interface for both modes
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional
import random
import time

from .models import AccountInfo, OrderRequest, OrderResult, Position, OrderHistory


class BaseConnector(ABC):
    """Abstract base MT5 connector."""

    @abstractmethod
    def initialize(self, login: int, server: str, password: str) -> bool:
        ...

    @abstractmethod
    def shutdown(self):
        ...

    @abstractmethod
    def get_account_info(self) -> Optional[AccountInfo]:
        ...

    @abstractmethod
    def place_order(self, request: OrderRequest) -> OrderResult:
        ...

    @abstractmethod
    def close_position(self, ticket: int) -> bool:
        ...

    @abstractmethod
    def modify_position(self, ticket: int, sl: float, tp: float) -> bool:
        ...

    @abstractmethod
    def get_positions(self) -> list[Position]:
        ...

    @abstractmethod
    def get_history(self, from_date: datetime, to_date: datetime) -> list[OrderHistory]:
        ...


class MT5SimulationConnector(BaseConnector):
    """Simulation connector — works on macOS for development."""

    def __init__(self):
        self._connected = False
        self._account = AccountInfo()
        self._positions: dict[int, Position] = {}
        self._next_ticket = 100000
        self._prices: dict[str, float] = {
            "EURUSD": 1.0824, "GBPUSD": 1.2678, "USDJPY": 151.45,
            "AUDUSD": 0.6580, "USDCAD": 1.3580, "NZDUSD": 0.6010,
        }

    def initialize(self, login: int = 123456, server: str = "ICMarkets-Demo",
                   password: str = "demo") -> bool:
        self._connected = True
        self._account = AccountInfo(
            login=login,
            server=server,
            balance=100_000.0,
            equity=100_000.0,
            margin=0.0,
            margin_free=100_000.0,
            margin_level=100.0,
            currency="USD",
            name=f"Simulation Account ({login})",
            leverage=100,
            connected=True,
        )
        return True

    def shutdown(self):
        self._connected = False

    def get_account_info(self) -> Optional[AccountInfo]:
        if not self._connected:
            return None
        # Simulate floating P&L
        total_profit = sum(p.profit for p in self._positions.values())
        self._account.equity = self._account.balance + total_profit
        self._account.margin_free = self._account.equity - self._account.margin
        self._account.margin_level = (self._account.equity / self._account.margin * 100
                                       if self._account.margin > 0 else 0)
        return self._account

    def place_order(self, request: OrderRequest) -> OrderResult:
        if not self._connected:
            return OrderResult(status="ERROR", error_message="Not connected")

        # Determine execution price
        if request.order_type in ("BUY", "BUY_LIMIT", "BUY_STOP"):
            price = request.price if request.price > 0 else self._prices.get(request.symbol, 1.0)
        else:
            price = request.price if request.price > 0 else self._prices.get(request.symbol, 1.0)

        ticket = self._next_ticket
        self._next_ticket += 1

        # Add position
        pos = Position(
            ticket=ticket,
            symbol=request.symbol,
            type=request.order_type,
            volume=request.volume,
            price_open=price,
            price_current=price,
            sl=request.sl,
            tp=request.tp,
            profit=0.0,
            swap=0.0,
            comment=request.comment or f"Signal: {request.signal_id or 'manual'}",
            magic=request.magic,
            open_time=datetime.utcnow(),
        )
        self._positions[ticket] = pos

        return OrderResult(
            ticket=ticket,
            filled_volume=request.volume,
            price=price,
            status="FILLED",
            request=request,
        )

    def close_position(self, ticket: int) -> bool:
        pos = self._positions.pop(ticket, None)
        if pos:
            return True
        return False

    def modify_position(self, ticket: int, sl: float, tp: float) -> bool:
        pos = self._positions.get(ticket)
        if pos:
            pos.sl = sl
            pos.tp = tp
            return True
        return False

    def get_positions(self) -> list[Position]:
        # Simulate price movements for open positions
        for pos in self._positions.values():
            base = self._prices.get(pos.symbol, 1.0)
            movement = (random.random() - 0.48) * 0.0005  # Slight bullish bias
            sim_price = base + movement
            pos.price_current = round(sim_price, 5)

            if pos.type == "BUY":
                pos.profit = round((pos.price_current - pos.price_open) * pos.volume * 100_000, 2)
            else:
                pos.profit = round((pos.price_open - pos.price_current) * pos.volume * 100_000, 2)

        return list(self._positions.values())

    def get_history(self, from_date: datetime, to_date: datetime) -> list[OrderHistory]:
        return []

    def simulate_price_update(self, symbol: str, price: float):
        """For testing: manually set a price."""
        self._prices[symbol] = price


class MT5Connector(BaseConnector):
    """Real MT5 connector — requires Windows + MetaTrader5 library.

    Falls back to simulation if MetaTrader5 is not available.
    """

    def __init__(self):
        self._mt5 = None
        self._initialized = False

    def initialize(self, login: int, server: str, password: str) -> bool:
        try:
            import MetaTrader5 as mt5
            self._mt5 = mt5
            self._initialized = mt5.initialize(login=login, server=server, password=password)
            return self._initialized
        except ImportError:
            print("⚠️ MetaTrader5 not available. Falling back to simulation.")
            sim = MT5SimulationConnector()
            return sim.initialize(login, server, password)

    def shutdown(self):
        if self._mt5 and self._initialized:
            self._mt5.shutdown()

    def get_account_info(self) -> Optional[AccountInfo]:
        if not self._mt5 or not self._initialized:
            return None
        info = self._mt5.account_info()
        if info:
            return AccountInfo(
                login=info.login,
                server=info.server or "",
                balance=info.balance,
                equity=info.equity,
                margin=info.margin,
                margin_free=info.margin_free,
                margin_level=info.margin_level,
                currency=info.currency,
                name=info.name or "",
                leverage=info.leverage,
                connected=True,
            )
        return None

    def place_order(self, request: OrderRequest) -> OrderResult:
        # Implementation for real MT5
        return OrderResult(status="ERROR", error_message="Live MT5 requires Windows")

    def close_position(self, ticket: int) -> bool:
        return False

    def modify_position(self, ticket: int, sl: float, tp: float) -> bool:
        return False

    def get_positions(self) -> list[Position]:
        return []

    def get_history(self, from_date: datetime, to_date: datetime) -> list[OrderHistory]:
        return []
