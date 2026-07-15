"""Position Management — Open, close, and track positions."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Position:
    """A single trading position."""
    id: str
    symbol: str
    direction: str  # LONG or SHORT
    entry_price: float
    current_price: float
    stop_loss: float
    take_profit: float
    lot_size: float
    entry_time: datetime
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    profit: float = 0.0
    profit_pips: float = 0.0
    signal_id: Optional[str] = None
    exit_reason: str = ""  # TP_HIT, SL_HIT, MANUAL_CLOSE
    status: str = "OPEN"  # OPEN, CLOSED
    notes: str = ""


class PositionManager:
    """Manages open and closed positions."""

    def __init__(self):
        self.open_positions: dict[str, Position] = {}
        self.closed_positions: list[Position] = []
        self._next_id = 1

    def open_position(
        self,
        symbol: str,
        direction: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        lot_size: float,
        signal_id: Optional[str] = None,
    ) -> Position:
        """Open a new position."""
        pos_id = f"PT-{self._next_id:06d}"
        self._next_id += 1

        position = Position(
            id=pos_id,
            symbol=symbol,
            direction=direction,
            entry_price=entry_price,
            current_price=entry_price,
            stop_loss=stop_loss,
            take_profit=take_profit,
            lot_size=lot_size,
            entry_time=datetime.utcnow(),
            signal_id=signal_id,
        )
        self.open_positions[pos_id] = position
        return position

    def close_position(self, position_id: str, exit_price: float, exit_reason: str = "MANUAL_CLOSE") -> Optional[Position]:
        """Close an open position."""
        pos = self.open_positions.get(position_id)
        if not pos:
            return None

        pos.exit_price = exit_price
        pos.exit_time = datetime.utcnow()
        pos.exit_reason = exit_reason
        pos.status = "CLOSED"

        # Calculate P&L
        if pos.direction == "LONG":
            pos.profit_pips = (exit_price - pos.entry_price) / 0.0001
        else:
            pos.profit_pips = (pos.entry_price - exit_price) / 0.0001

        pip_value = 0.0001 * 100_000 * pos.lot_size
        pos.profit = round(pos.profit_pips * pip_value, 2)

        # Move to closed
        self.closed_positions.append(pos)
        del self.open_positions[position_id]

        return pos

    def update_prices(self, price_updates: dict[str, dict]):
        """Update current prices for all open positions."""
        for pos_id, pos in self.open_positions.items():
            if pos.symbol in price_updates:
                update = price_updates[pos.symbol]
                pos.current_price = update.get("close", pos.current_price)

                # Auto-check SL/TP
                high = update.get("high", pos.current_price)
                low = update.get("low", pos.current_price)

                if pos.direction == "LONG":
                    if low <= pos.stop_loss:
                        self.close_position(pos_id, pos.stop_loss, "SL_HIT")
                    elif high >= pos.take_profit:
                        self.close_position(pos_id, pos.take_profit, "TP_HIT")
                else:  # SHORT
                    if high >= pos.stop_loss:
                        self.close_position(pos_id, pos.stop_loss, "SL_HIT")
                    elif low <= pos.take_profit:
                        self.close_position(pos_id, pos.take_profit, "TP_HIT")

    def get_open_pnl(self) -> float:
        """Calculate total unrealized P&L of open positions."""
        total = 0.0
        for pos in self.open_positions.values():
            if pos.direction == "LONG":
                pips = (pos.current_price - pos.entry_price) / 0.0001
            else:
                pips = (pos.entry_price - pos.current_price) / 0.0001
            pip_value = 0.0001 * 100_000 * pos.lot_size
            total += pips * pip_value
        return round(total, 2)

    def get_total_realized_pnl(self) -> float:
        """Calculate total realized P&L from closed positions."""
        return round(sum(p.profit for p in self.closed_positions), 2)

    def summary(self) -> dict:
        """Get position summary."""
        return {
            "open_positions": len(self.open_positions),
            "closed_positions": len(self.closed_positions),
            "open_pnl": self.get_open_pnl(),
            "realized_pnl": self.get_total_realized_pnl(),
            "positions": [
                {
                    "id": p.id,
                    "symbol": p.symbol,
                    "direction": p.direction,
                    "entry": p.entry_price,
                    "current": p.current_price,
                    "sl": p.stop_loss,
                    "tp": p.take_profit,
                    "lot": p.lot_size,
                    "profit": p.profit if p.status == "CLOSED" else None,
                    "entry_time": p.entry_time.isoformat(),
                    "status": p.status,
                }
                for p in list(self.open_positions.values()) + self.closed_positions[-20:]
            ],
        }
