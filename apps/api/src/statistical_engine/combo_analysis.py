"""Combo Analyzer — Analisis kombinasi indikator yang paling akurat."""

from dataclasses import dataclass
from itertools import combinations
from typing import Optional


@dataclass
class ComboResult:
    """Hasil analisis kombinasi indikator."""
    indicators: list[str]
    win_rate: float
    total_signals: int
    avg_confidence: float


class ComboAnalyzer:
    """Menganalisis kombinasi indikator mana yang paling sering akurat."""

    def __init__(self):
        self.combinations: list[ComboResult] = []

    def analyze(self, indicators_present: list[str], win_rate: float, confidence: float):
        """Catat kombinasi indikator yang aktif saat sinyal."""
        # Analyze pairs and triples
        for r in range(2, min(4, len(indicators_present) + 1)):
            for combo in combinations(indicators_present, r):
                self.combinations.append(ComboResult(
                    indicators=list(combo),
                    win_rate=win_rate,
                    total_signals=1,
                    avg_confidence=confidence,
                ))

    def best_combos(self, top_n: int = 5) -> list[ComboResult]:
        """Kombinasi dengan win rate tertinggi (min 5 sampel)."""
        # Aggregate
        grouped = {}
        for c in self.combinations:
            key = tuple(sorted(c.indicators))
            if key not in grouped:
                grouped[key] = {"win_rate": 0, "count": 0, "confidence": 0}
            grouped[key]["win_rate"] += c.win_rate
            grouped[key]["count"] += c.total_signals
            grouped[key]["confidence"] += c.avg_confidence

        results = []
        for key, val in grouped.items():
            if val["count"] >= 5:
                results.append(ComboResult(
                    indicators=list(key),
                    win_rate=val["win_rate"] / val["count"],
                    total_signals=val["count"],
                    avg_confidence=val["confidence"] / val["count"],
                ))

        return sorted(results, key=lambda x: x.win_rate, reverse=True)[:top_n]
