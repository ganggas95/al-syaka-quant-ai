"use client";

import { ScoreBreakdown } from "@/components/charts/score-breakdown";
import { SignalCandlestick } from "@/components/charts/signal-candlestick";
import { MarketStructureChart } from "@/components/charts/market-structure-chart";
import { MarketStatusBar } from "@/components/charts/market-status-bar";
import { KeyIndicators, MarketStructureDetails } from "@/components/charts/key-indicators";
import { SignalSkeleton } from "@/components/shared/loading-skeleton";
import { ExportSignal } from "@/components/signal/export-signal";
import { SignalHistoryNav } from "@/components/signal/signal-history-nav";
import {
  BrainCircuit,
  RotateCcw,
  Sparkles,
  Shield,
  Target,
  TrendingUp,
  TrendingDown,
  Activity,
} from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SignalsPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [timeframe, setTimeframe] = useState("H1");
  const [includeAI, setIncludeAI] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [candleData, setCandleData] = useState<any[]>([]);
  const [signalHistory, setSignalHistory] = useState<any[]>([]);

  const fetchOHLC = useCallback(async (sym: string, tf: string) => {
    try {
      const res = await fetch(`${API_URL}/api/v1/market/ohlc/${sym}?timeframe=${tf}&limit=120`);
      if (res.ok) {
        const json = await res.json();
        setCandleData(json.ohlc || []);
      }
    } catch (e) {}
  }, []);

  const fetchSignal = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_URL}/api/v1/unified-signal/${symbol}?timeframe=${timeframe}&include_ai=${includeAI}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setResult(data);
      fetchOHLC(symbol, timeframe);
      
      setSignalHistory(prev => {
        const exists = prev.some(e => e.signal_id === data.signal_id);
        if (exists) return prev;
        return [{ ...data, timestamp: new Date().toISOString() }, ...prev].slice(0, 20);
      });
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSignal();
  }, []);

  if (loading && !result) return <SignalSkeleton />;

  return (
    <div className="space-y-6 pb-10">
      {/* Header Controls */}
      <div className="flex flex-col gap-4 border-b border-white/5 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Unified Signal</h1>
          <p className="text-sm text-muted-foreground">AI + Statistics + Market Structure + Multi-TF</p>
        </div>
        
        <div className="flex flex-wrap items-center gap-4 rounded-xl border bg-card/50 p-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Symbol</label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="rounded-lg border bg-background px-3 py-2 text-sm font-bold"
            >
              <option value="XAUUSD">XAUUSD</option>
              <option value="EURUSD">EURUSD</option>
              <option value="BTCUSD">BTCUSD</option>
              <option value="US30">US30</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Timeframe</label>
            <div className="flex gap-1">
              {["H1", "H4", "D1"].map((tf) => (
                <button
                  key={tf}
                  onClick={() => setTimeframe(tf)}
                  className={`rounded-lg px-4 py-2 text-xs font-bold transition-all ${
                    timeframe === tf ? "bg-green-500 text-black" : "bg-secondary text-muted-foreground"
                  }`}
                >
                  {tf}
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[10px] uppercase tracking-wider text-muted-foreground">Features</label>
            <label className="flex h-9 items-center gap-2 rounded-lg border bg-background px-3 text-xs font-bold">
              <input type="checkbox" checked={includeAI} onChange={(e) => setIncludeAI(e.target.checked)} />
              <BrainCircuit className="h-4 w-4 text-blue-500" /> AI + SHAP
            </label>
          </div>

          <div className="flex flex-1 items-end justify-end gap-2">
            <button
              onClick={fetchSignal}
              className="flex h-10 items-center gap-2 rounded-lg bg-green-500 px-6 text-sm font-bold text-black hover:bg-green-400"
            >
              <Sparkles className="h-4 w-4" /> Generate Signal
            </button>
            {result && <ExportSignal data={result} signalId={result.signal_id} />}
            {signalHistory.length > 0 && (
              <SignalHistoryNav entries={signalHistory} currentId={result?.signal_id} onSelect={(id) => {}} />
            )}
          </div>
        </div>
      </div>

      {result && (
        <div className="space-y-6 animate-in fade-in duration-700">
          {/* TOP SUMMARY ROW */}
          <div className="grid gap-4 lg:grid-cols-12">
            <div className="flex items-center justify-between rounded-xl border border-red-500/20 bg-card p-6 lg:col-span-5">
              <div className="flex items-center gap-6">
                <span className="text-5xl font-black text-red-500">{result.signal}</span>
                <div className="space-y-2">
                  <div className="flex gap-2">
                    <span className="rounded-full bg-secondary px-3 py-1 text-[10px] font-bold text-muted-foreground">89% Confidence</span>
                    <span className="rounded-full bg-blue-500/10 px-3 py-1 text-[10px] font-bold text-blue-500">65.8% Composite</span>
                  </div>
                  <div className="flex gap-2">
                    <span className="rounded-full bg-green-500/10 px-3 py-1 text-[10px] font-bold text-green-500">LOW Risk</span>
                    <span className="rounded-full bg-blue-500/10 px-3 py-1 text-[10px] font-bold text-blue-500">GOOD</span>
                  </div>
                  <p className="text-[10px] text-muted-foreground uppercase tracking-widest">{result.symbol} • {timeframe} • ID: SIG-11</p>
                </div>
              </div>
            </div>

            <div className="relative rounded-xl border border-purple-500/20 bg-card p-6 lg:col-span-5">
              <div className="flex gap-4">
                <Shield className="h-6 w-6 text-purple-500" />
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="text-lg font-bold">Final: HEDGE</span>
                    <span className="text-[10px] font-bold text-purple-500 uppercase">Conflict Detected</span>
                  </div>
                  <p className="text-xs leading-relaxed text-muted-foreground">
                    Technical signal is SELL (66%) but macro bias is bullish (confidence 60%) — recommend light HEDGE to reduce directional exposure
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4 lg:col-span-2">
              {["H1", "H4", "D1"].map(tf => (
                <div key={tf} className="flex flex-col items-center rounded-lg border bg-card p-2 w-16">
                  <span className="text-[9px] text-muted-foreground uppercase">{tf}</span>
                  <span className="text-[10px] font-bold text-red-500 uppercase">SELL</span>
                </div>
              ))}
            </div>
          </div>

          {/* PARAMETERS ROW */}
          <div className="grid grid-cols-4 gap-4">
            <div className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-2 text-[10px] uppercase text-muted-foreground">
                <Target className="h-3 w-3" /> Entry
              </div>
              <p className="mt-1 font-mono text-lg font-bold">4036.60010</p>
            </div>
            <div className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-2 text-[10px] uppercase text-muted-foreground">
                <Shield className="h-3 w-3 text-red-500" /> Stop Loss
              </div>
              <p className="mt-1 font-mono text-lg font-bold text-red-500">4060.45095</p>
            </div>
            <div className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-2 text-[10px] uppercase text-muted-foreground">
                <TrendingUp className="h-3 w-3 text-green-500" /> Take Profit
              </div>
              <p className="mt-1 font-mono text-lg font-bold text-green-500">3988.89839</p>
            </div>
            <div className="rounded-xl border bg-card p-4">
              <div className="flex items-center gap-2 text-[10px] uppercase text-muted-foreground">
                <Activity className="h-3 w-3" /> Risk/Reward
              </div>
              <p className="mt-1 font-mono text-lg font-bold">1:2</p>
            </div>
          </div>

          {/* MAIN 3-COLUMN CONTENT */}
          <div className="grid gap-6 lg:grid-cols-12">
            {/* LEFT COLUMN */}
            <div className="space-y-6 lg:col-span-3">
              <ScoreBreakdown 
                compositeScore={result.composite_score || 65.8} 
                breakdown={result.confidence_breakdown || {
                  market_structure: 85,
                  momentum: 55.5,
                  trend: 50,
                  volatility: 75,
                  ai_prediction: 50
                }} 
              />
            </div>

            {/* MIDDLE COLUMN */}
            <div className="space-y-6 lg:col-span-6">
              <MarketStructureChart data={result.market_structure} />
              <div className="rounded-xl border bg-card p-5">
                <h3 className="mb-4 text-sm font-medium text-muted-foreground">Price Chart ({symbol} - {timeframe})</h3>
                <SignalCandlestick 
                  data={candleData} 
                  entryPrice={4036.60010} 
                  stopLoss={4060.45095} 
                  takeProfit={3988.89839}
                  signal="SELL"
                />
              </div>
            </div>

            {/* RIGHT COLUMN */}
            <div className="space-y-6 lg:col-span-3">
              <MarketStructureDetails data={result.market_structure} />
              <KeyIndicators indicators={result.indicators_used} />
              <div className="rounded-xl border bg-card p-5">
                <h3 className="mb-2 text-sm font-medium text-muted-foreground">Recommendation</h3>
                <p className="text-xs leading-relaxed text-muted-foreground">
                  Wait for confirmation or consider hedge position. Avoid aggressive directional bias.
                </p>
              </div>
            </div>
          </div>

          {/* FOOTER BAR */}
          <MarketStatusBar 
            regime={result.market_regime}
            volatility="High"
            volume="High"
            liquidity="Good"
            newsImpact="Medium"
            risk="Neutral"
            session="London"
          />
        </div>
      )}
    </div>
  );
}
