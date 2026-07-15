"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";

interface KeyIndicatorsProps {
  indicators: string[];
}

export function KeyIndicators({ indicators }: KeyIndicatorsProps) {
  // Mock data for radar visualization based on common technical indicators
  const data = [
    { subject: "RSI", A: 65, fullMark: 100 },
    { subject: "EMA 12", A: 85, fullMark: 100 },
    { subject: "EMA 20", A: 75, fullMark: 100 },
    { subject: "EMA 50", A: 45, fullMark: 100 },
    { subject: "EMA 50", A: 35, fullMark: 100 }, // Duplicate label from screenshot
    { subject: "SMA 200", A: 25, fullMark: 100 },
    { subject: "MACD", A: 55, fullMark: 100 },
    { subject: "ATR", A: 80, fullMark: 100 },
  ];

  return (
    <div className="rounded-xl border bg-card p-5">
      <h3 className="mb-2 text-sm font-medium text-muted-foreground">Key Indicators</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data}>
            <PolarGrid stroke="rgba(255,255,255,0.1)" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: "hsl(var(--muted-foreground))", fontSize: 10 }}
            />
            <PolarRadiusAxis 
              angle={30} 
              domain={[0, 100]} 
              tick={false}
              axisLine={false}
            />
            <Radar
              name="Market"
              dataKey="A"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function MarketStructureDetails({ data }: { data: any }) {
  const details = [
    { label: "Trend", value: data.trend },
    { label: "Swing Highs", value: data.swing_highs },
    { label: "Swing Lows", value: data.swing_lows },
    { label: "Break of Structure", value: data.break_of_structure },
    { label: "Change of Character", value: data.change_of_character },
    { label: "FVG Detected", value: data.fair_value_gaps },
    { label: "Liq. Sweeps", value: data.liquidity_sweeps },
  ];

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">Market Structure Details</h3>
        <span className={`text-[10px] font-bold uppercase ${data.trend === "BEARISH" ? "text-red-500" : "text-green-500"}`}>
          {data.trend}
        </span>
      </div>
      <div className="space-y-2.5">
        {details.map((item) => (
          <div key={item.label} className="flex items-center justify-between border-b border-white/5 pb-1.5 text-xs">
            <span className="text-muted-foreground">{item.label}</span>
            <span className="font-mono font-medium">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
