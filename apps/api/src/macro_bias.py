"""Macro Bias Engine — Menambahkan konteks makro ke sistem sinyal.

Menganalisis kondisi makro berdasarkan data teknikal yang tersedia
dan menghasilkan bias makro (bullish, bearish, neutral) beserta
tingkat kekuatan dan confidence.

Juga mengintegrasikan konteks fundamental (economic events) untuk
menyesuaikan confidence dan strength berdasarkan risiko event
ekonomi yang akan datang.
"""

from typing import Optional

from src.macro.economic_provider import EconomicEventProvider

# Symbol class confidence multipliers (validated against historical data)
# INDICES: 43-47% accuracy → keep high confidence
# CRYPTO: 43-47% accuracy → slight reduction
# METALS: moderate accuracy → moderate reduction
# FOREX: 10-26% accuracy → significant reduction
SYMBOL_CLASS_WEIGHTS: dict[str, float] = {
    "INDICES": 1.0,
    "CRYPTO": 0.95,
    "METALS": 0.85,
    "FOREX": 0.65,
}


def _get_symbol_class(symbol: str) -> str:
    """Classify symbol into trading class based on naming convention."""
    prefix = symbol.upper().strip()
    if prefix in ("US30", "NAS100", "SPX500", "JP225", "UK100", "GER40"):
        return "INDICES"
    if prefix in ("BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD"):
        return "CRYPTO"
    if prefix in ("XAUUSD", "XAGUSD", "XPTUSD", "XPDUSD"):
        return "METALS"
    return "FOREX"


class MacroBiasEngine:
    """Engine untuk mendeteksi bias makro berdasarkan konteks pasar.

    Menggabungkan analisis teknikal multi-timeframe dengan konteks
    fundamental (economic events) untuk menghasilkan bias makro
    yang lebih akurat.
    """

    def __init__(
        self,
        economic_provider: Optional[EconomicEventProvider] = None,
    ):
        """Initialize engine with optional economic event provider.

        Args:
            economic_provider: If None, a default provider with
                14-day look-ahead is created.
        """
        self.economic_provider = (
            economic_provider or EconomicEventProvider()
        )

    def analyze(
        self,
        trend_h4: str = "NEUTRAL",
        trend_d1: str = "NEUTRAL",
        rsi_h4: Optional[float] = None,
        rsi_d1: Optional[float] = None,
        adx_h4: Optional[float] = None,
        adx_d1: Optional[float] = None,
        volatility_h4: Optional[float] = None,
        volatility_d1: Optional[float] = None,
        symbol: str = "",
        use_economic_context: bool = True,
    ) -> dict:
        """Analyze macro context and return bias, strength, and confidence.

        Menggunakan kombinasi trend multi-timeframe, momentum,
        volatilitas, dan konteks fundamental (economic events)
        untuk menyimpulkan bias makro.

        Args:
            symbol: Symbol name for symbol-aware confidence adjustment.
                   Empty string means no adjustment (default 1.0x).
            use_economic_context: Whether to include economic event
                context in the analysis. Set to False for testing.
        """
        try:
            bias = self._determine_bias(
                trend_h4, trend_d1, rsi_h4, rsi_d1,
            )
            strength = self._calculate_strength(
                adx_h4, adx_d1, volatility_h4, volatility_d1,
            )
            confidence = self._calculate_confidence(
                trend_h4, trend_d1, adx_h4, adx_d1,
                symbol=symbol,
            )

            # Economic event context
            event_context = None
            if use_economic_context:
                event_context = (
                    self.economic_provider.get_event_risk_score()
                )
                if event_context["event_risk_score"] > 0:
                    confidence = self._adjust_for_economic_risk(
                        confidence, event_context,
                    )
                    strength = self._adjust_for_economic_risk(
                        strength, event_context,
                    )

            return {
                "macro_bias": bias,
                "macro_strength": round(strength, 1),
                "macro_confidence": round(confidence, 1),
                "macro_reason": self._generate_reason(
                    bias, strength, confidence,
                    trend_h4, trend_d1, event_context,
                ),
                "macro_events": (
                    event_context["upcoming_events"]
                    if event_context else []
                ),
            }
        except Exception:
            return {
                "macro_bias": "NEUTRAL",
                "macro_strength": 0.0,
                "macro_confidence": 0.0,
                "macro_reason": (
                    "Insufficient data for macro analysis"
                ),
                "macro_events": [],
            }

    def _determine_bias(
        self,
        trend_h4: str,
        trend_d1: str,
        rsi_h4: Optional[float],
        rsi_d1: Optional[float],
    ) -> str:
        """Determine macro bias from multi-timeframe trend and momentum."""
        bullish_signals = 0
        bearish_signals = 0

        # Trend contribution (weighted higher)
        if trend_h4 == "BULLISH":
            bullish_signals += 2
        elif trend_h4 == "BEARISH":
            bearish_signals += 2

        if trend_d1 == "BULLISH":
            bullish_signals += 3
        elif trend_d1 == "BEARISH":
            bearish_signals += 3

        # RSI momentum contribution
        if rsi_h4 is not None:
            if rsi_h4 > 55:
                bullish_signals += 1
            elif rsi_h4 < 45:
                bearish_signals += 1

        if rsi_d1 is not None:
            if rsi_d1 > 55:
                bullish_signals += 1.5
            elif rsi_d1 < 45:
                bearish_signals += 1.5

        if bullish_signals > bearish_signals:
            return "BULLISH"
        elif bearish_signals > bullish_signals:
            return "BEARISH"
        return "NEUTRAL"

    def _calculate_strength(
        self,
        adx_h4: Optional[float],
        adx_d1: Optional[float],
        volatility_h4: Optional[float],
        volatility_d1: Optional[float],
    ) -> float:
        """Calculate macro strength (0-100) based on trend conviction."""
        strength = 0.0

        # ADX indicates trend strength
        if adx_h4 is not None:
            if adx_h4 >= 30:
                strength += 25
            elif adx_h4 >= 20:
                strength += 15
            else:
                strength += 5

        if adx_d1 is not None:
            if adx_d1 >= 30:
                strength += 35
            elif adx_d1 >= 20:
                strength += 20
            else:
                strength += 10

        # Volatility check — too high = uncertain
        vol_penalty = 0
        if volatility_h4 is not None and volatility_h4 > 0.02:
            vol_penalty += 10
        if volatility_d1 is not None and volatility_d1 > 0.03:
            vol_penalty += 15

        return max(0, min(100, strength - vol_penalty))

    def _calculate_confidence(
        self,
        trend_h4: str,
        trend_d1: str,
        adx_h4: Optional[float],
        adx_d1: Optional[float],
        symbol: str = "",
    ) -> float:
        """Calculate macro confidence (0-100) based on alignment.

        Adjusts confidence based on symbol class using validated
        multipliers. FOREX symbols get reduced confidence since
        historical validation shows 10-26% accuracy vs 43-47%
        for INDICES/CRYPTO.
        """
        confidence = 30.0  # base

        # Trend alignment across timeframes
        if trend_h4 == trend_d1 and trend_h4 != "NEUTRAL":
            confidence += 30
        elif trend_h4 != "NEUTRAL" or trend_d1 != "NEUTRAL":
            confidence += 10

        # ADX confirmation
        if adx_h4 is not None and adx_h4 >= 25:
            confidence += 15
        if adx_d1 is not None and adx_d1 >= 25:
            confidence += 25

        # Apply symbol class multiplier
        if symbol:
            symbol_class = _get_symbol_class(symbol)
            multiplier = SYMBOL_CLASS_WEIGHTS.get(symbol_class, 1.0)
            confidence *= multiplier

        return min(100, confidence)

    def _generate_reason(
        self,
        bias: str,
        strength: float,
        confidence: float,
        trend_h4: str,
        trend_d1: str,
        event_context: Optional[dict] = None,
    ) -> str:
        """Generate human-readable macro reason."""
        parts = []

        if bias == "NEUTRAL":
            parts.append(
                "Macro bias is neutral — no clear directional "
                "conviction across timeframes"
            )
        else:
            alignment = ""
            if trend_h4 == trend_d1 and trend_h4 != "NEUTRAL":
                alignment = (
                    f"H4 and D1 both show {trend_h4.lower()} trend — "
                    "strong alignment"
                )
            else:
                alignment = (
                    f"H4 is {trend_h4.lower()} while D1 is "
                    f"{trend_d1.lower()} — partial alignment"
                )

            strength_desc = (
                "strong" if strength >= 50
                else "moderate" if strength >= 25
                else "weak"
            )

            parts.append(
                f"Macro bias is {bias.lower()} ({strength_desc}, "
                f"confidence {confidence:.0f}%). {alignment}."
            )

        # Append economic context if available
        if event_context and event_context["event_risk_score"] > 0:
            high = event_context["high_impact_count"]
            soon = event_context["has_major_event_soon"]
            names = [
                e["name"]
                for e in event_context["upcoming_events"][:2]
            ]
            names_str = " and ".join(names)
            if soon:
                parts.append(
                    f"High-impact event{'' if high == 1 else 's'} "
                    f"({names_str}) within 3 days — "
                    "elevated uncertainty"
                )
            else:
                parts.append(
                    f"{high} high-impact event"
                    f"{' is' if high == 1 else 's are'} "
                    f"upcoming ({names_str}) — "
                    "moderate uncertainty"
                )

        return " ".join(parts)

    def _adjust_for_economic_risk(
        self,
        value: float,
        event_context: dict,
    ) -> float:
        """Reduce confidence/strength when major events approach.

        High-impact events within 3 days -> reduce by up to 20%.
        High-impact events within 7 days -> reduce by up to 10%.
        """
        risk_score = event_context["event_risk_score"]
        has_soon = event_context["has_major_event_soon"]

        if has_soon:
            # Major event within 3 days: reduce by up to 20%
            reduction = min(20, risk_score * 0.2)
        elif risk_score > 0:
            # General event risk: reduce by up to 10%
            reduction = min(10, risk_score * 0.1)
        else:
            reduction = 0

        return max(0, value - reduction)
