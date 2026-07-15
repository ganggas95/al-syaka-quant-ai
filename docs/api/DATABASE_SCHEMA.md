# Skema Database Al-Syaka Quant AI

## Teknologi

- **Database:** PostgreSQL
- **ORM:** SQLAlchemy Async (asyncpg driver)
- **Migration:** Alembic
- **Engine Pool:** pool_size=10, max_overflow=20
- **URL Koneksi:** `postgresql+asyncpg://quant:quant_pass@localhost:5432/al_syaka_quant`

## Entity Relationship Diagram

```
+------------------+       +------------------+
|     symbols      |       |      ohlc        |
+------------------+       +------------------+
| id (PK)          |<------| symbol_id (FK)   |
| name (UQ, IX)    |       | id (PK)          |
| base_currency    |       | timeframe        |
| quote_currency   |       | timestamp        |
| exchange         |       | open             |
| broker           |       | high             |
| pip_size         |       | low              |
| contract_size    |       | close            |
| is_active        |       | volume           |
| created_at       |       | spread           |
| updated_at       |       | created_at       |
+------------------+       +------------------+
        |                          |
        |                          |
        v                          v
+------------------+       +------------------+
|      ticks       |       |      news        |
+------------------+       +------------------+
| symbol_id (FK)   |       | id (PK)          |
| id (PK)          |       | title            |
| timestamp        |       | description      |
| bid              |       | source           |
| ask              |       | url              |
| last             |       | published_at (IX)|
| volume           |       | impact           |
| created_at       |       | currency (IX)    |
+------------------+       | category         |
                            | created_at       |
                            +------------------+

+------------------+
|     signals      |
+------------------+
| id (PK)          |
| symbol (IX)      |
| timeframe        |
| signal           |
| confidence       |
| entry_price      |
| stop_loss        |
| take_profit      |
| risk_reward      |
| risk_level       |
| reasons          |
| indicators_used  |
| market_trend     |
| h1_signal        |
| h4_signal        |
| d1_signal        |
| ai_accuracy      |
| created_at (IX)  |
| outcome_result   |
| outcome_profit   |
| outcome_updated  |
+------------------+
```

---

## Tabel: symbols

Menyimpan metadata instrumen trading.

| Kolom | Tipe | Constraint | Deskripsi |
|-------|------|------------|-----------|
| id | Integer | PK, autoincrement | Primary key |
| name | String(50) | UNIQUE, NOT NULL, INDEX | Nama simbol (EURUSD) |
| base_currency | String(10) | NOT NULL | Mata uang dasar (EUR) |
| quote_currency | String(10) | NOT NULL | Mata uang kutipan (USD) |
| exchange | String(50) | NULLABLE | Bursa asal |
| broker | String(50) | NULLABLE | Broker |
| pip_size | Numeric(10,8) | NOT NULL, default=0.0001 | Ukuran pip |
| contract_size | Integer | NOT NULL, default=100000 | Ukuran kontrak |
| is_active | Boolean | default=True | Status aktif |
| created_at | DateTime | default=utcnow | Waktu dibuat |
| updated_at | DateTime | default=utcnow, onupdate=utcnow | Waktu diupdate |

**Relationships:**
- `ohlc_records`: One-to-many ke tabel `ohlc`
- `ticks`: One-to-many ke tabel `ticks`

Index: `ix_symbols_name` (unique) pada kolom `name`.

---

## Tabel: ohlc

Menyimpan data harga OHLC (Open, High, Low, Close).

| Kolom | Tipe | Constraint | Deskripsi |
|-------|------|------------|-----------|
| id | BigInteger | PK, autoincrement | Primary key |
| symbol_id | Integer | FK -> symbols.id, NOT NULL | Referensi simbol |
| timeframe | String(10) | NOT NULL | Timeframe (M1, M5, M15, M30, H1, H4, D1, W1, MN) |
| timestamp | DateTime | NOT NULL | Waktu candle |
| open | Numeric(12,6) | NOT NULL | Harga pembukaan |
| high | Numeric(12,6) | NOT NULL | Harga tertinggi |
| low | Numeric(12,6) | NOT NULL | Harga terendah |
| close | Numeric(12,6) | NOT NULL | Harga penutupan |
| volume | BigInteger | NOT NULL, default=0 | Volume |
| spread | Integer | NULLABLE | Selisih bid-ask |
| created_at | DateTime | default=utcnow | Waktu dibuat |

**Constraints:**
- `uq_ohlc_symbol_tf_ts`: Unique (symbol_id, timeframe, timestamp) -- mencegah duplikasi candle
- `ix_ohlc_symbol_tf`: Index (symbol_id, timeframe) -- mempercepat query per simbol+timeframe
- `ix_ohlc_symbol_tf_ts`: Index (symbol_id, timeframe, timestamp) -- mempercepat query range waktu

**Relationship:**
- `symbol`: Many-to-one ke tabel `symbols`

---

## Tabel: ticks

Menyimpan data tick-by-tick.

| Kolom | Tipe | Constraint | Deskripsi |
|-------|------|------------|-----------|
| id | BigInteger | PK, autoincrement | Primary key |
| symbol_id | Integer | FK -> symbols.id, NOT NULL | Referensi simbol |
| timestamp | DateTime | NOT NULL | Waktu tick |
| bid | Numeric(12,6) | NOT NULL | Harga bid |
| ask | Numeric(12,6) | NOT NULL | Harga ask |
| last | Numeric(12,6) | NULLABLE | Harga last |
| volume | BigInteger | NULLABLE | Volume |
| created_at | DateTime | default=utcnow | Waktu dibuat |

**Index:**
- `ix_ticks_symbol_id_ts`: Index (symbol_id, timestamp) -- mempercepat query tick per simbol

**Relationship:**
- `symbol`: Many-to-one ke tabel `symbols`

---

## Tabel: news

Menyimpan berita pasar dan event ekonomi.

| Kolom | Tipe | Constraint | Deskripsi |
|-------|------|------------|-----------|
| id | Integer | PK, autoincrement | Primary key |
| title | String(500) | NOT NULL | Judul berita |
| description | Text | NULLABLE | Deskripsi |
| source | String(50) | NOT NULL | Sumber berita (investing, rss) |
| url | String(1000) | NULLABLE | URL berita |
| published_at | DateTime | NOT NULL | Waktu publikasi |
| impact | String(10) | NULLABLE | Dampak (high, medium, low) |
| currency | String(10) | NULLABLE | Mata uang terkait |
| category | String(50) | NULLABLE | Kategori |
| created_at | DateTime | default=utcnow | Waktu dibuat |

**Index:**
- `ix_news_published_at`: Index pada `published_at` -- mempercepat query berdasarkan waktu
- `ix_news_currency`: Index pada `currency` -- mempercepat filter berdasarkan mata uang

---

## Tabel: signals

Menyimpan catatan setiap sinyal trading yang dihasilkan beserta outcome-nya.

| Kolom | Tipe | Constraint | Deskripsi |
|-------|------|------------|-----------|
| id | Integer | PK, autoincrement | Primary key |
| symbol | String(50) | NOT NULL, INDEX | Simbol |
| timeframe | String(10) | NOT NULL | Timeframe |
| signal | String(10) | NOT NULL | Arah sinyal (BUY, SELL, NEUTRAL) |
| confidence | Float | NOT NULL | Confidence level (0-100) |
| entry_price | Numeric(12,6) | NULLABLE | Harga entry |
| stop_loss | Numeric(12,6) | NULLABLE | Harga stop loss |
| take_profit | Numeric(12,6) | NULLABLE | Harga take profit |
| risk_reward | Numeric(6,2) | NULLABLE | Rasio risk/reward |
| risk_level | String(10) | NULLABLE | Level risiko (LOW, MEDIUM, HIGH) |
| reasons | Text | NULLABLE | Alasan (JSON array) |
| indicators_used | Text | NULLABLE | Indikator yang digunakan (JSON array) |
| market_trend | String(20) | NULLABLE | Tren pasar (BULLISH, BEARISH, NEUTRAL) |
| h1_signal | String(10) | NULLABLE | Sinyal timeframe H1 |
| h4_signal | String(10) | NULLABLE | Sinyal timeframe H4 |
| d1_signal | String(10) | NULLABLE | Sinyal timeframe D1 |
| ai_accuracy | Float | NULLABLE | Akurasi model AI |
| created_at | DateTime | default=utcnow | Waktu dibuat |
| outcome_result | String(10) | NULLABLE | Hasil (WIN, LOSS, PENDING) |
| outcome_profit | Numeric(12,6) | NULLABLE | Profit yang direalisasikan |
| outcome_updated_at | DateTime | NULLABLE | Waktu update outcome |

**Index:**
- `ix_signals_symbol_created`: Index (symbol, created_at) -- mempercepat query sinyal per simbol

---

## Catatan Penting

1. **Temporal Data:** Tabel `ohlc` dan `ticks` diproyeksikan menjadi besar. Index komposit pada `(symbol_id, timeframe, timestamp)` sangat penting untuk performa query.

2. **Enum pada signal:** Kolom `signal` menggunakan string (BUY/SELL/NEUTRAL) dan `outcome_result` menggunakan string (WIN/LOSS/PENDING).

3. **JSON Storage:** Kolom `reasons` dan `indicators_used` di tabel `signals` menyimpan data JSON sebagai string Text untuk fleksibilitas.

4. **Migration Alembic:** Dua migration telah dibuat:
   - `6ff7a024a903` - Initial tables (symbols, ohlc, ticks, news)
   - `1553a94511fd` - Add signals table

5. **Seed Data:** Tersedia di `database/seed/symbols.py` untuk simbol-simbol utama forex seperti EURUSD, GBPUSD, USDJPY, AUDUSD, USDCAD, NZDUSD, XAUUSD.

6. **Async Session:** Semua operasi database menggunakan SQLAlchemy async session dengan pattern:
   ```python
   async with async_session_factory() as session:
       result = await session.execute(query)
       await session.commit()
   ```
