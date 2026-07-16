"use client";

import {
  TrendingUp,
  TrendingDown,
  Minus,
  Clock,
} from "lucide-react";
import { SignalHistoryEntry } from "@/lib/api";

interface SignalHistoryProps {
  entries: SignalHistoryEntry[];
  currentId?: string;
  onSelect: (id: string) => void;
}

function getSignalColor(signal: string) {
  switch (signal) {
    case "BUY":
    case "BULLISH":
      return "text-green-500";
    case "SELL":
    case "BEARISH":
      return "text-red-500";
    default:
      return "text-amber-500";
  }
}

function SignalBadge({ signal }: { signal: string }) {
  const Icon = signal === "BUY" || signal === "BULLISH"
    ? TrendingUp
    : signal === "SELL" || signal === "BEARISH"
    ? TrendingDown
    : Minus;

  return (
    <span className={`inline-flex items-center gap-1 text-xs font-bold ${getSignalColor(signal)}`}>
      <Icon className="h-3 w-3" />
      {signal}
    </span>
  );
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

export function SignalHistory({
  entries,
  currentId,
  onSelect,
}: SignalHistoryProps) {
  if (entries.length === 0) {
    return (
      <div className="rounded-xl border bg-card p-5">
        <div className="mb-3 flex items-center gap-2">
          <Clock className="h-5 w-5 text-muted-foreground" />
          <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
            Signal History
          </h3>
        </div>
        <p className="text-xs text-muted-foreground">No signal history yet.</p>
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-3 flex items-center gap-2">
        <Clock className="h-5 w-5 text-muted-foreground" />
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Signal History
        </h3>
        <span className="ml-auto text-[10px] text-muted-foreground">
          {entries.length} signals
        </span>
      </div>

      <div className="max-h-80 space-y-1 overflow-y-auto">
        {entries.map((entry) => {
          const isActive = entry.signal_id === currentId;
          return (
            <button
              key={entry.signal_id}
              onClick={() => onSelect(entry.signal_id)}
              className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-left text-xs transition-colors hover:bg-secondary/50 ${
                isActive ? "bg-secondary/80 ring-1 ring-primary/20" : ""
              }`}
            >
              <SignalBadge signal={entry.signal} />
              <span className="font-mono font-medium text-foreground">
                {entry.confidence.toFixed(0)}%
              </span>
              <span className="text-muted-foreground">{entry.symbol}</span>
              {entry.timeframe && (
                <span className="rounded bg-secondary/50 px-1.5 py-0.5 text-[9px] font-bold text-muted-foreground">
                  {entry.timeframe}
                </span>
              )}
              <span className="ml-auto text-muted-foreground">
                {formatTimestamp(entry.timestamp)}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
