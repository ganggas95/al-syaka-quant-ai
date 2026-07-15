# Task Tracking - Al-Syaka Quant AI

## Status Sprint

**Sprint Saat Ini:** Sprint 6 - MT5 Bridge & Auto Trading

**Versi Target:** 0.3.0

---

## Sprint 6: MT5 Bridge & Auto Trading

### Completed

| Task | Status | Assignee | Selesai |
|------|--------|----------|---------|
| MT5 connector dengan mode simulasi | Done | - | Sprint 6 |
| Order manager (place, close, modify) | Done | - | Sprint 6 |
| Auto trading engine | Done | - | Sprint 6 |
| Safety system (kill switch, max drawdown) | Done | - | Sprint 6 |
| MT5 API router (connect, disconnect, account, positions) | Done | - | Sprint 6 |
| Auto trading router (start, stop, status) | Done | - | Sprint 6 |
| Safety router (kill switch, status) | Done | - | Sprint 6 |
| Signal execution through auto trader | Done | - | Sprint 6 |

### In Progress

| Task | Status | Assignee | Target |
|------|--------|----------|--------|
| WebSocket real-time updates | In Progress | - | Sprint 7 |

### Backlog

| Task | Status | Assignee | Target |
|------|--------|----------|--------|
| Real MT5 connection (non-simulation) | Backlog | - | Sprint 7 |
| Redis caching untuk OHLC data | Backlog | - | Sprint 7 |
| Performance optimization untuk indicator computation | Backlog | - | Sprint 7 |

---

## Sprint 5: Paper Trading & Analytics

### Completed

| Task | Status | Assignee | Selesai |
|------|--------|----------|---------|
| Virtual account management | Done | - | Sprint 5 |
| Position manager (open, close, modify) | Done | - | Sprint 5 |
| Trade journal (entry, exit, notes, tags) | Done | - | Sprint 5 |
| Performance analytics (win rate, drawdown, equity curve) | Done | - | Sprint 5 |
| Signal tracker (confusion matrix) | Done | - | Sprint 5 |
| Paper trading API router | Done | - | Sprint 5 |

---

## Sprint 4: Multi-Engine Integration

### Completed

| Task | Status | Assignee | Selesai |
|------|--------|----------|---------|
| Probability engine | Done | - | Sprint 4 |
| Statistical engine (win rate, combo analysis) | Done | - | Sprint 4 |
| Macro bias engine | Done | - | Sprint 4 |
| Final decision engine | Done | - | Sprint 4 |
| Unified signal generator | Done | - | Sprint 4 |
| Unified signal API endpoint | Done | - | Sprint 4 |
| Multi-timeframe confirmation | Done | - | Sprint 4 |

---

## Sprint 3: AI & Backtesting

### Completed

| Task | Status | Assignee | Selesai |
|------|--------|----------|---------|
| XGBoost model implementation | Done | - | Sprint 3 |
| LightGBM model implementation | Done | - | Sprint 3 |
| SHAP explainability | Done | - | Sprint 3 |
| ML pipeline (train, evaluate, predict) | Done | - | Sprint 3 |
| Feature pipeline (momentum, volatility, session) | Done | - | Sprint 3 |
| Backtesting engine | Done | - | Sprint 3 |
| Backtesting metrics (Sharpe, Sortino, drawdown) | Done | - | Sprint 3 |
| AI prediction API endpoint | Done | - | Sprint 3 |
| Model comparison endpoint (XGBoost vs LightGBM) | Done | - | Sprint 3 |
| Backtesting API endpoint | Done | - | Sprint 3 |

---

## Sprint 2: Analytical Engine

### Completed

| Task | Status | Assignee | Selesai |
|------|--------|----------|---------|
| Indicator calculator (RSI, MACD, EMA, SMA, ADX, ATR, BB) | Done | - | Sprint 2 |
| Market structure detector (swing highs/lows, BOS, CHOCH) | Done | - | Sprint 2 |
| FVG detector | Done | - | Sprint 2 |
| Liquidity sweep detector | Done | - | Sprint 2 |
| Support/resistance detector | Done | - | Sprint 2 |
| Signal generator (basic) | Done | - | Sprint 2 |
| Indicator API endpoint | Done | - | Sprint 2 |
| Market structure API endpoint | Done | - | Sprint 2 |
| Signal API endpoint | Done | - | Sprint 2 |
| Signal service | Done | - | Sprint 2 |

---

## Sprint 1: Foundation

### Completed

| Task | Status | Assignee | Selesai |
|------|--------|----------|---------|
| Project scaffold (monorepo structure) | Done | - | Sprint 1 |
| FastAPI application setup | Done | - | Sprint 1 |
| PostgreSQL + SQLAlchemy async setup | Done | - | Sprint 1 |
| Database models (Symbol, OHLC, Tick, News, Signal) | Done | - | Sprint 1 |
| Alembic migrations (initial + signals) | Done | - | Sprint 1 |
| Data collectors (Yahoo Finance, Polygon, Massive) | Done | - | Sprint 1 |
| Data collector manager with failover | Done | - | Sprint 1 |
| Celery setup (broker Redis) | Done | - | Sprint 1 |
| Periodic task (fetch OHLC every 5 min) | Done | - | Sprint 1 |
| Market data API (symbols, OHLC, ticker) | Done | - | Sprint 1 |
| Settings API (keys, preferences, risk, data sources) | Done | - | Sprint 1 |
| Dashboard scaffold (Next.js App Router) | Done | - | Sprint 1 |
| Dashboard sidebar navigation | Done | - | Sprint 1 |
| OHLC table component | Done | - | Sprint 1 |
| API client (lib/api.ts) | Done | - | Sprint 1 |
| Seed data (symbols) | Done | - | Sprint 1 |
| Docker Compose setup | Done | - | Sprint 1 |
| Environment configuration | Done | - | Sprint 1 |
| Common package (config, database) | Done | - | Sprint 1 |

---

## Sprint Planning Format

### Template untuk Sprint Baru

```markdown
## Sprint N: Nama Sprint

### Goals
- Goal 1
- Goal 2
- Goal 3

### Tasks

| Task | Priority | Est. Time | Status |
|------|----------|-----------|--------|
| Task description | High/Medium/Low | X hari | Pending/In Progress/Done |

### Definition of Done
- [ ] Kode sudah di-review
- [ ] Unit test lulus
- [ ] API documentation diupdate
- [ ] Migration sudah di-test (jika ada perubahan DB)
- [ ] Tidak ada type error (mypy lulus)
- [ ] Tidak ada lint error (ruff lulus)
```

---

## Future Tasks / Roadmap

### Short-term (Sprint 7-8)

| Task | Priority | Deskripsi |
|------|----------|-----------|
| WebSocket implementation | High | Real-time data streaming ke dashboard |
| Redis caching | High | Cache OHLC data untuk akses lebih cepat |
| Dashboard price chart (lightweight-charts) | Medium | Interactive candlestick chart |
| Dashboard signal history | Medium | Tabel riwayat sinyal dengan filter |
| Real MT5 connection | Medium | Ganti simulation dengan koneksi real |
| Unit tests coverage | High | Minimal 70% coverage |

### Medium-term (Sprint 9-10)

| Task | Priority | Deskripsi |
|------|----------|-----------|
| User authentication (JWT) | High | Login, register, API key management |
| Multi-user support | High | Setiap user punya akun virtual sendiri |
| Telegram bot notifications | Medium | Signal alerts via Telegram |
| Email report (daily/weekly) | Low | Performance report otomatis |
| Mobile-responsive dashboard | Low | Layout yang responsif di mobile |

### Long-term

| Task | Priority | Deskripsi |
|------|----------|-----------|
| Transformer model for price prediction | Medium | Deep learning model |
| Live trading mode | High | Eksekusi sinyal ke broker real |
| Risk analytics dashboard | Medium | Visualisasi risk metrics |
| Strategy marketplace | Low | Share dan download strategy |
| Multi-broker support | Low | cTrader, NinjaTrader, dll |
