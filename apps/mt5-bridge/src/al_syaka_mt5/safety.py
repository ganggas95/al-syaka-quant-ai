"""Safety System — Kill switch, max drawdown, daily loss limit, circuit breaker."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class SafetyConfig:
    """Safety system configuration."""
    max_daily_loss: float = 500.0  # Max daily loss in dollars
    max_drawdown_percent: float = 10.0  # Max drawdown from peak
    max_consecutive_losses: int = 5
    max_positions: int = 5
    circuit_breaker_cooldown_minutes: int = 30
    kill_switch_engaged: bool = False


class SafetySystem:
    """Multiple layers of protection for auto trading."""

    def __init__(self, initial_balance: float = 10_000):
        self.config = SafetyConfig()
        self.peak_balance = initial_balance
        self.current_balance = initial_balance
        self.daily_loss = 0.0
        self.consecutive_losses = 0
        self.last_loss_date = datetime.utcnow().date()
        self.circuit_breaker_until: Optional[datetime] = None
        self.trade_log: list[dict] = []

    def can_trade(self) -> bool:
        """Check if trading is allowed based on all safety conditions."""
        # Kill switch
        if self.config.kill_switch_engaged:
            return False

        # Circuit breaker
        if self.circuit_breaker_until and datetime.utcnow() < self.circuit_breaker_until:
            return False

        # Daily loss limit
        today = datetime.utcnow().date()
        if today != self.last_loss_date:
            self.daily_loss = 0.0
            self.last_loss_date = today
        if self.daily_loss >= self.config.max_daily_loss:
            return False

        # Max drawdown
        if self.peak_balance > 0:
            dd = ((self.peak_balance - self.current_balance) / self.peak_balance) * 100
            if dd >= self.config.max_drawdown_percent:
                return False

        return True

    def record_trade(self, profit: float):
        """Record a trade result and update safety state."""
        self.current_balance += profit
        self.peak_balance = max(self.peak_balance, self.current_balance)

        # Track daily loss
        if profit < 0:
            self.daily_loss += abs(profit)
            self.consecutive_losses += 1

            # Circuit breaker on consecutive losses
            if self.consecutive_losses >= self.config.max_consecutive_losses:
                self.circuit_breaker_until = datetime.utcnow() + timedelta(
                    minutes=self.config.circuit_breaker_cooldown_minutes
                )
                self.consecutive_losses = 0
        else:
            self.consecutive_losses = 0

        self.trade_log.append({
            "time": datetime.utcnow().isoformat(),
            "profit": profit,
            "balance": self.current_balance,
        })

    def engage_kill_switch(self):
        """Emergency stop — kill all trading."""
        self.config.kill_switch_engaged = True

    def disengage_kill_switch(self):
        """Re-enable trading after kill switch."""
        self.config.kill_switch_engaged = False
        self.circuit_breaker_until = None

    def get_status(self) -> dict:
        """Get comprehensive safety status."""
        peak_dd = ((self.peak_balance - self.current_balance) / self.peak_balance * 100
                   if self.peak_balance > 0 else 0)

        return {
            "can_trade": self.can_trade(),
            "kill_switch": self.config.kill_switch_engaged,
            "circuit_breaker_active": (
                self.circuit_breaker_until and datetime.utcnow() < self.circuit_breaker_until
            ),
            "circuit_breaker_until": self.circuit_breaker_until.isoformat() if self.circuit_breaker_until else None,
            "current_balance": round(self.current_balance, 2),
            "peak_balance": round(self.peak_balance, 2),
            "drawdown_percent": round(peak_dd, 2),
            "daily_loss": round(self.daily_loss, 2),
            "max_daily_loss": self.config.max_daily_loss,
            "consecutive_losses": self.consecutive_losses,
            "max_consecutive_losses": self.config.max_consecutive_losses,
        }
