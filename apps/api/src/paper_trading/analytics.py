"""Performance Analytics — Equity curve, drawdown, monthly ROI, win rate by pair/session."""

import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from .journal import JournalEntry
from .virtual_account import AccountSnapshot


class PerformanceAnalytics:
    """Comprehensive performance analysis from journal entries and account history."""

    def __init__(self, journal_entries: Optional[list[JournalEntry]] = None,
                 equity_history: Optional[list[AccountSnapshot]] = None):
        self.entries = journal_entries or []
        self.equity_history = equity_history or []

    def overall_stats(self) -> dict:
        """Calculate overall trading statistics."""
        closed = [e for e in self.entries if e.result in ("WIN", "LOSS", "BREAKEVEN")]
        if not closed:
            return {"total_trades": 0}

        wins = [e for e in closed if e.result == "WIN"]
        losses = [e for e in closed if e.result == "LOSS"]
        breakeven = [e for e in closed if e.result == "BREAKEVEN"]

        total_profit = sum(e.profit for e in wins)
        total_loss = abs(sum(e.profit for e in losses))
        net_profit = sum(e.profit for e in closed)

        return {
            "total_trades": len(closed),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "breakeven_trades": len(breakeven),
            "win_rate": round(len(wins) / len(closed) * 100, 1) if closed else 0,
            "net_profit": round(net_profit, 2),
            "profit_factor": round(total_profit / total_loss, 2) if total_loss > 0 else float('inf'),
            "avg_profit": round(net_profit / len(closed), 2) if closed else 0,
            "avg_win": round(total_profit / len(wins), 2) if wins else 0,
            "avg_loss": round(total_loss / len(losses), 2) if losses else 0,
            "largest_win": round(max((e.profit for e in wins), default=0), 2),
            "largest_loss": round(min((e.profit for e in losses), default=0), 2),
        }

    def win_rate_by_pair(self) -> dict:
        """Calculate win rate for each trading pair."""
        pairs = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
        for e in self.entries:
            if e.result in ("WIN", "LOSS"):
                pairs[e.symbol]["total"] += 1
                if e.result == "WIN":
                    pairs[e.symbol]["wins"] += 1
                else:
                    pairs[e.symbol]["losses"] += 1

        return {
            pair: {
                "total": stats["total"],
                "win_rate": round(stats["wins"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0,
                "net_profit": round(sum(
                    e.profit for e in self.entries if e.symbol == pair and e.result == "WIN"
                ) - abs(sum(
                    e.profit for e in self.entries if e.symbol == pair and e.result == "LOSS"
                )), 2),
            }
            for pair, stats in sorted(pairs.items(), key=lambda x: x[1]["total"], reverse=True)
        }

    def win_rate_by_session(self) -> dict:
        """Calculate win rate by trading session."""
        sessions = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
        for e in self.entries:
            if e.result in ("WIN", "LOSS"):
                session = e.session or "unknown"
                sessions[session]["total"] += 1
                if e.result == "WIN":
                    sessions[session]["wins"] += 1
                else:
                    sessions[session]["losses"] += 1

        return {
            session: {
                "total": stats["total"],
                "win_rate": round(stats["wins"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0,
            }
            for session, stats in sessions.items()
        }

    def equity_curve(self) -> dict:
        """Get equity curve data for charting."""
        if not self.equity_history:
            return {"timestamps": [], "equity": [], "balance": []}

        return {
            "timestamps": [s.timestamp.isoformat() for s in self.equity_history],
            "equity": [s.equity for s in self.equity_history],
            "balance": [s.balance for s in self.equity_history],
        }

    def drawdown_analysis(self) -> dict:
        """Calculate drawdown statistics from equity curve."""
        if not self.equity_history:
            return {"max_drawdown": 0, "avg_drawdown": 0, "drawdown_periods": []}

        equity = [s.equity for s in self.equity_history]
        peak = np.maximum.accumulate(equity)
        drawdowns = (peak - equity) / peak * 100

        return {
            "max_drawdown": round(float(np.max(drawdowns)), 2),
            "avg_drawdown": round(float(np.mean(drawdowns)), 2),
            "current_drawdown": round(float(drawdowns[-1]), 2) if len(drawdowns) > 0 else 0,
        }

    def monthly_returns(self) -> list[dict]:
        """Calculate monthly return breakdown."""
        monthly = defaultdict(float)
        for e in self.entries:
            if e.exit_time:
                month_key = e.exit_time.strftime("%Y-%m")
                monthly[month_key] += e.profit

        return [
            {"month": month, "profit": round(profit, 2)}
            for month, profit in sorted(monthly.items())
        ]
