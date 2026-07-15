# Backtest Engine

## Ringkasan

Backtest Engine menguji strategi trading pada data historis untuk mengevaluasi kinerja sebelum digunakan pada akun real. Engine ini menyediakan simulasi trading yang realistis dengan konfigurasi yang fleksibel.

Package: `apps/backtester/src/al_syaka_backtester/`

---

## Komponen

### TradeRecord

**File**: `apps/backtester/src/al_syaka_backtester/trade.py`

Data class yang merekam setiap trade dalam backtest.

```python
@dataclass
class TradeRecord:
    entry_time: datetime
    exit_time: Optional[datetime] = None
    signal: str = ""           # BUY/SELL
    entry_price: float = 0.0
    exit_price: Optional[float] = None
    stop_loss: float = 0.0
    take_profit: float = 0.0
    lot_size: float = 0.01
    direction: str = ""        # LONG/SHORT
    result: str = ""           # WIN/LOSS/PENDING
    pips: float = 0.0
    profit: float = 0.0
    profit_percent: float = 0.0
    confidence: float = 0.0
    reasons: list[str] = field(default_factory=list)
    exit_reason: str = ""      # TP_HIT, SL_HIT, END_OF_DATA
```

---

### BacktestConfig

**File**: `apps/backtester/src/al_syaka_backtester/engine.py`

Konfigurasi untuk menjalankan backtest.

```python
@dataclass
class BacktestConfig:
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10_000
    risk_per_trade: float = 0.01      # 1% per trade
    atr_sl_multiplier: float = 1.5    # ATR multiplier untuk SL
    atr_tp_multiplier: float = 3.0    # ATR multiplier untuk TP
    min_confidence: float = 0.55      # Minimum confidence untuk entry
```

---

### BacktestEngine

**File**: `apps/backtester/src/al_syaka_backtester/engine.py`

Engine utama yang menjalankan simulasi trading.

```python
class BacktestEngine:
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trades: list[TradeRecord] = []
        self.equity_curve: list[float] = [config.initial_balance]
        self.balance = config.initial_balance
        self.peak_balance = config.initial_balance
```

**Alur Eksekusi**:

1. **Inisialisasi**: Siapkan data OHLC, urutkan berdasarkan timestamp.
2. **Looping Data**: Iterasi setiap baris data mulai dari index 100 (butuh data untuk indikator).
3. **Komputasi Indikator**: Hitung EMA, RSI, ATR untuk window data saat ini.
4. **Update Posisi Terbuka**: Cek apakah SL/TP kena untuk posisi yang sedang terbuka.
5. **Cek Sinyal**: Jika tidak ada posisi terbuka, cek kondisi entry.
6. **Open Trade**: Jika sinyal terdeteksi, buka posisi baru dengan SL/TP.
7. **Track Equity**: Catat equity curve setiap baris.
8. **Close Remaining**: Tutup posisi tersisa di akhir data.

**Signal Logic** (saat ini):
- BUY: EMA12 > EMA50 (bullish cross) + RSI 30-60 + RSI naik.
- SELL: EMA12 < EMA50 (bearish cross) + RSI 40-70 + RSI turun.
- Confidence: 0.6-0.9 berdasarkan posisi RSI.

**Entry/Exit**:
- Entry: Close price pada baris sinyal.
- Stop Loss: ATR * 1.5 dari entry.
- Take Profit: ATR * 3.0 dari entry.
- Position Size: `balance * risk_per_trade / (sl_pips * pip_value)`.

---

### MetricsCalculator

**File**: `apps/backtester/src/al_syaka_backtester/metrics.py`

Kalkulator metrik performa komprehensif.

```python
@dataclass
class BacktestMetrics:
    # Core stats
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float

    # Profitability
    total_profit: float
    total_loss: float
    net_profit: float
    profit_factor: float
    avg_profit_per_trade: float
    avg_win: float
    avg_loss: float
    max_consecutive_wins: int
    max_consecutive_losses: int

    # Risk metrics
    max_drawdown: float
    max_drawdown_percent: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float

    # Time metrics
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    total_days: int

    # Trade distribution
    best_trade: float
    worst_trade: float
    avg_bars_held: float

    # Monthly/yearly breakdown
    monthly_returns: dict
    yearly_returns: dict
```

**Metrik yang Dihitung**:

| Metrik | Formula | Deskripsi |
|--------|---------|-----------|
| Win Rate | winning / total | Persentase trade menang |
| Profit Factor | total_profit / total_loss | Rasio keuntungan terhadap kerugian |
| Sharpe Ratio | sqrt(252) * mean(return) / std(return) | Return yang disesuaikan risiko |
| Sortino Ratio | sqrt(252) * mean(return) / std(neg_return) | Hanya mempertimbangkan downside risk |
| Calmar Ratio | annual_return / max_drawdown | Return terhadap drawdown maksimum |
| Max Drawdown | max(peak - trough) | Penurunan maksimum dari puncak |
| Avg Bars Held | mean(holding_period) | Rata-rata waktu menahan posisi |

---

## API Endpoint

### Run Backtest

```
POST /api/v1/backtesting/run
    ?symbol=EURUSD
    &timeframe=H1
    &days=365
    &initial_balance=10000
    &risk_percent=1.0
```

**Response**:
```json
{
    "config": {
        "symbol": "EURUSD",
        "timeframe": "H1",
        "period_days": 365,
        "initial_balance": 10000
    },
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
        "max_consecutive_wins": 8,
        "max_consecutive_losses": 4
    },
    "summary": "Backtest completed: 120 trades | Win Rate: 60.0% | Net Profit: $1,520.50 | ...",
    "trades": [
        {
            "entry_time": "2025-01-15T08:00:00",
            "exit_time": "2025-01-15T12:00:00",
            "signal": "BUY",
            "entry": 1.0850,
            "exit": 1.0875,
            "result": "WIN",
            "pips": 25.0,
            "profit": 25.00,
            "exit_reason": "TP_HIT"
        }
    ]
}
```

---

## Rencana Pengembangan

- [ ] **Parameter Optimization**: Grid search untuk parameter optimal (ATR multiplier, risk per trade).
- [ ] **Walk-Forward Analysis**: Validasi strategi dengan walk-forward optimization.
- [ ] **Multi-Symbol Backtest**: Backtest pada portfolio multi-symbol.
- [ ] **Monte Carlo Simulation**: Simulasi Monte Carlo untuk distribusi hasil.
- [ ] **Strategy Comparison**: Perbandingan multiple strategies dalam satu run.
- [ ] **Export Report**: Generate report PDF/HTML dari hasil backtest.
