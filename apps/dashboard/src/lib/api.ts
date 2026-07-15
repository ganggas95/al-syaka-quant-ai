const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

export interface OHLCResponse {
  symbol: string;
  timeframe: string;
  count: number;
  data: Array<{
    timestamp: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }>;
}

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

export interface MarketStructureResponse {
  symbol: string;
  timeframe: string;
  current_trend: string;
  swing_highs: Array<{ index: number; price: number; label: string }>;
  swing_lows: Array<{ index: number; price: number; label: string }>;
  break_of_structure: Array<{ type: string; index: number; price: number }>;
  change_of_character: Array<{ type: string; index: number; price: number }>;
  fair_value_gaps: Array<{ type: string; index: number; gap_high: number; gap_low: number }>;
  liquidity_sweeps: Array<{ type: string; index: number; swept_level: number }>;
  support_resistance: {
    resistances: Array<{ price: number; touches: number }>;
    supports: Array<{ price: number; touches: number }>;
  };
}

export const api = {
  health: () => fetchJson<{ status: string }>(`${API_URL}/health`),
  ohlc: (symbol: string, timeframe = "H1", limit = 100) =>
    fetchJson<OHLCResponse>(`${API_URL}/api/v1/market/ohlc/${symbol}?timeframe=${timeframe}&limit=${limit}`),
  indicators: (symbol: string, timeframe = "H1", limit = 200) =>
    fetchJson<IndicatorsResponse>(`${API_URL}/api/v1/indicators/${symbol}?timeframe=${timeframe}&limit=${limit}`),
  marketStructure: (symbol: string, timeframe = "H1", limit = 200) =>
    fetchJson<MarketStructureResponse>(`${API_URL}/api/v1/market-structure/${symbol}?timeframe=${timeframe}&limit=${limit}`),
};
