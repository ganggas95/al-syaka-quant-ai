# Risk Engine

## Ringkasan

Risk Engine menyediakan manajemen risiko yang komprehensif untuk setiap trade. Engine ini mengintegrasikan position sizing, stop-loss/take-profit calculation, Kelly criterion, dan trade quality assessment.

Package: `packages/risk/src/al_syaka_risk/`

---

## Komponen

### 1. RiskManager

**File**: `packages/risk/src/al_syaka_risk/risk_manager.py`

Manager utama yang mengintegrasikan semua komponen risk management.

```python
class RiskManager:
    def __init__(self, account_balance: float = 10_000):
        self.account_balance = account_balance
        self.position_sizer = PositionSizer(account_balance=account_balance)
        self.sl_calculator = StopLossCalculator()
        self.consecutive_losses = 0
```

**Metode Utama**: `evaluate_trade(signal, entry_price, confidence, atr_value, support, resistance, win_rate, avg_win, avg_loss) -> RiskDecision`

**Alur Evaluasi**:
1. Tentukan direction (LONG/SHORT) dari signal (BUY/SELL).
2. Hitung SL/TP menggunakan ATR, S/R, atau fixed pips.
3. Sesuaikan risk percentage berdasarkan consecutive losses (konservatif setelah 3+ losses).
4. Hitung position size.
5. Hitung Kelly criterion.
6. Assess trade quality.

**Consecutive Loss Adjustment**:
- Default risk: 1%
- Setelah 3 losses: turun ke 0.5%
- Setelah 5 losses: turun ke 0.25%

### RiskDecision

```python
@dataclass
class RiskDecision:
    signal: str          # BUY/SELL
    direction: str       # LONG/SHORT
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    lot_size: float
    risk_amount: float
    risk_percent: float
    kelly_percent: float
    trade_quality: str   # POOR, FAIR, GOOD, EXCELLENT
```

---

### 2. StopLossCalculator

**File**: `packages/risk/src/al_syaka_risk/stop_loss.py`

Kalkulator untuk menentukan level stop-loss dan take-profit.

**Metode**:

| Metode | Deskripsi | Parameter |
|--------|-----------|-----------|
| `calculate_atr_based()` | SL/TP berdasarkan ATR | multiplier SL (1.5), TP (3.0) |
| `calculate_fixed_pips()` | SL/TP berdasarkan pip tetap | SL 20 pips, TP 40 pips |
| `calculate_sr_based()` | SL/TP berdasarkan S/R level | support/resistance level, RR target |

**ATR-Based Calculation**:
- LONG: SL = entry - (ATR * 1.5), TP = entry + (ATR * 3.0)
- SHORT: SL = entry + (ATR * 1.5), TP = entry - (ATR * 3.0)

**S/R-Based Calculation**:
- LONG with support: SL = support level, TP based on risk_reward ratio
- SHORT with resistance: SL = resistance level, TP based on risk_reward ratio

### SLTPResult

```python
@dataclass
class SLTPResult:
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward_ratio: float
    sl_pips: float
    tp_pips: float
```

---

### 3. PositionSizer

**File**: `packages/risk/src/al_syaka_risk/position_sizing.py`

Menghitung ukuran posisi (lot size) berdasarkan parameter risk.

```python
class PositionSizer:
    def __init__(self, account_balance=10_000, risk_per_trade=0.01,
                 contract_size=100_000, max_risk_per_trade=0.02):
```

**Rumus**:
```
risk_amount = balance * risk_percent
pip_value_per_lot = pip_size * contract_size
lot_size = risk_amount / (sl_pips * pip_value_per_lot)
```

**Rounding**:
- < 0.1 lot: round ke 2 desimal (micro lots: 0.01, 0.02, ...)
- 0.1 - 1.0 lot: round ke 1 desimal (mini lots: 0.1, 0.2, ...)
- >= 1.0 lot: round ke 0 desimal (standard lots: 1, 2, ...)
- Minimum: 0.01 lot

---

### 4. KellyCriterion

**File**: `packages/risk/src/al_syaka_risk/kelly.py`

Optimal bet sizing berdasarkan formula Kelly.

**Rumus**:
```
Kelly % = win_rate - ((1 - win_rate) / (avg_win / avg_loss))
```

**Level Risiko**:
| Level | Fraction | Penggunaan |
|-------|----------|------------|
| Full Kelly | 100% | Agresif, risiko tinggi |
| Aggressive | 50% Kelly | Risiko moderat-tinggi |
| Moderate | 25% Kelly | Default recommendation |
| Conservative | 10% Kelly | Konservatif, safety first |
| Max Recommended | 2% hard cap | Batas maksimum mutlak |

---

## Trade Quality Assessment

Skor berdasarkan:
- Confidence: >= 0.7 (2 poin), >= 0.6 (1 poin)
- Risk/Reward: >= 2.0 (2 poin), >= 1.5 (1 poin)
- Risk percent: <= 1% (1 poin)

**Klasifikasi**:
| Skor | Kualitas |
|------|----------|
| 4-5 | EXCELLENT |
| 3 | GOOD |
| 2 | FAIR |
| 0-1 | POOR |

---

## Integrasi dengan Signal Generator

Risk Engine digunakan oleh Signal Generator untuk melengkapi setiap sinyal dengan informasi risiko:

```python
# Di SignalGenerator.generate()
risk_decision = self.risk_manager.evaluate_trade(
    signal=prob_result.signal,
    entry_price=entry_price,
    confidence=prob_result.confidence,
    atr_value=atr_value,
    support=support,
    resistance=resistance,
)
```

Output risk yang ditambahkan ke sinyal:
- `entry_price`, `stop_loss`, `take_profit`
- `risk_reward_ratio`
- `lot_size`
- `risk_level` (dari probability engine)
- `trade_quality` (dari risk manager)
