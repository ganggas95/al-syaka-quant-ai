# Signal Engine

## Ringkasan

Signal Engine adalah pusat dari semua analisis di Al-Syaka Quant AI. Engine ini mengintegrasikan semua komponen (statistical, market structure, AI, macro, risk) menjadi satu sinyal trading yang komprehensif.

Platform memiliki dua level signal generator:
1. **SignalGenerator** -- Generator sinyal dasar (statistical + risk).
2. **UnifiedSignalGenerator** -- Generator sinyal terpadu (semua engine).

---

## 1. SignalGenerator (Dasar)

**File**: `apps/api/src/signal_service/generator.py`

Generator sinyal yang mengintegrasikan Statistical Engine dan Risk Engine.

```python
class SignalGenerator:
    def __init__(self, account_balance: float = 10_000):
        self.probability_engine = ProbabilityEngine()
        self.risk_manager = RiskManager(account_balance=account_balance)
```

**Alur Generate**:
1. Hitung probabilitas dari indicators + market structure.
2. Jika NEUTRAL, return early tanpa risk assessment.
3. Tentukan entry price (close terakhir).
4. Hitung ATR untuk SL/TP.
5. Ambil S/R levels dari market structure.
6. Risk assessment (SL/TP, position sizing, trade quality).
7. Kumpulkan indikator yang digunakan.

**SignalResult**:
```python
@dataclass
class SignalResult:
    symbol: str
    timeframe: str
    timestamp: datetime
    signal: str          # BUY, SELL, NEUTRAL
    confidence: float    # 0-100%
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward_ratio: Optional[float]
    lot_size: Optional[float]
    reasons: list[str]
    risk_level: str      # LOW, MEDIUM, HIGH
    trade_quality: str   # POOR, FAIR, GOOD, EXCELLENT
    indicators_used: list[str]
```

---

## 2. UnifiedSignalGenerator (Terpadu)

**File**: `apps/api/src/unified_signal.py`

Generator sinyal lengkap yang mengintegrasikan SEMUA engine:

- Statistical Engine (probability)
- Market Structure (BOS, CHOCH, FVG, S/R)
- AI Engine (XGBoost + SHAP)
- Risk Engine (position sizing)
- Macro Bias Engine (H4/D1)
- Multi-Timeframe Confirmation (H1, H4, D1)
- Final Decision Engine

### Alur Generate Lengkap

```
1. Fetch Data
   - Data H1 (timeframe utama)
   - Data H4 (timeframe lebih tinggi)
   - Data D1 (timeframe harian)

2. Compute Indicators
   - IndicatorCalculator -> RSI, EMA, ATR, MACD, ADX, Bollinger, dll.

3. Market Structure Analysis
   - Swing highs/lows, BOS, CHOCH
   - FVG detection
   - Liquidity sweeps
   - S/R levels
   - Current trend determination

4. Probability (Statistical Engine)
   - Weighted scoring dari trend, momentum, structure, volatility, volume, session

5. Multi-Timeframe Signals
   - Hitung sinyal untuk H4 dan D1 (jika berbeda dari timeframe utama)

6. Entry/SL/TP Calculation
   - Entry: close terakhir
   - SL: entry +/- (ATR * 1.5)
   - TP: entry +/- (ATR * 3.0)
   - R/R ratio

7. AI Prediction (opsional)
   - FeaturePipeline -> fitur
   - XGBoostModel -> training cepat
   - ExplainableAI -> SHAP explanation
   - Confidence, accuracy, reasons

8. Composite Score
   - 5 komponen: market structure (35%), momentum (20%), trend (15%), volatility (10%), AI (20%)
   - Confidence label: LOW (<55), MEDIUM (55-74), HIGH (>=75)

9. Market Regime Detection
   - TRENDING: ADX >= 25 + BOS
   - REVERSAL: RSI > 70 atau < 30
   - RANGE: ADX <= 15 + no BOS/CHOCH
   - VOLATILE: sisanya (default)

10. Macro Bias Analysis
    - Analisis H4 dan D1
    - Bias, strength, confidence

11. Final Decision
    - FinalDecisionEngine.decide()
    - BUY / SELL / WAIT / HEDGE
    - Conflict detection
    - Macro override logic

12. Quant Strategy Signal
    - MeanReversionStrategy sebagai tambahan

13. Build UnifiedSignal
    - Semua komponen digabung
```

### UnifiedSignal Output

```python
@dataclass
class UnifiedSignal:
    symbol: str
    timestamp: datetime
    signal: str                    # BUY, SELL, NEUTRAL
    confidence: float              # 0-100%
    entry_price: Optional[float]
    stop_loss: Optional[float]
    take_profit: Optional[float]
    risk_reward: Optional[float]
    risk_level: str
    reasons: list[str]
    indicators_used: list[str]

    # Market structure
    market_trend: str              # BULLISH/BEARISH/NEUTRAL
    swing_highs: int
    swing_lows: int
    bos_count: int
    choch_count: int
    fvg_count: int
    liquidity_sweeps: int

    # Multi-timeframe
    h1_signal: str
    h4_signal: str
    d1_signal: str

    # AI
    ai_confidence: Optional[float]
    ai_accuracy: Optional[float]
    shap_reasons: list[str]
    shap_summary: Optional[str]
    feature_contributions: Optional[dict]
    explanation_reason: Optional[str]

    # Trade setup
    lot_size: Optional[float]
    trade_quality: str
    signal_id: Optional[str]
    quant_strategy: Optional[dict]
    composite_score: Optional[float]
    confidence_breakdown: Optional[dict]
    confidence_label: Optional[str]
    market_regime: Optional[str]
    strategy_mode: Optional[str]
    regime_reason: Optional[str]

    # Macro bias
    macro_bias: Optional[str]
    macro_strength: Optional[float]
    macro_confidence: Optional[float]
    macro_reason: Optional[str]

    # Final decision
    final_decision: Optional[str]  # BUY/SELL/WAIT/HEDGE
    decision_reason: Optional[str]
    conflict_detected: Optional[bool]
```

---

## Composite Score

Bobot komponen dalam composite score:

| Komponen | Bobot | Sumber |
|----------|-------|--------|
| Market Structure | 35% | BOS, CHOCH, FVG |
| Momentum | 20% | RSI |
| Trend | 15% | EMA alignment |
| Volatility | 10% | ADX |
| AI Prediction | 20% | XGBoost confidence |

Confidence label: LOW (< 55), MEDIUM (55-74), HIGH (>= 75)

---

## Market Regime Detection

| Regime | Kondisi | Strategy Mode |
|--------|---------|---------------|
| TRENDING | ADX >= 25 + BOS | trend_following |
| REVERSAL | RSI > 70 atau < 30 | breakout |
| RANGE | ADX <= 15 + no BOS/CHOCH | mean_reversion |
| VOLATILE | Tidak memenuhi di atas | adaptive |

---

## Final Decision Engine

**File**: `apps/api/src/final_decision.py`

Menentukan keputusan akhir (BUY/SELL/WAIT/HEDGE) berdasarkan semua input.

**Prioritas Keputusan**:
1. Macro override (strong macro overrides weak technical).
2. Conflict -> HEDGE (konservatif).
3. Strong technical signal (confidence >= 70).
4. Moderate technical dengan macro support.
5. Low confidence -> WAIT.

---

## API Endpoints

### Basic Signal

```
GET /api/v1/signals/{symbol}?timeframe=H1&account_balance=10000
```

### Unified Signal

```
GET /api/v1/unified-signal/{symbol}?timeframe=H1&include_ai=true
```
