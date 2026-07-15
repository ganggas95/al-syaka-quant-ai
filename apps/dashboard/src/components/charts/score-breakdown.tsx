"use client";

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

interface ScoreBreakdownProps {
  compositeScore: number;
  breakdown: {
    market_structure: number;
    momentum: number;
    trend: number;
    volatility: number;
    ai_prediction: number;
  };
}

export function ScoreBreakdown({
  compositeScore,
  breakdown,
}: ScoreBreakdownProps) {
  const items = [
    { name: "Market Structure", value: breakdown.market_structure, color: "#3b82f6" },
    { name: "Momentum", value: breakdown.momentum, color: "#6366f1" },
    { name: "Trend", value: breakdown.trend, color: "#22c55e" },
    { name: "Volatility", value: breakdown.volatility, color: "#eab308" },
    { name: "AI Prediction", value: breakdown.ai_prediction, color: "#d946ef" },
  ];

  const total = items.reduce((s, i) => s + i.value, 0) || 1;
  const donutData = items.map(item => ({
    ...item,
    pct: ((item.value / total) * 100).toFixed(1)
  }));

  return (
    <div className="space-y-6">
      {/* Composite Score Gauge */}
      <div className="rounded-xl border bg-card p-5">
        <h3 className="mb-4 text-sm font-medium text-muted-foreground">Composite Score</h3>
        <div className="flex flex-col items-center">
          <div className="relative flex h-32 w-full items-center justify-center overflow-hidden">
            <svg width="200" height="100" viewBox="0 0 200 100">
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke="hsl(var(--secondary))"
                strokeWidth="16"
                strokeLinecap="round"
              />
              <path
                d="M 20 100 A 80 80 0 0 1 180 100"
                fill="none"
                stroke={compositeScore >= 70 ? "#22c55e" : compositeScore >= 40 ? "#3b82f6" : "#ef4444"}
                strokeWidth="16"
                strokeLinecap="round"
                strokeDasharray="251.32"
                strokeDashoffset={251.32 * (1 - compositeScore / 100)}
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute bottom-0 flex flex-col items-center">
              <span className="text-3xl font-bold">{compositeScore.toFixed(1)}%</span>
              <span className="text-[10px] uppercase tracking-wider text-muted-foreground">
                {compositeScore >= 70 ? "STRONG" : compositeScore >= 40 ? "MEDIUM" : "WEAK"}
              </span>
            </div>
          </div>
          
          <div className="mt-6 w-full space-y-3">
            {items.map((item) => (
              <div key={item.name} className="space-y-1">
                <div className="flex justify-between text-[10px] font-medium uppercase text-muted-foreground">
                  <span>{item.name}</span>
                  <span>{item.value}%</span>
                </div>
                <div className="h-1.5 w-full rounded-full bg-secondary">
                  <div 
                    className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${item.value}%`, backgroundColor: item.color }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Score Contribution Donut */}
      <div className="rounded-xl border bg-card p-5">
        <h3 className="mb-2 text-sm font-medium text-muted-foreground">Score Contribution</h3>
        <div className="flex items-center gap-2">
          <div className="h-40 w-40">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={65}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex-1 space-y-1.5">
            {donutData.map((item) => (
              <div key={item.name} className="flex items-center justify-between text-[10px]">
                <div className="flex items-center gap-1.5">
                  <div className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
                  <span className="text-muted-foreground">{item.name}</span>
                </div>
                <span className="font-mono font-medium">{item.pct}%</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
