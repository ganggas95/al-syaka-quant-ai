# PRD — AI Strategy Optimization Engine

> Version: 1.0
>
> Project: Unified Signal
>
> Module: AI Strategy Optimization Engine
>
> Owner: AI Research Team
>
> Status: Draft

---

# Overview

AI Strategy Optimization Engine merupakan modul penelitian (Research Engine) yang bertugas melakukan optimasi otomatis terhadap strategi trading Unified Signal menggunakan pendekatan Quantitative Research.

Modul ini **tidak bertugas mencari profit terbesar**, tetapi mencari strategi yang:

- Stabil
- Robust
- Explainable
- Memiliki Drawdown rendah
- Profit Factor tinggi
- Lolos Walk Forward Validation
- Lolos Monte Carlo Simulation

Engine harus bekerja layaknya seorang Quant Researcher yang melakukan ribuan eksperimen secara otomatis.

---

# Objectives

AI Agent harus mampu:

- Mengevaluasi kualitas strategi
- Menemukan penyebab strategi gagal
- Mengoptimasi parameter
- Mengoptimasi filter
- Mengoptimasi risk management
- Mengoptimasi market regime
- Mengoptimasi session trading
- Menghasilkan laporan penelitian otomatis

---

# Optimization Workflow

```

Historical Data

↓

Strategy

↓

Backtest

↓

Trade Attribution

↓

Optimization

↓

Validation

↓

Walk Forward

↓

Monte Carlo

↓

Research Report

```

---

# Optimization Phases

## Phase 1 — Backtest Validation

### Objective

Memastikan engine backtest tidak memiliki kesalahan logika.

### Validation Checklist

- [ ] No Look Ahead Bias
- [ ] No Data Leakage
- [ ] Entry menggunakan candle berikutnya
- [ ] SL dan TP realistis
- [ ] Spread diperhitungkan
- [ ] Slippage disimulasikan
- [ ] Commission dihitung
- [ ] Swap dihitung
- [ ] Tidak repaint
- [ ] Timezone konsisten

### Output

```

Backtest Validation Report

✓ PASS

atau

✗ FAILED

```

---

## Phase 2 — Trade Attribution Analysis

### Objective

Menjelaskan penyebab profit maupun loss.

### AI harus menghasilkan analisis seperti berikut.

| Category | Profit |
| -------- | ------ |
| Trending | +3200  |
| Sideways | -7100  |
| London   | +1500  |
| New York | +900   |
| Asia     | -4300  |
| CPI Day  | -1200  |
| High ATR | +1700  |
| Low ATR  | -3900  |

### Goal

Mengidentifikasi kondisi market yang paling menguntungkan.

---

## Phase 3 — Signal Quality Optimization

### Objective

Meningkatkan kualitas signal.

AI harus mencoba berbagai threshold.

Contoh

```

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

```

### Metrics

- Profit Factor
- Win Rate
- Drawdown
- Expectancy
- Sharpe Ratio

---

## Phase 4 — Feature Importance

### Objective

Mengetahui kontribusi setiap feature.

### AI harus menghitung

- SHAP
- Feature Importance
- Mutual Information
- Correlation

Contoh

| Feature          | Importance |
| ---------------- | ---------- |
| Market Structure | 26%        |
| Liquidity Sweep  | 18%        |
| ATR              | 16%        |
| EMA20            | 14%        |
| ADX              | 11%        |
| RSI              | 7%         |
| Volume           | 5%         |
| MACD             | 3%         |

### Output

Feature Ranking

---

## Phase 5 — Strategy Combination Optimization

### Objective

Menguji berbagai kombinasi strategi.

Contoh

```

EMA + ATR

↓

Backtest

EMA + BOS

↓

Backtest

EMA + BOS + ATR

↓

Backtest

EMA + BOS + ATR + Liquidity Sweep

↓

Backtest

```

AI memilih kombinasi terbaik.

---

## Phase 6 — Parameter Optimization

### Objective

Mencari parameter optimal.

Parameter yang harus dioptimasi

### EMA

```

5
10
20
30
50
100
200

```

### ATR Multiplier

```

1.0
1.2
1.5
2.0
2.5

```

### ADX

```

15
20
25
30
35

```

### RSI

```

25
30
35
40

60
65
70
75

```

### Risk Reward

```

1:1

1:1.5

1:2

1:2.5

1:3

```

Output

Parameter terbaik.

---

## Phase 7 — Market Regime Optimization

AI harus mampu mengklasifikasikan market.

### Trending

Menggunakan

Trend Following

---

### Sideways

Menggunakan

Mean Reversion

---

### High Volatility

Menggunakan

ATR Breakout

---

### News Driven

WAIT

---

### Output

Market Regime Classifier

---

## Phase 8 — Trading Session Optimization

AI harus mencoba

London Only

↓

Backtest

New York Only

↓

Backtest

Asia Only

↓

Backtest

London + New York

↓

Backtest

### Output

Session Ranking

---

## Phase 9 — Risk Management Optimization

AI mengoptimasi

- Position Size
- ATR Stop Loss
- Dynamic Take Profit
- Break Even
- Trailing Stop
- Partial Close

Output

Risk Engine Recommendation

---

## Phase 10 — Walk Forward Analysis

### Objective

Menguji robustness.

```

Train

↓

Test

↓

Shift Window

↓

Train

↓

Test

↓

Repeat

```

### Metrics

- Profit Factor
- Drawdown
- Stability
- Consistency

---

## Phase 11 — Monte Carlo Simulation

Minimal

10000 simulasi.

Output

- Probability of Ruin
- Expected Drawdown
- Worst Case
- Median Return
- Confidence Interval

---

# Optimization Metrics

## Primary Metrics

- Profit Factor
- Expectancy
- Max Drawdown
- Sharpe Ratio
- Sortino Ratio
- Calmar Ratio
- Recovery Factor
- CAGR

---

## Secondary Metrics

- Win Rate
- Average Win
- Average Loss
- Consecutive Win
- Consecutive Loss
- Average Holding Time
- Exposure Time

---

# AI Agents

## Research Agent

Bertugas menghasilkan hipotesis penelitian.

Contoh

- Bagaimana jika ADX dinaikkan?
- Bagaimana jika ATR diperbesar?
- Bagaimana jika Composite Score > 80?

---

## Optimizer Agent

Mencoba ribuan kombinasi parameter.

---

## Evaluator Agent

Menilai kualitas strategi.

Menggunakan

- Profit Factor
- Sharpe
- Drawdown
- Stability

---

## Explainability Agent

Menjelaskan

Mengapa strategi menang.

Mengapa strategi kalah.

---

## Risk Agent

Mengoptimasi

- SL
- TP
- Position Size
- Risk per Trade

---

## Macro Agent

Menghubungkan performa strategi dengan

- CPI
- NFP
- FOMC
- Oil
- DXY
- Bond Yield
- VIX
- Geopolitical Risk

---

# Research Dashboard

Dashboard harus menampilkan

- Strategy Score
- Optimization History
- Parameter Comparison
- Equity Curve
- Drawdown Curve
- Walk Forward Result
- Monte Carlo Result
- Feature Importance
- Trade Attribution
- Session Performance
- Market Regime Performance

---

# Success Criteria

Strategi dinyatakan layak apabila memenuhi

| Metric          | Minimum Target | Ideal Target |
| --------------- | -------------- | ------------ |
| Profit Factor   | > 1.30         | > 1.70       |
| Win Rate        | > 45%          | > 55%        |
| Expectancy      | Positif        | > 0.20R      |
| Max Drawdown    | < 20%          | < 10%        |
| Sharpe Ratio    | > 1.00         | > 1.50       |
| Sortino Ratio   | > 1.50         | > 2.00       |
| Recovery Factor | > 2.00         | > 3.00       |

---

# Stop Optimization Criteria

AI Agent harus menghentikan proses optimasi apabila:

- Terjadi indikasi overfitting
- Walk Forward gagal
- Monte Carlo gagal
- Profit Factor menurun
- Drawdown meningkat
- Stabilitas menurun

AI tidak diperbolehkan memilih strategi hanya berdasarkan Net Profit.

---

# Engineering Principles

Seluruh proses optimasi harus mengikuti prinsip berikut.

1. Explainable sebelum kompleks.
2. Data-driven, bukan asumsi.
3. Stabilitas lebih penting daripada profit maksimum.
4. Profit Factor lebih penting daripada Win Rate.
5. Drawdown rendah lebih penting daripada jumlah transaksi.
6. Semua perubahan harus divalidasi melalui Backtest, Walk Forward, dan Monte Carlo.
7. Setiap hasil optimasi wajib menghasilkan laporan penelitian yang dapat direproduksi.

---

# Vision

AI Strategy Optimization Engine bukan sekadar melakukan optimasi parameter.

Engine ini dirancang sebagai **Quantitative Research Assistant** yang secara otomatis melakukan penelitian, mengevaluasi ribuan eksperimen, menjelaskan penyebab keberhasilan maupun kegagalan strategi, serta merekomendasikan konfigurasi trading yang paling stabil dan dapat diandalkan untuk kondisi pasar nyata.

Target akhir modul ini adalah membangun sistem trading yang **robust, explainable, adaptif terhadap perubahan market regime, dan memiliki probabilitas keberhasilan jangka panjang yang tinggi**, bukan sekadar menghasilkan performa terbaik pada data historis.
