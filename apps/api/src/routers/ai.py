"""API router for AI model predictions & explainability."""

from datetime import datetime, timedelta
from fastapi import APIRouter, Query, HTTPException
import pandas as pd
import numpy as np

from src.collectors.manager import DataCollector
from al_syaka_ai import (
    MLPipeline,
    XGBoostModel,
    LightGBMModel,
    ExplainableAI,
)
from al_syaka_features import FeaturePipeline

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


@router.get("/predict/{symbol}")
async def ai_predict(
    symbol: str,
    timeframe: str = Query("H1"),
    limit: int = Query(500, le=2000),
):
    """Generate AI-powered prediction with SHAP explanation for a symbol."""
    try:
        collector = DataCollector()
        end = datetime.utcnow()
        start = end - timedelta(days=_tf_to_days(timeframe, limit))

        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")

        df = pd.DataFrame([{
            "timestamp": d.timestamp, "open": d.open, "high": d.high,
            "low": d.low, "close": d.close, "volume": d.volume or 0,
        } for d in data])

        # Prepare features
        pipeline = FeaturePipeline()
        features = pipeline.compute(
            open=df["open"], high=df["high"], low=df["low"],
            close=df["close"], volume=df["volume"],
            timestamps=df["timestamp"],
        )
        features = features.replace([np.inf, -np.inf], np.nan).dropna()

        if len(features) < 50:
            raise HTTPException(status_code=400, detail="Need at least 50 data points")

        # Generate simple labels for quick training
        close_series = df["close"].loc[features.index]
        future_ret = close_series.shift(-12) / close_series - 1
        labels = (future_ret > 0.003).astype(int)
        labels = labels.dropna()
        features = features.loc[labels.index]

        # Train/test split
        split = int(len(features) * 0.8)
        X_train, X_test = features.iloc[:split], features.iloc[split:]
        y_train, y_test = labels.iloc[:split], labels.iloc[split:]

        if len(X_train) < 30 or len(X_test) < 10:
            raise HTTPException(status_code=400, detail="Insufficient data after preprocessing")

        # Train XGBoost model
        model = XGBoostModel()
        model.train(X_train, y_train)

        # Evaluate
        metrics = model.evaluate(X_test, y_test)

        # SHAP explanation on latest data point
        explainer = ExplainableAI(model, X_train.columns.tolist())
        explainer.fit(X_train.iloc[:50])
        explanation = explainer.explain(X_test.iloc[-1:])

        # Feature importance
        importance = model.feature_importance_
        top_features = importance.head(10).to_dict() if importance is not None else {}

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "model": "XGBoost",
            "metrics": {
                "accuracy": round(metrics.get("accuracy", 0) * 100, 1),
                "precision": round(metrics.get("precision", 0) * 100, 1),
                "recall": round(metrics.get("recall", 0) * 100, 1),
                "f1_score": round(metrics.get("f1", 0) * 100, 1),
                "roc_auc": round(metrics.get("roc_auc", 0) * 100, 1),
                "training_samples": len(X_train),
                "test_samples": len(X_test),
            },
            "prediction": {
                "signal": explanation["signal"],
                "confidence": explanation["confidence"],
                "reasons": explanation["reasons"],
            },
            "feature_importance": {k: round(v, 4) for k, v in top_features.items()},
            "explanation": {
                "shap_values": explanation["shap_values"],
                "feature_values": explanation["feature_values"],
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/compare/{symbol}")
async def compare_models(
    symbol: str,
    timeframe: str = Query("H1"),
    limit: int = Query(500, le=2000),
):
    """Compare XGBoost vs LightGBM performance."""
    try:
        collector = DataCollector()
        end = datetime.utcnow()
        start = end - timedelta(days=_tf_to_days(timeframe, limit))

        data = await collector.fetch_ohlc(symbol, timeframe, start, end)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data for {symbol}")

        df = pd.DataFrame([{
            "timestamp": d.timestamp, "open": d.open, "high": d.high,
            "low": d.low, "close": d.close, "volume": d.volume or 0,
        } for d in data])

        # Features
        pipeline = FeaturePipeline()
        features = pipeline.compute(
            open=df["open"], high=df["high"], low=df["low"],
            close=df["close"], volume=df["volume"],
            timestamps=df["timestamp"],
        )
        features = features.replace([np.inf, -np.inf], np.nan).dropna()

        close_series = df["close"].loc[features.index]
        future_ret = close_series.shift(-12) / close_series - 1
        labels = (future_ret > 0.003).astype(int).dropna()
        features = features.loc[labels.index]

        split = int(len(features) * 0.8)
        X_train, X_test = features.iloc[:split], features.iloc[split:]
        y_train, y_test = labels.iloc[:split], labels.iloc[split:]

        # Train both models
        xgb_model = XGBoostModel()
        xgb_model.train(X_train, y_train)
        xgb_metrics = xgb_model.evaluate(X_test, y_test)

        lgb_model = LightGBMModel()
        lgb_model.train(X_train, y_train)
        lgb_metrics = lgb_model.evaluate(X_test, y_test)

        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "comparison": {
                "xgboost": {k: round(v * 100, 1) if k != "roc_auc" else round(v * 100, 1) for k, v in xgb_metrics.items()},
                "lightgbm": {k: round(v * 100, 1) if k != "roc_auc" else round(v * 100, 1) for k, v in lgb_metrics.items()},
            },
            "recommendation": "XGBoost" if xgb_metrics.get("accuracy", 0) >= lgb_metrics.get("accuracy", 0) else "LightGBM",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _tf_to_days(timeframe: str, limit: int) -> int:
    mapping = {"M1": 1, "M5": 1, "M15": 2, "M30": 3, "H1": 7, "H4": 30, "D1": limit}
    return mapping.get(timeframe.upper(), 30) * (limit // 100 + 1)
