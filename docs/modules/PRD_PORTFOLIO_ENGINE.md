# Portfolio Engine

## Ringkasan

Portfolio Engine (dalam tahap perencanaan) akan mengelola trading multi-symbol dengan alokasi risiko yang optimal. Engine ini memungkinkan trader untuk memonitor dan mengelola portfolio yang terdiri dari beberapa instrumen secara simultan.

---

## Status Saat Ini

Saat ini, fungsionalitas portfolio dasar sudah tersedia melalui **Paper Trading** system yang mencakup:

### VirtualAccount

**File**: `apps/api/src/paper_trading/virtual_account.py`

Manajemen akun virtual dengan tracking balance, equity, dan history.

**Fitur**:
- Initial balance konfigurasi.
- Track balance, floating P&L, equity.
- Record snapshots periodik untuk equity curve.
- Apply trade results (win/loss).

### PositionManager

**File**: `apps/api/src/paper_trading/position.py`

Manajemen posisi multi-symbol.

**Fitur**:
- Open/close positions untuk multiple symbols.
- Track SL/TP untuk setiap posisi.
- Hitung floating P&L dan realized P&L.
- Batasi maksimum posisi per symbol.

### TradeJournal

**File**: `apps/api/src/paper_trading/journal.py`

Jurnal trading untuk mencatat semua aktivitas.

**Fitur**:
- Entry dan exit journal untuk setiap trade.
- Tags dan notes untuk kategorisasi.
- Filter by symbol, direction, result.
- Recent entries query.

### PerformanceAnalytics

**File**: `apps/api/src/paper_trading/analytics.py`

Analitik performa untuk portfolio.

**Fitur**:
- Overall stats (total trades, win rate, profit).
- Win rate by pair (per symbol).
- Win rate by session (Asian, London, US).
- Drawdown analysis.
- Monthly returns breakdown.
- Equity curve.

---

## Rencana Pengembangan Portfolio Engine

### 1. Multi-Symbol Risk Allocation

Alokasi risiko yang optimal ketika trading multiple symbols secara bersamaan.

**Fitur Rencana**:
- Risk budgeting berdasarkan volatilitas per symbol.
- Correlation matrix untuk menghindari overexposure pada aset berkorelasi.
- Dynamic leverage adjustment berdasarkan portfolio risk.
- Maximum exposure limit per sector/asset class.

### 2. Portfolio Rebalancing

Rebalancing otomatis berdasarkan target alokasi.

**Fitur Rencana**:
- Target allocation configuration.
- Threshold-based rebalancing triggers.
- Rebalancing cost consideration.

### 3. Portfolio Metrics

Metrik performa portfolio yang komprehensif.

**Fitur Rencana**:
- Portfolio Sharpe dan Sortino ratio.
- Correlation matrix antar symbol.
- Value at Risk (VaR) dan Conditional VaR.
- Portfolio beta dan diversification score.
- Maximum sector exposure.

### 4. Integration dengan Signal Engine

Sinyal dari Unified Signal Generator akan dipertimbangkan dalam konteks portfolio:

- **Position Sizing** -- Ukuran posisi disesuaikan dengan risiko portfolio saat ini.
- **Symbol Selection** -- Hanya symbol dengan sinyal terbaik yang di-trade.
- **Risk Override** -- Portfolio risk limit dapat override individual position sizing.

---

## API Endpoints (Saat Ini)

### Paper Trading

```
GET  /api/v1/paper-trading/account           -- Ringkasan akun
POST /api/v1/paper-trading/positions/open    -- Buka posisi baru
POST /api/v1/paper-trading/positions/close   -- Tutup posisi
GET  /api/v1/paper-trading/positions         -- Daftar posisi
GET  /api/v1/paper-trading/journal           -- Jurnal trading
GET  /api/v1/paper-trading/analytics         -- Analitik performa
GET  /api/v1/paper-trading/signal-performance -- Performa sinyal
POST /api/v1/paper-trading/reset             -- Reset akun
```

### Performance Analytics Response

```json
{
    "overall": {
        "total_trades": 45,
        "winning_trades": 28,
        "losing_trades": 17,
        "win_rate": 62.2,
        "net_profit": 1250.50,
        "profit_factor": 1.85,
        "avg_win": 85.30,
        "avg_loss": -45.20
    },
    "by_pair": {
        "EURUSD": {"wins": 12, "losses": 5, "win_rate": 70.6},
        "GBPUSD": {"wins": 8, "losses": 7, "win_rate": 53.3},
        "XAUUSD": {"wins": 8, "losses": 5, "win_rate": 61.5}
    },
    "by_session": {
        "london": {"wins": 15, "losses": 8, "win_rate": 65.2},
        "us": {"wins": 10, "losses": 6, "win_rate": 62.5},
        "asian": {"wins": 3, "losses": 3, "win_rate": 50.0}
    },
    "drawdown": {
        "max_drawdown": 350.00,
        "max_drawdown_percent": 3.5
    },
    "monthly_returns": {
        "2026-01": 2.5,
        "2026-02": -1.2,
        "2026-03": 3.8
    },
    "equity_curve": [10000, 10050, 10020, ...]
}
```

---

## Signal Tracker (Integrasi Portfolio)

**File**: `apps/api/src/paper_trading/signal_tracker.py`

Melacak performa sinyal trading dengan confusion matrix.

**Fitur**:
- Record setiap sinyal yang dihasilkan.
- Resolve signal saat posisi ditutup (WIN/LOSS).
- Confusion matrix (TP, FP, TN, FN).
- Accuracy by confidence bucket.
- Signal performance summary.

Confusion matrix digunakan untuk mengevaluasi kualitas sinyal dan menyesuaikan strategi.
