# Development Plan — Market Data & Settings Pages

> Berdasarkan analisis halaman yang masih kosong (`market-data`, `settings`) 
> dan infrastruktur yang sudah ada di platform Al-Syaka Quant AI.

---

## 📊 Halaman 1: Market Data (`/market-data`)

### Visi
Pusat eksplorasi data pasar — melihat, menganalisis, dan mengexport data OHLC 
multi-symbol multi-timeframe secara real-time maupun historis.

### Fitur & Breakdown

#### Fase 1 — Data Explorer (Core) ⭐

| # | Fitur | Komponen Frontend | Backend | Estimasi |
|---|-------|-------------------|---------|----------|
| 1.1 | **Symbol Selector** — Dropdown dengan search, daftar pair favorit | `SymbolPicker.tsx` | `GET /api/v1/market/symbols` | ½ hari |
| 1.2 | **Timeframe Selector** — Tombol M1/M5/M15/M30/H1/H4/D1/W1 | `TimeframePicker.tsx` | — | ¼ hari |
| 1.3 | **Candlestick Chart** — Candlestick dengan volume, zoom/pan | `CandleChart.tsx` (Recharts or lightweight-charts) | `GET /api/v1/market/ohlc/{symbol}` | 1½ hari |
| 1.4 | **Data Range Picker** — Date range selector (7d, 30d, 1y, custom) | `DateRangePicker.tsx` | Query params `start`/`end` | ½ hari |
| 1.5 | **OHLC Table** — Tabel interaktif: Open, High, Low, Close, Volume, spread | `OHLCTable.tsx` | — | ½ hari |
| 1.6 | **Indicator Overlays** — Toggle SMA/EMA/Bollinger langsung di chart (reuse dari PriceChart) | Update `CandleChart.tsx` | `GET /api/v1/indicators/{symbol}` | ½ hari |

**Total Fase 1**: ~4 hari

#### Fase 2 — Multi-Symbol Dashboard

| # | Fitur | Komponen | Backend | Estimasi |
|---|-------|----------|---------|----------|
| 2.1 | **Watchlist Grid** — Grid 2×2 atau 3×2 mini chart multi-symbol | `WatchlistGrid.tsx` | Parallel fetch OHLC multi-symbol | 1 hari |
| 2.2 | **Price Ticker** — Running ticker harga实时 beberapa pair | `PriceTicker.tsx` | WebSocket / polling `GET /api/v1/market/ticker` | 1 hari |
| 2.3 | **Market Movers** — Pair dengan pergerakan terbesar hari ini | `MarketMovers.tsx` | Perhitungan dari OHLC D1 | ½ hari |
| 2.4 | **Economic Calendar** — Menampilkan news & event dari Investing | `EconCalendar.tsx` | `GET /api/v1/market/calendar` (Module 1) | 1½ hari |

**Total Fase 2**: ~4 hari

#### Fase 3 — Advanced Tools

| # | Fitur | Komponen | Backend | Estimasi |
|---|-------|----------|---------|----------|
| 3.1 | **Chart Patterns** — Deteksi pattern candlestick langsung di chart | `ChartPatterns.tsx` | `al_syaka_indicators` pattern detection | 1 hari |
| 3.2 | **Data Export** — Export CSV/JSON OHLC + indikator | `ExportButton.tsx` | `GET /api/v1/market/export/{symbol}` | ½ hari |
| 3.3 | **Comparison Mode** — Side-by-side compare 2+ symbol | `SymbolCompare.tsx` | Multi-fetch | 1 hari |
| 3.4 | **Session Overlay** — Tampilkan Asian/London/US session di chart | `SessionOverlay.tsx` | — | ½ hari |

**Total Fase 3**: ~3 hari

### Arsitektur Komponen Market Data

```
src/app/market-data/
├── page.tsx                    # Main page (orchestrator)
├── components/
│   ├── SymbolPicker.tsx        # Dropdown pencarian symbol
│   ├── TimeframePicker.tsx     # Tombol timeframe
│   ├── DateRangePicker.tsx     # Rentang tanggal
│   ├── CandleChart.tsx         # Candlestick chart (utama)
│   ├── OHLCTable.tsx           # Tabel data OHLC
│   ├── IndicatorOverlay.tsx    # Kontrol overlay indikator
│   ├── WatchlistGrid.tsx       # Grid multi-symbol
│   ├── PriceTicker.tsx         # Running ticker
│   ├── MarketMovers.tsx        # Pergerakan pasar
│   ├── EconCalendar.tsx        # Kalender ekonomi
│   └── ExportButton.tsx        # Export data
```

### API Endpoints Baru Diperlukan

```python
# Sudah ada:
GET /api/v1/market/ohlc/{symbol}     # OHLC data
GET /api/v1/market/health             # Connector health
GET /api/v1/indicators/{symbol}       # Indicators
GET /api/v1/indicators/{symbol}/features  # Features

# Perlu ditambahkan:
GET /api/v1/market/symbols            # List available symbols
GET /api/v1/market/ticker             # Current prices for all pairs
GET /api/v1/market/calendar           # Economic calendar events
GET /api/v1/market/export/{symbol}    # Export OHLC + indicators
```

---

## ⚙️ Halaman 2: Settings (`/settings`)

### Visi
Pusat konfigurasi platform — API keys, preferensi trading, risk management,
notifikasi, dan manajemen akun terpadu.

### Fitur & Breakdown

#### Fase 1 — Platform Configuration (Core) ⭐

| # | Fitur | Komponen Frontend | Backend | Estimasi |
|---|-------|-------------------|---------|----------|
| 1.1 | **API Keys Manager** — Input & simpan Polygon, Alpha Vantage, MT5 keys | `ApiKeysForm.tsx` | `POST /api/v1/settings/keys` | 1 hari |
| 1.2 | **Trading Preferences** — Default symbol, timeframe, account balance | `TradingPrefs.tsx` | `POST /api/v1/settings/preferences` | ½ hari |
| 1.3 | **Risk Defaults** — Default risk%, max position, max drawdown | `RiskDefaults.tsx` | `POST /api/v1/settings/risk` | ½ hari |
| 1.4 | **Theme Selector** — Dark/Light mode toggle + accent color | `ThemeSelector.tsx` | localStorage | ¼ hari |

**Total Fase 1**: ~2½ hari

#### Fase 2 — Advanced Configuration

| # | Fitur | Komponen | Backend | Estimasi |
|---|-------|----------|---------|----------|
| 2.1 | **Data Source Priority** — Urutan provider data (Yahoo > Alpha > Polygon) | `DataSourceConfig.tsx` | `POST /api/v1/settings/data-sources` | ½ hari |
| 2.2 | **Notification Settings** — Alert untuk signal, SL/TP, error | `NotificationConfig.tsx` | — | ½ hari |
| 2.3 | **Auto Trading Defaults** — Min confidence, max daily trades, allowed symbols | `AutoTradeConfig.tsx` | `POST /api/v1/settings/auto-trade` | ½ hari |
| 2.4 | **Account Management** — Reset paper trading, view account history | `AccountManage.tsx` | `POST /api/v1/paper-trading/reset` | ¼ hari |

**Total Fase 2**: ~1¾ hari

#### Fase 3 — System Management

| # | Fitur | Komponen | Backend | Estimasi |
|---|-------|----------|---------|----------|
| 3.1 | **Database Status** — Tabel stats, row count, last update | `DbStatus.tsx` | `GET /api/v1/settings/db-status` | ½ hari |
| 3.2 | **Logs Viewer** — System logs & error history | `LogsViewer.tsx` | `GET /api/v1/settings/logs` | ½ hari |
| 3.3 | **Model Management** — Lihat trained models, trigger re-training | `ModelManager.tsx` | `POST /api/v1/ai/train` | ½ hari |
| 3.4 | **About / System Info** — Version, uptime, dependencies | `SystemInfo.tsx` | `GET /api/v1/settings/system-info` | ¼ hari |

**Total Fase 3**: ~1¾ hari

### Arsitektur Komponen Settings

```
src/app/settings/
├── page.tsx                    # Main page with tabs/sections
├── components/
│   ├── SettingsSidebar.tsx     # Navigasi section settings
│   ├── sections/
│   │   ├── ApiKeysSection.tsx      # API Keys
│   │   ├── TradingPrefsSection.tsx # Preferensi trading
│   │   ├── RiskSection.tsx         # Risk management
│   │   ├── DataSourceSection.tsx   # Data provider priority
│   │   ├── NotificationSection.tsx # Notifikasi
│   │   ├── AutoTradeSection.tsx    # Auto trading config
│   │   ├── AccountSection.tsx      # Account management
│   │   ├── SystemSection.tsx       # System info & logs
│   │   └── AboutSection.tsx        # About
```

### API Endpoints Baru Diperlukan

```python
# Perlu dibuat:
GET/POST /api/v1/settings/keys            # API Keys CRUD
GET/POST /api/v1/settings/preferences     # Trading preferences
GET/POST /api/v1/settings/risk            # Risk defaults
GET/POST /api/v1/settings/data-sources    # Data source priority
GET/POST /api/v1/settings/auto-trade      # Auto trading config
GET     /api/v1/settings/db-status        # Database statistics
GET     /api/v1/settings/logs             # System logs
GET     /api/v1/settings/system-info      # Version & info
```

---

## 📋 Prioritasi & Timeline

| Fase | Halaman | Prioritas | Estimated Duration |
|------|---------|-----------|-------------------|
| **Fase 1** | Market Data — Data Explorer | 🔴 **High** | ~4 hari |
| **Fase 1** | Settings — Platform Config | 🔴 **High** | ~2½ hari |
| **Fase 2** | Market Data — Multi-Symbol | 🟡 **Medium** | ~4 hari |
| **Fase 2** | Settings — Advanced Config | 🟡 **Medium** | ~1¾ hari |
| **Fase 3** | Market Data — Advanced Tools | 🟢 **Low** | ~3 hari |
| **Fase 3** | Settings — System Management | 🟢 **Low** | ~1¾ hari |

### Rekomendasi Eksekusi

```
Minggu 1: Market Data Fase 1 + Settings Fase 1  (6½ hari)
Minggu 2: Market Data Fase 2 + Settings Fase 2  (5¾ hari)
Minggu 3: Market Data Fase 3 + Settings Fase 3  (4¾ hari)
```

---

## 🔧 Dependencies & Prerequisites

Sebelum memulai, pastikan:

1. **Database PostgreSQL running** — `docker compose -f docker/docker-compose.yml up -d`
2. **Yahoo Finance connector berfungsi** — sudah terinstall `yfinance`
3. **API server running** — `uv run uvicorn src.main:app --reload`
4. **Frontend dev server** — `pnpm dev`

---

## 🚀 Mulai Eksekusi?

Fase pertama yang akan kita kerjakan:

### Market Data Fase 1 (Prioritas Tertinggi)
1. **CandleChart.tsx** — Candlestick chart dengan lightweight-charts
2. **SymbolPicker.tsx** — Pencarian & pilih pair
3. **OHLCTable.tsx** — Data interaktif
4. **IndicatorOverlay.tsx** — Overlay indikator di chart
5. **API**: `GET /api/v1/market/symbols`

### Settings Fase 1
1. **Settings layout** — Tab/sidebar navigasi
2. **ApiKeysSection** — Form API keys
3. **TradingPrefsSection** — Default preferences
4. **API**: Settings CRUD endpoints
