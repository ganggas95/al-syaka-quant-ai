"use client";

interface FeatureBarProps {
  data: Record<string, { value: number; shap_impact: number; direction: string }>;
  title?: string;
}

/**
 * Horizontal bar chart untuk menampilkan SHAP feature importance.
 * Bar merah = negative impact (SELL), bar hijau = positive impact (BUY).
 */
export function FeatureBar({
  data,
  title = "Feature Importance (SHAP)",
}: FeatureBarProps) {
  const entries = Object.entries(data);

  if (entries.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md bg-secondary/30 text-sm text-muted-foreground">
        No SHAP data available
      </div>
    );
  }

  // Sort by absolute SHAP impact
  const sorted = entries.sort(
    ([, a], [, b]) => Math.abs(b.shap_impact) - Math.abs(a.shap_impact),
  );

  const maxAbs = Math.max(
    ...sorted.map(([, v]) => Math.abs(v.shap_impact)),
    0.01,
  );

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-medium">{title}</h3>
      <div className="space-y-2">
        {sorted.map(([key, feat]) => {
          const pct = (Math.abs(feat.shap_impact) / maxAbs) * 100;
          const isPositive = feat.direction === "positive";
          return (
            <div key={key} className="space-y-0.5">
              <div className="flex items-center justify-between text-xs">
                <span className="capitalize text-muted-foreground">
                  {key.replace(/_/g, " ")}
                </span>
                <span
                  className={`font-mono font-medium ${
                    isPositive ? "text-green-500" : "text-red-500"
                  }`}
                >
                  {isPositive ? "+" : ""}
                  {feat.shap_impact.toFixed(4)}
                </span>
              </div>
              <div className="relative h-2 w-full overflow-hidden rounded-full bg-secondary">
                <div
                  className={`absolute inset-y-0 rounded-full transition-all duration-500 ${
                    isPositive
                      ? "right-1/2 bg-green-500/70"
                      : "left-1/2 bg-red-500/70"
                  }`}
                  style={{
                    [isPositive ? "right" : "left"]: `${100 - pct}%`,
                    width: `${pct}%`,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
