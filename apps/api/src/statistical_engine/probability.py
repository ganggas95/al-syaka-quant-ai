"""Probability Engine — Hitung probabilitas BUY/SELL berdasarkan kondisi pasar."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProbabilityResult:
    """Hasil kalkulasi probabilitas."""
    signal: str  # BUY or SELL
    confidence: float  # 0.0 - 1.0
    reasons: list[str]
    risk_level: str  # LOW, MEDIUM, HIGH
    suggested_rr: float  # Risk/Reward ratio


class ProbabilityEngine:
    """Menghitung probabilitas arah market dari kondisi indikator dan structure."""

    def __init__(self):
        # Bobot untuk setiap komponen analisis
        self.weights = {
            "trend": 0.30,
            "momentum": 0.20,
            "market_structure": 0.25,
            "volatility": 0.10,
            "volume": 0.10,
            "session": 0.05,
        }

    def evaluate(
        self,
        indicators: dict,
        market_structure: Optional[dict] = None,
        session: Optional[dict] = None,
    ) -> ProbabilityResult:
        """Evaluasi probabilitas dari dict indicators dan market structure."""
        scores = {"BUY": 0.0, "SELL": 0.0}
        reasons = []
        risk = "MEDIUM"

        # 1. Trend Analysis (30%)
        trend_score = self._evaluate_trend(indicators)
        scores["BUY"] += trend_score["BUY"] * self.weights["trend"]
        scores["SELL"] += trend_score["SELL"] * self.weights["trend"]
        if trend_score["reason"]:
            reasons.append(trend_score["reason"])

        # 2. Momentum Analysis (20%)
        momentum_score = self._evaluate_momentum(indicators)
        scores["BUY"] += momentum_score["BUY"] * self.weights["momentum"]
        scores["SELL"] += momentum_score["SELL"] * self.weights["momentum"]
        if momentum_score["reason"]:
            reasons.append(momentum_score["reason"])

        # 3. Market Structure (25%)
        if market_structure:
            struct_score = self._evaluate_structure(market_structure)
            scores["BUY"] += struct_score["BUY"] * self.weights["market_structure"]
            scores["SELL"] += struct_score["SELL"] * self.weights["market_structure"]
            if struct_score["reason"]:
                reasons.append(struct_score["reason"])

        # 4. Volatility Analysis (10%)
        vol_score = self._evaluate_volatility(indicators)
        scores["BUY"] += vol_score["BUY"] * self.weights["volatility"]
        scores["SELL"] += vol_score["SELL"] * self.weights["volatility"]
        if vol_score["reason"]:
            reasons.append(vol_score["reason"])

        # 5. Volume Analysis (10%)
        vol_score2 = self._evaluate_volume(indicators)
        scores["BUY"] += vol_score2["BUY"] * self.weights["volume"]
        scores["SELL"] += vol_score2["SELL"] * self.weights["volume"]
        if vol_score2["reason"]:
            reasons.append(vol_score2["reason"])

        # 6. Session Analysis (5%)
        if session:
            sess_score = self._evaluate_session(session)
            scores["BUY"] += sess_score["BUY"] * self.weights["session"]
            scores["SELL"] += sess_score["SELL"] * self.weights["session"]
            if sess_score["reason"]:
                reasons.append(sess_score["reason"])

        # Final decision
        total = scores["BUY"] + scores["SELL"]
        if total == 0:
            return ProbabilityResult("NEUTRAL", 0.0, ["Insufficient data"], "HIGH", 1.0)

        buy_conf = scores["BUY"] / total
        sell_conf = scores["SELL"] / total

        if buy_conf > sell_conf:
            signal = "BUY"
            confidence = buy_conf
            # Suggested RR based on confidence
            rr = min(1.0 + (confidence - 0.5) * 5, 3.0) if confidence > 0.5 else 1.0
        else:
            signal = "SELL"
            confidence = sell_conf
            rr = min(1.0 + (confidence - 0.5) * 5, 3.0) if confidence > 0.5 else 1.0

        # Risk level
        if confidence >= 0.75:
            risk = "LOW"
        elif confidence >= 0.6:
            risk = "MEDIUM"
        else:
            risk = "HIGH"

        # If confidence too low, suggest NEUTRAL
        if confidence < 0.55:
            return ProbabilityResult("NEUTRAL", confidence, reasons, risk, rr)

        return ProbabilityResult(signal, confidence, reasons, risk, round(rr, 1))

    def _evaluate_trend(self, ind: dict) -> dict:
        """Evaluate based on EMA/SMA crossovers and ADX."""
        score = {"BUY": 0.0, "SELL": 0.0, "reason": ""}
        reasons = []

        # EMA cross (ema_12 vs ema_50)
        if "ema_12" in ind and "ema_50" in ind:
            ema12 = ind["ema_12"]
            ema50 = ind["ema_50"]
            if len(ema12) > 1 and len(ema50) > 1:
                if ema12[-1] > ema50[-1] and ema12[-2] <= ema50[-2]:
                    score["BUY"] += 0.8
                    reasons.append("EMA Golden Cross")
                elif ema12[-1] < ema50[-1] and ema12[-2] >= ema50[-2]:
                    score["SELL"] += 0.8
                    reasons.append("EMA Death Cross")
                elif ema12[-1] > ema50[-1]:
                    score["BUY"] += 0.4
                    reasons.append("EMA Bullish Alignment")
                else:
                    score["SELL"] += 0.4
                    reasons.append("EMA Bearish Alignment")

        # Price vs SMA_200
        if "sma_200" in ind and "close" in ind:
            if ind["close"][-1] > ind["sma_200"][-1]:
                score["BUY"] += 0.3
                reasons.append("Price above SMA 200 (Bullish)")
            else:
                score["SELL"] += 0.3
                reasons.append("Price below SMA 200 (Bearish)")

        # ADX strength
        if "adx_adx" in ind:
            adx_val = ind["adx_adx"][-1]
            if adx_val > 25:
                if score["BUY"] > score["SELL"]:
                    reasons.append(f"Strong uptrend (ADX {adx_val:.1f})")
                else:
                    reasons.append(f"Strong downtrend (ADX {adx_val:.1f})")

        if reasons:
            score["reason"] = "; ".join(reasons[:2])
        return score

    def _evaluate_momentum(self, ind: dict) -> dict:
        """Evaluate based on RSI, Stochastic, CCI."""
        score = {"BUY": 0.0, "SELL": 0.0, "reason": ""}
        reasons = []

        # RSI
        if "rsi_14" in ind:
            rsi_val = ind["rsi_14"][-1]
            if rsi_val < 30:
                score["BUY"] += 0.7
                reasons.append(f"RSI Oversold ({rsi_val:.0f})")
            elif rsi_val > 70:
                score["SELL"] += 0.7
                reasons.append(f"RSI Overbought ({rsi_val:.0f})")
            elif 40 <= rsi_val <= 60:
                score["BUY"] += 0.1
                score["SELL"] += 0.1  # Neutral
            elif rsi_val < 40:
                score["BUY"] += 0.3
                reasons.append(f"RSI Momentum Down ({rsi_val:.0f})")
            else:
                score["SELL"] += 0.3
                reasons.append(f"RSI Momentum Up ({rsi_val:.0f})")

        # CCI
        if "cci_20" in ind:
            cci_val = ind["cci_20"][-1]
            if cci_val < -100:
                score["BUY"] += 0.4
                reasons.append("CCI Oversold")
            elif cci_val > 100:
                score["SELL"] += 0.4
                reasons.append("CCI Overbought")

        # Williams %R
        if "williams_r_14" in ind:
            wr = ind["williams_r_14"][-1]
            if wr < -80:
                score["BUY"] += 0.3
                reasons.append("Williams %R Oversold")
            elif wr > -20:
                score["SELL"] += 0.3
                reasons.append("Williams %R Overbought")

        if reasons:
            score["reason"] = "; ".join(reasons[:2])
        return score

    def _evaluate_structure(self, struct: dict) -> dict:
        """Evaluate based on market structure."""
        score = {"BUY": 0.0, "SELL": 0.0, "reason": ""}
        reasons = []

        trend = struct.get("current_trend", "NEUTRAL")
        if trend == "BULLISH":
            score["BUY"] += 0.6
            reasons.append("Bullish Market Structure")
        elif trend == "BEARISH":
            score["SELL"] += 0.6
            reasons.append("Bearish Market Structure")

        # Break of Structure
        bos = struct.get("break_of_structure", [])
        for b in bos:
            if b["type"] == "BOS_HIGH":
                score["BUY"] += 0.3
                reasons.append("BOS High (Bullish)")
            elif b["type"] == "BOS_LOW":
                score["SELL"] += 0.3
                reasons.append("BOS Low (Bearish)")

        # CHOCH
        choch = struct.get("change_of_character", [])
        for c in choch:
            if c["type"] == "CHOCH_UP":
                score["BUY"] += 0.4
                reasons.append("CHOCH to Uptrend")
            elif c["type"] == "CHOCH_DOWN":
                score["SELL"] += 0.4
                reasons.append("CHOCH to Downtrend")

        # FVG
        fvg = struct.get("fair_value_gaps", [])
        for f in fvg:
            if f["type"] == "BULLISH_FVG":
                score["BUY"] += 0.2
            elif f["type"] == "BEARISH_FVG":
                score["SELL"] += 0.2

        if reasons:
            score["reason"] = "; ".join(reasons[:2])
        return score

    def _evaluate_volatility(self, ind: dict) -> dict:
        """Evaluate based on volatility (ATR, Bollinger)."""
        score = {"BUY": 0.0, "SELL": 0.0, "reason": ""}

        if "bb_position" in ind:
            pos = ind["bb_position"][-1]
            if pos < 0.2:
                score["BUY"] += 0.4
            elif pos > 0.8:
                score["SELL"] += 0.4

        if "atr_14" in ind:
            # Low volatility often precedes breakout
            pass

        return score

    def _evaluate_volume(self, ind: dict) -> dict:
        """Evaluate based on volume indicators."""
        score = {"BUY": 0.0, "SELL": 0.0, "reason": ""}
        return score

    def _evaluate_session(self, session: dict) -> dict:
        """Evaluate based on trading session."""
        score = {"BUY": 0.0, "SELL": 0.0, "reason": ""}
        return score
