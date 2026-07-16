# Plan: Visualisasi Proses Backtesting dengan Candlestick Chart

---

## Ringkasan

Menambahkan visualisasi candlestick chart ke halaman Backtesting yang menampilkan pergerakan harga selama periode backtest beserta overlay trade (entry/exit, SL/TP, arah sinyal). Saat ini halaman backtesting hanya menampilkan tabel trades, equity curve, dan metrik performa — tidak ada visualisasi harga.

---

## Analisis Kondisi Saat Ini

### Backend (API)
- **Endpoint:** `POST /api/v1/backtesting/run-stream` (SSE streaming)
- **Response saat ini:** config, metrics, summary, equity_curve, monthly_returns, session_breakdown, trades (50 terakhir)
- **Data trade sudah mencakup:** `entry_time`, `exit_time`, `signal`, `direction`, `entry`, `exit`, `sl`, `tp`, `result`, `pips`, `profit`, `exit_reason`
- **OHLC data** di-fetch di `_fetch_ohlc_data()` tapi **TIDAK disertakan** dalam response
- **Downsampling equity curve:** max 500 titik

### Frontend
- **Page:** [backtesting/page.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/app/backtesting/page.tsx)
- **Components existing:** `EquityCurve`, `MonthlyHeatmap`, `PerfStats`, `SessionBreakdown`, `BacktestProgress`
- **Candlestick component existing:** `SignalCandlestick` di [signal-candlestick.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/signal-candlestick.tsx) — menggunakan `lightweight-charts`, sudah support entry/SL/TP lines dan signal marker
- **Tipe data trade saat ini:** `entry_time`, `signal`, `direction`, `entry`, `exit`, `result`, `pips`, `profit`, `exit_reason` — **tidak termasuk** `sl` dan `tp`

### Library Tersedia
- `lightweight-charts` — sudah terinstall, digunakan di `SignalCandlestick`
- `recharts` — sudah terinstall, digunakan untuk chart lain

---

## Tingkat Kesulitan: **MEDIUM-HIGH (7/10)**

| Faktor | Bobot | Skor | Alasan |
|--------|-------|------|--------|
| Data volume | 3/10 | 8 | ~8760 candles untuk H1 365 hari; perlu downsampling strategy |
| Kompleksitas rendering | 3/10 | 7 | Banyak trade overlay di atas candlestick |
| Backend changes | 2/10 | 5 | Perlu tambah OHLC data di response, size management |
| Frontend integration | 2/10 | 8 | Integrasi dengan SSE stream, loading states, interaktivitas |
| **Total** | **10/10** | **7** | |

---

## Perubahan yang Diperlukan

### 1. Backend: Tambah OHLC Data ke Response

**File:** [routers/backtesting.py](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/api/src/routers/backtesting.py)

**Apa:**
- Di function `_build_response()`, tambahkan field `ohlc` dengan OHLC data yang sudah di-downsample
- Gunakan algoritma downsampling LTTB (Largest Triangle Three Buckets) atau equal-spaced sampling ke max 1000 candles
- Format: array of `{timestamp, open, high, low, close}`

**Mengapa:**
- Frontend butuh data harga untuk merender candlestick chart
- Tanpa ini, frontend harus fetch ulang OHLC data secara terpisah (tidak efisien)
- Downsampling diperlukan karena 8760+ candles terlalu berat untuk dikirim dan dirender

**Bagaimana:**
```python
# Di _build_response(), setelah equity_curve downsampling:
ohlc_data = []
step = max(1, len(df) // 1000)  # max 1000 candles
for i in range(0, len(df), step):
    row = df.iloc[i]
    ohlc_data.append({
        "timestamp": row["timestamp"].isoformat() if hasattr(row["timestamp"], "isoformat") else str(row["timestamp"]),
        "open": row["open"],
        "high": row["high"],
        "low": row["low"],
        "close": row["close"],
    })

return {
    # ... existing fields ...
    "ohlc": ohlc_data,
    # ... existing fields ...
}
```

**Catatan:** OHLC data di sini hanya untuk visualisasi — semua kalkulasi sudah dilakukan oleh engine. Sampling ke 1000 candles sudah cukup untuk memberikan gambaran harga yang akurat.

---

### 2. Frontend: Update Tipe BacktestResult

**File:** [backtesting/page.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/app/backtesting/page.tsx)

**Apa:**
- Tambahkan field `ohlc` ke interface `BacktestResult`
- Tambahkan field `sl` dan `tp` ke trade object (sudah ada di response API tapi tidak di frontend type)

**Mengapa:**
- TypeScript type harus sesuai dengan response API yang baru
- Data `sl` dan `tp` diperlukan untuk overlay di candlestick

**Bagaimana:**
```typescript
interface BacktestResult {
  // ... existing fields ...
  ohlc: Array<{
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
  }>;
  trades: Array<{
    // ... existing fields ...
    sl?: number;     // NEW
    tp?: number;     // NEW
  }>;
}
```

---

### 3. Frontend: Buat BacktestCandlestick Component

**File baru:** `apps/dashboard/src/components/charts/backtest-candlestick.tsx`

**Apa:**
Komponen baru yang menggunakan `lightweight-charts` untuk menampilkan:
- Candlestick chart dari data OHLC
- **Entry markers**: Panah hijau (BUY) di bawah bar, panah merah (SELL) di atas bar
- **Exit markers**: Lingkaran kecil di harga exit
- **SL/TP lines**: Garis putus-putus untuk setiap trade (hanya visible di range trade tersebut)
- **Trade connection lines**: Garis dari entry ke exit untuk menunjukkan holding period
- **Tooltip**: Menampilkan detail trade saat hover di marker

**Mengapa:**
- `lightweight-charts` sudah terinstall dan terbukti bekerja (digunakan di `SignalCandlestick`)
- Performa lebih baik daripada `recharts` untuk candlestick
- Mendukung markers, garis, dan interaktivitas seperti zoom/pan

**Bagaimana (struktur):**
```typescript
interface BacktestCandlestickProps {
  ohlc: Array<{ timestamp: string; open: number; high: number; low: number; close: number }>;
  trades: Array<{
    entry_time: string;
    exit_time?: string;
    signal: string;
    entry: number;
    exit?: number;
    sl?: number;
    tp?: number;
    result: string;
    profit: number;
  }>;
  height?: number;
}
```

Detail implementasi:
1. **Candlestick series** — data OHLC dari response API
2. **Entry/Exit markers** — gunakan `candleSeries.setMarkers()` (seperti di `SignalCandlestick`)
3. **SL/TP lines** — gunakan `chart.addLineSeries()` per trade, hanya di range waktu trade
4. **Performance optimization** — jika trades > 50, hanya tampilkan trades WIN/LOSS terbesar
5. **Time range selector** — dropdown untuk quick zoom: 1M, 3M, 6M, 1Y, ALL
6. **Legend** — menampilkan total trades visible, win/loss count di range visible

---

### 4. Frontend: Update Halaman Backtesting

**File:** [backtesting/page.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/app/backtesting/page.tsx)

**Apa:**
- Integrasikan `BacktestCandlestick` ke dalam layout hasil backtesting
- Tempatkan di antara Equity Curve dan Monthly Heatmap (atau sebagai row baru)

**Mengapa:**
- Visualisasi candlestick adalah elemen utama yang diminta
- Posisi yang natural adalah setelah metrik performa dan sebelum breakdown

**Bagaimana (layout baru):**
```
Results:
  ├── Summary text
  ├── PerfStats (metric cards)
  ├── [BARU] BacktestCandlestick (full width)
  ├── EquityCurve + MonthlyHeatmap (2-col grid)
  ├── SessionBreakdown
  └── Trades Table
```

---

### 5. Loading State untuk Ohlc Data

**File:** [backtesting/page.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/app/backtesting/page.tsx)

**Apa:**
- Saat SSE streaming selesai dan OHLC data tersedia, candlestick chart perlu menunggu data di-render
- Tampilkan skeleton khusus untuk candlestick chart (rectangular placeholder)

**Mengapa:**
- OHLC data bisa besar (1000 titik) — perlu loading indicator
- Konsisten dengan pattern yang sudah ada (BacktestProgress)

---

## File yang Akan Dibuat/Dimodifikasi

| File | Action | Keterangan |
|------|--------|------------|
| `apps/api/src/routers/backtesting.py` | MODIFY | Tambah OHLC data (downsampled) ke response di `_build_response()` |
| `apps/dashboard/src/app/backtesting/page.tsx` | MODIFY | Tambah `ohlc`, `sl`, `tp` ke interface; integrasi component baru |
| `apps/dashboard/src/components/charts/backtest-candlestick.tsx` | CREATE | Komponen candlestick chart dengan trade overlay |

---

## Verifikasi

1. **Backend**: Run API server, hit `POST /api/v1/backtesting/run-stream?symbol=XAUUSD&timeframe=H1&days=30`, pastikan response mengandung field `ohlc` dengan array candles
2. **Frontend**: Build TypeScript tanpa error (`npx tsc --noEmit`)
3. **Visual**: Buka halaman backtesting, run backtest, verifikasi:
   - Candlestick chart muncul dengan data harga
   - Trade markers terlihat di chart
   - Hover tooltip menampilkan detail trade
   - Zoom/pan berfungsi
4. **Performance**: Verifikasi bahwa halaman tidak lag saat render 1000 candles + 50 trades

---

## Catatan Tambahan

- **Prioritas rendering**: Candlestick > markers > lines. Jika performa menurun, prioritaskan candlestick.
- **Trade filtering**: Jika ada >100 trades, hanya tampilkan yang profit/loss signifikan (top 50 by absolute profit). Ini bisa dikonfigurasi.
- **Responsive**: Layout chart harus responsif (gunakan container width, bukan fixed width).
- **Dark theme**: Konsisten dengan tema existing (background transparan, text color #9ca3af).
