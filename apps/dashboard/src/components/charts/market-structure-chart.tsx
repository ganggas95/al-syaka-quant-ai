"use client";

import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, CartesianGrid } from "recharts";

interface MarketStructureChartProps {
  data: {
    trend: string;
    swing_highs: number;
    swing_lows: number;
    break_of_structure: number;
    change_of_character: number;
    fair_value_gaps: number;
    liquidity_sweeps: number;
  };
}

export function MarketStructureChart({ data }: MarketStructureChartProps) {
  const chartData = [
    { name: "Trend", value: data.trend === "BULLISH" ? 8 : data.trend === "BEARISH" ? 8 : 4, type: data.trend },
    { name: "Swing Highs", value: data.swing_highs, type: "BEARISH" },
    { name: "Swing Lows", value: data.swing_lows, type: "BULLISH" },
    { name: "Break of Structure", value: data.break_of_structure, type: "BEARISH" },
    { name: "Change of Character", value: data.change_of_character, type: "BULLISH" },
    { name: "FVG Detected", value: data.fair_value_gaps, type: "NEUTRAL" },
    { name: "Liq. Sweeps", value: data.liquidity_sweeps, type: "NEUTRAL" },
  ];

  const getColor = (type: string) => {
    if (type === "BULLISH") return "#22c55e";
    if (type === "BEARISH") return "#ef4444";
    return "#f59e0b";
  };

  return (
    <div className="rounded-xl border bg-card p-5">
      <h3 className="mb-4 text-sm font-medium text-muted-foreground">Market Structure Overview</h3>
      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis 
              dataKey="name" 
              fontSize={9} 
              tickLine={false} 
              axisLine={false}
              interval={0}
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <YAxis 
              fontSize={10} 
              tickLine={false} 
              axisLine={false} 
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <Bar dataKey="value" radius={[4, 4, 0, 0]} barSize={30}>
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getColor(entry.type)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 flex justify-center gap-4 text-[10px] text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-red-500" />
          <span>Bearish Pressure</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-amber-500" />
          <span>Neutral / Mixed</span>
        </div>
        <div className="flex items-center gap-1.5">
          <div className="h-2 w-2 rounded-full bg-green-500" />
          <span>Bullish Pressure</span>
        </div>
      </div>
    </div>
  );
}
