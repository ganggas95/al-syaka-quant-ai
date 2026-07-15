# Entry dan Exit Criteria — Al-Syaka Quant AI

> Dokumen ini menjelaskan kriteria entry dan exit yang digunakan oleh platform Al-Syaka Quant AI. Semua keputusan entry dan exit didasarkan pada analisis komposit dari berbagai engine dan indikator.

---

## Daftar Isi

- [Entry Criteria](#entry-criteria)
- [Composite Score Threshold](#composite-score-threshold)
- [Regime Confirmation](#regime-confirmation)
- [Stop Loss](#stop-loss)
- [Take Profit](#take-profit)
- [Risk/Reward Ratio Targeting](#riskreward-ratio-targeting)
- [Exit Management](#exit-management)
- [Special Scenarios](#special-scenarios)

---

## Entry Criteria

### Hierarki Entry Decision

Alur pengambilan keputusan entry di Al-Syaka Quant AI:

```
UnifiedSignalGenerator.generate()
    |
    +--> Composite Score (threshold check)
    +--> Market Regime (regime confirmation)
    +--> Final Decision (BUY/SELL/WAIT/HEDGE)
    |
    v
RiskManager.evaluate_trade()
    |
    +--> SL/TP calculation (ATR-based)
    +--> Position sizing
    +--> Trade quality assessment
    |
    v
Entry EXECUTED (jika semua kondisi terpenuhi)
```

### Entry Checklist

Sebelum entry, pastikan semua kondisi berikut terpenuhi:

| No | Kondisi | Syarat |
|----|---------|--------|
| 1 | Final Decision | BUY atau SELL (bukan WAIT atau HEDGE) |
| 2 | Composite Score | >= 55 (MEDIUM atau HIGH) |
| 3 | Market Regime | Mendukung strategi yang dipilih |
| 4 | Macro Bias | Tidak conflict dengan sinyal |
| 5 | Trade Quality | FAIR, GOOD, atau EXCELLENT |
| 6 | Risk/Reward | >= 1:2 |
| 7 | Position Sizing | Lot size > 0.01 |
| 8 | Max Positions | Total open positions < 3 |

---

## Composite Score Threshold

### Komponen Composite Score

Berdasarkan implementasi `UnifiedSignalGenerator._calculate_composite_score()`:

| Komponen | Bobot | Indikator | Rentang |
|----------|-------|-----------|---------|
| Market Structure | 35% | BOS, CHOCH, FVG | 20 - 90 |
| Momentum | 20% | RSI (14) | 10 - 90 |
| Trend | 15% | EMA alignment | 10 - 90 |
| Volatility | 10% | ADX (14) | 45 - 75 |
| AI Prediction | 20% | XGBoost/LightGBM | 10 - 90 |

### Rumus Composite Score

```python
composite = (
    structure_component * 0.35 +
    momentum_component * 0.20 +
    trend_component * 0.15 +
    volatility_component * 0.10 +
    ai_component * 0.20
)
```

### Threshold Levels

| Label | Rentang Score | Tindakan |
|-------|--------------|----------|
| HIGH | 75 - 100 | Entry dengan keyakinan tinggi, risk penuh |
| MEDIUM | 55 - 74 | Entry dengan caution, kurangi risk 25% |
| LOW | 0 - 54 | Tidak entry, pilih WAIT |

### Komponen Detail

**Market Structure Component:**
```
Base: 50
+15 jika ada Break of Structure (BOS)
+10 jika ada Change of Character (CHOCH)
+10 jika ada Fair Value Gap (FVG)
Clamp: 20 - 90
```

**Momentum Component (RSI-based):**
```
Jika RSI > 60: score = 50 + (RSI - 60) * 1.2
Jika RSI < 40: score = 50 - (40 - RSI) * 1.2
Jika RSI 40-60: score = 50 (neutral)
Clamp: 10 - 90
```

**Trend Component (EMA-based):**
```
Base: 50
Adjustment = ((EMA_12 - EMA_20) / ATR) * 10
Clamp: 10 - 90
```

**Volatility Component (ADX-based):**
```
Jika ADX >= 25: score = 75 (strong trend)
Jika ADX <= 15: score = 45 (weak/no trend)
Lainnya: score = 60 (moderate)
Default: 60
```

**AI Component:**
```
Jika ada AI confidence: score = clamp(ai_confidence * 100, 10, 90)
Jika tidak ada AI: score = 50 (neutral)
```

---

## Regime Confirmation

### Mapping Regime ke Strategi

Berdasarkan implementasi `UnifiedSignalGenerator._detect_market_regime()`:

| Market Regime | Strategy Mode | Threshold Composite | Action |
|--------------|---------------|--------------------|--------|
| TRENDING | trend_following | >= 65 | BUY/SELL dengan trend |
| RANGE | mean_reversion | >= 55 | BUY di support, SELL di resistance |
| REVERSAL | breakout | >= 70 | BUY/SELL saat breakout konfirmasi |
| VOLATILE | adaptive | >= 70 | Hati-hati, kurangi lot size |

### Deteksi Regime Detail

**TRENDING:**
```
ADX >= 25 AND ada Break of Structure (BOS)
Strategi: Trend following
Risk: Full (1.0%)
```

**REVERSAL:**
```
RSI > 70 (overbought) ATAU RSI < 30 (oversold)
Strategi: Breakout (counter-trend)
Risk: Reduced (0.5%)
```

**RANGE:**
```
ADX <= 15 AND tidak ada BOS AND tidak ada CHOCH
Strategi: Mean reversion
Risk: Reduced (0.5%)
```

**VOLATILE:**
```
Tidak masuk kategori di atas
Strategi: Adaptive
Risk: Reduced (0.75%)
```

---

## Stop Loss

### ATR-Based Stop Loss

Metode utama untuk menentukan stop loss adalah ATR-based, dengan formula:

```python
# LONG position
stop_loss = entry_price - (atr_value * sl_multiplier)

# SHORT position
stop_loss = entry_price + (atr_value * sl_multiplier)
```

### SL Multiplier Configuration

| Level | Multiplier | Keterangan |
|-------|-----------|------------|
| Tight | 1.0x ATR | Untuk range market, scalping |
| Standard | 1.5x ATR | Default untuk semua strategi |
| Wide | 2.0x ATR | Untuk trending market, swing trading |

### Support/Resistance-Based Stop Loss

Metode alternatif ketika level S/R tersedia:

```python
# LONG: SL di bawah support level terdekat
stop_loss = support_level

# SHORT: SL di atas resistance level terdekat
stop_loss = resistance_level
```

### Fixed Pips Stop Loss

Metode fallback ketika ATR dan S/R tidak tersedia:

| Timeframe | Default SL Pips | Keterangan |
|-----------|----------------|-----------|
| M15 | 10 pips | Scalping |
| M30 | 15 pips | Intraday pendek |
| H1 | 20 pips | Intraday standar |
| H4 | 40 pips | Swing trading |
| D1 | 80 pips | Position trading |

### Aturan SL

1. SL tidak boleh lebih besar dari 5% dari entry price.
2. SL harus disesuaikan secara manual jika ada level S/R yang lebih ketat dari ATR-based SL.
3. SL tidak boleh dipindahkan lebih jauh dari entry setelah posisi berjalan (hanya bisa dipindahkan ke arah yang lebih menguntungkan).
4. Dalam kondisi REVERSAL regime, SL harus menggunakan ATR-based multiplier yang lebih ketat (1.0x).

---

## Take Profit

### ATR-Based Take Profit

```python
# LONG position
take_profit = entry_price + (atr_value * tp_multiplier)

# SHORT position
take_profit = entry_price - (atr_value * tp_multiplier)
```

### TP Multiplier Configuration

| Level | Multiplier | Risk/Reward | Keterangan |
|-------|-----------|-------------|-----------|
| Conservative | 2.0x ATR | 1:1.3 | Untuk scalping, range market |
| Standard | 3.0x ATR | 1:2.0 | Default untuk trending |
| Extended | 4.0x ATR | 1:2.7 | Untuk strong trend |

### Partial Take Profit Levels

| Level | Persentase Exit | Target | SL Sisa |
|-------|----------------|--------|---------|
| TP1 (50%) | 50% posisi | 2.0x ATR | Pindahkan SL ke break even |
| TP2 (50%) | 50% posisi | 3.0x ATR (default) | Trailing 1.5x ATR |

### Aturan TP

1. TP minimal harus memberikan Risk/Reward ratio 1:2 (3.0x ATR TP dengan 1.5x ATR SL).
2. TP dapat diperpanjang (trailing) jika trend masih kuat (ADX > 30 dan BOS baru terkonfirmasi).
3. Jangan memindahkan TP lebih dekat ke entry (mengurangi potensi profit).
4. Dalam regime TRENDING, gunakan trailing stop setelah TP tercapai.

---

## Risk/Reward Ratio Targeting

### Minimum RR Requirements

| Market Regime | Minimum RR | Target RR | Keterangan |
|--------------|-----------|-----------|------------|
| TRENDING | 1:2.0 | 1:3.0 | Trend kuat, biarkan profit berjalan |
| RANGE | 1:1.5 | 1:2.0 | Range terbatas, ambil profit cepat |
| REVERSAL | 1:2.5 | 1:3.5 | Risiko lebih tinggi, reward harus lebih besar |
| VOLATILE | 1:2.0 | 1:2.5 | Volatilitas tinggi, SL perlu lebih lebar |

### Cara Menghitung RR

```python
# LONG position
risk = entry_price - stop_loss
reward = take_profit - entry_price
rr_ratio = reward / risk

# SHORT position
risk = stop_loss - entry_price
reward = entry_price - take_profit
rr_ratio = reward / risk
```

### Dynamic RR Adjustment

RR dapat disesuaikan berdasarkan kualitas setup:

```python
def adjust_rr(composite_score: float, regime: str) -> tuple:
    """Adjust SL and TP multipliers based on setup quality."""
    base_sl = 1.5
    base_tp = 3.0

    if composite_score >= 80:
        # High confidence: wider SL, further TP
        sl_mult = base_sl * 1.0
        tp_mult = base_tp * 1.2  # 3.6x ATR
    elif composite_score >= 65:
        # Medium confidence: standard
        sl_mult = base_sl
        tp_mult = base_tp
    else:
        # Low confidence: tighter SL
        sl_mult = base_sl * 0.8  # 1.2x ATR
        tp_mult = base_tp * 0.8  # 2.4x ATR

    return sl_mult, tp_mult
```

---

## Exit Management

### Exit Signals

Posisi harus ditutup ketika salah satu kondisi berikut terpenuhi:

1. **Stop Loss Tersentuh:** Exit otomatis oleh sistem.
2. **Take Profit Tersentuh:** Exit otomatis oleh sistem.
3. **Change of Character (CHOCH):** Struktur trend berubah, exit manual.
4. **Break of Structure (BOS) terbaru:** Exit jika BOS berlawanan arah dengan posisi.
5. **Time-based Exit:** Posisi belum mencapai TP dalam 5 trading days.
6. **Macro Reversal:** Macro bias berubah drastis (dari BULLISH ke BEARISH atau sebaliknya).
7. **Maximum Drawdown Harian Tercapai:** Tutup semua posisi.

### Trailing Stop

Trailing stop digunakan dalam regime TRENDING untuk mengoptimalkan profit:

```python
def update_trailing_stop(current_price: float,
                          current_stop: float,
                          atr_value: float,
                          direction: str) -> float:
    """Update trailing stop based on price movement."""
    trail_distance = atr_value * 1.5

    if direction == "LONG":
        new_stop = current_price - trail_distance
        return max(new_stop, current_stop)  # Hanya pindahkan ke atas
    else:
        new_stop = current_price + trail_distance
        return min(new_stop, current_stop)  # Hanya pindahkan ke bawah
```

### Aturan Trailing Stop

1. Trailing stop diaktifkan setelah harga mencapai 2.0x ATR dari entry.
2. Jarak trailing adalah 1.5x ATR.
3. Trailing stop hanya bergerak satu arah (menguntungkan).
4. Pada REVERSAL regime, trailing stop menggunakan jarak 1.0x ATR (lebih ketat).

---

## Special Scenarios

### Scenario 1: Gap Open

Jika harga open mengalami gap yang melewati SL:

- Jika gap berlawanan arah dan melewati SL, posisi ditutup pada harga open (gap loss diterima).
- Jika gap searah dan melewati TP, posisi ditutup pada harga open (profit diambil).

### Scenario 2: News Event

Sekitar rilis news besar (NFP, FOMC, CPI, dll):

- 30 menit sebelum news: Tidak boleh membuka posisi baru.
- Posisi yang sudah ada: Pertimbangkan untuk mengurangi (scale out) 50% sebelum news.
- 15 menit setelah news: Evaluasi dampak, baru boleh entry kembali.

### Scenario 3: Multiple Signals

Jika beberapa symbol memberikan signal secara bersamaan:

- Prioritaskan symbol dengan composite score tertinggi.
- Maksimum 3 posisi simultan.
- Jangan entry pada pair dengan korelasi tinggi secara bersamaan.

### Scenario 4: Consecutive Losses

Setelah 3 consecutive losses:

- Risk dikurangi dari 1.0% menjadi 0.5%.
- Hanya trading dengan composite score HIGH (>= 75).
- Hanya trading dalam regime TRENDING.
- Setelah 5 consecutive losses, semua trading dihentikan untuk evaluasi.

---

*Dokumen ini adalah bagian dari platform Al-Syaka Quant AI. Parameter entry dan exit dapat disesuaikan berdasarkan hasil backtesting dan kondisi pasar terkini.*
