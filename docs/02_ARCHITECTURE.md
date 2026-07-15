# Arsitektur Al-Syaka Quant AI

## Gambaran Umum

Al-Syaka Quant AI adalah platform monorepo yang terdiri dari beberapa aplikasi dan package yang saling terintegrasi. Arsitektur didesain modular dengan pemisahan tanggung jawab yang jelas antara pengumpulan data, analisis, prediksi AI, dan eksekusi.

```
al-syaka-quant-ai/
  apps/
    api/              -- FastAPI REST API (backend utama)
    ai-engine/        -- XGBoost/LightGBM/Transformer + SHAP
    backtester/       -- Backtesting engine
    dashboard/        -- Next.js frontend
    mt5-bridge/       -- MT5 integration
  packages/
    common/           -- database, config, models bersama
    feature-engineering/ -- ekstraksi fitur dari OHLC
    indicators/       -- kalkulasi indikator teknikal
    quant/            -- strategi kuantitatif
    risk/             -- risk management
```

---

## Aplikasi

### `apps/api` -- FastAPI REST API

Backend utama yang menyediakan REST API untuk semua fitur platform.

**Teknologi**: Python FastAPI, SQLAlchemy async, Celery, Redis.

**Router**:
- `/api/v1/market` -- Data pasar (OHLC, ticker, symbols)
- `/api/v1/signals` -- Generasi sinyal trading
- `/api/v1/indicators` -- Indikator teknikal dan feature engineering
- `/api/v1/market-structure` -- Analisis market structure
- `/api/v1/backtesting` -- Backtest engine
- `/api/v1/ai` -- Prediksi AI dan explainability
- `/api/v1/paper-trading` -- Paper trading virtual
- `/api/v1/mt5` -- Integrasi MT5
- `/api/v1/settings` -- Konfigurasi
- `/api/v1/unified-signal` -- Sinyal terpadu (all-in-one)

**Komponen Internal**:
- `collectors/` -- Data collector connectors (Yahoo, Polygon, Massive)
- `market_structure/` -- Market structure detection
- `signal_service/` -- Signal generator engine
- `statistical_engine/` -- Probability dan win rate analysis
- `paper_trading/` -- Virtual trading system
- `tasks/` -- Celery tasks untuk scheduled jobs
- `routers/` -- API routers

### `apps/ai-engine` -- AI/ML Engine

Engine machine learning untuk prediksi arah pasar.

**Teknologi**: XGBoost, LightGBM, PyTorch (Transformer), SHAP, scikit-learn.

**Komponen**:
- `models/` -- Model implementations (XGBoost, LightGBM, Transformer, Base)
- `pipeline.py` -- ML pipeline: features -> labels -> train/test split
- `labeling.py` -- Label generator untuk supervised learning
- `explainability.py` -- SHAP-based explainability

### `apps/backtester` -- Backtesting Engine

Engine untuk menguji strategi trading pada data historis.

**Komponen**:
- `engine.py` -- Main backtest engine dengan event loop
- `trade.py` -- Trade record data class
- `metrics.py` -- Performance metrics calculator

### `apps/dashboard` -- Next.js Frontend

Dashboard web interaktif untuk visualisasi dan monitoring.

**Teknologi**: Next.js 14, TypeScript, Tailwind CSS, lightweight-charts, Recharts.

**Halaman**:
- `/` -- Halaman utama dengan ringkasan
- `/market-data` -- Data pasar dan chart
- `/signals` -- Sinyal trading real-time
- `/backtesting` -- Konfigurasi dan hasil backtest
- `/paper-trading` -- Virtual trading
- `/mt5` -- Status koneksi MT5
- `/settings` -- Pengaturan

### `apps/mt5-bridge` -- MetaTrader 5 Bridge

Jembatan untuk koneksi dan eksekusi trading di MetaTrader 5.

**Komponen**:
- `connector.py` -- Koneksi ke MT5 terminal
- `order_manager.py` -- Manajemen order dengan validasi risiko
- `auto_trader.py` -- Auto trading engine berbasis sinyal
- `safety.py` -- Safety system (kill switch, circuit breaker)

---

## Packages

### `packages/common`

Package bersama yang digunakan oleh semua aplikasi.

**Komponen**:
- `config.py` -- Konfigurasi aplikasi (pydantic-settings)
- `database.py` -- Async SQLAlchemy engine dan session factory
- `models.py` -- Model database (Symbol, OHLC, Tick, News, Signal)

### `packages/indicators`

Kalkulasi indikator teknikal.

**Komponen**:
- `trend.py` -- SMA, EMA, MACD, ADX, Ichimoku
- `oscillators.py` -- RSI, Stochastic, CCI, Williams %R
- `volatility.py` -- ATR, Bollinger Bands, Keltner Channels
- `volume.py` -- Volume indicators

### `packages/feature-engineering`

Pipeline ekstraksi fitur dari data OHLC untuk model AI.

**Komponen**:
- `candlestick.py` -- Body, wick, range, candle patterns
- `momentum.py` -- Price momentum, rate of change, price position
- `volatility.py` -- True Range, ATR variants, normalized volatility
- `session.py` -- Asian, London, US session features
- `pipeline.py` -- Orchestrator semua feature extraction

### `packages/risk`

Manajemen risiko untuk trading.

**Komponen**:
- `risk_manager.py` -- Risk manager terintegrasi
- `kelly.py` -- Kelly criterion calculator
- `stop_loss.py` -- SL/TP calculator (ATR-based, S/R-based, fixed pips)
- `position_sizing.py` -- Position size calculator

### `packages/quant`

Strategi kuantitatif.

**Komponen**:
- `strategies.py` -- Implementasi strategi (Mean Reversion, dll.)
- `backtest.py` -- Backtest utilities
- `utils.py` -- Fungsi utilitas kuantitatif

---

## Alur Data

Berikut adalah alur data end-to-end dari pengumpulan hingga pengambilan keputusan:

```
[Market Data Providers]
  Yahoo Finance  Polygon.io  Massive
        |             |          |
        v             v          v
  [DataCollector] -- Smart Routing & Failover
        |
        v
  [OHLC Data Storage] -- PostgreSQL (async)
        |
        v
  [FeaturePipeline] -- Candlestick, Momentum, Volatility, Session
        |
        v
  [IndicatorCalculator] -- SMA, EMA, RSI, ATR, MACD, ADX, BB
        |
        +---------+---------+---------+
        |         |         |         |
        v         v         v         v
  [Market     [AI       [Statistical [Risk
   Structure]  Engine]   Engine]      Engine]
     |           |          |           |
     | BOS       | XGBoost  | Probability| Position Sizing
     | CHOCH     | LightGBM | Win Rate   | Kelly Criterion
     | FVG       | SHAP     | Combo      | SL/TP
     | Liquidity |          |            |
     | S/R       |          |            |
     |           |          |            |
     +-------+---+----------+----+------+
             |                  |
             v                  v
      [Composite Score]   [Market Regime]
             |                  |
             +--------+---------+
                      |
                      v
            [Macro Bias Engine]
              (H4/D1 analysis)
                      |
                      v
            [Final Decision Engine]
              BUY / SELL / WAIT / HEDGE
                      |
                      v
            [Signal Output]
              - Confidence breakdown
              - Entry/SL/TP
              - Risk level
              - Reasons & explanation
              - AI confidence & SHAP
```

---

## Database

### PostgreSQL dengan SQLAlchemy Async

**Tabel Utama**:

| Tabel | Deskripsi |
|-------|-----------|
| `symbols` | Metadata instrumen trading (nama, base/quote currency, pip size, contract size) |
| `ohlc` | Data harga OHLC (symbol, timeframe, timestamp, open, high, low, close, volume) |
| `ticks` | Data tick-by-tick (bid, ask, last, volume) |
| `news` | Berita pasar dan event ekonomi |
| `signals` | Rekam sinyal trading yang dihasilkan |

**Konfigurasi Koneksi**:
- Async engine dengan `asyncpg` driver
- Connection pool (pool_size=10, max_overflow=20)
- Session factory dengan `async_sessionmaker`
- Migration dengan Alembic

### Redis

- Celery broker dan result backend
- Caching untuk data pasar
- Rate limiting untuk API

---

## Task Queue (Celery)

**Scheduled Tasks**:
- `fetch_ohlc_task` -- Fetch data OHLC periodik untuk semua simbol aktif
- Data processing tasks (indicator computation, feature extraction)
- Model retraining tasks

**Konfigurasi**:
- Broker: Redis
- Result backend: Redis
- Task serialization: JSON
- Retry mechanism dengan exponential backoff
