"use client";

import { ChevronLeft, ChevronRight, Clock } from "lucide-react";

interface HistoryEntry {
  signal_id: string;
  symbol: string;
  signal: string;
  confidence: number;
  timestamp: string;
}

interface SignalHistoryNavProps {
  entries: HistoryEntry[];
  currentId?: string;
  onSelect: (id: string) => void;
}

/**
 * Signal History Navigation — prev/next browsing.
 * Menampilkan daftar sinyal terbaru dengan navigasi.
 */
export function SignalHistoryNav({
  entries,
  currentId,
  onSelect,
}: SignalHistoryNavProps) {
  const currentIdx = entries.findIndex(
    (e) => e.signal_id === currentId,
  );

  const goPrev = () => {
    if (currentIdx > 0) onSelect(entries[currentIdx - 1].signal_id);
  };
  const goNext = () => {
    if (currentIdx < entries.length - 1)
      onSelect(entries[currentIdx + 1].signal_id);
  };

  if (entries.length === 0) return null;

  return (
    <div className="rounded-lg border bg-card p-3">
      <div className="mb-2 flex items-center gap-2 text-xs text-muted-foreground">
        <Clock className="h-3 w-3" />
        Signal History
        <span className="ml-auto">
          {currentIdx >= 0
            ? `${currentIdx + 1} / ${entries.length}`
            : `${entries.length} signals`}
        </span>
      </div>

      {/* Navigation buttons */}
      <div className="mb-2 flex gap-2">
        <button
          onClick={goPrev}
          disabled={currentIdx <= 0}
          className="flex items-center gap-1 rounded-md bg-secondary px-3 py-1.5 text-xs font-medium transition-colors hover:bg-secondary/80 disabled:opacity-40"
        >
          <ChevronLeft className="h-3 w-3" /> Prev
        </button>
        <button
          onClick={goNext}
          disabled={currentIdx < 0 || currentIdx >= entries.length - 1}
          className="flex items-center gap-1 rounded-md bg-secondary px-3 py-1.5 text-xs font-medium transition-colors hover:bg-secondary/80 disabled:opacity-40"
        >
          Next <ChevronRight className="h-3 w-3" />
        </button>
      </div>

      {/* Scrollable list */}
      <div className="max-h-32 space-y-1 overflow-y-auto">
        {entries.map((entry, idx) => {
          const isActive = entry.signal_id === currentId;
          return (
            <button
              key={entry.signal_id}
              onClick={() => onSelect(entry.signal_id)}
              className={`flex w-full items-center gap-2 rounded-md px-2.5 py-1.5 text-left text-xs transition-colors ${
                isActive
                  ? "bg-primary/10 font-medium text-primary"
                  : "text-muted-foreground hover:bg-secondary/50"
              }`}
            >
              <span
                className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                  entry.signal === "BUY"
                    ? "bg-green-500"
                    : entry.signal === "SELL"
                      ? "bg-red-500"
                      : "bg-yellow-500"
                }`}
              />
              <span className="font-medium">{entry.symbol}</span>
              <span className="ml-auto">{entry.confidence}%</span>
              {isActive && (
                <span className="text-[10px] text-muted-foreground">
                  now
                </span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}
