"""Signal Performance Tracking — Track signal vs outcome, confusion matrix."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from collections import defaultdict


@dataclass
class SignalOutcome:
    """Track a signal and its actual outcome."""
    signal_id: str
    timestamp: datetime
    symbol: str
    signal: str  # BUY/SELL
    confidence: float
    predicted_direction: str
    actual_outcome: str  # WIN, LOSS, PENDING
    profit: float = 0.0
    reasons: list[str] = field(default_factory=list)


class SignalTracker:
    """Track every signal generated vs actual market outcome."""

    def __init__(self):
        self.signals: list[SignalOutcome] = []
        self._next_id = 1

    def record_signal(self, symbol: str, signal: str, confidence: float,
                      reasons: Optional[list[str]] = None) -> SignalOutcome:
        """Record a new signal."""
        sig_id = f"SIG-{self._next_id:06d}"
        self._next_id += 1

        outcome = SignalOutcome(
            signal_id=sig_id,
            timestamp=datetime.utcnow(),
            symbol=symbol,
            signal=signal,
            confidence=confidence,
            predicted_direction="LONG" if signal == "BUY" else "SHORT",
            actual_outcome="PENDING",
            reasons=reasons or [],
        )
        self.signals.append(outcome)
        return outcome

    def resolve_signal(self, signal_id: str, profit: float):
        """Mark a signal as WIN or LOSS based on actual profit."""
        for sig in self.signals:
            if sig.signal_id == signal_id and sig.actual_outcome == "PENDING":
                sig.actual_outcome = "WIN" if profit > 0 else "LOSS"
                sig.profit = profit
                break

    def confusion_matrix(self) -> dict:
        """Calculate confusion matrix: predicted vs actual."""
        resolved = [s for s in self.signals if s.actual_outcome != "PENDING"]
        if not resolved:
            return {}

        # Predicted BUY → actual WIN/LOSS
        tp = sum(1 for s in resolved if s.signal == "BUY" and s.actual_outcome == "WIN")
        fp = sum(1 for s in resolved if s.signal == "BUY" and s.actual_outcome == "LOSS")
        tn = sum(1 for s in resolved if s.signal == "SELL" and s.actual_outcome == "WIN")
        fn = sum(1 for s in resolved if s.signal == "SELL" and s.actual_outcome == "LOSS")

        total = tp + tn + fp + fn
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

        return {
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "total_signals": total,
            "accuracy": round(accuracy * 100, 1),
            "precision": round(precision * 100, 1),
            "recall": round(recall * 100, 1),
            "f1_score": round(f1 * 100, 1),
        }

    def accuracy_by_confidence_bucket(self) -> dict:
        """Analyze accuracy by confidence level."""
        buckets = {
            "90-100%": {"count": 0, "correct": 0},
            "80-89%": {"count": 0, "correct": 0},
            "70-79%": {"count": 0, "correct": 0},
            "60-69%": {"count": 0, "correct": 0},
            "50-59%": {"count": 0, "correct": 0},
        }

        for s in self.signals:
            if s.actual_outcome == "PENDING":
                continue
            conf = s.confidence
            bucket = None
            if conf >= 90:
                bucket = "90-100%"
            elif conf >= 80:
                bucket = "80-89%"
            elif conf >= 70:
                bucket = "70-79%"
            elif conf >= 60:
                bucket = "60-69%"
            elif conf >= 50:
                bucket = "50-59%"

            if bucket and bucket in buckets:
                buckets[bucket]["count"] += 1
                if s.actual_outcome == "WIN":
                    buckets[bucket]["correct"] += 1

        return {
            bucket: {
                "total": stats["count"],
                "accuracy": round(stats["correct"] / stats["count"] * 100, 1) if stats["count"] > 0 else 0,
            }
            for bucket, stats in buckets.items()
        }

    def summary(self) -> dict:
        """Get signal tracking summary."""
        resolved = [s for s in self.signals if s.actual_outcome != "PENDING"]
        return {
            "total_signals": len(self.signals),
            "resolved_signals": len(resolved),
            "pending_signals": len(self.signals) - len(resolved),
            "confusion_matrix": self.confusion_matrix(),
            "accuracy_by_confidence": self.accuracy_by_confidence_bucket(),
        }
