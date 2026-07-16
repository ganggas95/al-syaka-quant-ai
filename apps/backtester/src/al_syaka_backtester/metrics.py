"""Backtest Metrics — Winrate, Drawdown, Sharpe, Sortino, Profit Factor."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class BacktestMetrics:
    """Comprehensive backtest performance metrics."""
    # Core stats
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: float = 0.0

    # Profitability
    total_profit: float = 0.0
    total_loss: float = 0.0
    net_profit: float = 0.0
    profit_factor: float = 0.0
    avg_profit_per_trade: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_consecutive_wins: int = 0
    max_consecutive_losses: int = 0

    # Risk metrics
    max_drawdown: float = 0.0
    max_drawdown_percent: float = 0.0
    sharpe_ratio: float = 0.0
    sortino_ratio: float = 0.0
    calmar_ratio: float = 0.0
    recovery_factor: float = 0.0     # Net Profit / Max Drawdown
    expectancy: float = 0.0          # (WR × AvgWin) - (LR × AvgLoss)

    # Time metrics
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    total_days: int = 0

    # Trade distribution
    best_trade: float = 0.0
    worst_trade: float = 0.0
    avg_bars_held: float = 0.0

    # Monthly/yearly breakdown
    monthly_returns: dict = None
    yearly_returns: dict = None


class MetricsCalculator:
    """Calculate comprehensive backtest metrics from trade records."""

    @staticmethod
    def calculate(trades: list, equity_curve: list) -> BacktestMetrics:
        """Calculate all metrics from list of TradeRecord objects."""
        m = BacktestMetrics()
        m.total_trades = len([t for t in trades if t.result != "PENDING"])
        if m.total_trades == 0:
            return m

        winning = [t for t in trades if t.result == "WIN"]
        losing = [t for t in trades if t.result == "LOSS"]
        m.winning_trades = len(winning)
        m.losing_trades = len(losing)
        m.win_rate = m.winning_trades / m.total_trades if m.total_trades > 0 else 0

        # Profit
        profits = [t.profit for t in trades if t.result != "PENDING"]
        m.net_profit = sum(profits)
        m.total_profit = sum(p for p in profits if p > 0)
        m.total_loss = abs(sum(p for p in profits if p < 0))
        m.profit_factor = m.total_profit / m.total_loss if m.total_loss > 0 else float('inf')
        m.avg_profit_per_trade = m.net_profit / m.total_trades if m.total_trades > 0 else 0

        # Avg win/loss
        m.avg_win = sum(t.profit for t in winning) / len(winning) if winning else 0
        m.avg_loss = sum(abs(t.profit) for t in losing) / len(losing) if losing else 0

        # Expectancy = (WR × AvgWin) - (LR × AvgLoss)
        loss_rate = m.losing_trades / m.total_trades if m.total_trades > 0 else 0
        m.expectancy = (m.win_rate * m.avg_win) - (loss_rate * m.avg_loss)

        # Best / worst
        if profits:
            m.best_trade = max(profits)
            m.worst_trade = min(profits)

        # Consecutive
        cons_wins = cons_losses = 0
        max_wins = max_losses = 0
        for t in trades:
            if t.result == "WIN":
                cons_wins += 1
                cons_losses = 0
                max_wins = max(max_wins, cons_wins)
            elif t.result == "LOSS":
                cons_losses += 1
                cons_wins = 0
                max_losses = max(max_losses, cons_losses)
        m.max_consecutive_wins = max_wins
        m.max_consecutive_losses = max_losses

        # Drawdown — extract equity values from dict format
        if equity_curve:
            equity_values = [e["equity"] if isinstance(e, dict) else e for e in equity_curve]
            equity_arr = np.array(equity_values)
            peak = np.maximum.accumulate(equity_arr)
            drawdown = peak - equity_arr
            drawdown_pct = drawdown / peak * 100
            m.max_drawdown = np.max(drawdown)
            m.max_drawdown_percent = np.max(drawdown_pct)
            m.recovery_factor = m.net_profit / m.max_drawdown if m.max_drawdown > 0 else 0.0

        # Sharpe Ratio (annualized, assuming daily returns)
        if len(equity_curve) > 1:
            equity_values = [e["equity"] if isinstance(e, dict) else e for e in equity_curve]
            equity_series = pd.Series(equity_values)
            daily_returns = equity_series.pct_change().dropna()
            if len(daily_returns) > 1 and daily_returns.std() > 0:
                m.sharpe_ratio = np.sqrt(252) * (daily_returns.mean() / daily_returns.std())
                # Sortino (only negative std)
                neg_returns = daily_returns[daily_returns < 0]
                if len(neg_returns) > 0 and neg_returns.std() > 0:
                    m.sortino_ratio = np.sqrt(252) * (daily_returns.mean() / neg_returns.std())
                # Calmar
                initial = equity_values[0] if equity_values else 10000
                calmar_num = m.net_profit / initial * 100
                m.calmar_ratio = calmar_num / m.max_drawdown_percent if m.max_drawdown_percent > 0 else 0

        # Time
        times = [t.entry_time for t in trades if t.entry_time]
        if times:
            m.start_date = min(times)
            m.end_date = max(times)
            m.total_days = (m.end_date - m.start_date).days

        # Avg bars held
        held = [((t.exit_time - t.entry_time).total_seconds() / 3600) for t in trades if t.exit_time and t.entry_time]
        m.avg_bars_held = np.mean(held) if held else 0

        # Monthly returns
        m.monthly_returns = MetricsCalculator._calc_monthly_returns(trades, equity_curve)

        return m

    @staticmethod
    def _calc_monthly_returns(trades: list, equity_curve: list) -> dict:
        """Calculate monthly returns from equity curve or trades."""
        monthly = {}
        for t in trades:
            if t.exit_time and t.result != "PENDING":
                key = t.exit_time.strftime("%Y-%m")
                if key not in monthly:
                    monthly[key] = 0.0
                monthly[key] += t.profit
        return monthly
