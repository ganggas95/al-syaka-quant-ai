"""Kelly Criterion — Optimal position sizing."""

import math


class KellyCriterion:
    """Optimal bet sizing based on Kelly formula."""

    @staticmethod
    def calculate(win_rate: float, avg_win: float, avg_loss: float) -> float:
        """Calculate optimal fraction of capital to risk.

        Args:
            win_rate: Probability of winning (0.0 - 1.0)
            avg_win: Average profit on winning trades
            avg_loss: Average loss on losing trades

        Returns:
            Kelly fraction (0.0 - 1.0). Use fractional Kelly (25-50%) for safety.
        """
        if avg_loss == 0:
            return 0.0

        r = avg_win / avg_loss  # Win/Loss ratio
        kelly = win_rate - ((1 - win_rate) / r)
        return max(0.0, kelly)

    @staticmethod
    def fractional_kelly(win_rate: float, avg_win: float, avg_loss: float, fraction: float = 0.25) -> float:
        """Conservative Kelly (25% default for safety)."""
        full_kelly = KellyCriterion.calculate(win_rate, avg_win, avg_loss)
        return full_kelly * fraction

    @staticmethod
    def recommended_risk(win_rate: float, avg_win: float, avg_loss: float) -> dict:
        """Get recommended risk per trade with multiple safety levels."""
        full = KellyCriterion.calculate(win_rate, avg_win, avg_loss)

        return {
            "full_kelly": round(full * 100, 2),
            "aggressive": round(full * 0.5 * 100, 2),   # 50% Kelly
            "moderate": round(full * 0.25 * 100, 2),     # 25% Kelly
            "conservative": round(full * 0.1 * 100, 2),  # 10% Kelly
            "max_recommended": 2.0,  # Hard cap at 2%
        }
