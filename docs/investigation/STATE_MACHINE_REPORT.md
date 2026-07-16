# State Machine Report
**Date**: 2026-07-16
**Component**: BacktestEngine Trade Lifecycle

---

## State Diagram

```
                    ┌─────────────────┐
                    │     READY       │
                    │ (No Open Trade) │
                    └────────┬────────┘
                             │ Signal Detected
                             ▼
                    ┌─────────────────┐
                    │  OPEN TRADE     │
                    │  entry_price    │
                    │  stop_loss      │
                    │  take_profit    │
                    │  lot_size       │
                    │  result=PENDING │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    MANAGE       │
                    │  ┌───────────┐  │
                    │  │ SL Check  │──│──▶ SL_HIT
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │ TP Check  │──│──▶ TP_HIT
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │ Breakeven │──│──▶ SL moved to entry
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │Partial TP │──│──▶ Partial close + SL move
                    │  └───────────┘  │
                    │  ┌───────────┐  │
                    │  │ Trailing  │──│──▶ SL trails price
                    │  └───────────┘  │
                    └────────┬────────┘
                             │ Exit Condition Met
                             ▼
                    ┌─────────────────┐
                    │  EXIT TRADE     │
                    │  exit_price     │
                    │  exit_time      │
                    │  result=WIN/LOSS│
                    │  profit calc    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   RECORD        │
                    │  daily_pnl +=   │
                    │  weekly_pnl +=  │
                    │  consec_loss++  │
                    │  or reset to 0  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     READY       │◄── Back to loop
                    └─────────────────┘
```

---

## State Validation

### OPEN State
[`engine.py` lines 590-716](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L590-L716)

| Property | Set? | Value Source |
|----------|------|-------------|
| entry_time | ✅ | `row["timestamp"]` (current bar) |
| signal | ✅ | Strategy output (BUY/SELL) |
| entry_price | ✅ | Signal entry price |
| stop_loss | ✅ | Entry ± ATR × SL multiplier |
| take_profit | ✅ | Entry ± ATR × TP multiplier |
| lot_size | ✅ | Risk-based calculation |
| direction | ✅ | Derived from signal |
| result | ✅ | "PENDING" |
| confidence | ✅ | From signal |
| session | ✅ | `get_session_name()` |
| regime | ✅ | Detected regime |
| strategy | ✅ | Strategy name |
| macro_bias | ✅ | From macro engine |

### MANAGE State
[`engine.py` lines 718-837](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L718-L837)

#### State Transitions in MANAGE

```
MANAGE
  │
  ├── Breakeven Check
  │   └── If profit_atr ≥ breakeven_atr → SL = entry, exit_reason = "BREAKEVEN"
  │
  ├── Partial TP Check
  │   └── If profit_atr ≥ p_atr AND not partial_closed
  │       → lot_size *= (1 - ratio), partial_closed = true
  │       → SL = entry ± 0.1 × ATR
  │
  ├── Trailing Stop Check
  │   └── If profit_atr ≥ trail_activation_atr
  │       → trailing_active = true
  │       → Update peak_price
  │       → Update SL based on trail_mode (chandelier/fixed)
  │
  ├── SL Hit Check
  │   └── If low ≤ SL (LONG) / high ≥ SL (SHORT)
  │       → EXIT state
  │
  └── TP Hit Check
      └── If high ≥ TP (LONG) / low ≤ TP (SHORT)
          → EXIT state
```

### EXIT State
[`engine.py` lines 814-837](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L814-L837)

| Exit Reason | Condition | Priority |
|-------------|-----------|----------|
| `SL_HIT` | Low ≤ SL (LONG) / High ≥ SL (SHORT) | Normal |
| `TP_HIT` | High ≥ TP (LONG) / Low ≤ TP (SHORT) | Normal |
| `BREAKEVEN` | SL moved to entry (via breakeven rule) | Override |
| `PARTIAL_TP` | Partial close executed | Override |
| `TRAILING` | Trailing stop updated SL | Override |
| `END_OF_DATA` | Loop ended, force close | Fallback |

**Priority override logic**: (BREAKEVEN, PARTIAL_TP, TRAILING) akan override SL_HIT:
```python
if t.exit_reason not in ("BREAKEVEN", "PARTIAL_TP", "TRAILING"):
    t.exit_reason = "SL_HIT"
```
[`engine.py` lines 815-816](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L815-L816)

### READY → OPEN Transition
[`engine.py` lines 263-270](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L263-L270)

```python
if len(open_trades) == 0:
    self.total_signal_checks += 1
    signal = self._check_adaptive_signal(ind, df.iloc[i])
    if signal:
        trade = self._open_trade(signal, df.iloc[i], ind)
        open_trades.append(trade)
        self.trades.append(trade)
```

✅ Satu posisi per waktu, tidak ada pyramiding.

---

## State Machine Verification

### Test: OPEN → MANAGE → EXIT → READY

| Step | Action | Expected State | Verified |
|------|--------|---------------|----------|
| 1 | Signal detected | OPEN | ✅ |
| 2 | SL not hit, TP not hit | MANAGE | ✅ |
| 3 | SL hit → exit_price = SL | EXIT → SL_HIT | ✅ |
| 4 | Trade removed from open_trades | READY | ✅ |
| 5 | Next bar, no open position → signal check | READY → OPEN (loop) | ✅ |

### Test: PENDING Trade at End of Data

| Step | Action | Expected State | Verified |
|------|--------|---------------|----------|
| 1 | Loop ends, trade still PENDING | MANAGE (open) | ✅ |
| 2 | Force close at last price | EXIT → END_OF_DATA | ✅ |
| 3 | Result set to PENDING (not WIN/LOSS) | Special case | ✅ |

```python
# engine.py:278-284
for t in open_trades:
    if t.result == "PENDING":
        t.exit_price = df.iloc[-1]["close"]
        t.exit_time = df.iloc[-1]["timestamp"]
        t.result, t.pips, t.profit = self._calculate_result(t)
        t.exit_reason = "END_OF_DATA"
```

⚠️ Note: Di `_calculate_result`, END_OF_DATA menghasilkan result="PENDING":
```python
if trade.exit_reason == "END_OF_DATA":
    result = "PENDING"
```
[`engine.py` lines 864-866](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L864-L866)

Ini berarti **PENDING trade tidak masuk ke statistik WIN/LOSS** — `MetricsCalculator.calculate` memfilter PENDING:
```python
m.total_trades = len([t for t in trades if t.result != "PENDING"])
```

---

## State Machine Issues Found

### Issue 1: Consecutive Loss Lockout (Cross-State)

**Source**: [`engine.py` lines 366-368](file:///Users/nizar/MyProject/al-syaka-quant-ai/apps/backtester/src/al_syaka_backtester/engine.py#L366-L368)

State machine tidak bisa kembali ke READY setelah lockout:
```
EXIT → RECORD (consec_loss = 5) → READY → OPEN (BLOCKED by max_consecutive_losses)
```

Ini adalah **state transition violation** — guard condition di `_check_adaptive_signal` mencegah transisi READY→OPEN, membuat state machine stuck di READY selamanya.

### Issue 2: No Cleanup on Lockout

Tidak ada mekanisme untuk keluar dari lockout. Setelah `consecutive_losses >= 5`, tidak ada:
- Daily reset counter
- Cooldown timer
- Decay factor

---

## Recommendations

1. **Tambahkan cooldown mechanism**: Setelah lockout, tunggu N bar sebelum reset counter
2. **Atau daily reset**: Reset `consecutive_losses` setiap hari baru (bersama `daily_pnl`)
3. **Log state transitions**: Untuk debugging, log setiap state change
4. **Add state machine unit tests**: Verifikasi semua transisi dan edge cases
