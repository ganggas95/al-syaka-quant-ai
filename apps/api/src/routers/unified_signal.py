"""API Router — Unified Signal: menggabungkan semua engine jadi satu endpoint."""

from datetime import datetime

from al_syaka_common.database import async_session_factory
from al_syaka_common.models import Signal
from fastapi import APIRouter, HTTPException, Query
from src.unified_signal import UnifiedSignalGenerator

router = APIRouter(prefix="/api/v1/unified-signal", tags=["unified-signal"])

generator = UnifiedSignalGenerator()


@router.get("/{symbol}")
async def get_unified_signal(
    symbol: str,
    timeframe: str = Query("H1", description="H1, H4, D1"),
    include_ai: bool = Query(False, description="Include AI prediction (slower)"),
):
    """Generate unified trading signal — statistik + struktur + AI + multi-TF.

    Returns one comprehensive response with:
    - Signal BUY/SELL/NEUTRAL + confidence
    - Entry, SL, TP, Risk/Reward
    - Market structure analysis (BOS, CHOCH, FVG, sweeps)
    - Multi-timeframe confirmation (H1, H4, D1)
    - AI prediction + SHAP explanations (optional)
    - Reasons in natural language
    """
    try:
        result = await generator.generate(
            symbol=symbol.upper(),
            timeframe=timeframe.upper(),
            include_ai=include_ai,
        )

        # Save to database
        try:
            async with async_session_factory() as session:
                db_signal = Signal(
                    symbol=result.symbol,
                    timeframe=timeframe,
                    signal=result.signal,
                    confidence=result.confidence,
                    entry_price=result.entry_price,
                    stop_loss=result.stop_loss,
                    take_profit=result.take_profit,
                    risk_reward=result.risk_reward,
                    risk_level=result.risk_level,
                    reasons=str(result.reasons),
                    indicators_used=str(result.indicators_used),
                    market_trend=result.market_trend,
                    h1_signal=result.h1_signal,
                    h4_signal=result.h4_signal,
                    d1_signal=result.d1_signal,
                    ai_accuracy=result.ai_accuracy,
                )
                session.add(db_signal)
                await session.commit()
                result.signal_id = f"SIG-{db_signal.id}"
        except Exception:
            pass  # Database save is non-critical

        return {
            "signal_id": result.signal_id,
            "symbol": result.symbol,
            "timestamp": result.timestamp.isoformat(),
            "signal": result.signal,
            "confidence": result.confidence,
            "composite_score": result.composite_score,
            "confidence_breakdown": result.confidence_breakdown,
            "confidence_label": result.confidence_label,
            "market_regime": result.market_regime,
            "strategy_mode": result.strategy_mode,
            "regime_reason": result.regime_reason,
            "macro_bias": result.macro_bias,
            "macro_strength": result.macro_strength,
            "macro_confidence": result.macro_confidence,
            "macro_reason": result.macro_reason,
            "final_decision": result.final_decision,
            "decision_reason": result.decision_reason,
            "conflict_detected": result.conflict_detected,
            "hedge_intensity": result.hedge_intensity,
            "decision_confidence": result.decision_confidence,
            "position_multiplier": result.position_multiplier,
            "entry_price": result.entry_price,
            "stop_loss": result.stop_loss,
            "take_profit": result.take_profit,
            "risk_reward": result.risk_reward,
            "risk_level": result.risk_level,
            "trade_quality": result.trade_quality,
            "reasons": result.reasons,
            "indicators_used": result.indicators_used,
            "quant_strategy": result.quant_strategy,
            "h1_signal": result.h1_signal,
            "h4_signal": result.h4_signal,
            "d1_signal": result.d1_signal,
            "market_structure": {
                "trend": result.market_trend,
                "swing_highs": result.swing_highs,
                "swing_lows": result.swing_lows,
                "break_of_structure": result.bos_count,
                "change_of_character": result.choch_count,
                "fair_value_gaps": result.fvg_count,
                "liquidity_sweeps": result.liquidity_sweeps,
            },
            "multi_timeframe": {
                "H1": result.h1_signal,
                "H4": result.h4_signal,
                "D1": result.d1_signal,
            },
            "ai": {
                "confidence": result.ai_confidence,
                "accuracy": result.ai_accuracy,
                "shap_reasons": result.shap_reasons,
                "shap_summary": result.shap_summary,
                "feature_contributions": result.feature_contributions,
                "explanation_reason": result.explanation_reason,
            } if include_ai else None,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signal generation failed: {str(e)}")
