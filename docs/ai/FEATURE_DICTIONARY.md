# Feature Dictionary — Al-Syaka Quant AI

Dokumen ini mendefinisikan seluruh fitur (features) yang digunakan dalam pipeline machine learning Al-Syaka Quant AI. Fitur dihasilkan oleh modul `al_syaka_features` yang berada di `packages/feature-engineering/`.

## 1. Candlestick Features

Fitur ini dihasilkan dari function `candle_features()` pada modul `al_syaka_features.candlestick`. Input yang digunakan: open, high, low, close.

| Nama Fitur       | Tipe    | Deskripsi | Rumus Komputasi |
|------------------|---------|-----------|-----------------|
| `body`           | float   | Besar badan candle (absolute) | `abs(close - open)` |
| `upper_wick`     | float   | Panjang sumbu atas | `high - max(open, close)` |
| `lower_wick`     | float   | Panjang sumbu bawah | `min(open, close) - low` |
| `candle_range`   | float   | Total rentang harga candle | `high - low` |
| `body_ratio`     | float   | Rasio badan terhadap total range | `body / candle_range` |
| `bullish`        | int     | Indikator candle bullish (0/1) | `1 jika close > open, else 0` |
| `bearish`        | int     | Indikator candle bearish (0/1) | `1 jika close < open, else 0` |
| `doji`           | int     | Indikator candle doji (0/1) | `1 jika abs(close-open) <= range*0.1, else 0` |

## 2. Momentum Features

Fitur ini dihasilkan dari function `momentum_features()` pada modul `al_syaka_features.momentum`. Input: close, volume (opsional).

| Nama Fitur          | Tipe  | Deskripsi | Rumus Komputasi |
|---------------------|-------|-----------|-----------------|
| `mom_1`             | float | Price change 1 periode | `close.pct_change(1)` |
| `mom_5`             | float | Price change 5 periode | `close.pct_change(5)` |
| `mom_10`            | float | Price change 10 periode | `close.pct_change(10)` |
| `mom_20`            | float | Price change 20 periode | `close.pct_change(20)` |
| `roc_10`            | float | Rate of Change 10 periode (persen) | `(close / close.shift(10) - 1) * 100` |
| `price_position_10` | float | Posisi harga dalam range 10 periode terakhir | `(close - lowest_10) / (highest_10 - lowest_10)` |
| `vim_10`            | float | Volume-Weighted Momentum 10 periode | `(close*volume).rolling(10).sum() / volume.rolling(10).sum()` -- hanya jika volume tersedia |

## 3. Volatility Features

Fitur ini dihasilkan dari function `volatility_features()` pada modul `al_syaka_features.volatility`. Input: high, low, close, open (opsional).

| Nama Fitur      | Tipe  | Deskripsi | Rumus Komputasi |
|-----------------|-------|-----------|-----------------|
| `tr`            | float | True Range | `max(high-low, abs(high-close.shift()), abs(low-close.shift()))` |
| `atr_5`         | float | Average True Range periode 5 | `tr.rolling(5).mean()` |
| `atr_10`        | float | Average True Range periode 10 | `tr.rolling(10).mean()` |
| `atr_20`        | float | Average True Range periode 20 | `tr.rolling(20).mean()` |
| `volatility_10` | float | Standar deviasi return 10 periode | `close.pct_change().rolling(10).std()` |
| `volatility_20` | float | Standar deviasi return 20 periode | `close.pct_change().rolling(20).std()` |
| `gap`           | float | Gap harga pembukaan | `open - close.shift(1)` -- hanya jika open tersedia |

## 4. Session Features

Fitur ini dihasilkan dari function `session_features()` pada modul `al_syaka_features.session`. Input: timestamps.

| Nama Fitur         | Tipe | Deskripsi | Rentang Waktu (UTC) |
|--------------------|------|-----------|---------------------|
| `asian_session`    | int  | Sesi Asia aktif | 00:00 - 09:00 |
| `london_session`   | int  | Sesi London aktif | 08:00 - 17:00 |
| `us_session`       | int  | Sesi US aktif | 13:00 - 22:00 |
| `london_open`      | int  | Jam pembukaan London | 08:00 - 09:00 |
| `us_open`          | int  | Jam pembukaan US | 13:30 - 14:30 |
| `session_overlap`  | int  | Overlap London-US | 13:00 - 17:00 (0/1) |

## 5. Key Indicators

Fitur ini ditambahkan langsung oleh `FeaturePipeline.compute()` menggunakan fungsi dari `al_syaka_indicators`.

| Nama Fitur          | Tipe  | Periode | Deskripsi | Function |
|---------------------|-------|---------|-----------|----------|
| `sma_20`            | float | 20      | Simple Moving Average | `sma(close, 20)` |
| `sma_50`            | float | 50      | Simple Moving Average | `sma(close, 50)` |
| `ema_20`            | float | 20      | Exponential Moving Average | `ema(close, 20)` |
| `ema_50`            | float | 50      | Exponential Moving Average | `ema(close, 50)` |
| `rsi_14`            | float | 14      | Relative Strength Index | `rsi(close, 14)` |
| `atr_14`            | float | 14      | Average True Range (EMA-based) | `atr(high, low, close, 14)` |
| `ema_distance_20`   | float | 20      | Jarak harga dari EMA 20 (persen) | `(close - ema_20) / close * 100` |
| `ema_distance_50`   | float | 50      | Jarak harga dari EMA 50 (persen) | `(close - ema_50) / close * 100` |
| `bb_upper`          | float | 20,2sd | Bollinger Bands Upper | `sma(close,20) + 2*std(close,20)` |
| `bb_lower`          | float | 20,2sd | Bollinger Bands Lower | `sma(close,20) - 2*std(close,20)` |
| `bb_position`       | float | 20      | Posisi harga dalam Bollinger Bands | `(close - bb_lower) / (bb_upper - bb_lower)` |

## 6. Daftar Lengkap Fitur

Berikut adalah urutan kolom fitur sebagaimana dihasilkan oleh `FeaturePipeline.compute()`:

### Candlestick (8 fitur)
`body`, `upper_wick`, `lower_wick`, `candle_range`, `body_ratio`, `bullish`, `bearish`, `doji`

### Momentum (6-7 fitur)
`mom_1`, `mom_5`, `mom_10`, `mom_20`, `roc_10`, `price_position_10`, (`vim_10` jika volume tersedia)

### Volatility (6-7 fitur)
`tr`, `atr_5`, `atr_10`, `atr_20`, `volatility_10`, `volatility_20`, (`gap` jika open tersedia)

### Session (6 fitur, jika timestamps tersedia)
`asian_session`, `london_session`, `us_session`, `london_open`, `us_open`, `session_overlap`

### Key Indicators (11 fitur)
`sma_20`, `sma_50`, `ema_20`, `ema_50`, `rsi_14`, `atr_14`, `ema_distance_20`, `ema_distance_50`, `bb_upper`, `bb_lower`, `bb_position`

**Total fitur: 31-37 fitur, tergantung ketersediaan volume dan timestamps.**

## 7. Preprocessing

Setelah semua fitur dihitung, `MLPipeline.prepare_data()` melakukan:

1. Mengganti nilai `inf` dan `-inf` dengan `NaN`
2. Menghapus baris yang mengandung `NaN` (menggunakan `dropna()`)
3. Menyelaraskan label dengan index fitur yang tersisa

Hal ini penting karena fitur seperti `mom_20`, `volatility_20`, dan `atr_20` membutuhkan 20 baris data awal untuk kalkulasi, sehingga baris-baris awal akan otomatis di-drop.
