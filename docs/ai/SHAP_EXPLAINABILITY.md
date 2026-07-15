# SHAP Explainability — Al-Syaka Quant AI

Dokumen ini menjelaskan implementasi SHAP (SHapley Additive exPlanations) pada platform Al-Syaka Quant AI untuk interpretasi prediksi model machine learning.

## 1. Konsep Dasar SHAP

SHAP adalah metode explainability berbasis game theory yang menghitung kontribusi setiap fitur terhadap prediksi model. Nilai SHAP (SHapley values) menunjukkan seberapa besar pengaruh suatu fitur dalam mendorong prediksi menjadi kelas tertentu (BUY atau SELL).

Karakteristik utama SHAP:
- **Local explanation**: menjelaskan prediksi individual (per sampel)
- **Global explanation**: menunjukkan feature importance secara keseluruhan
- **Additive property**: jumlah kontribusi semua fitur + base value = prediksi
- **Consistency**: jika model berubah sehingga fitur lebih berpengaruh, nilai SHAP tidak akan menurun

## 2. Implementasi ExplainableAI

Kelas `ExplainableAI` berada di:

```
apps/ai-engine/src/al_syaka_ai/explainability.py
```

### 2.1 Inisialisasi

```python
from al_syaka_ai import ExplainableAI

explainer = ExplainableAI(model, feature_names)
```

Parameter:
- `model`: instance dari `BaseModel` (XGBoostModel, LightGBMModel, atau TransformerModel) yang sudah di-train
- `feature_names`: daftar nama kolom fitur (list of strings)

### 2.2 Fitting Explainer

```python
explainer.fit(X_background)
```

Proses:
- Untuk model **XGBoost** dan **LightGBM**: menggunakan `shap.TreeExplainer` yang bekerja langsung pada struktur tree model. Cepat dan akurat.
- Untuk model **Transformer** (PyTorch): menggunakan `shap.KernelExplainer` dengan 100 sampel background. Lebih lambat tetapi kompatibel dengan model black-box.

### 2.3 Generate Explanation

```python
explanation = explainer.explain(X)
```

Parameter `X` bisa berupa satu baris (DataFrame dengan 1 baris) atau multiple baris.

## 3. Output ExplainableAI

Method `explain()` mengembalikan dictionary dengan struktur berikut:

### 3.1 Single Sample Output

```python
{
    "signal": "BUY",                    # BUY atau SELL
    "confidence": 84.0,                 # Confidence level (0-100%)
    "reasons": [                        # 5 alasan teratas (natural language)
        "EMA 20: Bullish Cross",
        "ATR meningkat — Volatility tinggi",
        "RSI 61 — Momentum Bullish",
        "London Session: Active",
        "Momentum 5: Bullish (1.2%)"
    ],
    "shap_summary": "Model memprediksi BUY dengan confidence 84%. Faktor positif (3) mendominasi faktor negatif (2).",
    "explanation_reason": "Keputusan BUY terutama dipengaruhi oleh ema_20. Secara keseluruhan, 5 faktor dianalisis dengan 3 faktor mendukung dan 2 faktor menahan.",
    "feature_contributions": {
        "ema_20": {
            "value": 0.0042,        # Nilai aktual fitur
            "shap_impact": 0.1834,  # Kontribusi SHAP
            "direction": "positive" # positive (mendorong BUY) / negative (mendorong SELL)
        },
        "rsi_14":      { "value": 61.2, "shap_impact": 0.1201, "direction": "positive" },
        "atr_14":      { "value": 0.0023, "shap_impact": 0.0912, "direction": "positive" },
        "mom_5":       { "value": 0.012, "shap_impact": -0.0543, "direction": "negative" },
        "london_session": { "value": 1.0, "shap_impact": 0.0332, "direction": "positive" }
    },
    "shap_values": {
        "ema_20": 0.1834,
        "rsi_14": 0.1201,
        # ... nilai SHAP untuk 5 fitur teratas
    },
    "feature_values": {
        "ema_20": 0.0042,
        "rsi_14": 61.2,
        # ... nilai aktual untuk 5 fitur teratas
    }
}
```

### 3.2 Multiple Samples Output

Jika `X` berisi lebih dari 1 baris, output berupa list dari dictionary di atas.

## 4. Feature-to-Reason Mapping

Method `_feature_to_reason()` mengonversi nama fitur teknis menjadi alasan natural-language dalam Bahasa Indonesia/Inggris.

### Mapping yang Didukung

| Fitur | Label Output | Logika |
|-------|-------------|--------|
| `ema_12` | EMA 12 | Bullish/Bearish |
| `ema_20` | EMA 20 | Bullish/Bearish berdasarkan arah SHAP |
| `ema_50` | EMA 50 | Bullish/Bearish |
| `sma_20` | SMA 20 | Price above/below SMA 20 |
| `sma_50` | SMA 50 | Price above/below SMA 50 |
| `sma_200` | SMA 200 | Price above/below SMA 200 (Bullish/Bearish) |
| `rsi_14` | RSI | Oversold (<30), Overbought (>70), Momentum Bullish/Bearish |
| `atr_14` | ATR | ATR meningkat/menurun, Volatility tinggi/rendah |
| `ema_distance_20` | EMA Distance | Persentase jarak price dari EMA 20 |
| `ema_distance_50` | EMA Distance 50 | Persentase jarak price dari EMA 50 |
| `volatility_10` | Volatility | Volatility meningkat/menurun |
| `mom_5` | Momentum 5 | Bullish/Bearish dengan nilai persentase |
| `mom_10` | Momentum 10 | Bullish/Bearish dengan nilai persentase |
| `bb_position` | Bollinger | Price at upper/mid/lower Bollinger Band |
| `london_session` | London Session | Active/Inactive |
| `us_session` | US Session | Active/Inactive |
| `asian_session` | Asian Session | Active/Inactive |
| `session_overlap` | Session Overlap | London-New York Overlap - High Liquidity |
| `body_ratio` | Candle Body | Persentase body ratio |
| `candle_range` | Range | Candle range melebar/menyempit |

## 5. Global Feature Importance

Method `get_feature_importance()` mengembalikan feature importance global berdasarkan rata-rata absolut nilai SHAP:

```python
importance_df = explainer.get_feature_importance()
# Output: DataFrame dengan kolom ['feature', 'importance'], diurutkan menurun
```

## 6. Cara Membaca Output SHAP

### Interpretasi Nilai SHAP

- **Nilai SHAP positif**: fitur mendorong prediksi ke arah BUY (kelas 1)
- **Nilai SHAP negatif**: fitur mendorong prediksi ke arah SELL (kelas 0)
- **Magnitude absolut**: seberapa besar pengaruh fitur terhadap prediksi
- **Base value**: nilai prediksi rata-rata tanpa informasi fitur (expected value)

### Membaca `shap_summary`

Ringkasan satu kalimat yang menjelaskan:
1. Prediksi model (BUY/SELL)
2. Confidence level
3. Dominasi faktor positif vs negatif

### Membaca `explanation_reason`

Naratif yang lebih mendetail:
1. Fitur dengan pengaruh terkuat
2. Jumlah total faktor yang dianalisis
3. Sebaran faktor positif vs negatif

### Membaca `feature_contributions`

Untuk setiap fitur:
- `value`: nilai aktual fitur pada sampel yang diprediksi
- `shap_impact`: kontribusi SHAP (positif = mendorong BUY, negatif = mendorong SELL)
- `direction`: "positive" atau "negative" untuk memudahkan interpretasi

## 7. Contoh Penggunaan di API

Endpoint `/api/v1/ai/predict/{symbol}` menggunakan `ExplainableAI` sebagai berikut:

1. Mengumpulkan data OHLC dari collector
2. Menghitung features via `FeaturePipeline`
3. Melatih model XGBoost secara cepat
4. Membuat SHAP explainer dengan 50 sampel background
5. Generate explanation untuk baris terakhir (data terkini)
6. Mengembalikan response yang mencakup signal, confidence, reasons, dan SHAP output

Detail implementasi dapat dilihat di `apps/api/src/routers/ai.py`.
