# Feature Engineering Pipeline

## Ringkasan

Feature engineering pipeline bertanggung jawab untuk mengekstrak fitur-fitur kuantitatif dari data OHLC mentah. Fitur-fitur ini digunakan oleh AI Engine untuk training model dan oleh Statistical Engine untuk kalkulasi probabilitas.

Package: `packages/feature-engineering/src/al_syaka_features/`

---

## FeaturePipeline

**File**: `packages/feature-engineering/src/al_syaka_features/pipeline.py`

Orchestrator utama yang mengintegrasikan semua modul ekstraksi fitur.

```python
class FeaturePipeline:
    def compute(self, open, high, low, close, volume=None, timestamps=None) -> pd.DataFrame:
        # 1. Candlestick features
        # 2. Momentum features
        # 3. Volatility features
        # 4. Session features
        # 5. Key indicators (SMA, EMA, RSI, ATR, Bollinger Bands)
```

Fitur yang dihasilkan (total ~30+ fitur per baris data):

| Kategori | Jumlah Fitur |
|----------|-------------|
| Candlestick | 8 fitur |
| Momentum | 6 fitur |
| Volatilitas | 7 fitur |
| Session | 6 fitur |
| Indicators | 6 fitur + derivatif |

---

## Candlestick Features

**File**: `packages/feature-engineering/src/al_syaka_features/candlestick.py`

Fitur berdasarkan struktur lilin (candle):

| Fitur | Deskripsi |
|-------|-----------|
| `body` | Nilai absolut selisih close - open |
| `upper_wick` | Jarak high ke max(open, close) |
| `lower_wick` | Jarak min(open, close) ke low |
| `candle_range` | Total rentang high - low |
| `body_ratio` | Rasio body terhadap range (0-1) |
| `bullish` | Binary: 1 jika close > open |
| `bearish` | Binary: 1 jika close < open |
| `doji` | Binary: 1 jika body <= 10% dari range |

---

## Momentum Features

**File**: `packages/feature-engineering/src/al_syaka_features/momentum.py`

Fitur berdasarkan momentum harga:

| Fitur | Deskripsi |
|-------|-----------|
| `mom_1` | Return 1 periode (pct_change) |
| `mom_5` | Return 5 periode |
| `mom_10` | Return 10 periode |
| `mom_20` | Return 20 periode |
| `roc_10` | Rate of Change 10 periode (%) |
| `price_position_10` | Posisi harga dalam range 10 periode (0-1) |
| `vim_10` | Volume-weighted momentum 10 periode |

---

## Volatility Features

**File**: `packages/feature-engineering/src/al_syaka_features/volatility.py`

Fitur berdasarkan volatilitas harga:

| Fitur | Deskripsi |
|-------|-----------|
| `tr` | True Range (max of 3 methods) |
| `atr_5` | Average True Range 5 periode |
| `atr_10` | Average True Range 10 periode |
| `atr_20` | Average True Range 20 periode |
| `volatility_10` | Standar deviasi return 10 periode |
| `volatility_20` | Standar deviasi return 20 periode |
| `gap` | Gap harga open - previous close |

---

## Session Features

**File**: `packages/feature-engineering/src/al_syaka_features/session.py`

Fitur berdasarkan sesi trading global:

| Fitur | Deskripsi |
|-------|-----------|
| `asian_session` | 1 jika dalam sesi Asia (00:00-09:00 UTC) |
| `london_session` | 1 jika dalam sesi London (08:00-17:00 UTC) |
| `us_session` | 1 jika dalam sesi US (13:00-22:00 UTC) |
| `london_open` | 1 jika jam pembukaan London (08:00-09:00 UTC) |
| `us_open` | 1 jika jam pembukaan US (13:30-14:30 UTC) |
| `session_overlap` | 1 jika overlap London-US |

---

## Key Indicators

Fitur indikator teknikal yang dihitung langsung di pipeline:

| Fitur | Parameter | Deskripsi |
|-------|-----------|-----------|
| `sma_20` | 20 periode | Simple Moving Average |
| `sma_50` | 50 periode | Simple Moving Average |
| `ema_20` | 20 periode | Exponential Moving Average |
| `ema_50` | 50 periode | Exponential Moving Average |
| `rsi_14` | 14 periode | Relative Strength Index |
| `atr_14` | 14 periode | Average True Range |
| `ema_distance_20` | - | (close - ema_20) / close * 100 |
| `ema_distance_50` | - | (close - ema_50) / close * 100 |
| `bb_upper` | 20, 2 std | Bollinger Band atas |
| `bb_lower` | 20, 2 std | Bollinger Band bawah |
| `bb_position` | - | Posisi harga dalam Bollinger Bands (0-1) |

---

## Alur Ekstraksi Fitur

```
[OHLC Data] -- Data mentah dari database/collector
     |
     v
[FeaturePipeline.compute()]
     |
     +-> candle_features()     -- 8 fitur candlestick
     +-> momentum_features()   -- 6 fitur momentum
     +-> volatility_features() -- 7 fitur volatilitas
     +-> session_features()    -- 6 fitur sesi (jika timestamp tersedia)
     +-> Indicators            -- SMA, EMA, RSI, ATR, BB
     |
     v
[pd.DataFrame] -- 30+ kolom fitur, index sama dengan input
     |
     v
[MLPipeline / API Endpoint] -- Siap untuk training atau inference
```

---

## Penggunaan di API

Feature pipeline dapat diakses melalui endpoint:

```
GET /api/v1/indicators/{symbol}/features?timeframe=H1&limit=200
```

Response mencakup semua fitur dalam format JSON array per kolom.
