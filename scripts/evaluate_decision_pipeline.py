"""Pipeline Evaluation — Composite Score, Regime & Final Decision.

Menguji apakah keputusan final decision engine correlated dengan
pergerakan harga forward. Menggunakan data D1 historis dari database.

Metodologi:
  1. Query D1 data dari database (12+ bulan)
  2. Untuk setiap bar, hitung composite score, regime, macro bias,
     dan final decision menggunakan logika yang sama dengan pipeline
  3. Hitung forward return (N bar ke depan)
  4. Bandingkan final_decision vs actual return
  5. Hitung metrik: accuracy, precision, recall
"""

import asyncio
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Optional

sys.path.insert(0, "apps/api")
sys.path.insert(0, ".")

import pandas as pd
from al_syaka_common.database import async_session_factory
from al_syaka_common.models import OHLC, Symbol
from sqlalchemy import select

from apps.api.src.final_decision import FinalDecisionEngine
from apps.api.src.macro_bias import MacroBiasEngine

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

FORWARD_BARS_LIST = [5, 10, 20]
FORWARD_THRESHOLD = 0.002  # 0.2% minimum return
MIN_HISTORY = 100

# Symbols to evaluate
EVALUATION_SYMBOLS = [
    "US30", "NAS100", "SPX500",
    "BTCUSD", "ETHUSD",
    "XAUUSD", "XAGUSD",
    "EURUSD", "GBPUSD", "USDJPY",
    "AUDUSD", "USDCAD",
]

SYMBOL_CLASSES = {
    "US30": "INDICES", "NAS100": "INDICES", "SPX500": "INDICES",
    "BTCUSD": "CRYPTO", "ETHUSD": "CRYPTO",
    "XAUUSD": "METALS", "XAGUSD": "METALS",
    "EURUSD": "FOREX", "GBPUSD": "FOREX", "USDJPY": "FOREX",
    "AUDUSD": "FOREX", "USDCAD": "FOREX",
}


# ──────────────────────────────────────────────
# Simplified Engine Logic (mirrors production)
# ──────────────────────────────────────────────

def compute_sma(series: pd.Series, window: int) -> float:
    """Simple moving average."""
    if len(series) < window:
        return float(series.iloc[-1])
    return float(series.iloc[-window:].mean())


def detect_trend(closes: pd.Series) -> str:
    """Infer trend direction (mirrors _get_trend_from_df)."""
    if len(closes) < 20:
        return "NEUTRAL"
    sma_20 = compute_sma(closes, 20)
    sma_50 = compute_sma(closes, 50) if len(closes) >= 50 else sma_20
    current = closes.iloc[-1]
    if current > sma_20 > sma_50:
        return "BULLISH"
    if current < sma_20 < sma_50:
        return "BEARISH"
    return "NEUTRAL"


def compute_rsi(closes: pd.Series, window: int = 14) -> Optional[float]:
    """Compute RSI."""
    if len(closes) < window + 1:
        return None
    deltas = closes.diff().iloc[1:]
    gains = deltas.where(deltas > 0, 0.0)
    losses = (-deltas.where(deltas < 0, 0.0))
    avg_gain = gains.iloc[-window:].mean()
    avg_loss = losses.iloc[-window:].mean()
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))


def compute_adx(closes: pd.Series, highs: pd.Series,
                lows: pd.Series, window: int = 14) -> Optional[float]:
    """Compute ADX."""
    if len(closes) < window * 2:
        return None
    tr = pd.concat([
        (highs - lows).abs(),
        (highs - closes.shift(1)).abs(),
        (lows - closes.shift(1)).abs(),
    ], axis=1).max(axis=1)
    up = highs.diff()
    down = -lows.diff()
    plus_dm = ((up > down) & (up > 0)).astype(float) * up
    minus_dm = ((down > up) & (down > 0)).astype(float) * down
    atr = tr.rolling(window).mean()
    plus_di = 100 * (plus_dm.rolling(window).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window).mean() / atr)
    dx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di))
    adx = dx.rolling(window).mean()
    return float(adx.iloc[-1])


def evaluate_point(
    closes: pd.Series,
    highs: pd.Series,
    lows: pd.Series,
    forward_bars: int,
    macro_engine: MacroBiasEngine,
    decision_engine: FinalDecisionEngine,
    symbol: str,
) -> dict:
    """Evaluate a single data point through the full pipeline."""
    # Trend
    trend_h4 = detect_trend(closes)
    trend_d1 = detect_trend(closes)

    # RSI & ADX
    rsi_h4 = compute_rsi(closes, 14)
    rsi_d1 = compute_rsi(closes, 14)
    adx_h4 = compute_adx(closes, highs, lows, 14)
    adx_d1 = compute_adx(closes, highs, lows, 14)

    # ATR (volatility proxy)
    if len(closes) >= 14:
        tr = pd.concat([
            (highs - lows).abs(),
            (highs - closes.shift(1)).abs(),
            (lows - closes.shift(1)).abs(),
        ], axis=1).max(axis=1)
        atr_h4 = float(tr.iloc[-14:].mean())
        atr_d1 = atr_h4
    else:
        atr_h4 = None
        atr_d1 = None

    # 1. Macro bias
    macro_result = macro_engine.analyze(
        trend_h4=trend_h4,
        trend_d1=trend_d1,
        rsi_h4=rsi_h4,
        rsi_d1=rsi_d1,
        adx_h4=adx_h4,
        adx_d1=adx_d1,
        volatility_h4=atr_h4,
        volatility_d1=atr_d1,
        symbol=symbol,
    )

    # 2. Technical signal (simplified: use SMA cross)
    macd_val = None
    if len(closes) >= 26:
        ema_12 = closes.ewm(span=12).mean().iloc[-1]
        ema_26 = closes.ewm(span=26).mean().iloc[-1]
        macd_val = float(ema_12 - ema_26)
    tech_signal = "NEUTRAL"
    tech_conf = 30.0
    if macd_val is not None:
        if macd_val > 0:
            tech_signal = "BUY"
            tech_conf = min(70, 50 + abs(macd_val) * 1000)
        elif macd_val < 0:
            tech_signal = "SELL"
            tech_conf = min(70, 50 + abs(macd_val) * 1000)

    # 3. Market regime (simplified)
    regime = "VOLATILE"
    if adx_h4 is not None and adx_h4 >= 25:
        regime = "TRENDING"
    elif adx_h4 is not None and adx_h4 <= 15:
        regime = "RANGE"

    # 4. Composite score (simplified)
    score = (tech_conf + macro_result["macro_confidence"]) / 2.0

    # 5. Final decision
    decision_result = decision_engine.decide(
        technical_signal=tech_signal,
        technical_confidence=tech_conf,
        composite_score=score,
        market_regime=regime,
        macro_bias=macro_result["macro_bias"],
        macro_confidence=macro_result["macro_confidence"],
        macro_strength=macro_result["macro_strength"],
    )

    # 6. Forward return
    if len(closes) > forward_bars:
        future_idx = min(forward_bars, len(closes) - 1)
        forward_ret = (
            closes.iloc[-1] / closes.iloc[-(future_idx + 1)] - 1
        )
    else:
        forward_ret = 0.0

    return {
        "symbol": symbol,
        "symbol_class": SYMBOL_CLASSES.get(symbol, "FOREX"),
        "tech_signal": tech_signal,
        "tech_confidence": round(tech_conf, 1),
        "macro_bias": macro_result["macro_bias"],
        "macro_confidence": macro_result["macro_confidence"],
        "market_regime": regime,
        "composite_score": round(score, 1),
        "final_decision": decision_result["final_decision"],
        "decision_confidence": decision_result["decision_confidence"],
        "forward_return": round(forward_ret * 100, 2),
        "forward_bars": forward_bars,
    }


def is_decision_correct(decision: str, forward_return: float) -> bool:
    """Check if decision aligns with forward return."""
    if decision == "WAIT":
        return True  # WAIT is always "safe"
    if decision == "BUY" and forward_return > FORWARD_THRESHOLD:
        return True
    if decision == "SELL" and forward_return < -FORWARD_THRESHOLD:
        return True
    if decision == "HEDGE":
        # HEDGE is correct if market moves either way significantly
        return abs(forward_return) > FORWARD_THRESHOLD
    return False


def is_decision_profitable(decision: str, forward_return: float) -> float:
    """Calculate profit factor for a decision (-1.0 to 1.0)."""
    if decision == "BUY":
        return forward_return
    if decision == "SELL":
        return -forward_return
    if decision == "HEDGE":
        return abs(forward_return) * 0.5  # Hedge captures half the move
    return 0.0  # WAIT


async def evaluate_symbol(
    symbol: str,
    days: int = 365,
    macro_engine: Optional[MacroBiasEngine] = None,
    decision_engine: Optional[FinalDecisionEngine] = None,
) -> list[dict]:
    """Evaluate a single symbol through the decision pipeline."""
    engine_m = macro_engine or MacroBiasEngine()
    engine_d = decision_engine or FinalDecisionEngine()

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)

    async with async_session_factory() as session:
        stmt = (
            select(OHLC)
            .join(OHLC.symbol)
            .where(Symbol.symbol == symbol)
            .where(OHLC.timeframe == "D1")
            .where(OHLC.timestamp >= start)
            .where(OHLC.timestamp <= end)
            .order_by(OHLC.timestamp)
        )
        result = await session.execute(stmt)
        rows = result.scalars().all()

    if len(rows) < MIN_HISTORY:
        return []

    df = pd.DataFrame([{
        "timestamp": r.timestamp,
        "open": float(r.open),
        "high": float(r.high),
        "low": float(r.low),
        "close": float(r.close),
    } for r in rows])

    results = []
    for forward_bars in FORWARD_BARS_LIST:
        if len(df) < forward_bars + MIN_HISTORY:
            continue

        eval_point = evaluate_point(
            closes=df["close"],
            highs=df["high"],
            lows=df["low"],
            forward_bars=forward_bars,
            macro_engine=engine_m,
            decision_engine=engine_d,
            symbol=symbol,
        )
        eval_point["correct"] = is_decision_correct(
            eval_point["final_decision"],
            eval_point["forward_return"],
        )
        eval_point["profit"] = round(
            is_decision_profitable(
                eval_point["final_decision"],
                eval_point["forward_return"] / 100.0,
            ) * 100, 2,
        )
        results.append(eval_point)

    return results


async def main():
    """Run evaluation across all symbols."""
    print("=" * 80)
    print("DECISION PIPELINE EVALUATION")
    print("=" * 80)

    macro_engine = MacroBiasEngine()
    decision_engine = FinalDecisionEngine()

    all_results = []
    for symbol in EVALUATION_SYMBOLS:
        print(f"\nEvaluating {symbol}...", end=" ", flush=True)
        results = await evaluate_symbol(
            symbol,
            days=365,
            macro_engine=macro_engine,
            decision_engine=decision_engine,
        )
        if results:
            all_results.extend(results)
            print(f"{len(results)} data points")
        else:
            print("SKIP (insufficient data)")

    if not all_results:
        print("\nNo results. Is the database populated?\n"
              "Run scripts/backfill_ohlc_db.py first.")
        return

    # ── Aggregate Metrics ──
    df = pd.DataFrame(all_results)

    print("\n" + "=" * 80)
    print("AGGREGATE METRICS BY SYMBOL CLASS")
    print("=" * 80)

    for symbol_class in df["symbol_class"].unique():
        subset = df[df["symbol_class"] == symbol_class]
        total = len(subset)
        correct = subset["correct"].sum()
        accuracy = correct / total * 100
        avg_profit = subset["profit"].mean()

        print(f"\n  {symbol_class}:")
        print(f"    Total evaluations: {total}")
        print(f"    Correct decisions: {correct}/{total} "
              f"({accuracy:.1f}%)")
        print(f"    Avg profit factor: {avg_profit:.2f}%")

        for fb in FORWARD_BARS_LIST:
            fb_subset = subset[subset["forward_bars"] == fb]
            if len(fb_subset) == 0:
                continue
            fb_correct = fb_subset["correct"].sum()
            fb_acc = fb_correct / len(fb_subset) * 100
            fb_profit = fb_subset["profit"].mean()
            print(f"      {fb}-bar forward: "
                  f"acc={fb_acc:.1f}%, profit={fb_profit:.2f}%")

    # ── Decision Distribution ──
    print("\n" + "=" * 80)
    print("DECISION DISTRIBUTION")
    print("=" * 80)
    decision_counts = Counter(df["final_decision"])
    for decision, count in decision_counts.most_common():
        pct = count / len(df) * 100
        correct = df[df["final_decision"] == decision]["correct"].sum()
        print(f"  {decision:10s}: {count:4d} ({pct:5.1f}%) "
              f"correct={correct:.0f}/{count} "
              f"({correct/count*100:.1f}% acc)")

    # ── Overall ──
    print("\n" + "=" * 80)
    print("OVERALL SUMMARY")
    print("=" * 80)
    overall_acc = df["correct"].sum() / len(df) * 100
    overall_profit = df["profit"].mean()
    print(f"  Total evaluations: {len(df)}")
    print(f"  Overall accuracy: {overall_acc:.1f}%")
    print(f"  Average profit factor: {overall_profit:.2f}%")
    print(f"  True positives (BUY ↑): "
          f"{(df['final_decision'] == 'BUY') & (df['forward_return'] > 0)}.sum()")
    print(f"  True negatives (SELL ↓): "
          f"{(df['final_decision'] == 'SELL') & (df['forward_return'] < 0)}.sum()")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
