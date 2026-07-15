"""Position Sizing — Hitung lot size berdasarkan risk management."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PositionSizeResult:
    lot_size: float
    notional_value: float
    risk_amount: float
    risk_percent: float


class PositionSizer:
    """Menghitung ukuran posisi (lot) berdasarkan parameter risk."""

    def __init__(
        self,
        account_balance: float = 10_000,
        risk_per_trade: float = 0.01,  # 1% default
        contract_size: int = 100_000,
        max_risk_per_trade: float = 0.02,  # 2% max
    ):
        self.account_balance = account_balance
        self.risk_per_trade = risk_per_trade
        self.contract_size = contract_size
        self.max_risk_per_trade = max_risk_per_trade

    def calculate(
        self,
        entry_price: float,
        stop_loss: float,
        pip_size: float = 0.0001,
        account_balance: Optional[float] = None,
        risk_percent: Optional[float] = None,
    ) -> PositionSizeResult:
        """Calculate optimal lot size."""
        bal = account_balance or self.account_balance
        risk_pct = risk_percent or self.risk_per_trade

        # Clamp risk to max
        risk_pct = min(risk_pct, self.max_risk_per_trade)

        # Risk amount in account currency
        risk_amount = bal * risk_pct

        # Stop loss in pips
        sl_pips = abs(entry_price - stop_loss) / pip_size
        if sl_pips == 0:
            sl_pips = 10  # minimum 10 pips

        # Pip value per lot
        pip_value_per_lot = pip_size * self.contract_size

        # Lot size
        lot_size = risk_amount / (sl_pips * pip_value_per_lot)

        # Round to standard lot sizes
        if lot_size < 0.1:
            lot_size = round(lot_size, 2)  # micro lots
        elif lot_size < 1.0:
            lot_size = round(lot_size, 1)  # mini lots
        else:
            lot_size = round(lot_size, 0)  # standard lots

        notional_value = lot_size * self.contract_size * entry_price

        return PositionSizeResult(
            lot_size=max(lot_size, 0.01),  # minimum 0.01 lot
            notional_value=notional_value,
            risk_amount=risk_amount,
            risk_percent=risk_pct * 100,
        )
