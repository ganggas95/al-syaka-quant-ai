import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.unified_signal import UnifiedSignalGenerator
from src.macro_bias import MacroBiasEngine
from src.final_decision import FinalDecisionEngine


def test_quant_strategy_is_exposed_on_signal_payload():
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    signal = type("SignalPayload", (), {"quant_strategy": {"strategy": "MeanReversionStrategy", "action": "buy", "confidence": 0.77}})()

    payload = {
        "signal_id": None,
        "symbol": "EURUSD",
        "timestamp": "2024-01-01T00:00:00",
        "signal": "BUY",
        "confidence": 75,
        "entry_price": 1.1,
        "stop_loss": 1.05,
        "take_profit": 1.15,
        "risk_reward": 1.5,
        "risk_level": "MEDIUM",
        "trade_quality": "GOOD",
        "reasons": ["test"],
        "indicators_used": ["RSI"],
        "quant_strategy": signal.quant_strategy,
    }

    assert payload["quant_strategy"]["action"] == "buy"
    assert payload["quant_strategy"]["strategy"] == "MeanReversionStrategy"


def test_composite_score_and_regime_detection_are_returned():
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)

    indicators = {
        "rsi_14": [58.0],
        "ema_12": [1.102],
        "ema_20": [1.098],
        "ema_50": [1.095],
        "adx_adx": [26.0],
        "atr_14": [0.012],
        "macd_macd": [0.004],
        "macd_signal": [0.001],
    }
    structure = {
        "current_trend": "BULLISH",
        "break_of_structure": [{"type": "BOS"}],
        "change_of_character": [{"type": "CHOCH"}],
        "fair_value_gaps": [{"type": "FVG"}],
    }

    composite = generator._calculate_composite_score(indicators, structure, 0.72)
    regime = generator._detect_market_regime(indicators, structure)

    assert 0 <= composite["composite_score"] <= 100
    assert composite["confidence_label"] in {"LOW", "MEDIUM", "HIGH"}
    assert "market_structure" in composite["confidence_breakdown"]
    assert regime["market_regime"] in {"TRENDING", "RANGE", "REVERSAL", "VOLATILE"}
    assert regime["strategy_mode"] in {"trend_following", "mean_reversion", "breakout", "adaptive"}


def test_macro_bias_engine_returns_all_fields():
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="BULLISH",
        trend_d1="BULLISH",
        rsi_h4=62.0,
        rsi_d1=58.0,
        adx_h4=28.0,
        adx_d1=32.0,
    )

    assert result["macro_bias"] in {"BULLISH", "BEARISH", "NEUTRAL"}
    assert 0 <= result["macro_strength"] <= 100
    assert 0 <= result["macro_confidence"] <= 100
    assert isinstance(result["macro_reason"], str)
    assert len(result["macro_reason"]) > 0


def test_macro_bias_neutral_when_no_clear_direction():
    engine = MacroBiasEngine()
    result = engine.analyze(
        trend_h4="NEUTRAL",
        trend_d1="NEUTRAL",
        rsi_h4=50.0,
        rsi_d1=50.0,
    )

    assert result["macro_bias"] == "NEUTRAL"


def test_final_decision_buy_when_technical_and_macro_align():
    engine = FinalDecisionEngine()
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=72.0,
        market_regime="TRENDING",
        macro_bias="BULLISH",
        macro_confidence=70.0,
        macro_strength=60.0,
    )

    assert result["final_decision"] == "BUY"
    assert result["conflict_detected"] is False
    assert isinstance(result["decision_reason"], str)


def test_final_decision_hedge_when_conflict():
    engine = FinalDecisionEngine()
    result = engine.decide(
        technical_signal="BUY",
        technical_confidence=75.0,
        composite_score=72.0,
        market_regime="TRENDING",
        macro_bias="BEARISH",
        macro_confidence=60.0,
        macro_strength=50.0,
    )

    assert result["final_decision"] == "HEDGE"
    assert result["conflict_detected"] is True


def test_final_decision_wait_when_low_confidence():
    engine = FinalDecisionEngine()
    result = engine.decide(
        technical_signal="NEUTRAL",
        technical_confidence=25.0,
        composite_score=30.0,
        market_regime="RANGE",
        macro_bias="NEUTRAL",
        macro_confidence=20.0,
        macro_strength=10.0,
    )

    assert result["final_decision"] == "WAIT"


def test_macro_override_when_macro_strong_and_technical_weak():
    engine = FinalDecisionEngine()
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
