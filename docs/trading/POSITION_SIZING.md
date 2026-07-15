# Position Sizing — Al-Syaka Quant AI

> Dokumen ini menjelaskan metode perhitungan ukuran posisi (lot size) yang digunakan oleh platform Al-Syaka Quant AI. Perhitungan position sizing terintegrasi dengan ATR, risk tolerance, dan Kelly Criterion.

---

## Daftar Isi

- [Position Sizing Berbasis ATR](#position-sizing-berbasis-atr)
- [Lot Size Calculation](#lot-size-calculation)
- [Position Sizing Berdasarkan Risk Tolerance](#position-sizing-berdasarkan-risk-tolerance)
- [Scaling In Strategy](#scaling-in-strategy)
- [Scaling Out Strategy](#scaling-out-strategy)
- [Position Sizing untuk Berbagai Instrumen](#position-sizing-untuk-berbagai-instrumen)
- [Studi Kasus](#studi-kasus)

---

## Position Sizing Berbasis ATR

Platform menggunakan Average True Range (ATR) sebagai dasar utama perhitungan position sizing. ATR memberikan ukuran volatilitas yang objektif dan adaptif terhadap kondisi pasar.

### Rumus Dasar

```
Stop Loss Distance = ATR x SL Multiplier

Dimana:
- SL Multiplier default = 1.5 (untuk arah LONG maupun SHORT)
- ATR = Average True Range periode 14
```

### Cara Kerja di Platform

Berdasarkan implementasi `UnifiedSignalGenerator.generate()`:

```python
# Entry price adalah harga close terakhir
entry = float(df["close"].iloc[-1])

# ATR value dari indikator
atr_val = indicators_list.get("atr_14", [0.001])[-1]

# Stop Loss untuk LONG
sl = entry - (atr_val * 1.5)

# Stop Loss untuk SHORT
sl = entry + (atr_val * 1.5)

# Take Profit untuk LONG
tp = entry + (atr_val * 3.0)

# Take Profit untuk SHORT
tp = entry - (atr_val * 3.0)

# Risk/Reward Ratio
rr = abs(tp - entry) / abs(sl - entry)
```

### Parameter ATR Berdasarkan Timeframe

| Timeframe | ATR Period | SL Multiplier | TP Multiplier | Typical SL Distance |
|-----------|-----------|---------------|---------------|-------------------|
| M15 | 14 | 1.5 | 3.0 | 0.15% - 0.30% |
| M30 | 14 | 1.5 | 3.0 | 0.20% - 0.40% |
| H1 | 14 | 1.5 | 3.0 | 0.30% - 0.60% |
| H4 | 14 | 1.5 | 3.0 | 0.50% - 1.00% |
| D1 | 14 | 1.5 | 3.0 | 1.00% - 2.00% |

---

## Lot Size Calculation

### Rumus Perhitungan Lot

Berdasarkan implementasi `PositionSizer.calculate()`:

```python
# 1. Hitung risk amount
risk_amount = account_balance * risk_percent

# 2. Hitung stop loss dalam pip
sl_pips = abs(entry_price - stop_loss) / pip_size

# 3. Hitung pip value per lot
pip_value_per_lot = pip_size * contract_size

# 4. Hitung lot size
lot_size = risk_amount / (sl_pips * pip_value_per_lot)
```

### Parameter Default

| Parameter | Nilai Default | Keterangan |
|-----------|--------------|------------|
| Account Balance | $10,000 | Balance awal akun |
| Risk per Trade | 1.0% | Persentase modal yang di-risk-kan |
| Contract Size | 100,000 unit | Standard lot untuk Forex |
| Pip Size | 0.0001 | Untuk pair mayor (kecuali JPY) |
| Minimum Lot | 0.01 lot | Micro lot |
| Maximum Risk per Trade | 2.0% | Hard limit |

### Pembulatan Lot Size

```python
if lot_size < 0.1:
    lot_size = round(lot_size, 2)  # Micro lots (0.01, 0.02, ..., 0.09)
elif lot_size < 1.0:
    lot_size = round(lot_size, 1)  # Mini lots (0.1, 0.2, ..., 0.9)
else:
    lot_size = round(lot_size, 0)  # Standard lots (1, 2, 3, ...)
```

### Contoh Perhitungan Lengkap

**Skenario:** EURUSD, entry 1.1050, SL 20 pips, balance $10,000, risk 1%

```
Risk Amount = $10,000 x 1% = $100
SL Pips = 20 pips
Pip Value = 0.0001 x 100,000 = $10 per lot
Lot Size = $100 / (20 x $10) = 0.5 lot

Notional Value = 0.5 x 100,000 x 1.1050 = $55,250
Leverage Efektif = $55,250 / $10,000 = 5.5x
```

---

## Position Sizing Berdasarkan Risk Tolerance

### Risk Tolerance Levels

| Level | Risk per Trade | Deskripsi | Cocok Untuk |
|-------|---------------|-----------|-------------|
| Very Conservative | 0.25% | Minimal risk | Recovery mode, akun kecil |
| Conservative | 0.50% | Low risk | Trader pemula |
| Moderate | 1.00% | Standard risk | Trader berpengalaman (default) |
| Slightly Aggressive | 1.50% | Above average | Trader profesional |
| Aggressive | 2.00% | Maximum risk | Trader professional dengan hedging |

### Dynamic Position Sizing

Position sizing dapat disesuaikan secara dinamis berdasarkan:

1. **Composite Score:**
   - HIGH (>= 75): Gunakan risk penuh (1.0%)
   - MEDIUM (55 - 74): Gunakan 75% dari risk (0.75%)
   - LOW (< 55): Tidak entry

2. **Market Regime:**
   - TRENDING: Risk penuh (1.0%)
   - VOLATILE: 75% risk (0.75%)
   - REVERSAL: 50% risk (0.50%)
   - RANGE: 50% risk (0.50%)

3. **Trade Quality (dari RiskManager):**
   - EXCELLENT: Risk penuh (1.0%)
   - GOOD: 75% risk (0.75%)
   - FAIR: 50% risk (0.50%)
   - POOR: Tidak entry

### Contoh Position Sizing dengan Dynamic Adjustment

```python
from al_syaka_risk import PositionSizer, KellyCriterion

sizer = PositionSizer(account_balance=10_000)

# Trade quality = GOOD, regime = TRENDING
effective_risk = 0.01 * 1.0  # 1.0% (regime TRENDING, full risk)

result = sizer.calculate(
    entry_price=1.1050,
    stop_loss=1.1030,  # 20 pips
    risk_percent=effective_risk  # 1.0%
)

print(f"Lot Size: {result.lot_size}")
print(f"Risk Amount: ${result.risk_amount:.2f}")
```

---

## Scaling In Strategy

### Aturan Scaling In

Scaling in adalah strategi menambah posisi secara bertahap ketika harga bergerak sesuai prediksi.

### Level Scaling In

| Level | Entry Point | Persentase Posisi | Risk Porsi |
|-------|------------|-------------------|------------|
| Initial Entry | Entry awal (E0) | 50% dari total target | 50% dari risk total |
| Scale 1 | E0 + 0.5x ATR | 30% dari total target | 30% dari risk total |
| Scale 2 | E0 + 1.0x ATR | 20% dari total target | 20% dari risk total |

### Aturan Scaling In

1. Scaling in hanya dilakukan jika trade quality adalah GOOD atau EXCELLENT.
2. Setiap level scaling in harus memiliki SL sendiri (dihitung dari entry price masing-masing).
3. Total risk dari semua posisi tidak boleh melebihi maximum risk per trade (2%).
4. Scaling in hanya dilakukan dalam regime TRENDING.
5. Jika setelah scale 1 harga berbalik dan mencapai SL, posisi keseluruhan harus ditutup.

### Contoh Scaling In

**Skenario:** EURUSD, balance $20,000, total target 0.5 lot

```
Initial Entry (50%): 0.25 lot @ 1.1050, SL @ 1.1030 (20 pips)
Scale 1 (30%):      0.15 lot @ 1.1075 (0.5x ATR), SL @ 1.1055
Scale 2 (20%):      0.10 lot @ 1.1100 (1.0x ATR), SL @ 1.1080

Total Position: 0.50 lot
Average Entry:  1.1066
Aggregated SL:  1.1030 (gunakan SL paling ketat)
```

---

## Scaling Out Strategy

### Aturan Scaling Out

Scaling out adalah strategi mengambil profit secara bertahap untuk mengamankan keuntungan sambil tetap membiarkan sebagian posisi berjalan.

### Level Scaling Out

| Level | Exit Point | Persentase Posisi Exit | Sisa Posisi |
|-------|-----------|----------------------|-------------|
| TP 1 | 1.0x ATR | 33% | 67% |
| TP 2 | 2.0x ATR | 33% | 34% |
| TP 3 | 3.0x ATR (TP utama) | 34% | 0% |

### Aturan Scaling Out

1. Scaling out hanya dilakukan ketika harga bergerak sesuai arah prediksi.
2. Setelah TP 1 tercapai, SL untuk sisa posisi dipindahkan ke break even (entry price).
3. Setelah TP 2 tercapai, SL untuk sisa posisi menggunakan trailing stop (1x ATR).
4. Scaling out tidak boleh dilakukan dalam regime REVERSAL atau RANGE.

### Contoh Scaling Out

**Skenario:** BUY EURUSD @ 1.1050, ATR = 0.0050 (50 pips)

```
Entry: 1.1050
ATR:   50 pips

TP 1 (1.0x ATR): 1.1100 -> Exit 33% posisi
TP 2 (2.0x ATR): 1.1150 -> Exit 33% posisi
TP 3 (3.0x ATR): 1.1200 -> Exit 34% posisi

Setelah TP 1: SL sisa posisi pindah ke 1.1050 (break even)
Setelah TP 2: SL sisa posisi = 1.1100 (trailing 1x ATR)
```

---

## Position Sizing untuk Berbagai Instrumen

### Forex Pairs

| Pair Type | Pip Size | Contract Size | Contoh Perhitungan |
|-----------|---------|---------------|-------------------|
| Mayor (EURUSD, GBPUSD) | 0.0001 | 100,000 | Standard |
| JPY Pairs (USDJPY) | 0.01 | 100,000 | Pip value berbeda |
| Cross (GBPJPY, EURJPY) | 0.01 | 100,000 | Pip value = rate dependent |

### Perhitungan Pip Value untuk JPY Pairs

```python
# Untuk USDJPY di akun USD-dominasi
pip_value = (0.01 / usdjpy_rate) * contract_size

# Contoh: USDJPY = 150.00, contract size = 100,000
pip_value = (0.01 / 150.00) * 100,000 = $6.67 per lot
```

### XAUUSD (Gold)

| Parameter | Nilai |
|-----------|-------|
| Contract Size | 100 oz |
| Pip/Point Size | 0.01 |
| Pip Value | $1.0 per 0.01 per lot |
| Typical ATR H1 | 0.50 - 1.50 |
| Typical SL | 1.5x ATR = 0.75 - 2.25 |

### Indeks Saham (US30, NASDAQ, S&P500)

| Parameter | Nilai |
|-----------|-------|
| Contract Size | 1 CFD unit |
| Pip/Point Size | 1.0 |
| Point Value | $1.0 - $5.0 per point (tergantung broker) |
| Typical ATR H1 | 50 - 150 points |

---

## Studi Kasus

### Kasus 1: EURUSD Trending

**Kondisi:**
- Balance: $25,000
- Risk: 1.0% (moderate)
- Signal: BUY, composite score HIGH (82)
- Regime: TRENDING
- Entry: 1.1200
- ATR: 0.0040 (40 pips)
- SL: 1.1140 (1.5x ATR = 60 pips)
- TP: 1.1320 (3.0x ATR = 120 pips)

**Perhitungan:**
```
Risk Amount = $25,000 x 1.0% = $250
SL Pips = 60 pips
Pip Value = $10 per lot (EURUSD standard)
Lot Size = $250 / (60 x $10) = 0.42 lot -> dibulatkan 0.4 lot

Max Risk jika trade loss = 0.4 x 60 x $10 = $240 (0.96%)
Notional Value = 0.4 x 100,000 x 1.12 = $44,800
Potential Profit = 0.4 x 120 x $10 = $480 (RR 1:2)
```

### Kasus 2: XAUUSD Volatile

**Kondisi:**
- Balance: $10,000
- Risk: 0.75% (VOLATILE regime)
- Signal: SELL, composite score MEDIUM (68)
- Regime: VOLATILE
- Entry: 1950.00
- ATR: 1.20
- SL: 1951.80 (1.5x ATR)
- TP: 1946.40 (3.0x ATR)

**Perhitungan:**
```
Risk Amount = $10,000 x 0.75% = $75
SL Distance = 1951.80 - 1950.00 = 1.80
Pip Value = $1.0 per 0.01 (100 oz contract)
SL Pips = 180 pips (dalam 0.01 unit)
Lot Size = $75 / (180 x $1.0) = 0.42 lot -> dibulatkan 0.40 lot

Max Risk = 0.40 x 180 x $1.0 = $72 (0.72%)
Potential Profit = 0.40 x 360 x $1.0 = $144 (RR 1:2)
```

---

*Dokumen ini adalah bagian dari platform Al-Syaka Quant AI. Selalu lakukan validasi parameter position sizing dengan backtesting sebelum diterapkan pada akun real.*
