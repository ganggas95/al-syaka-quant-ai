# MLOps — Al-Syaka Quant AI

Dokumen ini mendefinisikan pipeline MLOps untuk platform Al-Syaka Quant AI, mencakup alur dari pengumpulan data hingga deployment dan monitoring model.

## 1. Arsitektur MLOps Pipeline

```
[Data Collection] --> [Feature Engineering] --> [Training] --> [Evaluation] --> [Deployment] --> [Monitoring]
       |                      |                     |              |                |                |
       v                      v                     v              v                v                v
  Polygon.io           31-37 features         XGBoost/        Metrik:          FastAPI          Performance
  Yahoo Finance        Candlestick            LightGBM/       accuracy,        Endpoint         tracking
  MT5 Bridge           Momentum                Transformer     precision,       /api/v1/ai/      Retraining
                        Volatility                              recall, f1,     predict/         trigger
                        Session                                 ROC-AUC
```

## 2. Data Collection

### 2.1 Sumber Data

| Sumber | Tipe Data | Frekuensi | Reliability |
|--------|-----------|-----------|-------------|
| Polygon.io | Real-time + Historis | Streaming | High |
| Yahoo Finance | Historis | Batch harian | Medium |
| MT5 Broker Bridge | Real-time | Streaming | High |

### 2.2 Data Pipeline

Data dikumpulkan oleh `DataCollector` di `apps/api/src/collectors/manager.py`:

1. **Scheduled Tasks**: Celery periodic tasks mengumpulkan data secara berkala
2. **On-Demand**: API endpoint menerima permintaan untuk symbol/timeframe tertentu
3. **Storage**: Data disimpan di database melalui SQLAlchemy models

### 2.3 Data Quality Checks

- Validasi nilai OHLC (tidak negatif, high >= low, open/close dalam range)
- Deteksi missing bars (gap timestamp)
- Filter outlier (price spike > 5x ATR dari rata-rata)

## 3. Feature Engineering

### 3.1 Feature Pipeline

Semua fitur dihitung secara otomatis oleh `FeaturePipeline` di:

```
packages/feature-engineering/src/al_syaka_features/pipeline.py
```

Proses:
1. Input: OHLC + timestamp (optional)
2. Output: DataFrame dengan 31-37 kolom fitur
3. Preprocessing: replace inf/-inf, drop NaN

### 3.2 Feature Store

Fitur tidak disimpan secara persist di database. Fitur dihitung ulang setiap kali diperlukan dari data OHLC mentah. Untuk produksi dengan volume besar, pertimbangkan:

- Menyimpan fitur yang sudah dihitung di tabel terpisah untuk mengurangi komputasi berulang
- Menggunakan joblib atau parquet untuk caching fitur

## 4. Model Training

### 4.1 Training Trigger

Training dapat dipicu oleh:

1. **Manual Trigger**: via API endpoint `/api/v1/ai/predict/{symbol}` -- training cepat setiap request
2. **Scheduled Training**: Celery beat task untuk retraining periodik
3. **Event-driven**: training dipicu ketika data baru mencapai threshold tertentu (misal: 500 bar baru)

### 4.2 Training Pipeline

```
1. Fetch OHLC data
2. Compute features (FeaturePipeline)
3. Generate labels (LabelGenerator)
4. Train/Test split (80/20 time-series aware)
5. Train model:
   - XGBoostModel (default, cepat)
   - LightGBMModel (alternatif, ensemble)
   - TransformerModel (deep learning, sequences)
6. Evaluate metrics
7. Save model (joblib)
8. Log experiment
```

### 4.3 Model Versioning

Model disimpan dengan struktur berikut:

```
models/
  xgboost/
    v1.0_20260715.pkl
    v1.1_20260716.pkl
  lightgbm/
    v1.0_20260715.pkl
  transformer/
    v1.0_20260715.pth
```

Setiap model disertai dengan metadata:
- Timestamp training
- Jumlah data training
- Metrik evaluasi
- Feature columns used
- Label config yang digunakan
- Git commit hash

### 4.4 Experiment Tracking

Untuk tracking eksperimen, disarankan menggunakan:
- **MLflow**: untuk logging parameters, metrics, dan artifacts
- Atau log manual ke file JSON di direktori `models/`

Saat ini, tracking dilakukan secara sederhana dengan menyimpan metrik di `model.metrics` (dictionary).

## 5. Model Evaluation

### 5.1 Gate Check

Sebelum model dideploy, harus melewati gate check:

| Metrik | Minimum Threshold | Status |
|--------|------------------|--------|
| Accuracy | > 0.55 | Required |
| ROC-AUC | > 0.60 | Recommended |
| F1-Score | > 0.50 | Required |
| Precision | > 0.50 | Required |

### 5.2 Backtesting Validation

Model juga divalidasi melalui backtesting engine di `apps/backtester/`:
- Simulasi trading dengan sinyal model
- Hitung Sharpe ratio, win rate, profit factor
- Bandingkan dengan benchmark (buy-and-hold, model sebelumnya)

### 5.3 Model Comparison

Sebelum deployment, model baru dibandingkan dengan model produksi saat ini:
- A/B testing pada data terbaru
- Perbandingan metrik lengkap
- Champion/challenger approach

## 6. Model Deployment

### 6.1 Deployment Strategy

Model dideploy sebagai bagian dari FastAPI application:

```
FastAPI App (apps/api/src/main.py)
    |
    +-- Router: /api/v1/ai/predict/{symbol}
    |       - Load model terbaru
    |       - Compute features
    |       - Predict
    |       - Generate SHAP explanation
    |       - Return signal
    |
    +-- Router: /api/v1/ai/compare/{symbol}
            - Train XGBoost + LightGBM
            - Bandingkan performa
            - Return comparison
```

### 6.2 Model Loading

Model di-load dari disk menggunakan `joblib.load()`:

```python
model = XGBoostModel()
model.load("models/xgboost/v1.0_20260715.pkl")
```

Untuk produksi dengan traffic tinggi, model di-cache di memory untuk menghindari I/O disk berulang.

### 6.3 Inference Pipeline

```
Request: /api/v1/ai/predict/XAUUSD?timeframe=H1
    |
    v
1. Fetch OHLC XAUUSD H1 (200 bar terakhir)
2. Compute features
3. Load model (XGBoost)
4. Predict probability
5. If confidence > threshold:
     - Generate SHAP explanation
     - Return signal + reasons
   Else:
     - Fallback ke signal engine tradisional
```

## 7. Monitoring

### 7.1 Metrics Monitoring

Metrik yang dimonitor secara real-time:

| Metrik | Deskripsi | Alert Threshold |
|--------|-----------|-----------------|
| Prediction volume | Jumlah prediksi per menit | < 10 (low traffic) |
| Average confidence | Rata-rata confidence prediksi | < 60% |
| BUY/SELL ratio | Rasio sinyal BUY vs SELL | > 3:1 atau < 1:3 |
| Response time | Latency endpoint prediksi | > 5 detik |
| Model drift | Perbedaan distribusi prediksi | KS-test p < 0.05 |

### 7.2 Data Drift Monitoring

Data drift terdeteksi dengan memonitor:
- Distribusi fitur input (perbandingan dengan training data)
- Performa model menurun seiring waktu
- Perubahan volatilitas pasar

### 7.3 Alerting

Alert dikirim melalui:
- Logging ke file dengan level WARNING/ERROR
- Celery task monitoring (flower)
- Dashboard monitoring (grafana opsional)

## 8. Retraining Strategy

### 8.1 Scheduled Retraining

| Model | Frekuensi | Trigger | Data |
|-------|-----------|---------|------|
| XGBoost (online) | Setiap request | API call | 200-500 bar terakhir |
| XGBoost (production) | Mingguan | Celery beat | 30 hari terakhir |
| LightGBM | 2 mingguan | Celery beat | 60 hari terakhir |
| Transformer | Bulanan | Celery beat | 90 hari terakhir |

### 8.2 Retraining Triggers

Retraining dilakukan jika:
1. **Scheduled**: sesuai jadwal di atas
2. **Performance degradation**: accuracy turun > 5% dalam 1 minggu
3. **Data drift**: KS-test menunjukkan perubahan signifikan pada distribusi fitur
4. **New data available**: volume data baru > 1000 bars

### 8.3 Retraining Pipeline

```
1. Detect trigger
2. Fetch latest data (lebih banyak dari training sebelumnya)
3. Compute features
4. Generate labels
5. Train model baru
6. Evaluate (harus lebih baik dari model lama)
7. If pass gate check:
     - Save model baru
     - Update pointer model aktif
     - Log ke experiment tracking
   Else:
     - Alert: retraining failed
     - Keep model lama
```

## 9. Infrastructure

### 9.1 Docker Deployment

Platform menggunakan Docker Compose untuk deployment:

```
docker/docker-compose.yml
    |
    +-- api (FastAPI + Uvicorn)
    +-- celery_worker (Background tasks)
    +-- celery_beat (Scheduled tasks)
    +-- redis (Message broker)
    +-- postgres (Database)
```

### 9.2 Resource Requirements

| Komponen | CPU | RAM | Disk | GPU |
|----------|-----|-----|------|-----|
| API (inference) | 2 core | 4 GB | 10 GB | Optional |
| Training (XGBoost/LightGBM) | 4 core | 8 GB | 20 GB | Optional |
| Training (Transformer) | 4 core | 16 GB | 20 GB | Recommended |

## 10. Security & Compliance

- Model tidak menyimpan data pribadi
- Semua data training bersifat anonim (harga pasar publik)
- API endpoint memerlukan authentication key
- Model files di-restrict aksesnya (file system permissions)
