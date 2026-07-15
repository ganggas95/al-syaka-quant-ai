"""Auto Trading Engine — Signal-based auto execution, scheduling, kill switch."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Callable
import time
import threading

from .connector import BaseConnector
from .order_manager import OrderManager
from .models import OrderRequest
from .safety import SafetySystem


@dataclass
class AutoTradeConfig:
    """Configuration for auto trading."""
    enabled: bool = False
    max_daily_trades: int = 5
    min_confidence: float = 0.65  # Minimum AI confidence
    allowed_symbols: list[str] = None
    max_position_size: float = 1.0  # Max lots
    only_trade_sessions: list[str] = None  # asian, london, us


class AutoTradingEngine:
    """Automatically executes signals from the Signal Generator."""

    def __init__(self, connector: BaseConnector, order_manager: OrderManager, safety: SafetySystem):
        self.connector = connector
        self.order_manager = order_manager
        self.safety = safety
        self.config = AutoTradeConfig(allowed_symbols=["EURUSD", "GBPUSD", "USDJPY"])
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.daily_trades = 0
        self.last_trade_date = datetime.utcnow().date()
        self.executed_signals: list[dict] = []

    def start(self):
        """Start the auto trading loop."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop auto trading."""
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def process_signal(self, signal: dict) -> Optional[dict]:
        """Process a single signal and execute if conditions are met."""
        # Reset daily counter at midnight
        today = datetime.utcnow().date()
        if today != self.last_trade_date:
            self.daily_trades = 0
            self.last_trade_date = today

        # Safety checks
        if not self.safety.can_trade():
            return {"executed": False, "reason": "Safety system blocked trade"}

        if not self.config.enabled:
            return {"executed": False, "reason": "Auto trading disabled"}

        # Check signal validity
        sig_signal = signal.get("signal", "NEUTRAL")
        if sig_signal not in ("BUY", "SELL"):
            return {"executed": False, "reason": f"Signal is {sig_signal}, not actionable"}

        confidence = signal.get("confidence", 0)
        if confidence < self.config.min_confidence:
            return {"executed": False, "reason": f"Confidence {confidence}% < min {self.config.min_confidence * 100}%"}

        symbol = signal.get("symbol", "")
        if symbol not in self.config.allowed_symbols:
            return {"executed": False, "reason": f"{symbol} not in allowed list"}

        if self.daily_trades >= self.config.max_daily_trades:
            return {"executed": False, "reason": f"Daily limit reached ({self.daily_trades})"}

        # Build order
        direction = "BUY" if sig_signal == "BUY" else "SELL"
        volume = min(0.1 * (confidence / 50), self.config.max_position_size)
        entry = signal.get("entry", 0)
        sl = signal.get("stop_loss", 0)
        tp = signal.get("take_profit", 0)

        if entry == 0:
            return {"executed": False, "reason": "No entry price"}

        request = OrderRequest(
            symbol=symbol,
            order_type=direction,
            volume=round(volume, 2),
            price=entry,
            sl=sl,
            tp=tp,
            comment=f"Auto: {signal.get('signal_id', 'AI')}",
            signal_id=signal.get("signal_id"),
        )

        # Execute
        result = self.order_manager.execute_order(request)

        if result.status == "FILLED":
            self.daily_trades += 1
            self.safety.record_trade(profit=0)  # Will update when closed
            self.executed_signals.append({
                "time": datetime.utcnow().isoformat(),
                "symbol": symbol,
                "signal": sig_signal,
                "confidence": confidence,
                "ticket": result.ticket,
                "price": result.price,
                "volume": result.filled_volume,
            })

        return {
            "executed": result.status == "FILLED",
            "ticket": result.ticket,
            "status": result.status,
            "reason": result.error_message or "OK",
        }

    def _run_loop(self):
        """Main auto trading loop — checks for new signals periodically."""
        while self._running:
            time.sleep(5)  # Check every 5 seconds
            if not self.safety.can_trade():
                continue
            # In production, this would poll a signal queue
