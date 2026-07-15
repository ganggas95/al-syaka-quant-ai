"use client";

import { RotateCcw } from "lucide-react";

interface BacktestProgressProps {
  percent: number;
  status?: string;
  trading?: number;
}

/**
 * Progress bar for backtesting — menampilkan percentage bar real-time via SSE.
 */
export function BacktestProgress({ percent, status, trading }: BacktestProgressProps) {
  const pct = Math.min(Math.max(percent, 0), 100);

  return (
    <div className="rounded-lg border bg-card p-5">
      <div className="flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <RotateCcw className="h-5 w-5 animate-spin text-primary" />
          <div>
            <p className="text-sm font-medium">Running Backtest...</p>
            <p className="text-xs text-muted-foreground">
              {status || `Processing historical data`}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-2xl font-bold text-primary">{pct}%</p>
          {trading !== undefined && (
            <p className="text-xs text-muted-foreground">{trading} trades</p>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mt-4 h-2.5 w-full overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full bg-gradient-to-r from-blue-500 via-primary to-green-500 transition-all duration-500 ease-out"
          style={{ width: `${pct}%` }}
        />
      </div>

      {/* Steps indicator */}
      <div className="mt-3 flex justify-between text-[10px] text-muted-foreground">
        <span className={pct >= 0 ? "text-primary" : ""}>Fetching Data</span>
        <span className={pct >= 25 ? "text-primary" : ""}>Computing Indicators</span>
        <span className={pct >= 50 ? "text-primary" : ""}>Running Signals</span>
        <span className={pct >= 75 ? "text-primary" : ""}>Calculating Metrics</span>
        <span className={pct >= 100 ? "text-green-500" : ""}>Done</span>
      </div>
    </div>
  );
}
