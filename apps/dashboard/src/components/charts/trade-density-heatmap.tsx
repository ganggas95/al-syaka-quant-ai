"use client";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

interface TradePlot {
  entry_time: string;
  signal: string;
  result: string;
}

interface TradeDensityHeatmapProps {
  trades: TradePlot[];
}

interface MonthData {
  month: string;
  key: string;
  total: number;
  buys: number;
  sells: number;
  wins: number;
  losses: number;
  intensity: number;
}

function CustomTooltip({
  active,
  payload,
}: {
  active?: boolean;
  payload?: { payload: MonthData }[];
}) {
  if (!active || !payload || !payload[0]) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-lg border border-border/60 bg-card/95 px-3 py-2 text-xs shadow-xl backdrop-blur-sm">
      <p className="mb-1 font-semibold text-foreground">{d.month}</p>
      <div className="space-y-0.5 text-muted-foreground">
        <p>
          Total: <span className="font-medium text-foreground">{d.total}</span>
        </p>
        <p>
          BUY: <span className="font-medium text-green-400">{d.buys}</span> ·
          SELL: <span className="font-medium text-red-400">{d.sells}</span>
        </p>
        <p>
          WIN: <span className="font-medium text-green-400">{d.wins}</span> ·
          LOSS: <span className="font-medium text-red-400">{d.losses}</span>
        </p>
        <p>
          Win rate:{" "}
          <span className="font-medium text-foreground">
            {d.total > 0 ? ((d.wins / d.total) * 100).toFixed(1) : "0"}%
          </span>
        </p>
      </div>
    </div>
  );
}

export function TradeDensityHeatmap({ trades }: TradeDensityHeatmapProps) {
  if (!trades || trades.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-lg border bg-card text-sm text-muted-foreground">
        No trade data available
      </div>
    );
  }

  // Aggregate trades by month
  const buckets = new Map<string, MonthData>();
  trades.forEach((t) => {
    const d = new Date(t.entry_time);
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
    const month = d.toLocaleDateString("en-US", {
      month: "short",
      year: "numeric",
    });

    let b = buckets.get(key);
    if (!b) {
      b = {
        month,
        key,
        total: 0,
        buys: 0,
        sells: 0,
        wins: 0,
        losses: 0,
        intensity: 0,
      };
      buckets.set(key, b);
    }
    b.total++;
    if (t.signal === "BUY" || t.signal === "BULLISH") b.buys++;
    else b.sells++;
    if (t.result === "WIN") b.wins++;
    else if (t.result === "LOSS") b.losses++;
  });

  const months = Array.from(buckets.values()).sort((a, b) =>
    a.key.localeCompare(b.key),
  );
  const maxCount = Math.max(...months.map((m) => m.total), 1);
  months.forEach((m) => {
    m.intensity = m.total / maxCount;
  });

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-1 text-sm font-medium">Trade Density Heatmap</h3>
      <p className="mb-3 text-[10px] text-muted-foreground">
        Trade distribution per month — bar height shows trade count, color
        intensity shows density
      </p>

      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={months} barSize={32}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
            <XAxis
              dataKey="month"
              tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
              axisLine={{ stroke: "hsl(var(--border))" }}
              tickLine={false}
            />
            <YAxis
              tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
              axisLine={{ stroke: "hsl(var(--border))" }}
              tickLine={false}
              allowDecimals={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={false} />
            <Bar
              dataKey="total"
              radius={[4, 4, 0, 0]}
              isAnimationActive={true}
              animationDuration={600}
            >
              {months.map((entry) => (
                <Cell
                  key={entry.key}
                  fill={`rgba(139, 92, 246, ${0.15 + entry.intensity * 0.7})`}
                  stroke={`rgba(139, 92, 246, ${0.3 + entry.intensity * 0.5})`}
                  strokeWidth={1}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
