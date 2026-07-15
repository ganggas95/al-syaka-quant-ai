"""Trade Attribution Analysis — cluster wins/losses to find root causes."""

from dataclasses import dataclass
from typing import List

from .trade import TradeRecord


@dataclass
class ClusterStats:
    """Statistics for a trade cluster."""
    dimension: str       # e.g. "regime", "session", "volatility"
    value: str           # e.g. "TRENDING", "LONDON", "HIGH"
    trades: int
    wins: int
    losses: int
    win_rate: float
    net_profit: float
    profit_factor: float
    avg_profit: float
    total_confidence: float


class TradeAttributionAnalyzer:
    """Analyze trades across multiple dimensions to find patterns."""

    def __init__(self, trades: List[TradeRecord]):
        self.closed_trades = [
            t for t in trades if t.result in ("WIN", "LOSS")
        ]

    def _cluster(self, attr: str) -> List[ClusterStats]:
        """Group closed trades by a given attribute."""
        groups: dict = {}
        for t in self.closed_trades:
            val = str(getattr(t, attr, "unknown") or "unknown")
            if val not in groups:
                groups[val] = {"trades": 0, "wins": 0, "losses": 0,
                               "profit": 0.0, "confidence": 0.0}
            groups[val]["trades"] += 1
            if t.result == "WIN":
                groups[val]["wins"] += 1
            else:
                groups[val]["losses"] += 1
            groups[val]["profit"] += t.profit
            groups[val]["confidence"] += t.confidence

        results = []
        for val, stats in sorted(groups.items()):
            n = stats["trades"]
            wr = stats["wins"] / n if n > 0 else 0
            # PF: sum of wins / sum of losses (abs)
            win_total = sum(t.profit for t in self.closed_trades
                           if str(getattr(t, attr, "")).lower() == val.lower()
                           and t.result == "WIN")
            loss_total = abs(sum(t.profit for t in self.closed_trades
                                if str(getattr(t, attr, "")).lower() == val.lower()
                                and t.result == "LOSS"))
            pf = win_total / loss_total if loss_total > 0 else 0
            avg_prof = stats["profit"] / n if n > 0 else 0
            avg_conf = stats["confidence"] / n if n > 0 else 0

            results.append(ClusterStats(
                dimension=attr, value=val,
                trades=n, wins=stats["wins"],
                losses=stats["losses"],
                win_rate=round(wr * 100, 1),
                net_profit=round(stats["profit"], 2),
                profit_factor=round(pf, 2),
                avg_profit=round(avg_prof, 2),
                total_confidence=round(avg_conf, 2),
            ))
        return results

    def by_regime(self) -> List[ClusterStats]:
        """Cluster by market regime."""
        return self._cluster("regime")

    def by_session(self) -> List[ClusterStats]:
        """Cluster by trading session."""
        return self._cluster("session")

    def by_strategy(self) -> List[ClusterStats]:
        """Cluster by strategy type."""
        return self._cluster("strategy")

    def by_exit_reason(self) -> List[ClusterStats]:
        """Cluster by exit reason."""
        return self._cluster("exit_reason")

    def by_volatility(self) -> List[ClusterStats]:
        """Cluster by volatility level."""
        return self._cluster("volatility_at_entry")

    def by_confidence_bucket(self) -> List[ClusterStats]:
        """Cluster by confidence ranges (60-70, 70-80, 80-90, 90-100)."""
        buckets = {
            "60-70%": lambda c: 60 <= c < 70,
            "70-80%": lambda c: 70 <= c < 80,
            "80-90%": lambda c: 80 <= c < 90,
            "90-100%": lambda c: c >= 90,
        }
        groups = {k: {"trades": 0, "wins": 0, "losses": 0,
                      "profit": 0.0, "confidence": 0.0}
                 for k in buckets}

        for t in self.closed_trades:
            confidence = t.confidence * 100
            for k, check_fn in buckets.items():
                if check_fn(confidence):
                    groups[k]["trades"] += 1
                    if t.result == "WIN":
                        groups[k]["wins"] += 1
                    else:
                        groups[k]["losses"] += 1
                    groups[k]["profit"] += t.profit
                    groups[k]["confidence"] += t.confidence
                    break

        results = []
        for val, stats in groups.items():
            n = stats["trades"]
            if n == 0:
                continue
            wr = stats["wins"] / n
            pf = (stats["wins"] * 100) / max(stats["losses"] * 100, 1)
            results.append(ClusterStats(
                dimension="confidence_bucket", value=val,
                trades=n, wins=stats["wins"],
                losses=stats["losses"],
                win_rate=round(wr * 100, 1),
                net_profit=round(stats["profit"], 2),
                profit_factor=round(pf, 2),
                avg_profit=round(stats["profit"] / n, 2),
                total_confidence=round(stats["confidence"] / n * 100, 2),
            ))
        return results

    def by_adx_level(self) -> List[ClusterStats]:
        """Cluster by ADX level at entry."""
        levels = {
            "Weak (ADX<20)": lambda a: a < 20,
            "Developing (20-25)": lambda a: 20 <= a < 25,
            "Strong (25-40)": lambda a: 25 <= a < 40,
            "Very Strong (40+)": lambda a: a >= 40,
        }
        groups = {k: {"trades": 0, "wins": 0, "profit": 0.0}
                 for k in levels}

        for t in self.closed_trades:
            for k, check_fn in levels.items():
                if check_fn(t.adx_at_entry):
                    groups[k]["trades"] += 1
                    if t.result == "WIN":
                        groups[k]["wins"] += 1
                    groups[k]["profit"] += t.profit
                    break

        results = []
        for val, stats in groups.items():
            n = stats["trades"]
            if n == 0:
                continue
            wr = stats["wins"] / n
            results.append(ClusterStats(
                dimension="adx_level", value=val,
                trades=n, wins=stats["wins"],
                losses=n - stats["wins"],
                win_rate=round(wr * 100, 1),
                net_profit=round(stats["profit"], 2),
                profit_factor=0.0, avg_profit=round(stats["profit"] / n, 2),
                total_confidence=0.0,
            ))
        return results

    def top_winning_patterns(self, top_n: int = 5) -> str:
        """Identify top N winning characteristics by win rate (min 5 trades)."""
        all_clusters = (
            self.by_regime() + self.by_session() + self.by_strategy()
            + self.by_volatility() + self.by_exit_reason()
            + self.by_adx_level()
        )
        valid = [c for c in all_clusters if c.trades >= 5]
        sorted_clusters = sorted(valid, key=lambda c: c.win_rate, reverse=True)

        lines = ["=== TOP WINNING PATTERNS ==="]
        lines.append(f"{'Rank':<5} {'Dimension':<18} {'Value':<20} {'Trades':<7} {'WR':<7} {'Net$':<10}")
        lines.append("-" * 70)
        for i, c in enumerate(sorted_clusters[:top_n], 1):
            lines.append(
                f"{i:<5} {c.dimension:<18} {c.value:<20} {c.trades:<7} "
                f"{c.win_rate:<7} ${c.net_profit:<8.2f}"
            )
        return "\n".join(lines)

    def top_losing_patterns(self, top_n: int = 5) -> str:
        """Identify top N losing characteristics by lowest win rate (min 5 trades)."""
        all_clusters = (
            self.by_regime() + self.by_session() + self.by_strategy()
            + self.by_volatility() + self.by_exit_reason()
            + self.by_adx_level()
        )
        valid = [c for c in all_clusters if c.trades >= 5]
        sorted_clusters = sorted(valid, key=lambda c: c.win_rate)

        lines = ["=== TOP LOSING PATTERNS ==="]
        lines.append(f"{'Rank':<5} {'Dimension':<18} {'Value':<20} {'Trades':<7} {'WR':<7} {'Net$':<10}")
        lines.append("-" * 70)
        for i, c in enumerate(sorted_clusters[:top_n], 1):
            lines.append(
                f"{i:<5} {c.dimension:<18} {c.value:<20} {c.trades:<7} "
                f"{c.win_rate:<7} ${c.net_profit:<8.2f}"
            )
        return "\n".join(lines)

    def full_report(self) -> str:
        """Generate full attribution report."""
        parts = []
        parts.append("=" * 60)
        parts.append("TRADE ATTRIBUTION ANALYSIS")
        parts.append(f"Total closed trades: {len(self.closed_trades)}")
        parts.append("=" * 60)

        for name, cluster_fn in [
            ("BY REGIME", self.by_regime),
            ("BY SESSION", self.by_session),
            ("BY STRATEGY", self.by_strategy),
            ("BY EXIT REASON", self.by_exit_reason),
            ("BY VOLATILITY", self.by_volatility),
            ("BY CONFIDENCE", self.by_confidence_bucket),
            ("BY ADX LEVEL", self.by_adx_level),
        ]:
            parts.append(f"\n--- {name} ---")
            parts.append(f"{'Value':<20} {'Trades':<7} {'WR':<7} {'PF':<7} {'Net$':<10} {'Avg$':<8}")
            for c in cluster_fn():
                parts.append(
                    f"{c.value:<20} {c.trades:<7} {c.win_rate:<7} "
                    f"{c.profit_factor:<7} ${c.net_profit:<8.2f} ${c.avg_profit:<7.2f}"
                )

        parts.append(f"\n\n{self.top_winning_patterns()}")
        parts.append(f"\n{self.top_losing_patterns()}")
        return "\n".join(parts)
