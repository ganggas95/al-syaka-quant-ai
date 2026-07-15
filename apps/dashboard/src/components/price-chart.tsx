"use client";

import { useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";

interface ChartData {
  time: string;
  price: number;
  sma20?: number;
  ema20?: number;
  bb_upper?: number;
  bb_lower?: number;
}

interface PriceChartProps {
  data?: ChartData[];
  symbol?: string;
  price?: number;
  change?: string;
  trend?: "up" | "down";
}

const sampleData: ChartData[] = [
  { time: "09:00", price: 1.0820, sma20: 1.0815, ema20: 1.0818, bb_upper: 1.0835, bb_lower: 1.0805 },
  { time: "09:05", price: 1.0825, sma20: 1.0816, ema20: 1.0819, bb_upper: 1.0836, bb_lower: 1.0804 },
  { time: "09:10", price: 1.0818, sma20: 1.0817, ema20: 1.0820, bb_upper: 1.0837, bb_lower: 1.0803 },
  { time: "09:15", price: 1.0822, sma20: 1.0818, ema20: 1.0821, bb_upper: 1.0838, bb_lower: 1.0802 },
  { time: "09:20", price: 1.0830, sma20: 1.0819, ema20: 1.0822, bb_upper: 1.0839, bb_lower: 1.0801 },
  { time: "09:25", price: 1.0827, sma20: 1.0820, ema20: 1.0823, bb_upper: 1.0840, bb_lower: 1.0800 },
  { time: "09:30", price: 1.0835, sma20: 1.0821, ema20: 1.0824, bb_upper: 1.0841, bb_lower: 1.0799 },
  { time: "09:35", price: 1.0840, sma20: 1.0822, ema20: 1.0825, bb_upper: 1.0842, bb_lower: 1.0798 },
  { time: "09:40", price: 1.0838, sma20: 1.0823, ema20: 1.0826, bb_upper: 1.0843, bb_lower: 1.0797 },
  { time: "09:45", price: 1.0842, sma20: 1.0824, ema20: 1.0827, bb_upper: 1.0844, bb_lower: 1.0796 },
  { time: "09:50", price: 1.0835, sma20: 1.0825, ema20: 1.0828, bb_upper: 1.0845, bb_lower: 1.0795 },
  { time: "09:55", price: 1.0838, sma20: 1.0826, ema20: 1.0829, bb_upper: 1.0846, bb_lower: 1.0794 },
  { time: "10:00", price: 1.0845, sma20: 1.0827, ema20: 1.0830, bb_upper: 1.0847, bb_lower: 1.0793 },
];

const overlayOptions = [
  { id: "sma20", label: "SMA 20", color: "#f59e0b" },
  { id: "ema20", label: "EMA 20", color: "#3b82f6" },
  { id: "bb", label: "Bollinger", color: "#8b5cf6" },
];

export function PriceChart({
  data = sampleData,
  symbol: externalSymbol,
  price: externalPrice,
  change: externalChange,
  trend: externalTrend,
}: PriceChartProps) {
  const [activeOverlays, setActiveOverlays] = useState<string[]>(["sma20", "ema20"]);

  const toggleOverlay = (id: string) => {
    setActiveOverlays((prev) =>
      prev.includes(id) ? prev.filter((o) => o !== id) : [...prev, id]
    );
  };

  const latestPrice = externalPrice ?? data[data.length - 1]?.price ?? 0;
  const latestChange = externalChange ?? "+0.25%";
  const isUp = externalTrend !== undefined ? externalTrend === "up" : latestPrice >= (data[data.length - 2]?.price ?? latestPrice);

  return (
    <div className="rounded-lg border bg-card p-4">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-muted-foreground">
            {externalSymbol || "EUR/USD"}
          </h3>
          <p className="text-2xl font-bold">{latestPrice.toFixed(4)}</p>
        </div>
        <div className="text-right">
          <p className={`text-sm font-medium ${isUp ? "text-green-500" : "text-red-500"}`}>
            {latestChange}
          </p>
          <p className="text-xs text-muted-foreground">Today</p>
        </div>
      </div>

      {/* Overlay Toggles */}
      <div className="mb-3 flex gap-2">
        {overlayOptions.map((opt) => (
          <button
            key={opt.id}
            onClick={() => toggleOverlay(opt.id)}
            className={`rounded-full px-3 py-1 text-xs font-medium transition-colors ${
              activeOverlays.includes(opt.id)
                ? "bg-secondary text-foreground"
                : "bg-secondary/50 text-muted-foreground hover:bg-secondary"
            }`}
          >
            <span className="mr-1 inline-block h-2 w-2 rounded-full" style={{ backgroundColor: opt.color }} />
            {opt.label}
          </button>
        ))}
      </div>

      {/* Chart */}
      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis dataKey="time" stroke="hsl(var(--muted-foreground))" fontSize={12} tickLine={false} />
            <YAxis
              domain={["dataMin - 0.001", "dataMax + 0.001"]}
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickLine={false}
              tickFormatter={(v) => v.toFixed(4)}
            />
            <Tooltip
              contentStyle={{
                background: "hsl(var(--card))",
                border: "1px solid hsl(var(--border))",
                borderRadius: "8px",
              }}
              labelStyle={{ color: "hsl(var(--muted-foreground))" }}
            />
            <Legend />

            {/* Bollinger Bands */}
            {activeOverlays.includes("bb") && (
              <>
                <Line type="monotone" dataKey="bb_upper" stroke="#8b5cf6" strokeWidth={1} dot={false} opacity={0.5} name="BB Upper" />
                <Line type="monotone" dataKey="bb_lower" stroke="#8b5cf6" strokeWidth={1} dot={false} opacity={0.5} name="BB Lower" />
              </>
            )}

            {/* SMA / EMA */}
            {activeOverlays.includes("sma20") && (
              <Line type="monotone" dataKey="sma20" stroke="#f59e0b" strokeWidth={1.5} dot={false} name="SMA 20" />
            )}
            {activeOverlays.includes("ema20") && (
              <Line type="monotone" dataKey="ema20" stroke="#3b82f6" strokeWidth={1.5} dot={false} name="EMA 20" />
            )}

            {/* Price Line */}
            <Line type="monotone" dataKey="price" stroke="hsl(var(--primary))" strokeWidth={2} dot={false} activeDot={{ r: 4 }} name="Price" />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
