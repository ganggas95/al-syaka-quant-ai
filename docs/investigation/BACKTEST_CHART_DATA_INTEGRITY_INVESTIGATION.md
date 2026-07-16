# Backtest Chart Data Integrity Investigation

**Author:** Lead AI Engineer  
**Status:** Investigation Required  
**Priority:** HIGH  
**Module:** Backtesting Dashboard  
**Scope:** Frontend Visualization & Data Validation (Non-Backend Logic)

---

# Background

Pada dashboard Backtesting ditemukan bahwa visualisasi **Price Chart with Trades** tidak menampilkan hasil yang sesuai dengan ekspektasi.

Contoh temuan:

- Trade marker hanya muncul pada sebagian kecil timeline.
- Jumlah trade pada hasil backtest mencapai ratusan hingga ribuan, namun visualisasi hanya memperlihatkan sebagian trade.
- Candlestick terlihat tidak sinkron dengan posisi trade.
- Garis Stop Loss dan Take Profit terlihat memanjang sepanjang chart.
- UI TradingView bekerja normal tetapi data yang diterima tampak tidak konsisten.

Dugaan awal menunjukkan bahwa akar masalah berada pada **pipeline data**, bukan pada library chart.

---

# Objective

Melakukan investigasi menyeluruh terhadap proses pengiriman data dari Backtesting Engine menuju komponen visualisasi agar dapat memastikan bahwa:

- Data OHLC lengkap.
- Timestamp sinkron.
- Dataset chart identik dengan dataset backtest.
- Seluruh trade dapat divisualisasikan.

---

# Investigation Scope

Investigasi hanya mencakup:

- Data Integrity
- Timestamp Mapping
- OHLC Dataset
- Trade Visualization
- Frontend Rendering

Tidak diperbolehkan mengubah:

- Trading Strategy
- AI Model
- Risk Management
- Signal Generation
- Backtesting Algorithm

---

# Investigation Checklist

---

## 1. Verify OHLC Dataset

### Objective

Pastikan jumlah candle sesuai dengan periode backtest.

Contoh:

365 hari

Timeframe H1

Expected:

```
365 × 24
≈ 8760 candle
```

Investigasi:

- Berapa jumlah candle sebenarnya?
- Apakah terdapat missing candle?
- Apakah terdapat duplicated candle?

Output:

```
Expected Candle

8760

Actual Candle

________
```

---

## 2. Verify Timeframe

Pastikan timeframe chart sama dengan timeframe backtest.

Misal:

```
Backtest

H1

↓

Chart

H1
```

Bukan:

```
Backtest

H1

↓

Chart

H4
```

Checklist:

- timeframe request
- timeframe response
- timeframe chart

---

## 3. Verify Timestamp

Bandingkan timestamp berikut:

```
Price Candle

timestamp
```

```
Trade Entry

entryTime
```

```
Trade Exit

exitTime
```

Pastikan seluruhnya menggunakan format yang sama.

Misalnya:

```
UTC
```

atau

```
Unix Milliseconds
```

Jangan sampai:

```
Price

UTC

Trade

GMT+7
```

karena akan menyebabkan mapping gagal.

---

## 4. Verify Dataset Consistency

Pastikan chart menggunakan dataset yang sama dengan engine backtest.

Kemungkinan bug:

```
Backtest

CSV A

↓

Chart

CSV B
```

Checklist:

- source data
- file
- cache
- API endpoint
- symbol
- timeframe

---

## 5. Verify Trade Coverage

Hitung coverage trade.

Contoh:

```
Total Trade

978
```

Berapa trade yang berhasil dipetakan ke candle?

Output:

```
Matched

________

Missing

________
```

Coverage minimal:

```
99%
```

Jika coverage rendah maka mapping bermasalah.

---

## 6. Verify Entry Position

Periksa apakah marker BUY dan SELL benar-benar berada pada candle entry.

Contoh ideal:

```
BUY

▲
│
│ Candle
│
```

Bukan:

```
BUY

▲

(di antara candle)
```

Checklist:

- Entry marker
- Exit marker
- Stop Loss marker
- Take Profit marker

---

## 7. Verify SL / TP Rendering

Saat ini garis SL dan TP terlihat memanjang sepanjang chart.

Pastikan rendering mengikuti lifecycle trade.

Ideal:

```
Entry

────────────

Exit
```

Bukan:

```
──────────────────────────────
```

selama satu tahun.

---

## 8. Verify Chart Window

Pastikan chart benar-benar menampilkan seluruh periode.

Contoh:

```
Start

2025-07-16

End

2026-07-16
```

Bukan hanya sebagian window.

---

## 9. Verify Missing Candles

Hitung:

```
Gap Candle
```

Misalnya:

```
2025-10-01

↓

2025-10-04
```

Jika ada gap maka visualisasi trade akan salah.

---

## 10. Verify Duplicate Candle

Cari candle dengan timestamp identik.

Misalnya:

```
2025-11-12 10:00
```

muncul dua kali.

---

# Data Integrity Report

AI Agent wajib menghasilkan laporan berikut.

## OHLC

| Item             | Value |
| ---------------- | ----- |
| Expected Candle  |       |
| Actual Candle    |       |
| Missing Candle   |       |
| Duplicate Candle |       |

---

## Timestamp

| Item            | Status |
| --------------- | ------ |
| UTC Consistency |        |
| Entry Mapping   |        |
| Exit Mapping    |        |
| SL Mapping      |        |
| TP Mapping      |        |

---

## Trade Coverage

| Item         | Value |
| ------------ | ----- |
| Total Trades |       |
| Matched      |       |
| Missing      |       |
| Coverage     |       |

---

## Dataset

| Item           | Status |
| -------------- | ------ |
| Same Symbol    |        |
| Same Timeframe |        |
| Same Period    |        |
| Same Source    |        |

---

# Possible Root Causes

Prioritas investigasi berdasarkan probabilitas.

| Root Cause                                    | Probability |
| --------------------------------------------- | ----------- |
| Timestamp Mapping Error                       | ⭐⭐⭐⭐⭐  |
| OHLC Dataset Incomplete                       | ⭐⭐⭐⭐⭐  |
| Chart Dataset Different from Backtest Dataset | ⭐⭐⭐⭐☆   |
| Timezone Conversion Error                     | ⭐⭐⭐⭐☆   |
| API Cache Issue                               | ⭐⭐⭐☆☆    |
| TradingView Rendering Bug                     | ⭐☆☆☆☆      |

---

# Expected Deliverables

AI Agent wajib menghasilkan:

- Data Integrity Report
- Timestamp Audit
- Coverage Report
- Missing Trade Report
- Missing Candle Report
- Duplicate Candle Report
- Root Cause Analysis
- Sequence Diagram Data Flow
- Screenshot Before vs After (jika ditemukan bug)
- Rekomendasi perbaikan tanpa mengubah Backtesting Engine

---

# Success Criteria

Investigasi dianggap selesai apabila seluruh kondisi berikut terpenuhi.

- ✅ Jumlah candle sesuai dengan periode backtest.
- ✅ Tidak ada missing candle.
- ✅ Tidak ada duplicate candle.
- ✅ Timestamp seluruh data konsisten.
- ✅ Coverage trade ≥ 99%.
- ✅ Seluruh marker BUY dan SELL berada pada candle yang benar.
- ✅ SL dan TP hanya dirender selama trade aktif.
- ✅ Chart menggunakan dataset yang identik dengan Backtesting Engine.
- ✅ Tidak ditemukan ketidaksesuaian antara hasil backtest dan visualisasi.

---

# Notes

Dokumen ini **hanya berfokus pada validasi data dan visualisasi**.

Tidak diperbolehkan melakukan perubahan terhadap:

- AI Prediction
- Trading Strategy
- Risk Management
- Backtesting Logic
- Position Sizing
- Exit Strategy

Seluruh perubahan harus bersifat **observasi, audit, dan validasi**, sehingga apabila ditemukan bug, perbaikannya dapat dilakukan secara terukur tanpa memengaruhi hasil backtest yang telah tervalidasi.
