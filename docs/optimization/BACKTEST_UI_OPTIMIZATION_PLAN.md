# Backtest Dashboard UI Optimization — Development Plan

**Date**: 2026-07-16
**Source PRD**: [BACKTEST_DASHBOARD_UI_OPTIMIZATION_PRD.md](file:///Users/nizar/MyProject/al-syaka-quant-ai/docs/optimization/BACKTEST_DASHBOARD_UI_OPTIMIZATION_PRD.md)
**Target File**: [backtest-candlestick.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx)
**Other Charts**: [equity-curve.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/equity-curve.tsx), [monthly-heatmap.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/monthly-heatmap.tsx)

---

## Current State Analysis

### Stack
| Komponen | Detail |
|----------|--------|
| Chart Library | `lightweight-charts` v4.2.1 |
| UI Framework | Next.js 14 + React 18 |
| Styling | Tailwind CSS + shadcn/ui |
| Dashboard Pages | `page.tsx`, `backtest-candlestick.tsx`, 5 chart komponen |
| Other Charts | `recharts` v2.12.0 (equity curve, heatmap, breakdowns) |

### Current Rendering Approach

```
Backtest Result (JSON)
  → BacktestCandlestick component
    → createChart() + addCandlestickSeries()
    → setData(ohlc) → semua candlestick
    → setMarkers(markers) → entry/exit markers dengan profit text
    → setTimeout(50ms) → addLineSeries() per trade untuk SL/TP
```

### Performance Metrics (Current)

| Metric | Value |
|--------|-------|
| Trades rendered | Semua (via markers) |
| Markers per trade | 2 (entry + exit) |
| SL/TP lines per trade | 2 (masing-masing 1 LineSeries) |
| Marker text | Profit ($) — langsung di marker |
| SL/TP drawing | setTimeout 50ms (viewport-aware) |
| Time range selector | `Date.now()` based (bisa offset) |
| Viewport culling | Hanya SL/TP lines, **tidak** untuk markers |
| Zoom level awareness | Tidak ada |

---

## Phase 1: Viewport Culling (PRIORITY: HIGH)

### Masalah
Semua marker di-set via `candleSeries.setMarkers(markers)`. lightweight-charts tetap merender semua marker meskipun di luar viewport. Dengan 500+ trades = 1000+ markers, rendering jadi lambat.

### Solusi
Gunakan `subscribeVisibleTimeRangeChange()` untuk mendeteksi perubahan viewport, lalu filter marker yang visible.

### Implementation

```typescript
// 1. Subscribe ke visible range change
const handleVisibleRange = (range: TimeRange | null) => {
    if (!range) return;
    const visStart = range.from as number;
    const visEnd = range.to as number;
    
    const visibleMarkers = allMarkers.filter(m => {
        const t = m.time as number;
        return t >= visStart && t <= visEnd;
    });
    
    candleSeries.setMarkers(visibleMarkers);
};

chart.timeScale().subscribeVisibleTimeRangeChange(handleVisibleRange);

// 2. Simpan semua marker untuk refiltering
const allMarkers = [...]; // semua marker
candleSeries.setMarkers(allMarkers); // initial render
```

### Code Changes
- File: `backtest-candlestick.tsx`
- Tambah: `subscribeVisibleTimeRangeChange` callback
- Simpan: `allMarkersRef` untuk akses dari callback
- Filter: marker berdasarkan visible range sebelum `setMarkers()`

### Risk
- Perlu throttle/debounce (300ms) untuk menghindari re-render berlebihan saat panning cepat
- Marker count masih fixed di 1000

---

## Phase 2: Zoom Level Rendering (PRIORITY: HIGH)

### Masalah
Pada zoom out (melihat 365 hari), marker individu tidak berguna — terlalu padat. Pada zoom in (melihat 1 hari), butuh detail maksimal.

### Solusi
Hitung zoom level dari `getVisibleLogicalRange()`, lalu pilih rendering strategy:

```
Zoom Level     | Bars Visible | Rendering Strategy
---------------|-------------|-------------------
FAR (0)        | > 5000      | No markers, only equity line overlay
MEDIUM (1)     | 1000-5000   | Entry/exit only (no text labels)
CLOSE (2)      | 200-1000    | Entry/exit + pips, SL/TP on hover
VERY_CLOSE (3) | < 200       | Full detail: entry/exit, pips, SL/TP, confidence
```

### Implementation

```typescript
function getZoomLevel(chart: IChartApi): number {
    const logicalRange = chart.timeScale().getVisibleLogicalRange();
    if (!logicalRange) return 0;
    
    const visibleBars = logicalRange.to - logicalRange.from;
    if (visibleBars > 5000) return 0;   // FAR
    if (visibleBars > 1000) return 1;    // MEDIUM
    if (visibleBars > 200) return 2;     // CLOSE
    return 3;                              // VERY_CLOSE
}
```

### Code Changes
- File: `backtest-candlestick.tsx`
- Tambah: `getZoomLevel()` function
- Modifikasi: `handleVisibleRange` — panggil `getZoomLevel()` untuk tentukan detail
- Modifikasi: Marker rendering — hapus `text` untuk zoom MEDIUM

---

## Phase 3: Trade Clustering (PRIORITY: MEDIUM)

### Masalah
Di zoom level FAR/MEDIUM, banyak trade saling tumpuk. Markernya tidak terbaca.

### Solusi
Grupkan trade yang berdekatan, render sebagai single marker dengan count badge.

```
Zoom FAR:
  [5 trades] [3 trades] [12 trades] ...
  
Zoom CLOSE:
  [BUY] [SELL] [BUY] [SELL] [SELL] ...
```

### Implementation

```typescript
function clusterTrades(
    trades: TradePlot[], 
    zoomLevel: number
): Array<{time: number, count: number, ...}> {
    const timeWindow = zoomLevel === 0 ? 86400 * 7 :  // FAR: cluster per week
                       zoomLevel === 1 ? 86400 :       // MEDIUM: cluster per day
                       0;                              // CLOSE: no clustering

    if (timeWindow === 0) return trades.map(t => ({...t, count: 1}));
    
    // Sort by time, group by timeWindow buckets
    const clusters: Array<{...}> = [];
    // ... grouping logic
    
    return clusters;
}
```

---

## Phase 4: Tooltip Only (PRIORITY: MEDIUM)

### Masalah
Saat ini profit text langsung di marker. Ini membuat marker jadi besar dan padat.

### Solusi
Hapus profit text dari marker. Tambahkan crosshair tooltip yang muncul saat hover.

### Implementation (Opsi A: lightweight-charts native)

```typescript
chart.applyOptions({
    crosshair: { mode: CrosshairMode.Normal },
});

chart.subscribeCrosshairMove((param) => {
    if (!param.time || !param.point) return;
    
    // Cari trade di timestamp ini
    const trade = findTradeAt(param.time as number);
    if (trade) {
        showTooltip(param.point.x, param.point.y, trade);
    }
});
```

### Implementation (Opsi B: Custom overlay HTML)
Gunakan div absolute di atas chart container yang muncul/ilang sesuai hover position.

**Rekomendasi**: Opsi B karena lebih fleksibel untuk menampilkan multi-line info (signal, entry/exit, profit, SL/TP, result).

---

## Phase 5: Marker Filtering (PRIORITY: LOW — Depend on Phase 3)

### Masalah
Tidak ada kontrol untuk filter trade di chart — user melihat SEMUA trade.

### Solusi
Tambah filter bar di atas chart dengan opsi:

| Filter | Options |
|--------|---------|
| Result | ALL, WIN, LOSS, PENDING |
| Signal | ALL, BUY, SELL |
| Session | ALL, ASIA, LONDON, NEWYORK |
| Regime | ALL, TRENDING, SIDEWAYS, HIGH_VOL |
| Profit | ALL, Positive, Negative |

### Implementation
Tambahkan state `tradeFilters` dan filter `allMarkers` sebelum render.

---

## Phase 6: Trade Density View (PRIORITY: LOW)

### Masalah
User tidak bisa melihat distribusi trade secara visual di chart — hanya dari tabel.

### Solusi
Tambahkan histogram density di bawah chart (timeframe yang sama) yang menunjukkan jumlah trade per periode waktu.

### Implementation
Gunakan `chart.addHistogramSeries()` (tersedia di lightweight-charts) sebagai secondary series.

```typescript
const densitySeries = chart.addHistogramSeries({
    priceFormat: { type: 'volume' },
    priceScaleId: 'density',
});
// Set data di bawah chart
```

---

## Phase 7: Heatmap Overlay (PRIORITY: LOW — Separate Component)

### Masalah
Tidak ada visualisasi performa per kombinasi (session × regime, month × direction).

### Solusi
Heatmap sudah ada di `MonthlyHeatmap` (recharts). Tinggal ditambah heatmap baru untuk:
- Session × Regime
- Hour × DayOfWeek
- Profit factor per month

Ini bisa jadi komponen baru, bukan overlay di chart utama.

---

## Phase 8: Lazy Marker Rendering (PRIORITY: HIGH)

### Masalah
`setMarkers(markers)` dipanggil dengan semua marker sekaligus. Untuk data besar (500+ trades), ini blocking.

### Solusi
Render marker dalam batch (100 per batch) menggunakan `requestAnimationFrame` atau microtask.

```typescript
function renderMarkersBatched(
    candleSeries: ISeriesApi<"Candlestick">,
    allMarkers: any[],
    batchSize = 100,
    delay = 0 // ms between batches
) {
    let idx = 0;
    const renderNextBatch = () => {
        const batch = allMarkers.slice(0, idx + batchSize);
        candleSeries.setMarkers(batch);
        idx += batchSize;
        if (idx < allMarkers.length) {
            setTimeout(renderNextBatch, delay);
        }
    };
    renderNextBatch();
}
```

### Performance Impact
- **Before**: `setMarkers(1000)` — 1 frame, ~16ms blocking
- **After**: `setMarkers(100)` × 10 batches — 10 frames, ~1-2ms each, no jank

---

## Phase 9: Progressive Detail Loading (PRIORITY: MEDIUM)

### Masalah
Semua data (ohlc, trades, lines) dimuat sekaligus saat `result` tersedia.

### Solusi
Load data secara progresif:
1. **Tahap 1**: OHLC candlestick (+200ms)
2. **Tahap 2**: Market regime (ADX/BB) overlay (+200ms)
3. **Tahap 3**: Trade markers (batch, +100ms per batch)
4. **Tahap 4**: SL/TP lines (setelah markers, +50ms)

Ini bisa diintegrasikan dengan SSE streaming yang sudah ada. Saat SSE `type: "complete"` diterima, tahap 1 langsung jalan. Tahap 2-4 jalan bertahap via setTimeout.

---

## Phase 10: Canvas Optimization (PRIORITY: MEDIUM)

### Masalah
Setiap SL/TP line butuh `addLineSeries()` baru. Dengan 250 trades × 2 lines = 500 series. lightweight-charts handle seriessecara internal.

### Solusi
1. Gunakan **satu LineSeries** per price level (SL/TP) dengan data points untuk SEMUA trade → jauh lebih efisien
2. Atau render SL/TP via Canvas API langsung

### Opsi A: Single LineSeries per Level

```typescript
// Sebagai ganti 500 LineSeries:
const slSeries = chart.addLineSeries({...});
slSeries.setData(allSLPoints);  // semua SL point dalam satu series

const tpSeries = chart.addLineSeries({...});
tpSeries.setData(allTPPoints);  // semua TP point dalam satu series
```

Ini TIDAK akan menghasilkan garis terputus antar trade. Solusi: gunakan `NaN` sebagai pemisah:
```typescript
const slData = [];
trades.forEach(t => {
    slData.push({ time: entryTime, value: t.sl });
    slData.push({ time: exitTime, value: t.sl });
    slData.push({ time: exitTime + 1, value: NaN }); // pemisah
});
```

---

## Implementation Timeline

### Phase Ordering (Dependencies)

```
Phase 1: Viewport Culling ← START HERE (foundation untuk semua optimization)
  ├─ Phase 8: Lazy Rendering ← independen, bisa parallel
  │
  └─ Phase 2: Zoom Level Rendering ← butuh Phase 1
       ├─ Phase 3: Trade Clustering ← butuh Phase 2
       │    └─ Phase 5: Marker Filtering ← butuh Phase 3
       │
       ├─ Phase 4: Tooltip Only ← independen dari Phase 2, tapi synergy
       │
       └─ Phase 9: Progressive Detail ← independen, tapi synergy
            └─ Phase 10: Canvas Optimization ← butuh Phase 9
    
Phase 6: Trade Density ← bisa parallel setelah Phase 1
Phase 7: Heatmap Overlay ← komponen baru, independen
```

### Recommended Iteration Plan

| Iteration | Phases | Effort | Deliverable |
|-----------|--------|--------|-------------|
| **Iteration 1** | Phase 1 + 8 | 2-3h | Viewport-aware markers + batching |
| **Iteration 2** | Phase 2 | 1-2h | Zoom level rendering (FAR/MEDIUM/CLOSE) |
| **Iteration 3** | Phase 3 + 5 | 2-3h | Trade clustering + filter controls |
| **Iteration 4** | Phase 4 | 2-3h | Tooltip (custom HTML overlay) |
| **Iteration 5** | Phase 9 + 10 | 2-3h | Progressive loading + Canvas optimization |
| **Iteration 6** | Phase 6 + 7 | 3-4h | Density histogram + Heatmap baru |

---

## Effort Estimation

| Phase | Complexity | Effort | Risk | Priority |
|-------|-----------|--------|------|----------|
| P1: Viewport Culling | Medium | 2-3h | Low | HIGH |
| P2: Zoom Level Rendering | Medium | 1-2h | Low | HIGH |
| P3: Trade Clustering | Medium | 1-2h | Medium | MEDIUM |
| P4: Tooltip Only | High | 2-3h | Medium | MEDIUM |
| P5: Marker Filtering | Low | 1h | Low | LOW |
| P6: Density View | Medium | 1-2h | Medium | LOW |
| P7: Heatmap Overlay | Low | 1-2h | Low | LOW |
| P8: Lazy Rendering | Low | 1h | Low | HIGH |
| P9: Progressive Loading | Medium | 1-2h | Medium | MEDIUM |
| P10: Canvas Optimization | High | 1-2h | High | MEDIUM |

**Total Estimated Effort**: 14-22 jam

---

## Key Files

| File | Purpose | Changes Needed |
|------|---------|---------------|
| [backtest-candlestick.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/components/charts/backtest-candlestick.tsx) | Main chart component | All Phases 1-6, 8-10 |
| [page.tsx](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/dashboard/src/app/backtesting/page.tsx) | Dashboard page | Minor (if add filter UI) |
| New: `backtest-density.tsx` | Density histogram | New component (Phase 6) |
| New: `backtest-heatmap.tsx` | Heatmap overlay | New component (Phase 7) |
| New: `backtest-tooltip.tsx` | Custom tooltip | New component (Phase 4) |

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Marker render time (500 trades) | ~1000 markers semua di-render | Hanya ~50 visible markers |
| SL/TP line count | 2 × total trades | 2 lines total (1 SL + 1 TP) |
| Chart interaction | No hover info | Full tooltip on hover |
| Time range selector | Date.now()-based | Data-based |
| Zoom level | None | 4 levels (FAR→VERY_CLOSE) |
| First paint time | Wait all result | Progressive (OHLC first) |
