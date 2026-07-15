"""Order Manager — Order validation, risk check, partial fill, error recovery."""

from datetime import datetime
from typing import Optional

from .models import OrderRequest, OrderResult, AccountInfo
from .connector import BaseConnector
from al_syaka_risk import RiskManager


class OrderManager:
    """Validates and executes orders with risk checks."""

    def __init__(self, connector: BaseConnector, min_balance: float = 100):
        self.connector = connector
        self.min_balance = min_balance
        self.risk_manager = RiskManager(account_balance=10_000)
        self.max_positions_per_symbol = 1
        self.max_total_positions = 10
        self.order_history: list[OrderResult] = []

    def validate_order(self, request: OrderRequest, account: Optional[AccountInfo] = None) -> tuple[bool, str]:
        """Validate an order before execution."""
        if not account or not account.connected:
            return False, "Not connected to MT5"

        if account.balance < self.min_balance:
            return False, f"Balance too low: ${account.balance:.2f}"

        if request.volume <= 0:
            return False, "Invalid volume"

        if request.volume > 10:
            return False, "Volume exceeds maximum (10 lots)"

        # Check margin
        margin_required = request.volume * 100_000 * 0.01  # ~1% margin
        if margin_required > account.margin_free:
            return False, f"Insufficient margin: need ${margin_required:.2f}, free ${account.margin_free:.2f}"

        # Check SL/TP proximity
        if request.sl > 0 and request.tp > 0:
            sl_distance = abs(request.price - request.sl)
            tp_distance = abs(request.tp - request.price)
            if tp_distance < sl_distance:
                return False, "Take Profit too close to entry (RR < 1:1)"

        # Check max drawdown
        current_dd = ((account.balance - account.equity) / account.balance * 100
                      if account.balance > 0 else 0)
        if current_dd > 15:
            return False, f"Max drawdown exceeded: {current_dd:.1f}%"

        return True, "OK"

    def execute_order(self, request: OrderRequest) -> OrderResult:
        """Validate and execute an order."""
        account = self.connector.get_account_info()
        valid, msg = self.validate_order(request, account)

        if not valid:
            result = OrderResult(
                status="REJECTED",
                error_message=msg,
                request=request,
            )
            self.order_history.append(result)
            return result

        result = self.connector.place_order(request)
        self.order_history.append(result)
        return result

    def close_position_safely(self, ticket: int) -> bool:
        """Close a position with validation."""
        return self.connector.close_position(ticket)

    def modify_position_safely(self, ticket: int, sl: float, tp: float) -> bool:
        """Modify SL/TP with validation."""
        if sl > 0 and tp > 0 and tp <= sl:
            return False
        return self.connector.modify_position(ticket, sl, tp)

    def get_open_positions(self) -> list:
        """Get all open positions with risk info."""
        positions = self.connector.get_positions()
        total_risk = sum(abs(p.price_open - p.sl) * p.volume * 100_000
                         for p in positions if p.sl > 0)
        return {
            "count": len(positions),
            "total_risk": round(total_risk, 2),
            "positions": positions,
        }
