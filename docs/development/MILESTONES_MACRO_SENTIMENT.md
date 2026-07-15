# Milestone Implementasi — Macro Sentiment Engine

## Ringkasan

Dokumen ini membagi implementasi Macro Sentiment Engine menjadi 4 milestone yang dapat diuji dan divalidasi secara independen. Setiap milestone memiliki acceptance criteria, test plan, dan exit gate.

---

## Milestone 1: Core Engine (MacroBiasEngine)

**Fokus**: Implementasi class `MacroBiasEngine` dengan 4 method analisis.

### Scope

| Komponen | Status |
| -------- | ------ |
| `MacroBiasEngine.analyze()` | Implemented |
| `MacroBiasEngine._determine_bias()` | Implemented |
| `MacroBiasEngine._calculate_strength()` | Implemented |
| `MacroBiasEngine._calculate_confidence()` | Implemented |
| `MacroBiasEngine._generate_reason()` | Implemented |

### Acceptance Criteria

| ID | Kriteria | Cara Uji |
| -- | -------- | -------- |
| M1.1 | Engine menghasilkan macro_bias (BULLISH/BEARISH/NEUTRAL) | Unit test input -> output |
| M1.2 | Nilai bias konsisten dengan bobot PRD (H4=2pt, D1=3pt, RSI H4=1pt, RSI D1=1.5pt) | Unit test setiap kombinasi |
| M1.3 | macro_strength dalam rentang 0-100 | Assert boundary |
| M1.4 | macro_confidence dalam rentang 0-100 | Assert boundary |
| M1.5 | macro_reason tidak kosong untuk semua input valid | Assert string length |
| M1.6 | Fallback NEUTRAL ketika exception terjadi | Mock error pada internal method |

### Test Plan

```python
# File: tests/test_macro_bias_engine.py (dedicated)

test_bias_trend_agreement       # H4 & D1 same direction -> same bias
test_bias_trend_conflict         # H4 bullish + D1 bearish -> NEUTRAL
test_bias_rsi_reinforcement      # RSI H4 > 55 adds weight to BULLISH
test_bias_nuetral_no_data        # All neutral input -> NEUTRAL
test_strength_adx_high           # ADX >= 30 contributes full points
test_strength_adx_low            # ADX < 20 contributes minimum points
test_strength_volatility_penalty # Volatility > threshold reduces strength
test_confidence_alignment_bonus  # H4 == D1 direction gives +30
test_confidence_adx_confirmation # ADX >= 25 adds confirmation points
test_confidence_base_minimum     # No data should give base 30
test_fallback_on_exception       # Exception -> NEUTRAL fallback
test_reason_not_empty            # Reason string is always populated
```

### Exit Gate

- [ ] Semua unit test M1 lulus
- [ ] Coverage engine >= 90%
- [ ] Input edge case (None values) handled gracefully

---

## Milestone 2: Integrasi dengan UnifiedSignalPipeline

**Fokus**: Menghubungkan MacroBiasEngine ke `UnifiedSignalGenerator._analyze_macro()`.

### Scope

| Komponen | Status |
| -------- | ------ |
| `UnifiedSignalGenerator._analyze_macro()` di unified_signal.py | Implemented |
| H4/D1 data fetching dari collector | Implemented |
| Indicator computation untuk H4/D1 | Implemented |
| Passing macro_result ke UnifiedSignal constructor | Implemented |
| Router: macro fields di API response | Implemented |

### Acceptance Criteria

| ID | Kriteria | Cara Uji |
| -- | -------- | -------- |
| M2.1 | H4 dan D1 indicators dikomputasi tanpa crash | Integration test |
| M2.2 | `_get_trend_from_df()` mengembalikan BULLISH/BEARISH/NEUTRAL | Unit test dengan sample OHLC |
| M2.3 | Macro fields muncul di API response `/api/v1/unified-signal/{symbol}` | E2E test |
| M2.4 | Null safety: jika df_h4 kosong, macro_result tetap NEUTRAL | Edge case test |
| M2.5 | Exception di wrapped: error di macro tidak crash kan pipeline | Integration test |

### Test Plan

```python
# File: tests/test_macro_integration.py (dedicated)

test_analyze_macro_returns_all_fields  # _analyze_macro returns 4 fields
test_get_trend_bullish                 # SMA 20 < SMA 50 < current -> BULLISH
test_get_trend_bearish                 # SMA 20 > SMA 50 > current -> BEARISH
test_get_trend_neutral                 # Mixed direction -> NEUTRAL
test_get_trend_empty_df                # Empty df -> NEUTRAL fallback
test_macro_fields_in_api_response      # API response contains macro_bias etc.
test_macro_does_not_crash_pipeline     # Error in macro = graceful fallback
test_macro_result_passed_to_constructor # UnifiedSignal receives macro fields
```

### Exit Gate

- [ ] Semua integration test M2 lulus
- [ ] Response API tervalidasi includes `macro_bias`, `macro_strength`, `macro_confidence`, `macro_reason`
- [ ] Pipeline tetap berjalan walau data H4/D1 tidak tersedia

---

## Milestone 3: Final Decision & Conflict Handling

**Fokus**: FinalDecisionEngine dengan conflict detection, macro override, dan fallback.

### Scope

| Komponen | Status |
| -------- | ------ |
| `FinalDecisionEngine.decide()` | Implemented |
| `_detect_conflict()` logic | Implemented |
| `_resolve_decision()` priority chain | Implemented |
| 4 decision types (BUY/SELL/WAIT/HEDGE) | Implemented |
| Macro override condition | Implemented |

### Acceptance Criteria

| ID | Kriteria | Cara Uji |
| -- | -------- | -------- |
| M3.1 | Teknikal BUY + Makro BULLISH = BUY (aligned) | Unit test |
| M3.2 | Teknikal BUY + Makro BEARISH + confidence >= 30 = HEDGE (conflict) | Unit test |
| M3.3 | Teknikal lemah + Makro kuat = Ikut makro (override) | Unit test |
| M3.4 | Semua input NEUTRAL = WAIT | Unit test |
| M3.5 | conflict_detected = True hanya saat konflik signifikan | Unit test setiap skenario |
| M3.6 | Fallback WAIT ketika exception terjadi | Mock error test |
| M3.7 | priority chain benar: override > conflict > normal > wait | Integration test |

### Test Plan

```python
# File: tests/test_final_decision.py (dedicated)

# Scenario-based tests
test_aligned_bullish       # BUY + BULLISH -> BUY, no conflict
test_aligned_bearish       # SELL + BEARISH -> SELL, no conflict
test_conflict_buy_bearish  # BUY + BEARISH -> HEDGE, conflict
test_conflict_sell_bullish # SELL + BULLISH -> HEDGE, conflict
test_macro_override        # Weak tech + strong macro -> macro direction
test_all_neutral           # All NEUTRAL/zero -> WAIT
test_low_confidence        # Tech NEUTRAL + low conf -> WAIT

# Priority chain tests
test_priority_override_over_conflict  # Override happens before conflict check
test_priority_strong_technical        # Strong tech 70%+ takes priority
test_priority_moderate_with_support   # Moderate tech + macro support = BUY/SELL
test_priority_moderate_no_support     # Moderate tech + no support = cautious signal

# Edge case tests
test_conflict_low_macro_confidence    # Macro conf < 30 = no conflict
test_conflict_low_macro_strength      # Macro strength < 20 = no conflict
test_exception_fallback               # Exception -> WAIT
test_detect_conflict_boundary         # Boundary: conf=30, strength=20
```

### Exit Gate

- [ ] Semua unit test M3 lulus
- [ ] 4 decision type (BUY/SELL/WAIT/HEDGE) tervalidasi
- [ ] Priority chain tervalidasi (override > conflict > normal > wait)
- [ ] Edge case: macro_confidance=29, strength=19 -> no conflict (boundary test)

---

## Milestone 4: Dashboard & E2E Validation

**Fokus**: Visualisasi macro sentiment dan final decision di frontend.

### Scope

| Komponen | Status |
| -------- | ------ |
| Macro Sentiment card di signals/page.tsx | Implemented |
| Final Decision banner di signals/page.tsx | Implemented |
| Conflict badge | Implemented |
| Conditional rendering (null safety) | Implemented |

### Acceptance Criteria

| ID | Kriteria | Cara Uji |
| -- | -------- | -------- |
| M4.1 | Macro bias ditampilkan dengan warna (hijau/merah/netral) | Visual check |
| M4.2 | Macro confidence dan strength tampil sebagai angka | Visual check |
| M4.3 | Final Decision banner muncul dengan warna sesuai jenis | Visual check |
| M4.4 | Conflict badge muncul hanya saat conflict_detected = True | Visual check |
| M4.5 | Semua field null-safe — tidak crash saat data tidak lengkap | Render test |
| M4.6 | Responsive layout — tidak rusak di mobile | Visual check (375px) |

### Test Plan

```typescript
// Visual validation checklist

test_macro_bias_card_renders         // Macro card muncul di DOM
test_macro_bias_color_bullish        // BULLISH = green text
test_macro_bias_color_bearish        // BEARISH = red text
test_final_decision_banner_renders   // Banner muncul di DOM
test_final_decision_color_buy        // BUY = green border
test_final_decision_color_hedge      // HEDGE = purple border
test_conflict_badge_visible          // Badge visible only when conflict
test_macro_bias_hidden_when_null     // No macro data = card not rendered
test_null_safety                     // All optional fields = no crash
```

### Exit Gate

- [ ] Semua visual check M4 lulus
- [ ] Responsive test di 375px, 768px, 1024px tidak ada overlap/overflow
- [ ] Null safety: hapus semua field macro dari response API -> dashboard tidak crash

---

## Ringkasan Milestone

| Milestone | Komponen | File Utama | Test File |
| --------- | -------- | ---------- | --------- |
| M1 | Core Engine | `macro_bias.py` | `tests/test_macro_bias_engine.py` |
| M2 | Pipeline Integration | `unified_signal.py` | `tests/test_macro_integration.py` |
| M3 | Final Decision | `final_decision.py` | `tests/test_final_decision.py` |
| M4 | Dashboard | `signals/page.tsx` | Visual checklist |

## Alur Validasi

```
M1 Lulus? → M2 Lulus? → M3 Lulus? → M4 Lulus? → RELEASE
   ↓            ↓            ↓            ↓
  Fix          Fix          Fix          Fix
```

Setiap milestone WAJIB lulus sebelum melanjutkan ke milestone berikutnya.
Jika milestone gagal, regression test harus dijalankan ulang setelah fix.
