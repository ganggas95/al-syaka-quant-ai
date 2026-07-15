# Data Pipeline

## Ringkasan

Data pipeline adalah fondasi dari seluruh platform Al-Syaka Quant AI. Pipeline ini bertanggung jawab untuk mengumpulkan, menyimpan, dan menyediakan data pasar yang akurat dan tepat waktu untuk semua engine analisis.

---

## Arsitektur Data Collector

### Base Connector Interface

Semua connector mengimplementasikan `BaseConnector` abstract class:

```python
class BaseConnector(ABC):
    async def fetch_ohlc(symbol, timeframe, start, end) -> list[OHLCData]
    async def health_check() -> bool
```

### OHLCData Dataclass

```python
@dataclass
class OHLCData:
    symbol: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int
    spread: Optional[int] = None
```

---

## Connectors

### 1. Yahoo Finance Connector

**File**: `apps/api/src/collectors/yahoo.py`

Provider gratis dan real-time, cocok untuk data live yang mendekati TradingView.

**Symbol Mapping**:
- XAUUSD -> GC=F (Gold Futures)
- XAGUSD -> SI=F (Silver Futures)
- US30 -> ^DJI (Dow Jones)
- NAS100 -> ^IXIC (Nasdaq)
- SPX500 -> ^GSPC (S&P 500)
- BTCUSD -> BTC-USD
- ETHUSD -> ETH-USD
- Forex (6 chars) -> EURUSD=X

**Timeframe Mapping**:
- 1m, 5m, 15m, 30m -> interval same
- 1h -> 60m
- 4h -> 60m (Yahoo tidak mendukung 4h langsung)
- 1d -> 1d

**Keunggulan**: Data real-time gratis, coverage luas (forex, crypto, saham, indeks).

### 2. Polygon.io Connector

**File**: `apps/api/src/collectors/polygon.py`

Provider premium untuk harga spot yang akurat, terutama untuk logam mulia.

**Symbol Mapping**:
- XAUUSD -> C:XAUUSD
- XAGUSD -> C:XAGUSD
- BTCUSD -> X:BTCUSD
- ETHUSD -> X:ETHUSD

**Rate Limiting**: Free tier 5 calls/menit, dengan rate limiter internal (max 4 calls/menit).

**Keunggulan**: Harga spot akurat untuk XAUUSD/XAGUSD (tidak menggunakan futures).

### 3. Massive Connector

**File**: `apps/api/src/collectors/massive.py`

Provider premium opsional yang dapat dikonfigurasi.

**Endpoint**: `/v2/aggs/ticker/{symbol}/range/{multiplier}/{timespan}/{start}/{end}`

**Konfigurasi**: API key diset melalui environment variable `MASSIVE_API_KEY`.

---

## DataCollector Manager

**File**: `apps/api/src/collectors/manager.py`

Orchestrator yang mengelola semua connector dengan smart routing dan fallback.

**Routing Logic**:
1. Untuk XAUUSD, XAGUSD -> Prioritas Yahoo (real-time), fallback Polygon.
2. Untuk forex/crypto lain -> Yahoo Finance (gratis, reliable).
3. Jika provider utama gagal, fallback otomatis ke provider sekunder.
4. Massive connector digunakan jika API key dikonfigurasi.

```python
class DataCollector:
    def __init__(self):
        self.yahoo = YahooFinanceConnector()
        self.polygon = PolygonConnector(api_key=...)
        self.massive = MassiveConnector(api_key=...)

    async def fetch_ohlc(symbol, timeframe, start, end, provider=None):
        # Smart routing: coba primary, fallback ke secondary
        for connector in preferred_connectors:
            try:
                return await connector.fetch_ohlc(...)
            except Exception as e:
                errors.append(e)
                continue
        raise ValueError("All sources failed")
```

---

## Data Storage

### PostgreSQL dengan SQLAlchemy Async

**Model Database**:

**Symbol** -- Metadata instrumen trading:
- `name` (string, unique): EURUSD, XAUUSD, BTCUSD, dll.
- `base_currency`, `quote_currency`
- `pip_size`: 0.0001 untuk forex, 0.01 untuk XAUUSD
- `contract_size`: 100000 (standard lot)
- `is_active`: status aktif/non-aktif

**OHLC** -- Data harga:
- `symbol_id` -> ForeignKey ke symbols
- `timeframe`: M1, M5, M15, M30, H1, H4, D1
- `timestamp`: Waktu candle
- `open`, `high`, `low`, `close` (Numeric 12,6)
- `volume` (BigInteger)
- Unique constraint: (symbol_id, timeframe, timestamp)

**Tick** -- Data tick:
- `symbol_id`, `timestamp`, `bid`, `ask`, `last`, `volume`
- Index: (symbol_id, timestamp)

---

## Celery Tasks

**File**: `apps/api/src/tasks/market_data.py`

### Scheduled Tasks

```python
@shared_task(name="fetch_ohlc_task", bind=True, max_retries=3, default_retry_delay=60)
def fetch_ohlc_task(self):
    """Periodic task untuk fetch data OHLC terbaru."""
    return asyncio.run(_fetch_and_store_ohlc())
```

**Fungsi**:
- Mengambil data OHLC terbaru untuk semua simbol aktif secara periodik.
- Retry mechanism dengan exponential backoff (max 3 retry, delay 60 detik).
- Async execution via `asyncio.run()`.

### Data Processing Tasks

**File**: `apps/api/src/tasks/processing.py`

Placeholder untuk task pemrosesan data di masa depan:
- Komputasi indikator batch.
- Ekstraksi fitur untuk retraining model.
- Pembersihan dan validasi data historis.

---

## Alur Data End-to-End

```
[Market Data Providers]
     |
     v
[DataCollector] -- Smart routing & failover
     |
     v
[OHLC Data] -- Disimpan ke PostgreSQL
     |
     v
[Celery Tasks] -- Scheduled fetching & processing
     |
     v
[API Endpoints] -- Disajikan ke dashboard & engine
```

## Konfigurasi

Semua konfigurasi data pipeline dikelola melalui environment variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://quant:quant_pass@localhost:5432/al_syaka_quant

# Market Data Providers
YAHOO_FINANCE_ENABLED=true
POLYGON_API_KEY=your_polygon_key
MASSIVE_API_KEY=your_massive_key

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
```
