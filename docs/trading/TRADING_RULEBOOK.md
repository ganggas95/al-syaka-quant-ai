# Trading Rulebook — Al-Syaka Quant AI

> Dokumen ini berisi aturan-aturan utama trading yang digunakan oleh platform Al-Syaka Quant AI. Setiap aturan dirancang untuk menjaga konsistensi, disiplin, dan objektivitas dalam pengambilan keputusan trading.

---

## Daftar Isi

- [Prinsip Dasar Trading](#prinsip-dasar-trading)
- [Aturan Trend Following](#aturan-trend-following)
- [Aturan Mean Reversion](#aturan-mean-reversion)
- [Aturan Breakout](#aturan-breakout)
- [Aturan Risk Management](#aturan-risk-management)
- [Aturan Position Sizing](#aturan-position-sizing)
- [Aturan Entry dan Exit](#aturan-entry-dan-exit)
- [Aturan Multi-Timeframe Confirmation](#aturan-multi-timeframe-confirmation)
- [Aturan Trading Harian](#aturan-trading-harian)

---

## Prinsip Dasar Trading

1. **Trading berdasarkan sistem, bukan emosi.** Semua keputusan trading harus berdasarkan signal yang dihasilkan oleh Unified Signal Generator dan Final Decision Engine.

2. **Utamakan konservasi modal.** Aturan risk management adalah prioritas utama dan tidak boleh dilanggar dalam kondisi apapun.

3. **Gunakan konfirmasi multi-timeframe.** Entry hanya dilakukan jika trend pada H4 dan D1 sejalan (alignment) atau setidaknya tidak bertentangan.

4. **Jangan memaksakan entry.** Jika komposit score berada di bawah threshold atau market regime tidak mendukung, pilih WAIT.

5. **Catat semua trading.** Setiap entry dan exit harus dicatat di trading journal untuk evaluasi dan improvement.

6. **Evaluasi secara berkala.** Lakukan review mingguan terhadap performa trading, hitung win rate, profit factor, dan maximum drawdown.

---

## Aturan Trend Following

Strategi trend following digunakan ketika market berada dalam regime **TRENDING** (ADX >= 25 dengan Break of Structure).

### Syarat Entry Trend Following

| Komponen | Syarat |
|----------|--------|
| Market Regime | TRENDING |
| ADX | >= 25 |
| Break of Structure | Terkonfirmasi (BOS terjadi) |
| Composite Score | >= 65 (MEDIUM atau HIGH) |
| Multi-Timeframe | Trend H4 dan D1 searah |
| Macro Bias | Tidak bertentangan dengan sinyal |

### Aturan Pelaksanaan

- **BUY (LONG):** Harga berada di atas EMA 20 dan EMA 50, dengan struktur higher highs dan higher lows.
- **SELL (SHORT):** Harga berada di bawah EMA 20 dan EMA 50, dengan struktur lower highs dan lower lows.
- **Konfirmasi tambahan:** RSI tidak boleh overbought (untuk BUY) atau oversold (untuk SELL). Overbought = RSI > 70, Oversold = RSI < 30.
- **Exit trend following:** Exit ketika terjadi Change of Character (CHOCH) atau struktur trend mulai melemah.

### Parameter Indikator

| Indikator | Parameter | Fungsi |
|-----------|-----------|--------|
| EMA 12 | Period 12 | Momentum jangka pendek |
| EMA 20 | Period 20 | Trend jangka menengah |
| EMA 50 | Period 50 | Trend jangka panjang |
| ADX | Period 14 | Kekuatan trend |
| ATR | Period 14 | Volatilitas untuk SL/TP |

---

## Aturan Mean Reversion

Strategi mean reversion digunakan ketika market berada dalam regime **RANGE** (ADX <= 15, tidak ada BOS atau CHOCH).

### Syarat Entry Mean Reversion

| Komponen | Syarat |
|----------|--------|
| Market Regime | RANGE |
| ADX | <= 15 |
| Break of Structure | Tidak ada BOS atau CHOCH |
| Composite Score | >= 55 |
| Harga | Mendekati support atau resistance level |

### Aturan Pelaksanaan

- **BUY (LONG):** Harga mendekati support level atau lower Bollinger Band (RSI < 35).
- **SELL (SHORT):** Harga mendekati resistance level atau upper Bollinger Band (RSI > 65).
- **Konfirmasi:** Fair Value Gap (FVG) atau Liquidity Sweep pada level support/resistance menjadi konfirmasi tambahan.
- **Exit mean reversion:** Exit pada level midpoint range atau ketika harga mencapai opposite side.

### Parameter Indikator

| Indikator | Parameter | Fungsi |
|-----------|-----------|--------|
| Bollinger Bands | Period 20, Std 2 | Batas overbought/oversold range |
| RSI | Period 14 | Momentum ekstrem |
| Support/Resistance | Dynamic S/R | Level pembalikan harga |
| ATR | Period 14 | Jarak SL/TP |

---

## Aturan Breakout

Strategi breakout digunakan ketika market berada dalam regime **REVERSAL** (RSI > 70 atau RSI < 30) atau saat terjadi breakout dari struktur konsolidasi.

### Syarat Entry Breakout

| Komponen | Syarat |
|----------|--------|
| Market Regime | REVERSAL atau VOLATILE |
| RSI | > 70 (overbought) atau < 30 (oversold) |
| Composite Score | >= 70 |
| Volume | Meningkat signifikan saat breakout |
| Konfirmasi | FVG atau Liquidity Sweep terkonfirmasi |

### Aturan Pelaksanaan

- **BUY (LONG):** Breakout di atas resistance level dengan volume tinggi, dikonfirmasi oleh Fair Value Gap bullish.
- **SELL (SHORT):** Breakdown di bawah support level dengan volume tinggi, dikonfirmasi oleh Fair Value Gap bearish.
- **Breakout palsu:** Jika harga kembali ke dalam range dalam 3 candle, breakout dianggap gagal. Exit posisi.
- **Exit breakout:** Trail stop menggunakan ATR atau supertrend.

---

## Aturan Risk Management

### Batasan Risiko

| Parameter | Aturan | Keterangan |
|-----------|--------|------------|
| Risk per trade | 1% - 2% | Maksimum 2% dari balance |
| Maximum drawdown harian | 5% | Stop trading jika tercapai |
| Maximum drawdown mingguan | 10% | Stop trading, evaluasi strategi |
| Maximum drawdown bulanan | 15% | Review total dan restart dengan akun demo |
| Maximum open positions | 3 | Tidak boleh lebih dari 3 posisi simultan |
| Maximum risk per pair | 3% | Jumlah risk untuk pair yang sama |
| Correlation limit | 2 pasangan | Tidak boleh overlap pada pair dengan korelasi tinggi |

### Aturan Consecutive Losses

Berdasarkan implementasi `RiskManager.record_loss()` dan `evaluate_trade()`:

| Jumlah Loss Beruntun | Risk per Trade | Tindakan |
|----------------------|----------------|----------|
| 0 - 2 loss | 1.0% | Risk normal |
| 3 - 4 loss | 0.5% | Kurangi risk 50% |
| >= 5 loss | 0.25% | Stop trading, evaluasi strategi |

### Aturan Macro Override

Berdasarkan implementasi `FinalDecisionEngine._resolve_decision()`:

- Jika macro confidence >= 60% dan macro strength >= 50 serta technical confidence < 50, macro bias akan mengoverride sinyal teknikal.
- Jika macro bias bullish dengan confidence tinggi, hanya sinyal BUY atau WAIT yang diizinkan.
- Jika macro bias bearish dengan confidence tinggi, hanya sinyal SELL atau WAIT yang diizinkan.

---

## Aturan Position Sizing

### Aturan Dasar Position Sizing

1. Hitung lot size berdasarkan rumus:

   ```
   Lot Size = (Balance x Risk%) / (SL Pips x Pip Value per Lot)
   ```

2. Risk% default adalah 1% (dapat dikurangi menjadi 0.5% atau 0.25% tergantung consecutive losses).

3. Lot size minimum adalah 0.01 lot (micro lot).

4. Pembulatan lot size:
   - < 0.1 lot: dibulatkan ke 2 desimal (micro lots)
   - < 1.0 lot: dibulatkan ke 1 desimal (mini lots)
   - >= 1.0 lot: dibulatkan ke 0 desimal (standard lots)

Berdasarkan implementasi `PositionSizer.calculate()`:

```python
sl_pips = abs(entry_price - stop_loss) / pip_size
pip_value_per_lot = pip_size * contract_size
lot_size = risk_amount / (sl_pips * pip_value_per_lot)
```

### Aturan Kelly Criterion

Berdasarkan implementasi `KellyCriterion.recommended_risk()`:

| Level Kelly | Persentase Kelly Penuh | Deskripsi |
|-------------|----------------------|-----------|
| Full Kelly | 100% | Tidak digunakan (terlalu agresif) |
| Aggressive | 50% | Hanya untuk portofolio terdiversifikasi |
| Moderate | 25% | Default untuk akun standar |
| Conservative | 10% | Untuk akun kecil atau trader baru |
| Hard Cap | 2% | Batas absolut risk per trade |

Rumus Kelly:

```
K = W - ((1 - W) / R)
```

Dimana:
- K = Kelly fraction
- W = Win rate (probabilitas menang)
- R = Rasio rata-rata win / rata-rata loss

---

## Aturan Entry dan Exit

### Entry Rules

1. **Threshold Composite Score:**
   - HIGH (>= 75): Entry dengan keyakinan tinggi
   - MEDIUM (55 - 74): Entry dengan caution, pastikan konfirmasi tambahan
   - LOW (< 55): Tidak entry, pilih WAIT

2. **Final Decision WAIT** jika:
   - Composite score < 55
   - Terdeteksi konflik teknikal vs makro
   - Market regime tidak mendukung strategi yang dipilih
   - Setelah 5 consecutive losses

3. **Final Decision HEDGE** jika:
   - Terdeteksi konflik antara sinyal teknikal dan macro bias
   - Technical signal BUY tapi macro bias BEARISH
   - Technical signal SELL tapi macro bias BULLISH

### Exit Rules

1. **Stop Loss:** ATR-based (1.5x ATR) atau berdasarkan level support/resistance.
2. **Take Profit:** ATR-based (3x ATR) atau Risk/Reward ratio minimal 1:2.
3. **Trailing Stop:** Gunakan ATR trailing setelah harga bergerak 2x ATR menguntungkan.
4. **Time-based Exit:** Jika posisi tidak mencapai TP dalam 5 hari, evaluasi dan pertimbangkan exit manual.

---

## Aturan Multi-Timeframe Confirmation

| Timeframe | Peran | Indikator Utama |
|-----------|-------|-----------------|
| H1 | Entry timeframe | Signal utama, entry execution |
| H4 | Trend confirmation | Konfirmasi trend menengah |
| D1 | Macro context | Bias makro, trend utama |

### Aturan Alignment

- **Strong Alignment:** Semua timeframe (H1, H4, D1) menunjukkan arah yang sama.
- **Partial Alignment:** H1 dan H4 searah, D1 netral. Entry diperbolehkan dengan caution.
- **Conflict:** H1 dan D1 berlawanan arah. Jangan entry, atau gunakan HEDGE.

---

## Aturan Trading Harian

### Pre-Trading Checklist

1. Periksa macro bias (H4 dan D1).
2. Identifikasi market regime saat ini.
3. Cek composite score dan confidence breakdown.
4. Verifikasi multi-timeframe alignment.
5. Tentukan level support/resistance utama.
6. Hitung ATR untuk menentukan SL/TP.

### Post-Trading Checklist

1. Catat semua trade di journal.
2. Update win rate dan profit factor.
3. Evaluasi apakah aturan diikuti dengan disiplin.
4. Identifikasi area improvement.

### Aturan Stop Trading

1. Maximum drawdown harian 5% tercapai.
2. 5 consecutive losses dalam satu hari.
3. Technical issue pada platform atau data feed.
4. News event besar (NFP, FOMC, CPI) -- 30 menit sebelum dan sesudah.

---

*Dokumen ini adalah bagian dari platform Al-Syaka Quant AI. Setiap perubahan pada aturan trading harus melalui review dan approval tim development.*
