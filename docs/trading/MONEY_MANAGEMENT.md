# Money Management — Al-Syaka Quant AI

> Dokumen ini menjelaskan framework manajemen modal yang digunakan oleh platform Al-Syaka Quant AI. Tujuan utama adalah menjaga konsistensi pertumbuhan akun dengan risiko yang terkontrol.

---

## Daftar Isi

- [Filosofi Manajemen Modal](#filosofi-manajemen-modal)
- [Risk per Trade](#risk-per-trade)
- [Maximum Drawdown Limits](#maximum-drawdown-limits)
- [Kelly Criterion Implementation](#kelly-criterion-implementation)
- [Account Growth Targets](#account-growth-targets)
- [Risk Scaling](#risk-scaling)
- [Portfolio Risk Management](#portfolio-risk-management)
- [Recovery Mode](#recovery-mode)

---

## Filosofi Manajemen Modal

Manajemen modal di Al-Syaka Quant AI didasarkan pada tiga prinsip utama:

1. **Konservasi Modal (Capital Preservation):** Aturan pertama adalah jangan kehilangan uang. Aturan kedua adalah jangan lupakan aturan pertama.
2. **Pertumbuhan Konsisten (Consistent Growth):** Target pertumbuhan bulanan yang realistis antara 5% hingga 15%, bukan mengejar keuntungan instan.
3. **Risk-Adjusted Return:** Setiap keputusan trading harus mempertimbangkan rasio risk/reward, win rate, dan probabilitas statistik.

---

## Risk per Trade

### Batasan Risiko per Trading

Berdasarkan implementasi `PositionSizer` dan `RiskManager`:

| Level Trader | Risk per Trade | Maksimum per Hari | Keterangan |
|-------------|----------------|-------------------|------------|
| Konservatif | 0.5% - 1.0% | 3% | Trader pemula atau akun kecil |
| Moderat | 1.0% - 1.5% | 5% | Trader berpengalaman |
| Agresif | 1.5% - 2.0% | 6% | Trader profesional (wajib hedging) |
| Maximum | 2.0% | 6% | Hard limit, tidak boleh dilampaui |

### Aturan Dinamis Berdasarkan Drawdown

Risk per trade menyesuaikan dengan kondisi drawdown akun:

```python
def calculate_dynamic_risk(drawdown_percent: float) -> float:
    """Menghitung risk per trade berdasarkan drawdown saat ini."""
    if drawdown_percent < 3:
        return 0.01  # 1% risk
    elif drawdown_percent < 5:
        return 0.0075  # 0.75% risk
    elif drawdown_percent < 8:
        return 0.005  # 0.5% risk
    elif drawdown_percent < 10:
        return 0.0025  # 0.25% risk
    else:
        return 0.0  # Stop trading
```

### Contoh Perhitungan Risk

**Skenario:** Akun $10,000, risk 1% per trade

```
Risk Amount = $10,000 x 1% = $100
```

Jika SL adalah 20 pips dan pip value per lot adalah $10:

```
Lot Size = $100 / (20 pips x $10) = 0.5 lot
```

---

## Maximum Drawdown Limits

### Hierarki Drawdown Limit

| Level | Drawdown | Tindakan | Status |
|-------|----------|----------|--------|
| Warning Level | 5% (harian) | Stop trading untuk hari itu | Peringatan |
| Soft Limit | 10% (mingguan) | Stop trading, evaluasi mingguan | Evaluasi |
| Hard Limit | 15% (bulanan) | Stop trading, restart dengan akun demo | Reset |
| Critical Limit | 25% (total) | Review sistem, kemungkinan restart total | Darurat |

### Daily Drawdown Limit

- **Daily Loss Limit:** 5% dari balance awal hari.
- Jika tercapai, semua posisi harus ditutup dan trading dihentikan untuk hari itu.
- Hitungan drawdown harian di-reset setiap hari trading baru.

### Weekly Drawdown Limit

- **Weekly Loss Limit:** 10% dari balance awal minggu.
- Jika tercapai, trading dihentikan untuk sisa minggu tersebut.
- Dilakukan evaluasi strategi dan review trade mingguan.

### Monthly Drawdown Limit

- **Monthly Loss Limit:** 15% dari balance awal bulan.
- Jika tercapai, semua trading dihentikan.
- Wajib dilakukan review komprehensif meliputi:
  - Analisis performa tiap strategi
  - Market regime analysis selama periode tersebut
  - Evaluasi kepatuhan terhadap trading rulebook
  - Rekomendasi perubahan parameter

### Drawdown Recovery Plan

```
Jika DD < 5%  -> Trading normal dengan risk 1%
Jika DD 5-10% -> Risk dikurangi ke 0.5%, hanya trading dengan signal HIGH confidence
Jika DD > 10% -> Risk dikurangi ke 0.25%, hanya trading dengan regime TRENDING
```

---

## Kelly Criterion Implementation

Platform Al-Syaka Quant AI mengimplementasikan Kelly Criterion melalui kelas `KellyCriterion` di package `al-syaka-risk`.

### Rumus Dasar

```
K = W - ((1 - W) / R)
```

Dimana:
- **K** = Kelly fraction (persentase modal yang harus dipertaruhkan)
- **W** = Win rate (probabilitas menang, 0.0 - 1.0)
- **R** = Rasio rata-rata win terhadap rata-rata loss (avg_win / avg_loss)

### Interpretasi Hasil

| Nilai K | Interpretasi | Tindakan |
|---------|--------------|----------|
| K <= 0 | Ekspektasi negatif | Jangan trading, cari setup lain |
| 0 < K < 0.05 | Ekspektasi rendah | Gunakan conservative Kelly (10%) |
| 0.05 <= K < 0.15 | Ekspektasi sedang | Gunakan moderate Kelly (25%) |
| 0.15 <= K < 0.25 | Ekspektasi baik | Gunakan aggressive Kelly (50%) |
| K >= 0.25 | Ekspektasi sangat baik | Evaluasi ulang, pastikan win rate akurat |

### Contoh Perhitungan

**Skenario 1:** Win rate 60%, avg win $100, avg loss $50

```
R = 100/50 = 2.0
K = 0.60 - ((1 - 0.60) / 2.0) = 0.60 - 0.20 = 0.40
Kelly fraction = 40% (Full Kelly)
```

**Implementasi di platform:**

```python
from al_syaka_risk import KellyCriterion

result = KellyCriterion.recommended_risk(
    win_rate=0.60,
    avg_win=100,
    avg_loss=50
)
# Output:
# {
#     "full_kelly": 40.0,        # 40% - terlalu agresif
#     "aggressive": 20.0,        # 20% - 50% Kelly
#     "moderate": 10.0,          # 10% - 25% Kelly (default)
#     "conservative": 4.0,       # 4% - 10% Kelly
#     "max_recommended": 2.0     # Hard cap 2%
# }
```

### Fractional Kelly

Platform menggunakan **Fractional Kelly** dengan default 25% (moderate) untuk menjaga safety margin. Ini berarti jika full Kelly menunjukkan 40%, maka risk yang digunakan adalah 40% x 25% = 10%. Namun, nilai ini tetap dibatasi oleh hard cap **2%** max risk per trade.

---

## Account Growth Targets

### Target Bulanan

| Level | Target Bulanan | Risk per Trade | Target Tahunan |
|-------|---------------|----------------|----------------|
| Konservatif | 3% - 5% | 0.5% - 1.0% | 36% - 60% |
| Moderat | 5% - 10% | 1.0% - 1.5% | 60% - 120% |
| Agresif | 10% - 15% | 1.5% - 2.0% | 120% - 180% |

### Compound Growth Calculation

Target menggunakan compound growth (bunga berbunga):

```python
future_balance = initial_balance * (1 + monthly_return) ** months
```

**Contoh:**

| Initial Balance | Monthly Target | 6 Bulan | 12 Bulan | 24 Bulan |
|----------------|---------------|---------|----------|----------|
| $10,000 | 5% | $13,401 | $17,958 | $32,251 |
| $10,000 | 8% | $15,869 | $25,181 | $63,418 |
| $10,000 | 10% | $17,715 | $31,384 | $98,497 |

### Performance Metrics Tracking

Platform melacak metrik berikut secara otomatis:

| Metrik | Target | Deskripsi |
|--------|--------|-----------|
| Win Rate | >= 55% | Persentase trading yang profit |
| Profit Factor | >= 1.5 | Gross profit / gross loss |
| Sharpe Ratio | >= 1.0 | Return per unit risk |
| Max Drawdown | < 15% | Drawdown maksimum |
| Average RR | >= 1:2 | Rata-rata risk/reward ratio |
| Expectancy | Positif | (Win% x AvgWin) - (Loss% x AvgLoss) |

---

## Risk Scaling

### Berdasarkan Account Balance

| Account Balance | Risk per Trade | Notes |
|----------------|----------------|-------|
| < $1,000 | 0.5% | Akun mikro, sangat konservatif |
| $1,000 - $5,000 | 1.0% | Akun kecil, standar konservatif |
| $5,000 - $25,000 | 1.0% - 1.5% | Akun menengah |
| $25,000 - $100,000 | 1.0% | Akun besar, risk lebih rendah |
| > $100,000 | 0.5% - 1.0% | Akun institutional |

### Berdasarkan Win Rate (Adaptive)

Jika win rate aktual < 50% dalam 30 hari terakhir, risk per trade otomatis diturunkan:

```python
def adapt_risk_to_win_rate(actual_win_rate: float) -> float:
    base_risk = 0.01  # 1%
    if actual_win_rate >= 0.60:
        return base_risk
    elif actual_win_rate >= 0.50:
        return base_risk * 0.75
    elif actual_win_rate >= 0.40:
        return base_risk * 0.5
    else:
        return base_risk * 0.25
```

---

## Portfolio Risk Management

### Maximum Exposure

| Metrik | Limit | Keterangan |
|--------|-------|------------|
| Total open positions | 3 posisi | Maksimum simultan |
| Risk per pair | 3% | Total risk untuk pair yang sama |
| Correlation limit | 2 pasangan | Pair dengan korelasi > 0.7 dianggap sama |
| Margin used | < 20% | Total margin yang digunakan |
| Leverage efektif | < 5x | Total notional / balance |

### Correlation Matrix Rules

Pasangan dengan korelasi tinggi tidak boleh di-trading-kan secara simultan:

| Pair 1 | Pair 2 | Korelasi | Boleh Bersamaan? |
|--------|--------|----------|------------------|
| EURUSD | GBPUSD | Tinggi | Tidak |
| EURUSD | USDCHF | Negatif tinggi | Tidak |
| XAUUSD | USDJPY | Rendah | Ya |
| GBPJPY | EURJPY | Tinggi | Tidak |

---

## Recovery Mode

Recovery Mode diaktifkan secara otomatis ketika akun mengalami drawdown > 10%.

### Aturan Recovery Mode

1. **Risk reduction:** Risk per trade dikurangi menjadi 0.25%.
2. **Signal filter:** Hanya trading dengan composite score HIGH (>= 75).
3. **Regime filter:** Hanya trading saat market regime TRENDING.
4. **Reduced frequency:** Maksimum 1 posisi per hari.
5. **No martingale:** Dilarang keras menambah posisi untuk averaging.
6. **Strict SL/TP:** SL harus 1.5x ATR, TP minimal 3x ATR (RR 1:2).

### Exit Recovery Mode

Recovery mode berakhir ketika salah satu kondisi berikut terpenuhi:
- Akun kembali ke drawdown < 5%
- 20 trading days telah berlalu dalam recovery mode
- Evaluasi mingguan menunjukkan performa positif

---

*Dokumen ini adalah bagian dari platform Al-Syaka Quant AI. Perubahan pada parameter manajemen modal harus melalui review dan validasi backtesting terlebih dahulu.*
