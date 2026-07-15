"""Walk Forward Validation & Monte Carlo Simulation."""

import random
from dataclasses import dataclass
from typing import List

import numpy as np
import pandas as pd

from .engine import BacktestConfig, BacktestEngine


@dataclass
class WalkForwardResult:
    """Single Walk Forward fold result."""
    fold: int
    is_trades: int
    is_pf: float
    is_net: float
    oos_trades: int
    oos_pf: float
    oos_net: float
    oos_dd: float


@dataclass
class MonteCarloResult:
    """Monte Carlo simulation results."""
    simulations: int
    total_trades: int
    prob_profitable: float       # % of sims with net > 0
    prob_pf_gt_1: float          # % of sims with PF > 1.0
    prob_pf_gt_1_3: float        # % of sims with PF > 1.30
    prob_dd_gt_10: float         # % of sims with DD > 10%
    avg_net: float
    median_net: float
    ci_95_low: float             # 2.5th percentile
    ci_95_high: float            # 97.5th percentile
    worst_case: float
    best_case: float


class WalkForwardValidator:
    """Walk Forward Analysis — tests strategy stability across time periods."""

    def __init__(self, df: pd.DataFrame, config: BacktestConfig,
                 n_folds: int = 4):
        self.df = df
        self.config = config
        self.n_folds = n_folds
        self.results: List[WalkForwardResult] = []

    def run(self) -> List[WalkForwardResult]:
        """Run walk forward analysis."""
        total_bars = len(self.df)
        fold_size = total_bars // self.n_folds
        is_pct = 0.7  # 70% in-sample, 30% out-of-sample

        dfs = []
        for fold in range(self.n_folds):
            fold_start = fold * fold_size
            is_end = fold_start + int(fold_size * is_pct)
            fold_end = min(fold_start + fold_size, total_bars)

            if fold_end - is_end < 50:  # Skip if OOS too small
                continue

            df_is = self.df.iloc[fold_start:is_end].copy()
            df_oos = self.df.iloc[is_end:fold_end].copy()

            if len(df_is) < 100 or len(df_oos) < 50:
                continue

            # Run on in-sample
            engine_is = BacktestEngine(self.config)
            is_metrics = engine_is.run(df_is)

            # Run on out-of-sample
            engine_oos = BacktestEngine(self.config)
            oos_metrics = engine_oos.run(df_oos)

            result = WalkForwardResult(
                fold=fold + 1,
                is_trades=is_metrics.total_trades,
                is_pf=round(is_metrics.profit_factor, 4),
                is_net=round(is_metrics.net_profit, 2),
                oos_trades=oos_metrics.total_trades,
                oos_pf=round(oos_metrics.profit_factor, 4),
                oos_net=round(oos_metrics.net_profit, 2),
                oos_dd=round(oos_metrics.max_drawdown_percent, 2),
            )
            self.results.append(result)

        return self.results

    def summary(self) -> str:
        """Generate walk forward summary."""
        if not self.results:
            return "No results."

        lines = []
        lines.append(f"{'Fold':<6} {'IS Trades':<10} {'IS PF':<8} {'IS Net':<10} "
                     f"{'OOS Trades':<11} {'OOS PF':<8} {'OOS Net':<10} {'OOS DD':<8}")
        lines.append("-" * 75)

        for r in self.results:
            lines.append(
                f"{r.fold:<6} {r.is_trades:<10} {r.is_pf:<8} ${r.is_net:<8.2f} "
                f"{r.oos_trades:<11} {r.oos_pf:<8} ${r.oos_net:<8.2f} {r.oos_dd:<8}"
            )

        lines.append("-" * 75)
        oos_pfs = [r.oos_pf for r in self.results if r.oos_pf != float('inf')]
        oos_nets = [r.oos_net for r in self.results]
        oos_valid = [r for r in self.results
                     if r.oos_pf != float('inf') and r.oos_trades >= 10]
        avg_pf = np.mean(oos_pfs) if oos_pfs else 0
        avg_net = np.mean(oos_nets) if oos_nets else 0
        positive_folds = sum(1 for r in oos_valid if r.oos_pf > 1.0)

        lines.append(f"Avg OOS PF: {avg_pf:.4f}")
        lines.append(f"Avg OOS Net: ${avg_net:.2f}")
        lines.append(f"Positive PF folds: {positive_folds}/{len(oos_valid)}")

        return "\n".join(lines)


class MonteCarloSimulator:
    """Monte Carlo Simulation — randomizes trade outcomes to assess robustness."""

    def __init__(self, trades: list, simulations: int = 10000):
        self.trades = trades
        self.simulations = simulations
        self.closed_trades = [
            t for t in trades if t.result in ("WIN", "LOSS")
        ]

    def run(self) -> MonteCarloResult:
        """Run Monte Carlo simulation."""
        n_trades = len(self.closed_trades)
        if n_trades < 10:
            return MonteCarloResult(
                simulations=self.simulations,
                total_trades=n_trades,
                prob_profitable=0.0,
                prob_pf_gt_1=0.0,
                prob_pf_gt_1_3=0.0,
                prob_dd_gt_10=0.0,
                avg_net=0.0, median_net=0.0,
                ci_95_low=0.0, ci_95_high=0.0,
                worst_case=0.0, best_case=0.0,
            )

        pnl_values = [t.profit for t in self.closed_trades]
        trade_size = abs(np.mean(pnl_values)) if pnl_values else 1.0

        net_profits = []
        dd_pcts = []

        for _ in range(self.simulations):
            sampled = random.choices(pnl_values, k=n_trades)
            net = sum(sampled)
            net_profits.append(net)

            # Calculate drawdown for this simulation
            peak = 0.0
            max_dd = 0.0
            running = 0.0
            for pnl in sampled:
                running += pnl
                if running > peak:
                    peak = running
                dd = peak - running
                if dd > max_dd:
                    max_dd = dd
            dd_pct = (max_dd / 10000) * 100  # % of 10k balance
            dd_pcts.append(dd_pct)

        net_profits = np.array(net_profits)
        dd_pcts = np.array(dd_pcts)

        profitable_count = int(np.sum(net_profits > 0))
        pf_gt_1_count = int(np.sum(net_profits > 0))  # net > 0 ≈ PF > 1.0
        pf_gt_1_3 = int(np.sum(net_profits > 1000))  # approx PF > 1.30
        dd_gt_10 = int(np.sum(dd_pcts > 10))

        return MonteCarloResult(
            simulations=self.simulations,
            total_trades=n_trades,
            prob_profitable=round(profitable_count / self.simulations * 100, 2),
            prob_pf_gt_1=round(pf_gt_1_count / self.simulations * 100, 2),
            prob_pf_gt_1_3=round(pf_gt_1_3 / self.simulations * 100, 2),
            prob_dd_gt_10=round(dd_gt_10 / self.simulations * 100, 2),
            avg_net=round(float(np.mean(net_profits)), 2),
            median_net=round(float(np.median(net_profits)), 2),
            ci_95_low=round(float(np.percentile(net_profits, 2.5)), 2),
            ci_95_high=round(float(np.percentile(net_profits, 97.5)), 2),
            worst_case=round(float(np.min(net_profits)), 2),
            best_case=round(float(np.max(net_profits)), 2),
        )

    def summary(self, result: MonteCarloResult) -> str:
        """Generate Monte Carlo summary."""
        lines = [
            "=== MONTE CARLO SIMULATION ===",
            f"Trades: {result.total_trades}  Simulations: {result.simulations:,}",
            "",
            f"Probability of Profit (Net > 0):    {result.prob_profitable:.1f}%",
            f"Probability of PF > 1.0:            {result.prob_pf_gt_1:.1f}%",
            f"Probability of PF > 1.30:           {result.prob_pf_gt_1_3:.1f}%",
            f"Probability of DD > 10%:            {result.prob_dd_gt_10:.1f}%",
            "",
            f"Expected Net Profit:                ${result.avg_net:.2f}",
            f"Median Net Profit:                  ${result.median_net:.2f}",
            f"95% CI:                             [${result.ci_95_low:.2f}, ${result.ci_95_high:.2f}]",
            f"Best Case:                          ${result.best_case:.2f}",
            f"Worst Case:                         ${result.worst_case:.2f}",
        ]
        return "\n".join(lines)
