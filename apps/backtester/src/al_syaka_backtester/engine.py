"""Backtest Engine — Eksekusi sinyal virtual pada data historis dengan adaptive regime strategy."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable, Optional

import numpy as np
import pandas as pd
from al_syaka_indicators import IndicatorCalculator
from al_syaka_risk import RiskManager

from .macro import BacktestMacroEngine, _resolve_final_decision
from .metrics import BacktestMetrics, MetricsCalculator
from .regime import MarketRegime, MarketRegimeClassifier
from .trade import TradeRecord, get_session_name

# ── Symbol Info ──────────────────────────────────────────────────────────
# Correct pip_size and contract_size per symbol class.
# Without this, P&L calculations for metals/indices/crypto are wrong.
SYMBOL_INFO: dict[str, dict] = {
    "XAUUSD": {"pip_size": 0.01, "contract_size": 100},       # Gold
    "XAGUSD": {"pip_size": 0.001, "contract_size": 5000},     # Silver
    "BTCUSD": {"pip_size": 0.1, "contract_size": 1},          # Bitcoin
    "ETHUSD": {"pip_size": 0.1, "contract_size": 1},          # Ethereum
    "US30":   {"pip_size": 0.1, "contract_size": 10},         # US30 Index
    "NAS100": {"pip_size": 0.1, "contract_size": 10},         # NAS100 Index
    "SPX500": {"pip_size": 0.1, "contract_size": 10},         # S&P500 Index
    "JP225":  {"pip_size": 1.0, "contract_size": 10},         # Nikkei Index
    "UK100":  {"pip_size": 0.1, "contract_size": 10},         # UK100 Index
    "GER40":  {"pip_size": 0.1, "contract_size": 10},         # GER40 Index
}
_DEFAULT_SYMBOL_INFO: dict = {"pip_size": 0.0001, "contract_size": 100_000}


def get_symbol_info(symbol: str) -> dict:
    """Get pip_size and contract_size for a symbol.
    
    Falls back to forex defaults (0.0001, 100_000) for unknown symbols.
    """
    prefix = symbol.upper().strip()
    info = SYMBOL_INFO.get(prefix)
    if info:
        return info
    # Try partial match: "XAUUSD" also matches in longer strings
    for key, val in SYMBOL_INFO.items():
        if key in prefix:
            return val
    return _DEFAULT_SYMBOL_INFO


@dataclass
class BacktestConfig:
    """Configuration for backtest run."""
    symbol: str
    timeframe: str
    start_date: datetime
    end_date: datetime
    initial_balance: float = 10_000
    risk_per_trade: float = 0.01  # 1%

    # Trade management (optimized via Optuna — Iteration 006)
    atr_sl_multiplier: float = 1.0
    atr_tp_multiplier: float = 1.0
    min_confidence: float = 0.55
    # Per-strategy confidence thresholds (Priority 4 — Iteration 005)
    tf_min_confidence: float = 0.65   # Trend following: optimized from grid search (was 0.70)
    mr_min_confidence: float = 0.50   # Mean reversion: match RSI extreme zone (≤35/≥65)
    bo_min_confidence: float = 0.55   # ATR breakout: keep default
    max_hold_bars: int = 60           # P99 durasi = 55 bars (safe threshold)

    # Regime adaptive parameters
    use_regime_adaptive: bool = True
    adx_trending: float = 22.0
    adx_sideways: float = 18.0
    use_session_filter: bool = False  # Session Intelligence handles session filtering
    mean_rev_sl_multiplier: float = 0.9    # Wider SL (was 0.7) — reduces premature stop-outs
    mean_rev_tp_multiplier: float = 1.1    # Better RR (was 0.7) — improves MR profitability
    breakout_sl_multiplier: float = 1.3
    breakout_tp_multiplier: float = 1.0

    # Dynamic Risk/Reward by Regime (Priority 3 — Iteration 004)
    # Multiplier applied to base TP for each regime
    regime_rr: dict = field(default_factory=lambda: {
        "TRENDING": 1.0,       # RR 1:1.0
        "SIDEWAYS": 1.0,       # RR 1:1.0
        "HIGH_VOLATILITY": 1.0,# RR 1:1.0
    })

    # Exit Optimization (Priority 2 — Iteration 005)
    # DISABLED by default: breakeven/partial TP hurt PF with tight SL/TP (RR 1:1)
    use_breakeven: bool = False
    breakeven_atr: float = 0.5      # Move SL to entry at 0.5x ATR profit
    use_partial_tp: bool = False
    partial_tp_ratio: float = 0.5   # Close 50% at partial level
    partial_tp_atr: float = 0.7     # Partial TP at 0.7x ATR profit
    use_trailing: bool = False      # Disabled — hurts with tight SL/TP
    trail_activation_rr: float = 0.8
    trail_distance_atr: float = 0.5

    # Risk Management (Phase 9)
    use_partial_close: bool = False
    partial_close_atr: float = 1.5      # Close 50% at 1.5x ATR profit
    partial_close_ratio: float = 0.5    # 50% of position
    max_daily_loss: float = 500.0       # Stop trading if daily loss > $500
    max_consecutive_losses: int = 5     # Stop after 5 consecutive losses
    # Weekly loss limit — stop trading if weekly loss exceeds threshold
    use_weekly_loss_limit: bool = False  # Disabled by default (opt-in)
    max_weekly_loss: float = 1500.0     # Stop trading if weekly loss > $1500
    use_dynamic_sizing: bool = True     # Scale size based on ATR volatility

    # Confidence-based Position Sizing (Priority 5 — Iteration 005)
    # Maps confidence thresholds to risk multipliers
    use_confidence_sizing: bool = True   # Scale position by confidence
    confidence_size_tiers: list = field(default_factory=lambda: [
        (0.50, 0.50),  # confidence 50%+  → 50% of base risk
        (0.60, 0.75),  # confidence 60%+  → 75% of base risk
        (0.70, 1.00),  # confidence 70%+  → 100% of base risk
        (0.80, 1.50),  # confidence 80%+  → 150% of base risk
        (0.90, 2.00),  # confidence 90%+  → 200% of base risk
    ])

    # Phase 4: Macro Engine + Final Decision Engine
    # Integrates macro context from H4/D1 analysis and resolves
    # conflicts between technical signals and macro bias.
    use_macro_engine: bool = True        # Enable H4/D1 macro analysis
    use_final_decision: bool = True       # Enable tech×macro conflict resolution

    # Session Intelligence Engine (Priority 7 — Session Distribution Analysis)
    # Session-specific config for risk, confidence, and signal filters
    use_session_intelligence: bool = True
    session_config: dict = field(default_factory=lambda: {
        "ASIA": {
            "risk_multiplier": 1.0,      # Normal risk
            "min_confidence": 0.60,      # MR works at 60%+
            "require_bos": False,        # BOS not needed for MR
        },
        "LONDON": {
            "risk_multiplier": 0.5,      # Reduced risk (SELL+LONDON = 64% loss)
            "min_confidence": 0.65,      # Aligned with tf_min_confidence (was 0.72)
            "require_bos": False,        # Redundant — regime classifier handles this
        },
        "NEWYORK": {
            "risk_multiplier": 1.0,      # Normal risk
            "min_confidence": 0.65,      # Aligned with tf_min_confidence (was 0.70)
            "require_bos": False,        # BOS not required
        },
    })

    # Market Regime × Session Cross Filter (Priority 7 — Cross-Analysis)
    # Allows/disallows specific (session, regime) combinations.
    # Default: all sessions × all regimes allowed (empty dict = no filter).
    # To filter, list only the allowed regimes per session.
    # Example: {"LONDON": ["TRENDING"], "ASIA": ["SIDEWAYS"]}
    use_regime_session_filter: bool = False
    regime_session_allowed: dict = field(default_factory=dict)


class BacktestEngine:
    """Main backtesting engine — runs adaptive strategy based on market regime."""

    def __init__(self, config: BacktestConfig):
        self.config = config
        self.trades: list[TradeRecord] = []
        self.equity_curve: list[dict] = [{"timestamp": config.start_date, "equity": config.initial_balance}]
        self.balance = config.initial_balance
        self.risk_manager = RiskManager(account_balance=config.initial_balance)
        self.peak_balance = config.initial_balance
        self.regime_history: list[dict] = []
        self.classifier = MarketRegimeClassifier(
            adx_trending=config.adx_trending,
            adx_sideways=config.adx_sideways,
            use_session_filter=config.use_session_filter,
        ) if config.use_regime_adaptive else None
        # Phase 4: Macro Engine (initialized in run() when data is available)
        self.macro_engine: Optional[BacktestMacroEngine] = None
        # Risk management state
        self.daily_pnl: float = 0.0
        self.current_day: Optional[str] = None
        self.weekly_pnl: float = 0.0
        self.current_week: Optional[str] = None
        self.consecutive_losses: int = 0
        self._consecutive_loss_triggered: bool = False

    def run(self, ohlc_data: pd.DataFrame,
            progress_callback: Optional[Callable[[int, int], None]] = None) -> BacktestMetrics:
        """Run backtest on historical OHLC data."""
        df = ohlc_data.copy()
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Pre-compute all indicators once on full dataset (major perf win)
        full_calc = IndicatorCalculator({
            "open": df["open"], "high": df["high"],
            "low": df["low"], "close": df["close"],
            "volume": df.get("volume", pd.Series([0] * len(df))),
        })
        all_indicators = full_calc.compute_all()

        # Phase 4: Initialize Macro Engine (H4/D1 resampling from H1 data)
        if self.config.use_macro_engine:
            self.macro_engine = BacktestMacroEngine(df)

        open_trades: list[TradeRecord] = []
        total_steps = max(1, len(df) - 100)
        last_pct = -1

        for i in range(100, len(df)):
            if progress_callback:
                pct = int(((i - 100) / total_steps) * 100)
                if pct != last_pct:
                    progress_callback(i - 100, total_steps)
                    last_pct = pct

            # Daily P&L reset
            ts = df.iloc[i]["timestamp"]
            day_key = ts.strftime("%Y-%m-%d") if hasattr(ts, "strftime") else str(ts)[:10]
            if self.current_day is None:
                self.current_day = day_key
            elif day_key != self.current_day:
                self.daily_pnl = 0.0
                self.current_day = day_key

            # Weekly P&L reset
            week_key = ts.strftime("%Y-W%V") if hasattr(ts, "strftime") else str(ts)[:10]
            if self.current_week is None:
                self.current_week = week_key
            elif week_key != self.current_week:
                self.weekly_pnl = 0.0
                self.current_week = week_key

            # Slice pre-computed indicators up to current bar
            ind = {k: v[:i + 1] for k, v in all_indicators.items()}

            self._update_open_trades(open_trades, df.iloc[i], ind)
            self.balance = self._calculate_balance(open_trades)

            # Detect regime (once per session, at signal check time)
            if len(open_trades) == 0:
                signal = self._check_adaptive_signal(ind, df.iloc[i])
                if signal:
                    trade = self._open_trade(signal, df.iloc[i], ind)
                    open_trades.append(trade)
                    self.trades.append(trade)

            equity = self.balance + sum(t.profit for t in open_trades)
            self.equity_curve.append({"timestamp": df.iloc[i]["timestamp"], "equity": equity})
            self.peak_balance = max(self.peak_balance, equity)

        for t in open_trades:
            if t.result == "PENDING":
                t.exit_price = df.iloc[-1]["close"]
                t.exit_time = df.iloc[-1]["timestamp"]
                t.result, t.pips, t.profit = self._calculate_result(t)
                t.exit_reason = "END_OF_DATA"

        return MetricsCalculator.calculate(self.trades, self.equity_curve)

    def _detect_regime(self, indicators: dict, timestamp: datetime) -> MarketRegime:
        """Detect market regime using classifier."""
        if self.classifier:
            return self.classifier.detect(indicators, timestamp)
        # Fallback: always trending if classifier disabled
        return MarketRegime.TRENDING

    def _check_adaptive_signal(self, indicators: dict,
                                current_row: pd.Series) -> Optional[dict]:
        """Adaptive signal checking — pilih strategi berdasarkan regime."""
        # Risk guard: max daily loss
        if self.daily_pnl <= -self.config.max_daily_loss:
            return None
        # Risk guard: max weekly loss
        if (self.config.use_weekly_loss_limit
                and self.weekly_pnl <= -self.config.max_weekly_loss):
            return None
        # Risk guard: max consecutive losses
        if self.consecutive_losses >= self.config.max_consecutive_losses:
            return None

        regime = self._detect_regime(indicators, current_row["timestamp"])

        # Track regime for analysis
        self.regime_history.append({
            "timestamp": current_row["timestamp"],
            "regime": regime.value,
            "close": current_row["close"],
        })

        # Route to appropriate strategy
        strategy_map = {
            MarketRegime.TRENDING: self._signal_trend_following,
            MarketRegime.SIDEWAYS: self._signal_mean_reversion,
            MarketRegime.HIGH_VOLATILITY: self._signal_atr_breakout,
            MarketRegime.NEWS_DAY: lambda i, r: None,  # WAIT
        }
        strategy_conf_map = {
            MarketRegime.TRENDING: self.config.tf_min_confidence,
            MarketRegime.SIDEWAYS: self.config.mr_min_confidence,
            MarketRegime.HIGH_VOLATILITY: self.config.bo_min_confidence,
        }
        checker = strategy_map.get(regime, lambda i, r: None)
        signal = checker(indicators, current_row)
        if signal:
            signal["regime"] = regime.value
            # Apply per-strategy confidence filter (Priority 4)
            min_conf = strategy_conf_map.get(regime, self.config.min_confidence)
            if signal.get("confidence", 0) < min_conf:
                return None

            # Phase 4: Macro Analysis + Final Decision Resolution
            macro = None
            if self.config.use_macro_engine and self.macro_engine is not None:
                macro = self.macro_engine.analyze_at(
                    current_row["timestamp"],
                    symbol=self.config.symbol,
                )
                # Store macro bias in signal for trade record
                signal["macro_bias"] = macro.get("macro_bias", "NEUTRAL")

                # Final Decision: resolve tech × macro conflict
                if self.config.use_final_decision:
                    decision = _resolve_final_decision(
                        technical_signal=signal["signal"],
                        technical_confidence=signal.get("confidence", 0.5),
                        regime=regime.value,
                        macro_result=macro,
                    )
                    final_dec = decision["final_decision"]
                    # HEDGE or WAIT → skip trade (conflict too high)
                    if final_dec in ("WAIT", "HEDGE"):
                        return None
                    # Override: macro overrides weak tech signal
                    if final_dec != signal["signal"]:
                        signal["signal"] = final_dec
                    # Adjust confidence based on decision confidence
                    dec_conf = decision["decision_confidence"] / 100.0
                    if 0 < dec_conf < signal.get("confidence", 0.5):
                        signal["confidence"] = dec_conf

            # Market Regime × Session Cross Filter (Priority 7)
            if self.config.use_regime_session_filter and self.config.regime_session_allowed:
                session = get_session_name(current_row["timestamp"])
                allowed = self.config.regime_session_allowed.get(session)
                if allowed is not None:
                    if regime.value not in allowed:
                        return None

            # Session Intelligence Engine (Priority 7)
            if self.config.use_session_intelligence:
                session = get_session_name(current_row["timestamp"])
                sess_cfg = self.config.session_config.get(session, {})
                # Session-specific confidence (takes max of strategy & session thresholds)
                sess_conf = sess_cfg.get("min_confidence", 0)
                effective_conf = max(min_conf, sess_conf)
                if signal.get("confidence", 0) < effective_conf:
                    return None
                # Session-specific BOS confirmation for SELL signals during LONDON
                if session == "LONDON" and sess_cfg.get("require_bos", False):
                    ema12 = indicators.get("ema_12")
                    ema50 = indicators.get("ema_50")
                    if ema12 is not None and ema50 is not None and len(ema12) > 1:
                        has_bos_uptrend = ema12.iloc[-1] > ema50.iloc[-1]
                        has_bos_downtrend = ema12.iloc[-1] < ema50.iloc[-1]
                        if signal["signal"] == "SELL" and not has_bos_downtrend:
                            return None
                        if signal["signal"] == "BUY" and not has_bos_uptrend:
                            return None
        return signal

    def _signal_trend_following(self, indicators: dict,
                                 current_row: pd.Series) -> Optional[dict]:
        """Trend following strategy (EMA crossover + RSI filter)."""
        try:
            ema12 = indicators["ema_12"]
            ema50 = indicators["ema_50"]
            rsi_val = indicators["rsi_14"]
            atr_val = indicators["atr_14"]

            if len(ema12) < 2: return None
            last = -1
            if pd.isna(ema12.iloc[last]) or pd.isna(rsi_val.iloc[last]):
                return None

            close = current_row["close"]

            # BUY: EMA12 > EMA50 (uptrend), RSI < 70 (not overbought)
            if ema12.iloc[last] > ema50.iloc[last] and rsi_val.iloc[last] < 70:
                confidence = 0.55 + (rsi_val.iloc[last] / 100) * 0.25
                reasons = ["Trend: EMA Bullish", f"RSI {rsi_val.iloc[last]:.0f}"]
                return {
                    "signal": "BUY", "confidence": min(confidence, 0.9),
                    "entry": close, "atr": atr_val.iloc[last],
                    "strategy": "trend_following", "reasons": reasons,
                }

            # SELL: EMA12 < EMA50 (downtrend), RSI > 30 (not oversold)
            if ema12.iloc[last] < ema50.iloc[last] and rsi_val.iloc[last] > 30:
                confidence = 0.55 + (1 - rsi_val.iloc[last] / 100) * 0.25
                reasons = ["Trend: EMA Bearish", f"RSI {rsi_val.iloc[last]:.0f}"]
                return {
                    "signal": "SELL", "confidence": min(confidence, 0.9),
                    "entry": close, "atr": atr_val.iloc[last],
                    "strategy": "trend_following", "reasons": reasons,
                }
        except (KeyError, IndexError, TypeError):
            return None
        return None

    def _signal_mean_reversion(self, indicators: dict,
                                current_row: pd.Series) -> Optional[dict]:
        """Mean reversion strategy (RSI oversold/overbought)."""
        try:
            rsi_val = indicators["rsi_14"]
            atr_val = indicators["atr_14"]

            if len(rsi_val) < 2: return None
            last = -1
            if pd.isna(rsi_val.iloc[last]): return None

            close = current_row["close"]

            # BUY: RSI oversold (≤ 35)
            if rsi_val.iloc[last] <= 35:
                confidence = 0.50 + (35 - rsi_val.iloc[last]) / 35 * 0.30
                return {
                    "signal": "BUY", "confidence": min(confidence, 0.85),
                    "entry": close, "atr": atr_val.iloc[last],
                    "strategy": "mean_reversion",
                    "reasons": ["MeanRev: RSI Oversold", f"RSI {rsi_val.iloc[last]:.0f}"],
                }

            # SELL: RSI overbought (≥ 65)
            if rsi_val.iloc[last] >= 65:
                confidence = 0.50 + (rsi_val.iloc[last] - 65) / 35 * 0.30
                return {
                    "signal": "SELL", "confidence": min(confidence, 0.85),
                    "entry": close, "atr": atr_val.iloc[last],
                    "strategy": "mean_reversion",
                    "reasons": ["MeanRev: RSI Overbought", f"RSI {rsi_val.iloc[last]:.0f}"],
                }
        except (KeyError, IndexError, TypeError):
            return None
        return None

    def _signal_atr_breakout(self, indicators: dict,
                              current_row: pd.Series) -> Optional[dict]:
        """ATR breakout strategy (breakout of BB with high volatility)."""
        try:
            atr_val = indicators["atr_14"]
            bb_upper = indicators.get("bb_upper")
            bb_lower = indicators.get("bb_lower")

            if atr_val is None or len(atr_val) < 2: return None
            last = -1
            close = current_row["close"]

            # BUY: close breaks above BB upper
            if bb_upper is not None and not pd.isna(bb_upper.iloc[last]):
                if close > bb_upper.iloc[last]:
                    return {
                        "signal": "BUY", "confidence": 0.7,
                        "entry": close, "atr": atr_val.iloc[last],
                        "strategy": "atr_breakout",
                        "reasons": ["Breakout: Close > BB Upper"],
                    }

            # SELL: close breaks below BB lower
            if bb_lower is not None and not pd.isna(bb_lower.iloc[last]):
                if close < bb_lower.iloc[last]:
                    return {
                        "signal": "SELL", "confidence": 0.7,
                        "entry": close, "atr": atr_val.iloc[last],
                        "strategy": "atr_breakout",
                        "reasons": ["Breakout: Close < BB Lower"],
                    }
        except (KeyError, IndexError, TypeError):
            return None
        return None

    def _open_trade(self, signal: dict, row: pd.Series, indicators: dict) -> TradeRecord:
        """Open a new trade based on signal."""
        direction = "LONG" if signal["signal"] == "BUY" else "SHORT"
        entry = signal["entry"]
        atr_val = signal.get("atr", 0.001)
        strategy = signal.get("strategy", "trend_following")
        regime = signal.get("regime", "UNKNOWN")

        # Adaptive SL/TP based on strategy
        if strategy == "mean_reversion":
            base_sl = self.config.mean_rev_sl_multiplier
            base_tp = self.config.mean_rev_tp_multiplier
        elif strategy == "atr_breakout":
            base_sl = self.config.breakout_sl_multiplier
            base_tp = self.config.breakout_tp_multiplier
        else:
            base_sl = self.config.atr_sl_multiplier
            base_tp = self.config.atr_tp_multiplier

        # Dynamic RR: apply regime multiplier to TP (Priority 3)
        rr_mult = self.config.regime_rr.get(regime, 1.0)
        sl_mult = base_sl
        tp_mult = base_tp * rr_mult

        if direction == "LONG":
            sl = entry - (atr_val * sl_mult)
            tp = entry + (atr_val * tp_mult)
        else:
            sl = entry + (atr_val * sl_mult)
            tp = entry - (atr_val * tp_mult)

        # Position size
        risk_amount = self.balance * self.config.risk_per_trade
        if self.config.use_dynamic_sizing and atr_val > 0:
            atr_scale = 0.001 / max(atr_val, 0.0001)
            atr_scale = max(0.5, min(atr_scale, 2.0))
            risk_amount *= atr_scale

        # Confidence-based position sizing (Priority 5 — Iteration 005)
        confidence = signal.get("confidence", 0.6)
        if self.config.use_confidence_sizing:
            conf_mult = 1.0
            for conf_threshold, size_mult in sorted(self.config.confidence_size_tiers,
                                                     key=lambda x: -x[0]):
                if confidence >= conf_threshold:
                    conf_mult = size_mult
                    break
            risk_amount *= conf_mult

        # Session-specific risk multiplier (Priority 7 — Session Intelligence)
        if self.config.use_session_intelligence:
            session = get_session_name(row["timestamp"])
            sess_cfg = self.config.session_config.get(session, {})
            risk_amount *= sess_cfg.get("risk_multiplier", 1.0)
        sl_distance = abs(entry - sl)
        # Correct lot size formula: risk / (SL distance × contract_size)
        sym_info = get_symbol_info(self.config.symbol)
        contract_size = sym_info["contract_size"]
        lot_size = max(0.01, risk_amount / (sl_distance * contract_size))

        # Capture metadata for trade attribution
        adx_val = indicators.get("adx_adx")
        adx_val_f = float(adx_val.iloc[-1]) if adx_val is not None and len(adx_val) > 0 else 0.0
        atr_entry = float(atr_val)
        atr_series = indicators.get("atr_14")
        if atr_series is not None and len(atr_series) > 20:
            atr_sma = atr_series.iloc[-20:].mean()
            vol_ratio = atr_entry / atr_sma if atr_sma > 0 else 1.0
            if vol_ratio > 1.3:
                vol_level = "HIGH"
            elif vol_ratio < 0.7:
                vol_level = "LOW"
            else:
                vol_level = "MEDIUM"
        else:
            vol_level = "MEDIUM"

        return TradeRecord(
            entry_time=row["timestamp"],
            signal=signal["signal"],
            entry_price=entry,
            stop_loss=sl, take_profit=tp,
            lot_size=round(lot_size, 2),
            direction=direction, result="PENDING",
            confidence=signal.get("confidence", 0.6),
            reasons=signal.get("reasons", [strategy]),
            session=get_session_name(row["timestamp"]),
            regime=regime,
            adx_at_entry=round(adx_val_f, 1),
            atr_at_entry=round(atr_entry, 6),
            volatility_at_entry=vol_level,
            strategy=strategy,
            # Phase 4: Macro context for trade attribution
            macro_bias=signal.get("macro_bias", ""),
            composite_score=round(signal.get("confidence", 0.6) * 100, 1),
        )

    def _update_open_trades(self, open_trades: list[TradeRecord],
                             row: pd.Series, indicators: dict):
        """Check and manage open trades — enhanced exit management (Iteration 004)."""
        to_remove = []
        atr_val = indicators.get("atr_14")
        current_atr = atr_val.iloc[-1] if atr_val is not None and len(atr_val) > 0 else 0.001

        for t in open_trades:
            if t.result != "PENDING":
                to_remove.append(t); continue

            price, low, high = row["close"], row["low"], row["high"]
            entry = t.entry_price
            direction = t.direction

            if direction == "LONG":
                profit_atr = (price - entry) / current_atr
            else:
                profit_atr = (entry - price) / current_atr

            # Calculate total TP distance in ATR
            tp_distance = abs(t.take_profit - entry) / current_atr if t.take_profit else 999
            # Breakeven at RR 0.5 (Priority 2)
            if (self.config.use_breakeven and not t.partial_closed
                    and profit_atr >= self.config.breakeven_atr):
                if direction == "LONG":
                    if t.stop_loss < entry: t.stop_loss = entry
                else:
                    if t.stop_loss > entry: t.stop_loss = entry
                t.exit_reason = "BREAKEVEN"

            # Partial Take Profit: close 50% at partial_tp_atr ATR (Priority 2)
            if (self.config.use_partial_tp and not t.partial_closed
                    and profit_atr >= self.config.partial_tp_atr):
                partial_profit = t.profit * self.config.partial_tp_ratio
                self.daily_pnl += partial_profit
                t.lot_size = round(t.lot_size * (1 - self.config.partial_tp_ratio), 2)
                t.partial_closed = True
                t.exit_reason = "PARTIAL_TP"
                # Move SL to entry + small buffer for remaining position
                if direction == "LONG":
                    t.stop_loss = max(t.stop_loss or 0, entry + current_atr * 0.1)
                else:
                    t.stop_loss = min(t.stop_loss or float('inf'), entry - current_atr * 0.1)

            # Trailing stop: activate at 80% of TP distance (Priority 2)
            if (self.config.use_trailing and t.partial_closed
                    and profit_atr >= tp_distance * self.config.trail_activation_rr):
                trail_level = current_atr * self.config.trail_distance_atr
                if direction == "LONG":
                    new_sl = price - trail_level
                    if t.stop_loss is None or new_sl > t.stop_loss:
                        t.stop_loss = new_sl; t.exit_reason = "TRAILING"
                else:
                    new_sl = price + trail_level
                    if t.stop_loss is None or new_sl < t.stop_loss:
                        t.stop_loss = new_sl; t.exit_reason = "TRAILING"

            # Check SL/TP
            if direction == "LONG":
                if t.stop_loss is not None and low <= t.stop_loss:
                    t.exit_price = t.stop_loss; t.exit_time = row["timestamp"]
                    t.result, t.pips, t.profit = self._calculate_result(t)
                    if t.exit_reason not in ("BREAKEVEN", "PARTIAL_TP", "TRAILING"):
                        t.exit_reason = "SL_HIT"
                    self._record_trade_result(t); to_remove.append(t)
                elif t.take_profit is not None and high >= t.take_profit:
                    t.exit_price = t.take_profit; t.exit_time = row["timestamp"]
                    t.result, t.pips, t.profit = self._calculate_result(t)
                    t.exit_reason = "TP_HIT"
                    self._record_trade_result(t); to_remove.append(t)
            else:
                if t.stop_loss is not None and high >= t.stop_loss:
                    t.exit_price = t.stop_loss; t.exit_time = row["timestamp"]
                    t.result, t.pips, t.profit = self._calculate_result(t)
                    if t.exit_reason not in ("BREAKEVEN", "PARTIAL_TP", "TRAILING"):
                        t.exit_reason = "SL_HIT"
                    self._record_trade_result(t); to_remove.append(t)
                elif t.take_profit is not None and low <= t.take_profit:
                    t.exit_price = t.take_profit; t.exit_time = row["timestamp"]
                    t.result, t.pips, t.profit = self._calculate_result(t)
                    t.exit_reason = "TP_HIT"
                    self._record_trade_result(t); to_remove.append(t)

        for t in to_remove:
            if t in open_trades: open_trades.remove(t)

    def _record_trade_result(self, trade: TradeRecord):
        """Track result for risk management."""
        self.daily_pnl += trade.profit
        self.weekly_pnl += trade.profit
        if trade.result == "LOSS":
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0

    def _calculate_result(self, trade: TradeRecord) -> tuple:
        """Calculate P&L with correct contract_size for any symbol."""
        sym_info = get_symbol_info(self.config.symbol)
        contract_size = sym_info["contract_size"]
        pip_size = sym_info["pip_size"]

        if trade.direction == "LONG":
            price_diff = trade.exit_price - trade.entry_price
        else:
            price_diff = trade.entry_price - trade.exit_price

        # Profit = price_diff × lot_size × contract_size
        profit = price_diff * trade.lot_size * contract_size
        # Pips for reporting only
        pips = price_diff / pip_size

        result = "WIN" if profit > 0 else "LOSS"
        if trade.exit_reason == "END_OF_DATA":
            result = "PENDING"
        return result, round(pips, 1), round(profit, 2)

    def _calculate_balance(self, open_trades: list) -> float:
        balance = self.config.initial_balance
        for t in self.trades:
            if t.result in ("WIN", "LOSS"):
                balance += t.profit
        return balance
