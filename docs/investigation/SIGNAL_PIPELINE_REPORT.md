# Signal Pipeline Report
**Date**: 2026-07-16
**Source**: Code Audit of Backtest Engine

---

## Signal Flow Diagram

```
                    ┌──────────────────────┐
                    │  Candle (i = 100..N)  │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  No Open Position?   │───❌ POSITION_OPEN → Skip
                    └──────────┬───────────┘
                               │ YES
                    ┌──────────▼───────────┐
                    │  Risk Guards         │
                    │  • Daily Loss ($500) │───❌ DAILY_LOSS
                    │  • Weekly Loss ($1.5k)│───❌ WEEKLY_LOSS
                    │  • Consec Loss (5)  │───❌ MAX_LOSSES ⚠️
                    └──────────┬───────────┘
                               │ PASS
                    ┌──────────▼───────────┐
                    │  Regime Detection    │
                    │  (ADX + BB Width)    │
                    └──────────┬───────────┘
                               │
                    ┌──────────▼───────────┐
                    │  Strategy Signal     │
                    │  • Trend Following   │───❌ TRENDING_NO_SIGNAL
                    │  • Mean Reversion    │───❌ SIDEWAYS_NO_SIGNAL
                    │  • ATR Breakout      │───❌ HIGH_VOL_NO_SIGNAL
                    │  • NEWS_DAY → WAIT   │───❌ NEWS_DAY
                    └──────────┬───────────┘
                               │ VALID SIGNAL
                    ┌──────────▼───────────┐
                    │  Confidence Filter   │
                    │  (per-strategy min)  │───❌ LOW_CONFIDENCE
                    └──────────┬───────────┘
                               │ PASS
                    ┌──────────▼───────────┐
                    │  Session Intelligence│
                    │  • Session confidence│───❌ LOW_CONFIDENCE (session)
                    │  • BOS Filter       │───❌ BOS_FILTER (LONDON only)
                    └──────────┬───────────┘
                               │ PASS
                    ┌──────────▼───────────┐
                    │  Macro Engine        │
                    │  (H4/D1 Analysis)    │
                    │  + Final Decision    │───❌ MACRO_WAIT
                    └──────────┬───────────┘
                               │ GO
                    ┌──────────▼───────────┐
                    │  Regime × Session    │
                    │  Cross Filter        │───❌ REGIME_SESSION
                    └──────────┬───────────┘
                               │ PASS
                    ┌──────────▼───────────┐
                    │    OPEN TRADE 🎯     │
                    └──────────────────────┘
```

---

## Pipeline Statistics (Expected)

| Stage | Total | % of Candles |
|-------|-------|-------------|
| **Total Candle** | ~8,760 (365d × 24h) | 100% |
| After Warmup (100 bars) | ~8,660 | 98.9% |
| No Open Position Check | ~8,660 | 100% |
| **Pass Risk Guards** | ~8,600 | 99.3% |
| **Pass Regime Detection** | ~8,600 | 100% |
| **Strategy Produces Signal** | ~500-800 | 5.7-9.1% |
| **Pass Confidence Filter** | ~400-600 | 4.6-6.8% |
| **Pass Session Intelligence** | ~380-550 | 4.3-6.3% |
| **Pass Macro Engine** | ~350-500 | 4.0-5.7% |
| **Trade Opened** | ~257 | 2.9% |
| **Trade Closed** | ~257 | 100% of opened |
| **Trade Visualized** | **50** | **19.5%** ❌ |

---

## Signal Rejection Categories

### Rejection Codes

| Code | Source | Impact |
|------|--------|--------|
| `POSITION_OPEN` | Loop guard | High (waiting for close) |
| `DAILY_LOSS` | Risk guard | Medium (resets daily) |
| `WEEKLY_LOSS` | Risk guard | Medium (resets weekly) |
| `MAX_LOSSES` | Risk guard | **CRITICAL** (permanent lockout) |
| `TRENDING_NO_SIGNAL` | Strategy | Normal (no setup) |
| `SIDEWAYS_NO_SIGNAL` | Strategy | Normal (no setup) |
| `HIGH_VOL_NO_SIGNAL` | Strategy | Normal (no setup) |
| `NEWS_DAY` | Strategy | Low (rare) |
| `LOW_CONFIDENCE` | Confidence filter | Normal |
| `BOS_FILTER` | Session intelligence | Low (LONDON only) |
| `MACRO_WAIT` | Final decision | Low (rarely triggered) |
| `REGIME_SESSION` | Cross filter | Low (disabled by default) |

### Category Mapping

```python
# engine.py:303-316
REASON_TO_CATEGORY = {
    "POSITION_OPEN":       "Others",
    "DAILY_LOSS":          "Others",
    "WEEKLY_LOSS":         "Others",
    "MAX_LOSSES":          "Others",          ← BUG: should be tracked separately
    "SIDEWAYS_NO_SIGNAL":  "Sideways Market",
    "TRENDING_NO_SIGNAL":  "Sideways Market",
    "HIGH_VOL_NO_SIGNAL":  "Others",
    "NEWS_DAY":            "News Hour",
    "LOW_CONFIDENCE":      "Low Confidence",
    "BOS_FILTER":          "Others",
    "MACRO_WAIT":          "Low Confidence",
    "REGIME_SESSION":      "Others",
}
```

⚠️ **FINDING**: `MAX_LOSSES` dikategorikan sebagai "Others" — seharusnya kategori terpisah untuk monitoring.

---

## Strategy Signal Detail

### Trend Following
[`engine.py` lines 480-517](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L480-L517)

| Condition | BUY | SELL |
|-----------|-----|------|
| EMA Relationship | EMA12 > EMA50 | EMA12 < EMA50 |
| RSI Filter | RSI < 70 (not OB) | RSI > 30 (not OS) |
| Confidence Formula | `0.55 + (RSI/100) × 0.25` | `0.55 + (1-RSI/100) × 0.25` |
| Max Confidence | 0.9 | 0.9 |

### Mean Reversion
[`engine.py` lines 519-553](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L519-L553)

| Condition | BUY | SELL |
|-----------|-----|------|
| Entry Signal | RSI ≤ 35 | RSI ≥ 65 |
| Confidence Formula | `0.50 + (35-RSI)/35 × 0.30` | `0.50 + (RSI-65)/35 × 0.30` |
| Max Confidence | 0.85 | 0.85 |

### ATR Breakout
[`engine.py` lines 555-588](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L555-L588)

| Condition | BUY | SELL |
|-----------|-----|------|
| Entry Signal | Close > BB Upper | Close < BB Lower |
| Confidence | Fixed 0.7 | Fixed 0.7 |

---

## Critical Finding: RSI Filter in Strong Trend

Di strong trending market:
- **Uptrend**: EMA12 > EMA50 ✅, tapi RSI > 70 ❌ (overbought)
- **Downtrend**: EMA12 < EMA50 ✅, tapi RSI < 30 ❌ (oversold)

**Akibat**: **Strategy menghasilkan 0 sinyal di strong trend.**

Ini adalah **design choice** dari strategy — RSI digunakan untuk menghindari entry setelah pergerakan besar. Namun, efek sampingnya adalah engine tidak bisa trading di tren kuat.

---

## Recommendations

1. **Konfirmasi lockout dengan logging**: Tambahkan log `consecutive_losses` setiap bar di loop utama
2. **Separate `MAX_LOSSES` category**: Pisahkan dari "Others" di signal breakdown
3. **Review RSI thresholds**: Evaluasi apakah filter RSI terlalu ketat untuk trend following
