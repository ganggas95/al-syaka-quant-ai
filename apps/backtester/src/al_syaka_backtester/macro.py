"""Backtest Macro Engine — H4/D1 Resampling + Macro Analysis for Backtesting.

Self-contained macro engine that resamples H1 data to H4/D1 and provides
timestamp-aware macro analysis without lookahead bias.

No external dependencies beyond numpy/pandas (forks MacroBiasEngine logic
to avoid importing from the API package).
"""

from typing import Optional

import numpy as np
import pandas as pd

# Symbol class confidence multipliers (mirrors apps/api/src/macro_bias.py)
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


class BacktestMacroEngine:
    """Macro engine for backtesting with H4/D1 resampling from H1 data.

    Resamples H1 OHLC data to H4 and D1 timeframes, pre-computes indicators,
    and provides timestamp-aware lookups to avoid lookahead bias.

    Usage:
        engine = BacktestMacroEngine(h1_dataframe)
        macro = engine.analyze_at(timestamp, symbol="XAUUSD")
    """

    def __init__(self, df: pd.DataFrame):
        self.h1_df = df

        # Resample H1 -> H4, D1
        self.h4_df, self.h4_available_at = self._resample_h1_to_h4(df)
        self.d1_df, self.d1_available_at = self._resample_h1_to_d1(df)

        # Pre-compute indicators on higher timeframes
        self.h4_inds = self._compute_tf_indicators(self.h4_df)
        self.d1_inds = self._compute_tf_indicators(self.d1_df)

    # ------------------------------------------------------------------
    # Resampling Logic
    # ------------------------------------------------------------------

    @staticmethod
    def _resample_h1_to_h4(df: pd.DataFrame):
        """Resample H1 -> H4 by grouping every 4 consecutive bars."""
        n = 4
        # Use positional index (0, 1, 2, ...) for grouping
        indices = np.arange(len(df))
        groups = indices // n

        h4_df = pd.DataFrame({
            "timestamp": df["timestamp"].groupby(groups, sort=False).last(),
            "open": df["open"].groupby(groups, sort=False).first(),
            "high": df["high"].groupby(groups, sort=False).max(),
            "low": df["low"].groupby(groups, sort=False).min(),
            "close": df["close"].groupby(groups, sort=False).last(),
        }).reset_index(drop=True)

        # available_at = timestamp of the last H1 bar in each H4 group
        available_at = df["timestamp"].groupby(groups, sort=False).last().values

        return h4_df, available_at

    @staticmethod
    def _resample_h1_to_d1(df: pd.DataFrame):
        """Resample H1 -> D1 by grouping by calendar date."""
        # Extract date from timestamp
        dates = df["timestamp"].apply(
            lambda t: t.date() if hasattr(t, "date") else str(t)[:10]
        )
        # Preserve order — groupby with sort=False
        groups = pd.factorize(dates)[0]

        d1_df = pd.DataFrame({
            "timestamp": df["timestamp"].groupby(groups, sort=False).last(),
            "open": df["open"].groupby(groups, sort=False).first(),
            "high": df["high"].groupby(groups, sort=False).max(),
            "low": df["low"].groupby(groups, sort=False).min(),
            "close": df["close"].groupby(groups, sort=False).last(),
        }).reset_index(drop=True)

        available_at = df["timestamp"].groupby(groups, sort=False).last().values

        return d1_df, available_at

    # ------------------------------------------------------------------
    # Indicator Computation
    # ------------------------------------------------------------------

    def _compute_tf_indicators(self, tf_df: pd.DataFrame) -> dict:
        """Compute indicators needed for macro analysis on a timeframe."""
        if tf_df.empty or len(tf_df) < 20:
            return {}
        from al_syaka_indicators import IndicatorCalculator

        calc = IndicatorCalculator({
            "open": tf_df["open"],
            "high": tf_df["high"],
            "low": tf_df["low"],
            "close": tf_df["close"],
        })
        return calc.compute_all()

    # ------------------------------------------------------------------
    # Timestamp Lookup (no lookahead)
    # ------------------------------------------------------------------

    def _find_index(self, tf_df: pd.DataFrame, timestamp) -> int:
        """Find last row index in tf_df whose timestamp <= given timestamp.

        Returns -1 if no such row exists (avoid lookahead bias).
        """
        if tf_df.empty:
            return -1
        mask = tf_df["timestamp"] <= timestamp
        if not mask.any():
            return -1
        return mask.sum() - 1  # Last True index (timestamps are sorted)

    def _safe_val(self, inds: dict, key: str, idx: int) -> Optional[float]:
        """Get scalar value from indicators dict at given index."""
        if key not in inds or idx < 0:
            return None
        vals = inds[key]
        if isinstance(vals, pd.Series) and not vals.empty and idx < len(vals):
            v = vals.iloc[idx]
            return float(v) if not pd.isna(v) else None
        if isinstance(vals, (list, np.ndarray)) and idx < len(vals):
            v = vals[idx]
            return float(v) if not (v is None or (isinstance(v, float) and np.isnan(v))) else None
        return None

    # ------------------------------------------------------------------
    # Trend Detection
    # ------------------------------------------------------------------

    def _get_trend_at(self, tf_df: pd.DataFrame, idx: int) -> str:
        """Determine trend direction at given index using SMA comparison."""
        if idx < 20 or tf_df.empty:
            return "NEUTRAL"
        closes = tf_df["close"].values[: idx + 1]
        if len(closes) < 20:
            return "NEUTRAL"
        sma20 = np.mean(closes[-20:])
        sma50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma20
        current = closes[-1]
        if current > sma20 > sma50:
            return "BULLISH"
        if current < sma20 < sma50:
            return "BEARISH"
        return "NEUTRAL"

    # ------------------------------------------------------------------
    # Macro Analysis (mirrors MacroBiasEngine logic)
    # ------------------------------------------------------------------

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

        if trend_h4 == "BULLISH":
            bullish_signals += 2
        elif trend_h4 == "BEARISH":
            bearish_signals += 2

        if trend_d1 == "BULLISH":
            bullish_signals += 3
        elif trend_d1 == "BEARISH":
            bearish_signals += 3

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
        """Calculate macro confidence (0-100) based on alignment."""
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
    ) -> str:
        """Generate human-readable macro reason."""
        if bias == "NEUTRAL":
            return (
                "Macro bias is neutral — no clear directional "
                "conviction across timeframes"
            )

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

        return (
            f"Macro bias is {bias.lower()} ({strength_desc}, "
            f"confidence {confidence:.0f}%). {alignment}."
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze_at(self, timestamp, symbol: str = "") -> dict:
        """Get macro analysis at a specific point in time (no lookahead).

        Args:
            timestamp: The current backtest timestamp.
            symbol: Symbol name for confidence adjustment.

        Returns:
            dict with keys: macro_bias, macro_strength, macro_confidence,
            macro_reason, macro_events.
        """
        try:
            h4_idx = self._find_index(self.h4_df, timestamp)
            d1_idx = self._find_index(self.d1_df, timestamp)

            trend_h4 = self._get_trend_at(self.h4_df, h4_idx)
            trend_d1 = self._get_trend_at(self.d1_df, d1_idx)

            rsi_h4 = self._safe_val(self.h4_inds, "rsi_14", h4_idx)
            rsi_d1 = self._safe_val(self.d1_inds, "rsi_14", d1_idx)
            adx_h4 = self._safe_val(self.h4_inds, "adx_adx", h4_idx)
            adx_d1 = self._safe_val(self.d1_inds, "adx_adx", d1_idx)
            vol_h4 = self._safe_val(self.h4_inds, "atr_14", h4_idx)
            vol_d1 = self._safe_val(self.d1_inds, "atr_14", d1_idx)

            bias = self._determine_bias(trend_h4, trend_d1, rsi_h4, rsi_d1)
            strength = self._calculate_strength(
                adx_h4, adx_d1, vol_h4, vol_d1,
            )
            confidence = self._calculate_confidence(
                trend_h4, trend_d1, adx_h4, adx_d1, symbol=symbol,
            )

            return {
                "macro_bias": bias,
                "macro_strength": round(strength, 1),
                "macro_confidence": round(confidence, 1),
                "macro_reason": self._generate_reason(
                    bias, strength, confidence, trend_h4, trend_d1,
                ),
                "macro_events": [],
            }
        except Exception:
            return {
                "macro_bias": "NEUTRAL",
                "macro_strength": 0.0,
                "macro_confidence": 0.0,
                "macro_reason": "Backtest macro analysis unavailable",
                "macro_events": [],
            }


def _resolve_final_decision(
    technical_signal: str,
    technical_confidence: float,
    regime: str,
    macro_result: dict,
) -> dict:
    """Resolve final decision with technical-macro conflict handling.

    Mirrors FinalDecisionEngine logic for backtest use.
    Priority chain:
    1. Macro override (strong macro overrides weak technical)
    2. Conflict -> HEDGE (skip trade)
    3. Strong technical signal
    4. Moderate technical with macro support
    5. Low confidence -> WAIT

    Returns:
        dict with keys: final_decision, decision_confidence, conflict_detected
    """
    try:
        macro_bias = macro_result.get("macro_bias", "NEUTRAL")
        macro_conf = macro_result.get("macro_confidence", 0.0)
        macro_strength = macro_result.get("macro_strength", 0.0)
        confidence = technical_confidence * 100  # Convert to 0-100 scale

        # --- Conflict detection ---
        conflict = False
        if macro_conf >= 30 and macro_strength >= 20 and macro_bias != "NEUTRAL":
            direct_conflict = (
                (technical_signal == "BUY" and macro_bias == "BEARISH")
                or (technical_signal == "SELL" and macro_bias == "BULLISH")
            )

            # Macro override: strong macro + weak tech -> no conflict, follow macro
            macro_override = (
                macro_conf >= 60
                and macro_strength >= 50
                and confidence < 50
                and direct_conflict
            )

            if macro_override:
                macro_dir = "BUY" if macro_bias == "BULLISH" else "SELL"
                dec_conf = min(80, 60 + macro_conf * 0.2)
                return {
                    "final_decision": macro_dir,
                    "decision_confidence": round(dec_conf, 1),
                    "conflict_detected": False,
                }

            if direct_conflict:
                conflict = True

        # --- Decision resolution ---
        if conflict:
            return {
                "final_decision": "HEDGE",
                "decision_confidence": round(
                    min(60, (confidence + macro_conf) / 2.0 * 0.6), 1
                ),
                "conflict_detected": True,
            }

        # Strong technical signal
        if confidence >= 70 and technical_signal != "NEUTRAL":
            return {
                "final_decision": technical_signal,
                "decision_confidence": round(min(100, max(50, confidence)), 1),
                "conflict_detected": False,
            }

        # Moderate technical with macro support
        if confidence >= 40 and technical_signal != "NEUTRAL":
            macro_aligned = (
                (macro_bias == "BULLISH" and technical_signal == "BUY")
                or (macro_bias == "BEARISH" and technical_signal == "SELL")
            )
            if macro_aligned:
                return {
                    "final_decision": technical_signal,
                    "decision_confidence": round(confidence, 1),
                    "conflict_detected": False,
                }
            else:
                # Tech without macro support — reduce confidence
                return {
                    "final_decision": technical_signal,
                    "decision_confidence": round(confidence * 0.75, 1),
                    "conflict_detected": False,
                }

        # Low confidence or neutral
        if technical_signal == "NEUTRAL" or confidence < 30:
            return {
                "final_decision": "WAIT",
                "decision_confidence": 0.0,
                "conflict_detected": False,
            }

        # Default fallback
        return {
            "final_decision": "WAIT",
            "decision_confidence": 0.0,
            "conflict_detected": False,
        }

    except Exception:
        return {
            "final_decision": "WAIT",
            "decision_confidence": 0.0,
            "conflict_detected": False,
        }
