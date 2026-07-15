"use client";

import { History, Pause, Play, RotateCcw, SkipBack, SkipForward } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";

import { TradeTimeline } from "@/components/charts/trade-timeline";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface HistorySignal {
  id: number;
  signal: string;
  confidence: number;
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  risk_reward: number | null;
  risk_level: string | null;
  reasons: string[];
  indicators_used: string[];
  outcome_result: string | null;
  outcome_profit: number | null;
  created_at: string | null;
}

/**
 * Historical Replay page — browse, replay, and analyze past signals.
 * Phase 3: Playback controls with auto-advance.
 */
export default function ReplayPage() {
  const [symbol, setSymbol] = useState("XAUUSD");
  const [signals, setSignals] = useState<HistorySignal[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(2);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Fetch signal history
  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_URL}/api/v1/signals/${symbol}/history?limit=50`,
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setSignals(data.signals || []);
      setCurrentIdx(0);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  // Fetch on mount and symbol change
  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  // Playback timer
  useEffect(() => {
    if (playing && signals.length > 0) {
      timerRef.current = setInterval(() => {
        setCurrentIdx((prev) => {
          if (prev >= signals.length - 1) {
            setPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 3000 / speed);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [playing, signals.length, speed]);

  const togglePlay = () => setPlaying((p) => !p);
  const goPrev = () => setCurrentIdx((i) => Math.max(0, i - 1));
  const goNext = () =>
    setCurrentIdx((i) => Math.min(signals.length - 1, i + 1));
  const restart = () => {
    setCurrentIdx(0);
    setPlaying(true);
  };

  const currentSignal = signals[currentIdx];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-3xl font-bold tracking-tight">
            <History className="h-7 w-7 text-primary" />
            Historical Replay
          </h1>
          <p className="text-muted-foreground">
            Browse and replay past trading signals
          </p>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap items-end gap-3 rounded-lg border bg-card p-4">
        {/* Symbol */}
        <div>
          <label className="mb-1 block text-xs text-muted-foreground">
            Symbol
          </label>
          <select
            value={symbol}
            onChange={(e) => {
              setSymbol(e.target.value);
              setPlaying(false);
            }}
            className="rounded-md border bg-background px-3 py-2 text-sm font-medium"
          >
            <optgroup label="INDICES">
              <option value="US30">US30</option>
              <option value="NAS100">NAS100</option>
              <option value="SPX500">SPX500</option>
            </optgroup>
            <optgroup label="FOREX">
              <option value="EURUSD">EURUSD</option>
              <option value="GBPUSD">GBPUSD</option>
              <option value="USDJPY">USDJPY</option>
              <option value="XAUUSD">XAUUSD</option>
            </optgroup>
            <optgroup label="CRYPTO">
              <option value="BTCUSD">BTCUSD</option>
              <option value="ETHUSD">ETHUSD</option>
            </optgroup>
          </select>
        </div>

        {/* Playback controls */}
        <div className="flex items-center gap-1.5">
          <button
            onClick={goPrev}
            disabled={currentIdx <= 0}
            className="rounded-md bg-secondary p-2 transition-colors hover:bg-secondary/80 disabled:opacity-40"
            title="Previous signal"
          >
            <SkipBack className="h-4 w-4" />
          </button>
          <button
            onClick={togglePlay}
            disabled={signals.length === 0}
            className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
          >
            {playing ? (
              <><Pause className="h-4 w-4" /> Pause</>
            ) : (
              <><Play className="h-4 w-4" /> Play</>
            )}
          </button>
          <button
            onClick={goNext}
            disabled={currentIdx >= signals.length - 1}
            className="rounded-md bg-secondary p-2 transition-colors hover:bg-secondary/80 disabled:opacity-40"
            title="Next signal"
          >
            <SkipForward className="h-4 w-4" />
          </button>
          <button
            onClick={restart}
            disabled={signals.length === 0}
            className="rounded-md bg-secondary p-2 transition-colors hover:bg-secondary/80 disabled:opacity-40"
            title="Restart playback"
          >
            <RotateCcw className="h-4 w-4" />
          </button>
        </div>

        {/* Speed */}
        <div className="flex items-center gap-2">
          <label className="text-xs text-muted-foreground">Speed</label>
          <div className="flex gap-1">
            {[1, 2, 5, 10].map((s) => (
              <button
                key={s}
                onClick={() => setSpeed(s)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium ${
                  speed === s
                    ? "bg-primary text-primary-foreground"
                    : "bg-secondary text-muted-foreground"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>

        {/* Refresh */}
        <button
          onClick={fetchHistory}
          disabled={loading}
          className="ml-auto flex items-center gap-1.5 rounded-md bg-secondary px-3 py-2 text-xs font-medium transition-colors hover:bg-secondary/80 disabled:opacity-50"
        >
          <RotateCcw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-500">
          {error}
        </div>
      )}

      {/* Progress bar */}
      {signals.length > 0 && (
        <div className="space-y-1">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              Signal {currentIdx + 1} of {signals.length}
            </span>
            <span>
              {((currentIdx + 1) / signals.length * 100).toFixed(0)}%
            </span>
          </div>
          <div className="h-1.5 overflow-hidden rounded-full bg-secondary">
            <div
              className="h-full rounded-full bg-primary transition-all duration-300"
              style={{
                width: `${((currentIdx + 1) / signals.length) * 100}%`,
              }}
            />
          </div>
        </div>
      )}

      {/* Two-column layout */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Timeline */}
        <TradeTimeline
          signals={signals}
          selectedId={currentSignal?.id}
          onSelect={(id) => {
            const idx = signals.findIndex((s) => s.id === id);
            if (idx >= 0) {
              setCurrentIdx(idx);
              setPlaying(false);
            }
          }}
        />

        {/* Current signal detail */}
        <div className="rounded-lg border bg-card p-4">
          <h3 className="mb-3 text-sm font-medium">Signal Detail</h3>

          {currentSignal ? (
            <div className="space-y-4">
              {/* Signal + Confidence */}
              <div className="flex items-center gap-3">
                <span
                  className={`rounded-lg px-4 py-2 text-lg font-bold ${
                    currentSignal.signal === "BUY"
                      ? "bg-green-500/10 text-green-500"
                      : currentSignal.signal === "SELL"
                        ? "bg-red-500/10 text-red-500"
                        : "bg-yellow-500/10 text-yellow-500"
                  }`}
                >
                  {currentSignal.signal}
                </span>
                <div>
                  <p className="text-2xl font-bold">
                    {currentSignal.confidence}%
                  </p>
                  <p className="text-xs text-muted-foreground">Confidence</p>
                </div>
                {currentSignal.outcome_result && (
                  <span
                    className={`ml-auto rounded-full px-3 py-1 text-xs font-medium ${
                      currentSignal.outcome_result === "WIN"
                        ? "bg-green-500/10 text-green-500"
                        : currentSignal.outcome_result === "LOSS"
                          ? "bg-red-500/10 text-red-500"
                          : "bg-yellow-500/10 text-yellow-500"
                    }`}
                  >
                    {currentSignal.outcome_result}
                  </span>
                )}
              </div>

              {/* Price levels */}
              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-md bg-secondary/50 p-3 text-center">
                  <p className="text-xs text-muted-foreground">Entry</p>
                  <p className="font-mono font-medium">
                    {currentSignal.entry_price?.toFixed(2) ?? "-"}
                  </p>
                </div>
                <div className="rounded-md bg-secondary/50 p-3 text-center">
                  <p className="text-xs text-muted-foreground">Stop Loss</p>
                  <p className="font-mono font-medium text-red-500">
                    {currentSignal.stop_loss?.toFixed(2) ?? "-"}
                  </p>
                </div>
                <div className="rounded-md bg-secondary/50 p-3 text-center">
                  <p className="text-xs text-muted-foreground">Take Profit</p>
                  <p className="font-mono font-medium text-green-500">
                    {currentSignal.take_profit?.toFixed(2) ?? "-"}
                  </p>
                </div>
              </div>

              {/* Reasons */}
              {currentSignal.reasons.length > 0 && (
                <div>
                  <p className="mb-1 text-xs text-muted-foreground">Reasons</p>
                  <ul className="space-y-1">
                    {currentSignal.reasons.map((r, i) => (
                      <li
                        key={i}
                        className="rounded-md bg-secondary/30 px-2.5 py-1.5 text-xs"
                      >
                        {r}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Indicators */}
              {currentSignal.indicators_used.length > 0 && (
                <div>
                  <p className="mb-1 text-xs text-muted-foreground">Indicators</p>
                  <div className="flex flex-wrap gap-1">
                    {currentSignal.indicators_used.map((ind, i) => (
                      <span
                        key={i}
                        className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium"
                      >
                        {ind}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
              {loading
                ? "Loading..."
                : "No signals found. Generate some signals first at the Signals page."}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
