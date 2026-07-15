"use client";

import { EquityCurve } from "@/components/charts/equity-curve";
import { MonthlyHeatmap } from "@/components/charts/monthly-heatmap";
import { PerfStats } from "@/components/charts/perf-stats";
import { SessionBreakdown } from "@/components/charts/session-breakdown";
import { BacktestProgress } from "@/components/shared/backtest-progress";
import {
    AlertTriangle,
    CheckCircle2,
    Play,
    RotateCcw,
    XCircle,
} from "lucide-react";
import { useRef, useState } from "react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface BacktestResult {
  config: {
    symbol: string;
    timeframe: string;
    period_days: number;
    initial_balance: number;
    risk_percent: number;
  };
  metrics: {
    total_trades: number;
    winning_trades: number;
    losing_trades: number;
    win_rate: number;
    net_profit: number;
    profit_factor: number;
    avg_profit_per_trade: number;
    avg_win: number;
    avg_loss: number;
    max_drawdown: number;
    max_drawdown_percent: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    calmar_ratio: number;
    max_consecutive_wins: number;
    max_consecutive_losses: number;
    best_trade: number;
    worst_trade: number;
  };
  summary: string;
  equity_curve: Array<{ timestamp: string; equity: number }>;
  monthly_returns: Record<string, number>;
  session_breakdown: {
    asia: {
      trades: number;
      wins: number;
      losses: number;
      win_rate: number;
      net_profit: number;
      avg_trade: number;
    };
    london: {
      trades: number;
      wins: number;
      losses: number;
      win_rate: number;
      net_profit: number;
      avg_trade: number;
    };
    newyork: {
      trades: number;
      wins: number;
      losses: number;
      win_rate: number;
      net_profit: number;
      avg_trade: number;
    };
  };
  trades: Array<{
    entry_time: string;
    signal: string;
    direction: string;
    entry: number;
    exit: number;
    result: string;
    pips: number;
    profit: number;
    exit_reason: string;
  }>;
}

export default function BacktestingPage() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState("H1");
  const [days, setDays] = useState(365);
  const [balance, setBalance] = useState(10000);
  const [riskPct, setRiskPct] = useState(1.0);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const runBacktest = async () => {
    // Cancel previous run if any
    if (abortRef.current) {
      abortRef.current.abort();
    }
    abortRef.current = new AbortController();
    const { signal } = abortRef.current;

    setLoading(true);
    setProgress(0);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(
        `${API_URL}/api/v1/backtesting/run-stream` +
          `?symbol=${symbol}&timeframe=${timeframe}&days=${days}` +
          `&initial_balance=${balance}&risk_percent=${riskPct}`,
        { method: "POST", signal },
      );

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body?.getReader();
      if (!reader) throw new Error("No response body");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const dataStr = line.slice(6);

          try {
            const data = JSON.parse(dataStr);

            if (data.type === "progress") {
              setProgress(data.percent);
            } else if (data.type === "complete") {
              setResult(data.result);
              setProgress(100);
            } else if (data.type === "error") {
              setError(data.detail);
            }
          } catch {
            // Skip malformed JSON
          }
        }
      }
    } catch (e: any) {
      if (e.name !== "AbortError") {
        setError(e.message || "Backtest failed");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Backtesting</h1>
          <p className="text-muted-foreground">
            Historical strategy testing & performance analysis
          </p>
        </div>
      </div>

      {/* Config Form */}
      <div className="rounded-lg border bg-card p-6">
        <h2 className="mb-4 text-lg font-semibold">Configuration</h2>
        <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">
              Symbol
            </label>
            <select
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            >
              {[
                "EURUSD",
                "XAUUSD",
                "GBPUSD",
                "USDJPY",
                "AUDUSD",
                "USDCAD",
                "NZDUSD",
              ].map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">
              Timeframe
            </label>
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            >
              {["M15", "M30", "H1", "H4", "D1"].map((tf) => (
                <option key={tf} value={tf}>
                  {tf}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">
              Period (days)
            </label>
            <input
              type="number"
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              min={30}
              max={1825}
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">
              Balance ($)
            </label>
            <input
              type="number"
              value={balance}
              onChange={(e) => setBalance(Number(e.target.value))}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">
              Risk / Trade (%)
            </label>
            <input
              type="number"
              value={riskPct}
              onChange={(e) => setRiskPct(Number(e.target.value))}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm"
              min={0.1}
              max={5}
              step={0.1}
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={runBacktest}
              disabled={loading}
              className="flex w-full items-center justify-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
            >
              {loading ? (
                <RotateCcw className="h-4 w-4 animate-spin" />
              ) : (
                <Play className="h-4 w-4" />
              )}
              {loading ? "Running..." : "Run Backtest"}
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-500">
          <AlertTriangle className="h-4 w-4" />
          {error}
        </div>
      )}

      {/* Progress Bar (real-time via SSE) */}
      {loading && (
        <BacktestProgress
          percent={progress}
          status="Processing historical data..."
        />
      )}

      {/* Results */}
      {result && (
        <>
          {/* Summary */}
          <div className="rounded-lg border bg-card p-4 text-sm text-muted-foreground">
            {result.summary}
          </div>

          {/* Performance Stats Cards */}
          <PerfStats metrics={result.metrics} />

          {/* Charts Row */}
          <div className="grid gap-6 lg:grid-cols-2">
            <EquityCurve
              data={result.equity_curve}
              initialBalance={result.config.initial_balance}
            />
            <MonthlyHeatmap data={result.monthly_returns} />
          </div>

          {/* Session Breakdown */}
          {result.session_breakdown && (
            <SessionBreakdown data={result.session_breakdown} />
          )}

          {/* Trades Table */}
          <div className="rounded-lg border bg-card">
            <div className="border-b px-4 py-3">
              <h3 className="text-sm font-medium">Recent Trades</h3>
              <p className="text-xs text-muted-foreground">
                Showing last {result.trades.length} of{" "}
                {result.metrics.total_trades} trades
              </p>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="px-4 py-2 text-left">Time</th>
                    <th className="px-4 py-2 text-left">Signal</th>
                    <th className="px-4 py-2 text-right">Entry</th>
                    <th className="px-4 py-2 text-right">Exit</th>
                    <th className="px-4 py-2 text-right">Pips</th>
                    <th className="px-4 py-2 text-right">Profit</th>
                    <th className="px-4 py-2 text-center">Result</th>
                    <th className="px-4 py-2 text-left">Exit Reason</th>
                  </tr>
                </thead>
                <tbody>
                  {result.trades.map((t, i) => (
                    <tr
                      key={i}
                      className="border-b last:border-0 hover:bg-secondary/30"
                    >
                      <td className="px-4 py-2 text-muted-foreground">
                        {new Date(t.entry_time).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`font-medium ${t.signal === "BUY" ? "text-green-500" : "text-red-500"}`}
                        >
                          {t.signal}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-right font-mono">
                        {t.entry.toFixed(5)}
                      </td>
                      <td className="px-4 py-2 text-right font-mono">
                        {t.exit?.toFixed(5) || "-"}
                      </td>
                      <td
                        className={`px-4 py-2 text-right font-mono ${t.pips > 0 ? "text-green-500" : "text-red-500"}`}
                      >
                        {t.pips > 0 ? "+" : ""}
                        {t.pips}
                      </td>
                      <td
                        className={`px-4 py-2 text-right font-mono ${t.profit > 0 ? "text-green-500" : "text-red-500"}`}
                      >
                        {t.profit > 0 ? "+" : ""}${t.profit.toFixed(2)}
                      </td>
                      <td className="px-4 py-2 text-center">
                        {t.result === "WIN" ? (
                          <CheckCircle2 className="mx-auto h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="mx-auto h-4 w-4 text-red-500" />
                        )}
                      </td>
                      <td className="px-4 py-2 text-muted-foreground">
                        {t.exit_reason}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
