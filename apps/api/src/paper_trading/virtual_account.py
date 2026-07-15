"""Virtual Account — Balance tracking, margin, equity."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AccountSnapshot:
    """Snapshot of account state at a point in time."""
    timestamp: datetime
    balance: float
    equity: float
    free_margin: float
    open_positions: int
    daily_pnl: float


class VirtualAccount:
    """Virtual trading account with balance tracking."""

    def __init__(self, initial_balance: float = 10_000, account_name: str = "Paper Trading"):
        self.account_name = account_name
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.peak_balance = initial_balance
        self.equity_history: list[AccountSnapshot] = []
        self.daily_pnl = 0.0
        self.last_snapshot_date = datetime.utcnow().date()
        self.total_deposits = initial_balance
        self.total_withdrawals = 0.0
        self.consecutive_losses = 0
        self.consecutive_wins = 0

    def record_snapshot(self, equity: float, open_positions: int):
        """Record an equity snapshot for charting."""
        now = datetime.utcnow()

        # Reset daily PnL at start of new day
        if now.date() != self.last_snapshot_date:
            self.daily_pnl = 0
            self.last_snapshot_date = now.date()

        self.peak_balance = max(self.peak_balance, self.balance)

        self.equity_history.append(AccountSnapshot(
            timestamp=now,
            balance=self.balance,
            equity=equity,
            free_margin=equity - sum(0 for _ in range(open_positions)),  # simplified
            open_positions=open_positions,
            daily_pnl=self.daily_pnl,
        ))

    def apply_trade_result(self, profit: float):
        """Apply trade result to balance."""
        self.balance += profit
        self.daily_pnl += profit

        if profit > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
            self.consecutive_wins = 0

    def get_drawdown(self) -> float:
        """Calculate current drawdown from peak."""
        if self.peak_balance == 0:
            return 0
        return ((self.peak_balance - self.balance) / self.peak_balance) * 100

    def get_total_return(self) -> float:
        """Calculate total return percentage."""
        if self.initial_balance == 0:
            return 0
        return ((self.balance - self.initial_balance) / self.initial_balance) * 100

    def summary(self) -> dict:
        """Get account summary."""
        return {
            "account_name": self.account_name,
            "initial_balance": self.initial_balance,
            "current_balance": round(self.balance, 2),
            "total_return_pct": round(self.get_total_return(), 2),
            "current_drawdown_pct": round(self.get_drawdown(), 2),
            "peak_balance": self.peak_balance,
            "daily_pnl": round(self.daily_pnl, 2),
            "consecutive_wins": self.consecutive_wins,
            "consecutive_losses": self.consecutive_losses,
        }
