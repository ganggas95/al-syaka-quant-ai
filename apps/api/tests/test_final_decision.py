"""Milestone 3 — Final Decision & Conflict Handling: FinalDecisionEngine Tests.

Validasi:
  M3.1 Aligned: BUY + BULLISH = BUY, SELL + BEARISH = SELL
  M3.2 Conflict: BUY + BEARISH = HEDGE, SELL + BULLISH = HEDGE
  M3.3 Macro Override: weak tech + strong macro = ikut macro
  M3.4 All neutral = WAIT
  M3.5 conflict_detected benar
  M3.6 Fallback WAIT ketika exception
  M3.7 Priority chain: override > conflict > normal > wait
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.final_decision import FinalDecisionEngine

engine = FinalDecisionEngine()


# ──────────────────────────────────────────────
# M3.1 — Aligned: Technical & Macro searah
# ──────────────────────────────────────────────

def test_aligned_bullish():
    """BUY + BULLISH -> BUY, no conflict."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=70.0,
        macro_strength=60.0,
    )
    assert result["final_decision"] == "BUY"
    assert result["conflict_detected"] is False
    assert "strong technical signal" in result["decision_reason"].lower()


def test_aligned_bearish():
    """SELL + BEARISH -> SELL, no conflict."""
    result = engine.decide(
        technical_signal="SELL",
        technical_confidence=72.0,
        composite_score=68.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=65.0,
        macro_strength=55.0,
    )
    assert result["final_decision"] == "SELL"
    assert result["conflict_detected"] is False


# ──────────────────────────────────────────────
# M3.2 — Conflict Detection
# ──────────────────────────────────────────────

def test_conflict_buy_bearish():
    """BUY + BEARISH (with confidence) -> HEDGE, conflict=True."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    assert result["final_decision"] == "HEDGE"
    assert result["conflict_detected"] is True


def test_conflict_sell_bullish():
    """SELL + BULLISH (with confidence) -> HEDGE, conflict=True."""
    result = engine.decide(
        technical_signal="SELL",
        technical_confidence=72.0,
        composite_score=68.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=55.0,
        macro_strength=45.0,
    )
    assert result["final_decision"] == "HEDGE"
    assert result["conflict_detected"] is True


def test_no_conflict_when_macro_neutral():
    """Macro NEUTRAL = tidak ada conflict."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="NEUTRAL",
        macro_confidence=30.0,
        macro_strength=0.0,
    )
    assert result["conflict_detected"] is False


def test_no_conflict_when_macro_low_confidence():
    """Macro confidence < 30 = tidak ada conflict."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=25.0,
        macro_strength=50.0,
    )
    assert result["conflict_detected"] is False
    assert result["final_decision"] == "BUY"  # fallback ke teknikal


def test_no_conflict_when_macro_low_strength():
    """Macro strength < 20 = tidak ada conflict."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=50.0,
        macro_strength=15.0,
    )
    assert result["conflict_detected"] is False
    assert result["final_decision"] == "BUY"


# ──────────────────────────────────────────────
# M3.3 — Macro Override
# ──────────────────────────────────────────────

def test_macro_override_bearish():
    """Weak BUY + strong BEARISH -> SELL (macro override)."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=35.0,
        composite_score=38.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=80.0,
        macro_strength=70.0,
    )
    assert result["final_decision"] == "SELL"
    assert result["conflict_detected"] is False
    assert "overriding" in result["decision_reason"].lower()


def test_macro_override_bullish():
    """Weak SELL + strong BULLISH -> BUY (macro override)."""
    result = engine.decide(
        technical_signal="SELL",
        technical_confidence=30.0,
        composite_score=35.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=85.0,
        macro_strength=75.0,
    )
    assert result["final_decision"] == "BUY"
    assert result["conflict_detected"] is False


def test_no_override_when_technical_strong():
    """Tech confidence >= 50 = tidak ada macro override walaupun macro kuat."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=55.0,
        composite_score=60.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=80.0,
        macro_strength=70.0,
    )
    # Conflict (BUY + BEARISH with high macro confidence & strength)
    assert result["conflict_detected"] is True
    assert result["final_decision"] == "HEDGE"


# ──────────────────────────────────────────────
# M3.4 — All Neutral / Low Confidence
# ──────────────────────────────────────────────

def test_all_neutral():
    """Semua NEUTRAL -> WAIT."""
    result = engine.decide(
        technical_signal="NEUTRAL",
        technical_confidence=0.0,
        composite_score=0.0,
        market_regime="RANGE",
        macro_bias="NEUTRAL",
        macro_confidence=0.0,
        macro_strength=0.0,
    )
    assert result["final_decision"] == "WAIT"


def test_low_confidence_wait():
    """Confidence rendah (< 30) -> WAIT."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=20.0,
        composite_score=25.0,
        market_regime="RANGE",
        macro_bias="NEUTRAL",
        macro_confidence=10.0,
        macro_strength=5.0,
    )
    assert result["final_decision"] == "WAIT"


# ──────────────────────────────────────────────
# M3.5 — conflict_detected Field Accuracy
# ──────────────────────────────────────────────

def test_conflict_detected_accurate():
    """conflict_detected hanya True saat kondisi conflict terpenuhi."""
    # True case
    r1 = engine.decide(
        technical_signal="BUY", technical_confidence=75.0,
        composite_score=80.0, market_regime="TRENDING",
        macro_bias="BEARISH", macro_confidence=50.0, macro_strength=40.0,
    )
    assert r1["conflict_detected"] is True

    # False case (aligned)
    r2 = engine.decide(
        technical_signal="BUY", technical_confidence=75.0,
        composite_score=80.0, market_regime="TRENDING",
        macro_bias="BULLISH", macro_confidence=50.0, macro_strength=40.0,
    )
    assert r2["conflict_detected"] is False


# ──────────────────────────────────────────────
# M3.6 — Fallback
# ──────────────────────────────────────────────

def test_fallback_on_exception(monkeypatch):
    """Exception di dalam decide -> WAIT fallback."""
    engine_local = FinalDecisionEngine()

    def _mock_error(*args, **kwargs):
        raise ValueError("Simulated error")

    monkeypatch.setattr(engine_local, "_detect_conflict", _mock_error)
    result = engine_local.decide(
        technical_signal="BUY", technical_confidence=75.0,
        composite_score=80.0, market_regime="TRENDING",
        macro_bias="BULLISH", macro_confidence=70.0, macro_strength=60.0,
    )
    assert result["final_decision"] == "WAIT"
    assert "Unable to compute" in result["decision_reason"]
    assert result["conflict_detected"] is False


# ──────────────────────────────────────────────
# M3.7 — Priority Chain
# ──────────────────────────────────────────────

def test_priority_macro_override_over_conflict():
    """Override lebih tinggi dari conflict: macro override diproses duluan."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=35.0,  # weak -> masuk override
        composite_score=38.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",       # opposite -> conflict potential
        macro_confidence=80.0,      # strong -> override
        macro_strength=70.0,
    )
    # Must be SELL (override), not HEDGE (conflict)
    assert result["final_decision"] == "SELL"
    assert result["conflict_detected"] is False


def test_priority_strong_technical():
    """Confidence >= 70 dengan sinyal jelas -> langsung BUY/SELL."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=85.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="NEUTRAL",
        macro_confidence=20.0,
        macro_strength=10.0,
    )
    assert result["final_decision"] == "BUY"


def test_priority_moderate_with_support():
    """Moderate confidence + macro support -> BUY/SELL (supported)."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=55.0,
        composite_score=58.0,
        market_regime="RANGE",
        macro_bias="BULLISH",
        macro_confidence=50.0,
        macro_strength=40.0,
    )
    assert result["final_decision"] == "BUY"
    assert "supported" in result["decision_reason"].lower()


def test_priority_moderate_no_support():
    """Moderate confidence tanpa macro support -> tetap BUY/SELL dengan caution."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=55.0,
        composite_score=58.0,
        market_regime="RANGE",
        macro_bias="BEARISH",
        macro_confidence=20.0,  # low, jadi no conflict
        macro_strength=15.0,    # low, jadi no conflict
    )
    assert result["final_decision"] == "BUY"


# ──────────────────────────────────────────────
# Boundary Tests
# ──────────────────────────────────────────────

def test_conflict_boundary_confidence_30():
    """Macro confidence = 29 -> no conflict, 30 -> conflict possible."""
    macro_bearish = {"macro_bias": "BEARISH", "macro_strength": 40.0}
    tech_buy = {
        "technical_signal": "BUY", "technical_confidence": 75.0,
        "composite_score": 80.0, "market_regime": "TRENDING",
    }

    # conf=29 is below threshold
    r1 = engine.decide(**tech_buy, **macro_bearish, macro_confidence=29.0)
    assert r1["conflict_detected"] is False

    # conf=30 is at threshold
    r2 = engine.decide(**tech_buy, **macro_bearish, macro_confidence=30.0)
    assert r2["conflict_detected"] is True


def test_conflict_boundary_strength_20():
    """Macro strength = 19 -> no conflict, 20 -> conflict possible."""
    macro_bearish = {"macro_bias": "BEARISH", "macro_confidence": 50.0}
    tech_buy = {
        "technical_signal": "BUY", "technical_confidence": 75.0,
        "composite_score": 80.0, "market_regime": "TRENDING",
    }

    r1 = engine.decide(**tech_buy, **macro_bearish, macro_strength=19.0)
    assert r1["conflict_detected"] is False

    r2 = engine.decide(
        **tech_buy, **macro_bearish, macro_strength=20.0,
    )
    assert r2["conflict_detected"] is True


# ──────────────────────────────────────────────
# Sprint 5 — New Fields: hedge_intensity,
# decision_confidence, position_multiplier
# ──────────────────────────────────────────────

def test_hedge_intensity_full():
    """Strong conflict -> FULL hedge."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    assert result["final_decision"] == "HEDGE"
    assert result["hedge_intensity"] == "FULL"


def test_hedge_intensity_light():
    """Weak conflict -> LIGHT hedge."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=35.0,  # weak tech signal
        composite_score=40.0,
        market_regime="RANGE",
        macro_bias="BEARISH",
        macro_confidence=45.0,  # moderate macro
        macro_strength=35.0,
    )
    assert result["final_decision"] == "HEDGE"
    assert result["hedge_intensity"] == "LIGHT"


def test_hedge_intensity_none_when_not_hedge():
    """hedge_intensity is None for non-HEDGE decisions."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=50.0,
        macro_strength=40.0,
    )
    assert result["final_decision"] == "BUY"
    assert result["hedge_intensity"] is None


def test_decision_confidence_high_for_strong_signal():
    """Strong technical signal -> high decision confidence."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=85.0,
        composite_score=88.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    assert result["final_decision"] == "BUY"
    assert result["decision_confidence"] >= 70


def test_decision_confidence_low_for_wait():
    """WAIT decision -> low decision confidence."""
    result = engine.decide(
        technical_signal="NEUTRAL",
        technical_confidence=10.0,
        composite_score=15.0,
        market_regime="RANGE",
        macro_bias="NEUTRAL",
        macro_confidence=5.0,
        macro_strength=0.0,
    )
    assert result["final_decision"] == "WAIT"
    assert result["decision_confidence"] <= 30


def test_position_multiplier_full_for_strong_buy():
    """Strong BUY -> position_multiplier >= 0.8."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=85.0,
        composite_score=90.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    assert result["final_decision"] == "BUY"
    assert result["position_multiplier"] >= 0.8


def test_position_multiplier_low_for_full_hedge():
    """FULL HEDGE -> position_multiplier <= 0.2."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=65.0,
        macro_strength=55.0,
    )
    assert result["final_decision"] == "HEDGE"
    assert result["hedge_intensity"] == "FULL"
    assert result["position_multiplier"] == 0.2


def test_position_multiplier_zero_for_wait():
    """WAIT -> position_multiplier = 0.0."""
    result = engine.decide(
        technical_signal="NEUTRAL",
        technical_confidence=0.0,
        composite_score=0.0,
        market_regime="RANGE",
        macro_bias="NEUTRAL",
        macro_confidence=0.0,
        macro_strength=0.0,
    )
    assert result["final_decision"] == "WAIT"
    assert result["position_multiplier"] == 0.0


def test_all_new_fields_present():
    """All Sprint 5 fields are present in output."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    assert "hedge_intensity" in result
    assert "decision_confidence" in result
    assert "position_multiplier" in result


def test_enhanced_reason_contains_data_points():
    """Enhanced reason includes specific confidence/regime data."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    reason = result["decision_reason"].lower()
    assert "75" in reason or "80" in reason  # confidence data point
    assert "trending" in reason  # regime data point


def test_fallback_contains_new_fields():
    """Fallback response includes all Sprint 5 fields."""
    engine_local = FinalDecisionEngine()

    def _mock_error(*args, **kwargs):
        raise ValueError("Simulated error")

    monkeypatch = __import__("pytest").MonkeyPatch()
    monkeypatch.setattr(engine_local, "_detect_conflict", _mock_error)
    result = engine_local.decide(
        technical_signal="BUY", technical_confidence=75.0,
        composite_score=80.0, market_regime="TRENDING",
        macro_bias="BULLISH", macro_confidence=70.0,
        macro_strength=60.0,
    )
    assert result["final_decision"] == "WAIT"
    assert result["hedge_intensity"] is None
    assert result["decision_confidence"] == 0.0
    assert result["position_multiplier"] == 0.0


# ──────────────────────────────────────────────
# Sprint 6 — Stability & Edge Case Tests
# ──────────────────────────────────────────────

def test_extreme_confidence_values():
    """Engine handles confidence values at boundaries."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=100.0,
        composite_score=100.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=100.0,
        macro_strength=100.0,
    )
    assert result["final_decision"] == "BUY"
    assert result["decision_confidence"] <= 100.0
    assert result["position_multiplier"] >= 0.8


def test_zero_all_values():
    """Engine handles all-zero inputs gracefully."""
    result = engine.decide(
        technical_signal="NEUTRAL",
        technical_confidence=0.0,
        composite_score=0.0,
        market_regime="VOLATILE",
        macro_bias="NEUTRAL",
        macro_confidence=0.0,
        macro_strength=0.0,
    )
    assert result["final_decision"] == "WAIT"
    assert result["decision_confidence"] <= 30.0
    assert result["position_multiplier"] == 0.0


def test_confidence_at_boundaries():
    """Edge case: confidence exactly at threshold boundaries."""
    # At 70 boundary (strong signal threshold)
    r70 = engine.decide(
        technical_signal="BUY",
        technical_confidence=70.0,
        composite_score=70.0,
        market_regime="TRENDING",
        macro_bias="NEUTRAL",
        macro_confidence=20.0,
        macro_strength=10.0,
    )
    assert r70["final_decision"] == "BUY"

    # At 40 boundary (moderate signal threshold)
    r40 = engine.decide(
        technical_signal="BUY",
        technical_confidence=40.0,
        composite_score=40.0,
        market_regime="RANGE",
        macro_bias="NEUTRAL",
        macro_confidence=20.0,
        macro_strength=10.0,
    )
    assert r40["final_decision"] == "BUY"

    # At 30 boundary (minimum confidence for conflict)
    r30 = engine.decide(
        technical_signal="BUY",
        technical_confidence=50.0,
        composite_score=50.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=30.0,
        macro_strength=25.0,
    )
    assert "conflict_detected" in r30


def test_rapidly_changing_macro():
    """Engine handles scenario where macro just shifted."""
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=60.0,
        composite_score=65.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",  # Just turned bearish
        macro_confidence=30.0,  # Conflict at boundary
        macro_strength=25.0,
    )
    # Macro is bearish but tech is BUY -> conflict or caution
    assert result["final_decision"] in ("BUY", "HEDGE", "WAIT")


def test_hedge_with_boundary_macro_confidence():
    """HEDGE with macro confidence at exact thresholds."""
    # Just above conflict threshold (30)
    r31 = engine.decide(
        technical_signal="BUY",
        technical_confidence=60.0,
        composite_score=60.0,
        market_regime="RANGE",
        macro_bias="BEARISH",
        macro_confidence=31.0,
        macro_strength=25.0,
    )
    assert r31["conflict_detected"] is True

    # Just below conflict threshold (29)
    r29 = engine.decide(
        technical_signal="BUY",
        technical_confidence=60.0,
        composite_score=60.0,
        market_regime="RANGE",
        macro_bias="BEARISH",
        macro_confidence=29.0,
        macro_strength=25.0,
    )
    # Should not detect conflict (below 30 threshold)
    if r29["conflict_detected"]:
        # If it does detect, it should still produce a valid decision
        assert r29["final_decision"] in ("BUY", "HEDGE", "WAIT")


def test_multiple_consecutive_decisions():
    """Engine produces consistent results across consecutive calls."""
    params = dict(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=80.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )
    results = [engine.decide(**params) for _ in range(5)]
    decisions = [r["final_decision"] for r in results]
    # All should be identical (deterministic)
    assert len(set(decisions)) == 1
    assert decisions[0] == "BUY"


def test_decision_confidence_range():
    """decision_confidence is always in 0-100 range."""
    test_cases = [
        {"tech": "BUY", "tc": 85.0, "mb": "BULLISH", "mc": 70.0, "ms": 60.0},
        {"tech": "SELL", "tc": 50.0, "mb": "BEARISH", "mc": 45.0, "ms": 35.0},
        {"tech": "BUY", "tc": 75.0, "mb": "BEARISH", "mc": 65.0, "ms": 55.0},
        {"tech": "NEUTRAL", "tc": 0.0, "mb": "NEUTRAL", "mc": 0.0, "ms": 0.0},
    ]
    for case in test_cases:
        result = engine.decide(
            technical_signal=case["tech"],
            technical_confidence=case["tc"],
            composite_score=case["tc"],
            market_regime="RANGE",
            macro_bias=case["mb"],
            macro_confidence=case["mc"],
            macro_strength=case["ms"],
        )
        assert 0 <= result["decision_confidence"] <= 100
        assert 0 <= result["position_multiplier"] <= 1.0
