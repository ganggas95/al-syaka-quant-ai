# Backtest Review — Iteration 003

> Project: Unified Signal
>
> Reviewer: Lead AI Engineer
>
> Version: Iteration 003
>
> Status: Promising
>
> Priority: High

---

# Executive Summary

Iteration 003 menunjukkan peningkatan yang sangat signifikan dibanding dua iterasi sebelumnya.

Strategi mulai menunjukkan karakteristik yang mendekati **break-even system**, dengan peningkatan hampir di seluruh metrik utama.

Perubahan terbesar terjadi pada:

- Win Rate meningkat menjadi di atas 50%.
- Profit Factor meningkat mendekati 1.
- Expectancy hampir mencapai nilai positif.
- Drawdown tetap sangat rendah.
- Jumlah trade mulai cukup representatif.

Walaupun strategi masih mengalami kerugian kecil, arah optimasi sudah benar.

---

# Comparison History

| Metric        | Iteration 001 | Iteration 002 | Iteration 003 | Status              |
| ------------- | ------------- | ------------- | ------------- | ------------------- |
| Trades        | 578           | 14            | 80            | ✅ Better           |
| Win Rate      | 44.5%         | 42.9%         | **53.8%**     | ✅ Excellent        |
| Profit Factor | 0.69          | 0.30          | **0.96**      | ✅ Huge Improvement |
| Net Profit    | -6479         | -473          | **-105**      | ✅ Near Break Even  |
| Expectancy    | -11.21        | -33.79        | **-1.32**     | ✅ Almost Positive  |
| Max Drawdown  | 66.97%        | 5.12%         | **4.34%**     | ✅ Excellent        |
| Sharpe Ratio  | -0.86         | -0.38         | **-0.03**     | ✅ Near Neutral     |

---

# Overall Assessment

Current Grade

⭐⭐⭐⭐☆

(3.8 / 5)

---

# What Has Improved

## 1. Win Rate

Current

53.8%

Target

> 50%

Status

PASS

Win rate sudah berada pada level yang sehat.

Tidak disarankan mengejar win rate lebih tinggi apabila harus mengorbankan Risk Reward.

---

## 2. Profit Factor

Current

0.96

Target

> 1.20

Ideal

> 1.50

Status

Almost PASS

Ini adalah peningkatan terbesar selama proses pengembangan.

Profit Factor meningkat dari:

0.30

↓

0.96

Artinya sistem sudah sangat dekat menuju titik impas.

---

## 3. Expectancy

Current

-1.32

Previous

-33.79

Status

Excellent Improvement

Expectancy hampir mencapai nilai positif.

Ini menunjukkan kualitas trade mulai meningkat.

---

## 4. Drawdown

Current

4.34%

Target

<10%

Status

PASS

Risk management sudah berada pada level yang sangat baik.

Drawdown tidak lagi menjadi masalah utama.

---

## 5. Trade Frequency

Current

80 trades

Target

100+

Status

Almost PASS

Jumlah trade mulai cukup untuk dianalisis.

Namun masih perlu diperbanyak agar evaluasi statistik semakin valid.

---

# Current Bottleneck

Strategi sudah tidak memiliki masalah besar pada sisi Risk Management.

Masalah utama sekarang berada pada:

- Entry Quality
- Exit Quality
- Position Management

Bukan lagi pada jumlah indikator.

---

# Engineering Recommendation

## Priority 1 — Trade Attribution Analysis

AI harus menganalisis seluruh trade yang dilakukan.

Untuk setiap trade simpan metadata berikut.

```json
{
  "confidence": 84,
  "market_regime": "TREND",
  "session": "London",
  "volatility": "HIGH",
  "ADX": 32,
  "ATR": 21,
  "CompositeScore": 79,
  "MacroBias": "Bullish",
  "TechnicalSignal": "BUY",
  "Result": "LOSS"
}
```

Kemudian lakukan clustering.

Contoh:

Trade yang rugi memiliki karakteristik apa?

Trade yang untung memiliki karakteristik apa?

Output yang diharapkan:

- Top 10 penyebab loss
- Top 10 penyebab win

---

## Priority 2 — Exit Optimization

Saat ini entry kemungkinan sudah cukup baik.

Fokus optimasi berpindah ke exit strategy.

Eksperimen.

### ATR Trailing Stop

Backtest.

- 1 ATR
- 1.5 ATR
- 2 ATR

---

### Break Even

Aktifkan ketika profit mencapai:

- RR 0.5
- RR 1.0
- RR 1.2

---

### Partial Take Profit

Contoh.

50%

↓

TP 1

50%

↓

Trailing Stop

Bandingkan dengan TP penuh.

---

## Priority 3 — Dynamic Risk Reward

Jangan menggunakan RR tetap.

Gunakan berdasarkan Market Regime.

| Regime          | RR       |
| --------------- | -------- |
| Strong Trend    | 1 : 3    |
| Trend           | 1 : 2    |
| Sideways        | 1 : 1.5  |
| High Volatility | Adaptive |

---

## Priority 4 — Confidence Calibration

Kelompokkan trade.

60-70%

70-80%

80-90%

90-100%

Hitung untuk setiap kelompok.

- Win Rate
- Profit Factor
- Expectancy

Tujuan.

Menentukan confidence minimum yang benar-benar profitable.

---

## Priority 5 — Position Sizing

Gunakan Dynamic Position Sizing.

Contoh.

Confidence

↓

Risk

60%

↓

0.5%

75%

↓

1%

90%

↓

1.5%

95%

↓

2%

Position size mengikuti kualitas signal.

---

## Priority 6 — Composite Score Optimization

Saat ini Composite Score sudah baik.

Namun bobot setiap komponen perlu dievaluasi.

Contoh.

Current.

```
Market Structure 35%
Trend 20%
Momentum 15%
Volatility 10%
AI Prediction 20%
```

Gunakan Bayesian Optimization atau Optuna untuk mencari kombinasi bobot terbaik.

---

## Priority 7 — Trade Duration Analysis

Analisis.

Berapa lama trade menang?

Berapa lama trade kalah?

Output.

Average Holding Time.

Kemudian optimalkan timeout trade.

---

## Priority 8 — False Signal Detection

Buat AI mendeteksi pola.

Signal yang sering gagal.

Misalnya.

SELL

-

Strong Uptrend

-

ADX rendah

=

Ignore

---

## Priority 9 — Explainable AI Dashboard

Tambahkan dashboard.

Contoh.

```
Top Winning Factors

+ Strong BOS
+ High ADX
+ London Session

-----------------------

Top Losing Factors

- Sideways
- Low ATR
- Macro Conflict
```

Dashboard ini akan mempercepat proses optimasi.

---

## Priority 10 — Automatic Hyperparameter Optimization

Gunakan.

- Optuna
- Bayesian Optimization
- Genetic Algorithm

Parameter yang dioptimasi.

- ATR Multiplier
- EMA Length
- RSI Threshold
- Composite Weight
- Confidence Threshold
- Risk Reward

---

# New KPIs

Iteration 004

| Metric        | Current | Target   |
| ------------- | ------- | -------- |
| Win Rate      | 53.8%   | >54%     |
| Profit Factor | 0.96    | >1.20    |
| Net Profit    | -105    | Positive |
| Expectancy    | -1.32   | Positive |
| Sharpe Ratio  | -0.03   | >0.50    |
| Drawdown      | 4.34%   | <6%      |
| Trades        | 80      | >120     |

---

# Research Roadmap

Phase 1

✅ Market Structure

✅ Composite Score

✅ AI Confidence

Completed

---

Phase 2

✅ Dynamic Filtering

✅ Market Regime

Completed

---

Phase 3

Current Focus

- Exit Optimization
- Trade Attribution
- Position Sizing
- Confidence Calibration

---

Phase 4

Future

- Reinforcement Learning
- Portfolio Optimization
- Multi Symbol Optimization
- Walk Forward Validation
- Monte Carlo Simulation

---

# Final Recommendation

Jangan lagi menambahkan indikator teknikal baru.

Fokus pengembangan harus beralih pada:

1. Meningkatkan kualitas Exit Strategy.
2. Mengoptimalkan Position Sizing berdasarkan Confidence.
3. Mengidentifikasi penyebab utama trade yang gagal melalui Trade Attribution Analysis.
4. Menyesuaikan Risk/Reward secara dinamis berdasarkan kondisi pasar.
5. Menggunakan Explainable AI untuk memahami faktor yang paling berkontribusi terhadap kemenangan dan kerugian.

Dengan Profit Factor yang sudah mencapai **0.96**, strategi berada sangat dekat dengan titik impas. Perubahan kecil namun tepat sasaran pada manajemen posisi dan exit berpotensi mendorong Profit Factor melewati **1.20**, yang merupakan ambang awal sebuah strategi dengan **statistical edge**.
