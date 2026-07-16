# Visualization Audit Report
**Date**: 2026-07-16
**Component**: `BacktestCandlestick` + `Backend API`

---

## Data Flow: Engine → Screen

```
┌─────────┐     ┌──────────┐     ┌──────────────┐     ┌─────────┐
│ Engine  │────▶│  API     │────▶│  Frontend    │────▶│  Chart  │
│ 257 tr  │     │  50 tr   │     │  50 tr       │     │  ~100   │
│         │     │ [-50:]   │     │ slice(0,100) │     │ markers │
└─────────┘     └──────────┘     └──────────────┘     └─────────┘
    100%            19.5%             19.5%              ~19.5%
```

---

## Truncation Points

### Truncation #1: Backend API

**File**: [`backtesting.py` lines 127-128](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/api/src/routers/backtesting.py#L127-L128)

```python
"trades": [
    ...
    for t in engine.trades[-50:]  # ← HANYA 50 TRADE TERAKHIR
],
```

| Detail | Value |
|--------|-------|
| Total di Engine | 257 |
| Dikirim ke Frontend | **50** |
| Data Loss | **207 trades (80.5%)** |
| Selection | Last 50 (chronological) |

### Truncation #2: Frontend Filter

**File**: [`backtest-candlestick.tsx` line 136](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx#L136)

```typescript
const validTrades = trades
    .filter((t) => t.entry != null && ...)
    .slice(0, 100);  // ← LIMIT 100 TRADES
```

| Detail | Value |
|--------|-------|
| Diterima dari API | 50 |
| Setelah filter | 50 (all valid) |
| Setelah slice | 50 (50 < 100, no-op) |

### Truncation #3: Marker Cap

**File**: [`backtest-candlestick.tsx` lines 172-175](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx#L172-L175)

```typescript
if (markers.length > 200) {
    markers.length = 200;  // ← CAP MARKERS
}
```

| Detail | Value |
|--------|-------|
| Max trades × 2 markers | 100 |
| Cap | 200 |
| Terkena dampak? | Tidak (100 < 200) |

---

## Trade-to-Marker Mapping

Setiap trade menghasilkan **2 marker**:

```typescript
// Entry marker
markers.push({
    time: entryTime,
    position: isBuy ? "belowBar" : "aboveBar",
    color: markerColor,
    shape: isBuy ? "arrowUp" : "arrowDown",
    text: `${t.signal} ${t.profit > 0 ? "+" : ""}$${t.profit}`,
});

// Exit marker (if exited)
markers.push({
    time: exitTime,
    position: "inBar",
    color: t.result === "WIN" ? "#22c55e" : "#ef4444",
    shape: "circle",
    text: `Exit $${t.exit.toFixed(2)}`,
});
```

**Total markers**: 50 trades × 2 = **100 marker** (under 200 cap)

---

## SL/TP Lines Visualization

Hanya ditampilkan untuk trade yang **visible di current time range**:

```typescript
// backtest-candlestick.tsx:189-200
validTrades.forEach((t) => {
    const entryTime = parseTime(t.entry_time);
    const exitTime = t.exit_time ? parseTime(t.exit_time) : entryTime + 86400;

    if (!isTimeInRange(entryTime, visStart, visEnd) &&
        !isTimeInRange(exitTime, visStart, visEnd)) {
        return;  // Skip jika trade tidak visible
    }
    // Draw SL/TP lines...
});
```

Tidak ada limit pada jumlah SL/TP lines — bisa menjadi performance issue dengan banyak trade.

---

## Time Range Selector

```typescript
const TF_OPTIONS = [
    { label: "1M", days: 30 },
    { label: "3M", days: 90 },
    { label: "6M", days: 180 },
    { label: "1Y", days: 365 },
    { label: "ALL", days: Infinity },  // ← DEFAULT
] as const;
```

**Default**: ALL — yang memanggil `chart.timeScale().fitContent()`.

**Masalah potensial**: Filter time range menggunakan `Date.now()` sebagai referensi:
```typescript
const nowTs = Date.now() / 1000;
const fromTs = nowTs - timeRange * 86400;
```

Ini menggunakan waktu **saat ini** (bukan waktu data). Untuk data historis 365 hari, ini bisa menyebabkan offset visual jika data tidak berakhir hari ini.

---

## Summary: Quantifiable Impact

| Metric | Current | Expected (if fixed) |
|--------|---------|---------------------|
| Trades in engine | 257 | 257 |
| Trades sent to frontend | 50 | 257 |
| Trades rendered on chart | 50 | 257 |
| Markers on chart | ~100 | ~514 |
| % of trades visualized | **19.5%** | **100%** |
| SL/TP lines drawn | All visible | All visible |

---

## Root Cause of "Trades Only in Sep-Oct" Chart

Kombinasi dua faktor:

1. **Hanya 50 trade terakhir yang dikirim** — Jika seluruh 257 trade terjadi di Sep-Okt, 50 terakhir juga di Sep-Okt
2. **Consecutive Loss Lockout** — Engine berhenti total setelah mencapai 5 losses

Jika lockout terjadi di sekitar November (trade ke-200), maka 50 trade terakhir (trade #207-257) semuanya terjadi **sebelum** lockout, yaitu di Sep-Okt.

---

## Recommendations

### HIGH PRIORITY
1. **Kirim semua trade** — Hapus `[-50:]` di backend, atau gunakan sampling periodik (setiap Nth trade)
2. **Tambahkan parameter query** untuk limit trades (default: semua, dengan opsi `max_trades=N`)

### MEDIUM PRIORITY
3. **Perbaiki time range filter** — Gunakan timestamp data, bukan `Date.now()`
4. **Tambahkan trade counter** di chart legend (e.g., "Showing 50 of 257 trades")

### LOW PRIORITY
5. **Virtualisasi SL/TP lines** — Hanya render lines untuk trade visible di viewport
