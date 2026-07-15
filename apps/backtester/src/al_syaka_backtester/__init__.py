"""Al-Syaka Backtester — Historical strategy testing engine."""

__version__ = "0.2.0"

from .metrics import BacktestMetrics
from .engine import BacktestEngine, BacktestConfig
from .trade import TradeRecord
from .optimizer import BacktestOptimizer, OptimizationResult

from .attribution import TradeAttributionAnalyzer, ClusterStats
from .validation import WalkForwardValidator, MonteCarloSimulator

__all__ = [
    "BacktestEngine", "BacktestConfig", "BacktestMetrics",
    "TradeRecord", "BacktestOptimizer", "OptimizationResult",
    "TradeAttributionAnalyzer", "ClusterStats",
    "WalkForwardValidator", "MonteCarloSimulator",
]
