# AI Engine

## Ringkasan

AI Engine adalah inti dari kemampuan prediktif Al-Syaka Quant AI. Engine ini menyediakan pipeline lengkap dari feature engineering, labeling, training model, hingga explainability dengan SHAP.

Package: `apps/ai-engine/src/al_syaka_ai/`

---

## Arsitektur

```
[OHLC Data] -> [FeaturePipeline] -> [MLPipeline] -> [Model Training] -> [SHAP Explainability]
                                                  -> [Inference API]
```

---

## Model Implementations

### Base Model Interface

**File**: `apps/ai-engine/src/al_syaka_ai/models/base.py`

Abstract base class untuk semua model:

```python
class BaseModel(ABC):
    def __init__(self, name: str): ...
    def train(X_train, y_train, X_val, y_val): ...
    def predict(X) -> np.ndarray: ...
    def predict_proba(X) -> np.ndarray: ...
    def evaluate(X_test, y_test) -> dict: ...
    def save(path): ...
    def load(path): ...
```

### XGBoostModel

**File**: `apps/ai-engine/src/al_syaka_ai/models/xgboost_model.py`

Model utama untuk prediksi arah pasar.

**Default Hyperparameters**:

```python
{
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_weight": 3,
    "gamma": 0.1,
    "reg_alpha": 0.1,
    "reg_lambda": 1,
    "eval_metric": "logloss",
    "random_state": 42,
}
```

**Fitur**:

- Training dengan validation set.
- Hyperparameter tuning via grid search (max_depth, learning_rate, n_estimators, subsample).
- Feature importance extraction.
- Save/load model dengan joblib.

### LightGBMModel

**File**: `apps/ai-engine/src/al_syaka_ai/models/lightgbm_model.py`

Model alternatif untuk perbandingan dan ensemble.

**Default Hyperparameters**:

```python
{
    "n_estimators": 200,
    "max_depth": 6,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "min_child_samples": 20,
    "reg_alpha": 0.1,
    "reg_lambda": 0.1,
    "random_state": 42,
}
```

**Fitur**:

- Early stopping dengan callback.
- Feature importance extraction.
- Perbandingan performa via API `/api/v1/ai/compare/{symbol}`.

### TransformerModel

**File**: `apps/ai-engine/src/al_syaka_ai/models/transformer_model.py`

Model deep learning untuk sequence-based prediction (belum diimplementasikan penuh).

---

## ML Pipeline

**File**: `apps/ai-engine/src/al_syaka_ai/pipeline.py`

Pipeline end-to-end untuk menyiapkan data training.

```python
class MLPipeline:
    def __init__(self, label_config: LabelConfig):
        self.feature_pipeline = FeaturePipeline()
        self.label_generator = LabelGenerator(label_config)

    def prepare_data(self, open, high, low, close, volume, timestamps) -> tuple:
        # 1. Generate features
        # 2. Generate labels
        # 3. Align features & labels
        return features, labels

    def train_test_split(self, test_size=0.2):
        # Time-series aware split (no shuffling)
        return X_train, X_test, y_train, y_test

    def time_series_cv(self, n_splits=5):
        # TimeSeriesSplit for cross-validation
        return list of (train_idx, test_idx)
```

---

## Labeling

**File**: `apps/ai-engine/src/al_syaka_ai/labeling.py`

Generator label untuk supervised learning.

### LabelConfig

```python
@dataclass
class LabelConfig:
    forward_bars: int = 12    # Look-ahead bars
    tp_percent: float = 0.005 # 0.5% take profit threshold
    sl_percent: float = 0.003 # 0.3% stop loss threshold
    min_holding_bars: int = 3
```

### Label Generation Methods

**`generate_labels(close, high, low)`** -- Binary classification labels:

- 1 (BUY): Jika TP tercapai sebelum SL dalam forward_bars.
- 0 (SELL): Jika SL tercapai sebelum TP dalam forward_bars.
- Berdasarkan perbandingan upside vs downside jika tidak ada yang kena.

**`generate_regression_labels(close)`** -- Regression labels:

- Forward return: `close.shift(-forward_bars) / close - 1`

---

## Explainability (SHAP)

**File**: `apps/ai-engine/src/al_syaka_ai/explainability.py`

Memberikan penjelasan transparan untuk setiap prediksi model.

```python
class ExplainableAI:
    def __init__(self, model, feature_names):
        self.model = model
        self.feature_names = feature_names

    def fit(self, X_background):
        # Pilih explainer berdasarkan tipe model
        # TreeExplainer untuk XGBoost/LightGBM
        # KernelExplainer untuk Transformer

    def explain(self, X) -> dict:
        # Hitung SHAP values
        # Generate natural language reasons
        # Return: signal, confidence, reasons, shap_summary, feature_contributions
```

**Output**:

```python
{
    "signal": "BUY|SELL",
    "confidence": 84.0,  # 0-100%
    "reasons": [
        "EMA 20: Bullish (1.2345)",
        "ATR meningkat (0.00123) -- Volatility tinggi",
        "RSI 61 -- Momentum Bullish",
        "London Session Active"
    ],
    "shap_summary": "Model memprediksi BUY dengan confidence 84%. Faktor positif (3) mendominasi faktor negatif (2).",
    "explanation_reason": "Keputusan BUY terutama dipengaruhi oleh ema_20. 5 faktor dianalisis dengan 3 mendukung dan 2 menahan.",
    "feature_contributions": {
        "ema_20": {"value": 1.2345, "shap_impact": 0.15, "direction": "positive"},
        "rsi_14": {"value": 61.0, "shap_impact": 0.08, "direction": "positive"}
    }
}
```

**Feature-to-Reason Mapping**:

- RSI -> Oversold/Overbought/Momentum description
- ATR -> Volatility direction description
- EMA/SMA -> Bullish/Bearish alignment
- Bollinger Bands -> Price position
- Session -> Active/Inactive
- Momentum -> Direction & magnitude

---

## API Endpoints

### Prediction

```
GET /api/v1/ai/predict/{symbol}?timeframe=H1&limit=500
```

Response: Signal, confidence, SHAP explanation, feature importance, model metrics.

### Model Comparison

```
GET /api/v1/ai/compare/{symbol}?timeframe=H1&limit=500
```

Response: Perbandingan metrik XGBoost vs LightGBM, rekomendasi model terbaik.

---

## Integrasi dengan Unified Signal

AI Engine diintegrasikan ke dalam Unified Signal Generator sebagai komponen opsional. Jika AI diaktifkan (`include_ai=True`), hasil prediksi AI ditambahkan ke sinyal akhir dengan bobot 20% dalam composite score.

```python
# Di UnifiedSignalGenerator.generate()
if include_ai:
    ai_conf, ai_acc, ai_reasons, shap_summary, feat_contrib, expl_reason = await self._ai_predict(df)
```
