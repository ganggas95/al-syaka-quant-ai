"use client";

import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart as RechartsRadar,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RadarScoreProps {
  data: Record<string, number>;
  title?: string;
}

/**
 * Radar Chart untuk menampilkan Composite Score breakdown.
 * 5 dimensions: Market Structure, Momentum, Trend, Volatility, AI Prediction.
 */
export function RadarScore({ data, title = "Composite Score" }: RadarScoreProps) {
  const chartData = Object.entries(data).map(([key, value]) => ({
    subject: key
      .replace(/_/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase()),
    value,
    fullMark: 100,
  }));

  if (chartData.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-md bg-secondary/30 text-sm text-muted-foreground">
        No composite data available
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-3 flex items-center gap-2 text-sm font-medium">
        <span className="text-primary">{title}</span>
      </h3>
      <ResponsiveContainer width="100%" height={260}>
        <RechartsRadar data={chartData} cx="50%" cy="50%" outerRadius="70%">
          <PolarGrid stroke="hsl(var(--border))" />
          <PolarAngleAxis
            dataKey="subject"
            tick={{ fontSize: 11, fill: "hsl(var(--muted-foreground))" }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "hsl(var(--card))",
              border: "1px solid hsl(var(--border))",
              borderRadius: "8px",
              fontSize: "13px",
            }}
            formatter={(val: number) => [`${val}%`, "Score"]}
          />
          <Radar
            name="Score"
            dataKey="value"
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.2}
          />
        </RechartsRadar>
      </ResponsiveContainer>
    </div>
  );
}
