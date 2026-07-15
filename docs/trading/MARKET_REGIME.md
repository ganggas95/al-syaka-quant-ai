# Market Regime Detection — Al-Syaka Quant AI

> Dokumen ini menjelaskan sistem deteksi market regime yang digunakan oleh platform Al-Syaka Quant AI. Regime detection adalah komponen kritis yang menentukan strategi trading yang akan digunakan.

---

## Daftar Isi

- [Empat Market Regime](#empat-market-regime)
- [Deteksi Menggunakan ADX](#deteksi-menggunakan-adx)
- [Deteksi Menggunakan RSI](#deteksi-menggunakan-rsi)
- [Deteksi Menggunakan Market Structure](#deteksi-menggunakan-market-structure)
- [Strategi per Regime](#strategi-per-regime)
- [Regime Transition Detection](#regime-transition-detection)
- [Multi-Timeframe Regime Analysis](#multi-timeframe-regime-analysis)
- [Parameter dan Threshold](#parameter-dan-threshold)
- [Fallback Mechanism](#fallback-mechanism)

---

## Empat Market Regime

Platform Al-Syaka Quant AI mendeteksi empat jenis market regime. Masing-masing regime memiliki karakteristik, indikator, dan strategi yang berbeda.

### 1. TRENDING

Pasar sedang bergerak dalam satu arah yang jelas dengan struktur impulse dan retracement yang teratur.

| Karakteristik               | Nilai                   |
| --------------------------- | ----------------------- |
| ADX                         | >= 25                   |
| RSI                         | 40 - 60 (tidak ekstrem) |
| Break of Structure (BOS)    | Terkonfirmasi           |
| Change of Character (CHOCH) | Tidak ada               |
| Strategi                    | trend_following         |

**Ciri-ciri tambahan:**

- Harga berada di atas (bullish) atau di bawah (bearish) EMA 20 dan EMA 50.
- Higher highs dan higher lows untuk uptrend.
- Lower highs dan lower lows untuk downtrend.
- Momentum konsisten dengan arah trend.

### 2. RANGE (Sideways)

Pasar bergerak sideways dalam kisaran harga tertentu tanpa arah yang jelas.

| Karakteristik               | Nilai          |
| --------------------------- | -------------- |
| ADX                         | <= 15          |
| RSI                         | 40 - 60        |
| Break of Structure (BOS)    | Tidak ada      |
| Change of Character (CHOCH) | Tidak ada      |
| Strategi                    | mean_reversion |

**Ciri-ciri tambahan:**
| Harga berosilasi di antara level support dan resistance yang jelas.
| Volume cenderung menurun.
| Bollinger Bands menyempit (squeeze).
| EMA 20 dan EMA 50 saling berpotongan atau bergerak mendatar.

### 3. REVERSAL

Pasar berada dalam kondisi jenuh (overbought/oversold) dan berpotensi berbalik arah.

| Karakteristik               | Nilai                                  |
| --------------------------- | -------------------------------------- |
| ADX                         | Bervariasi (sering tinggi)             |
| RSI                         | > 70 (overbought) atau < 30 (oversold) |
| Break of Structure (BOS)    | Mungkin ada exhaustion                 |
| Change of Character (CHOCH) | Sering terjadi                         |
| Strategi                    | breakout (counter-trend)               |

**Ciri-ciri tambahan:**
| Momentum ekstrem dengan RSI di zona overbought/oversold.
| Divergence antara harga dan RSI.
| Volume meningkat di akhir pergerakan (climax).
| Fair Value Gap (FVG) sering terisi.

### 4. VOLATILE

Pasar aktif tetapi tidak memiliki arah yang jelas. Volatilitas tinggi dengan pergerakan harga yang tidak menentu.

| Karakteristik               | Nilai                            |
| --------------------------- | -------------------------------- |
| ADX                         | 15 - 25                          |
| RSI                         | Bervariasi                       |
| Break of Structure (BOS)    | Mungkin ada tapi tidak konsisten |
| Change of Character (CHOCH) | Mungkin ada                      |
| Strategi                    | adaptive                         |

**Ciri-ciri tambahan:**
| Harga bergerak dengan range lebar tetapi tanpa struktur yang jelas.
| Sering terjadi false breakout.
| Spread melebar.
| Cocok untuk intraday trading dengan manajemen risiko ketat.

---

## Deteksi Menggunakan ADX

### ADX untuk Mengukur Kekuatan Trend

Average Directional Index (ADX) adalah indikator utama untuk mengukur kekuatan trend, tanpa memperdulikan arah.

Berdasarkan implementasi `UnifiedSignalGenerator._detect_market_regime()`:

### Threshold ADX

| ADX Value | Interpretasi         | Regime                     |
| --------- | -------------------- | -------------------------- |
| 0 - 15    | Very Weak / No Trend | RANGE                      |
| 15 - 25   | Weak to Moderate     | VOLATILE                   |
| 25 - 35   | Strong Trend         | TRENDING                   |
| 35 - 50   | Very Strong Trend    | TRENDING                   |
| 50+       | Extremely Strong     | TRENDING (jelang reversal) |

### ADX untuk Regime Detection

```python
def classify_by_adx(adx_value: float, has_bos: bool) -> str:
    """Klasifikasi regime berdasarkan ADX."""
    if adx_value >= 25 and has_bos:
        return "TRENDING"
    elif adx_value <= 15 and not has_bos:
        return "RANGE"
    else:
        return "VOLATILE"
```

### Directional Indicators (DI+/DI-)

Selain ADX, platform juga menggunakan DI+ dan DI- untuk menentukan arah trend:

| Kondisi                | Arah                      |
| ---------------------- | ------------------------- |
| DI+ > DI- dan ADX > 25 | Bullish trend             |
| DI- > DI+ dan ADX > 25 | Bearish trend             |
| DI+ dan DI- berdekatan | Trend lemah atau sideways |

---

## Deteksi Menggunakan RSI

### RSI untuk Identifikasi Momentum Ekstrem

Relative Strength Index (RSI) digunakan untuk mendeteksi kondisi overbought/oversold yang mengindikasikan potensi reversal.

### Threshold RSI

| RSI Value | Interpretasi     | Implikasi Regime           |
| --------- | ---------------- | -------------------------- |
| > 70      | Overbought       | Potensi REVERSAL (bearish) |
| 60 - 70   | Bullish momentum | TRENDING bullish           |
| 40 - 60   | Netral           | RANGE atau VOLATILE        |
| 30 - 40   | Bearish momentum | TRENDING bearish           |
| < 30      | Oversold         | Potensi REVERSAL (bullish) |

### RSI dalam Regime Detection

```python
def check_reversal_by_rsi(rsi_value: float) -> bool:
    """Cek apakah RSI mengindikasikan reversal."""
    return rsi_value > 70 or rsi_value < 30
```

Jika RSI > 70 atau < 30, regime diklasifikasikan sebagai REVERSAL (terlepas dari ADX).

### RSI Divergence

RSI Divergence digunakan sebagai konfirmasi tambahan untuk deteksi reversal:

| Jenis Divergence   | Harga       | RSI         | Implikasi                      |
| ------------------ | ----------- | ----------- | ------------------------------ |
| Bullish Divergence | Lower low   | Higher low  | Potensi reversal bullish       |
| Bearish Divergence | Higher high | Lower high  | Potensi reversal bearish       |
| Hidden Bullish     | Higher low  | Lower low   | Konfirmasi uptrend berlanjut   |
| Hidden Bearish     | Lower high  | Higher high | Konfirmasi downtrend berlanjut |

---

## Deteksi Menggunakan Market Structure

### Market Structure Analysis

Market structure detection menggunakan swing highs, swing lows, Break of Structure (BOS), dan Change of Character (CHOCH).

Berdasarkan implementasi `MarketStructureDetector`:

### Break of Structure (BOS)

BOS terjadi ketika harga menembus swing high (untuk uptrend) atau swing low (untuk downtrend) sebelumnya.

```
Uptrend: Harga membuat higher high baru > previous swing high = BOS bullish
Downtrend: Harga membuat lower low baru < previous swing low = BOS bearish
```

**Peran dalam Regime Detection:**

- Adanya BOS + ADX >= 25 = TRENDING
- Tidak ada BOS + ADX <= 15 = RANGE

### Change of Character (CHOCH)

CHOCH terjadi ketika struktur trend berubah, menandakan potensi reversal.

```
Uptrend berakhir: Harga跌破 previous swing low = CHOCH bearish
Downtrend berakhir: Harga突破 previous swing high = CHOCH bullish
```

**Peran dalam Regime Detection:**

- CHOCH dalam trend kuat bisa menandakan transisi ke REVERSAL.
- CHOCH di range bisa berarti ekspansi menuju VOLATILE atau TRENDING baru.

### Fair Value Gap (FVG)

FVG adalah celah harga yang terjadi karena ketidakseimbangan order flow. FVG sering terisi (di-retest) sebelum harga melanjutkan pergerakan.

**Peran dalam Regime Detection:**

- Banyak FVG dalam waktu singkat = VOLATILE.
- FVG yang terisi = potensi reversal atau retest.

### Liquidity Sweep

Liquidity sweep terjadi ketika harga menyapu level likuiditas (swing high/low) sebelum berbalik.

**Peran dalam Regime Detection:**

- Liquidity sweep + reversal = konfirmasi REVERSAL.
- Liquidity sweep + lanjut = konfirmasi TRENDING kuat.

---

## Strategi per Regime

### TRENDING -> Trend Following

| Parameter    | Setting                                        |
| ------------ | ---------------------------------------------- |
| Strategi     | trend_following                                |
| Entry        | Searah trend saat retracement (pullback)       |
| SL           | 1.5x ATR di bawah/atas swing low/high terdekat |
| TP           | 3.0x ATR atau trailing stop                    |
| Risk         | 1.0% (full)                                    |
| Indikator    | EMA 12/20/50, ADX, BOS                         |
| Entry Timing | Saat pullback ke EMA 20 atau EMA 50            |
| Exit Timing  | CHOCH atau BOS berlawanan arah                 |

**Contoh Eksekusi:**

```
Uptrend TRENDING (ADX 32, BOS bullish):
- Entry BUY saat retracement ke EMA 20
- SL di bawah swing low terakhir
- TP 3x ATR, trailing setelah TP1

Downtrend TRENDING (ADX 28, BOS bearish):
- Entry SELL saat retracement ke EMA 20
- SL di atas swing high terakhir
- TP 3x ATR, trailing setelah TP1
```

### RANGE -> Mean Reversion

| Parameter    | Setting                                       |
| ------------ | --------------------------------------------- |
| Strategi     | mean_reversion                                |
| Entry        | Di dekat support (BUY) atau resistance (SELL) |
| SL           | 1.0x ATR di luar support/resistance           |
| TP           | 2.0x ATR atau midpoint range                  |
| Risk         | 0.5% (reduced)                                |
| Indikator    | RSI, Bollinger Bands, Support/Resistance      |
| Entry Timing | RSI < 35 (BUY) atau RSI > 65 (SELL)           |
| Exit Timing  | Mendekati opposite side range                 |

**Contoh Eksekusi:**

```
Range market (ADX 12, S/R jelas):
- BUY di support dengan RSI 32, SL 1x ATR di bawah support
- SELL di resistance dengan RSI 68, SL 1x ATR di atas resistance
- TP di midpoint range (RR 1:1.5 minimal)
```

### REVERSAL -> Breakout (Counter-Trend)

| Parameter    | Setting                                             |
| ------------ | --------------------------------------------------- |
| Strategi     | breakout                                            |
| Entry        | Setelah konfirmasi reversal (CHOCH atau FVG filled) |
| SL           | 1.0x ATR                                            |
| TP           | 3.5x ATR (lebih besar karena risk lebih tinggi)     |
| Risk         | 0.5% (reduced)                                      |
| Indikator    | RSI divergence, FVG, Liquidity Sweep                |
| Entry Timing | Setelah candle konfirmasi reversal                  |
| Exit Timing  | Resistance/support berikutnya                       |

**Contoh Eksekusi:**

```
Bullish reversal (RSI 28, bullish divergence, liquidity sweep):
- Entry BUY setelah candle bullish konfirmasi
- SL 1x ATR di bawah swing low
- TP 3.5x ATR

Bearish reversal (RSI 75, bearish divergence, FVG filled):
- Entry SELL setelah candle bearish konfirmasi
- SL 1x ATR di atas swing high
- TP 3.5x ATR
```

### VOLATILE -> Adaptive

| Parameter    | Setting                                             |
| ------------ | --------------------------------------------------- |
| Strategi     | adaptive                                            |
| Entry        | Hanya dengan konfirmasi kuat (HIGH composite score) |
| SL           | 2.0x ATR (lebih lebar)                              |
| TP           | 3.0x ATR                                            |
| Risk         | 0.75% (reduced)                                     |
| Indikator    | Semua indikator dengan weighting adaptif            |
| Entry Timing | Saat volatility contraction                         |
| Exit Timing  | Ketat, gunakan time-based exit                      |

**Contoh Eksekusi:**

```
Volatile market (ADX 20, false breakout):
- Tunggu volatility contraction (Bollinger squeeze)
- Entry hanya jika composite score HIGH (> 75)
- Gunakan SL 2x ATR untuk menghindari false breakout
- Ambil profit cepat, TP 2.5x ATR
```

---

## Regime Transition Detection

### Transisi Antar Regime

Platform mendeteksi transisi regime secara real-time untuk mengantisipasi perubahan strategi.

| Dari     | Ke       | Indikator                           |
| -------- | -------- | ----------------------------------- |
| RANGE    | TRENDING | ADX naik di atas 25 + BOS           |
| RANGE    | VOLATILE | ADX naik 15-25 + false breakout     |
| TRENDING | REVERSAL | RSI ekstrem + CHOCH + divergence    |
| TRENDING | RANGE    | ADX turun di bawah 20 + BOS melemah |
| REVERSAL | TRENDING | BOS baru setelah reversal           |
| VOLATILE | TRENDING | ADX > 25 + BOS konsisten            |
| VOLATILE | RANGE    | ADX < 15 + harga kembali ke range   |

### Early Warning Signals

| Signal                | Potensi Transisi     | Lead Time                |
| --------------------- | -------------------- | ------------------------ |
| RSI approaching 70/30 | TRENDING -> REVERSAL | 3-5 candle               |
| ADX turun dari > 30   | TRENDING -> RANGE    | 5-10 candle              |
| BOS gagal             | TRENDING -> RANGE    | 1-2 candle setelah gagal |
| CHOCH muncul          | TRENDING -> REVERSAL | 1-2 candle               |
| Bollinger squeeze     | VOLATILE -> RANGE    | 3-5 candle               |
| Volatility expansion  | RANGE -> VOLATILE    | 1-2 candle               |

### Konfirmasi Transisi

Setiap transisi regime harus dikonfirmasi dengan setidaknya 2 dari 3 indikator berikut:

1. **Price Action:** Candle close yang valid (bukan false breakout).
2. **Indikator:** ADX, RSI, dan struktur harga mendukung transisi.
3. **Volume:** Volume meningkat untuk konfirmasi transisi.

---

## Multi-Timeframe Regime Analysis

### Peran Timeframe dalam Regime

| Timeframe | Fungsi                                 | Prioritas             |
| --------- | -------------------------------------- | --------------------- |
| H1        | Entry timeframe: regime untuk eksekusi | Tertinggi untuk entry |
| H4        | Konfirmasi: regime menengah            | Konfirmasi strategi   |
| D1        | Konteks: regime makro                  | Bias strategi         |

### Skenario Alignment

| H1 Regime | H4 Regime | D1 Regime | Tindakan                        |
| --------- | --------- | --------- | ------------------------------- |
| TRENDING  | TRENDING  | BULLISH   | BUY dengan full confidence      |
| RANGE     | RANGE     | NEUTRAL   | Mean reversion, risk reduced    |
| REVERSAL  | TRENDING  | BULLISH   | Hati-hati, tunggu konfirmasi H4 |
| VOLATILE  | VOLATILE  | VOLATILE  | WAIT, tidak ada konfirmasi      |

---

## Parameter dan Threshold

### Ringkasan Threshold Deteksi

| Parameter | TRENDING  | RANGE     | REVERSAL           | VOLATILE        |
| --------- | --------- | --------- | ------------------ | --------------- |
| ADX       | >= 25     | <= 15     | Bervariasi         | 15 - 25         |
| RSI       | 40 - 60   | 40 - 60   | > 70 atau < 30     | Bervariasi      |
| BOS       | Ada       | Tidak ada | Mungkin exhaustion | Tidak konsisten |
| CHOCH     | Tidak ada | Tidak ada | Sering terjadi     | Mungkin ada     |
| FVG       | Jarang    | Jarang    | Sering terisi      | Banyak          |

### Default Fallback

Jika deteksi regime gagal karena data tidak memadai:

```python
# Fallback dari UnifiedSignalGenerator._detect_market_regime()
return {
    "market_regime": "VOLATILE",
    "strategy_mode": "adaptive",
    "regime_reason": "Fallback regime detection — data insufficient",
}
```

---

_Dokumen ini adalah bagian dari platform Al-Syaka Quant AI. Parameter deteksi regime dapat disesuaikan berdasarkan hasil backtesting dan karakteristik instrumen._
