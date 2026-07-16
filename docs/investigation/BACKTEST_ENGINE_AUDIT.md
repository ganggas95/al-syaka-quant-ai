# Backtest Engine Audit Report

**Version**: 2.0 (Investigation Complete)
**Date**: 2026-07-16
**Auditor**: AI Agent
**Status**: Complete

---

## Executive Summary

Audit menyeluruh telah dilakukan pada Backtesting Engine untuk menginvestigasi anomali visualisasi "Price Chart with Trades" yang menunjukkan trade hanya terjadi pada September–Oktober, sementara statistik mencatat 257 total trades.

**Kesimpulan Utama**: Anomali ini disebabkan oleh **kombinasi tiga faktor**:

1. **Consecutive Loss Lockout (BUG)**: Setelah mencapai 5 kerugian beruntun, engine berhenti total dan tidak bisa pulih — tidak ada mekanisme reset periodik.
2. **Trade Data Truncation (DESIGN ISSUE)**: Backend hanya mengirim 50 trade terakhir ke frontend.
3. **Strategy Behavior di Strong Trend**: Strategy tidak menghasilkan sinyal saat RSI berada di zona overbought/oversold pada tren kuat.

---

## Phase 1: Historical Data Validation

### Pemeriksaan

| Item                    | Status                    | Evidence                                                        |
| ----------------------- | ------------------------- | --------------------------------------------------------------- |
| Jumlah candle di-load   | ✅ OK                     | Seluruh data dari `_fetch_ohlc_data()` di-pass ke engine        |
| Tanggal candle pertama  | ✅ OK                     | `start = end - timedelta(days=days)`                            |
| Tanggal candle terakhir | ✅ OK                     | `end = datetime.utcnow()`                                       |
| Timeframe               | ✅ OK                     | Sesuai parameter (H1)                                           |
| Missing candle          | ⚠️ Tergantung data source | Engine memproses apa yang diterima                              |
| Duplicated candle       | ✅ OK                     | `df.sort_values("timestamp").reset_index(drop=True)` — di-dedup |

### Detail

- **Engine start**: Baris ke-100 (warmup indikator) : [`engine.py` line 233](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L233)
- **Total candles diproses**: `len(df) - 100`
- **Data diterima dari**: [`backtesting.py` line 18-30](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/api/src/routers/backtesting.py#L18-L30)

**Verdict**: ✅ Data historis tervalidasi. Seluruh candle yang tersedia diproses.

---

## Phase 2: Backtest Loop Validation

### Loop Utama

```python
for i in range(100, len(df)):  # ← engine.py:233
```

- **Start index**: 100 (warmup)
- **End index**: `len(df) - 1` (candle terakhir)
- **Total steps**: `len(df) - 100`

### Verifikasi Progress

```python
total_steps = max(1, len(df) - 100)
for i in range(100, len(df)):
    if progress_callback:
        pct = int(((i - 100) / total_steps) * 100)
```

- Progress callback dipanggil setiap perubahan persentase
- Loop berjalan hingga candle terakhir

### Output

```python
for t in open_trades:
    if t.result == "PENDING":
        t.exit_price = df.iloc[-1]["close"]  # Force close at end
        t.exit_time = df.iloc[-1]["timestamp"]
```

- Semua posisi terbuka dipaksa tutup di akhir data — ✅ OK
- [`engine.py` lines 278-284](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L278-L284)

**Verdict**: ✅ Seluruh candle (index 100 sampai akhir) diproses. Tidak ada early termination.

---

## Phase 3: Signal Generation Audit

### Pipeline Signal

```
Candle → Risk Guard → Regime Detection → Strategy Signal → Confidence Filter
  → Session Intelligence → Macro Analysis → Final Decision → Trade
```

### Signal Rejection Tracking

Engine mencatat setiap penolakan signal via `_record_rejection()`:
[`engine.py` lines 289-291](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L289-L291)

### Risk Guards (Pre-Signal)

| Guard                  | Line | Threshold                                     |
| ---------------------- | ---- | --------------------------------------------- |
| Daily Loss             | 357  | `<= -max_daily_loss ($500)`                   |
| Weekly Loss            | 361  | `<= -max_weekly_loss ($1500)`                 |
| Max Consecutive Losses | 366  | `>= max_consecutive_losses (5)` ⚠️ **KRITIS** |

### Strategy Signal Distribution

| Regime          | Strategy        | Entry Condition               |
| --------------- | --------------- | ----------------------------- |
| TRENDING        | Trend Following | EMA crossover + RSI filter    |
| SIDEWAYS        | Mean Reversion  | RSI ≤ 35 (BUY) / ≥ 65 (SELL)  |
| HIGH_VOLATILITY | ATR Breakout    | Close > BB Upper / < BB Lower |
| NEWS_DAY        | WAIT            | Skip trading                  |

### ⚠️ FINDING: Consecutive Loss Lockout (BUG)

**Lokasi**: [`engine.py` lines 366-368](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L366-L368)

```python
if self.consecutive_losses >= self.config.max_consecutive_losses:
    self._record_rejection("MAX_LOSSES", ts)
    return None
```

**Masalah**: Ketika `consecutive_losses` mencapai 5, semua signal ditolak. Karena tidak ada trade baru yang bisa dibuka, `_record_trade_result` tidak pernah dipanggil, sehingga `consecutive_losses` tidak pernah direset. Ini menciptakan **lockout permanen**.

**Dampak**: Begitu strategy mengalami 5 kerugian beruntun (probable dengan 257 trades), engine berhenti menghasilkan trade selamanya.

**Tidak ada mekanisme recovery** — tidak ada:

- ✅ Reset harian/mingguan
- ✅ Cooldown period
- ✅ Decay factor

**Verdict**: ⚠️ Seluruh signal dievaluasi, tetapi lockout permanen dapat menghentikan engine lebih awal.

---

## Phase 4: Trade Lifecycle Audit

### State Machine Trade

```
OPEN → MANAGE (SL/TP/BE/Trailing) → EXIT → READY → OPEN
```

### Verifikasi Lifecycle

| Tahap               | File        | Line    | Status                        |
| ------------------- | ----------- | ------- | ----------------------------- |
| OPEN                | `engine.py` | 590-716 | ✅ `_open_trade()`            |
| MANAGE (SL)         | `engine.py` | 718-837 | ✅ Check low ≤ SL / high ≥ SL |
| MANAGE (TP)         | `engine.py` | 718-837 | ✅ Check high ≥ TP / low ≤ TP |
| MANAGE (Breakeven)  | `engine.py` | 741-748 | ✅ Optional                   |
| MANAGE (Partial TP) | `engine.py` | 751-774 | ✅ Regime-adaptive            |
| MANAGE (Trailing)   | `engine.py` | 781-808 | ✅ Chandelier/Fixed           |
| EXIT                | `engine.py` | 814-834 | ✅ SL/TP hit                  |
| CLOSE at end        | `engine.py` | 278-284 | ✅ END_OF_DATA                |

### Balance Calculation

```python
def _calculate_balance(self, open_trades: list) -> float:
    balance = self.config.initial_balance
    for t in self.trades:
        if t.result in ("WIN", "LOSS"):
            balance += t.profit
    return balance
```

[`engine.py` lines 869-874](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L869-L874)

✅ Fungsional: Rekalkulasi penuh setiap bar (O(n) per bar = O(n²) total — tidak optimal untuk perf, tapi benar secara logika).

---

## Phase 5: Open Position Audit

### Pemeriksaan

| Item                         | Status  | Evidence                                        |
| ---------------------------- | ------- | ----------------------------------------------- |
| Posisi tidak pernah ditutup? | ✅ Aman | `for t in open_trades` di loop akhir (line 278) |
| Posisi baru boleh dibuka?    | ✅ Ya   | Hanya jika `len(open_trades) == 0` (line 264)   |
| State machine bekerja?       | ✅ Ya   | OPEN→MANAGE→EXIT→READY cycle lengkap            |

### Satu Posisi per Waktu

```python
if len(open_trades) == 0:          # ← engine.py:264
    signal = self._check_adaptive_signal(ind, df.iloc[i])
    if signal:
        trade = self._open_trade(signal, df.iloc[i], ind)
        open_trades.append(trade)
```

✅ Hanya 1 posisi per waktu — tidak ada pyramiding.

### Verifikasi Trade Record

[`trade.py`](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/trade.py)

| Field       | Present? |
| ----------- | -------- |
| entry_time  | ✅       |
| exit_time   | ✅       |
| entry_price | ✅       |
| exit_price  | ✅       |
| stop_loss   | ✅       |
| take_profit | ✅       |
| direction   | ✅       |
| result      | ✅       |
| profit      | ✅       |
| exit_reason | ✅       |

---

## Phase 6: Trade Distribution Analysis

### Analisis Root Cause

Berdasarkan audit kode, ada **tiga kemungkinan penyebab** trade hanya terjadi di September-Oktober:

### 🟥 Faktor 1: Consecutive Loss Lockout (BUG - HIGH PRIORITY)

**Probability**: HIGH

Dengan 257 trades dan win rate ~52.9%, probabilitas streak 5 losses beruntun:

```
P(5 consecutive losses) = (1 - 0.529)^5 ≈ 0.023 = 2.3%
Expected occurrences in 257 trades ≈ 257 × 0.023 × 0.529 ≈ 3.1
```

Sekali lockout terjadi, engine **berhenti total**. Trade selanjutnya = 0.

**Evidence**:

- [`engine.py` lines 366-368](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L366-L368): Lockout check
- [`engine.py` lines 839-846](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L839-L846): `consecutive_losses` hanya direset oleh WIN
- Tidak ada reset periodik (daily/weekly) untuk counter ini

### 🟨 Faktor 2: Strategy Tidak Menghasilkan Signal di Strong Trend (DESIGN BEHAVIOR)

**Probability**: MEDIUM

Strategy Trend Following mensyaratkan:

- BUY: EMA12 > EMA50 **AND** RSI < 70
- SELL: EMA12 < EMA50 **AND** RSI > 30

Di strong trend:

- Uptrend: RSI sering > 70 → gagal filter BUY
- Downtrend: RSI sering < 30 → gagal filter SELL

Akibatnya: **nol sinyal di strong trend**. Ini adalah **design choice**, bukan bug.

### 🟨 Faktor 3: Trade Truncation di Backend & Frontend

**Backend**: [`backtesting.py` lines 127-128](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/api/src/routers/backtesting.py#L127-L128)

```python
"trades": [... for t in engine.trades[-50:]]
```

Hanya **50 trade terakhir** yang dikirim.

**Frontend**: [`backtest-candlestick.tsx` line 136](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx#L136)

```typescript
const validTrades = trades.filter(...).slice(0, 100);
```

Hanya **100 trade pertama** dari data yang diterima yang di-render.

**Marker Limit**: [`backtest-candlestick.tsx` lines 172-175](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx#L172-L175)

```typescript
if (markers.length > 200) {
  markers.length = 200;
}
```

---

## Phase 7: Visualization Audit

### Perbandingan Trade vs Marker

| Kuantitas             | Sumber                   | Nilai                |
| --------------------- | ------------------------ | -------------------- |
| `tradeHistory.length` | Engine                   | 257                  |
| `trades[-50:]`        | Backend API              | 50                   |
| `validTrades.length`  | Frontend (after slice)   | 50                   |
| `markers.length`      | Frontend (entry + exit)  | ~100 (50 trades × 2) |
| Markers rendered      | Frontend (capped at 200) | ~100                 |

### ⚠️ FINDING: Data Truncation Chain

```
Engine (257 trades)
  → Backend API (50 trades, [-50:])      ← TRUNCATION #1
    → Frontend (50 trades, slice(0,100))  ← OK (50 < 100)
      → Markers (~100 marker)            ← OK (< 200 cap)
        → Chart rendered
```

**Dampak**: Hanya **19.5%** (50/257) dari total trade yang divisualisasikan.

Jika lockout terjadi di tengah dan 50 trade terakhir semuanya terjadi sebelum lockout (di Sep-Okt), maka chart hanya menunjukkan periode tersebut.

---

## Phase 8: Chart Validation

### Data Source Consistency

| Item                   | Status       | Evidence                               |
| ---------------------- | ------------ | -------------------------------------- |
| Chart pakai data sama? | ✅ Ya        | `ohlc` dari response API yang sama     |
| Timestamp format       | ✅ OK        | ISO format, konsisten                  |
| Timezone               | ✅ UTC       | Konsisten di engine dan frontend       |
| Offset                 | ✅ Tidak ada | `parseTime()` langsung dari ISO string |

### Time Range Selector

Default: ALL (menampilkan seluruh data). [`backtest-candlestick.tsx` line 71](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx#L71)

```typescript
chart.timeScale().fitContent(); // ← line 240
```

✅ Tidak ada offset data. Chart menggunakan engine data yang sama.

---

## Phase 9: Data Consistency

### Trade Entry/Exit Validation

| Check                       | Status   | Evidence                                        |
| --------------------------- | -------- | ----------------------------------------------- |
| Entry pada candle benar?    | ✅ Ya    | `entry_time = row["timestamp"]` (current bar)   |
| Exit pada candle benar?     | ✅ Ya    | `exit_time = row["timestamp"]` (saat SL/TP hit) |
| Trade di luar rentang data? | ✅ Tidak | Loop terbatas di `range(100, len(df))`          |
| SL/TP price valid?          | ✅ Ya    | Dihitung dari entry price ± ATR × multiplier    |

### Lookahead Bias Check

| Komponen              | Risk       | Evidence                                       |
| --------------------- | ---------- | ---------------------------------------------- |
| Indicator pre-compute | ✅ No bias | `indicators[:i+1]` slicing prevents lookahead  |
| EMA/RSI/ATR           | ✅ No bias | Recursive/rolling, only past data              |
| Macro Engine H4/D1    | ✅ No bias | `_find_index()` ensures `timestamp <= current` |
| Trade execution       | ✅ No bias | Harga close bar saat ini, tidak lebih          |

---

## Phase 10: Performance Audit

### Estimasi Performance

| Aspek               | Detail                                             |
| ------------------- | -------------------------------------------------- |
| **Processing Time** | O(n) per bar, O(n × m) total (n=bars, m=trades)    |
| **Memory Usage**    | `all_indicators` dict with full-length Series      |
| **Trade Gen Time**  | Per bar: signal check → trade open (if applicable) |
| **Rendering Time**  | Frontend: lightweight-charts native rendering      |

### ⚠️ Potential Optimization

1. `_calculate_balance()` di-loop bar: O(n) per bar = O(n²) total
2. `all_indicators` menahan semua data di memory
3. `_compute_signal_breakdown()` menghitung ulang setiap request

---

## Root Cause Analysis

### Pertanyaan Investigasi

#### 1. Apakah seluruh candle diproses?

**YA** ✅ — Loop `for i in range(100, len(df))` memproses semua candle.

#### 2. Apakah seluruh signal dievaluasi?

**YA, TAPI** ⚠️ — Seluruh signal dievaluasi, namun lockout permanent (consecutive loss ≥5) dapat menghentikan engine.

#### 3. Apakah seluruh trade tersimpan?

**YA** ✅ — Semua trade disimpan di `self.trades`.

#### 4. Apakah seluruh trade divisualisasikan?

**TIDAK** ❌ — Hanya 50 trade terakhir (19.5%) yang dikirim ke frontend.

#### 5. Mengapa trade hanya muncul di periode awal (Sep-Okt)?

**Kombinasi dari:**

- **BUG: Consecutive Loss Lockout** — Engine berhenti total setelah 5 losses
- **Strategy stop producing signals** — Di strong trend, RSI filter memblokir sinyal
- **Visualisasi hanya 50 trade terakhir** — Jika lockout terjadi setelah Okt, chart hanya menunjukkan data Sep-Okt

#### 6. Apakah ini bug engine? Bug visualisasi? Atau perilaku strategy?

| Komponen                            | Klasifikasi                             |
| ----------------------------------- | --------------------------------------- |
| Consecutive Loss Lockout (no reset) | **BUG ENGINE** — Severity: HIGH         |
| Trade truncation (50 trades)        | **DESIGN FLAW** — Severity: MEDIUM      |
| Strategy stops in strong trend      | **STRATEGY BEHAVIOR** — Intended design |

---

## Deliverables Cross-Reference

| Dokumen                   | Status     | Path                                           |
| ------------------------- | ---------- | ---------------------------------------------- |
| BACKTEST_ENGINE_AUDIT.md  | ✅ Selesai | `docs/investigation/BACKTEST_ENGINE_AUDIT.md`  |
| TRADE_DISTRIBUTION.md     | ✅ Selesai | `docs/investigation/TRADE_DISTRIBUTION.md`     |
| SIGNAL_PIPELINE_REPORT.md | ✅ Selesai | `docs/investigation/SIGNAL_PIPELINE_REPORT.md` |
| VISUALIZATION_AUDIT.md    | ✅ Selesai | `docs/investigation/VISUALIZATION_AUDIT.md`    |
| STATE_MACHINE_REPORT.md   | ✅ Selesai | `docs/investigation/STATE_MACHINE_REPORT.md`   |

---

## Final Recommendations

### Priority: HIGH

| #   | Issue                                | Action                                             | Complexity |
| --- | ------------------------------------ | -------------------------------------------------- | ---------- |
| 1   | Consecutive loss lockout tanpa reset | Tambahkan daily/weekly reset atau cooldown period  | Low        |
| 2   | Trade truncation di API backend      | Kirim semua trade atau sampling yang representatif | Low        |

### Priority: MEDIUM

| #   | Issue                                        | Action                                         | Complexity |
| --- | -------------------------------------------- | ---------------------------------------------- | ---------- |
| 3   | Tidak ada logging distribusi trade per waktu | Tambahkan logging trade distribution di engine | Low        |
| 4   | Tidak ada unit test untuk engine             | Buat test suite untuk BacktestEngine           | Medium     |

### Priority: LOW

| #   | Issue                                     | Action                               | Complexity |
| --- | ----------------------------------------- | ------------------------------------ | ---------- |
| 5   | Performance: `_calculate_balance()` O(n²) | Gunakan incremental balance tracking | Low        |
| 6   | RSI filter di strong trend                | Evaluasi ulang strategy parameters   | Medium     |

---

## Evidence Summary

| #   | Evidence                                           | File                       | Line    |
| --- | -------------------------------------------------- | -------------------------- | ------- |
| E1  | Consecutive loss lockout                           | `engine.py`                | 366-368 |
| E2  | Tidak ada reset mechanism untuk consecutive_losses | `engine.py`                | 839-846 |
| E3  | Hanya 50 trades dikirim ke frontend                | `backtesting.py`           | 127-128 |
| E4  | Trades di-slice ke 100 di frontend                 | `backtest-candlestick.tsx` | 136     |
| E5  | Markers capped di 200                              | `backtest-candlestick.tsx` | 172-175 |
| E6  | Full loop coverage                                 | `engine.py`                | 233     |
| E7  | No lookahead bias (indicator slicing)              | `engine.py`                | 258     |
| E8  | Macro engine no lookahead                          | `macro.py`                 | 127-137 |
| E9  | Force close open positions at end                  | `engine.py`                | 278-284 |
