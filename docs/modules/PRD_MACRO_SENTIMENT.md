# Macro Bias Engine

## Ringkasan

Macro Bias Engine menyediakan konteks makro untuk sistem sinyal dengan menganalisis kondisi pasar dari timeframe yang lebih tinggi (H4, D1). Engine ini menghasilkan bias makro (bullish, bearish, neutral) beserta tingkat kekuatan dan confidence.

File: `apps/api/src/macro_bias.py`

---

## Tujuan

Sinyal teknikal pada timeframe rendah (H1) bisa menyesatkan tanpa konteks makro yang lebih luas. Macro Bias Engine menambahkan perspektif makro untuk:

- Menghindari sinyal palsu yang berlawanan dengan tren makro.
- Mendeteksi konflik antara sinyal teknikal dan kondisi makro.
- Memberikan bobot tambahan ketika teknikal dan makro searah.
- Menghasilkan keputusan HEDGE ketika terjadi konflik.

---

## MacroBiasEngine

```python
class MacroBiasEngine:
    def analyze(
        self,
        trend_h4: str = "NEUTRAL",    # BULLISH/BEARISH/NEUTRAL
        trend_d1: str = "NEUTRAL",
        rsi_h4: Optional[float] = None,
        rsi_d1: Optional[float] = None,
        adx_h4: Optional[float] = None,
        adx_d1: Optional[float] = None,
        volatility_h4: Optional[float] = None,
        volatility_d1: Optional[float] = None,
    ) -> dict:
```

**Output**:

```python
{
    "macro_bias": "BULLISH|BEARISH|NEUTRAL",
    "macro_strength": 65.5,     # 0-100
    "macro_confidence": 72.0,   # 0-100
    "macro_reason": "Macro bias is bullish (strong, confidence 72%). H4 and D1 both show bullish trend — strong alignment."
}
```

---

## Komponen Analisis

### 1. Bias Determination (`_determine_bias`)

Menentukan arah bias makro dari multi-timeframe trend dan momentum.

**Bobot**:

- Trend H4: 2 poin
- Trend D1: 3 poin
- RSI H4: 1 poin (jika > 55 bullish, < 45 bearish)
- RSI D1: 1.5 poin (jika > 55 bullish, < 45 bearish)

Jika total bullish > bearish -> BULLISH
Jika total bearish > bullish -> BEARISH
Jika sama -> NEUTRAL

### 2. Strength Calculation (`_calculate_strength`)

Mengukur kekuatan keyakinan makro (0-100).

**ADX Contribution**:

- ADX H4 >= 30: +25, >= 20: +15, else: +5
- ADX D1 >= 30: +35, >= 20: +20, else: +10

**Volatility Penalty**:

- Volatilitas H4 > 0.02: -10
- Volatilitas D1 > 0.03: -15

### 3. Confidence Calculation (`_calculate_confidence`)

Mengukur tingkat confidence bias makro (0-100).

**Base**: 30 (selalu ada minimum confidence)
**Trend Alignment**: +30 jika H4 dan D1 searah (sama-sama bullish/bearish)
**Partial Alignment**: +10 jika salah satu timeframe memiliki trend
**ADX Confirmation**: +15 jika ADX H4 >= 25, +25 jika ADX D1 >= 25

---

## Integrasi dengan Unified Signal

Macro Bias Engine diintegrasikan ke dalam Unified Signal Generator:

```python
# Di UnifiedSignalGenerator.generate()
macro_result = self._analyze_macro(df_h4, df_d1)
```

**Data Flow**:

1. Fetch data H4 dan D1 dari collector.
2. Hitung indikator (trend, RSI, ADX, ATR) untuk kedua timeframe.
3. MacroBiasEngine.analyze() menghasilkan bias, strength, confidence.
4. Hasil macro diteruskan ke Final Decision Engine.

**Final Decision Integration**:

| Skenario       | Teknikal    | Makro        | Final Decision   |
| -------------- | ----------- | ------------ | ---------------- |
| Aligned        | BUY         | BULLISH      | BUY (supported)  |
| Aligned        | SELL        | BEARISH      | SELL (supported) |
| Conflict       | BUY         | BEARISH      | HEDGE atau WAIT  |
| Conflict       | SELL        | BULLISH      | HEDGE atau WAIT  |
| Macro Override | Weak signal | Strong macro | Ikut makro       |
| Neutral        | Any         | NEUTRAL      | Ikut teknikal    |

### Conflict Detection

Konflik terjadi ketika:

- Teknikal BUY tapi makro BEARISH (dengan confidence).
- Teknikal SELL tapi makro BULLISH (dengan confidence).
- Macro confidence >= 30 dan strength >= 20.

**Tidak konflik** jika macro cukup kuat untuk override:

- Macro confidence >= 60, strength >= 50, teknikal confidence < 50.

---

## Penggunaan

Macro Bias Engine dipanggil secara internal oleh `UnifiedSignalGenerator._analyze_macro()` yang mengambil data H4 dan D1, menghitung indikator, lalu memanggil `MacroBiasEngine.analyze()`.

Tidak ada API endpoint publik khusus untuk macro bias -- hasilnya disertakan dalam output unified signal.
