"use client";

interface TimelineEntry {
  id: number;
  signal: string;
  confidence: number;
  entry_price: number | null;
  stop_loss: number | null;
  take_profit: number | null;
  outcome_result: string | null;
  created_at: string | null;
}

interface TradeTimelineProps {
  signals: TimelineEntry[];
  onSelect?: (id: number) => void;
  selectedId?: number;
}

/**
 * Horizontal timeline chart showing historical signal entries.
 * Color-coded markers per signal type with confidence indicator.
 */
export function TradeTimeline({
  signals,
  onSelect,
  selectedId,
}: TradeTimelineProps) {
  if (signals.length === 0) {
    return (
      <div className="flex h-48 items-center justify-center rounded-md bg-secondary/30 text-sm text-muted-foreground">
        No signal history available. Generate signals to build history.
      </div>
    );
  }

  const sorted = [...signals].sort((a, b) => {
    const ta = a.created_at ? new Date(a.created_at).getTime() : 0;
    const tb = b.created_at ? new Date(b.created_at).getTime() : 0;
    return tb - ta; // newest first
  });

  const styleBySignal = (s: string) => {
    switch (s) {
      case "BUY":
        return {
          dot: "bg-green-500 border-green-500",
          text: "text-green-500",
          bg: "bg-green-500/10",
        };
      case "SELL":
        return {
          dot: "bg-red-500 border-red-500",
          text: "text-red-500",
          bg: "bg-red-500/10",
        };
      case "HEDGE":
        return {
          dot: "bg-purple-500 border-purple-500",
          text: "text-purple-500",
          bg: "bg-purple-500/10",
        };
      default:
        return {
          dot: "bg-yellow-500 border-yellow-500",
          text: "text-yellow-500",
          bg: "bg-yellow-500/10",
        };
    }
  };

  const fmtDate = (iso: string | null) => {
    if (!iso) return "Unknown";
    try {
      const d = new Date(iso);
      return d.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return "Invalid";
    }
  };

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-4 text-sm font-medium">Trade Timeline</h3>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[7px] top-2 h-[calc(100%-16px)] w-0.5 bg-secondary" />

        <div className="space-y-3">
          {sorted.map((entry) => {
            const isSelected = entry.id === selectedId;
            const s = styleBySignal(entry.signal);

            return (
              <button
                key={entry.id}
                onClick={() => onSelect?.(entry.id)}
                className={`relative flex w-full items-start gap-3 rounded-lg p-3 text-left text-xs transition-colors ${
                  isSelected
                    ? `${s.bg} ring-1 ring-inset ring-secondary`
                    : "hover:bg-secondary/50"
                }`}
              >
                {/* Dot */}
                <div
                  className={`relative z-10 mt-1 h-3.5 w-3.5 shrink-0 rounded-full border-2 ${s.dot} ${
                    isSelected ? "ring-2 ring-background" : ""
                  }`}
                />

                {/* Content */}
                <div className="min-w-0 flex-1 text-left">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`font-semibold ${s.text}`}>
                      {entry.signal}
                    </span>
                    <span className="shrink-0 text-muted-foreground">
                      {fmtDate(entry.created_at)}
                    </span>
                  </div>
                  <div className="mt-0.5 flex flex-wrap gap-x-3 text-muted-foreground">
                    <span>Conf: {entry.confidence}%</span>
                    {entry.entry_price && (
                      <span>Entry: {entry.entry_price.toFixed(2)}</span>
                    )}
                    {entry.outcome_result && (
                      <span
                        className={
                          entry.outcome_result === "WIN"
                            ? "text-green-500"
                            : entry.outcome_result === "LOSS"
                              ? "text-red-500"
                              : "text-yellow-500"
                        }
                      >
                        {entry.outcome_result}
                      </span>
                    )}
                  </div>
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
