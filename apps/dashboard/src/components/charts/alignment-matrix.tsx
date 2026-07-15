"use client";

interface AlignmentMatrixProps {
  data: Record<string, string>; // e.g. { H1: "BUY", H4: "SELL", D1: "SELL" }
}

/**
 * Heatmap-style matrix untuk menampilkan Multi Timeframe Alignment.
 * Setiap cell menunjukkan signal (BUY/SELL/NEUTRAL) per timeframe.
 * Warna cell menyesuaikan signal.
 */
export function AlignmentMatrix({ data }: AlignmentMatrixProps) {
  const entries = Object.entries(data);

  if (entries.length === 0) {
    return (
      <div className="flex h-32 items-center justify-center rounded-md bg-secondary/30 text-sm text-muted-foreground">
        No timeframe data
      </div>
    );
  }

  const signalColor = (signal: string) => {
    switch (signal) {
      case "BUY":
        return "bg-green-500/15 text-green-500 border-green-500/30";
      case "SELL":
        return "bg-red-500/15 text-red-500 border-red-500/30";
      default:
        return "bg-secondary text-muted-foreground border-border";
    }
  };

  // Calculate alignment percentage
  const signals = entries.map(([, s]) => s);
  const nonNeutral = signals.filter((s) => s !== "NEUTRAL");
  const aligned = nonNeutral.filter((s) => s === nonNeutral[0]);
  const alignmentPct =
    nonNeutral.length > 0
      ? Math.round((aligned.length / entries.length) * 100)
      : 0;

  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-sm font-medium">Multi Timeframe</h3>
        <span className="rounded-full bg-secondary px-2.5 py-0.5 text-xs font-medium">
          {alignmentPct}% Aligned
        </span>
      </div>
      <div className="grid grid-cols-3 gap-2">
        {entries.map(([tf, signal]) => (
          <div
            key={tf}
            className={`flex flex-col items-center gap-1 rounded-lg border p-3 ${signalColor(signal)}`}
          >
            <span className="text-xs font-medium text-muted-foreground">
              {tf}
            </span>
            <span className="text-sm font-bold">{signal}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
