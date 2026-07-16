"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Cell,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from "recharts";

interface BreakdownCategory {
  count: number;
  percentage: number;
}

interface SignalBreakdownData {
  total_signal_checks: number;
  total_signals_taken: number;
  breakdown: Record<string, BreakdownCategory>;
  raw_counts: Record<string, number>;
}

interface SignalBreakdownProps {
  data: SignalBreakdownData;
}

const CATEGORY_COLORS: Record<string, string> = {
  "Sideways Market": "hsl(220, 70%, 50%)",
  "Low Confidence": "hsl(35, 90%, 50%)",
  "News Hour": "hsl(0, 70%, 50%)",
  "Asia Session": "hsl(50, 80%, 50%)",
  Others: "hsl(220, 10%, 50%)",
};
const FALLBACK_COLORS = [
  "hsl(180, 70%, 50%)",
  "hsl(280, 60%, 60%)",
  "hsl(120, 60%, 45%)",
  "hsl(300, 50%, 50%)",
];

/**
 * Signal Breakdown — Bar chart + Spider chart showing why signals were rejected.
 */
export function SignalBreakdown({ data }: SignalBreakdownProps) {
  const entries = Object.entries(data.breakdown).sort(
    (a, b) => b[1].percentage - a[1].percentage,
  );
  const totalRejected =
    data.total_signal_checks - data.total_signals_taken;

  if (entries.length === 0) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <h3 className="mb-3 text-sm font-medium">Signal Loss Breakdown</h3>
        <p className="text-xs text-muted-foreground">
          No rejection data available
        </p>
      </div>
    );
  }

  // Data for Radar chart
  const radarData = entries.map(([key, val]) => ({
    subject: key,
    value: val.percentage,
    fullMark: 100,
  }));

  // Data for Bar chart
  const barData = entries.map(([key, val]) => ({
    name: key,
    percentage: val.percentage,
    count: val.count,
    fill: CATEGORY_COLORS[key] || FALLBACK_COLORS[entries.indexOf(entries.find(e => e[0] === key)!) % FALLBACK_COLORS.length],
  }));

  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium">Signal Loss Breakdown</h3>
          <p className="text-[10px] text-muted-foreground">
            {data.total_signal_checks.toLocaleString()} signal checks ·{" "}
            {totalRejected.toLocaleString()} rejected ·{" "}
            {data.total_signals_taken} trades taken
          </p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* ── Bar Chart ── */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={barData}
              layout="vertical"
              margin={{ top: 5, right: 30, bottom: 5, left: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                className="stroke-border"
                horizontal={false}
              />
              <XAxis
                type="number"
                domain={[0, 100]}
                tick={{ fontSize: 10 }}
                tickFormatter={(v: number) => `${v}%`}
                className="text-muted-foreground"
              />
              <YAxis
                type="category"
                dataKey="name"
                tick={{ fontSize: 11 }}
                width={110}
                className="text-muted-foreground"
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                formatter={(val: number, _name: string, props: any) => [
                  `${val}% (${props.payload.count} signals)`,
                  props.payload.name,
                ]}
              />
              <Bar dataKey="percentage" radius={[0, 4, 4, 0]} maxBarSize={20}>
                {barData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* ── Radar / Spider Chart ── */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData} cx="50%" cy="50%" outerRadius="70%">
              <PolarGrid stroke="hsl(var(--border))" />
              <PolarAngleAxis
                dataKey="subject"
                tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
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
                  borderRadius: "6px",
                  fontSize: "12px",
                }}
                formatter={(val: number, _name: string, props: any) => [
                  `${val}%`,
                  props.payload.subject,
                ]}
              />
              <Radar
                name="Rejection Rate"
                dataKey="value"
                stroke="hsl(var(--primary))"
                fill="hsl(var(--primary))"
                fillOpacity={0.2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Summary Cards ── */}
      <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-4">
        {entries.map(([key, val]) => (
          <div
            key={key}
            className="rounded-md border p-2.5 text-center"
            style={{
              borderColor: `${CATEGORY_COLORS[key] || FALLBACK_COLORS[entries.indexOf(entries.find(e => e[0] === key)!)]}40`,
            }}
          >
            <p className="text-lg font-bold" style={{ color: CATEGORY_COLORS[key] || FALLBACK_COLORS[entries.indexOf(entries.find(e => e[0] === key)!)] }}>
              {val.percentage}%
            </p>
            <p className="text-[10px] leading-tight text-muted-foreground">
              {key}
            </p>
            <p className="mt-0.5 text-[10px] text-muted-foreground/60">
              {val.count} signals
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
