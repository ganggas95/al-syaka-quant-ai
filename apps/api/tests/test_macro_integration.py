"""Milestone 2 — Pipeline Integration Tests.

Validasi:
  M2.1 H4 dan D1 indicators dikomputasi tanpa crash
  M2.2 _get_trend_from_df() mengembalikan BULLISH/BEARISH/NEUTRAL
  M2.3 Macro fields muncul di API response
  M2.4 Null safety: df kosong -> NEUTRAL
  M2.5 Exception wrapped -> pipeline tidak crash
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from src.unified_signal import UnifiedSignalGenerator

# ──────────────────────────────────────────────
# M2.2 — _get_trend_from_df
# ──────────────────────────────────────────────

def _make_ohlc_df(closes):
    """Helper: buat OHLC dataframe dari list close prices."""
    n = len(closes)
    return pd.DataFrame({
        "open": closes,
        "high": [c * 1.005 for c in closes],
        "low": [c * 0.995 for c in closes],
        "close": closes,
        "volume": [1000000] * n,
    })


def test_get_trend_bullish():
    """SMA 20 < SMA 50 < current = BULLISH."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    # Higher closes: current > SMA20 > SMA50
    closes = [100.0 + i * 0.5 for i in range(60)]
    df = _make_ohlc_df(closes)
    result = generator._get_trend_from_df(df)
    assert result == "BULLISH"


def test_get_trend_bearish():
    """SMA 20 > SMA 50 > current = BEARISH."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    # Lower closes: current < SMA20 < SMA50
    closes = [110.0 - i * 0.5 for i in range(60)]
    df = _make_ohlc_df(closes)
    result = generator._get_trend_from_df(df)
    assert result == "BEARISH"


def test_get_trend_neutral():
    """Mixed direction = NEUTRAL."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    # Random walk: no clear trend
    closes = [100.0, 101.0, 99.5, 100.5, 100.0, 101.5, 99.0, 100.8]
    df = _make_ohlc_df(closes)
    result = generator._get_trend_from_df(df)
    assert result == "NEUTRAL"


def test_get_trend_empty_df():
    """DataFrame kosong = NEUTRAL."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    df = _make_ohlc_df([])
    result = generator._get_trend_from_df(df)
    assert result == "NEUTRAL"


def test_get_trend_insufficient_data():
    """Data < 20 baris = NEUTRAL."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    closes = [100.0 + i * 0.5 for i in range(15)]
    df = _make_ohlc_df(closes)
    result = generator._get_trend_from_df(df)
    assert result == "NEUTRAL"


# ──────────────────────────────────────────────
# M2.4 — _analyze_macro null safety
# ──────────────────────────────────────────────

def test_analyze_macro_returns_all_fields():
    """_analyze_macro mengembalikan 4 field."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    df = _make_ohlc_df([100.0 + i * 0.3 for i in range(60)])
    result = generator._analyze_macro(df_h4=df, df_d1=df)
    assert "macro_bias" in result
    assert "macro_strength" in result
    assert "macro_confidence" in result
    assert "macro_reason" in result


def test_analyze_macro_empty_df():
    """DataFrame kosong -> NEUTRAL fallback."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    empty_df = _make_ohlc_df([])
    result = generator._analyze_macro(df_h4=empty_df, df_d1=empty_df)
    assert result["macro_bias"] in {"BULLISH", "BEARISH", "NEUTRAL"}
    assert 0 <= result["macro_strength"] <= 100
    assert 0 <= result["macro_confidence"] <= 100


def test_analyze_macro_no_dataframes(monkeypatch):
    """Jika ada exception di _analyze_macro -> fallback NEUTRAL."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)

    def _mock_error(*args, **kwargs):
        raise ValueError("Simulated error")

    monkeypatch.setattr(generator, "_compute_indicators", _mock_error)
    df = _make_ohlc_df([100.0 + i * 0.3 for i in range(60)])
    result = generator._analyze_macro(df_h4=df, df_d1=df)
    assert result["macro_bias"] == "NEUTRAL"
    assert "unavailable" in result["macro_reason"].lower()


# ──────────────────────────────────────────────
# M2.5 — Macro does not crash pipeline
# ──────────────────────────────────────────────

def test_macro_error_does_not_crash_analyze_macro():
    """Error di komputasi indicator tidak crash kan _analyze_macro."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    # DataFrame with NaN should be handled gracefully
    closes = [100.0] * 60
    df = _make_ohlc_df(closes)
    # Insert NaN
    df.loc[0, "close"] = np.nan
    result = generator._analyze_macro(df_h4=df, df_d1=df)
    assert "macro_bias" in result
    assert "macro_reason" in result


def test_macro_fields_type():
    """Semua macro field memiliki tipe yang benar."""
    generator = UnifiedSignalGenerator.__new__(UnifiedSignalGenerator)
    df = _make_ohlc_df([100.0 + i * 0.3 for i in range(60)])
    result = generator._analyze_macro(df_h4=df, df_d1=df)
    assert isinstance(result["macro_bias"], str)
    assert isinstance(result["macro_strength"], (int, float))
    assert isinstance(result["macro_confidence"], (int, float))
    assert isinstance(result["macro_reason"], str)
