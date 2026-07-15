"use client";

import {
  TrendingUp,
  BarChart2,
  Activity,
  Droplets,
  Zap,
  ShieldCheck,
  Clock,
} from "lucide-react";

interface MarketStatusBarProps {
  regime?: string;
  volatility?: string;
  volume?: string;
  liquidity?: string;
  newsImpact?: string;
  risk?: string;
  session?: string;
}

export function MarketStatusBar({
  regime,
  volatility,
  volume,
  liquidity,
  newsImpact,
  risk,
  session,
}: MarketStatusBarProps) {
  const items = [
    { icon: TrendingUp, label: "Regime", value: regime || "Trending" },
    { icon: BarChart2, label: "Volatility", value: volatility || "High" },
    { icon: Activity, label: "Volume", value: volume || "High" },
    { icon: Droplets, label: "Liquidity", value: liquidity || "Good" },
    { icon: Zap, label: "News Impact", value: newsImpact || "Medium" },
    { icon: ShieldCheck, label: "Risk Environment", value: risk || "Neutral" },
    { icon: Clock, label: "Session", value: session || "London" },
  ];

  const getValueColor = (value: string) => {
    const v = value.toLowerCase();
    if (["high", "bearish", "elevated", "aggressive"].includes(v)) return "text-red-500";
    if (["low", "bullish", "good", "calm", "safe"].includes(v)) return "text-green-500";
    if (["medium", "neutral", "moderate"].includes(v)) return "text-amber-500";
    return "text-foreground";
  };

  return (
    <div className="rounded-xl border bg-card/50 p-4 backdrop-blur-sm">
      <div className="flex flex-wrap items-center justify-between gap-6">
        {items.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.label} className="flex items-center gap-2.5">
              <Icon className="h-4 w-4 text-muted-foreground" />
              <div className="flex flex-col">
                <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                  {item.label}
                </span>
                <span className={`text-xs font-bold ${getValueColor(item.value)}`}>
                  {item.value}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
