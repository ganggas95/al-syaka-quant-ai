# Trading Playbook — Al-Syaka Quant AI

> Dokumen ini berisi skenario trading untuk berbagai kondisi pasar. Setiap skenario menunjukkan bagaimana platform Al-Syaka Quant AI merespons kondisi pasar yang berbeda berdasarkan aturan yang telah ditetapkan.

---

## Daftar Isi

- [Skenario 1: Trending Bullish](#skenario-1-trending-bullish)
- [Skenario 2: Trending Bearish](#skenario-2-trending-bearish)
- [Skenario 3: Range Market](#skenario-3-range-market)
- [Skenario 4: Reversal Bullish](#skenario-4-reversal-bullish)
- [Skenario 5: Reversal Bearish](#skenario-5-reversal-bearish)
- [Skenario 6: Volatile Market](#skenario-6-volatile-market)
- [Skenario 7: Conflict Macro vs Technical](#skenario-7-conflict-macro-vs-technical)
- [Skenario 8: Consecutive Losses](#skenario-8-consecutive-losses)
- [Skenario 9: News Event](#skenario-9-news-event)
- [Skenario 10: Gap Open](#skenario-10-gap-open)

---

## Skenario 1: Trending Bullish

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | EURUSD |
| Timeframe | H1 |
| Market Regime | TRENDING |
| ADX | 32 (strong trend) |
| RSI | 58 (momentum bullish, tidak overbought) |
| EMA Alignment | Harga > EMA 20 > EMA 50 (bullish alignment) |
| BOS | Terkonfirmasi (break of structure bullish) |
| H4 Trend | BULLISH |
| D1 Trend | BULLISH |
| Macro Bias | BULLISH (confidence 75%, strength 65%) |
| Support | 1.1020 |
| Resistance | 1.1100 |
| ATR (H1) | 0.0050 (50 pips) |

### Signal yang Dihasilkan

| Komponen | Output |
|----------|--------|
| Technical Signal | BUY |
| Confidence | 82% |
| Composite Score | 78 (HIGH) |
| Market Structure | market_structure: 72, momentum: 68, trend: 80, volatility: 75, ai_prediction: 70 |
| Final Decision | BUY |
| Decision Reason | Strong technical signal (82%) with trending regime — recommend BUY |
| Conflict | Tidak ada |

### Execution Plan

| Parameter | Nilai |
|-----------|-------|
| Entry Price | 1.1050 (saat pullback ke EMA 20) |
| Stop Loss | 1.0975 (1.5x ATR = 75 pips di bawah entry) |
| Take Profit | 1.1200 (3.0x ATR = 150 pips di atas entry) |
| Risk/Reward | 1:2.0 |
| Lot Size (balance $10k) | 0.13 lot |
| Risk Amount | $100 (1.0%) |
| Strategy Mode | trend_following |
| Trade Quality | EXCELLENT |

### Exit Plan

1. **TP1 (2.0x ATR = 1.1150):** Exit 50% posisi, pindahkan SL ke break even (1.1050).
2. **TP2 (3.0x ATR = 1.1200):** Exit 50% sisa posisi.
3. **Jika harga lanjut setelah TP1:** Gunakan trailing stop 1.5x ATR (75 pips).
4. **Jika terjadi CHOCH bearish:** Exit semua posisi, terlepas dari profit/loss.

### Risk Scenario

- **Jika SL tersentuh:** Loss $100 (1.0% dari balance). Catat di journal. Lanjutkan trading normal.
- **Jika TP tercapai:** Profit $200 (2.0% dari balance). Catat di journal.

---

## Skenario 2: Trending Bearish

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | GBPUSD |
| Timeframe | H1 |
| Market Regime | TRENDING |
| ADX | 28 (strong trend) |
| RSI | 42 (momentum bearish, tidak oversold) |
| EMA Alignment | Harga < EMA 20 < EMA 50 (bearish alignment) |
| BOS | Terkonfirmasi (break of structure bearish) |
| H4 Trend | BEARISH |
| D1 Trend | BEARISH |
| Macro Bias | BEARISH (confidence 70%, strength 55%) |
| ATR (H1) | 0.0060 (60 pips) |

### Signal yang Dihasilkan

| Komponen | Output |
|----------|--------|
| Technical Signal | SELL |
| Confidence | 78% |
| Composite Score | 75 (HIGH) |
| Final Decision | SELL |
| Strategy Mode | trend_following |
| Trade Quality | GOOD |

### Execution Plan

| Parameter | Nilai |
|-----------|-------|
| Entry Price | 1.2500 (saat retracement ke EMA 20) |
| Stop Loss | 1.2590 (1.5x ATR = 90 pips di atas entry) |
| Take Profit | 1.2320 (3.0x ATR = 180 pips di bawah entry) |
| Risk/Reward | 1:2.0 |
| Lot Size (balance $10k) | 0.11 lot |
| Risk Amount | $100 (1.0%) |

### Catatan

- Pullback ke EMA 20 dalam downtrend adalah entry point standar untuk trend following.
- Pastikan retracement tidak terlalu dalam (tidak boleh break EMA 50).
- Jika harga break di atas EMA 50, trend melemah. Pertimbangkan untuk menunda entry.

---

## Skenario 3: Range Market

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | EURUSD |
| Timeframe | H1 |
| Market Regime | RANGE |
| ADX | 12 (very weak trend) |
| RSI | 58 (netral, tidak ekstrem) |
| BOS | Tidak ada |
| CHOCH | Tidak ada |
| H4 Trend | NEUTRAL |
| D1 Trend | NEUTRAL |
| Macro Bias | NEUTRAL |
| Support | 1.0950 |
| Resistance | 1.1030 |
| Range Width | 80 pips |
| ATR (H1) | 0.0030 (30 pips) |

### Signal yang Dihasilkan

| Komponen | Output |
|----------|--------|
| Technical Signal | NEUTRAL (dengan bias mean reversion) |
| Confidence | 45% |
| Composite Score | 58 (MEDIUM) |
| Final Decision | WAIT |
| Strategy Mode | mean_reversion |

### Execution Plan (jika harga mendekati support/resistance)

**Skenario A: Harga mendekati support (1.0950)**

| Parameter | Nilai |
|-----------|-------|
| Entry Price | 1.0960 (konfirmasi bounce dari support) |
| Stop Loss | 1.0920 (1.0x ATR = 40 pips di bawah support) |
| Take Profit | 1.1000 (midpoint range, RR 1:1) |
| Risk/Reward | 1:1.0 |
| Lot Size (balance $10k) | 0.25 lot |
| Risk Amount | $50 (0.5%, reduced) |
| Trade Quality | FAIR |

**Skenario B: Harga mendekati resistance (1.1030)**

| Parameter | Nilai |
|-----------|-------|
| Entry Price | 1.1020 (konfirmasi reject dari resistance) |
| Stop Loss | 1.1060 (1.0x ATR = 40 pips di atas resistance) |
| Take Profit | 1.0980 (midpoint range, RR 1:1) |
| Risk/Reward | 1:1.0 |
| Lot Size (balance $10k) | 0.25 lot |
| Risk Amount | $50 (0.5%, reduced) |

### Catatan

- Range market memberikan risk yang lebih rendah tetapi juga reward yang lebih rendah. Gunakan risk reduced (0.5%).
- Jika ADX turun di bawah 10, range bisa berkontraksi lebih lanjut. Kurangi target TP.
- Jika ADX naik di atas 15, waspadai potensi transisi ke VOLATILE atau TRENDING. Siapkan strategi alternatif.

---

## Skenario 4: Reversal Bullish

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | XAUUSD (Gold) |
| Timeframe | H1 |
| Market Regime | REVERSAL |
| ADX | 35 (trend kuat menjelang exhaustion) |
| RSI | 25 (oversold) |
| BOS | Ada exhaustion BOS bearish |
| CHOCH | Terkonfirmasi (change of character bullish) |
| FVG | Terisi (fair value gap filled) |
| Liquidity Sweep | Terjadi |
| H4 Trend | BEARISH (melemah) |
| D1 Trend | BULLISH (konteks makro) |
| Macro Bias | BULLISH (dari D1) |
| ATR (H1) | 1.20 |

### Signal yang Dihasilkan

| Komponen | Output |
|----------|--------|
| Technical Signal | BUY |
| Confidence | 72% |
| Composite Score | 70 (HIGH) |
| Final Decision | BUY |
| Decision Reason | Technical signal (72%) supported by bullish macro bias — recommend BUY |
| Strategy Mode | breakout (counter-trend) |

### Execution Plan

| Parameter | Nilai |
|-----------|-------|
| Entry Price | 1920.00 (setelah candle bullish konfirmasi) |
| Stop Loss | 1908.00 (1.0x ATR = 12.0 di bawah entry) |
| Take Profit | 1942.00 (1.83x ATR = 22.0 di atas entry) |
| Risk/Reward | 1:1.83 |
| Lot Size (balance $10k) | 0.42 lot |
| Risk Amount | $50 (0.5%, reduced untuk reversal) |
| Trade Quality | GOOD |

### Konfirmasi Entry

Untuk reversal, diperlukan konfirmasi tambahan sebelum entry:

1. **Candle konfirmasi:** Candle bullish dengan close di atas high candle sebelumnya.
2. **Volume:** Volume meningkat dibandingkan rata-rata 20 periode.
3. **FVG:** Fair value gap terisi (retest level).
4. **Liquidity Sweep:** Harga menyapu swing low sebelum reversal.
5. **RSI:** RSI mulai naik dari zona oversold.

### Exit Plan

- Gunakan SL ketat (1.0x ATR) karena ini counter-trend trade.
- TP lebih besar (3.5x ATR) karena risiko yang lebih tinggi.
- Jika harga kembali di bawah entry, evaluasi dan exit manual.

---

## Skenario 5: Reversal Bearish

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | USDJPY |
| Timeframe | H1 |
| Market Regime | REVERSAL |
| ADX | 38 (trend kuat, potensi exhaustion) |
| RSI | 76 (overbought) |
| BOS | Ada exhaustion BOS bullish |
| CHOCH | Terkonfirmasi (change of character bearish) |
| Divergence | Bearish divergence (harga higher high, RSI lower high) |
| H4 Trend | BULLISH (melemah) |
| D1 Trend | BULLISH (konteks makro) |
| ATR (H1) | 0.50 |

### Signal yang Dihasilkan

| Komponen | Output |
|----------|--------|
| Technical Signal | SELL |
| Confidence | 68% |
| Composite Score | 72 (HIGH) |
| Final Decision | SELL |
| Strategy Mode | breakout (counter-trend) |

### Execution Plan

| Parameter | Nilai |
|-----------|-------|
| Entry Price | 150.00 (setelah candle bearish konfirmasi) |
| Stop Loss | 150.50 (1.0x ATR = 50 pips di atas entry) |
| Take Profit | 148.25 (3.5x ATR = 175 pips di bawah entry) |
| Risk/Reward | 1:3.5 |
| Lot Size (balance $10k) | 1.0 lot (USDJPY pip value = $6.67) |
| Risk Amount | $50 (0.5%) |

### Catatan Penting

- Reversal trade memiliki risiko lebih tinggi karena melawan trend utama.
- Pastikan konfirmasi reversal kuat (CHOCH + divergence + FVG).
- Jika harga melanjutkan trend lama (tidak reversal), exit segera. Jangan menahan posisi reversal yang gagal.

---

## Skenario 6: Volatile Market

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | GBPJPY |
| Timeframe | H1 |
| Market Regime | VOLATILE |
| ADX | 22 (moderate, tidak jelas arah) |
| RSI | 55 (fluktuatif) |
| BOS | Beberapa false breakout |
| FVG | Banyak fair value gap |
| Spread | Melebar (0.8 - 1.2 pips) |
| H4 Trend | NEUTRAL |
| D1 Trend | NEUTRAL |
| Macro Bias | NEUTRAL |
| ATR (H1) | 0.80 |

### Signal yang Dihasilkan

| Komponen | Output |
|----------|--------|
| Technical Signal | NEUTRAL |
| Confidence | 35% |
| Composite Score | 52 (LOW) |
| Final Decision | WAIT |
| Decision Reason | Low conviction across all inputs (confidence 35%) — recommend WAIT for clearer setup |
| Strategy Mode | adaptive |

### Tindakan

Dalam kondisi VOLATILE dengan composite score LOW:

1. **Jangan entry.** Tidak ada setup yang jelas.
2. **Tunggu volatility contraction** (Bollinger squeeze).
3. **Pantau ADX:** Jika ADX naik di atas 25 dengan BOS, market bertransisi ke TRENDING.
4. **Pantau RSI:** Jika RSI mencapai ekstrem, market bertransisi ke REVERSAL.

### Jika Terpaksa Entry (Composite Score HIGH)

Jika composite score mencapai HIGH (>= 75) meskipun regime VOLATILE:

| Parameter | Nilai |
|-----------|-------|
| Lot Size | 0.5x dari normal (risk 0.75%) |
| SL | 2.0x ATR (lebih lebar dari biasanya) |
| TP | 2.5x ATR (lebih konservatif) |
| Time-based Exit | Exit setelah 12 jam jika TP belum tercapai |

---

## Skenario 7: Conflict Macro vs Technical

### Kondisi Pasar

| Parameter | Nilai |
|-----------|-------|
| Symbol | EURUSD |
| Timeframe | H1 |
| Technical Signal | BUY |
| Technical Confidence | 65% |
| Composite Score | 62 (MEDIUM) |
| Market Regime | TRENDING |
| Macro Bias | BEARISH |
| Macro Confidence | 55% |
| Macro Strength | 45% |

### Conflict Detection

Berdasarkan implementasi `FinalDecisionEngine._detect_conflict()`:

```python
# Technical signal = BUY, macro bias = BEARISH
# Macro confidence = 55% (>= 30)
# Macro strength = 45% (>= 20)
# Technical confidence = 65% (>= 50, jadi macro tidak override)
# Direct conflict: BUY vs BEARISH = True
conflict = True
```

### Final Decision

| Komponen | Output |
|----------|--------|
| Conflict Detected | True |
| Final Decision | HEDGE |
| Decision Reason | Technical signal is BUY but macro bias is bearish — recommend HEDGE to reduce exposure |

### Execution Plan untuk HEDGE

**Opsi 1: Hedge dengan Pair Berkorelasi**
- BUY EURUSD (sesuai signal teknikal) dengan lot size reduced (0.5% risk).
- BUY USDCHF (pair dengan korelasi negatif tinggi) dengan lot size yang sama.

**Opsi 2: Hedge dengan Options**
- BUY EURUSD (posisi spot).
- BUY put option pada EURUSD untuk proteksi downside.

**Opsi 3: Tidak Entry (WAIT)**
- Jika tidak bisa melakukan hedge, pilih WAIT.
- Tunggu hingga konflik terresolve (macro bias berubah atau teknikal melemah).

### Aturan Conflict Handling

| Technical | Macro | Macro Confidence | Macro Strength | Result |
|-----------|-------|-----------------|----------------|--------|
| BUY | BEARISH | >= 60 | >= 50 | Macro override: SELL |
| BUY | BEARISH | 30 - 59 | >= 20 | Conflict: HEDGE |
| BUY | BEARISH | < 30 | < 20 | Tidak conflict: ikuti teknikal |
| SELL | BULLISH | >= 60 | >= 50 | Macro override: BUY |
| SELL | BULLISH | 30 - 59 | >= 20 | Conflict: HEDGE |
| SELL | BULLISH | < 30 | < 20 | Tidak conflict: ikuti teknikal |

---

## Skenario 8: Consecutive Losses

### Kondisi

Trader mengalami 4 consecutive losses berturut-turut.

### Response Sistem

Berdasarkan implementasi `RiskManager`:

```python
# Setelah 3 consecutive losses
risk_pct = 0.005  # 0.5% (turun dari 1.0%)

# Setelah 5 consecutive losses
risk_pct = 0.0025  # 0.25%
```

### Action Plan

| Jumlah Loss | Tindakan | Risk per Trade | Syarat Entry |
|------------|----------|----------------|-------------|
| 1-2 | Trading normal | 1.0% | Normal |
| 3 | Kurangi risk | 0.75% | Composite score >= 65 |
| 4 | Kurangi risk lagi | 0.50% | Composite score >= 75, regime TRENDING |
| 5+ | Stop trading | 0.25% | Evaluasi strategi total |

### Evaluasi Setelah 4 Losses

1. **Review keempat trade:** Analisis apakah aturan diikuti dengan benar.
2. **Cek market regime:** Apakah regime berubah tanpa terdeteksi?
3. **Cek parameter:** Apakah SL terlalu ketat? Apakah TP terlalu jauh?
4. **Cek psikologis:** Apakah ada deviation dari trading plan?

### Recovery Trade

Setelah evaluasi, lakukan recovery dengan aturan ketat:

- Hanya 1 trade per hari.
- Hanya pada pair dengan performa historis terbaik.
- Composite score harus HIGH (>= 75).
- Regime harus TRENDING.
- Risk hanya 0.5% (setengah dari normal).

---

## Skenario 9: News Event

### Kondisi

Rilis berita Non-Farm Payrolls (NFP) dalam 30 menit.

### Pre-News Actions

1. **30 menit sebelum news:**
   - Hentikan semua new entry.
   - Evaluasi posisi yang sudah ada.
   - Jika ada posisi dengan floating loss > 2x ATR, pertimbangkan untuk close.

2. **15 menit sebelum news:**
   - Jika posisi sudah profit > 1x ATR, tutup 50% (scale out).
   - Pindahkan SL untuk sisa posisi ke break even.

### During News

- Jangan melakukan entry baru selama 15 menit setelah rilis.
- Biarkan volatilitas mereda.
- Perhatikan apakah price membuat struktur baru (BOS/CHOCH) setelah news.

### Post-News Actions

1. **15 menit setelah news:**
   - Evaluasi dampak news terhadap trend.
   - Jika struktur baru terbentuk, pertimbangkan entry.
   - Jika harga masih fluktuatif tanpa arah, tunggu 30 menit lagi.

2. **Signal setelah news:**
   - Gunakan parameter yang lebih konservatif.
   - SL: 2.0x ATR (lebih lebar).
   - TP: 2.5x ATR (lebih pendek).
   - Risk: 0.5% (dikurangi).

### Jadwal News Penting

| News | Hari | Waktu (UTC) | Dampak |
|------|------|-------------|--------|
| Non-Farm Payrolls (NFP) | Jumat pertama bulan | 12:30 | Sangat Tinggi |
| FOMC Rate Decision | 8x setahun | 18:00 | Sangat Tinggi |
| CPI (Inflasi) | Bulanan | 12:30 | Tinggi |
| GDP | Kuartalan | 12:30 | Tinggi |
| ECB Rate Decision | 8x setahun | 12:15 | Tinggi |
| BOJ Rate Decision | 8x setahun | Variabel | Tinggi |

---

## Skenario 10: Gap Open

### Kondisi

Pasar buka dengan gap (setelah weekend atau news besar). EURUSD open di 1.1080, sebelumnya close di 1.1050 (gap 30 pips bullish).

### Evaluasi Gap

| Jenis Gap | Implikasi | Tindakan |
|-----------|-----------|----------|
| Common Gap | Biasanya terisi (filled) | Tunggu fill, lalu entry searah trend |
| Breakaway Gap | Awal trend baru | Entry searah gap |
| Runaway Gap | Tengah trend | Lanjutkan posisi |
| Exhaustion Gap | Akhir trend | Waspada reversal |

### Tindakan Berdasarkan Posisi

**Jika tidak ada posisi:**
- Jangan entry saat gap. Tunggu 30-60 menit untuk melihat apakah gap terisi.
- Jika gap tidak terisi dan harga melanjutkan: entry searah gap.
- Jika gap terisi: entry counter-gap (mean reversion).

**Jika ada posisi LONG:**
- Gap menguntungkan (30 pips profit unrealized). Pertahankan posisi.
- Pindahkan SL ke break even.

**Jika ada posisi SHORT:**
- Gap merugikan (30 pips loss). Evaluasi:
  - Jika gap < SL distance: pertahankan posisi, tunggu retracement.
  - Jika gap > SL distance: posisi sudah auto-closed. Cari entry baru.

### Aturan Gap Trading

1. Jangan entry dalam 15 menit pertama setelah gap.
2. Jika gap > 2x ATR: market dalam kondisi ekstrem. Hindari entry.
3. Jika gap terisi dalam 1 jam: mean reversion, entry counter-gap.
4. Jika gap bertahan > 1 jam: breakout, entry searah gap.

---

## Lampiran: Decision Matrix Cepat

### Matrix: Technical Signal vs Macro Bias

| Teknikal \ Makro | BULLISH | NEUTRAL | BEARISH |
|------------------|---------|---------|---------|
| **BUY** | BUY (high conf) | BUY (moderate) | HEDGE / WAIT |
| **NEUTRAL** | Macro override: BUY* | WAIT | Macro override: SELL* |
| **SELL** | HEDGE / WAIT | SELL (moderate) | SELL (high conf) |

*Macro override hanya berlaku jika macro confidence >= 60% dan macro strength >= 50%.

### Matrix: Market Regime vs Strategy

| Regime \ Score | LOW (< 55) | MEDIUM (55-74) | HIGH (>= 75) |
|----------------|-----------|---------------|-------------|
| **TRENDING** | WAIT | BUY/SELL (0.75%) | BUY/SELL (1.0%) |
| **RANGE** | WAIT | Mean rev (0.5%) | Mean rev (0.75%) |
| **REVERSAL** | WAIT | WAIT | Counter-trend (0.5%) |
| **VOLATILE** | WAIT | WAIT | Adaptive (0.75%) |

### Matrix: Trade Quality vs Action

| Quality | Action | Risk |
|---------|--------|------|
| EXCELLENT | Entry full | 1.0% |
| GOOD | Entry standard | 0.75% |
| FAIR | Entry reduced | 0.5% |
| POOR | Tidak entry | 0% |

---

*Dokumen ini adalah bagian dari platform Al-Syaka Quant AI. Semua skenario bersifat ilustratif berdasarkan parameter default. Hasil aktual dapat bervariasi tergantung kondisi pasar.*
