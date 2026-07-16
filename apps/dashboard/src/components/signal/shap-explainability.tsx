"use client";

import { BrainCircuit } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

interface ShapExplainabilityProps {
  /** Feature contributions from SHAP (key = feature name, value = contribution) */
  featureContributions?: Record<string, number>;
  /** SHAP summary text */
  shapSummary?: string;
  /** SHAP reasons list */
  shapReasons?: string[];
}

export function ShapExplainability({
  featureContributions,
  shapSummary,
  shapReasons,
}: ShapExplainabilityProps) {
  // Convert contributions to sorted chart data
  const chartData = featureContributions
    ? Object.entries(featureContributions)
        .map(([name, value]) => ({ name, value: Math.round(value * 100) / 100 }))
        .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
        .slice(0, 10) // Top 10 features
    : [];

  const hasData = chartData.length > 0 || shapSummary || (shapReasons && shapReasons.length > 0);

  if (!hasData) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-3 flex items-center gap-2">
          <BrainCircuit className="h-5 w-5 text-purple-500" />
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            AI Explainability (SHAP)
          </h3>
        </div>
        <p className="text-xs text-muted-foreground">
          Enable AI + SHAP in the features panel to see model explainability.
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex items-center gap-2">
        <BrainCircuit className="h-5 w-5 text-purple-500" />
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          AI Explainability (SHAP)
        </h3>
      </div>

      {/* Summary */}
      {shapSummary && (
        <p className="mb-4 text-xs leading-relaxed text-muted-foreground">
          {shapSummary}
        </p>
      )}

      {/* Feature contributions chart */}
      {chartData.length > 0 && (
        <div className="mb-4 h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              layout="vertical"
              margin={{ top: 5, right: 30, left: 60, bottom: 5 }}
            >
              <CartesianGrid
                strokeDasharray="3 3"
                horizontal={false}
                stroke="rgba(255,255,255,0.05)"
              />
              <XAxis
                type="number"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <YAxis
                type="category"
                dataKey="name"
                fontSize={9}
                tickLine={false}
                axisLine={false}
                width={55}
                tick={{ fill: "hsl(var(--muted-foreground))" }}
              />
              <Tooltip
                contentStyle={{
                  background: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                  fontSize: "12px",
                }}
                formatter={(value: number) => [value.toFixed(3), "Contribution"]}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={20}>
                {chartData.map((entry, index) => (
                  <Cell
                    key={index}
                    fill={entry.value >= 0 ? "#22c55e" : "#ef4444"}
                    fillOpacity={Math.min(Math.abs(entry.value) / Math.max(...chartData.map(d => Math.abs(d.value))), 1)}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* SHAP reasons */}
      {shapReasons && shapReasons.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            SHAP Insights
          </h4>
          <ul className="space-y-1.5">
            {shapReasons.map((reason, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-purple-500" />
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
