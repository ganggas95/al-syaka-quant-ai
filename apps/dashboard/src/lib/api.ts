const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Base fetch with AbortController support ────────────────────────────────

async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const res = await fetch(url, { signal });
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// ─── OHLC ───────────────────────────────────────────────────────────────────

export interface Candle {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface OHLCResponse {
  symbol: string;
  timeframe: string;
  count: number;
  data: Candle[];
  /** Some endpoints return ohlc array directly instead of nested data */
  ohlc?: Candle[];
}

// ─── Indicators ─────────────────────────────────────────────────────────────

export interface IndicatorsResponse {
  symbol: string;
  timeframe: string;
  timestamps: string[];
  ohlc: {
    open: number[];
    high: number[];
    low: number[];
    close: number[];
    volume: number[];
  };
  indicators: Record<string, number[]>;
}

// ─── Market Structure ───────────────────────────────────────────────────────

export interface SwingPoint {
  index: number;
  price: number;
  label: string;
}

export interface StructureEvent {
  type: string;
  index: number;
  price: number;
}

export interface FVG {
  type: string;
  index: number;
  gap_high: number;
  gap_low: number;
}

export interface LiquiditySweep {
  type: string;
  index: number;
  swept_level: number;
}

export interface SRLevel {
  price: number;
  touches: number;
}

export interface MarketStructureResponse {
  symbol: string;
  timeframe: string;
  current_trend: string;
  swing_highs: SwingPoint[];
  swing_lows: SwingPoint[];
  break_of_structure: StructureEvent[];
  change_of_character: StructureEvent[];
  fair_value_gaps: FVG[];
  liquidity_sweeps: LiquiditySweep[];
  support_resistance: {
    resistances: SRLevel[];
    supports: SRLevel[];
  };
}

// ─── Unified Signal (full response shape) ───────────────────────────────────

export interface ConfidenceBreakdown {
  market_structure: number;
  momentum: number;
  trend: number;
  volatility: number;
  ai_prediction: number;
}

export interface MarketStructureData {
  trend: string;
  swing_highs: number;
  swing_lows: number;
  break_of_structure: number;
  change_of_character: number;
  fair_value_gaps: number;
  liquidity_sweeps: number;
}

export interface UnifiedSignalResponse {
  signal_id: string;
  symbol: string;
  timestamp: string;

  // Core signal
  signal: "BUY" | "SELL" | "NEUTRAL";
  confidence: number;
  confidence_label?: string;

  // Price levels
  entry_price: number;
  stop_loss: number;
  take_profit: number;
  risk_reward: number;

  // Risk
  risk_level: string;
  lot_size?: number;
  trade_quality?: string;
  position_multiplier?: number;

  // Reasons & indicators
  reasons: string[];
  indicators_used?: string[];

  // Multi-timeframe
  h1_signal?: string;
  h4_signal?: string;
  d1_signal?: string;

  // AI
  ai_confidence?: number;
  ai_accuracy?: number;
  shap_reasons?: string[];
  shap_summary?: string;
  feature_contributions?: Record<string, number>;
  explanation_reason?: string;

  // Composite score
  composite_score: number;
  confidence_breakdown?: ConfidenceBreakdown;

  // Market
  market_regime?: string;
  regime_reason?: string;
  market_trend?: string;
  market_structure?: MarketStructureData;

  // Macro
  macro_bias?: string;
  macro_strength?: number;
  macro_confidence?: number;
  macro_reason?: string;
  macro_events?: string[];

  // Final decision
  final_decision?: string;
  decision_reason?: string;
  conflict_detected?: boolean;
  hedge_intensity?: string;
  decision_confidence?: number;
}

// ─── Signal History ─────────────────────────────────────────────────────────

export interface SignalHistoryEntry {
  signal_id: string;
  symbol: string;
  signal: string;
  confidence: number;
  timestamp: string;
  timeframe?: string;
}

// ─── API Client ─────────────────────────────────────────────────────────────

export const api = {
  health: (signal?: AbortSignal) =>
    fetchJson<{ status: string }>(`${API_URL}/health`, signal),

  ohlc: (symbol: string, timeframe = "H1", limit = 100, signal?: AbortSignal) =>
    fetchJson<OHLCResponse>(
      `${API_URL}/api/v1/market/ohlc/${symbol}?timeframe=${timeframe}&limit=${limit}`,
      signal
    ),

  indicators: (symbol: string, timeframe = "H1", limit = 200, signal?: AbortSignal) =>
    fetchJson<IndicatorsResponse>(
      `${API_URL}/api/v1/indicators/${symbol}?timeframe=${timeframe}&limit=${limit}`,
      signal
    ),

  marketStructure: (symbol: string, timeframe = "H1", limit = 200, signal?: AbortSignal) =>
    fetchJson<MarketStructureResponse>(
      `${API_URL}/api/v1/market-structure/${symbol}?timeframe=${timeframe}&limit=${limit}`,
      signal
    ),

  unifiedSignal: (
    symbol: string,
    timeframe = "H1",
    includeAI = false,
    signal?: AbortSignal
  ) =>
    fetchJson<UnifiedSignalResponse>(
      `${API_URL}/api/v1/unified-signal/${symbol}?timeframe=${timeframe}&include_ai=${includeAI}`,
      signal
    ),
};
