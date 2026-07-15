"""Weighting Validation — Macro Bias Engine.

Validasi apakah bobot MacroBiasEngine saat ini (H4=2pt, D1=3pt, RSI=1pt)
benar correlated dengan pergerakan harga forward.

Methodology:
  1. Query D1 data dari database (6 bulan)
  2. Untuk setiap bar, hitung macro_bias menggunakan trend SMA + RSI
  3. Hitung forward return (N bars ke depan)
  4. Bandingkan macro_bias vs actual return
  5. Hitung metrik: accuracy, precision, recall, confusion matrix
"""

import asyncio
import sys
from collections import Counter

sys.path.insert(0, "apps/api")
sys.path.insert(0, ".")

import numpy as np
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import OHLC, Symbol
from sqlalchemy import select

from apps.api.src.macro_bias import MacroBiasEngine

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

FORWARD_BARS_LIST = [5, 10, 20]  # D1 bars to look forward
FORWARD_THRESHOLD = 0.002  # 0.2% minimum return to count as up/down
MIN_HISTORY = 50  # minimum SMA50 requires 50 bars


# ──────────────────────────────────────────────
# Backtest Logic
# ──────────────────────────────────────────────

def compute_trend(closes):
    """Infer trend from close prices (mirror of _get_trend_from_df)."""
    if len(closes) < 20:
        return "NEUTRAL"
    sma20 = np.mean(closes[-20:])
    sma50 = np.mean(closes[-50:]) if len(closes) >= 50 else sma20
    current = closes[-1]
    if current > sma20 > sma50:
        return "BULLISH"
    if current < sma20 < sma50:
        return "BEARISH"
    return "NEUTRAL"


def compute_rsi(closes, period=14):
    """Simple RSI computation."""
    if len(closes) < period + 1:
        return 50.0
    deltas = np.diff(closes[-(period + 1):])
    gains = deltas[deltas > 0].sum()
    losses = -deltas[deltas < 0].sum()
    if losses == 0:
        return 100.0
    rs = gains / losses
    return 100.0 - (100.0 / (1.0 + rs))


def forward_return(closes, idx, forward_bars):
    """Compute forward return from idx to idx + forward_bars."""
    if idx + forward_bars >= len(closes):
        return None
    return (closes[idx + forward_bars] / closes[idx]) - 1.0


async def validate_symbol(symbol_name, closes, timestamps):
    """Run macro bias validation for one symbol."""
    engine = MacroBiasEngine()
    results = []

    # From bar 50 onwards (need SMA50)
    for i in range(MIN_HISTORY, len(closes)):
        data_slice = closes[:i + 1]
        current_price = closes[i]

        # Trend pada H4 dan D1 level
        # For simplicity, we use D1 closes for both H4 and D1 trend
        trend_h4 = compute_trend(data_slice)
        trend_d1 = compute_trend(data_slice)

        # RSI
        rsi = compute_rsi(data_slice)

        # Run macro engine
        macro = engine.analyze(
            trend_h4=trend_h4,
            trend_d1=trend_d1,
            rsi_h4=rsi,
            rsi_d1=rsi,
            adx_h4=None,
            adx_d1=None,
        )

        results.append({
            "date": timestamps[i],
            "price": current_price,
            "macro_bias": macro["macro_bias"],
            "macro_strength": macro["macro_strength"],
            "macro_confidence": macro["macro_confidence"],
            "trend_d1": trend_d1,
            "rsi": rsi,
        })

    # Add forward returns
    for fb in FORWARD_BARS_LIST:
        for i, r in enumerate(results):
            idx = MIN_HISTORY + i
            ret = forward_return(closes, idx, fb)
            if ret is not None:
                r[f"fwd_ret_{fb}"] = ret
                r[f"fwd_dir_{fb}"] = (
                    "UP" if ret > FORWARD_THRESHOLD
                    else "DOWN" if ret < -FORWARD_THRESHOLD
                    else "FLAT"
                )
            else:
                r[f"fwd_ret_{fb}"] = None
                r[f"fwd_dir_{fb}"] = None

    return results


def compute_metrics(results, forward_bars):
    """Compute accuracy metrics for a specific forward horizon."""
    field = f"fwd_dir_{forward_bars}"

    # Filter valid entries
    valid = [r for r in results if r[field] is not None]
    total = len(valid)
    if total == 0:
        return {"total": 0}

    correct = 0
    confused = Counter()
    bias_dist = Counter()
    dir_dist = Counter()

    for r in valid:
        bias = r["macro_bias"]
        direction = r[field]
        bias_dist[bias] += 1
        dir_dist[direction] += 1

        if bias == "NEUTRAL":
            continue  # NEUTRAL tidak dianggap "correct"

        if (bias == "BULLISH" and direction == "UP") or \
           (bias == "BEARISH" and direction == "DOWN"):
            correct += 1
        else:
            confused[(bias, direction)] += 1

    non_neutral = bias_dist.get("BULLISH", 0) + bias_dist.get("BEARISH", 0)
    non_neutral_valid = sum(
        1 for r in valid
        if r["macro_bias"] != "NEUTRAL" and r[field] is not None
    )

    return {
        "total": total,
        "non_neutral": non_neutral,
        "non_neutral_valid": non_neutral_valid,
        "correct": correct,
        "accuracy": (
            correct / non_neutral_valid
            if non_neutral_valid > 0
            else 0
        ),
        "bias_distribution": dict(bias_dist),
        "direction_distribution": dict(dir_dist),
        "confusion": dict(confused),
    }


def print_results(symbol_name, results, metrics_all):
    """Pretty print validation results."""
    print(f"\n{'=' * 70}")
    print(f"  {symbol_name} — Macro Bias Weighting Validation")
    print(f"{'=' * 70}")
    print(f"  Data points: {len(results)}")
    print(f"  Date range:  {results[0]['date']} - {results[-1]['date']}")

    # Bias distribution
    bias_counts = Counter(r["macro_bias"] for r in results)
    total = sum(bias_counts.values())
    print("\n  Bias Distribution:")
    for bias in ["BULLISH", "BEARISH", "NEUTRAL"]:
        cnt = bias_counts.get(bias, 0)
        pct = cnt / total * 100 if total else 0
        print(f"    {bias:<10} {cnt:>5} ({pct:>5.1f}%)")

    for fb in FORWARD_BARS_LIST:
        m = metrics_all[fb]
        print(f"\n  Forward {fb} bars (~{fb} days):")
        if m["total"] == 0:
            print("    No valid data")
            continue
        print(f"    Non-neutral predictions: {m['non_neutral_valid']}")
        print(f"    Correct:                 {m['correct']}")
        print(f"    Accuracy:                {m['accuracy']*100:.1f}%")

        if m.get("confusion"):
            print("    Confusion (bias -> actual):")
            for (bias, actual), cnt in sorted(
                m["confusion"].items(), key=lambda x: -x[1]
            )[:5]:
                print(f"      {bias:<10} -> {actual:<5} : {cnt}")


async def main():
    print("=" * 70)
    print("  MACRO BIAS WEIGHTING VALIDATION")
    print("=" * 70)

    async with async_session_factory() as session:
        result = await session.execute(
            select(Symbol).where(Symbol.is_active.is_(True))
        )
        symbols = result.scalars().all()

    all_metrics = {
        fb: {"total_correct": 0, "total_valid": 0}
        for fb in FORWARD_BARS_LIST
    }

    for sym in symbols:
        # Query all D1 data
        async with async_session_factory() as session:
            result = await session.execute(
                select(OHLC)
                .where(
                    OHLC.symbol_id == sym.id,
                    OHLC.timeframe == "D1",
                )
                .order_by(OHLC.timestamp.asc())
            )
            rows = result.scalars().all()

        if len(rows) < MIN_HISTORY:
            label = f"{sym.name}: only {len(rows)} rows"
            print(f"\n  {label} (min {MIN_HISTORY}) — skipped")
            continue

        closes = np.array([float(r.close) for r in rows])
        timestamps = [r.timestamp for r in rows]

        results = await validate_symbol(sym.name, closes, timestamps)
        metrics = {
            fb: compute_metrics(results, fb)
            for fb in FORWARD_BARS_LIST
        }
        print_results(sym.name, results, metrics)

        # Aggregate
        for fb in FORWARD_BARS_LIST:
            m = metrics[fb]
            all_metrics[fb]["total_correct"] += m.get("correct", 0)
            all_metrics[fb]["total_valid"] += m.get("non_neutral_valid", 0)

    # Overall summary
    sep = "=" * 70
    print(f"\n{sep}")
    print("  OVERALL SUMMARY \u2014 All Symbols")
    print(sep)
    for fb in FORWARD_BARS_LIST:
        m = all_metrics[fb]
        if m["total_valid"] > 0:
            acc = m["total_correct"] / m["total_valid"] * 100
            msg = (
                f"  Forward {fb:>2} bars: {m['total_correct']}/"
                f"{m['total_valid']} correct = {acc:.1f}%"
            )
            print(msg)
        else:
            nvd = f"  Forward {fb:>2} bars: no valid data"
            print(nvd)


if __name__ == "__main__":
    asyncio.run(main())
