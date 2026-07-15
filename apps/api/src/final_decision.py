"""Final Decision Engine — Menggabungkan sinyal teknikal dan makro.

Menentukan keputusan akhir (BUY, SELL, WAIT, HEDGE) berdasarkan:
- Sinyal teknikal (signal + confidence)
- Composite score
- Market regime
- Macro bias
- Konflik antara teknikal dan makro

Sprint 5 enhancements:
- HEDGE intensity (LIGHT/FULL) berdasarkan severity konflik
- decision_confidence (0-100) — tingkat keyakinan keputusan
- position_multiplier (0.0-1.0) — rekomendasi ukuran posisi
- Enhanced reason dengan data points spesifik
"""

from typing import Optional


class FinalDecisionEngine:
    """Engine for final trading decision with conflict handling.

    Priority chain:
    1. Macro override (strong macro overrides weak technical)
    2. Conflict → HEDGE with intensity level
    3. Strong technical signal
    4. Moderate technical with macro support
    5. Low confidence → WAIT
    """

    def decide(
        self,
        technical_signal: str = "NEUTRAL",
        technical_confidence: float = 0.0,
        composite_score: Optional[float] = None,
        market_regime: str = "VOLATILE",
        macro_bias: str = "NEUTRAL",
        macro_confidence: float = 0.0,
        macro_strength: float = 0.0,
    ) -> dict:
        """Generate final decision with conflict detection.

        Returns:
            dict with keys:
                - final_decision: BUY, SELL, WAIT, HEDGE
                - decision_reason: human-readable explanation
                - conflict_detected: bool
                - hedge_intensity: LIGHT or FULL (only when HEDGE)
                - decision_confidence: 0-100 confidence in decision
                - position_multiplier: 0.0-1.0 recommended position size
        """
        try:
            score = composite_score or technical_confidence

            # Detect conflict between technical and macro
            conflict = self._detect_conflict(
                technical_signal, macro_bias,
                macro_confidence, macro_strength,
                technical_confidence,
            )

            decision, reason, hedge_intensity = (
                self._resolve_decision(
                    technical_signal, score, market_regime,
                    macro_bias, macro_confidence,
                    macro_strength, conflict,
                )
            )

            decision_conf = self._calculate_decision_confidence(
                decision, score, technical_confidence,
                macro_confidence, conflict,
            )
            pos_mult = self._calculate_position_multiplier(
                decision, hedge_intensity,
                decision_conf,
            )

            return {
                "final_decision": decision,
                "decision_reason": reason,
                "conflict_detected": conflict,
                "hedge_intensity": hedge_intensity,
                "decision_confidence": round(decision_conf, 1),
                "position_multiplier": round(pos_mult, 2),
            }
        except Exception:
            return {
                "final_decision": "WAIT",
                "decision_reason": (
                    "Unable to compute final decision — "
                    "falling back to WAIT"
                ),
                "conflict_detected": False,
                "hedge_intensity": None,
                "decision_confidence": 0.0,
                "position_multiplier": 0.0,
            }

    def _detect_conflict(
        self,
        technical_signal: str,
        macro_bias: str,
        macro_confidence: float,
        macro_strength: float,
        technical_confidence: float = 0.0,
    ) -> bool:
        """Detect conflict between technical signal and macro bias.

        Conflict occurs when:
        - Technical says BUY but macro is BEARISH (with confidence)
        - Technical says SELL but macro is BULLISH (with confidence)
        - Strong macro bias opposes weak technical signal

        No conflict if macro is strong enough to override
        (confidence >= 60 and strength >= 50 and technical confidence < 50).
        """
        if technical_signal == "NEUTRAL" or macro_bias == "NEUTRAL":
            return False

        if macro_confidence < 30 or macro_strength < 20:
            return False

        # Macro is strong enough to override — no conflict
        if (
            macro_confidence >= 60
            and macro_strength >= 50
            and technical_confidence < 50
        ):
            return False

        direct_conflict = (
            (technical_signal == "BUY" and macro_bias == "BEARISH")
            or (technical_signal == "SELL" and macro_bias == "BULLISH")
        )

        return direct_conflict

    def _calculate_hedge_intensity(
        self,
        macro_confidence: float,
        macro_strength: float,
        technical_confidence: float,
    ) -> str:
        """Determine HEDGE intensity based on conflict severity.

        FULL: macro is confident (>= 45) and tech is strong (>= 60)
              -> serious conflict, full hedge recommended
        LIGHT: one side is weak -> light hedge, partial reduction
        """
        severity = (
            (macro_confidence / 100.0)
            * (macro_strength / 100.0)
            * (technical_confidence / 100.0)
        )
        # severity ranges from 0 to 1. Higher means both sides are confident
        if severity >= 0.15:
            return "FULL"
        return "LIGHT"

    def _resolve_decision(
        self,
        technical_signal: str,
        confidence: float,
        market_regime: str,
        macro_bias: str,
        macro_confidence: float,
        macro_strength: float,
        conflict: bool,
    ) -> tuple:
        """Resolve final decision from all inputs.

        Priority:
        1. Macro override (strong macro overrides weak technical)
        2. Conflict → HEDGE with intensity
        3. Strong technical signal
        4. Moderate technical with macro support
        5. Low confidence → WAIT

        Returns:
            Tuple of (decision, reason, hedge_intensity).
            hedge_intensity is None for non-HEDGE decisions.
        """
        # 1. Macro override — when macro is strong/confident
        #    and technical is weak (conflict is expected in this case)
        if (
            macro_confidence >= 60
            and macro_bias != "NEUTRAL"
            and confidence < 50
        ):
            macro_signal = "BUY" if macro_bias == "BULLISH" else "SELL"
            return (
                macro_signal,
                (
                    f"Macro bias dominates ({macro_bias.lower()}, "
                    f"confidence {macro_confidence:.0f}%, "
                    f"strength {macro_strength:.0f}%) — "
                    f"overriding weak technical signal "
                    f"({confidence:.0f}%) in {market_regime.lower()} market"
                ),
                None,
            )

        # 2. Conflict → conservative decision
        if conflict:
            intensity = self._calculate_hedge_intensity(
                macro_confidence, macro_strength, confidence,
            )
            if technical_signal == "BUY":
                return (
                    "HEDGE",
                    (
                        f"Technical signal is BUY ({confidence:.0f}%) "
                        f"but macro bias is {macro_bias.lower()} "
                        f"(confidence {macro_confidence:.0f}%) — "
                        f"recommend {intensity.lower()} HEDGE "
                        f"to reduce directional exposure"
                    ),
                    intensity,
                )
            elif technical_signal == "SELL":
                return (
                    "HEDGE",
                    (
                        f"Technical signal is SELL ({confidence:.0f}%) "
                        f"but macro bias is {macro_bias.lower()} "
                        f"(confidence {macro_confidence:.0f}%) — "
                        f"recommend {intensity.lower()} HEDGE "
                        f"to reduce directional exposure"
                    ),
                    intensity,
                )
            return (
                "WAIT",
                (
                    f"Conflicting signals between technical "
                    f"({technical_signal.lower()}, "
                    f"{confidence:.0f}%) and macro "
                    f"({macro_bias.lower()}, "
                    f"{macro_confidence:.0f}%) — "
                    "recommend WAIT"
                ),
                None,
            )

        # 3. Technical signal with strong confidence
        if confidence >= 70 and technical_signal != "NEUTRAL":
            macro_context = (
                f" with {macro_bias.lower()} macro support"
                if macro_bias != "NEUTRAL"
                else ""
            )
            return (
                technical_signal,
                (
                    f"Strong technical signal ({confidence:.0f}%)"
                    f"{macro_context} in "
                    f"{market_regime.lower()} regime — "
                    f"recommend {technical_signal}"
                ),
                None,
            )

        # Technical signal with moderate confidence
        if confidence >= 40 and technical_signal != "NEUTRAL":
            # Check if macro supports
            macro_support = (
                (macro_bias == "BULLISH" and technical_signal == "BUY")
                or (macro_bias == "BEARISH" and technical_signal == "SELL")
            )
            if macro_support:
                return (
                    technical_signal,
                    (
                        f"Technical signal ({confidence:.0f}%) "
                        f"supported by {macro_bias.lower()} macro bias "
                        f"(confidence {macro_confidence:.0f}%) — "
                        f"recommend {technical_signal}"
                    ),
                    None,
                )
            else:
                return (
                    technical_signal,
                    (
                        f"Moderate technical signal "
                        f"({confidence:.0f}%) with "
                        f"{macro_bias.lower()} macro context — "
                        f"recommend {technical_signal} with caution"
                    ),
                    None,
                )

        # Low confidence or neutral — wait
        if technical_signal == "NEUTRAL" or confidence < 30:
            return (
                "WAIT",
                (
                    f"Low conviction across all inputs "
                    f"(confidence {confidence:.0f}%, "
                    f"regime: {market_regime.lower()}) — "
                    "recommend WAIT for clearer setup"
                ),
                None,
            )

        # Default fallback
        return ("WAIT", "Insufficient signals — recommend WAIT", None)

    def _calculate_decision_confidence(
        self,
        decision: str,
        score: float,
        technical_confidence: float,
        macro_confidence: float,
        conflict: bool,
    ) -> float:
        """Calculate confidence in the final decision (0-100).

        - Strong BUY/SELL -> 70-100 (based on score)
        - Macro override -> 60-80 (based on macro confidence)
        - HEDGE -> 40-60 (based on average of inputs)
        - WAIT -> 0-30 (low confidence scenario)
        """
        if decision in ("BUY", "SELL"):
            if conflict:
                # Override scenario
                return min(80, 60 + macro_confidence * 0.2)
            # Normal trade
            return min(100, max(50, score))

        if decision == "HEDGE":
            # Hedge confidence is moderate — acknowledging uncertainty
            avg = (technical_confidence + macro_confidence) / 2.0
            return min(65, max(30, avg * 0.6))

        # WAIT — low confidence
        base = score * 0.3
        return min(30, base)

    def _calculate_position_multiplier(
        self,
        decision: str,
        hedge_intensity: Optional[str],
        decision_confidence: float,
    ) -> float:
        """Calculate recommended position size multiplier (0.0-1.0).

        Based on decision type and confidence:
        - BUY/SELL (strong, confident) -> 0.8-1.0
        - BUY/SELL (moderate) -> 0.5-0.7
        - HEDGE (LIGHT) -> 0.3-0.4
        - HEDGE (FULL) -> 0.1-0.2
        - WAIT -> 0.0
        """
        if decision in ("BUY", "SELL"):
            # Scale with confidence: 50% conf -> 0.5, 100% -> 1.0
            return max(0.4, min(1.0, decision_confidence / 80.0))

        if decision == "HEDGE":
            if hedge_intensity == "FULL":
                return 0.2
            return 0.4

        # WAIT
        return 0.0
