"use client";

import { SignalHistoryEntry } from "@/lib/api";

interface SignalTimelineProps {
  entries: SignalHistoryEntry[];
  currentId?: string;
  onSelect: (id: string) => void;
}

function getDotColor(signal: string): string {
  switch (signal) {
    case "BUY":
    case "BULLISH":
      return "bg-green-500 ring-green-500/20";
    case "SELL":
    case "BEARISH":
      return "bg-red-500 ring-red-500/20";
    default:
      return "bg-amber-500 ring-amber-500/20";
  }
}

function getLineColor(signal: string): string {
  switch (signal) {
    case "BUY":
    case "BULLISH":
      return "bg-green-500/20";
    case "SELL":
    case "BEARISH":
      return "bg-red-500/20";
    default:
      return "bg-amber-500/20";
  }
}

function formatTimestamp(ts: string) {
  try {
    const d = new Date(ts);
    return d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return ts;
  }
}

export function SignalTimeline({
  entries,
  currentId,
  onSelect,
}: SignalTimelineProps) {
  if (entries.length === 0) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <h3 className="mb-2 text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Signal Timeline
        </h3>
        <p className="text-xs text-muted-foreground">No signals to display.</p>
      </div>
    );
  }

  // Show most recent first, limit to 10
  const timelineEntries = entries.slice(0, 10);

  return (
    <div className="rounded-xl border bg-card p-5">
      <h3 className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wider">
        Signal Timeline
      </h3>

      <div className="relative space-y-0">
        {timelineEntries.map((entry, i) => {
          const isActive = entry.signal_id === currentId;
          const isLast = i === timelineEntries.length - 1;

          return (
            <button
              key={entry.signal_id}
              onClick={() => onSelect(entry.signal_id)}
              className={`relative flex w-full items-start gap-4 pb-6 text-left transition-opacity hover:opacity-80 ${
                isActive ? "opacity-100" : "opacity-60"
              }`}
            >
              {/* Vertical line */}
              {!isLast && (
                <div
                  className={`absolute left-[7px] top-3 h-full w-0.5 ${getLineColor(entry.signal)}`}
                />
              )}

              {/* Dot */}
              <div
                className={`relative z-10 mt-1 h-4 w-4 shrink-0 rounded-full ring-4 ${getDotColor(
                  entry.signal
                )} ${isActive ? "scale-125" : ""}`}
              />

              {/* Content */}
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span
                    className={`text-xs font-bold ${
                      entry.signal === "BUY" || entry.signal === "BULLISH"
                        ? "text-green-500"
                        : entry.signal === "SELL" || entry.signal === "BEARISH"
                        ? "text-red-500"
                        : "text-amber-500"
                    }`}
                  >
                    {entry.signal}
                  </span>
                  <span className="font-mono text-xs font-medium text-foreground">
                    {entry.confidence.toFixed(0)}%
                  </span>
                  {entry.timeframe && (
                    <span className="rounded bg-secondary/50 px-1.5 py-0.5 text-[9px] font-bold text-muted-foreground">
                      {entry.timeframe}
                    </span>
                  )}
                </div>
                <span className="text-[10px] text-muted-foreground">
                  {entry.symbol} &middot; {formatTimestamp(entry.timestamp)}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
