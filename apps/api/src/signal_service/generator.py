"""Signal Generator — Mengintegrasikan Statistical Engine + Risk Engine + Market Structure."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.statistical_engine import ProbabilityEngine
from src.statistical_engine.probability import ProbabilityResult
from al_syaka_risk import RiskManager
from al_syaka_risk.risk_manager import RiskDecision


@dataclass
class SignalResult:
    """Output final signal — seperti yang diminta PRD."""
    symbol: str
    timeframe: str
    timestamp: datetime
    signal: str  # BUY, SELL, NEUTRAL
    confidence: float  # 0-100%
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward_ratio: Optional[float]
    lot_size: Optional[float]
    reasons: list[str]
    risk_level: str  # LOW, MEDIUM, HIGH
    trade_quality: str  # POOR, FAIR, GOOD, EXCELLENT
    indicators_used: list[str] = field(default_factory=list)


class SignalGenerator:
    """Signal Generator utama — integrasi semua engine."""

    def __init__(self, account_balance: float = 10_000):
        self.probability_engine = ProbabilityEngine()
        self.risk_manager = RiskManager(account_balance=account_balance)

    def generate(
        self,
        symbol: str,
        timeframe: str,
        ohlc: Optional[dict] = None,
        indicators: Optional[dict] = None,
        market_structure: Optional[dict] = None,
        session: Optional[dict] = None,
        win_rate_stats: Optional[dict] = None,
    ) -> SignalResult:
        """Generate complete signal dari semua input."""
        # 1. Hitung probabilitas
        prob_result = self.probability_engine.evaluate(
            indicators=indicators or {},
            market_structure=market_structure,
            session=session,
        )

        # 2. Jika NEUTRAL, tidak perlu lanjut risk
        if prob_result.signal == "NEUTRAL":
            return SignalResult(
                symbol=symbol,
                timeframe=timeframe,
                timestamp=datetime.utcnow(),
                signal="NEUTRAL",
                confidence=round(prob_result.confidence * 100, 0),
                entry_price=None,
                stop_loss=None,
                take_profit=None,
                risk_reward_ratio=None,
                lot_size=None,
                reasons=prob_result.reasons or ["No clear signal"],
                risk_level=prob_result.risk_level,
                trade_quality="POOR",
            )

        # 3. Tentukan entry price
        entry_price = self._determine_entry(indicators, ohlc, prob_result)

        if entry_price is None:
            return SignalResult(
                symbol=symbol, timeframe=timeframe,
                timestamp=datetime.utcnow(),
                signal="NEUTRAL", confidence=0,
                entry_price=None, stop_loss=None, take_profit=None,
                risk_reward_ratio=None, lot_size=None,
                reasons=["Could not determine entry price"],
                risk_level="HIGH", trade_quality="POOR",
            )

        # 4. Hitung ATR untuk SL/TP
        atr_value = None
        if indicators and "atr_14" in indicators:
            atr_val_list = indicators["atr_14"]
            if len(atr_val_list) > 0:
                atr_value = atr_val_list[-1]

        # 5. Ambil S/R levels
        support = None
        resistance = None
        if market_structure and "support_resistance" in market_structure:
            sr = market_structure["support_resistance"]
            supports = sr.get("supports", [])
            resistances = sr.get("resistances", [])
            if prob_result.signal == "BUY" and supports:
                support = supports[0]["price"]
            elif prob_result.signal == "SELL" and resistances:
                resistance = resistances[0]["price"]

        # 6. Risk assessment
        risk_decision = self.risk_manager.evaluate_trade(
            signal=prob_result.signal,
            entry_price=entry_price,
            confidence=prob_result.confidence,
            atr_value=atr_value,
            support=support,
            resistance=resistance,
        )

        # 7. Kumpulkan indikator yang digunakan
        indicators_used = self._extract_used_indicators(indicators_or_none=indicators)

        return SignalResult(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=datetime.utcnow(),
            signal=prob_result.signal,
            confidence=round(prob_result.confidence * 100, 0),
            entry_price=risk_decision.entry_price,
            stop_loss=risk_decision.stop_loss,
            take_profit=risk_decision.take_profit,
            risk_reward_ratio=risk_decision.risk_reward_ratio,
            lot_size=risk_decision.lot_size,
            reasons=prob_result.reasons,
            risk_level=prob_result.risk_level,
            trade_quality=risk_decision.trade_quality,
            indicators_used=indicators_used,
        )

    def _determine_entry(self, indicators: dict, ohlc: dict, prob: ProbabilityResult) -> Optional[float]:
        """Determine optimal entry price."""
        if ohlc and "close" in ohlc and len(ohlc["close"]) > 0:
            return ohlc["close"][-1]
        return None

    def _extract_used_indicators(self, indicators_or_none: Optional[dict]) -> list[str]:
        if not indicators_or_none:
            return []
        used = []
        key_map = {
            "rsi_14": "RSI", "ema_12": "EMA 12", "ema_20": "EMA 20",
            "ema_50": "EMA 50", "sma_200": "SMA 200", "macd_macd": "MACD",
            "adx_adx": "ADX", "atr_14": "ATR", "bb_upper": "Bollinger",
            "supertrend_direction": "Supertrend",
        }
        for key, label in key_map.items():
            if key in indicators_or_none:
                used.append(label)
        return used[:5]  # Max 5 indicators
