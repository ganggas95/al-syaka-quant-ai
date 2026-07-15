"""Win Rate Analyzer — Hitung win rate historis berdasarkan kondisi pasar."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class WinRateRecord:
    """Record of a single trade outcome."""
    timestamp: datetime
    signal: str  # BUY/SELL
    entry_price: float
    exit_price: float
    direction: str  # LONG/SHORT
    result: str  # WIN/LOSS
    pips: float
    conditions: dict  # kondisi indikator saat entry


class WinRateAnalyzer:
    """Menganalisis win rate historis."""

    def __init__(self):
        self.trades: list[WinRateRecord] = []

    def add_trade(self, trade: WinRateRecord):
        self.trades.append(trade)

    def overall_win_rate(self) -> float:
        if not self.trades:
            return 0.0
        wins = sum(1 for t in self.trades if t.result == "WIN")
        return wins / len(self.trades)

    def win_rate_by_session(self) -> dict:
        """Win rate berdasarkan sesi trading."""
        sessions = {"asian": [], "london": [], "us": [], "overlap": []}
        for t in self.trades:
            h = t.timestamp.hour
            if 0 <= h < 9:
                sessions["asian"].append(t)
            elif 8 <= h < 17:
                sessions["london"].append(t)
            elif 13 <= h < 22:
                sessions["us"].append(t)
            if 13 <= h < 17:
                sessions["overlap"].append(t)

        return {
            s: (sum(1 for t in ts if t.result == "WIN") / len(ts) if ts else 0)
            for s, ts in sessions.items()
        }

    def win_rate_by_signal_type(self) -> dict:
        """Win rate berdasarkan jenis sinyal."""
        signals = {}
        for t in self.trades:
            sig = t.signal
            if sig not in signals:
                signals[sig] = []
            signals[sig].append(t)
        return {
            s: (sum(1 for t in ts if t.result == "WIN") / len(ts) if ts else 0)
            for s, ts in signals.items()
        }

    def best_conditions(self) -> list[dict]:
        """Kondisi dengan win rate tertinggi."""
        # Group by conditions
        condition_groups = {}
        for t in self.trades:
            key = frozenset(t.conditions.items())
            if key not in condition_groups:
                condition_groups[key] = []
            condition_groups[key].append(t)

        results = []
        for conditions, trades in condition_groups.items():
            if len(trades) < 3:  # Minimal sample
                continue
            wr = sum(1 for t in trades if t.result == "WIN") / len(trades)
            results.append({
                "conditions": dict(conditions),
                "win_rate": wr,
                "total_trades": len(trades),
            })

        return sorted(results, key=lambda x: x["win_rate"], reverse=True)[:5]
