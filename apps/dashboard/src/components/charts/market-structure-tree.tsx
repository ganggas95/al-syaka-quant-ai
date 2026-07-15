"use client";

import { ChevronRight } from "lucide-react";

interface MarketStructureData {
  trend: string;
  swing_highs: number;
  swing_lows: number;
  break_of_structure: number;
  change_of_character: number;
  fair_value_gaps: number;
  liquidity_sweeps: number;
}

interface MarketStructureTreeProps {
  data: MarketStructureData;
}

/**
 * Tree diagram untuk Market Structure.
 * Root: Trend (BULLISH/BEARISH) → Branch 1: Structure (Swing, BOS, CHOCH)
 * → Branch 2: Price Action (FVG, Liquidity Sweeps)
 */
export function MarketStructureTree({ data }: MarketStructureTreeProps) {
  const trendColor =
    data.trend === "BULLISH"
      ? "text-green-500 border-green-500/30 bg-green-500/10"
      : data.trend === "BEARISH"
        ? "text-red-500 border-red-500/30 bg-red-500/10"
        : "text-muted-foreground border-border bg-secondary/50";

  const items: Array<{
    label: string;
    value: number;
    color: string;
    desc: string;
  }> = [
    {
      label: "Swing Highs",
      value: data.swing_highs,
      color: "text-green-500",
      desc: "Higher highs in uptrend",
    },
    {
      label: "Swing Lows",
      value: data.swing_lows,
      color: "text-red-500",
      desc: "Lower lows in downtrend",
    },
    {
      label: "Break of Structure",
      value: data.break_of_structure,
      color: data.break_of_structure > 0 ? "text-orange-500" : "text-muted-foreground",
      desc: "Key level broken",
    },
    {
      label: "Change of Character",
      value: data.change_of_character,
      color: data.change_of_character > 0 ? "text-purple-500" : "text-muted-foreground",
      desc: "Trend shift detected",
    },
    {
      label: "Fair Value Gaps",
      value: data.fair_value_gaps,
      color: data.fair_value_gaps > 0 ? "text-cyan-500" : "text-muted-foreground",
      desc: "Inefficient price",
    },
    {
      label: "Liquidity Sweeps",
      value: data.liquidity_sweeps,
      color: data.liquidity_sweeps > 0 ? "text-yellow-500" : "text-muted-foreground",
      desc: "Stop hunts detected",
    },
  ];

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-medium">Market Structure</h3>

      {/* Root: Trend */}
      <div className="mb-4 flex items-center justify-center">
        <div
          className={`rounded-lg border px-4 py-2 text-center text-sm font-bold ${trendColor}`}
        >
          {data.trend}
        </div>
      </div>

      {/* Tree branches */}
      <div className="space-y-1">
        {items.map((item) => (
          <div
            key={item.label}
            className="group flex items-center justify-between rounded-md px-3 py-2 text-sm transition-colors hover:bg-secondary/50"
          >
            <div className="flex items-center gap-2">
              <ChevronRight className="h-3 w-3 text-muted-foreground" />
              <span className="text-muted-foreground">{item.label}</span>
              <span className="hidden text-[10px] text-muted-foreground/60 group-hover:inline">
                {item.desc}
              </span>
            </div>
            <span className={`font-mono font-medium ${item.color}`}>
              {item.value}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
