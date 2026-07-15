# Spesifikasi API Al-Syaka Quant AI

## Informasi Umum

**Base URL:** `http://localhost:8000`

**Dokumentasi Interaktif:** `http://localhost:8000/docs` (Swagger UI)

**Versi API:** 0.3.0

**Deskripsi:** Al-Syaka Quant AI adalah platform kecerdasan pasar berbasis AI yang menyediakan analisis teknikal, prediksi machine learning, deteksi struktur pasar, backtesting, paper trading, dan integrasi dengan MetaTrader 5.

---

## Autentikasi

Saat ini API berjalan tanpa autentikasi untuk pengembangan lokal. Di production, rencananya akan menggunakan JWT token.

### CORS

CORS dikonfigurasi untuk mengizinkan semua origin selama pengembangan:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Middleware

- **GZip Middleware:** Kompresi respons untuk ukuran di atas 1000 bytes.

---

## Endpoints

### 1. Market Data

**Prefix:** `/api/v1/market`

#### GET /api/v1/market/symbols
Mengembalikan daftar semua simbol trading yang tersedia.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| active_only | bool | true | Filter hanya simbol aktif |

**Response:**
```json
{
  "count": 10,
  "symbols": [
    {
      "id": 1,
      "name": "EURUSD",
      "base": "EUR",
      "quote": "USD",
      "pip_size": 0.0001,
      "contract_size": 100000,
      "active": true
    }
  ]
}
```

#### GET /api/v1/market/ticker
Mengembalikan harga terkini untuk semua simbol aktif.

**Response:**
```json
{
  "tickers": [
    {
      "symbol": "EURUSD",
      "bid": 1.0850,
      "ask": 1.0850,
      "high": 1.0870,
      "low": 1.0830,
      "change": 0.15,
      "volume": 1234
    }
  ],
  "count": 10
}
```

#### GET /api/v1/market/ohlc/{symbol}
Mengembalikan data OHLC (Open, High, Low, Close) untuk suatu simbol.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | path | - | Nama simbol (EURUSD, GBPUSD, dll) |
| timeframe | query | H1 | M1, M5, M15, M30, H1, H4, D1 |
| limit | query | 100 | Maksimal 1000 bar |

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "count": 100,
  "data": [
    {
      "timestamp": "2026-07-15T00:00:00",
      "open": 1.0850,
      "high": 1.0870,
      "low": 1.0830,
      "close": 1.0860,
      "volume": 1234
    }
  ]
}
```

#### GET /api/v1/market/health
Memeriksa kesehatan semua konektor data.

**Response:**
```json
{
  "yahoo": "connected",
  "polygon": "not_configured",
  "massive": "not_configured"
}
```

---

### 2. Signals

**Prefix:** `/api/v1/signals`

#### GET /api/v1/signals/{symbol}
Menghasilkan sinyal trading lengkap untuk suatu simbol.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | path | - | Nama simbol |
| timeframe | query | H1 | M1, M5, M15, M30, H1, H4, D1 |
| account_balance | query | 10000 | Saldo akun untuk position sizing |

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "timestamp": "2026-07-15T10:00:00",
  "signal": "BUY",
  "confidence": 75.0,
  "entry": 1.0860,
  "stop_loss": 1.0830,
  "take_profit": 1.0920,
  "risk_reward": 2.0,
  "lot_size": 0.1,
  "risk_level": "MEDIUM",
  "trade_quality": "GOOD",
  "reasons": ["RSI oversold bounce", "Bullish MACD crossover"],
  "indicators_used": ["RSI", "MACD", "EMA 12", "EMA 50"]
}
```

#### GET /api/v1/signals/
Informasi cara penggunaan endpoint signals.

---

### 3. Indicators

**Prefix:** `/api/v1/indicators`

#### GET /api/v1/indicators/{symbol}
Menghitung semua indikator teknikal untuk suatu simbol.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | path | - | Nama simbol |
| timeframe | query | H1 | Timeframe |
| limit | query | 200 | Maksimal 1000 |

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "timestamps": ["2026-07-15T00:00:00"],
  "ohlc": {
    "open": [1.0850],
    "high": [1.0870],
    "low": [1.0830],
    "close": [1.0860],
    "volume": [1234]
  },
  "indicators": {
    "rsi_14": [55.2],
    "ema_12": [1.0855],
    "ema_20": [1.0845],
    "ema_50": [1.0820],
    "sma_200": [1.0700],
    "macd_macd": [0.0005],
    "macd_signal": [0.0003],
    "adx_adx": [28.0],
    "atr_14": [0.0020],
    "bb_upper": [1.0900],
    "bb_lower": [1.0800],
    "bb_middle": [1.0850]
  }
}
```

#### GET /api/v1/indicators/{symbol}/features
Menghitung feature engineering (teknikal lanjutan) untuk suatu simbol.

**Parameters:** Sama dengan di atas.

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "timestamps": [],
  "features": {
    "momentum_1h": [0.5],
    "volatility_1h": [0.002],
    "session_asia": [true]
  }
}
```

---

### 4. Market Structure

**Prefix:** `/api/v1/market-structure`

#### GET /api/v1/market-structure/{symbol}
Analisis struktur pasar lengkap termasuk BOS, CHOCH, FVG, dan likuiditas.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | path | - | Nama simbol |
| timeframe | query | H1 | Timeframe |
| limit | query | 200 | Maksimal 1000 |

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "current_trend": "BULLISH",
  "swing_highs": [
    {"index": 50, "price": 1.0900, "label": "HH"},
    {"index": 30, "price": 1.0870, "label": "LH"}
  ],
  "swing_lows": [
    {"index": 40, "price": 1.0840, "label": "HL"},
    {"index": 20, "price": 1.0820, "label": "LL"}
  ],
  "break_of_structure": [
    {"type": "BOS", "index": 45, "price": 1.0880}
  ],
  "change_of_character": [
    {"type": "CHOCH", "index": 35, "price": 1.0860}
  ],
  "fair_value_gaps": [
    {"type": "BULLISH_FVG", "index": 25, "gap_high": 1.0855, "gap_low": 1.0845}
  ],
  "liquidity_sweeps": [
    {"type": "BUY_SIDE", "index": 48, "swept_level": 1.0890}
  ],
  "support_resistance": {
    "resistances": [{"price": 1.0900, "touches": 3}],
    "supports": [{"price": 1.0800, "touches": 4}]
  }
}
```

---

### 5. Backtesting

**Prefix:** `/api/v1/backtesting`

#### POST /api/v1/backtesting/run
Menjalankan backtest pada data historis.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | query | EURUSD | Simbol |
| timeframe | query | H1 | Timeframe |
| days | query | 365 | Hari data historis (maks 5 tahun) |
| initial_balance | query | 10000 | Saldo awal |
| risk_percent | query | 1.0 | Risiko per trade (%) |

**Response:**
```json
{
  "config": {
    "symbol": "EURUSD",
    "timeframe": "H1",
    "period_days": 365,
    "initial_balance": 10000
  },
  "metrics": {
    "total_trades": 150,
    "winning_trades": 90,
    "losing_trades": 60,
    "win_rate": 60.0,
    "net_profit": 2500.50,
    "profit_factor": 1.85,
    "avg_profit_per_trade": 16.67,
    "avg_win": 45.20,
    "avg_loss": -30.10,
    "max_drawdown": 800.00,
    "max_drawdown_percent": 8.0,
    "sharpe_ratio": 1.35,
    "sortino_ratio": 1.80,
    "calmar_ratio": 0.85,
    "max_consecutive_wins": 8,
    "max_consecutive_losses": 5,
    "best_trade": 250.00,
    "worst_trade": -120.00
  },
  "summary": "Backtest completed: 150 trades | Win Rate: 60.0% | Net Profit: $2,500.50",
  "trades": [
    {
      "entry_time": "2026-01-15T08:00:00",
      "exit_time": "2026-01-15T20:00:00",
      "signal": "BUY",
      "direction": "LONG",
      "entry": 1.0850,
      "exit": 1.0900,
      "sl": 1.0820,
      "tp": 1.0930,
      "result": "WIN",
      "pips": 50,
      "profit": 50.00,
      "exit_reason": "TAKE_PROFIT"
    }
  ]
}
```

---

### 6. AI Predictions

**Prefix:** `/api/v1/ai`

#### GET /api/v1/ai/predict/{symbol}
Menghasilkan prediksi AI dengan penjelasan SHAP untuk suatu simbol.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | path | - | Nama simbol |
| timeframe | query | H1 | Timeframe |
| limit | query | 500 | Maksimal 2000 bar |

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "model": "XGBoost",
  "metrics": {
    "accuracy": 65.2,
    "precision": 68.1,
    "recall": 62.3,
    "f1_score": 65.1,
    "roc_auc": 70.5,
    "training_samples": 400,
    "test_samples": 100
  },
  "prediction": {
    "signal": "BUY",
    "confidence": 0.72,
    "reasons": ["rsi_14: 65.2 (bullish)", "ema_trend: uptrend"]
  },
  "feature_importance": {
    "rsi_14": 0.15,
    "ema_12_50_ratio": 0.12
  },
  "explanation": {
    "shap_values": [0.02, -0.01],
    "feature_values": {"rsi_14": 65.2}
  }
}
```

#### GET /api/v1/ai/compare/{symbol}
Membandingkan performa model XGBoost vs LightGBM.

**Response:**
```json
{
  "symbol": "EURUSD",
  "timeframe": "H1",
  "comparison": {
    "xgboost": {"accuracy": 65.2, "precision": 68.1},
    "lightgbm": {"accuracy": 63.8, "precision": 66.5}
  },
  "recommendation": "XGBoost"
}
```

---

### 7. Paper Trading

**Prefix:** `/api/v1/paper-trading`

#### GET /api/v1/paper-trading/account
Ringkasan akun virtual.

#### POST /api/v1/paper-trading/positions/open
Membuka posisi baru.

**Parameters:**
| Nama | Tipe | Deskripsi |
|------|------|-----------|
| symbol | query | Nama simbol |
| direction | query | LONG atau SHORT |
| entry_price | query | Harga entry |
| stop_loss | query | Harga stop loss |
| take_profit | query | Harga take profit |
| lot_size | query | Ukuran lot (default 0.01) |
| signal | query | BUY atau SELL |
| confidence | query | Confidence level |
| reasons | query | Alasan (dipisah ;) |
| tags | query | Tags (dipisah ,) |

#### POST /api/v1/paper-trading/positions/close
Menutup posisi.

#### GET /api/v1/paper-trading/positions
Daftar semua posisi (termasuk yang sudah ditutup jika `include_closed=true`).

#### GET /api/v1/paper-trading/journal
Catatan jurnal trading (limit: 20).

#### GET /api/v1/paper-trading/analytics
Analitik performa komprehensif.

#### GET /api/v1/paper-trading/signal-performance
Performa sinyal trading (confusion matrix).

#### POST /api/v1/paper-trading/reset
Reset akun paper trading.

---

### 8. MT5 Bridge

**Prefix:** `/api/v1/mt5`

#### POST /api/v1/mt5/connect
Menghubungkan ke MT5 (mode simulasi di macOS).

#### POST /api/v1/mt5/disconnect
Memutuskan koneksi MT5.

#### GET /api/v1/mt5/account
Informasi akun MT5.

#### GET /api/v1/mt5/positions
Semua posisi terbuka di MT5.

#### POST /api/v1/mt5/orders/place
Menempatkan order dengan validasi.

#### POST /api/v1/mt5/positions/close/{ticket}
Menutup posisi berdasarkan ticket.

#### POST /api/v1/mt5/auto/start
Memulai auto trading engine.

#### POST /api/v1/mt5/auto/stop
Menghentikan auto trading engine.

#### GET /api/v1/mt5/auto/status
Status auto trading.

#### GET /api/v1/mt5/safety
Status sistem keamanan (safety system).

#### POST /api/v1/mt5/safety/kill-switch
Mengaktifkan/mematikan kill switch.

#### POST /api/v1/mt5/signal/execute
Mengeksekusi sinyal trading melalui auto trader.

#### GET /api/v1/mt5/executed-signals
Riwayat sinyal yang telah dieksekusi.

---

### 9. Settings

**Prefix:** `/api/v1/settings`

#### GET/POST /api/v1/settings/keys
Mendapatkan/menyimpan API keys (termask).

#### GET/POST /api/v1/settings/preferences
Mendapatkan/menyimpan preferensi trading.

#### GET/POST /api/v1/settings/risk
Mendapatkan/menyimpan konfigurasi risk management.

#### GET/POST /api/v1/settings/data-sources
Mendapatkan/menyimpan konfigurasi sumber data.

#### GET/POST /api/v1/settings/auto-trade
Mendapatkan/menyimpan konfigurasi auto trading.

#### GET /api/v1/settings/system-info
Informasi sistem:
```json
{
  "version": "0.3.0",
  "sprint": "Sprint 6 - MT5 Bridge & Auto Trading",
  "python_version": "3.12",
  "platform": "Al-Syaka Quant AI"
}
```

#### GET /api/v1/settings/db-status
Status koneksi database dan jumlah record per tabel.

---

### 10. Unified Signal

**Prefix:** `/api/v1/unified-signal`

#### GET /api/v1/unified-signal/{symbol}
Endpoint utama yang menggabungkan semua engine: statistik, struktur pasar, AI, multi-timeframe, dan makro.

**Parameters:**
| Nama | Tipe | Default | Deskripsi |
|------|------|---------|-----------|
| symbol | path | - | Nama simbol |
| timeframe | query | H1 | H1, H4, D1 |
| include_ai | query | false | Sertakan prediksi AI (lebih lambat) |

**Response:**
```json
{
  "signal_id": "SIG-42",
  "symbol": "EURUSD",
  "timestamp": "2026-07-15T10:00:00",
  "signal": "BUY",
  "confidence": 72.5,
  "composite_score": 68.3,
  "confidence_breakdown": {
    "market_structure": 75.0,
    "momentum": 60.0,
    "trend": 65.0,
    "volatility": 70.0,
    "ai_prediction": 50.0
  },
  "confidence_label": "MEDIUM",
  "market_regime": "TRENDING",
  "strategy_mode": "trend_following",
  "regime_reason": "Strong trend with breakout structure",
  "macro_bias": "BULLISH",
  "macro_strength": 65.0,
  "macro_confidence": 70.0,
  "macro_reason": "Macro bias is bullish (moderate, confidence 70%)",
  "final_decision": "BUY",
  "decision_reason": "Strong technical signal (72%) with trending regime",
  "conflict_detected": false,
  "entry_price": 1.08600,
  "stop_loss": 1.08300,
  "take_profit": 1.09200,
  "risk_reward": 2.0,
  "risk_level": "MEDIUM",
  "trade_quality": "GOOD",
  "reasons": [
    "Market Trend: BULLISH",
    "EMA bullish alignment",
    "ADX confirms trend strength",
    "Market regime: trending"
  ],
  "indicators_used": ["RSI", "EMA 12", "EMA 20", "EMA 50", "MACD", "ADX", "ATR"],
  "quant_strategy": {
    "strategy": "MeanReversionStrategy",
    "action": "BUY",
    "confidence": 0.65
  },
  "market_structure": {
    "trend": "BULLISH",
    "swing_highs": 5,
    "swing_lows": 4,
    "break_of_structure": 2,
    "change_of_character": 1,
    "fair_value_gaps": 3,
    "liquidity_sweeps": 1
  },
  "multi_timeframe": {
    "H1": "BUY",
    "H4": "BUY",
    "D1": "NEUTRAL"
  },
  "ai": null
}
```

---

### System Endpoints

#### GET /health
Health check endpoint.

```json
{
  "status": "ok",
  "service": "al-syaka-quant-ai",
  "version": "0.2.0",
  "sprint": "Sprint 2 - Analytical Engine"
}
```

#### GET /
Root endpoint dengan informasi API.

---

## Error Handling

API menggunakan HTTPException standar FastAPI:

| Kode | Deskripsi |
|------|-----------|
| 400 | Bad Request (parameter tidak valid) |
| 404 | Data tidak ditemukan |
| 500 | Internal Server Error |

Format error:
```json
{
  "detail": "No data for EURUSD"
}
```

## Rate Limiting

Saat ini belum ada rate limiting. Akan ditambahkan di production.

## Catatan Deployment

- Gunakan `uvicorn src.main:app --reload` untuk development
- Gunakan Gunicorn + Uvicorn workers untuk production
- Docker Compose tersedia di `docker/docker-compose.yml`
- Environment variable dikelola melalui file `.env`
