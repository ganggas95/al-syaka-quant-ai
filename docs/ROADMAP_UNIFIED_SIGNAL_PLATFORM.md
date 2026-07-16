# Unified Signal Platform

## Product Development Roadmap

Version: 1.0

---

# Vision

Membangun platform AI Trading Research yang mampu:

- menghasilkan signal berkualitas tinggi,
- menjelaskan alasan di balik setiap signal,
- mengevaluasi performa strategy secara ilmiah,
- melakukan optimasi secara berkelanjutan,
- menjadi fondasi menuju autonomous AI Trading Assistant.

---

# Guiding Principles

Semua development HARUS mengikuti prinsip berikut.

1. Data Driven
2. Explainable AI
3. Reproducible Backtest
4. Modular Architecture
5. Research First
6. UI follows Data
7. No Feature Without Validation

Setiap feature harus dapat dibuktikan meningkatkan salah satu metric.

---

# Global Success Metrics

## Trading

Target Minimum

Profit Factor > 1.40

Win Rate
55–60%

Sharpe

> 0.8

Sortino

> 1.0

Recovery

> 3

Max Drawdown
<5%

Expectancy
Positive

Calmar

> 2

---

## AI

Inference

<500 ms

Backtest

1000 trade
<10 second

Signal Generation

<200 ms

UI Refresh

<100 ms

---

# Development Roadmap

---

# PHASE 1

Core Signal Engine

Status

Completed

Objective

Membangun engine yang mampu menghasilkan signal.

Deliverables

- Market Structure
- Trend Detection
- EMA
- RSI
- ATR
- MACD
- Composite Score
- AI Prediction
- Multi Timeframe
- Risk Management

Definition of Done

Signal dapat dihasilkan secara konsisten.

---

# PHASE 2

Backtesting Engine

Status

Completed

Objective

Menguji kualitas strategy.

Deliverables

- Historical Simulation
- Entry Exit
- TP
- SL
- Equity Curve
- Trade Statistics
- Session Analysis

Definition of Done

Backtest dapat dijalankan terhadap historical data.

---

# PHASE 3

Trading Analytics Dashboard

Status

In Progress

Objective

Mengubah data menjadi insight.

Deliverables

Dashboard Metrics

Win Rate

Profit Factor

Sharpe

Sortino

Recovery

Expectancy

Calmar

Trade Distribution

Session Breakdown

Signal Loss Breakdown

Price Chart

Monthly Return

Definition of Done

Semua metric dapat divisualisasikan.

---

# PHASE 4

Live Signal Workspace

Priority

HIGH

Objective

Menghilangkan proses Generate Signal manual.

Deliverables

Auto Generate

Auto Refresh

Live Signal

Loading Skeleton

Empty State

Market Overview

Market Thesis

Consensus

Confidence Meter

Probability Chart

Signal Timeline

Signal History

SHAP Explanation

Definition of Done

User hanya perlu memilih Symbol.

Signal muncul otomatis.

---

# PHASE 5

Explainable AI

Priority

HIGH

Objective

Menjelaskan alasan AI.

Deliverables

SHAP Importance

Feature Ranking

Positive Feature

Negative Feature

Confidence Breakdown

Decision Tree View

Market Reasoning

Conflict Detection

Risk Explanation

Definition of Done

Semua keputusan AI dapat dijelaskan.

---

# PHASE 6

Advanced Analytics

Priority

HIGH

Deliverables

Rolling Sharpe

Rolling Win Rate

Rolling Drawdown

Rolling Profit Factor

Trade Duration

Holding Time

Trade Heatmap

Hourly Performance

Weekday Performance

Monthly Trend

Regime Performance

Definition of Done

Trader dapat menemukan kelemahan strategy.

---

# PHASE 7

Research Tools

Priority

HIGH

Deliverables

Trade Replay

Signal Replay

Feature Comparison

Version Comparison

Parameter Comparison

A/B Testing

Walk Forward

Out of Sample

Monte Carlo

Definition of Done

Semua perubahan strategy dapat dibandingkan.

---

# PHASE 8

Optimization Lab

Priority

HIGH

Deliverables

Hyperparameter Search

Grid Search

Bayesian Optimization

Optuna

Threshold Optimizer

ATR Optimizer

EMA Optimizer

Risk Optimizer

Definition of Done

Parameter terbaik ditemukan otomatis.

---

# PHASE 9

Machine Learning

Priority

HIGH

Deliverables

Dataset Builder

Feature Store

Training Pipeline

Validation Pipeline

Model Registry

Experiment Tracking

Feature Selection

Cross Validation

Definition of Done

Model dapat dilatih ulang secara otomatis.

---

# PHASE 10

Live Monitoring

Priority

HIGH

Deliverables

Real Time Signal

Latency

Prediction Drift

Feature Drift

Accuracy Drift

Daily Report

Weekly Report

Alert

Discord Notification

Telegram Notification

Definition of Done

Platform mampu memonitor performa AI.

---

# PHASE 11

Portfolio Engine

Priority

Medium

Deliverables

Portfolio Backtest

Risk Allocation

Capital Allocation

Correlation Matrix

Portfolio Heatmap

Definition of Done

Multiple symbol dapat diuji bersamaan.

---

# PHASE 12

Paper Trading

Priority

Medium

Deliverables

Virtual Account

Paper Order

Position Tracking

Live PnL

Trade Journal

Definition of Done

Signal dapat diuji real-time tanpa uang asli.

---

# PHASE 13

Broker Integration

Priority

Medium

Deliverables

MT5

Binance

Bybit

Interactive Broker

Order Management

Definition of Done

Signal dapat dieksekusi otomatis.

---

# PHASE 14

AI Assistant

Priority

Medium

Deliverables

Natural Language Query

Market Summary

Trade Explanation

Performance Analysis

Strategy Recommendation

Definition of Done

User dapat bertanya langsung kepada AI.

---

# PHASE 15

Continuous Learning

Priority

Future

Deliverables

Automatic Retraining

Drift Detection

Feedback Loop

Model Versioning

Online Learning

Definition of Done

AI berkembang secara otomatis.

---

# Development Rules

Semua feature HARUS memenuhi:

✓ Unit Test

✓ Integration Test

✓ Backtest

✓ Documentation

✓ Benchmark

✓ Changelog

Tanpa itu Pull Request tidak boleh di-merge.

---

# Branch Strategy

main

Stable Production

develop

Integration

feature/\*

Feature Development

research/\*

Research

experiment/\*

AI Experiment

hotfix/\*

Bug Fix

---

# Definition of Ready

Sebelum development dimulai

Harus ada:

- PRD
- Task Breakdown
- Acceptance Criteria
- UI Mockup
- Technical Design

---

# Definition of Done

Suatu feature dianggap selesai jika:

- Code selesai
- Test lulus
- Documentation selesai
- Benchmark selesai
- Tidak menurunkan Backtest
- Tidak menurunkan Performance
- Pull Request telah direview

---

# AI Agent Rules

AI Agent DILARANG:

❌ mengubah strategy tanpa benchmark

❌ menghapus metric

❌ mengubah baseline

❌ menggabungkan beberapa feature besar dalam satu branch

❌ melakukan refactor besar bersamaan dengan penambahan feature

AI Agent WAJIB:

✔ menjaga backward compatibility

✔ membuat migration bila perlu

✔ membuat changelog

✔ membuat benchmark

✔ membandingkan sebelum dan sesudah perubahan

✔ selalu menjaga reproducibility

---

# North Star

Target akhir platform bukan sekadar menghasilkan BUY atau SELL.

Target akhir adalah membangun sebuah Explainable AI Trading Research Platform yang:

- Akurat
- Transparan
- Mudah dianalisis
- Mudah dioptimasi
- Mudah dikembangkan
- Siap digunakan untuk live trading.
