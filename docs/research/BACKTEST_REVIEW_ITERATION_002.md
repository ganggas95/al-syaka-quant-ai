# Backtest Review — Iteration 002

> Project: Unified Signal
>
> Reviewer: Lead AI Engineer
>
> Status: Needs Improvement
>
> Priority: High

---

# Executive Summary

Backtest Iteration 002 menunjukkan peningkatan yang signifikan pada aspek **Risk Management**, khususnya penurunan Max Drawdown. Namun, strategi masih belum memiliki **statistical edge** karena Profit Factor dan Expectancy masih berada pada nilai negatif.

Kesimpulan utama:

> Strategi menjadi lebih selektif, tetapi kualitas signal belum meningkat.

---

# Metrics Comparison

| Metric        | Previous | Current | Status                   |
| ------------- | -------- | ------- | ------------------------ |
| Total Trades  | 578      | 14      | ✅ Better                |
| Win Rate      | 44.5%    | 42.9%   | ➖ Stable                |
| Profit Factor | 0.69     | 0.30    | ❌ Worse                 |
| Net Profit    | -6479    | -473    | 🟡 Smaller Loss          |
| Max Drawdown  | 66.97%   | 5.12%   | ✅ Excellent Improvement |
| Expectancy    | -11.21   | -33.79  | ❌ Worse                 |
| Sharpe Ratio  | -0.86    | -0.38   | 🟡 Slight Improvement    |

---

# Positive Findings

## 1. Risk Management Improved

Max Drawdown turun dari hampir 67% menjadi sekitar 5%.

Ini menunjukkan bahwa filter baru berhasil mengurangi risiko secara signifikan.

Status:

PASS

---

## 2. Signal Filtering Improved

Jumlah trade turun drastis.

578 trades

↓

14 trades

Hal ini menunjukkan bahwa sistem tidak lagi membuka posisi secara agresif.

Status:

PASS

---

## 3. Equity Preservation

Kerugian absolut jauh lebih kecil dibanding iterasi sebelumnya.

Hal ini menunjukkan adanya peningkatan pada kontrol risiko.

Status:

PASS

---

# Critical Problems

## 1. Profit Factor

Current

0.30

Target

> 1.30

Ideal

> 1.70

Status

FAILED

Profit Factor merupakan indikator paling penting dalam evaluasi strategi.

Nilai di bawah 1 menunjukkan bahwa strategi secara statistik masih merugi.

---

## 2. Expectancy

Current

-33.79

Target

Positive

Status

FAILED

Setiap transaksi masih memberikan nilai ekspektasi negatif.

Semakin lama strategi dijalankan, semakin besar kemungkinan mengalami kerugian.

---

## 3. Sample Size

Total Trades

14

Status

Insufficient

Jumlah trade terlalu sedikit untuk menarik kesimpulan statistik.

Minimal:

100 Trade

Ideal:

300+ Trade

---

# Root Cause Hypothesis

Kemungkinan penyebab strategi masih gagal.

## Hypothesis 1

Filter terlalu ketat.

Akibatnya:

- Trade berkualitas ikut terfilter.
- Sample menjadi terlalu sedikit.

---

## Hypothesis 2

Entry masih terlambat.

Kemungkinan AI baru masuk setelah momentum mulai habis.

---

## Hypothesis 3

Risk Reward belum optimal.

Perlu dilakukan optimasi.

Contoh:

1:1.5

1:2

1:2.5

1:3

---

## Hypothesis 4

Market Regime belum digunakan.

Strategi mungkin tetap trading pada kondisi sideways.

---

## Hypothesis 5

Confidence Threshold terlalu tinggi.

Trade berkualitas kemungkinan tidak lolos filter.

---

# Recommendations

## Priority 1

Trade Attribution Analysis

AI harus menjawab:

Mengapa trade rugi?

Mengapa trade menang?

Kelompokkan berdasarkan:

- Session
- Market Regime
- ATR
- Trend
- Composite Score
- Confidence
- News

---

## Priority 2

Confidence Threshold Optimization

Lakukan eksperimen.

Confidence > 60

↓

Backtest

Confidence > 70

↓

Backtest

Confidence > 80

↓

Backtest

Confidence > 90

↓

Backtest

Bandingkan:

- Profit Factor
- Drawdown
- Expectancy

---

## Priority 3

Market Regime Filter

Pisahkan strategi.

Trending

↓

Trend Following

Sideways

↓

Mean Reversion

High Volatility

↓

Breakout

News

↓

WAIT

---

## Priority 4

Risk Reward Optimization

Backtest seluruh kombinasi.

- 1:1
- 1:1.5
- 1:2
- 1:2.5
- 1:3

---

## Priority 5

ATR Stop Loss Optimization

Gunakan ATR multiplier.

1.0 ATR

1.2 ATR

1.5 ATR

2.0 ATR

2.5 ATR

Pilih yang menghasilkan Profit Factor terbaik.

---

## Priority 6

Trading Session Optimization

Bandingkan performa.

London

New York

Asia

London + New York

---

## Priority 7

Feature Importance Analysis

Hitung kontribusi.

- SHAP
- Feature Importance
- Mutual Information

Hapus feature yang tidak memberikan kontribusi signifikan.

---

## Priority 8

Walk Forward Validation

Setelah strategi membaik.

Lakukan.

Train

↓

Test

↓

Shift Window

↓

Repeat

---

## Priority 9

Monte Carlo Simulation

Minimal

10000 Simulation

Output.

- Probability of Ruin
- Expected Drawdown
- Worst Case
- Median Return

---

# AI Agent Tasks

## Research Agent

Membuat hipotesis baru.

---

## Optimizer Agent

Menguji ribuan parameter.

---

## Evaluator Agent

Menilai strategi.

Menggunakan.

- Profit Factor
- Drawdown
- Expectancy
- Sharpe
- Recovery

---

## Explainability Agent

Menjelaskan penyebab.

Trade Menang.

Trade Kalah.

---

## Risk Agent

Mengoptimasi.

- SL
- TP
- Position Size
- ATR

---

## Macro Agent

Menghubungkan performa dengan.

- CPI
- NFP
- FOMC
- Oil
- DXY
- Bond Yield
- VIX

---

# Success Criteria

Iterasi berikutnya harus memenuhi.

| Metric        | Current | Target   |
| ------------- | ------- | -------- |
| Total Trades  | 14      | 100-300  |
| Profit Factor | 0.30    | >1.30    |
| Win Rate      | 42.9%   | >45%     |
| Expectancy    | -33.79  | Positive |
| Max Drawdown  | 5.12%   | <10%     |
| Sharpe Ratio  | -0.38   | >1.00    |

---

# Engineering Notes

AI Agent tidak diperbolehkan mengoptimasi strategi hanya berdasarkan Net Profit.

Prioritas evaluasi harus mengikuti urutan berikut.

1. Profit Factor
2. Drawdown
3. Expectancy
4. Sharpe Ratio
5. Recovery Factor
6. Win Rate
7. Net Profit

Strategi yang memiliki Profit Factor tinggi dan Drawdown rendah lebih layak digunakan dibanding strategi dengan Net Profit tinggi tetapi tidak stabil.

---

# Final Assessment

## Current Grade

⭐⭐☆☆☆

(2/5)

---

## Current Status

⚠ Research Continues

Strategi menunjukkan peningkatan yang signifikan pada aspek Risk Management, namun belum memiliki statistical edge yang memadai untuk digunakan pada trading live.

Fokus iterasi berikutnya bukan menambah indikator baru, melainkan meningkatkan kualitas signal melalui optimasi Market Regime, Trade Attribution Analysis, Risk Management, dan Parameter Optimization.

Target utama Iteration 003 adalah menghasilkan strategi dengan:

- Profit Factor > 1.30
- Drawdown < 10%
- Expectancy positif
- Minimum 100 trade valid
- Lolos Walk Forward Validation
- Lolos Monte Carlo Simulation
