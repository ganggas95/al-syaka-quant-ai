# Unified Signal - Backtesting Engine PRD

Version: 1.0
Status: Draft
Project: Unified Signal
Module: Backtesting Engine

---

# Overview

Backtesting Engine adalah modul yang digunakan untuk mengevaluasi performa seluruh strategi Unified Signal menggunakan data historis.

Tujuan utama modul ini bukan hanya menghitung profit, tetapi memvalidasi apakah seluruh kombinasi:

- AI Prediction
- Market Structure
- Technical Indicators
- Quant Strategy

benar-benar menghasilkan edge di market.

Backtesting merupakan fondasi utama sebelum suatu strategi digunakan pada Live Trading.

---

# Objectives

Backtesting harus mampu menjawab pertanyaan berikut:

1. Berapa winrate strategi?
2. Berapa Profit Factor?
3. Berapa Max Drawdown?
4. Berapa Expectancy?
5. Berapa Sharpe Ratio?
6. Berapa Recovery Factor?
7. Berapa Average RR?
8. Apakah AI Prediction benar-benar meningkatkan performa?

---

# Workflow

Historical Data

↓

Feature Engineering

↓

AI Prediction

↓

Signal Generation

↓

Trade Simulation

↓

Performance Evaluation

↓

Backtest Report

---

# Historical Data

Input:

- OHLCV
- Time
- Volume

Supported Timeframe

- M1
- M5
- M15
- H1
- H4
- D1

Supported Symbol

- XAUUSD
- EURUSD
- GBPUSD
- BTCUSD
- dll

---

# Feature Engineering

Generate seluruh feature yang digunakan Unified Signal.

Contoh:

- EMA 12
- EMA 20
- EMA 50
- SMA 200
- RSI
- ATR
- MACD
- ADX
- Market Structure
- Swing High
- Swing Low
- BOS
- CHoCH
- Liquidity Sweep
- Fair Value Gap
- Volume
- ATR StdDev
- Volatility Regime

Semua feature harus identik dengan feature yang digunakan pada Live Signal.

---

# AI Prediction

AI Model menerima seluruh feature.

Output:

BUY

SELL

HOLD

Beserta:

Confidence Score

Probability

SHAP Explanation

---

# Signal Generation

Signal dibangun dari kombinasi:

AI Prediction

-

Quant Strategy

-

Market Structure

-

Risk Filter

Output:

BUY

SELL

WAIT

---

# Trade Simulation

Simulator wajib berjalan candle demi candle.

Pseudo:

For each candle:

Generate Signal

Jika BUY

Open Position

Hitung:

SL

TP

Trailing Stop

Break Even

Jika SELL

Open Position

Hitung:

SL

TP

Trailing Stop

Break Even

Close posisi ketika:

TP

SL

Manual Exit

Reverse Signal

Time Exit

---

# Money Management

Support:

Fixed Lot

Risk %

Dynamic Lot

ATR Position Sizing

Contoh:

Risk 1%

Account

10000 USD

Stop Loss

20 point

Lot otomatis dihitung.

---

# Trading Rules

Support:

One Position

Multiple Position

No Hedging

Hedging

Maximum Daily Trade

Maximum Drawdown Stop

Maximum Consecutive Loss

Session Filter

News Filter

---

# Performance Metrics

Wajib dihitung.

## Trade Statistics

Total Trade

Winning Trade

Losing Trade

Break Even Trade

Win Rate

Loss Rate

Average Win

Average Loss

Largest Win

Largest Loss

Average Holding Time

---

## Risk Metrics

Max Drawdown

Average Drawdown

Recovery Factor

Ulcer Index

Risk Reward Ratio

---

## Profit Metrics

Net Profit

Gross Profit

Gross Loss

Profit Factor

Expected Payoff

Expectancy

Average RR

---

## Portfolio Metrics

Sharpe Ratio

Sortino Ratio

Calmar Ratio

MAR Ratio

CAGR

Annual Return

Monthly Return

Daily Return

---

# AI Validation

Hitung performa AI.

Confusion Matrix

Precision

Recall

F1 Score

ROC AUC

Accuracy

Bandingkan:

AI Enabled

vs

AI Disabled

Tujuannya mengetahui apakah AI benar-benar meningkatkan hasil trading.

---

# Explainable AI

Setiap signal harus memiliki alasan.

Contoh:

SELL

Reason

Market Structure = Bearish

EMA20 < EMA50

ATR Expansion

Liquidity Sweep

Mean Reversion

Top SHAP Feature

Market Structure

0.41

ATR

0.22

EMA20

0.18

---

# Backtest Report

Generate report lengkap.

Summary

Winrate

Profit Factor

Drawdown

Sharpe

Expectancy

Return

Trade List

Semua trade.

Tanggal

Entry

Exit

SL

TP

Profit

Reason

Equity Curve

Balance Curve

Monthly Performance

Heatmap

Best Month

Worst Month

Maximum Losing Streak

Maximum Winning Streak

---

# Validation

Backtest harus menghasilkan output yang identik apabila dijalankan kembali menggunakan data historis yang sama.

Seluruh proses harus deterministic.

---

# Future Roadmap

Phase 1

Single Asset Backtesting

Phase 2

Portfolio Backtesting

Phase 3

Walk Forward Analysis

Phase 4

Monte Carlo Simulation

Phase 5

Genetic Strategy Optimization

Phase 6

AI Auto Parameter Optimization

---

# Future Integration

Backtesting Engine harus dapat diintegrasikan dengan:

Unified Signal

AI Prediction Engine

Market Structure Engine

Risk Management Engine

Macro Sentiment Engine

Realtime Signal Engine

Portfolio Manager

---

# Vision

Unified Signal bukan sekadar Signal Generator.

Unified Signal harus berkembang menjadi Professional Decision Support System yang mampu memberikan:

- Signal
- Explainability
- Historical Validation
- Risk Analysis
- AI Insight
- Portfolio Evaluation

Tujuan akhirnya adalah membuat setiap keputusan trading dapat dipertanggungjawabkan secara statistik, bukan berdasarkan opini semata.
