"""Explainable AI — SHAP-based explanation untuk setiap prediksi sinyal.

Output yang dihasilkan seperti yang diminta PRD:
BUY
Confidence: 84%
Reason:
  - EMA20 > EMA50 (Bullish Cross)
  - ATR naik (Volatility Meningkat)
  - RSI 61 (Momentum Bullish)
  - London Session
  - DXY turun
"""

from typing import Optional

import numpy as np
import pandas as pd
import shap

from .models.base import BaseModel


class ExplainableAI:
    """SHAP-based explainability untuk setiap prediksi model."""

    def __init__(self, model: BaseModel, feature_names: list[str]):
        self.model = model
        self.feature_names = feature_names
        self.explainer = None
        self.base_value = None

    def fit(self, X_background: pd.DataFrame):
        """Fit SHAP explainer using background data."""
        if self.model.name == "xgboost" or self.model.name == "lightgbm":
            self.explainer = shap.TreeExplainer(self.model.model)
        else:
            # For Transformer or other models, use KernelExplainer
            self.explainer = shap.KernelExplainer(
                self.model.predict_proba,
                shap.sample(X_background.values, 100, random_state=42),
            )
        self.base_value = self.explainer.expected_value

    def explain(self, X: pd.DataFrame) -> dict:
        """Generate explanation untuk satu atau lebih sampel."""
        if self.explainer is None:
            raise ValueError("Call fit() first with background data")

        # Get SHAP values
        shap_values = self.explainer.shap_values(X)

        # Handle binary classification (shap_values is list for TreeExplainer)
        if isinstance(shap_values, list):
            shap_values = shap_values[1]  # Class 1 (BUY) probabilities

        # Convert to DataFrame
        shap_df = pd.DataFrame(
            shap_values, columns=self.feature_names, index=X.index
        )

        # Generate natural language reasons
        explanations = []
        for i in range(len(X)):
            row_shap = shap_df.iloc[i]
            row_X = X.iloc[i]

            # Get top contributing features
            top_features = row_shap.abs().sort_values(ascending=False).head(5)

            reasons = []
            positive_features = []
            negative_features = []
            for feat in top_features.index:
                impact = row_shap[feat]
                value = row_X[feat]
                reason = self._feature_to_reason(feat, value, impact)
                if reason:
                    reasons.append(reason)
                    if impact > 0:
                        positive_features.append(feat)
                    else:
                        negative_features.append(feat)

            # Predict probability
            proba = self.model.predict_proba(X.iloc[i:i+1])
            if isinstance(proba, np.ndarray) and proba.ndim >= 2:
                buy_prob = (
                    float(proba[0][1])
                    if proba.shape[1] > 1
                    else float(proba[0][0])
                )
            else:
                buy_prob = float(proba)

            signal = "BUY" if buy_prob >= 0.5 else "SELL"
            confidence = round(max(buy_prob, 1 - buy_prob) * 100, 0)

            # Build shap_summary — concise ringkasan
            pos_count = len(positive_features)
            neg_count = len(negative_features)
            conf_str = f"{confidence:.0f}%"
            if signal == "BUY":
                summary = (
                    f"Model memprediksi BUY dengan confidence {conf_str}. "
                    f"Faktor positif ({pos_count}) mendominasi "
                    f"faktor negatif ({neg_count})."
                )
            else:
                summary = (
                    f"Model memprediksi SELL dengan confidence {conf_str}. "
                    f"Faktor negatif ({neg_count}) mendominasi "
                    f"faktor positif ({pos_count})."
                )

            # Build explanation_reason — naratif sederhana
            if reasons:
                top_reason = (
                    reasons[0].split(":")[0]
                    if ":" in reasons[0]
                    else reasons[0]
                )
                reason_text = (
                    f"Keputusan {signal} terutama dipengaruhi oleh "
                    f"{top_reason.lower()}. "
                    f"Secara keseluruhan, {len(reasons)} faktor dianalisis "
                    f"dengan {pos_count} faktor mendukung dan "
                    f"{neg_count} faktor menahan."
                )
            else:
                reason_text = (
                    f"Keputusan {signal} berdasarkan analisis model "
                    f"dengan confidence {conf_str}."
                )

            # Feature contributions — daftar kontribusi tiap fitur
            feature_contributions = {}
            for feat in top_features.index:
                direction = (
                    "positive" if row_shap[feat] > 0 else "negative"
                )
                feature_contributions[feat] = {
                    "value": round(float(row_X[feat]), 4),
                    "shap_impact": round(float(row_shap[feat]), 4),
                    "direction": direction,
                }

            shap_vals = {
                feat: round(float(row_shap[feat]), 4)
                for feat in top_features.index
            }
            feat_vals = {
                feat: round(float(row_X[feat]), 4)
                for feat in top_features.index
            }
            explanations.append({
                "signal": signal,
                "confidence": confidence,
                "reasons": reasons[:5],
                "shap_summary": summary,
                "explanation_reason": reason_text,
                "feature_contributions": feature_contributions,
                "shap_values": shap_vals,
                "feature_values": feat_vals,
            })

        return explanations[0] if len(explanations) == 1 else explanations

    def _feature_to_reason(self, feature: str, value: float,
                           shap_impact: float) -> Optional[str]:
        """Convert feature + SHAP value to human-readable reason."""

        def _rsi(v, imp):
            if v < 30:
                return f"RSI {v:.0f} — Oversold"
            if v > 70:
                return f"RSI {v:.0f} — Overbought"
            return (
                f"RSI {v:.0f} — Momentum Bullish"
                if imp > 0
                else f"RSI {v:.0f} — Momentum Bearish"
            )

        def _atr(v, imp):
            atr_dir = "meningkat" if imp > 0 else "menurun"
            vol_dir = "tinggi" if imp > 0 else "rendah"
            return f"ATR {atr_dir} ({v:.5f}) — Volatility {vol_dir}"

        def _mom(label, v):
            direction = "Bullish" if v > 0 else "Bearish"
            return f"{label} {direction} ({(v*100):.1f}%)"

        def _bb(v):
            if v > 0.8:
                return "Price at upper Bollinger Band"
            if v < 0.2:
                return "Price at lower Bollinger Band"
            return "Price at mid Bollinger Band"

        def _session(name, v):
            return f"{name} {'Active' if v > 0 else 'Inactive'}"

        mapping = {
            "ema_12": ("EMA 12",
                       lambda v, imp: "Bullish" if imp > 0 else "Bearish"),
            "ema_20": ("EMA 20",
                       lambda v, imp: f"{'Bullish' if imp > 0 else 'Bearish'} "
                       f"({v:.2f})"),
            "ema_50": ("EMA 50",
                       lambda v, imp: "Bullish" if imp > 0 else "Bearish"),
            "sma_20": ("SMA 20",
                       lambda v, imp: "Price above SMA 20"
                       if imp > 0 else "Price below SMA 20"),
            "sma_50": ("SMA 50",
                       lambda v, imp: "Price above SMA 50"
                       if imp > 0 else "Price below SMA 50"),
            "sma_200": ("SMA 200",
                        lambda v, imp: "Price above SMA 200 (Bullish)"
                        if imp > 0 else "Price below SMA 200 (Bearish)"),
            "rsi_14": ("RSI", _rsi),
            "atr_14": ("ATR", _atr),
            "ema_distance_20": (
                "EMA Distance",
                lambda v, imp: f"Price {(v/100)*100:.2f}% "
                f"{'above' if imp > 0 else 'below'} EMA 20",
            ),
            "ema_distance_50": (
                "EMA Distance 50",
                lambda v, imp: f"Price {(v/100)*100:.2f}% "
                f"{'above' if imp > 0 else 'below'} EMA 50",
            ),
            "volatility_10": (
                "Volatility",
                lambda v, imp: "Volatility meningkat"
                if imp > 0 else "Volatility menurun",
            ),
            "mom_5": ("Momentum 5", lambda v, imp: _mom("Momentum 5", v)),
            "mom_10": ("Momentum 10", lambda v, imp: _mom("Momentum 10", v)),
            "bb_position": ("Bollinger", lambda v, imp: _bb(v)),
            "london_session": (
                "London Session",
                lambda v, imp: _session("London Session", v),
            ),
            "us_session": (
                "US Session",
                lambda v, imp: _session("US Session", v),
            ),
            "asian_session": (
                "Asian Session",
                lambda v, imp: _session("Asian Session", v),
            ),
            "session_overlap": (
                "Session Overlap",
                lambda v, imp: "London-New York Overlap — High Liquidity"
                if v > 0 else None,
            ),
            "body_ratio": (
                "Candle Body",
                lambda v, imp: f"Candle body ratio {(v*100):.0f}%",
            ),
            "candle_range": (
                "Range",
                lambda v, imp: "Candle range melebar"
                if imp > 0 else "Candle range menyempit",
            ),
        }

        if feature in mapping:
            label, formatter = mapping[feature]
            try:
                reason = formatter(value, shap_impact)
                if reason:
                    return f"{label}: {reason}"
            except Exception:
                return None

        return None

    def get_feature_importance(self) -> pd.DataFrame:
        """Get global feature importance from SHAP."""
        col_names = self.feature_names
        zeros = np.zeros((1, len(self.feature_names)))
        return pd.DataFrame({
            "feature": self.feature_names,
            "importance": np.abs(
                self.explainer.shap_values(
                    pd.DataFrame(zeros, columns=col_names)
                )
            ).mean(0) if self.explainer else 0,
        }).sort_values("importance", ascending=False)
