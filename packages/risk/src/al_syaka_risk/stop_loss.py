"""Stop Loss & Take Profit Calculator."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SLTPResult:
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    sl_pips: float
    tp_pips: float


class StopLossCalculator:
    """Menghitung SL dan TP berdasarkan level teknikal atau risk parameter."""

    def calculate_atr_based(
        self,
        entry_price: float,
        atr_value: float,
        direction: str,  # LONG or SHORT
        sl_multiplier: float = 1.5,
        tp_multiplier: float = 3.0,
    ) -> SLTPResult:
        """Calculate SL/TP based on ATR."""
        if direction == "LONG":
            stop_loss = entry_price - (atr_value * sl_multiplier)
            take_profit = entry_price + (atr_value * tp_multiplier)
        else:
            stop_loss = entry_price + (atr_value * sl_multiplier)
            take_profit = entry_price - (atr_value * tp_multiplier)

        rr = abs(take_profit - entry_price) / abs(stop_loss - entry_price)
        return self._make_result(entry_price, stop_loss, take_profit, rr)

    def calculate_fixed_pips(
        self,
        entry_price: float,
        direction: str,
        sl_pips: float = 20,
        tp_pips: float = 40,
        pip_size: float = 0.0001,
    ) -> SLTPResult:
        """Calculate SL/TP based on fixed pip distance."""
        sl_distance = sl_pips * pip_size
        tp_distance = tp_pips * pip_size

        if direction == "LONG":
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + tp_distance
        else:
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - tp_distance

        return self._make_result(entry_price, stop_loss, take_profit, tp_pips / sl_pips)

    def calculate_sr_based(
        self,
        entry_price: float,
        direction: str,
        support_level: Optional[float] = None,
        resistance_level: Optional[float] = None,
        risk_reward: float = 2.0,
    ) -> SLTPResult:
        """Calculate SL/TP based on S/R levels."""
        if direction == "LONG" and support_level:
            stop_loss = support_level
            sl_distance = entry_price - support_level
            take_profit = entry_price + (sl_distance * risk_reward)
        elif direction == "SHORT" and resistance_level:
            stop_loss = resistance_level
            sl_distance = resistance_level - entry_price
            take_profit = entry_price - (sl_distance * risk_reward)
        else:
            # Fallback to ATR-based
            return self.calculate_atr_based(entry_price, 0.001, direction)

        return self._make_result(entry_price, stop_loss, take_profit, risk_reward)

    def _make_result(self, entry, sl, tp, rr):
        return SLTPResult(
            entry_price=entry,
            stop_loss=round(sl, 5),
            take_profit=round(tp, 5),
            risk_reward_ratio=round(rr, 2),
            sl_pips=round(abs(entry - sl) / 0.0001, 0),
            tp_pips=round(abs(entry - tp) / 0.0001, 0),
        )
