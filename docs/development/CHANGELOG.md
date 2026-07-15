# Changelog Al-Syaka Quant AI

Semua perubahan signifikan pada project ini akan dicatat di dokumen ini.

Format mengacu pada [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), dan project ini menggunakan [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.3.0] - 2026-07-14

### Added

- **MT5 Bridge:** Koneksi ke MetaTrader 5 (mode simulasi untuk macOS)
- **Order Manager:** Place, close, dan modify order melalui API
- **Auto Trading Engine:** Eksekusi sinyal otomatis ke MT5
- **Safety System:** Kill switch, max daily trades, max drawdown protection
- **MT5 API Router:** Endpoints untuk connect, disconnect, account info, positions, orders
- **Signal Execution:** Eksekusi sinyal trading melalui auto trader dengan validasi

### Changed

- Versi API diupdate ke 0.3.0
- Informasi sprint di system info: "Sprint 6 - MT5 Bridge & Auto Trading"

---

## [0.2.0] - 2026-07-13

### Added

- **Paper Trading:** Virtual account dengan initial balance
- **Position Manager:** Open, close, dan track posisi virtual
- **Trade Journal:** Catatan entry/exit dengan notes, tags, dan reasons
- **Performance Analytics:** Win rate, equity curve, drawdown analysis, monthly returns
- **Signal Tracker:** Confusion matrix untuk tracking performa sinyal
- **Probability Engine:** Menghitung probabilitas arah harga dari indikator dan struktur pasar
- **Statistical Engine:** Win rate analysis, combo analysis
- **Macro Bias Engine:** Analisis bias makro dari multi-timeframe trend
- **Final Decision Engine:** Konflik deteksi antara sinyal teknikal dan makro
- **Unified Signal Generator:** Integrasi semua engine dalam satu pipeline
- **Unified Signal API:** Endpoint `/api/v1/unified-signal/{symbol}` dengan response komprehensif
- **Multi-Timeframe Confirmation:** Analisis H1, H4, D1 dalam satu sinyal
- **Composite Score:** Scoring dari market structure, momentum, trend, volatility, dan AI
- **Market Regime Detection:** TRENDING, REVERSAL, RANGE, VOLATILE
- **Quant Strategy Signal:** Integrasi Mean Reversion Strategy
- **Paper Trading API:** Endpoints untuk account, positions, journal, analytics, signal performance

### Changed

- Versi API diupdate ke 0.2.0
- Informasi sprint: "Analytical Engine"

---

## [0.1.1] - 2026-07-12

### Added

- **Market Structure Detector:** Swing highs/lows, Break of Structure (BOS), Change of Character (CHOCH)
- **FVG Detector:** Fair Value Gap detection (bullish dan bearish)
- **Liquidity Sweep Detector:** Buy-side dan sell-side liquidity sweep
- **Support/Resistance Detector:** Level support dan resistance berdasarkan touch count
- **Signals Table Migration:** Migration untuk tabel signals dengan outcome tracking
- **Signal Generator:** Integrasi probability engine + risk manager + market structure
- **Signal Service:** Layer bisnis untuk pembangkitan sinyal

### Changed

- Signal API endpoint sekarang menghasilkan sinyal lengkap dengan entry, SL, TP
- Response signal mencakup trade quality dan risk level

---

## [0.1.0] - 2026-07-11

### Added

- **Project Scaffold:** Struktur monorepo dengan apps/ dan packages/
- **FastAPI Application:** Setup FastAPI dengan lifespan, CORS, GZip middleware
- **Database Setup:** PostgreSQL + SQLAlchemy async engine
- **Database Models:** Symbol, OHLC, Tick, News dengan relationship dan indexes
- **Alembic Migration:** Initial migration untuk 4 tabel (symbols, ohlc, ticks, news)
- **Data Collectors:** Yahoo Finance connector, Polygon.io connector, Massive connector
- **Data Collector Manager:** Multi-provider dengan failover mechanism
- **Celery Setup:** Worker configuration dengan Redis broker
- **Periodic Task:** Fetch OHLC data setiap 5 menit
- **Settings API:** Endpoints untuk API keys, preferences, risk config, data sources, auto trade
- **Market Data API:** Endpoints untuk symbols, OHLC, ticker
- **Health Check:** System health endpoint
- **Dashboard Scaffold:** Next.js 14 App Router dengan dark theme
- **Sidebar Navigation:** Navigasi sidebar dengan link ke semua halaman
- **OHLC Table Component:** Tabel data OHLC di dashboard
- **API Client:** TypeScript API client di lib/api.ts
- **Seed Data:** Script untuk symbols forex (EURUSD, GBPUSD, USDJPY, dll)
- **Docker Compose:** PostgreSQL + Redis untuk development
- **Environment Configuration:** .env.example dengan semua konfigurasi
- **Common Package:** Shared config (pydantic-settings), database engine, base models
- **Documentation:** Dokumentasi awal project

### Notes

- Versi awal project, foundation untuk semua fitur selanjutnya
- Sprint: "Sprint 1 - Foundation"
- Dokumentasi interaktif tersedia di /docs (Swagger UI)

---

## Format Catatan

Setiap entry harus mengikuti format:

```
## [versi] - tanggal

### Added
- Fitur baru

### Changed
- Perubahan pada fitur existing

### Deprecated
- Fitur yang akan dihapus

### Removed
- Fitur yang dihapus

### Fixed
- Bug fixes

### Security
- Perbaikan keamanan
```
