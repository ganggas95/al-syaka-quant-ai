"use client";

interface MonthlyHeatmapProps {
  data: Record<string, number>;
}

export function MonthlyHeatmap({ data }: MonthlyHeatmapProps) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex h-48 items-center justify-center text-sm text-muted-foreground">
        No monthly returns data available
      </div>
    );
  }

  const entries = Object.entries(data).sort(([a], [b]) => a.localeCompare(b));
  const allValues = entries.map(([, v]) => v);
  const maxAbs = Math.max(...allValues.map((v) => Math.abs(v)), 1);

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-medium">Monthly Returns</h3>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-4 md:grid-cols-6">
        {entries.map(([month, value]) => {
          const intensity = Math.abs(value) / maxAbs;
          const isPositive = value >= 0;
          const r = isPositive ? 0 : 255;
          const g = isPositive ? 255 : 0;
          const alpha = 0.15 + intensity * 0.6;

          return (
            <div
              key={month}
              className="rounded-md border p-2 text-center transition-colors hover:opacity-80"
              style={{
                backgroundColor: `rgba(${r}, ${g}, 0, ${alpha})`,
                borderColor: `rgba(${r}, ${g}, 0, ${alpha + 0.2})`,
              }}
            >
              <p className="text-[10px] font-medium text-muted-foreground">{month}</p>
              <p
                className="mt-0.5 text-xs font-bold"
                style={{ color: isPositive ? "rgb(34, 197, 94)" : "rgb(239, 68, 68)" }}
              >
                {isPositive ? "+" : ""}${value.toFixed(0)}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
