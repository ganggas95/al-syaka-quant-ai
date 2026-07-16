# Backtest Chart Data Integrity — Investigation Report

## Overview

This report traces the data pipeline from **Python backend → API serialization → frontend → lightweight-charts rendering** to identify root causes of candlestick/trade synchronization issues.

---

## 1. Data Flow Diagram

```
Python Engine (naive UTC datetime)
    │
    ▼
API _build_response()  ──  OHLC downsampled ──  ISO strings
    │
    ▼
SSE JSON stream
    │
    ▼
page.tsx setResult(data.result)   ──  no transformation
    │
    ▼
BacktestCandlestick(ohlc, trades)
    │
    ▼
parseTime(ts) = new Date(ts).getTime()/1000  ──  UTCTimestamp
    │
    ▼
lightweight-charts CandlestickSeries + markers + LineSeries
```

## 2. Root Cause Analysis

### Root Cause #1: OHLC Downsampling (HIGH SEVERITY)

**File:** `backtesting.py:52`

```python
ohlc_step = max(1, len(ohlc_df) // 1000)
```

For a 365-day H1 backtest (8760 candles) → `step = 8` → **only 1095 candles (12.5%) are sent to the frontend**.

| Period | Total Candles | After Downsample | Data Loss |
|--------|-------------|-----------------|-----------|
| 365d H1 | 8,760 | ~1,095 | 87.5% |
| 180d H1 | 4,320 | ~540 | 87.5% |
| 90d H1 | 2,160 | ~270 | 87.5% |
| 30d H1 | 720 | ~720 (step=1) | 0% |

**Impact:**
- Trade entry/exit timestamps frequently fall between downsampled candles
- Trade markers appear to "float" without a corresponding candlestick
- Candlestick visualization shows misleading price action — O,H,L,C of only every 8th bar
- Trade markers match the full resolution, but chart resolution is 8× lower

### Root Cause #2: Naive UTC → Local Timezone Shift (MEDIUM SEVERITY)

**Backend:** `datetime.utcnow()` returns **naive** UTC datetime (no `tzinfo`).

**API:** `.isoformat()` produces `"2025-07-16T10:00:00"` (no timezone suffix).

**Frontend:** `new Date("2025-07-16T10:00:00")` interprets as **browser local time**.

```
Python:  2025-07-16T10:00:00 (naive UTC)
JSON:    "2025-07-16T10:00:00"
Browser (UTC+8):  new Date("2025-07-16T10:00:00") → 2025-07-16T02:00:00 UTC
```

**Impact:**
- All timestamps shifted by browser's timezone offset
- Relative ordering preserved (all data shifted equally)
- Absolute candle times are wrong — a "10:00" candle is displayed as "10:00 local" instead of "10:00 UTC"

### Root Cause #3: Marker Loading Race Condition (MEDIUM SEVERITY)

**Timeline of chart initialization:**

```
0ms    ── Stage 1:  Candle data set
50ms   ── Stage 2:  fitContent() + zoom init
50ms   ──           subscribeVisibleTimeRangeChange fires → debounce 300ms
120ms  ── Stage 3:  buildMarkers() → setMarkers(trades[0..99])
                    renderMarkersBatched starts (batch 100 every 50ms)
120ms  ──           Chart shows first 100 trades (earliest in timeline)
170ms  ──           Chart shows trades[0..199]
220ms  ──           Chart shows trades[0..N] (all trades)
350ms  ──           Viewport debounce fires → filterAndSetMarkers()
                    → correct viewport-filtered markers
```

During 120ms–350ms, users see the **first 100 trades** (chronologically earliest) clustered in the first portion of the timeline, creating the illusion of "trades only on part of the chart."

### Root Cause #4: SL/TP NaN Separator — Data Loss (LOW SEVERITY)

**File:** `backtest-candlestick.tsx:380-395`

```typescript
// Sort by time to ensure ascending order
slData.sort((a, b) => (a.time as number) - (b.time as number));
// Deduplicate by time
const dedupe = (arr: LineData[]) => {
  const seen = new Set<number>();
  return arr.filter((d) => {
    const t = d.time as number;
    if (seen.has(t)) return false;
    seen.add(t);
    return true;
  });
};
```

When multiple trades share the same entry/exit timestamp:
- Only the **first** trade's SL/TP point is kept
- Subsequent trades at the same timestamp lose their SL/TP line segment

### Root Cause #5: renderMarkersBatched vs filterAndSetMarkers Conflict (LOW SEVERITY)

Two competing mechanisms write markers to the same series:
- `renderMarkersBatched()` sets ALL markers progressively
- `filterAndSetMarkers()` sets FILTERED markers (viewport-aware)

Whichever runs last wins, causing flicker during zoom/scroll operations.

---

## 3. Verification Checklist

| Check | Status | Details |
|-------|--------|---------|
| OHLC sorted ascending | ✅ | `engine.py:215` — `df.sort_values("timestamp")` |
| OHLC no duplicates | ⚠️ | Downsampling step guarantees unique indices |
| OHLC data range matches trades | ✅ | Same source DataFrame |
| Trade timestamps in OHLC range | ✅ | Engine runs on same data |
| Timestamp format consistency | ⚠️ | Naive UTC (consistent but shifted by timezone) |
| SL/TP lines bounded | ✅ | Phase 10 — NaN separators bound lines |
| Markers never exceed trades count | ✅ | 1:1 mapping |
| Density data valid | ✅ | Pre-aggregated by bucket |
| Crosshair tooltip matches trades | ✅ | Uses same `tradeTimeMapRef` |
| Volume/spread not sent | ⚠️ | `BACKTEST_ENGINE_AUDIT.md` already documented |
| Fatal candle order errors | ✅ | All previous errors resolved via sorting+dedup |

---

## 4. Recommended Fixes

### Fix #1: Pass Full OHLC Resolution (HIGH PRIORITY)

Replace the static downsampling with resolution-adaptive sampling:

```python
# Option A: Send full data (lightweight-charts handles >5000 candles efficiently)
ohlc_data = [
    {
        "timestamp": row["timestamp"].isoformat(),
        "open": row["open"],
        "high": row["high"],
        "low": row["low"],
        "close": row["close"],
    }
    for _, row in ohlc_df.iterrows()
]

# Option B: Adaptive sampling — pass full data but let frontend decimate
# based on visible range
```

`lightweight-charts` efficiently handles large datasets through its internal viewport culling — sending all OHLC candles is performant.

### Fix #2: Use UTC-Aware Timestamps (MEDIUM PRIORITY)

Add `Z` suffix to ISO strings so JavaScript correctly interprets as UTC:

```python
# In backtesting.py _build_response():
"timestamp": row["timestamp"].isoformat() + "Z"  # UTC marker
```

This ensures `new Date("2025-07-16T10:00:00Z")` is interpreted as UTC regardless of browser timezone.

### Fix #3: Remove Initial Marker Batch (MEDIUM PRIORITY)

Remove the `setMarkers(slice(0, 100))` in Stage 3. Let `filterAndSetMarkers()` be the ONLY source of truth for markers. The viewport debounce will handle the initial render:

```typescript
// Stage 3 (120ms): Build markers only — don't set on series yet
const stage3 = setTimeout(() => {
    allMarkersRef.current = buildMarkers();
    // Trigger viewport filter to set correct markers
    const range = chartRef.current?.timeScale().getVisibleRange();
    if (range) filterAndSetMarkers(range);
}, 120);
```

This eliminates the "first 100 trades" flash.

### Fix #4: Preserve SL/TP at Duplicate Timestamps (LOW PRIORITY)

Instead of deduplication, append a tiny epsilon to time values:

```typescript
// Use micro-offset instead of NaN deduplication
slData.push({ time: (exitTime + 0.001) as UTCTimestamp, value: t.sl });
```

This preserves all data while keeping times unique.

### Fix #5: Unify Marker Update Path (LOW PRIORITY)

Remove `renderMarkersBatched` or make it the ONLY marker setter. Since `filterAndSetMarkers` already provides viewport-optimized markers, the batched approach is redundant.

---

## 5. Summary

| # | Issue | Severity | Status | Impact |
|---|-------|----------|--------|--------|
| 1 | OHLC downsampled to 12.5% | **HIGH** | ⚠️ Root cause of candlestick/trade misalignment | Trade markers at positions without candles |
| 2 | Naive UTC timezone shift | MEDIUM | ⚠️ All timestamps shifted by browser offset | Wrong absolute candle times |
| 3 | Marker loading race condition | MEDIUM | ⚠️ First 100 trades flash in wrong position | Temporary visual artifact (120-350ms) |
| 4 | SL/TP NaN dedup data loss | LOW | ⚠️ Drops 2nd+ trade at same timestamp | Missing SL/TP for overlapping trades |
| 5 | Competing marker setter paths | LOW | ⚠️ renderMarkersBatched vs filterAndSetMarkers | Potential marker flicker |

**Primary recommendation:** Fix #1 (pass full OHLC) will resolve the most visible issue — candlesticks not synced with trade positions. The remaining fixes are progressive improvements.
