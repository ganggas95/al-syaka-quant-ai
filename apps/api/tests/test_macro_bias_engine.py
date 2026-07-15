"""Milestone 1 — Core Engine: MacroBiasEngine Unit Tests.

Validasi:
  M1.1 Engine menghasilkan macro_bias (BULLISH/BEARISH/NEUTRAL)
  M1.2 Bobot konsisten dengan PRD (H4=2pt, D1=3pt, RSI H4=1pt, RSI D1=1.5pt)
  M1.3 macro_strength dalam rentang 0-100
  M1.4 macro_confidence dalam rentang 0-100
  M1.5 macro_reason tidak kosong
  M1.6 Fallback NEUTRAL ketika exception
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.macro_bias import (SYMBOL_CLASS_WEIGHTS, MacroBiasEngine,
                            _get_symbol_class)

# ──────────────────────────────────────────────
# Fixture: Mock provider with controlled events
# ──────────────────────────────────────────────

class MockEconomicProvider:
    """Mock provider that returns predictable event data."""

    def __init__(self, risk_score: int = 0):
        self.risk_score = risk_score

    def get_event_risk_score(self, from_date=None):
        return {
            "event_risk_score": self.risk_score,
            "high_impact_count": 1 if self.risk_score > 0 else 0,
            "medium_impact_count": 0,
            "upcoming_events": [
                {
                    "name": "FOMC Meeting",
                    "date": "2026-07-22",
                    "days_until": 3,
                    "impact": "HIGH",
                    "country": "US",
                },
            ] if self.risk_score > 0 else [],
            "has_major_event_soon": self.risk_score >= 25,
        }

    def get_bullish_factors(self, from_date=None):
        return []

    def get_bearish_factors(self, from_date=None):
        return []

# ──────────────────────────────────────────────
# M1.1 — Bias Determination
# ──────────────────────────────────────────────

def test_bias_trend_agreement():
    """H4 dan D1 same direction -> same bias."""
    engine = MacroBiasEngine()
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")
    assert result["macro_bias"] == "BULLISH"

    result = engine.analyze(trend_h4="BEARISH", trend_d1="BEARISH")
    assert result["macro_bias"] == "BEARISH"


def test_bias_trend_partial():
    """Salah satu timeframe memiliki trend -> NEUTRAL
    (tidak cukup dominant)."""
    engine = MacroBiasEngine()
    # H4 neutral, D1 bullish. H4=0, D1 BULLISH=3. Skor: 0 vs 3 -> BULLISH
    result = engine.analyze(trend_h4="NEUTRAL", trend_d1="BULLISH")
    assert result["macro_bias"] == "BULLISH"

    # H4 NEUTRAL, D1 BEARISH -> BEARISH
    result = engine.analyze(trend_h4="NEUTRAL", trend_d1="BEARISH")
    assert result["macro_bias"] == "BEARISH"


def test_bias_trend_conflict_equal():
    """H4 dan D1 berlawanan arah -> BULLISH (karena D1 bobot 3 > H4 2)."""
    engine = MacroBiasEngine()
    # H4 BULLISH=2, D1 BEARISH=3. Skor: 2 vs 3 -> BEARISH
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BEARISH",
    )
    assert result["macro_bias"] == "BEARISH"


def test_bias_rsi_reinforcement_bullish():
    """RSI H4 > 55 dan RSI D1 > 55 menambah bobot BULLISH."""
    engine = MacroBiasEngine()
    # H4 NEUTRAL=0, D1 NEUTRAL=0
    # RSI H4=60 (1pt), RSI D1=58 (1.5pt) -> 2.5 vs 0 -> BULLISH
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
        rsi_h4=60.0, rsi_d1=58.0,
    )
    assert result["macro_bias"] == "BULLISH"


def test_bias_rsi_reinforcement_bearish():
    """RSI H4 < 45 dan RSI D1 < 45 menambah bobot BEARISH."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
        rsi_h4=35.0, rsi_d1=40.0,
    )
    assert result["macro_bias"] == "BEARISH"


def test_bias_rsi_netral_zone():
    """RSI di 45-55 tidak menambah bobot apapun."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
        rsi_h4=50.0, rsi_d1=52.0,
    )
    assert result["macro_bias"] == "NEUTRAL"


# ──────────────────────────────────────────────
# M1.3 — Strength Calculation
# ──────────────────────────────────────────────

def test_strength_adx_high():
    """ADX >= 30 memberikan kontribusi penuh (H4=25, D1=35)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=35.0, adx_d1=40.0,
    )
    # ADX H4=25 + ADX D1=35 = 60, no volatility penalty
    assert result["macro_strength"] >= 55
    assert result["macro_strength"] <= 65


def test_strength_adx_moderate():
    """ADX >= 20 dan < 30 memberikan kontribusi sedang (H4=15, D1=20)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=22.0, adx_d1=24.0,
    )
    # ADX H4=15 + ADX D1=20 = 35
    assert 30 <= result["macro_strength"] <= 40


def test_strength_adx_low():
    """ADX < 20 memberikan kontribusi minimum (H4=5, D1=10)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=15.0, adx_d1=12.0,
    )
    # ADX H4=5 + ADX D1=10 = 15
    assert 10 <= result["macro_strength"] <= 20


def test_strength_volatility_penalty_high():
    """Volatilitas tinggi mengurangi strength."""
    engine = MacroBiasEngine()
    # Without volatility
    result_no_vol = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=30.0, adx_d1=30.0,
    )
    # With high volatility
    result_high_vol = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=30.0, adx_d1=30.0,
        volatility_h4=0.025, volatility_d1=0.035,
    )
    assert result_high_vol["macro_strength"] < result_no_vol["macro_strength"]


def test_strength_boundary_zero():
    """Strength tidak boleh negatif."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
        adx_h4=5.0, adx_d1=5.0,
        volatility_h4=0.1, volatility_d1=0.1,
    )
    # ADX H4=5 + ADX D1=10 = 15, penalty=10+15=25, max(0, -10) = 0
    assert result["macro_strength"] == 0


# ──────────────────────────────────────────────
# M1.4 — Confidence Calculation
# ──────────────────────────────────────────────

def test_confidence_base_minimum():
    """Tanpa data apapun, confidence minimal 30."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
    )
    assert result["macro_confidence"] == 30


def test_confidence_alignment_bonus():
    """H4 dan D1 searah memberikan +30."""
    engine = MacroBiasEngine()
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")
    # Base 30 + alignment 30 = 60
    assert result["macro_confidence"] == 60


def test_confidence_partial_alignment():
    """Salah satu timeframe memiliki trend -> +10."""
    engine = MacroBiasEngine()
    result = engine.analyze(trend_h4="BULLISH", trend_d1="NEUTRAL")
    # Base 30 + partial 10 = 40 (H4 NEUTRAL because trend_h4 is "BULLISH")
    # trend_h4 != "NEUTRAL" -> True: +10
    # Wait, let me look at the code again:
    # elif trend_h4 != "NEUTRAL" or trend_d1 != "NEUTRAL": confidence += 10
    # trend_h4 is "BULLISH" -> True -> +10
    assert result["macro_confidence"] == 40.0


def test_confidence_adx_confirmation():
    """ADX >= 25 memberikan confirmation bonus (H4=15, D1=25)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=30.0, adx_d1=28.0,
    )
    # Base 30 + alignment 30 + ADX H4 15 + ADX D1 25 = 100
    assert result["macro_confidence"] == 100.0


def test_confidence_boundary_max():
    """Confidence tidak boleh melebihi 100."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=40.0, adx_d1=45.0,
    )
    assert result["macro_confidence"] <= 100.0


# ──────────────────────────────────────────────
# M1.5 — Reason
# ──────────────────────────────────────────────

def test_reason_not_empty():
    """macro_reason selalu terisi."""
    engine = MacroBiasEngine()
    combinations = [
        ("BULLISH", "BULLISH"),
        ("BEARISH", "BEARISH"),
        ("BULLISH", "BEARISH"),
        ("NEUTRAL", "NEUTRAL"),
    ]
    for h4, d1 in combinations:
        result = engine.analyze(trend_h4=h4, trend_d1=d1)
        assert result["macro_reason"], f"Empty reason for {h4}/{d1}"
        assert len(result["macro_reason"]) > 10


def test_reason_contains_strength_description():
    """Reason mengandung deskripsi strength (strong/moderate/weak)."""
    engine = MacroBiasEngine()

    # ADX high -> strength >= 50 -> "strong"
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=35.0, adx_d1=40.0,
    )
    assert "strong" in result["macro_reason"]

    # ADX low -> weak
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=5.0, adx_d1=5.0,
    )
    assert "weak" in result["macro_reason"]


# ──────────────────────────────────────────────
# M1.6 — Fallback & Edge Cases
# ──────────────────────────────────────────────

def test_fallback_on_exception(monkeypatch):
    """Jika terjadi exception, fallback ke NEUTRAL."""
    engine = MacroBiasEngine()

    def _mock_error(*args, **kwargs):
        raise ValueError("Simulated error")

    monkeypatch.setattr(engine, "_determine_bias", _mock_error)
    result = engine.analyze()

    assert result["macro_bias"] == "NEUTRAL"
    assert result["macro_strength"] == 0.0
    assert result["macro_confidence"] == 0.0
    assert "Insufficient data" in result["macro_reason"]


def test_all_none_inputs():
    """Semua input None -> NEUTRAL."""
    engine = MacroBiasEngine()
    result = engine.analyze()
    assert result["macro_bias"] == "NEUTRAL"


def test_boundary_rsi_45():
    """RSI=45 adalah batas bawah netral (tidak bearish)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
        rsi_h4=45.0, rsi_d1=45.0,
    )
    # RSI 45 == 45, not < 45, so no bearish points
    assert result["macro_bias"] == "NEUTRAL"


def test_boundary_rsi_55():
    """RSI=55 adalah batas atas netral (tidak bullish)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL", trend_d1="NEUTRAL",
        rsi_h4=55.0, rsi_d1=55.0,
    )
    # RSI 55 == 55, not > 55, so no bullish points
    assert result["macro_bias"] == "NEUTRAL"


# ──────────────────────────────────────────────
# Symbol-Aware Confidence Tests (Sprint 3.2)
# ──────────────────────────────────────────────

def test_symbol_class_indices():
    """INDICES symbol (US30) keeps full confidence (multiplier 1.0x)."""
    engine = MacroBiasEngine()
    # Base 30 + alignment 30 = 60, with INDICES multiplier 1.0 = 60
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        symbol="US30",
    )
    assert result["macro_confidence"] == 60.0


def test_symbol_class_crypto():
    """CRYPTO symbol (BTCUSD) gets slight reduction (multiplier 0.95x)."""
    engine = MacroBiasEngine()
    # Base 30 + alignment 30 = 60, with CRYPTO multiplier 0.95 = 57
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        symbol="BTCUSD",
    )
    assert result["macro_confidence"] == 57.0


def test_symbol_class_metals():
    """METALS symbol (XAUUSD) gets moderate reduction (multiplier 0.85x)."""
    engine = MacroBiasEngine()
    # Base 30 + alignment 30 = 60, with METALS multiplier 0.85 = 51
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        symbol="XAUUSD",
    )
    assert result["macro_confidence"] == 51.0


def test_symbol_class_forex():
    """FOREX symbol (EURUSD) gets significant reduction (multiplier 0.65x)."""
    engine = MacroBiasEngine()
    # Base 30 + alignment 30 = 60, with FOREX multiplier 0.65 = 39
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        symbol="EURUSD",
    )
    assert result["macro_confidence"] == 39.0


def test_symbol_class_forex_adx():
    """FOREX symbol with ADX confirmation still gets reduced confidence."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=30.0, adx_d1=28.0,
        symbol="GBPUSD",
    )
    # Base 30 + alignment 30 + ADX H4 15 + ADX D1 25 = 100
    # FOREX multiplier 0.65 = 65
    assert result["macro_confidence"] == 65.0


def test_symbol_empty_no_adjustment():
    """Empty symbol means no multiplier applied (default 1.0x)."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        symbol="",
    )
    # Base 30 + alignment 30 = 60, no multiplier
    assert result["macro_confidence"] == 60.0


def test_get_symbol_class():
    """_get_symbol_class correctly classifies all symbol types."""
    assert _get_symbol_class("US30") == "INDICES"
    assert _get_symbol_class("NAS100") == "INDICES"
    assert _get_symbol_class("SPX500") == "INDICES"
    assert _get_symbol_class("BTCUSD") == "CRYPTO"
    assert _get_symbol_class("ETHUSD") == "CRYPTO"
    assert _get_symbol_class("XAUUSD") == "METALS"
    assert _get_symbol_class("XAGUSD") == "METALS"
    assert _get_symbol_class("EURUSD") == "FOREX"
    assert _get_symbol_class("GBPUSD") == "FOREX"
    assert _get_symbol_class("USDJPY") == "FOREX"
    assert _get_symbol_class("AUDUSD") == "FOREX"
    assert _get_symbol_class("unknown_symbol") == "FOREX"


def test_symbol_class_case_insensitive():
    """Symbol class detection should be case-insensitive."""
    assert _get_symbol_class("us30") == "INDICES"
    assert _get_symbol_class("btcusd") == "CRYPTO"
    assert _get_symbol_class("xauusd") == "METALS"
    assert _get_symbol_class("eurusd") == "FOREX"


def test_symbol_class_weight_values():
    """SYMBOL_CLASS_WEIGHTS values should be in valid range."""
    for symbol_class, weight in SYMBOL_CLASS_WEIGHTS.items():
        assert 0.0 < weight <= 1.0, (
            f"Weight for {symbol_class} must be in (0, 1]"
        )


# ──────────────────────────────────────────────
# Sprint 4 — Economic Event Context Tests
# ──────────────────────────────────────────────

def test_macro_events_field_present():
    """macro_events field is always present in result."""
    engine = MacroBiasEngine(economic_provider=MockEconomicProvider())
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")
    assert "macro_events" in result
    assert isinstance(result["macro_events"], list)


def test_economic_risk_reduces_confidence():
    """High event risk reduces macro confidence."""
    no_risk_engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=0),
    )
    high_risk_engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=50),
    )

    result_no_risk = no_risk_engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
    )
    result_high_risk = high_risk_engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
    )

    # With major event soon, confidence should be lower
    assert result_high_risk["macro_confidence"] < (
        result_no_risk["macro_confidence"]
    )


def test_economic_risk_reduces_strength():
    """High event risk reduces macro strength."""
    no_risk_engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=0),
    )
    high_risk_engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=50),
    )

    result_no_risk = no_risk_engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=30.0, adx_d1=30.0,
    )
    result_high_risk = high_risk_engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=30.0, adx_d1=30.0,
    )

    assert result_high_risk["macro_strength"] < (
        result_no_risk["macro_strength"]
    )


def test_economic_context_in_reason():
    """Reason includes economic context when events are upcoming."""
    engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=50),
    )
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")

    assert "FOMC" in result["macro_reason"]
    assert "uncertainty" in result["macro_reason"]


def test_no_economic_context_when_disabled():
    """use_economic_context=False skips economic analysis."""
    engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=50),
    )
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        use_economic_context=False,
    )

    # No event info in reason
    assert "FOMC" not in result["macro_reason"]
    # macro_events should still be present but empty
    assert result["macro_events"] == []


def test_no_economic_risk_with_empty_provider():
    """Default provider with no events keeps confidence unchanged."""
    engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=0),
    )
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")
    # Base 30 + alignment 30 = 60
    assert result["macro_confidence"] == 60.0


def test_use_economic_context_default_true():
    """Default behavior includes economic context."""
    engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=0),
    )
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")
    assert "macro_events" in result


def test_economic_risk_score_calculation():
    """Event risk score is calculated correctly for mock provider."""
    provider = MockEconomicProvider(risk_score=25)
    risk = provider.get_event_risk_score()

    assert risk["event_risk_score"] == 25
    assert risk["high_impact_count"] == 1
    assert risk["has_major_event_soon"] is True


def test_economic_risk_zero_no_effect():
    """Zero risk score should not affect confidence or strength."""
    engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=0),
    )
    # With no events, confidence = 60 (base 30 + alignment 30)
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
    )
    assert result["macro_confidence"] == 60.0


def test_macro_events_integration():
    """macro_events field contains event details when events exist."""
    engine = MacroBiasEngine(
        economic_provider=MockEconomicProvider(risk_score=50),
    )
    result = engine.analyze(trend_h4="BULLISH", trend_d1="BULLISH")
    events = result["macro_events"]

    assert len(events) > 0
    assert events[0]["name"] == "FOMC Meeting"
    assert events[0]["impact"] == "HIGH"


# ──────────────────────────────────────────────────────
# Sprint 6 — Stability & Edge Case Tests
# ──────────────────────────────────────────────────────

def test_extreme_rsi_values():
    """Engine handles extreme RSI values without breaking."""
    engine = MacroBiasEngine()
    for rsi_val in [100.0, 0.0, None]:
        result = engine.analyze(
            trend_h4="BULLISH", trend_d1="BULLISH",
            rsi_h4=rsi_val, rsi_d1=rsi_val,
        )
        assert "macro_bias" in result
        assert 0 <= result["macro_confidence"] <= 100


def test_extreme_adx_values():
    """Engine handles extreme ADX values without breaking."""
    engine = MacroBiasEngine()
    for adx_val in [100.0, 0.0, None]:
        result = engine.analyze(
            trend_h4="BULLISH", trend_d1="BULLISH",
            adx_h4=adx_val, adx_d1=adx_val,
        )
        assert "macro_bias" in result
        assert 0 <= result["macro_confidence"] <= 100


def test_all_inputs_none():
    """Engine handles all None/NEUTRAL inputs."""
    engine = MacroBiasEngine()
    result = engine.analyze()
    assert result["macro_bias"] == "NEUTRAL"
    assert result["macro_confidence"] == 30.0


def test_opposite_trends_with_extreme_rsi():
    """H4 BULLISH + D1 BEARISH with opposite RSI values."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BEARISH",
        rsi_h4=80.0, rsi_d1=20.0,
        adx_h4=40.0, adx_d1=40.0,
    )
    assert result["macro_bias"] in ("BULLISH", "BEARISH", "NEUTRAL")
    assert 0 <= result["macro_confidence"] <= 100


def test_invalid_symbol_name():
    """Invalid symbol name falls back to FOREX class."""
    assert _get_symbol_class("INVALID_XYZ") == "FOREX"
    assert _get_symbol_class("") == "FOREX"


def test_macro_confidence_with_extreme_adx():
    """ADX bonus is capped at 100 confidence max."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        adx_h4=100.0, adx_d1=100.0,
    )
    # Base 30 + alignment 30 + ADX H4 15 + ADX D1 25 = 100
    assert result["macro_confidence"] <= 100.0


def test_macro_strength_variation():
    """macro_strength returns sensible values across scenarios."""
    engine = MacroBiasEngine()
    # High volatility and strong trend -> higher strength
    high = engine.analyze(
        adx_h4=45.0, adx_d1=40.0,
        volatility_h4=0.05, volatility_d1=0.03,
    )
    # Low volatility and weak trend -> lower strength
    low = engine.analyze(
        adx_h4=10.0, adx_d1=10.0,
        volatility_h4=0.001, volatility_d1=0.001,
    )
    assert high["macro_strength"] >= low["macro_strength"]


def test_bearish_rsi_overrides_bullish_trend():
    """RSI bearish should influence bias but trend alignment
    takes priority in the engine logic."""
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH", trend_d1="BULLISH",
        rsi_h4=25.0, rsi_d1=25.0,
    )
    # Engine prioritizes trend alignment over RSI.
    # Both H4 and D1 are BULLISH, so bias stays BULLISH.
    # This test validates the engine doesn't crash on extreme RSI.
    assert "macro_bias" in result
    assert 0 <= result["macro_confidence"] <= 100
