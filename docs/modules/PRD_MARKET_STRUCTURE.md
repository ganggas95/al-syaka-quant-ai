# Market Structure Engine

## Ringkasan

Market Structure Engine mendeteksi struktur pasar berdasarkan analisis swing points, pola harga, dan level-level kunci. Engine ini mengimplementasikan konsep Smart Money Concepts (SMC) dan Price Action Analysis.

Package: `apps/api/src/market_structure/`

---

## Komponen

### 1. MarketStructureDetector

**File**: `apps/api/src/market_structure/structures.py`

Detektor struktur pasar yang mengidentifikasi swing points dan pola-pola struktur.

**Swing Point Detection**:
```python
class MarketStructureDetector:
    def __init__(self, swing_lookback: int = 5):
        # swing_lookback = jumlah candle yang dilihat ke kiri/kanan untuk konfirmasi
```

**Metode**:
- `find_swing_highs(high)` -- Mencari local maxima (swing high)
- `find_swing_lows(low)` -- Mencari local minima (swing low)
- `classify_swing_points(highs, lows)` -- Mengklasifikasi HH/HL/LH/LL

**Klasifikasi Swing Points**:

| Label | Arti | Kondisi |
|-------|------|---------|
| HH | Higher High | Swing high > previous swing high |
| LH | Lower High | Swing high < previous swing high |
| HL | Higher Low | Swing low > previous swing low |
| LL | Lower Low | Swing low < previous swing low |

**Break of Structure (BOS)**:
- BOS_HIGH: Ketika harga menembus swing high sebelumnya (HH).
- BOS_LOW: Ketika harga menembus swing low sebelumnya (LL).

**Change of Character (CHOCH)**:
- CHOCH_UP: Transisi dari downtrend ke uptrend (LL -> HL, LH -> HH).
- CHOCH_DOWN: Transisi dari uptrend ke downtrend (HH -> LH, HL -> LL).

**Output**:
```python
{
    "swing_highs": [{"index": int, "price": float, "label": "HH|LH"}],
    "swing_lows": [{"index": int, "price": float, "label": "HL|LL"}],
    "break_of_structure": [{"type": "BOS_HIGH|BOS_LOW", "index": int, "price": float}],
    "change_of_character": [{"type": "CHOCH_UP|CHOCH_DOWN", "index": int, "price": float}],
    "current_trend": "BULLISH|BEARISH|NEUTRAL"
}
```

---

### 2. Fair Value Gap (FVG) Detection

**File**: `apps/api/src/market_structure/fvg.py`

Mendeteksi Fair Value Gap (ketidakseimbangan antara candle berurutan).

**Bullish FVG**: Low candle saat ini > High candle sebelumnya (gap up).
**Bearish FVG**: High candle saat ini < Low candle sebelumnya (gap down).

```python
def detect_fvg(high, low, close, min_gap_pips=0.0001) -> List[dict]:
```

**Output**:
```python
{
    "type": "BULLISH_FVG|BEARISH_FVG",
    "index": int,
    "gap_high": float,
    "gap_low": float,
    "filled": bool  # Apakah gap sudah ditutup
}
```

---

### 3. Liquidity Sweep Detection

**File**: `apps/api/src/market_structure/liquidity.py`

Mendeteksi liquidity sweep (harga menembus level tinggi/rendah sebelumnya lalu berbalik).

**Sweep High**: Harga naik di atas recent high lalu ditutup di bawah high tersebut.
**Sweep Low**: Harga turun di bawah recent low lalu ditutup di atas low tersebut.

```python
def detect_liquidity_sweep(high, low, close, lookback=20) -> List[dict]:
```

**Output**:
```python
{
    "type": "SWEEP_HIGH|SWEEP_LOW",
    "index": int,
    "swept_level": float,  # Level yang disapu
    "high_reached/low_reached": float,  # Ekstrem yang dicapai
    "close": float  # Harga penutupan
}
```

---

### 4. Support & Resistance Detection

**File**: `apps/api/src/market_structure/suport_resistance.py`

Mendeteksi level support dan resistance horizontal menggunakan density-based clustering pada swing points.

```python
class SupportResistanceDetector:
    def __init__(self, n_clusters=10, min_touches=2):
        # n_clusters: jumlah klaster level harga
        # min_touches: minimum sentuhan untuk dianggap valid
```

**Metode**:
1. Temukan swing highs dan swing lows pada data.
2. Cluster harga swing points ke dalam bins (n_clusters).
3. Level dengan sentuhan >= min_touches dianggap valid.
4. Klasifikasikan sebagai resistance (swing high) atau support (swing low).

**Output**:
```python
{
    "resistances": [{"price": float, "touches": int}, ...],  # Top 5
    "supports": [{"price": float, "touches": int}, ...]      # Top 5
}
```

---

## API Endpoint

### Market Structure Analysis

```
GET /api/v1/market-structure/{symbol}?timeframe=H1&limit=200
```

Response mencakup semua komponen market structure:
- `current_trend`: BULLISH, BEARISH, NEUTRAL
- `swing_highs`, `swing_lows`: Daftar swing points
- `break_of_structure`: Daftar BOS
- `change_of_character`: Daftar CHOCH
- `fair_value_gaps`: Daftar FVG
- `liquidity_sweeps`: Daftar liquidity sweeps
- `support_resistance`: Level S/R
- `ohlc`: Data harga untuk charting

---

## Integrasi dengan Engine Lain

```
[MarketStructureDetector] -- Swing points, trend, BOS, CHOCH
         |
         +---> [ProbabilityEngine] -- 25% bobot dalam scoring
         |
         +---> [UnifiedSignalGenerator] -- Market trend, BOS/CHOCH count
         |
         +---> [CompositeScore] -- Market structure component (35% bobot)
         |
         +---> [Market Regime Detection] -- Trending vs Range vs Reversal
```

Market structure digunakan oleh:
1. **Statistical Engine**: 25% bobot dalam kalkulasi probabilitas.
2. **Unified Signal Generator**: Menyediakan konteks struktur pasar.
3. **Composite Score**: 35% bobot dalam perhitungan composite score.
4. **Market Regime**: Membantu deteksi regime pasar (trending, reversal, range).
5. **Support & Resistance**: Digunakan untuk penentuan level SL/TP.
