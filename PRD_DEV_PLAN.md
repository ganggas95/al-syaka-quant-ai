# Al-Syaka Quant AI — Development Plan

> **AI-powered Market Intelligence & Trading Signal Platform**
>
> Dokumen ini berisi perencanaan pengembangan berdasarkan [idea.md](file:///Users/nizar/MyProject/al-syaka-quant-ai/idea.md).

---

## Daftar Isi

- [Vision & Product Goal](#vision--product-goal)
- [Success Metrics](#success-metrics)
- [User Persona](#user-persona)
- [Arsitektur Monorepo](#arsitektur-monorepo)
- [Tech Stack](#tech-stack)
- [12 Module Overview](#12-module-overview)
- [Roadmap — 6 Sprint](#roadmap--6-sprint)
  - [Sprint 1: Foundation & Data Layer](#sprint-1--foundation--data-layer)
  - [Sprint 2: Analytical Engine](#sprint-2--analytical-engine)
  - [Sprint 3: Statistical Signal & Backtesting](#sprint-3--statistical-signal--backtesting)
  - [Sprint 4: AI Model & Explainability](#sprint-4--ai-model--explainability)
  - [Sprint 5: Paper Trading & Journal](#sprint-5--paper-trading--journal)
  - [Sprint 6: MT5 Bridge & Auto Trading](#sprint-6--mt5-bridge--auto-trading)
- [Dependency Graph](#dependency-graph)
- [Milestone & Timeline](#milestone--timeline)

---

## Vision & Product Goal

### Vision

Membangun platform AI yang mampu:

- Memahami kondisi pasar secara **real-time**
- Menghitung **probabilitas arah market**
- Memberikan trading signal yang dapat dijelaskan (**Explainable AI**)
- Melakukan **backtesting**
- Melakukan **paper trading**
- Pada tahap akhir mampu melakukan **auto execution**

Bukan sekadar indikator, tetapi sebuah **Decision Support System** untuk trader.

### Product Goal

Target utama bukan menghasilkan:

```
BUY
```

Tetapi:

```
BUY
Confidence : 84%
Reason :
  - Trend Bullish
  - Momentum meningkat
  - Liquidity Sweep selesai
  - Risk Low
  - Recommended RR 1:2.5
```

---

## Success Metrics

| Phase | Metrik | Target |
|-------|--------|--------|
| **Phase 1** — Data Collector | Stabilitas pengambilan data | 100% uptime |
| **Phase 2** — Indicator Engine | Akurasi kalkulasi indikator | 100% (verified against reference) |
| **Phase 3** — Backtesting | Coverage data historis | Minimal 5 tahun |
| **Phase 4** — Signal Accuracy | Akurasi sinyal | ≥ 60% |
| | Risk Reward ratio | ≥ 1:2 |
| **Phase 5** — Paper Trading | Profit Factor | ≥ 1.5 |
| **Phase 6** — Real Trading | Maximum Drawdown | < 10% |

---

## User Persona

| Persona | Kebutuhan |
|---------|-----------|
| **Beginner** | Membutuhkan signal siap pakai |
| **Intermediate** | Membutuhkan alasan di balik signal |
| **Advanced** | Membutuhkan statistik dan metrik |
| **Quant Researcher** | Membutuhkan akses data mentah |

---

## Arsitektur Monorepo

```
al-syaka-quant-ai/
├── apps/
│   ├── api/                  # FastAPI backend — REST API utama
│   ├── dashboard/            # NextJS frontend — UI dashboard
│   ├── ai-engine/            # AI model training & inference service
│   ├── backtester/           # Backtesting engine service
│   ├── signal-service/       # Signal generation service
│   └── mt5-bridge/           # MT5 connector service
├── packages/
│   ├── indicators/           # Technical indicators library (Python murni)
│   ├── feature-engineering/  # Feature extraction & transformation
│   ├── quant/                # Quantitative analysis tools
│   ├── risk/                 # Risk management (position sizing, SL/TP)
│   └── common/               # Shared utilities, models, configs
├── database/
│   ├── migrations/           # Alembic database migrations
│   └── seed/                 # Seed data & reference data
├── models/                   # Trained model artifacts (.pkl, .pt)
├── datasets/                 # Dataset storage (raw & processed)
├── scripts/                  # Utility scripts (one-off tasks, ETL)
├── docker/                   # Docker Compose & Dockerfiles
├── .github/                  # GitHub Actions workflows
└── ...
```

---

## Tech Stack

### Backend

| Teknologi | Fungsi |
|-----------|--------|
| **Python** | Bahasa utama backend & AI |
| **FastAPI** | REST API framework |
| **SQLAlchemy** | ORM untuk database |
| **Celery** | Task queue untuk async jobs |
| **Redis** | Message broker & cache |

### Database

| Teknologi | Fungsi |
|-----------|--------|
| **PostgreSQL** | Database utama (OHLC, tick, signal, journal) |

### AI / ML

| Teknologi | Fungsi |
|-----------|--------|
| **PyTorch** | Deep learning (Transformer) |
| **XGBoost** | Model prediksi versi 1 |
| **LightGBM** | Model prediksi versi 2 |
| **Scikit Learn** | Preprocessing & evaluation |
| **Pandas / NumPy** | Data manipulation |
| **SHAP** | Explainable AI |

### Frontend

| Teknologi | Fungsi |
|-----------|--------|
| **NextJS** | React framework |
| **Tailwind CSS** | Styling |
| **ShadCN** | UI component library |
| **TanStack Query** | Server state management |
| **Chart.js** | Grafik dan visualisasi |
| **TradingView Widget** | Advanced charting |

### Deployment

| Teknologi | Fungsi |
|-----------|--------|
| **Docker** | Containerization |
| **Nginx** | Reverse proxy |
| **GitHub Actions** | CI/CD |
| **Railway / VPS** | Hosting |

---

## 12 Module Overview

| # | Module | Sprint | Deskripsi |
|---|--------|--------|-----------|
| 1 | **Market Data Collector** | Sprint 1 | Mengumpulkan data dari MT5, Broker API, Yahoo Finance, Polygon, AlphaVantage, Investing Calendar |
| 2 | **Indicator Engine** | Sprint 2 | Menghitung EMA, SMA, RSI, ATR, MACD, ADX, Bollinger, VWAP, Ichimoku, Volume Profile, Pivot, Supertrend |
| 3 | **Feature Engineering** | Sprint 2 | Ekstraksi fitur dari OHLC: Body, Wick, Range, Momentum, Volatility, Session, News Impact, DXY, Yield |
| 4 | **Market Structure Engine** | Sprint 2 | Deteksi HH/HL/LH/LL, BOS, CHOCH, S/R, Trendline, Liquidity Sweep, FVG, Order Block |
| 5 | **Statistical Engine** | Sprint 3 | Hitung probabilitas berdasarkan kombinasi indikator & win rate historis |
| 6 | **AI Prediction Engine** | Sprint 4 | XGBoost → LightGBM → Transformer untuk prediksi arah market |
| 7 | **Explainable AI** | Sprint 4 | Wajib menjelaskan alasan setiap sinyal (SHAP-based) |
| 8 | **Risk Engine** | Sprint 3 | Position sizing, SL/TP, Kelly Criterion, risk management |
| 9 | **Signal Generator** | Sprint 3 | Output final: BUY/SELL, Entry, SL, TP, Confidence, Reason |
| 10 | **Backtesting** | Sprint 3 | Backtest 5 tahun data, output Winrate, Drawdown, Sharpe, Sortino, Profit Factor |
| 11 | **Paper Trading** | Sprint 5 | Trading virtual dengan data real-time |
| 12 | **Auto Trading** | Sprint 6 | Eksekusi order otomatis via MT5 Bridge |

---

## Roadmap — 6 Sprint

---

### Sprint 1 — Foundation & Data Layer

**Goal**: Infrastructure dasar + Data Collector berfungsi + API siap + Dashboard minimal bisa ditampilkan.

#### Tasks

| ID | Task | Module | Estimasi |
|----|------|--------|----------|
| 1.1 | **Setup Monorepo** — Inisialisasi folder structure, package management (pnpm/uv), root config | — | 1 hari |
| 1.2 | **Database Setup** — PostgreSQL instance, SQLAlchemy models (OHLC, tick, news, metadata), Alembic migrations | Module 1 | 2 hari |
| 1.3 | **FastAPI Base** — Project scaffold, base routing, middleware (CORS, logging), error handling, config management | — | 2 hari |
| 1.4 | **Market Data Collector** — Connector untuk MT5, Yahoo Finance, Polygon.io, AlphaVantage, Investing Calendar | Module 1 | 4 hari |
| 1.5 | **Celery + Redis** — Task queue setup, scheduler untuk periodic data fetching, retry mechanism | Module 1 | 2 hari |
| 1.6 | **Dashboard Minimal** — NextJS scaffold, Tailwind + ShadCN setup, halaman utama dengan grafik sederhana (line chart) | — | 3 hari |

#### Deliverables

- [ ] Monorepo structure siap
- [ ] PostgreSQL running dengan migration pertama
- [ ] FastAPI server running dengan health check endpoint
- [ ] Data Collector bisa mengambil data dari minimal 2 sumber
- [ ] Celery worker running dengan scheduled task
- [ ] Dashboard bisa diakses di browser, menampilkan grafik sederhana

#### Success Metric

- Data Collector stabil: **100% uptime**

---

### Sprint 2 — Analytical Engine

**Goal**: Semua indikator teknis berfungsi + feature engineering + market structure detection.

#### Tasks

| ID | Task | Module | Estimasi |
|----|------|--------|----------|
| 2.1 | **Indicator Engine — Basic** — EMA, SMA, RSI, ATR (Python murni, diverifikasi) | Module 2 | 2 hari |
| 2.2 | **Indicator Engine — Advanced** — MACD, ADX, Bollinger Bands, VWAP | Module 2 | 2 hari |
| 2.3 | **Indicator Engine — Complex** — Ichimoku, Volume Profile, Pivot, Supertrend | Module 2 | 3 hari |
| 2.4 | **Feature Engineering** — Body, Upper/Lower Wick, Range, ATR, EMA Distance, Momentum, Volatility, Session, News Impact, DXY, Yield | Module 3 | 3 hari |
| 2.5 | **Market Structure Engine** — HH/HL/LH/LL, Break of Structure, CHOCH, Support/Resistance, Trendline, Liquidity Sweep, Fair Value Gap, Order Block (opsional) | Module 4 | 4 hari |
| 2.6 | **API Integration** — Expose semua hasil kalkulasi via FastAPI endpoints | — | 1 hari |
| 2.7 | **Dashboard Update** — Tampilkan indikator + market structure di chart (TradingView Widget) | — | 2 hari |

#### Deliverables

- [ ] Semua indikator teknis terimplementasi dan terverifikasi
- [ ] Feature engineering pipeline siap
- [ ] Market structure engine bisa mendeteksi pattern dasar
- [ ] API endpoints untuk semua modul
- [ ] Dashboard menampilkan chart dengan indikator

#### Success Metric

- Indicator Engine akurasi: **100%** (verified)

---

### Sprint 3 — Statistical Signal & Backtesting

**Goal**: Signal berbasis statistik + probability engine + risk management + backtesting engine.

#### Tasks

| ID | Task | Module | Estimasi |
|----|------|--------|----------|
| 3.1 | **Statistical Engine** — Hitung probabilitas BUY/SELL berdasarkan kombinasi indikator, historical win rate, session analysis | Module 5 | 3 hari |
| 3.2 | **Risk Engine** — Position sizing (fixed %), Stop Loss / Take Profit calculation, Kelly Criterion (opsional), risk per trade (1-2%) | Module 8 | 2 hari |
| 3.3 | **Signal Generator** — Integrasi Statistical Engine + Risk Engine → output final: BUY/SELL, Entry, SL, TP, Confidence, Reason | Module 9 | 2 hari |
| 3.4 | **Backtesting Engine** — Input historical data (5 tahun), eksekusi sinyal virtual, kalkulasi metrik: Winrate, Drawdown, Sharpe, Sortino, Profit Factor | Module 10 | 4 hari |
| 3.5 | **Dashboard Backtesting** — UI untuk konfigurasi & menjalankan backtest, tampilkan hasil dalam bentuk grafik & tabel | Module 10 | 2 hari |

#### Deliverables

- [ ] Statistical engine menghasilkan probabilitas
- [ ] Risk engine menghitung lot/SL/TP
- [ ] Signal generator menghasilkan output lengkap
- [ ] Backtesting engine bisa memproses 5 tahun data
- [ ] Dashboard backtesting fungsional

#### Success Metric

- Backtesting coverage: **Minimal 5 tahun data**

---

### Sprint 4 — AI Model & Explainability

**Goal**: Machine learning model terintegrasi + explainable AI + dashboard AI.

#### Tasks

| ID | Task | Module | Estimasi |
|----|------|--------|----------|
| 4.1 | **Feature Pipeline for ML** — Automated feature engineering untuk training dataset, labeling (forward-looking), train/test split | Module 6 | 2 hari |
| 4.2 | **XGBoost Model** — Training, hyperparameter tuning, validation, inference pipeline | Module 6 | 3 hari |
| 4.3 | **LightGBM Model** — Training, comparison with XGBoost, ensemble strategy | Module 6 | 2 hari |
| 4.4 | **Transformer Model** — Time series transformer architecture, training, evaluation | Module 6 | 4 hari |
| 4.5 | **Explainable AI** — SHAP-based explanation untuk setiap prediksi, output alasan (EMA20 > EMA50, ATR naik, RSI 61, London Session, DXY turun) | Module 7 | 3 hari |
| 4.6 | **Dashboard AI** — Tampilkan prediksi AI, confidence score, explanation, perbandingan model | — | 2 hari |

#### Deliverables

- [ ] XGBoost model terlatih & siap inferensi
- [ ] LightGBM model sebagai ensemble
- [ ] Transformer model untuk pattern recognition
- [ ] Explainable AI menghasilkan alasan untuk setiap sinyal
- [ ] Dashboard AI menampilkan prediksi + explanation

#### Success Metric

- Signal Accuracy: **≥ 60%**
- Risk Reward: **≥ 1:2**

---

### Sprint 5 — Paper Trading & Journal

**Goal**: Simulasi trading live + trade journal + performance analytics.

#### Tasks

| ID | Task | Module | Estimasi |
|----|------|--------|----------|
| 5.1 | **Paper Trading Engine** — Virtual account, real-time signal execution, balance tracking, open/close position management | Module 11 | 4 hari |
| 5.2 | **Trade Journal** — Catat semua entry/exit, alasan sinyal, screenshot, notes, tag | — | 2 hari |
| 5.3 | **Performance Analytics** — Equity curve, drawdown chart, monthly ROI, win rate by pair/session, profit factor tracker | — | 3 hari |
| 5.4 | **Signal Performance Tracking** — Track setiap sinyal yang dihasilkan vs outcome aktual, confusion matrix | Module 11 | 2 hari |
| 5.5 | **Dashboard Paper Trading** — UI untuk monitoring posisi, journal entry, analytics view | — | 2 hari |

#### Deliverables

- [ ] Paper trading engine bisa menjalankan trading virtual
- [ ] Trade journal dengan semua histori
- [ ] Performance analytics dashboard
- [ ] Signal performance tracking

#### Success Metric

- Profit Factor Paper Trading: **≥ 1.5**

---

### Sprint 6 — MT5 Bridge & Auto Trading

**Goal**: Integrasi dengan MetaTrader 5 + auto execution dengan safety.

#### Tasks

| ID | Task | Module | Estimasi |
|----|------|--------|----------|
| 6.1 | **MT5 Connector** — Python-MT5 integration via MetaTrader5 library, account management, order execution | Module 12 | 3 hari |
| 6.2 | **Order Manager** — Order validation, risk check sebelum eksekusi, partial fill handling, error recovery | Module 12 | 3 hari |
| 6.3 | **Auto Trading Engine** — Signal-based auto execution, scheduling, kill switch, max daily loss limit | Module 12 | 4 hari |
| 6.4 | **Monitoring Dashboard** — Real-time position monitor, account equity, open orders, trade history, performance real-time | — | 3 hari |
| 6.5 | **Safety System** — Maximum drawdown protection, circuit breaker, notification/alert system | Module 12 | 2 hari |

#### Deliverables

- [ ] MT5 Bridge terkoneksi dan bisa eksekusi order
- [ ] Order manager dengan validasi & risk check
- [ ] Auto trading engine dengan safety system
- [ ] Monitoring dashboard real-time

#### Success Metric

- Maximum Drawdown Real Trading: **< 10%**

---

## Dependency Graph

```
Sprint 1 ──► Sprint 2 ──► Sprint 3 ──► Sprint 4 ──► Sprint 5 ──► Sprint 6
(Data)       (Indikator)  (Statistik)   (AI)         (Paper)      (Auto)

Dependency:
  Sprint 2 membutuhkan data dari Sprint 1
  Sprint 3 membutuhkan indikator dari Sprint 2
  Sprint 4 membutuhkan fitur dari Sprint 2 & 3
  Sprint 5 membutuhkan sinyal dari Sprint 3 & 4
  Sprint 6 membutuhkan semua modul sebelumnya
```

**Prinsip utama**: AI BUKAN fase pertama. Kualitas data, feature engineering, indikator, dan backtesting adalah fondasi. Model AI adalah lapisan akhir yang menyempurnakan sistem.

---

## Milestone & Timeline

| Sprint | Milestone | Estimated Duration |
|--------|-----------|-------------------|
| **Sprint 1** | Data infrastructure + Dashboard dasar | 2 minggu |
| **Sprint 2** | Analytical engine (indicators + market structure) | 2-3 minggu |
| **Sprint 3** | Statistical signal + Backtesting | 2-3 minggu |
| **Sprint 4** | AI Model + Explainability | 2-3 minggu |
| **Sprint 5** | Paper Trading + Journal | 2 minggu |
| **Sprint 6** | MT5 Bridge + Auto Trading | 2-3 minggu |
| **Total** | **MVP → Production** | **12-17 minggu** |

---

## Catatan Penting

1. **AI Bukan Fase Pertama** — Keunggulan sistem lebih ditentukan oleh kualitas data, feature engineering, dan backtesting daripada model AI.
2. **Explainability adalah Wajib** — Setiap sinyal harus menyertakan alasan yang bisa dipahami manusia.
3. **Safety First** — Auto trading harus memiliki multiple layer of protection (kill switch, max drawdown, daily loss limit).
4. **Modular & Testable** — Setiap modul harus bisa diuji secara independen.
5. **Monorepo** — Memudahkan pengelolaan kode bersama dan memastikan konsistensi antar modul.

---

*Dokumen ini disusun berdasarkan [idea.md](file:///Users/nizar/MyProject/al-syaka-quant-ai/idea.md) dan dapat disesuaikan sesuai kebutuhan pengembangan.*
