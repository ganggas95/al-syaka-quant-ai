## PRD (Product Requirements Document)

### Project Name

Al-Syaka Quant AI

### AI-powered Market Intelligence & Trading Signal Platform

⸻

### Vision

Membangun platform AI yang mampu:

- memahami kondisi pasar secara real-time,
- menghitung probabilitas arah market,
- memberikan trading signal yang dapat dijelaskan (Explainable AI),
- melakukan backtesting,
- melakukan paper trading,
- dan pada tahap akhir mampu melakukan auto execution.

Bukan sekadar indikator, tetapi sebuah Decision Support System untuk trader.

⸻

### Product Goal

Target utama bukan menghasilkan:

BUY

Tetapi

BUY
Confidence : 84%
Reason :
Trend Bullish
Momentum meningkat
Liquidity Sweep selesai
Risk Low
Recommended RR 1:2.5

⸻

### Success Metrics

### Phase 1

✅ Data Collector stabil

100%

⸻

### Phase 2

Indicator Engine

akurasi

100%

⸻

### Phase 3

Backtesting

minimal

5 tahun data

⸻

### Phase 4

Signal Accuracy

60%

Risk Reward

1:2

⸻

### Phase 5

Paper Trading

Profit Factor

1.5

⸻

### Phase 6

Real Trading

Maximum Drawdown

<10%

⸻

### User Persona

### Beginner

Membutuhkan signal.

⸻

### Intermediate

Membutuhkan alasan.

⸻

### Advanced

Membutuhkan statistik.

⸻

### Quant Researcher

Membutuhkan data.

⸻

### MVP

Dashboard

Trend

Signal

Probability

Market Structure

News

Trade Journal

Backtesting

⸻

### Technical PRD

⸻

### Module 1

#### Market Data Collector

Input

```
MT5
Broker API
Yahoo Finance
Polygon
AlphaVantage
Investing Calendar
```

Output

```
OHLC
Tick
Volume
Spread
News
```

Database

`PostgreSQL`

⸻

### Module 2

#### Indicator Engine

Menghitung

EMA

SMA

RSI

ATR

MACD

ADX

Bollinger

VWAP

Ichimoku

Volume Profile

Pivot

Supertrend

Semua dilakukan sendiri menggunakan Python agar mudah diuji, bukan hanya mengandalkan nilai dari MT5.

⸻

### Module 3

#### Feature Engineering

Input

```
OHLC
```

Output

```
Body
Upper Wick
Lower Wick
Range
ATR
EMA Distance
Momentum
Volatility
```

Ditambah

```
Session
News Impact
DXY
Yield
```

⸻

### Module 4

#### Market Structure Engine

Mendeteksi

Higher High

Higher Low

Lower High

Lower Low

Break of Structure

CHOCH

Support Resistance

Trendline

Liquidity Sweep

Fair Value Gap

Order Block (opsional)

⸻

### Module 5

#### Statistical Engine

Menghitung

```
Probability
BUY
SELL
```

Contoh

```
EMA Cross

- ATR
- Volume
- Session
  ↓
  Win Rate
  72%
```

⸻

### Module 6

#### AI Prediction Engine

Versi pertama

```
XGBoost
```

Versi kedua

```
LightGBM
```

Versi ketiga

```
Transformer
```

Output

```
BUY
Probability
Confidence
Expected Return
```

⸻

### Module 7

#### Explainable AI

Ini yang menurut saya paling penting.

AI wajib menjelaskan.

Misalnya

```
BUY
84%
karena
EMA20 > EMA50
ATR naik
RSI 61
London Session
DXY turun
```

Jangan pernah menghasilkan BUY tanpa alasan.

⸻

### Module 8

#### Risk Engine

Menghitung

```
Lot

Stop Loss

Take Profit

Position Size

Kelly Criterion (opsional)

Risk

1%

2%
```

⸻

### Module 9

#### Signal Generator

Output

```
BUY
Entry
SL
TP
Confidence
Reason
```

⸻

### Module 10

#### Backtesting

Input

```
5 tahun data
```

Output

```
Winrate
Drawdown
Sharpe
Sortino
Profit Factor
```

⸻

### Module 11

#### Paper Trading

Trading virtual

Simpan semua hasil.

⸻

### Module 12

#### Auto Trading

Tahap terakhir.

EA MT5 hanya menjalankan order.

AI tetap berada di Python.

⸻

### Tech Stack

#### Backend

```
Python
FastAPI
SQLAlchemy
Celery
Redis
PostgreSQL
```

#### AI

```
PyTorch
XGBoost
LightGBM
Scikit Learn
Pandas
NumPy
```

#### Frontend

```
NextJS
React
Tailwind
ShadCN
TanStack Query
Chart.js
TradingView Widget
```

Deployment

```
Docker
Nginx
GitHub Actions
Railway / VPS
```

⸻

### Folder Structure

```
apps/
├── api/
├── dashboard/
├── ai-engine/
├── backtester/
├── signal-service/
├── mt5-bridge/
packages/
├── indicators/
├── feature-engineering/
├── quant/
├── risk/
├── common/
database/
├── migrations/
├── seed/
models/
├── xgboost/
├── transformer/
datasets/
scripts/
```

⸻

### Roadmap

#### Sprint 1

✔ Data Collector

✔ PostgreSQL

✔ FastAPI

✔ Dashboard

⸻

#### Sprint 2

✔ Indicator Engine

✔ Feature Engineering

✔ Market Structure

⸻

#### Sprint 3

✔ Statistical Signal

✔ Probability Engine

✔ Backtesting

⸻

#### Sprint 4

✔ AI Model

✔ Explainable AI

✔ Dashboard AI

⸻

#### Sprint 5

✔ Paper Trading

✔ Journal

✔ Analytics

⸻

#### Sprint 6

✔ MT5 Bridge

✔ Auto Trading

⸻

Mengapa roadmap ini menurut saya tepat untuk Anda

Melihat pengalaman Anda membangun aplikasi berskala besar dengan Nx Monorepo, React/Next.js, FastAPI, NestJS, PostgreSQL, saya menyarankan agar proyek ini juga dibangun sebagai monorepo sejak awal. Dengan begitu:

- Modul AI bisa berkembang tanpa mengganggu backend API.
- Backtester dapat dijalankan secara independen.
- Dashboard dapat menggunakan API yang sama dengan layanan AI.
- Jika nanti ingin menambah aset (Forex, Crypto, Indeks), arsitektur tidak perlu dirombak.

Yang paling penting, fase AI sebaiknya tidak menjadi fase pertama. Keunggulan sistem seperti ini lebih banyak ditentukan oleh kualitas data, feature engineering, dan kemampuan melakukan backtesting daripada sekadar memilih model AI yang paling canggih. Dengan fondasi yang kuat, setiap peningkatan model akan lebih mudah diukur dan divalidasi secara objektif.
