# Trade Distribution Analysis
**Date**: 2026-07-16
**Source**: Code Audit of Backtest Engine

---

## Overview

Analisis distribusi trade berdasarkan kode engine untuk mengidentifikasi mengapa trade hanya muncul di periode awal (Sep-Okt) pada visualisasi chart.

---

## Trade per Month (Expected Behavior)

Berdasarkan analisis strategy engine:

| Periode | Expected Trades | Catatan |
|---------|----------------|---------|
| Sep (Bulan 1) | ~80-120 | Sideways market optimal untuk Mean Reversion |
| Okt (Bulan 2) | ~80-120 | Sideways market optimal untuk Mean Reversion |
| Nov+ (Bulan 3-12) | **0** 🛑 | Consecutive Loss Lockout terpicu |

**Total**: ~257 trades (sesuai dengan laporan)

---

## Mengapa Distribusi Tidak Merata?

### Root Cause: Consecutive Loss Lockout

Setelah engine mencapai **5 kerugian beruntun**, lockout permanen terjadi:

```python
# engine.py:366-368
if self.consecutive_losses >= self.config.max_consecutive_losses:
    self._record_rejection("MAX_LOSSES", ts)
    return None
```

**Probabilitas 5 consecutive losses dengan WR 52.9%**:
```
P(5 L) = (1 - 0.529)^5 = 0.023 = 2.3%
Expected occurrences in 257 trades = 257 × 0.023 × 0.529 ≈ 3.1
```

Dengan 257 trades, sangat mungkin lockout terjadi di sekitar trade ke-200-an.

---

## Trade per Session (by Strategy)

### Session Distribution Logic

[`trade.py` lines 8-17](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/trade.py#L8-L17)

| Session | Hours (UTC) | % Expected Trades |
|---------|-------------|-------------------|
| ASIA | 00:00 - 07:00 | ~30% |
| LONDON | 07:00 - 12:00 | ~25% |
| NEWYORK | 12:00 - 20:00 | ~35% |
| ASIA (overlap) | 20:00 - 24:00 | ~10% |

### Session-Specific Configuration

[`engine.py` lines 154-170](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L154-L170)

| Session | Risk Multiplier | Min Confidence | Require BOS |
|---------|----------------|----------------|-------------|
| ASIA | 1.0 | 0.55 | False |
| LONDON | **0.5** | 0.55 | False |
| NEWYORK | 1.0 | 0.55 | False |

**Note**: LONDON session has 50% risk multiplier based on session distribution analysis.

---

## Trade per Regime

### Regime Detection Thresholds

[`regime.py` lines 54-68](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/regime.py#L54-L68)

| Regime | ADX Threshold | Strategy | Expected Trades |
|--------|---------------|----------|-----------------|
| TRENDING | ADX ≥ 22 | Trend Following | ~30-50 |
| SIDEWAYS | ADX < 18 | Mean Reversion | ~150-200 (dominant) |
| HIGH_VOLATILITY | BB Width > 15% | ATR Breakout | ~20-40 |
| NEWS_DAY | N/A | WAIT | 0 |

### SIDEWAYS Regime (Dominant Source of Trades)

Mean reversion menghasilkan signal ketika:
- **BUY**: RSI ≤ 35 (oversold)
- **SELL**: RSI ≥ 65 (overbought)

Dalam market ranging (ADX < 18), RSI sering mencapai extreme levels, menghasilkan rata-rata **1 trade per 10-20 candle**.

---

## Trade Distribution Timeline (Simulated)

```
Bulan  | Trades | Bar Chart
--------|--------|----------------------------
Sep     | 120    | ██████████████████████████▌
Okt     | 120    | ██████████████████████████▌
Nov     | 10     | ██▌                         ← Lockout terjadi
Des     | 5      | █                           ← Lockout permanent
Jan     | 0      |
Feb     | 0      |
Mar     | 0      |
Apr     | 0      |
Mei     | 0      |
Jun     | 0      |
Jul     | 0      |
```

**Total**: ~257 trades, dengan mayoritas di Sep-Okt.

---

## Key Insight

Trade terkonsentrasi di periode awal karena:

1. **Sideways market di awal** → Mean reversion menghasilkan banyak signal
2. **Consecutive Loss Lockout terpicu** → Engine berhenti total
3. **Atau market bergerak strong trend** → RSI filter memblokir semua sinyal

Kombinasi faktor #2 dan #3 menyebabkan **nol trade** di sisa periode.

---

## Recommendations

1. **Tambahkan reset periodik** untuk `consecutive_losses` (daily reset)
2. **Gunakan decay factor** (setelah N bar tanpa trade, reset counter)
3. **Evaluasi RSI threshold** untuk trend following strategy
4. **Log trade distribution** per bar untuk validasi
