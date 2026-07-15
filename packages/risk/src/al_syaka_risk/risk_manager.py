"""Risk Manager — Mengintegrasikan semua komponen risk management."""

from dataclasses import dataclass
from typing import Optional

from .position_sizing import PositionSizer
from .stop_loss import StopLossCalculator
from .kelly import KellyCriterion


@dataclass
class RiskDecision:
    """Keputusan risk lengkap untuk sebuah trade."""
    signal: str  # BUY/SELL
    direction: str  # LONG/SHORT
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    lot_size: float
    risk_amount: float
    risk_percent: float
    kelly_percent: float
    trade_quality: str  # POOR, FAIR, GOOD, EXCELLENT


class RiskManager:
    """Risk manager yang mengintegrasikan position sizing, SL/TP, dan Kelly."""

    def __init__(self, account_balance: float = 10_000):
        self.account_balance = account_balance
        self.position_sizer = PositionSizer(account_balance=account_balance)
        self.sl_calculator = StopLossCalculator()
        self.consecutive_losses = 0

    def evaluate_trade(
        self,
        signal: str,
        entry_price: float,
        confidence: float,
        atr_value: Optional[float] = None,
        support: Optional[float] = None,
        resistance: Optional[float] = None,
        win_rate: float = 0.5,
        avg_win: float = 50,
        avg_loss: float = 25,
    ) -> RiskDecision:
        """Evaluate a complete trade with full risk assessment."""
        direction = "LONG" if signal == "BUY" else "SHORT"

        # 1. Calculate SL/TP
        if atr_value:
            sltp = self.sl_calculator.calculate_atr_based(entry_price, atr_value, direction)
        elif support and direction == "LONG":
            sltp = self.sl_calculator.calculate_sr_based(entry_price, direction, support_level=support)
        elif resistance and direction == "SHORT":
            sltp = self.sl_calculator.calculate_sr_based(entry_price, direction, resistance_level=resistance)
        else:
            sltp = self.sl_calculator.calculate_fixed_pips(entry_price, direction)

        # 2. Adjust risk based on consecutive losses
        risk_pct = 0.01  # 1% default
        if self.consecutive_losses >= 3:
            risk_pct = 0.005  # Reduce to 0.5% after 3 losses
        if self.consecutive_losses >= 5:
            risk_pct = 0.0025  # Reduce to 0.25% after 5 losses

        # 3. Calculate position size
        pos = self.position_sizer.calculate(
            entry_price=entry_price,
            stop_loss=sltp.stop_loss,
            risk_percent=risk_pct,
        )

        # 4. Kelly Criterion
        kelly = KellyCriterion.recommended_risk(win_rate, avg_win, avg_loss)

        # 5. Trade quality assessment
        quality = self._assess_quality(confidence, sltp.risk_reward_ratio, pos.risk_percent)

        return RiskDecision(
            signal=signal,
            direction=direction,
            entry_price=entry_price,
            stop_loss=sltp.stop_loss,
            take_profit=sltp.take_profit,
            risk_reward_ratio=sltp.risk_reward_ratio,
            lot_size=pos.lot_size,
            risk_amount=pos.risk_amount,
            risk_percent=pos.risk_percent,
            kelly_percent=kelly["moderate"],
            trade_quality=quality,
        )

    def _assess_quality(self, confidence: float, rr: float, risk_pct: float) -> str:
        """Assess overall trade quality."""
        score = 0
        if confidence >= 0.7:
            score += 2
        elif confidence >= 0.6:
            score += 1
        if rr >= 2.0:
            score += 2
        elif rr >= 1.5:
            score += 1
        if risk_pct <= 1.0:
            score += 1

        if score >= 4:
            return "EXCELLENT"
        elif score >= 3:
            return "GOOD"
        elif score >= 2:
            return "FAIR"
        return "POOR"

    def record_loss(self):
        self.consecutive_losses += 1

    def record_win(self):
        self.consecutive_losses = 0
