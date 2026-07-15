"""Unified Signal Generator — Menggabungkan Semua Engine Menjadi Satu Output Powerful.

Mengintegrasikan:
- Statistical Engine (probability)
- AI Engine (XGBoost/LightGBM + SHAP)
- Risk Engine (position sizing)
- Market Structure (BOS, CHOCH, FVG)
- Multi-Timeframe Confirmation (H1, H4, D1)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

import numpy as np
import pandas as pd


@dataclass
class CompositeScoreBreakdown:
    """Structured breakdown used to explain confidence."""
    market_structure: float = 0.0
    momentum: float = 0.0
    trend: float = 0.0
    volatility: float = 0.0
    ai_prediction: float = 0.0

    def to_dict(self) -> dict:
        return {
            "market_structure": round(self.market_structure, 2),
            "momentum": round(self.momentum, 2),
            "trend": round(self.trend, 2),
            "volatility": round(self.volatility, 2),
            "ai_prediction": round(self.ai_prediction, 2),
        }

from al_syaka_features import FeaturePipeline
from al_syaka_indicators import IndicatorCalculator
from al_syaka_quant import MeanReversionStrategy
from src.collectors.manager import DataCollector
from src.final_decision import FinalDecisionEngine
from src.macro_bias import MacroBiasEngine
from src.market_structure import (MarketStructureDetector,
                                  SupportResistanceDetector, detect_fvg,
                                  detect_liquidity_sweep)
from src.statistical_engine import ProbabilityEngine


@dataclass
class UnifiedSignal:
    """Output signal yang lengkap — seperti yang diminta PRD."""
    symbol: str
    timestamp: datetime
    signal: str  # BUY, SELL, NEUTRAL
    confidence: float  # 0-100%
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward: Optional[float]
    risk_level: str
    reasons: list[str]
    indicators_used: list[str]
    # Market structure
    market_trend: str
    swing_highs: int
    swing_lows: int
    bos_count: int
    choch_count: int
    fvg_count: int
    liquidity_sweeps: int
    # Multi-timeframe
    h1_signal: str = ""
    h4_signal: str = ""
    d1_signal: str = ""
    # AI (if available)
    ai_confidence: Optional[float] = None
    ai_accuracy: Optional[float] = None
    shap_reasons: list[str] = field(default_factory=list)
    shap_summary: Optional[str] = None
    feature_contributions: Optional[dict] = None
    explanation_reason: Optional[str] = None
    # Trade setup
    lot_size: Optional[float] = None
    trade_quality: str = ""
    signal_id: Optional[str] = None
    quant_strategy: Optional[dict] = None
    composite_score: Optional[float] = None
    confidence_breakdown: Optional[dict] = None
    confidence_label: Optional[str] = None
    market_regime: Optional[str] = None
    strategy_mode: Optional[str] = None
    regime_reason: Optional[str] = None
    # Macro bias
    macro_bias: Optional[str] = None
    macro_strength: Optional[float] = None
    macro_confidence: Optional[float] = None
    macro_reason: Optional[str] = None
    macro_events: list = field(default_factory=list)
    # Final decision
    final_decision: Optional[str] = None
    decision_reason: Optional[str] = None
    conflict_detected: Optional[bool] = None
    hedge_intensity: Optional[str] = None
    decision_confidence: Optional[float] = None
    position_multiplier: Optional[float] = None


class UnifiedSignalGenerator:
    """One generator to rule them all — unified signal dengan semua analisis."""

    def __init__(self):
        self.collector = DataCollector()
        self.probability_engine = ProbabilityEngine()
        self.structure_detector = MarketStructureDetector()
        self.sr_detector = SupportResistanceDetector()
        self.macro_engine = MacroBiasEngine()
        self.decision_engine = FinalDecisionEngine()

    async def generate(
        self,
        symbol: str,
        timeframe: str = "H1",
        include_ai: bool = False,
    ) -> UnifiedSignal:
        """Generate unified signal untuk satu symbol."""
        # Fetch data for main timeframe + higher timeframes
        df_h1 = await self._fetch_data(symbol, "H1", 200)
        df_h4 = await self._fetch_data(symbol, "H4", 100) if timeframe != "H4" else df_h1
        df_d1 = await self._fetch_data(symbol, "D1", 60) if timeframe != "D1" else df_h1

        # Gunakan timeframe yang diminta
        df = df_h1 if timeframe == "H1" else (df_h4 if timeframe == "H4" else df_d1)

        if df.empty:
            raise ValueError(f"No data available for {symbol}")

        # 1. Compute indicators
        indicators = self._compute_indicators(df)
        indicators_list = self._latest_values(indicators)

        # 2. Market Structure analysis
        structure = self._analyze_structure(df)

        # 3. Probability (Statistical Engine)
        prob = self.probability_engine.evaluate(indicators_list, structure)

        # 4. Multi-timeframe signals
        tf_h1 = await self._tf_signal(df_h1) if timeframe != "H1" else None
        tf_h4 = await self._tf_signal(df_h4) if timeframe != "H4" else None
        tf_d1 = await self._tf_signal(df_d1) if timeframe != "D1" else None

        # 5. Entry, SL, TP
        entry = float(df["close"].iloc[-1])
        atr_val = indicators_list.get("atr_14", [0.001])[-1] if isinstance(indicators_list.get("atr_14"), (list, np.ndarray)) else 0.001
        sl = entry - (atr_val * 1.5) if prob.signal == "BUY" else entry + (atr_val * 1.5)
        tp = entry + (atr_val * 3.0) if prob.signal == "BUY" else entry - (atr_val * 3.0)
        rr = round(abs(tp - entry) / abs(sl - entry), 2) if sl != entry else 1.0

        # 6. AI prediction (optional — slow)
        ai_conf = None
        ai_acc = None
        ai_reasons = []
        ai_shap_summary = None
        ai_feature_contributions = None
        ai_explanation_reason = None
        if include_ai:
            try:
                (
                    ai_conf, ai_acc, ai_reasons,
                    ai_shap_summary, ai_feature_contributions,
                    ai_explanation_reason,
                ) = await self._ai_predict(df)
            except Exception:
                pass

        # 7. Composite score + regime detection
        composite = self._calculate_composite_score(indicators_list, structure, ai_conf)
        regime = self._detect_market_regime(indicators_list, structure)

        # 8. Macro bias analysis (use higher timeframe data)
        macro_result = self._analyze_macro(df_h4, df_d1, symbol)

        # 9. Final decision
        decision_result = self.decision_engine.decide(
            technical_signal=prob.signal,
            technical_confidence=round(prob.confidence * 100, 0),
            composite_score=composite["composite_score"],
            market_regime=regime["market_regime"],
            macro_bias=macro_result["macro_bias"],
            macro_confidence=macro_result["macro_confidence"],
            macro_strength=macro_result["macro_strength"],
        )

        # 10. Add quant strategy signal
        quant_signal = self._build_quant_signal(df, symbol)

        # 11. Build final reasons
        reasons = prob.reasons[:4]
        reasons.append(f"Market regime: {regime['market_regime'].lower()}")
        if quant_signal:
            reasons.append(
                f"Quant strategy: {quant_signal['action']} via {quant_signal['strategy']}"
            )
        macro_reason_text = macro_result.get("macro_reason", "")
        if macro_reason_text:
            reasons.append(f"Macro: {macro_reason_text}")
        if structure.get("current_trend"):
            reasons.insert(0, f"Market Trend: {structure['current_trend']}")
        if ai_reasons:
            reasons.extend(ai_reasons[:2])
        if decision_result.get("decision_reason"):
            reasons.append(f"Decision: {decision_result['decision_reason']}")

        # 8. Indicators used
        used_inds = self._extract_indicators_used(indicators_list)

        return UnifiedSignal(
            symbol=symbol,
            timestamp=datetime.utcnow(),
            signal=prob.signal,
            confidence=round(prob.confidence * 100, 0),
            entry_price=round(entry, 5),
            stop_loss=round(sl, 5),
            take_profit=round(tp, 5),
            risk_reward=rr,
            risk_level=prob.risk_level,
            reasons=reasons[:6],
            indicators_used=used_inds[:8],
            market_trend=structure.get("current_trend", "NEUTRAL"),
            swing_highs=len(structure.get("swing_highs", [])),
            swing_lows=len(structure.get("swing_lows", [])),
            bos_count=len(structure.get("break_of_structure", [])),
            choch_count=len(structure.get("change_of_character", [])),
            fvg_count=len(structure.get("fair_value_gaps", [])),
            liquidity_sweeps=len(structure.get("liquidity_sweeps", [])),
            h1_signal=tf_h1 or prob.signal,
            h4_signal=tf_h4 or "",
            d1_signal=tf_d1 or "",
            ai_confidence=ai_conf,
            ai_accuracy=ai_acc,
            shap_reasons=ai_reasons,
            shap_summary=ai_shap_summary,
            feature_contributions=ai_feature_contributions,
            explanation_reason=ai_explanation_reason,
            trade_quality="GOOD" if prob.confidence >= 0.65 else "FAIR",
            quant_strategy=quant_signal,
            composite_score=composite["composite_score"],
            confidence_breakdown=composite["confidence_breakdown"],
            confidence_label=composite["confidence_label"],
            market_regime=regime["market_regime"],
            strategy_mode=regime["strategy_mode"],
            regime_reason=regime["regime_reason"],
            macro_bias=macro_result.get("macro_bias"),
            macro_strength=macro_result.get("macro_strength"),
            macro_confidence=macro_result.get("macro_confidence"),
            macro_reason=macro_result.get("macro_reason"),
            macro_events=macro_result.get("macro_events", []),
            final_decision=decision_result.get("final_decision"),
            decision_reason=decision_result.get("decision_reason"),
            conflict_detected=decision_result.get(
                "conflict_detected",
            ),
            hedge_intensity=decision_result.get("hedge_intensity"),
            decision_confidence=decision_result.get(
                "decision_confidence",
            ),
            position_multiplier=decision_result.get(
                "position_multiplier",
            ),
        )

    async def _fetch_data(self, symbol: str, timeframe: str, limit: int) -> pd.DataFrame:
        """Fetch OHLC data and return as DataFrame."""
        from datetime import timezone
        end = datetime.now(timezone.utc)
        days_map = {"M1": 1, "M5": 1, "M15": 2, "M30": 3, "H1": 5, "H4": 7, "D1": 60}
        days = min(days_map.get(timeframe, 5), 7)  # Max 7 days to use period param
        start = end - timedelta(days=days)

        try:
            data = await self.collector.fetch_ohlc(symbol, timeframe, start, end)
            if not data:
                return pd.DataFrame()
            df = pd.DataFrame([{
                "timestamp": d.timestamp, "open": d.open, "high": d.high,
                "low": d.low, "close": d.close, "volume": d.volume or 0,
            } for d in data])
            return df
        except Exception:
            return pd.DataFrame()

    def _compute_indicators(self, df: pd.DataFrame) -> dict:
        """Compute all indicators from DataFrame."""
        calc = IndicatorCalculator({
            "open": df["open"], "high": df["high"],
            "low": df["low"], "close": df["close"],
            "volume": df["volume"],
        })
        return calc.compute_all()

    def _latest_values(self, indicators: dict) -> dict:
        """Convert Series to latest values for probability engine."""
        result = {}
        for k, v in indicators.items():
            if isinstance(v, pd.Series):
                result[k] = v.fillna(0).tolist()
            elif isinstance(v, dict):
                result[k] = {sk: sv.tolist() if isinstance(sv, pd.Series) else sv for sk, sv in v.items()}
            else:
                result[k] = v
        return result

    def _analyze_structure(self, df: pd.DataFrame) -> dict:
        """Run full market structure analysis."""
        structure = self.structure_detector.analyze(df["high"], df["low"])
        sr = self.sr_detector.detect(df["high"], df["low"])
        fvg = detect_fvg(df["high"], df["low"], df["close"])
        sweeps = detect_liquidity_sweep(df["high"], df["low"], df["close"])
        return {**structure, "support_resistance": sr, "fair_value_gaps": fvg, "liquidity_sweeps": sweeps}

    async def _tf_signal(self, df: pd.DataFrame) -> Optional[str]:
        """Get signal direction for a timeframe."""
        if df.empty:
            return None
        indicators = self._compute_indicators(df)
        latest = self._latest_values(indicators)
        structure = self._analyze_structure(df)
        prob = self.probability_engine.evaluate(latest, structure)
        return prob.signal if prob.confidence >= 0.55 else "NEUTRAL"

    def _calculate_composite_score(self, indicators: dict, structure: dict, ai_confidence: Optional[float]) -> dict:
        """Create a composite score from multiple signal components."""
        try:
            rsi = indicators.get("rsi_14", [50])[-1] if isinstance(indicators.get("rsi_14"), (list, np.ndarray)) else 50
            adx = indicators.get("adx_adx", [0])[-1] if isinstance(indicators.get("adx_adx"), (list, np.ndarray)) else 0
            ema_12 = indicators.get("ema_12", [0])[-1] if isinstance(indicators.get("ema_12"), (list, np.ndarray)) else 0
            ema_20 = indicators.get("ema_20", [0])[-1] if isinstance(indicators.get("ema_20"), (list, np.ndarray)) else 0
            ema_50 = indicators.get("ema_50", [0])[-1] if isinstance(indicators.get("ema_50"), (list, np.ndarray)) else 0
            atr = indicators.get("atr_14", [0.001])[-1] if isinstance(indicators.get("atr_14"), (list, np.ndarray)) else 0.001

            trend_component = 50.0
            if ema_12 and ema_20 and ema_50:
                trend_component = 50 + min(40, max(0, ((ema_12 - ema_20) / max(atr, 0.0001)) * 10))
                trend_component = max(10, min(90, trend_component))

            momentum_component = 50.0
            if rsi:
                if rsi > 60:
                    momentum_component = min(90, 50 + (rsi - 60) * 1.2)
                elif rsi < 40:
                    momentum_component = max(10, 50 - (40 - rsi) * 1.2)

            structure_component = 50.0
            if structure.get("break_of_structure"):
                structure_component += 15
            if structure.get("change_of_character"):
                structure_component += 10
            if structure.get("fair_value_gaps"):
                structure_component += 10
            structure_component = max(20, min(90, structure_component))

            volatility_component = 60.0
            if adx >= 25:
                volatility_component = 75.0
            elif adx <= 15:
                volatility_component = 45.0

            ai_component = 50.0
            if ai_confidence is not None:
                ai_component = max(10, min(90, ai_confidence * 100))

            breakdown = {
                "market_structure": round(structure_component, 2),
                "momentum": round(momentum_component, 2),
                "trend": round(trend_component, 2),
                "volatility": round(volatility_component, 2),
                "ai_prediction": round(ai_component, 2),
            }
            # Optimized weights via Optuna Bayesian Optimization (Iteration 006)
            # Momentum (RSI) and Trend (EMA) are strongest predictors
            composite = round(
                breakdown["market_structure"] * 0.07
                + breakdown["momentum"] * 0.47
                + breakdown["trend"] * 0.28
                + breakdown["volatility"] * 0.09
                + breakdown["ai_prediction"] * 0.09,
                1,
            )
            label = "LOW"
            if composite >= 75:
                label = "HIGH"
            elif composite >= 55:
                label = "MEDIUM"
            return {
                "composite_score": round(composite, 1),
                "confidence_breakdown": breakdown,
                "confidence_label": label,
            }
        except Exception:
            return {
                "composite_score": 50.0,
                "confidence_breakdown": {
                    "market_structure": 50.0,
                    "momentum": 50.0,
                    "trend": 50.0,
                    "volatility": 50.0,
                    "ai_prediction": 50.0,
                },
                "confidence_label": "LOW",
            }

    def _detect_market_regime(self, indicators: dict, structure: dict) -> dict:
        """Detect a trading regime from market structure and momentum."""
        try:
            adx = indicators.get("adx_adx", [0])[-1] if isinstance(indicators.get("adx_adx"), (list, np.ndarray)) else 0
            rsi = indicators.get("rsi_14", [50])[-1] if isinstance(indicators.get("rsi_14"), (list, np.ndarray)) else 50
            has_bos = bool(structure.get("break_of_structure"))
            has_choch = bool(structure.get("change_of_character"))

            if adx >= 25 and has_bos:
                regime = "TRENDING"
                strategy_mode = "trend_following"
                reason = "Strong trend with breakout structure"
            elif rsi > 70 or rsi < 30:
                regime = "REVERSAL"
                strategy_mode = "breakout"
                reason = "Momentum is stretched and reversal risk is elevated"
            elif adx <= 15 and not has_bos and not has_choch:
                regime = "RANGE"
                strategy_mode = "mean_reversion"
                reason = "Price is oscillating without strong directional break"
            else:
                regime = "VOLATILE"
                strategy_mode = "adaptive"
                reason = "Market is active but not clearly directional"

            return {
                "market_regime": regime,
                "strategy_mode": strategy_mode,
                "regime_reason": reason,
            }
        except Exception:
            return {
                "market_regime": "VOLATILE",
                "strategy_mode": "adaptive",
                "regime_reason": "Fallback regime detection",
            }

    def _build_quant_signal(self, df: pd.DataFrame, symbol: str) -> Optional[dict]:
        """Build a lightweight quant signal using the new quant package."""
        try:
            if df.empty or "close" not in df.columns:
                return None

            strategy = MeanReversionStrategy(symbol=symbol, window=3)
            signals = strategy.generate(df[["close"]].copy())
            if not signals:
                return None

            latest = signals[-1]
            return {
                "strategy": strategy.__class__.__name__,
                "action": latest.action,
                "confidence": round(latest.confidence, 2),
            }
        except Exception:
            return None

    async def _ai_predict(self, df: pd.DataFrame) -> tuple:
        """Quick AI prediction (XGBoost)."""
        from al_syaka_ai import ExplainableAI, MLPipeline, XGBoostModel

        pipeline = FeaturePipeline()
        features = pipeline.compute(
            open=df["open"], high=df["high"], low=df["low"],
            close=df["close"], volume=df["volume"],
        )
        features = features.replace([np.inf, -np.inf], np.nan).dropna()
        if len(features) < 30:
            return None, None, [], None, None, None

        close_series = df["close"].loc[features.index]
        future_ret = close_series.shift(-12) / close_series - 1
        labels = (future_ret > 0.003).astype(int).dropna()
        features = features.loc[labels.index]

        split = int(len(features) * 0.8)
        X_train, X_test = features.iloc[:split], features.iloc[split:]
        y_train, y_test = labels.iloc[:split], labels.iloc[split:]

        if len(X_train) < 20:
            return None, None, [], None, None, None

        model = XGBoostModel()
        model.train(X_train, y_train)
        metrics = model.evaluate(X_test, y_test)

        explainer = ExplainableAI(model, X_train.columns.tolist())
        explainer.fit(X_train.iloc[:50])
        explanation = explainer.explain(X_test.iloc[-1:])

        conf = explanation["confidence"]
        acc = round(metrics.get("accuracy", 0) * 100, 1)
        reasons = explanation["reasons"]
        shap_summary = explanation.get("shap_summary")
        feature_contributions = explanation.get("feature_contributions")
        explanation_reason = explanation.get("explanation_reason")
        return (
            conf, acc, reasons,
            shap_summary, feature_contributions, explanation_reason,
        )

    def _extract_indicators_used(self, indicators: dict) -> list[str]:
        """Extract list of indicator names used."""
        used = []
        key_map = {
            "rsi_14": "RSI", "ema_12": "EMA 12", "ema_20": "EMA 20",
            "ema_50": "EMA 50", "sma_200": "SMA 200", "macd_macd": "MACD",
            "adx_adx": "ADX", "atr_14": "ATR", "bb_upper": "Bollinger",
            "supertrend": "Supertrend",
        }
        for key, label in key_map.items():
            if key in indicators:
                used.append(label)
        return used[:8]

    def _analyze_macro(
        self, df_h4, df_d1, symbol: str = "",
    ) -> dict:
        """Analyze macro bias from higher timeframe data."""
        try:
            trend_h4 = self._get_trend_from_df(df_h4)
            trend_d1 = self._get_trend_from_df(df_d1)

            ind_h4 = self._compute_indicators(df_h4) if not df_h4.empty else {}
            ind_d1 = self._compute_indicators(df_d1) if not df_d1.empty else {}

            def _safe_get(indicators, key, default=None):
                vals = indicators.get(key)
                if isinstance(vals, (list, np.ndarray)) and len(vals) > 0:
                    return vals[-1]
                if isinstance(vals, pd.Series) and not vals.empty:
                    return vals.iloc[-1]
                return default

            rsi_h4 = _safe_get(ind_h4, "rsi_14")
            rsi_d1 = _safe_get(ind_d1, "rsi_14")
            adx_h4 = _safe_get(ind_h4, "adx_adx")
            adx_d1 = _safe_get(ind_d1, "adx_adx")
            atr_h4 = _safe_get(ind_h4, "atr_14")
            atr_d1 = _safe_get(ind_d1, "atr_14")

            return self.macro_engine.analyze(
                trend_h4=trend_h4,
                trend_d1=trend_d1,
                rsi_h4=rsi_h4,
                rsi_d1=rsi_d1,
                adx_h4=adx_h4,
                adx_d1=adx_d1,
                volatility_h4=atr_h4,
                volatility_d1=atr_d1,
                symbol=symbol,
            )
        except Exception:
            return {
                "macro_bias": "NEUTRAL",
                "macro_strength": 0.0,
                "macro_confidence": 0.0,
                "macro_reason": "Macro analysis unavailable",
            }

    def _get_trend_from_df(self, df) -> str:
        """Infer trend direction from OHLC dataframe."""
        if df.empty or "close" not in df.columns:
            return "NEUTRAL"
        try:
            closes = df["close"].values
            if len(closes) < 20:
                return "NEUTRAL"
            sma_20 = np.mean(closes[-20:])
            sma_50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma_20
            current = closes[-1]
            if current > sma_20 > sma_50:
                return "BULLISH"
            if current < sma_20 < sma_50:
                return "BEARISH"
            return "NEUTRAL"
        except Exception:
            return "NEUTRAL"
