# Model Training — Al-Syaka Quant AI

Dokumen ini menjelaskan proses training model machine learning pada platform Al-Syaka Quant AI, mencakup persiapan data, komputasi fitur, labeling, dan konfigurasi setiap model.

## 1. Arsitektur Training

Proses training dijalankan melalui kelas `MLPipeline` yang berada di:

```
apps/ai-engine/src/al_syaka_ai/pipeline.py
```

### Alur Training

```
OHLC Data
    |
    v
FeaturePipeline.compute() --> 31-37 fitur teknikal
    |
    v
LabelGenerator.generate_labels() --> BUY(1)/SELL(0) labels
    |
    v
Data alignment & NaN removal
    |
    v
Train/Test Split (80/20 sequential)
    |
    v
Model Training (XGBoost / LightGBM / Transformer)
    |
    v
Model Evaluation
```

## 2. Data Preparation

### 2.1 Persiapan Data

```python
from al_syaka_ai import MLPipeline, LabelConfig

pipeline = MLPipeline(label_config=LabelConfig(
    forward_bars=12,
    tp_percent=0.005,
    sl_percent=0.003,
    min_holding_bars=3
))

features, labels = pipeline.prepare_data(
    open=open_series,
    high=high_series,
    low=low_series,
    close=close_series,
    volume=volume_series,       # opsional
    timestamps=timestamp_series  # opsional
)
```

### 2.2 Tahapan

1. **Feature Computation**: `FeaturePipeline.compute()` menghasilkan 31-37 fitur dari OHLC
2. **NaN Handling**: nilai `inf`/`-inf` diganti dengan `NaN`, lalu semua baris `NaN` dihapus
3. **Label Generation**: `LabelGenerator.generate_labels()` menghitung label BUY/SELL dari harga
4. **Alignment**: label diselaraskan dengan index fitur yang tersisa setelah dropna

### 2.3 Train/Test Split

```python
X_train, X_test, y_train, y_test = pipeline.train_test_split(test_size=0.2)
```

Split dilakukan secara **time-series aware** (sequential split), bukan random shuffle:
- 80% pertama: training set
- 20% terakhir: testing set

### 2.4 Time Series Cross Validation

```python
cv_indices = pipeline.time_series_cv(n_splits=5)
# Mengembalikan list of (train_index, test_index) tuples
```

Menggunakan `sklearn.model_selection.TimeSeriesSplit` yang mempertahankan urutan temporal data.

## 3. Model Training

### 3.1 XGBoostModel

File: `apps/ai-engine/src/al_syaka_ai/models/xgboost_model.py`

```python
from al_syaka_ai import XGBoostModel

model = XGBoostModel(name="xgboost", params={...})
model.train(X_train, y_train, X_val, y_val)
```

**Default Hyperparameters:**

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| `n_estimators` | 200 | Jumlah trees |
| `max_depth` | 6 | Kedalaman maksimum tree |
| `learning_rate` | 0.05 | Learning rate (eta) |
| `subsample` | 0.8 | Fraksi sampel per tree |
| `colsample_bytree` | 0.8 | Fraksi fitur per tree |
| `min_child_weight` | 3 | Minimum sum instance weight di child |
| `gamma` | 0.1 | Minimum loss reduction untuk split |
| `reg_alpha` | 0.1 | L1 regularization |
| `reg_lambda` | 1 | L2 regularization |
| `random_state` | 42 | Seed reproducibility |
| `eval_metric` | "logloss" | Metrik evaluasi internal |

**Hyperparameter Tuning:**

Method `tune()` melakukan grid search pada parameter:
- `max_depth`: [4, 6, 8]
- `learning_rate`: [0.01, 0.05, 0.1]
- `n_estimators`: [100, 200]
- `subsample`: [0.7, 0.8, 1.0]

Setelah grid search, model di-retrain dengan parameter terbaik.

### 3.2 LightGBMModel

File: `apps/ai-engine/src/al_syaka_ai/models/lightgbm_model.py`

```python
from al_syaka_ai import LightGBMModel

model = LightGBMModel(name="lightgbm", params={...})
model.train(X_train, y_train, X_val, y_val)
```

**Default Hyperparameters:**

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| `n_estimators` | 200 | Jumlah boosting rounds |
| `max_depth` | 6 | Kedalaman maksimum tree |
| `learning_rate` | 0.05 | Learning rate |
| `num_leaves` | 31 | Jumlah leaves per tree |
| `subsample` | 0.8 | Fraksi sampel per tree |
| `colsample_bytree` | 0.8 | Fraksi fitur per tree |
| `min_child_samples` | 20 | Minimum samples di leaf |
| `reg_alpha` | 0.1 | L1 regularization |
| `reg_lambda` | 0.1 | L2 regularization |
| `random_state` | 42 | Seed reproducibility |
| `verbose` | -1 | Silent mode |

**Early Stopping:**
LightGBM mendukung early stopping dengan 10 rounds jika validation set disediakan. Training berhenti jika metrik validation tidak membaik.

### 3.3 TransformerModel

File: `apps/ai-engine/src/al_syaka_ai/models/transformer_model.py`

```python
from al_syaka_ai import TransformerModel

model = TransformerModel(
    name="transformer",
    seq_len=20,
    d_model=64,
    nhead=4,
    num_layers=3,
    learning_rate=0.001,
    epochs=50,
    batch_size=32,
    device="cpu"
)
model.train(X_train, y_train)
```

**Arsitektur TimeSeriesTransformer:**

```
Input: (batch, seq_len=20, features)
    |
    v
Linear Projection: features -> d_model (64)
    |
    v
Positional Encoding (learned parameter)
    |
    v
TransformerEncoder (3 layers, 4 heads, FFN 128)
    |
    v
Global Average Pooling (mean across seq_len)
    |
    v
Linear Layer: d_model -> num_classes (2)
```

**Hyperparameters:**

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| `seq_len` | 20 | Panjang sequence untuk sliding window |
| `d_model` | 64 | Dimensi embedding |
| `nhead` | 4 | Jumlah attention heads |
| `num_layers` | 3 | Jumlah encoder layers |
| `dim_feedforward` | 128 | Dimensi feed-forward network |
| `dropout` | 0.1 | Dropout rate |
| `learning_rate` | 0.001 | Adam optimizer learning rate |
| `epochs` | 50 | Maksimum epochs |
| `batch_size` | 32 | Batch size |
| `device` | "cpu" | Device (otomatis ke CUDA jika tersedia) |

**Sequence Creation:**
TransformerModel menggunakan sliding window untuk mengubah data tabular menjadi sequence. Untuk setiap baris ke-i, sequence adalah `X[i : i+seq_len]` dan label adalah `y[i+seq_len]`.

**Loss Function:** CrossEntropyLoss
**Optimizer:** Adam

## 4. Model Comparison API

Endpoint `/api/v1/ai/compare/{symbol}` membandingkan performa XGBoost vs LightGBM pada dataset yang sama.

Proses:
1. Data OHLC dikumpulkan
2. Fitur dihitung
3. Label sederhana dibuat (forward return threshold 0.3%, 12 bars)
4. Train/test split 80/20
5. Kedua model di-train dan di-evaluasi
6. Hasil perbandingan dikembalikan (accuracy, precision, recall, f1 untuk masing-masing model)

## 5. Model Storage

### 5.1 Serialization

Model disimpan menggunakan `joblib`:

```python
model.save("models/xgboost_model.pkl")
model.load("models/xgboost_model.pkl")
```

### 5.2 Storage Location

Model yang sudah di-train disimpan di direktori `models/` pada root project:

```
models/
  xgboost_model.pkl
  lightgbm_model.pkl
  transformer_model.pth
```

### 5.3 Versioning

Model versioning menggunakan nama file dengan timestamp atau menggunakan sistem file berstruktur direktori yang terpisah untuk setiap versi model.
