# Alur Event Al-Syaka Quant AI

## Overview

Dokumen ini menjelaskan alur pemrosesan data dari hulu ke hilir: mulai dari pengumpulan data pasar, komputasi indikator, analisis struktur pasar, prediksi AI, hingga pembangkitan sinyal dan notifikasi.

---

## Diagram Alur Utama

```
[Data Sources] --> [Collectors] --> [Database] --> [Processing Pipeline] --> [Signal] --> [Output]
     |                 |               |                 |                       |            |
     v                 v               v                 v                       v            v
  Yahoo Finance    DataCollector    PostgreSQL     Celery Workers          SignalGenerator    API
  Polygon.io       Manager          Redis Cache    IndicatorCalculator     UnifiedSignal      Dashboard
  Massive                       Market Structure  AI Models (XGBoost)     FinalDecision      MT5
  MT5                            Feature Pipeline  SHAP Explainability     MacroBias          Paper Trading
```

---

## Alur Lengkap: Data Menjadi Sinyal

### Fase 1: Pengumpulan Data

```
Yahoo Finance/Polygon/Massive
         |
         v
   DataCollector.fetch_ohlc(symbol, timeframe, start, end)
         |
         v
   Database (tabel ohlc)
         |
         v
   Redis Cache (untuk akses cepat)
```

**Task Celery Periodik:**
```python
# Setiap 5 menit
celery_app.conf.beat_schedule = {
    "fetch-ohlc-every-5-minutes": {
        "task": "fetch_ohlc_task",
        "schedule": 300.0,
    },
}
```

Task `fetch_ohlc_task` di `/apps/api/src/tasks/market_data.py`:
- Mengambil data OHLC terbaru untuk semua simbol aktif
- Menyimpan ke database PostgreSQL
- Berjalan setiap 5 menit secara periodik

### Fase 2: Komputasi Indikator

```
Data OHLC dari Database
         |
         v
   IndicatorCalculator.compute_all()
         |
         +---> Trend Indicators: EMA 12, EMA 20, EMA 50, SMA 200
         +---> Oscillators: RSI 14, MACD, Stochastic
         +---> Volatility: ATR 14, Bollinger Bands
         +---> Strength: ADX, Supertrend
         +---> Volume Indicators
         |
         v
   FeaturePipeline.compute()
         |
         +---> Momentum Features
         +---> Volatility Features
         +---> Session Features (Asia, London, New York)
         +---> Candlestick Pattern Features
```

### Fase 3: Analisis Struktur Pasar

```
Data OHLC + Indikator
         |
         v
   MarketStructureDetector.analyze(high, low)
         |
         +---> Swing Highs & Swing Lows detection
         +---> Break of Structure (BOS)
         +---> Change of Character (CHOCH)
         |
   detect_fvg(high, low, close)
         |
         +---> Bullish Fair Value Gap
         +---> Bearish Fair Value Gap
         |
   detect_liquidity_sweep(high, low, close)
         |
         +---> Buy-side Liquidity Sweep
         +---> Sell-side Liquidity Sweep
         |
   SupportResistanceDetector.detect(high, low)
         |
         +---> Support Levels
         +---> Resistance Levels
```

### Fase 4: Prediksi AI (Opsional)

```
Feature Pipeline Output
         |
         v
   XGBoostModel.train(X_train, y_train)
         |
         v
   Model Evaluation: accuracy, precision, recall, f1, roc_auc
         |
         v
   ExplainableAI (SHAP)
         |
         +---> SHAP Values
         +---> Feature Importance
         +---> Natural Language Reasons
```

**Model yang Tersedia:**
- XGBoostModel (default, performa lebih baik)
- LightGBMModel (alternatif, lebih cepat)
- TransformerModel (untuk sequence prediction)

### Fase 5: Pembangkitan Sinyal

```
Semua Hasil Analisis
         |
         v
   ProbabilityEngine.evaluate(indicators, market_structure)
         |
         +---> Menghitung probabilitas arah harga
         +---> Menentukan signal: BUY, SELL, NEUTRAL
         +---> Confidence level (0-1)
         +---> Risk level (LOW, MEDIUM, HIGH)
         |
         v
   MacroBiasEngine.analyze()
         |
         +---> Analisis multi-timeframe (H4, D1)
         +---> Macro bias: BULLISH, BEARISH, NEUTRAL
         +---> Macro strength & confidence
         |
         v
   FinalDecisionEngine.decide()
         |
         +---> Input: technical signal, composite score, market regime, macro bias
         +---> Conflict detection (teknikal vs makro)
         +---> Output: BUY, SELL, WAIT, HEDGE
         |
         v
   RiskManager.evaluate_trade()
         |
         +---> Position sizing (Kelly Criterion)
         +---> Stop Loss & Take Profit (ATR-based)
         +---> Lot size calculation
         +---> Trade quality assessment
```

### Fase 6: Penyimpanan dan Output

```
UnifiedSignal (dataclass)
         |
         +---> Save ke Database (tabel signals)
         |       + symbol, timeframe, signal, confidence
         |       + entry_price, stop_loss, take_profit
         |       + reasons, indicators_used
         |       + market_structure data
         |       + multi-timeframe signals
         |       + AI predictions (jika ada)
         |
         +---> Return via API Response
         |       /api/v1/unified-signal/{symbol}
         |
         +---> (Future) WebSocket Broadcast
         |       real-time signal updates
         |
         +---> (Future) MT5 Auto Trading
                 AutoTradingEngine.process_signal()
```

---

## Celery Tasks

### Konfigurasi Celery

**File:** `/apps/api/src/celery_app.py`

```python
celery_app = Celery("al_syaka_quant")
celery_app.conf.update(
    broker=settings.celery_broker_url,  # redis://localhost:6379/0
    backend=settings.celery_result_backend,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)
```

### Daftar Task

| Nama Task | File | Schedule | Deskripsi |
|-----------|------|----------|-----------|
| `fetch_ohlc_task` | `tasks/market_data.py` | Setiap 5 menit | Mengambil data OHLC terbaru |
| (future) | `tasks/processing.py` | - | Komputasi indikator background |

### Task Detail: fetch_ohlc_task

```python
@shared_task(name="fetch_ohlc_task", bind=True, max_retries=3, default_retry_delay=60)
def fetch_ohlc_task(self):
    """Periodic task to fetch latest OHLC data for all active symbols."""
    return asyncio.run(_fetch_and_store_ohlc())
```

- **Retry:** 3 kali dengan delay 60 detik
- **Error handling:** Exception akan dicatat dan task akan di-retry
- **Output:** Status completion dengan timestamp

---

## Alur Multi-Timeframe

```
Request: symbol=EURUSD, timeframe=H1
         |
         v
   fetch_data("EURUSD", "H1", 200)  # Timeframe utama
   fetch_data("EURUSD", "H4", 100)  # Higher timeframe
   fetch_data("EURUSD", "D1", 60)   # Highest timeframe
         |
         v
   Analisis per timeframe:
         |
         +---> H1: Indikator + Struktur Pasar + Probabilitas
         +---> H4: Trend analysis + Macro context
         +---> D1: Trend analysis + Macro context
         |
         v
   Multi-timeframe confirmation:
         - Jika H1, H4, D1 semua BUY -> Strong BUY signal
         - Jika H1 BUY tapi D1 SELL -> Conflict, perlu waspada
         - Jika timeframe lebih tinggi netral -> Ikut timeframe entry
```

---

## Alur Final Decision

```
                        Input
                    +-----------+
                    | Technical |  (BUY/SELL/NEUTRAL + confidence)
                    +-----------+
                    +-----------+
                    | Composite |  (market structure + momentum + trend + volatility + AI)
                    +-----------+
                    +-----------+
                    |  Regime   |  (TRENDING, REVERSAL, RANGE, VOLATILE)
                    +-----------+
                    +-----------+
                    |  Macro    |  (BULLISH/BEARISH/NEUTRAL + strength + confidence)
                    +-----------+
                         |
                         v
               FinalDecisionEngine.decide()
                         |
            +------------+-------------+
            |            |             |
            v            v             v
        Conflict?   Macro Override?   Strong Tech?
            |            |             |
            v            v             v
         HEDGE/     Override to       Follow
         WAIT       Macro Signal      Technical
```

**Logika Keputusan:**
1. Macro override jika macro confidence >= 60 dan technical confidence < 50
2. Conflict = HEDGE atau WAIT
3. Strong technical (confidence >= 70) = ikuti technical
4. Moderate technical dengan dukungan macro = ikuti technical
5. Low confidence atau NEUTRAL = WAIT

---

## Catatan Implementasi

1. **Async/Sync Boundary:** Semua operasi database dan HTTP bersifat async. Operasi komputasi berat (indikator, ML) dapat berjalan sync di worker thread.

2. **Caching:** Data OHLC di-cache di Redis untuk akses cepat. Cache di-invalidasi setiap kali task periodik selesai.

3. **Error Handling:** Setiap fase memiliki error handling independen. Kegagalan di satu fase tidak menghentikan fase lainnya (graceful degradation).

4. **Database Save Non-Critical:** Penyimpanan sinyal ke database bersifat non-critical. Jika gagal, sinyal tetap dikembalikan ke user tanpa signal_id.

5. **AI Prediction Optional:** Parameter `include_ai=false` secara default karena prediksi AI membutuhkan komputasi lebih lama (training model on-the-fly).
