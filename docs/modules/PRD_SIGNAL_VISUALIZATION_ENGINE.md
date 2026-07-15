# PRD — Signal Visualization Engine

Version: 1.0

Status: Draft

Module:
Signal Visualization Engine

Project:
Unified Signal

Owner:
AI Analytics Layer

---

# Overview

Signal Visualization Engine bertugas mengubah hasil analisis Unified Signal menjadi visualisasi interaktif yang mudah dipahami.

Tujuan utama modul ini bukan hanya mempercantik UI, tetapi membantu trader memahami alasan di balik setiap keputusan trading.

Visualisasi harus menjawab tiga pertanyaan utama:

1. Apa keputusan sistem?
2. Mengapa keputusan tersebut dibuat?
3. Seberapa besar keyakinan sistem?

---

# Objectives

Visualisasi harus:

- mudah dipahami
- real-time
- explainable
- mendukung AI Explainability
- mendukung Multi Timeframe
- mendukung Technical + Macro Analysis
- responsif

---

# Dashboard Sections

Signal Visualization Engine terdiri dari beberapa komponen.

---

## 1. Signal Summary

Menampilkan keputusan akhir.

Contoh

SELL

Confidence

89%

Composite Score

65.8%

Risk

LOW

Quality

GOOD

Signal ID

SIG-11

---

Visual Component

- Signal Card
- Confidence Ring
- Quality Badge
- Risk Badge

---

## 2. Composite Score

Visualisasi kontribusi seluruh engine.

Contoh

Market Structure

85%

Momentum

55%

Trend

50%

Volatility

75%

AI Prediction

50%

---

Visualization

Radar Chart

Bar Chart

Horizontal Progress

Gauge

---

Purpose

Menjelaskan penyusun Composite Score.

---

## 3. Market Structure

Visualisasi kondisi market.

Menampilkan

Trend

Bullish / Bearish

Swing High

Swing Low

Break of Structure

CHOCH

Liquidity Sweep

Fair Value Gap

---

Visualization

Tree Diagram

Market Structure Timeline

Swing Chart

Trend Indicator

---

## 4. Multi Timeframe Alignment

Visualisasi sinkronisasi timeframe.

Contoh

M15

BUY

H1

SELL

H4

SELL

D1

SELL

---

Visualization

Heatmap

Alignment Matrix

Signal Tree

---

Output

Alignment %

Conflict %

---

## 5. Technical Indicators

Visualisasi seluruh indikator.

EMA

MACD

RSI

ADX

ATR

Volume

Bollinger

VWAP

---

Visualization

Mini Chart

Trend Line

Indicator Status

Gauge

---

## 6. AI Explainability

Menggunakan SHAP.

Visualisasi feature yang paling mempengaruhi keputusan.

Contoh

Market Structure

+0.42

ATR

+0.18

EMA20

+0.14

Liquidity Sweep

+0.09

RSI

-0.04

---

Visualization

Horizontal Importance Bar

Waterfall Chart

SHAP Summary Plot

Force Plot

---

Purpose

Menjelaskan alasan AI.

---

## 7. Macro Sentiment

Visualisasi kondisi makro.

Komponen

Fed Rate

CPI

PPI

Oil

Bond Yield

DXY

VIX

Geopolitics

---

Output

Bullish Gold

Bearish Gold

Neutral

---

Visualization

Sentiment Gauge

Heatmap

Pie Chart

Risk Meter

---

## 8. Market Regime

Visualisasi tipe market.

Trending

Sideways

High Volatility

Low Volatility

Risk On

Risk Off

News Driven

---

Visualization

Regime Badge

Probability Bar

Timeline

---

## 9. Entry Planning

Visualisasi setup trading.

Entry

Stop Loss

Take Profit

Risk Reward

ATR

Expected Holding Time

---

Visualization

Price Ladder

RR Diagram

Risk Box

Trade Map

---

## 10. Probability Distribution

Menampilkan probabilitas outcome.

BUY

SELL

WAIT

---

Visualization

Probability Bar

Bell Curve

Distribution Chart

Confidence Interval

---

## 11. Risk Analysis

Visualisasi risiko.

Drawdown

Volatility

ATR

Position Size

Maximum Loss

---

Visualization

Gauge

Risk Matrix

Heatmap

---

## 12. Historical Performance

Visualisasi performa strategi.

Win Rate

Profit Factor

Expectancy

Sharpe Ratio

Drawdown

Recovery

---

Visualization

Equity Curve

Balance Curve

Monthly Heatmap

Performance Trend

---

## 13. Trade Timeline

Menampilkan seluruh keputusan trading.

Signal

Entry

Exit

Profit

Loss

Reason

---

Visualization

Timeline

Trade History

Candle Overlay

---

## 14. AI Decision Flow

Menampilkan proses pengambilan keputusan AI.

Feature

↓

AI Prediction

↓

Composite Score

↓

Macro Filter

↓

Risk Engine

↓

Final Signal

---

Visualization

Flow Diagram

Decision Tree

Pipeline

---

# Interactive Features

Dashboard mendukung:

Hover

Tooltip

Zoom

Timeframe Switch

Comparison

History Replay

Explain Mode

Dark Mode

Export PNG

Export PDF

Export JSON

---

# Charts

Dashboard menggunakan:

Radar Chart

Bar Chart

Stacked Bar

Horizontal Bar

Pie Chart

Donut Chart

Gauge

Heatmap

Timeline

Line Chart

Area Chart

Scatter Plot

Waterfall Chart

Tree Diagram

Sankey Diagram

Treemap

---

# UI Requirements

Dark Theme

Responsive

Mobile Friendly

Desktop Optimized

Real-time Update

Smooth Animation

Loading Skeleton

---

# Performance

Rendering < 200 ms

Realtime Update < 1 second

Support 1000+ historical signals

Support WebSocket

---

# API

GET

/signal/{id}

GET

/signal/history

GET

/signal/composite

GET

/signal/shap

GET

/signal/performance

GET

/signal/market-structure

GET

/signal/macro

---

# Future Roadmap

Phase 1

Static Visualization

Phase 2

Interactive Dashboard

Phase 3

Historical Replay

Phase 4

Backtesting Visualization

Phase 5

Portfolio Visualization

Phase 6

AI Explainability Dashboard

Phase 7

Institutional Analytics Dashboard

---

# Success Metrics

Dashboard harus mampu menjawab:

Apa keputusan sistem?

Mengapa keputusan tersebut dibuat?

Bagaimana tingkat keyakinannya?

Bagaimana kondisi market?

Bagaimana risiko trading?

Bagaimana performa historis strategi?

Apakah AI dapat menjelaskan keputusannya?

---

# Vision

Signal Visualization Engine bukan sekadar dashboard.

Modul ini merupakan Decision Intelligence Layer yang menerjemahkan seluruh analisis Unified Signal menjadi visualisasi yang mudah dipahami oleh trader, analis, maupun AI Agent.
