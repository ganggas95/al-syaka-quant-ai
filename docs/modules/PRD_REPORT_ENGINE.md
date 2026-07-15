# Report Engine

## Ringkasan

Report Engine (dalam tahap perencanaan) akan menyediakan kemampuan reporting dan performance analytics yang komprehensif. Engine ini akan menghasilkan laporan periodik untuk evaluasi strategi trading, kinerja portfolio, dan analisis mendalam.

---

## Status Saat Ini

Saat ini, fungsionalitas reporting dasar sudah tersedia melalui:

### Backtest Report

Backtest API endpoint sudah menghasilkan ringkasan lengkap dari hasil backtest.

**Endpoint**: `POST /api/v1/backtesting/run`

**Metrik yang Dihasilkan**:
| Metrik | Deskripsi |
|--------|-----------|
| total_trades | Total trade yang dieksekusi |
| win_rate | Persentase trade menang |
| net_profit | Profit bersih |
| profit_factor | Rasio total profit / total loss |
| sharpe_ratio | Return yang disesuaikan risiko |
| sortino_ratio | Downside risk-adjusted return |
| max_drawdown_percent | Drawdown maksimum dari puncak |
| max_consecutive_wins/losses | Run terpanjang |
| avg_win / avg_loss | Rata-rata profit/loss per trade |

**Contoh Output**:
```json
{
    "config": { ... },
    "metrics": {
        "total_trades": 120,
        "winning_trades": 72,
        "losing_trades": 48,
        "win_rate": 60.0,
        "net_profit": 1520.50,
        "profit_factor": 1.85,
        "sharpe_ratio": 1.32,
        "sortino_ratio": 1.78,
        "max_drawdown_percent": 8.5,
        "best_trade": 85.20,
        "worst_trade": -45.30
    },
    "summary": "...",
    "trades": [...]
}
```

### Performance Analytics

**File**: `apps/api/src/paper_trading/analytics.py`

Analitik performa untuk paper trading dengan breakdown:

**Endpoint**: `GET /api/v1/paper-trading/analytics`

**Analytics Output**:
```python
{
    "overall": {
        "total_trades": int,
        "winning_trades": int,
        "losing_trades": int,
        "win_rate": float,
        "net_profit": float,
        "profit_factor": float,
        "avg_win": float,
        "avg_loss": float
    },
    "by_pair": {
        "EURUSD": {"wins": 12, "losses": 5, "win_rate": 70.6},
        ...
    },
    "by_session": {
        "london": {"wins": 15, "losses": 8, "win_rate": 65.2},
        ...
    },
    "drawdown": {
        "max_drawdown": float,
        "max_drawdown_percent": float
    },
    "monthly_returns": {
        "2026-01": 2.5,
        ...
    },
    "equity_curve": [10000, 10050, ...]
}
```

### Signal Tracker (Confusion Matrix)

**File**: `apps/api/src/paper_trading/signal_tracker.py`

Melacak performa sinyal dengan confusion matrix dan accuracy by confidence bucket.

**Endpoint**: `GET /api/v1/paper-trading/signal-performance`

**Output**:
```python
{
    "total_signals": 50,
    "resolved_signals": 40,
    "pending_signals": 10,
    "confusion_matrix": {
        "true_positives": 15,
        "false_positives": 8,
        "true_negatives": 12,
        "false_negatives": 5,
        "total_signals": 40,
        "accuracy": 67.5,
        "precision": 65.2,
        "recall": 75.0,
        "f1_score": 69.8
    },
    "accuracy_by_confidence": {
        "90-100%": {"total": 5, "accuracy": 80.0},
        "80-89%": {"total": 12, "accuracy": 75.0},
        "70-79%": {"total": 15, "accuracy": 66.7},
        "60-69%": {"total": 8, "accuracy": 50.0},
        "50-59%": {"total": 0, "accuracy": 0}
    }
}
```

---

## Rencana Pengembangan Report Engine

### 1. Backtest Report Generation

Laporan hasil backtest yang lebih detail dan visual.

**Fitur Rencana**:
- **PDF Report** -- Laporan PDF yang dapat di-download, mencakup:
  - Ringkasan eksekutif.
  - Tabel metrik performa.
  - Equity curve chart.
  - Drawdown chart.
  - Monthly returns heatmap.
  - Trade list dengan detail.
  - Risk metrics breakdown.
- **HTML Report** -- Laporan interaktif dengan chart JavaScript.
- **CSV Export** -- Data mentah untuk analisis lebih lanjut.

### 2. Signal Performance Report

Laporan periodik performa sinyal.

**Fitur Rencana**:
- **Daily Signal Summary** -- Ringkasan sinyal harian.
- **Weekly/Monthly Report** -- Laporan periodik dengan tren.
- **Accuracy Trend** -- Tren akurasi sinyal dari waktu ke waktu.
- **Best/Worst Performers** -- Symbol dengan performa terbaik/terburuk.
- **Confidence Calibration** -- Kalibrasi confidence vs actual outcome.

### 3. Portfolio Report

Laporan performa portfolio komprehensif.

**Fitur Rencana**:
- **Portfolio Snapshot** -- Ringkasan portfolio saat ini.
- **Return Attribution** -- Breakdown return per symbol.
- **Risk Attribution** -- Breakdown risiko per symbol.
- **Correlation Matrix** -- Matriks korelasi antar symbol.
- **Diversification Score** -- Skor diversifikasi portfolio.

### 4. Scheduled Reporting

Laporan otomatis yang dikirim secara periodik.

**Fitur Rencana**:
- **Daily Email Report** -- Ringkasan harian.
- **Weekly Performance Review** -- Review performa mingguan.
- **Monthly Strategy Evaluation** -- Evaluasi strategi bulanan.
- **Custom Schedule** -- Jadwal kustom sesuai preferensi.

### 5. Report Dashboard

Visualisasi interaktif untuk semua laporan.

**Fitur Rencana**:
- **Interactive Charts** -- Chart interaktif dengan filtering.
- **Date Range Picker** -- Pilih rentang waktu.
- **Export Button** -- Download laporan dalam berbagai format.
- **Comparison Mode** -- Bandingkan periode atau strategi.

---

## Integrasi dengan Dashboard

Report Engine akan terintegrasi dengan dashboard Next.js:

```typescript
// Halaman yang direncanakan
/signals          -- Signal performance report
/backtesting      -- Backtest results & reports
/paper-trading    -- Portfolio & performance analytics
/reports          -- Report center (scheduled & generated)
```

Komponen dashboard yang sudah ada:
- `stats-card.tsx` -- Kartu statistik.
- `export-button.tsx` -- Tombol export data.
- `mini-chart.tsx` -- Mini chart untuk sparklines.
- `candle-chart.tsx` -- Candlestick chart dengan lightweight-charts.
