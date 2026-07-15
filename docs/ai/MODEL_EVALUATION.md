# Model Evaluation — Al-Syaka Quant AI

Dokumen ini menjelaskan metrik evaluasi dan metodologi yang digunakan untuk mengukur performa model machine learning pada platform Al-Syaka Quant AI.

## 1. Metrik Evaluasi

Metrik dihitung melalui method `evaluate()` pada kelas `BaseModel` di:

```
apps/ai-engine/src/al_syaka_ai/models/base.py
```

### 1.1 Accuracy

Rasio prediksi benar terhadap total prediksi.

```
accuracy = (TP + TN) / (TP + TN + FP + FN)
```

Digunakan sebagai metrik dasar untuk mengukur performa umum model.

### 1.2 Precision (Weighted)

Rasio prediksi positif benar terhadap total prediksi positif. Menggunakan `average="weighted"` untuk menangani ketidakseimbangan kelas.

```
precision = TP / (TP + FP)
```

Precision tinggi berarti model jarang memberikan false positive (salah sinyal BUY).

### 1.3 Recall (Weighted)

Rasio prediksi positif benar terhadap total aktual positif. Menggunakan `average="weighted"`.

```
recall = TP / (TP + FN)
```

Recall tinggi berarti model berhasil menangkap sebagian besar sinyal BUY yang sebenarnya.

### 1.4 F1-Score (Weighted)

Harmonic mean dari precision dan recall.

```
f1 = 2 * (precision * recall) / (precision + recall)
```

Memberikan keseimbangan antara precision dan recall. Berguna ketika ada trade-off antara keduanya.

### 1.5 ROC-AUC (Khusus Binary Classification)

Area Under the Receiver Operating Characteristic Curve.

```
roc_auc = AUC(TPR vs FPR)
```

Hanya dihitung untuk klasifikasi biner (2 kelas unik). Mengukur kemampuan model membedakan kelas positif dan negatif di berbagai threshold. Nilai 0.5 berarti random, 1.0 berarti sempurna.

## 2. Implementasi di BaseModel

```python
def evaluate(self, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = self.predict(X_test)
    y_proba = self.predict_proba(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average="weighted", zero_division=0),
        "recall": recall_score(y_test, y_pred, average="weighted", zero_division=0),
        "f1": f1_score(y_test, y_pred, average="weighted", zero_division=0),
    }

    # ROC AUC hanya untuk binary classification
    if len(np.unique(y_test)) == 2 and y_proba.ndim >= 2 and y_proba.shape[1] >= 2:
        metrics["roc_auc"] = roc_auc_score(y_test, y_proba[:, 1])

    self.metrics = metrics
    return metrics
```

Parameter `zero_division=0` digunakan untuk menghindari error jika suatu kelas tidak muncul di prediksi.

## 3. Time Series Cross Validation

### 3.1 TimeSeriesSplit

Al-Syaka Quant AI menggunakan `sklearn.model_selection.TimeSeriesSplit` untuk cross validation. Metode ini menghormati urutan temporal data, berbeda dengan KFold standar yang melakukan random shuffle.

```python
from sklearn.model_selection import TimeSeriesSplit

tscv = TimeSeriesSplit(n_splits=5)
for train_idx, test_idx in tscv.split(features):
    X_train, X_test = features.iloc[train_idx], features.iloc[test_idx]
    y_train, y_test = labels.iloc[train_idx], labels.iloc[test_idx]
    # Train dan evaluasi model
```

### 3.2 Ilustrasi TimeSeriesSplit (n_splits=5)

```
Split 1: [Train: 20%] [Test: 20%]
Split 2: [Train: 40%]        [Test: 20%]
Split 3: [Train: 60%]              [Test: 20%]
Split 4: [Train: 80%]                    [Test: 20%]
Split 5: [Train: 100%]                         [Test: 20%] (yang terakhir)
```

Setiap split menggunakan data yang lebih baru untuk testing daripada training, mensimulasikan kondisi forecasting yang realistis.

### 3.3 Implementasi di MLPipeline

```python
cv_indices = pipeline.time_series_cv(n_splits=5)
```

Mengembalikan list of (train_index, test_index) tuples yang siap digunakan untuk iterasi training.

## 4. Confusion Matrix

Meskipun tidak dihitung langsung di `BaseModel.evaluate()`, confusion matrix dapat dihasilkan menggunakan `sklearn.metrics.confusion_matrix` untuk analisis lebih mendalam.

```
              Predicted
              BUY   SELL
Actual BUY    TP    FN
       SELL   FP    TN
```

Interpretasi:
- **TP (True Positive)**: model benar memprediksi BUY, dan harga naik
- **TN (True Negative)**: model benar memprediksi SELL, dan harga turun
- **FP (False Positive)**: model memprediksi BUY, tetapi harga turun (false signal)
- **FN (False Negative)**: model memprediksi SELL, tetapi harga naik (missed opportunity)

## 5. Feature Importance

### 5.1 Tree-based Importance (XGBoost & LightGBM)

Kedua model mengekstrak feature importance dari attribute `feature_importances_` setelah training:

```python
self.feature_importance_ = pd.Series(
    self.model.feature_importances_,
    index=X_train.columns,
).sort_values(ascending=False)
```

### 5.2 SHAP Global Importance

Method `ExplainableAI.get_feature_importance()` menghitung rata-rata absolut nilai SHAP untuk mendapatkan feature importance global yang lebih akurat dan konsisten dibandingkan importance bawaan tree.

## 6. Model Comparison

Endpoint `/api/v1/ai/compare/{symbol}` melakukan perbandingan langsung antara XGBoost dan LightGBM:

```python
# Train XGBoost
xgb_model = XGBoostModel()
xgb_model.train(X_train, y_train, X_val, y_val)
xgb_metrics = xgb_model.evaluate(X_test, y_test)

# Train LightGBM
lgb_model = LightGBMModel()
lgb_model.train(X_train, y_train, X_val, y_val)
lgb_metrics = lgb_model.evaluate(X_test, y_test)

# Return comparison
{
    "xgboost": xgb_metrics,
    "lightgbm": lgb_metrics,
    "best_model": "xgboost" if xgb_metrics["accuracy"] >= lgb_metrics["accuracy"] else "lightgbm"
}
```

## 7. Threshold Interpretasi Metrik

| Metrik | Range | Kategori |
|--------|-------|----------|
| Accuracy | > 0.70 | Baik |
|  | 0.55 - 0.70 | Cukup |
|  | < 0.55 | Perlu perbaikan |
| ROC-AUC | > 0.80 | Excellent |
|  | 0.70 - 0.80 | Baik |
|  | 0.60 - 0.70 | Cukup |
|  | < 0.60 | Random / perlu perbaikan |
| F1-Score | > 0.70 | Baik |
|  | 0.50 - 0.70 | Cukup |
|  | < 0.50 | Perlu perbaikan |

Catatan: threshold ini bersifat indikatif. Untuk trading kuantitatif, metrik tambahan seperti Sharpe ratio, win rate, dan profit factor dari backtesting lebih relevan untuk evaluasi akhir.
