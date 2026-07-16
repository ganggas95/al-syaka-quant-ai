"use client";

import {
    Activity,
    Scale,
    Shield,
    Target,
    TrendingDown,
    TrendingUp,
} from "lucide-react";

interface RiskSummaryProps {
  entryPrice?: number;
  stopLoss?: number;
  takeProfit?: number;
  riskReward?: number;
  riskLevel?: string;
  lotSize?: number;
  positionMultiplier?: number;
  tradeQuality?: string;
}

function getRiskBadgeColor(level?: string) {
  switch (level?.toLowerCase()) {
    case "low":
      return "bg-green-500/10 text-green-500 border-green-500/20";
    case "medium":
    case "moderate":
      return "bg-amber-500/10 text-amber-500 border-amber-500/20";
    case "high":
      return "bg-red-500/10 text-red-500 border-red-500/20";
    default:
      return "bg-secondary text-muted-foreground border-white/5";
  }
}

function getQualityColor(quality?: string) {
  switch (quality?.toLowerCase()) {
    case "good":
    case "excellent":
      return "text-green-500";
    case "average":
    case "fair":
      return "text-amber-500";
    case "poor":
      return "text-red-500";
    default:
      return "text-muted-foreground";
  }
}

export function RiskSummary({
  entryPrice,
  stopLoss,
  takeProfit,
  riskReward,
  riskLevel,
  lotSize,
  positionMultiplier,
  tradeQuality,
}: RiskSummaryProps) {
  const hasData = entryPrice != null || stopLoss != null || takeProfit != null;

  if (!hasData && !riskLevel) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-3 flex items-center gap-2">
          <Shield className="h-5 w-5 text-muted-foreground" />
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            Risk Summary
          </h3>
        </div>
        <p className="text-xs text-muted-foreground">
          No risk data available for this signal.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-muted-foreground" />
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            Risk Summary
          </h3>
        </div>
        {riskLevel && (
          <span
            className={`rounded-full border px-2.5 py-0.5 text-[10px] font-bold uppercase ${getRiskBadgeColor(riskLevel)}`}
          >
            {riskLevel}
          </span>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Entry Price */}
        <div className="rounded-lg bg-secondary/30 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase text-muted-foreground">
            <Target className="h-3 w-3" />
            Entry
          </div>
          <p className="mt-1 font-mono text-sm font-bold">
            {entryPrice != null ? entryPrice.toFixed(5) : "—"}
          </p>
        </div>

        {/* Stop Loss */}
        <div className="rounded-lg bg-secondary/30 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase text-muted-foreground">
            <TrendingDown className="h-3 w-3 text-red-500" />
            Stop Loss
          </div>
          <p className="mt-1 font-mono text-sm font-bold text-red-500">
            {stopLoss != null ? stopLoss.toFixed(5) : "—"}
          </p>
        </div>

        {/* Take Profit */}
        <div className="rounded-lg bg-secondary/30 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase text-muted-foreground">
            <TrendingUp className="h-3 w-3 text-green-500" />
            Take Profit
          </div>
          <p className="mt-1 font-mono text-sm font-bold text-green-500">
            {takeProfit != null ? takeProfit.toFixed(5) : "—"}
          </p>
        </div>

        {/* Risk/Reward */}
        <div className="rounded-lg bg-secondary/30 p-3">
          <div className="flex items-center gap-1.5 text-[10px] uppercase text-muted-foreground">
            <Activity className="h-3 w-3" />
            Risk/Reward
          </div>
          <p className="mt-1 font-mono text-sm font-bold">
            {riskReward != null ? `1:${riskReward.toFixed(1)}` : "—"}
          </p>
        </div>
      </div>

      {/* Position sizing row */}
      {(lotSize != null || positionMultiplier != null || tradeQuality) && (
        <div className="mt-4 flex flex-wrap items-center gap-4 rounded-lg bg-secondary/20 p-3">
          {lotSize != null && (
            <div className="flex items-center gap-1.5 text-xs">
              <Scale className="h-3 w-3 text-muted-foreground" />
              <span className="text-muted-foreground">Lot:</span>
              <span className="font-mono font-medium">
                {lotSize.toFixed(2)}
              </span>
            </div>
          )}
          {positionMultiplier != null && (
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-muted-foreground">Multiplier:</span>
              <span className="font-mono font-medium">
                x{positionMultiplier.toFixed(1)}
              </span>
            </div>
          )}
          {tradeQuality && (
            <div className="flex items-center gap-1.5 text-xs">
              <span className="text-muted-foreground">Quality:</span>
              <span className={`font-bold ${getQualityColor(tradeQuality)}`}>
                {tradeQuality}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
