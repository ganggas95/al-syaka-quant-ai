"""Backtest Optimizer — Grid search for optimal strategy parameters."""

from dataclasses import dataclass, replace
from typing import Callable, Optional

import pandas as pd

from .engine import BacktestConfig, BacktestEngine
from .metrics import BacktestMetrics


@dataclass
class OptimizationResult:
    """Single optimization run result."""
    params: dict
    metrics: BacktestMetrics
    total_trades: int
    profit_factor: float
    win_rate: float
    net_profit: float
    max_drawdown_pct: float
    sharpe_ratio: float
    expectancy: float


class BacktestOptimizer:
    """Grid search optimizer for backtest parameters."""

    def __init__(self, data_fetcher: Callable[[], pd.DataFrame],
                 base_config: BacktestConfig):
        self.data_fetcher = data_fetcher
        self.base_config = base_config
        self.results: list[OptimizationResult] = []

    def _run_single(self, config: BacktestConfig) -> OptimizationResult:
        """Run a single backtest with given config."""
        df = self.data_fetcher()
        engine = BacktestEngine(config)
        metrics = engine.run(df)

        total = metrics.total_trades
        expectancy = metrics.avg_profit_per_trade if total > 0 else 0.0

        return OptimizationResult(
            params={
                "atr_sl": config.atr_sl_multiplier,
                "atr_tp": config.atr_tp_multiplier,
                "confidence": config.min_confidence,
                "mean_rev_sl": config.mean_rev_sl_multiplier,
                "mean_rev_tp": config.mean_rev_tp_multiplier,
                "breakout_sl": config.breakout_sl_multiplier,
                "breakout_tp": config.breakout_tp_multiplier,
                "rr_ratio": round(
                    config.atr_tp_multiplier
                    / config.atr_sl_multiplier, 2
                ),
            },
            metrics=metrics,
            total_trades=total,
            profit_factor=round(metrics.profit_factor, 4),
            win_rate=round(metrics.win_rate * 100, 2),
            net_profit=round(metrics.net_profit, 2),
            max_drawdown_pct=round(metrics.max_drawdown_percent, 2),
            sharpe_ratio=round(metrics.sharpe_ratio, 4),
            expectancy=round(expectancy, 2),
        )

    def optimize_rr(self) -> list[OptimizationResult]:
        """Optimize RR — test SL (1.0,1.5,2.0) x TP (1.0,1.5,2.0,2.5,3.0,4.0)."""
        self.results = []
        sl_values = [1.0, 1.5, 2.0]
        tp_values = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0]

        for sl_mult in sl_values:
            for tp_mult in tp_values:
                config = replace(
                    self.base_config,
                    atr_sl_multiplier=sl_mult,
                    atr_tp_multiplier=tp_mult,
                    mean_rev_sl_multiplier=max(0.5, sl_mult * 0.7),
                    mean_rev_tp_multiplier=tp_mult * 0.7,
                    breakout_sl_multiplier=sl_mult * 1.3,
                    breakout_tp_multiplier=tp_mult,
                )
                result = self._run_single(config)
                self.results.append(result)

        self.results.sort(key=lambda r: r.profit_factor, reverse=True)
        return self.results

    def optimize_atr_sl(self) -> list[OptimizationResult]:
        """Optimize ATR SL — test SL: 0.8, 1.0, 1.2, 1.5, 2.0, 2.5 (TP=3.0)."""
        self.results = []
        sl_values = [0.8, 1.0, 1.2, 1.5, 2.0, 2.5]

        for sl_mult in sl_values:
            config = replace(
                self.base_config,
                atr_sl_multiplier=sl_mult,
                atr_tp_multiplier=3.0,
                mean_rev_sl_multiplier=max(0.5, sl_mult * 0.7),
                mean_rev_tp_multiplier=2.0,
                breakout_sl_multiplier=sl_mult * 1.3,
                breakout_tp_multiplier=3.0,
            )
            result = self._run_single(config)
            self.results.append(result)

        self.results.sort(key=lambda r: r.profit_factor, reverse=True)
        return self.results

    def optimize_confidence(self) -> list[OptimizationResult]:
        """Optimize confidence — test thresholds: 0.50-0.80."""
        self.results = []
        conf_values = [0.50, 0.55, 0.60, 0.65, 0.70, 0.80]

        for conf in conf_values:
            config = replace(self.base_config, min_confidence=conf)
            result = self._run_single(config)
            self.results.append(result)

        self.results.sort(key=lambda r: r.profit_factor, reverse=True)
        return self.results

    def optimize_all_params(self) -> list[OptimizationResult]:
        """Run full optimization — all RR + confidence combos."""
        self.results = []
        sl_values = [1.0, 1.5, 2.0]
        tp_values = [1.0, 1.5, 2.0, 2.5, 3.0]
        conf_values = [0.50, 0.60, 0.70]

        for sl_mult in sl_values:
            for tp_mult in tp_values:
                for conf in conf_values:
                    config = replace(
                        self.base_config,
                        atr_sl_multiplier=sl_mult,
                        atr_tp_multiplier=tp_mult,
                        min_confidence=conf,
                        mean_rev_sl_multiplier=max(0.5, sl_mult * 0.7),
                        mean_rev_tp_multiplier=tp_mult * 0.7,
                        breakout_sl_multiplier=sl_mult * 1.3,
                        breakout_tp_multiplier=tp_mult,
                    )
                    result = self._run_single(config)
                    self.results.append(result)

        self.results.sort(key=lambda r: r.profit_factor, reverse=True)
        return self.results

    def summary_table(self, top_n: int = 10) -> str:
        """Generate a formatted summary table of top results."""
        if not self.results:
            return "No results yet."

        header = (
            f"{'Rank':<5} {'SL':<6} {'TP':<6} {'RR':<6} {'Conf':<6} "
            f"{'Trades':<7} {'PF':<8} {'Win%':<7} {'Net$':<10} "
            f"{'DD%':<7} {'Sharpe':<8} {'Expect':<8}"
        )
        sep = "-" * 85
        lines = [header, sep]

        for rank, r in enumerate(self.results[:top_n], 1):
            pf_str = (
                f"{r.profit_factor:.2f}"
                if r.profit_factor != float('inf') else "INF"
            )
            sl = r.params.get("atr_sl", self.base_config.atr_sl_multiplier)
            tp = r.params.get("atr_tp", self.base_config.atr_tp_multiplier)
            conf = r.params.get(
                "confidence", self.base_config.min_confidence
            )
            rr = r.params.get(
                "rr_ratio", round(tp / sl, 2)
            )
            lines.append(
                f"{rank:<5} {sl:<6} {tp:<6} {rr:<6} {conf:<6} "
                f"{r.total_trades:<7} {pf_str:<8} {r.win_rate:<7} "
                f"{r.net_profit:<10} {r.max_drawdown_pct:<7} "
                f"{r.sharpe_ratio:<8} {r.expectancy:<8}"
            )

        return "\n".join(lines)

    def best_result(
        self, metric: str = "profit_factor", min_trades: int = 30
    ) -> Optional[OptimizationResult]:
        """Get the best result by a given metric."""
        if not self.results:
            return None
        metric_map = {
            "profit_factor": lambda r: (
                r.profit_factor if r.profit_factor != float('inf') else 0
            ),
            "sharpe": lambda r: r.sharpe_ratio,
            "net_profit": lambda r: r.net_profit,
            "expectancy": lambda r: r.expectancy,
        }
        key_fn = metric_map.get(metric, metric_map["profit_factor"])
        valid = [r for r in self.results if r.total_trades >= min_trades]
        if not valid:
            valid = self.results
        return max(valid, key=key_fn)
