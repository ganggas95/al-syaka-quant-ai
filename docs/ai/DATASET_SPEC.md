# Dataset Specification — Al-Syaka Quant AI

Dokumen ini mendefinisikan spesifikasi dataset yang digunakan untuk training model machine learning pada platform Al-Syaka Quant AI.

## 1. Data Source

Data OHLC (Open, High, Low, Close) diperoleh dari beberapa sumber melalui modul `DataCollector` di:

```
apps/api/src/collectors/
```

Sumber data yang didukung:
- **Polygon.io**: data real-time dan historis untuk forex, saham, crypto
- **Yahoo Finance**: data historis gratis
- **Massive connector**: konektor internal untuk data broker

## 2. Struktur Data

Setiap record dataset memiliki struktur sebagai berikut:

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `timestamp` | datetime | Waktu candle dalam UTC |
| `open` | float | Harga pembukaan |
| `high` | float | Harga tertinggi |
| `low` | float | Harga terendah |
| `close` | float | Harga penutupan |
| `volume` | float | Volume perdagangan |

## 3. Timeframes

Platform mendukung beberapa timeframe untuk training dan prediksi:

| Timeframe | Kode | Baris per Hari | Typical Lookback |
|-----------|------|----------------|------------------|
| 1 menit | M1 | 1440 | 3-7 hari |
| 5 menit | M5 | 288 | 7-14 hari |
| 15 menit | M15 | 96 | 14-30 hari |
| 30 menit | M30 | 48 | 30-60 hari |
| 1 jam | H1 | 24 | 60-120 hari |
| 4 jam | H4 | 6 | 120-365 hari |
| 1 hari | D1 | 1 | 365+ hari |

Jumlah minimum data yang diperlukan: **50 baris** (setelah feature computation dan dropna). Praktik umum menggunakan **200-500 baris** untuk hasil yang lebih stabil.

## 4. Label Generation

### 4.1 LabelConfig

Label dihasilkan oleh kelas `LabelGenerator` yang dikonfigurasi melalui `LabelConfig`:

```
apps/ai-engine/src/al_syaka_ai/labeling.py
```

```python
@dataclass
class LabelConfig:
    forward_bars: int = 12       # Jumlah bar ke depan untuk look-ahead
    tp_percent: float = 0.005    # Take profit threshold (0.5%)
    sl_percent: float = 0.003    # Stop loss threshold (0.3%)
    min_holding_bars: int = 3    # Minimum holding period
```

### 4.2 Label Logic (generate_labels)

Label dihasilkan dengan melihat **forward-looking price action**:

```
Untuk setiap baris i:
  entry = close[i]
  future_high = max(high[i+1 : i+forward_bars+1])
  future_low  = min(low[i+1 : i+forward_bars+1])

  tp_hit = (future_high - entry) / entry >= tp_percent
  sl_hit = (entry - future_low) / entry >= sl_percent

  IF tp_hit AND NOT sl_hit:
      label = 1 (BUY)
  ELIF sl_hit AND NOT tp_hit:
      label = 0 (SELL)
  ELSE:
      # Whichever hit first or larger move
      upside = (future_high - entry) / entry
      downside = (entry - future_low) / entry
      label = 1 if upside > downside else 0
```

**Label Values:**
- `1`: BUY (harga diperkirakan naik dalam 12 bar ke depan)
- `0`: SELL (harga diperkirakan turun dalam 12 bar ke depan)
- `-1`: NEUTRAL (digunakan sebagai placeholder internal, tidak digunakan dalam training)

### 4.3 Simplified Label (Quick Training)

Untuk quick training di endpoint API, digunakan label yang lebih sederhana:

```python
future_ret = close.shift(-12) / close - 1
labels = (future_ret > 0.003).astype(int)
```

Logika:
- `1` (BUY): forward return 12 bar > 0.3%
- `0` (SELL): forward return 12 bar <= 0.3%

Threshold **0.3%** (0.003) digunakan sebagai ambang batas minimal untuk dianggap sinyal valid.

### 4.4 Regression Labels

Alternatif labeling untuk regression-based model:

```python
future_returns = close.shift(-forward_bars) / close - 1
# Output: continuous values (bukan discrete)
```

## 5. Data Splitting

### 5.1 Train/Test Split

Split dilakukan secara **time-series aware** (berurutan, bukan acak):

```
|----------- Training Set (80%) -----------|-- Test Set (20%) --|
|---- Data historis lebih lama ----|---- Data lebih baru ----|
```

Implementasi:

```python
split_idx = int(len(features) * (1 - test_size))
X_train = features.iloc[:split_idx]
X_test = features.iloc[split_idx:]
y_train = labels.iloc[:split_idx]
y_test = labels.iloc[split_idx:]
```

### 5.2 Time Series Cross Validation

Untuk cross validation, digunakan `sklearn.model_selection.TimeSeriesSplit`:

```
Split 1: [Train] [Test]
Split 2: [Train       ] [Test]
Split 3: [Train            ] [Test]
Split 4: [Train                 ] [Test]
Split 5: [Train                      ] [Test]
```

Setiap split berikutnya menggunakan data training yang lebih banyak, mempertahankan urutan temporal.

## 6. Data Pipeline Flow

```
Data Collector (Polygon/Yahoo/Massive)
    |
    v
OHLC DataFrame (timestamp, open, high, low, close, volume)
    |
    v
FeaturePipeline.compute()
    - Candlestick features (8 fitur)
    - Momentum features (6-7 fitur)
    - Volatility features (6-7 fitur)
    - Session features (6 fitur, jika timestamps tersedia)
    - Key indicators + Bollinger (11 fitur)
    |
    v
Total: 31-37 fitur
    |
    v
Replace inf/-inf with NaN -> dropna()
    |
    v
LabelGenerator.generate_labels()
    |
    v
Align labels dengan feature index
    |
    v
Train/Test Split (80/20)
    |
    v
Model Training
```

## 7. Contoh Ukuran Dataset

Untuk referensi, berikut ukuran dataset tipikal setelah feature computation:

| Timeframe | Raw Data | Setelah Features | Training (80%) | Test (20%) |
|-----------|----------|------------------|----------------|------------|
| M5 (7 hari) | 2016 bar | ~1996 bar | ~1596 | ~400 |
| M15 (14 hari) | 1344 bar | ~1324 bar | ~1059 | ~265 |
| H1 (60 hari) | 1440 bar | ~1420 bar | ~1136 | ~284 |
| H4 (120 hari) | 720 bar | ~700 bar | ~560 | ~140 |
| D1 (2 tahun) | 520 bar | ~500 bar | ~400 | ~100 |
