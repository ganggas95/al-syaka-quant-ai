"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface ConsensusMultitfProps {
  h1Signal?: string;
  h4Signal?: string;
  d1Signal?: string;
}

function getSignalColor(signal?: string) {
  switch (signal) {
    case "BUY":
    case "BULLISH":
      return { text: "text-green-500", bg: "bg-green-500/10", border: "border-green-500/30" };
    case "SELL":
    case "BEARISH":
      return { text: "text-red-500", bg: "bg-red-500/10", border: "border-red-500/30" };
    default:
      return { text: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/30" };
  }
}

function SignalIcon({ signal }: { signal?: string }) {
  switch (signal) {
    case "BUY":
    case "BULLISH":
      return <TrendingUp className="h-4 w-4" />;
    case "SELL":
    case "BEARISH":
      return <TrendingDown className="h-4 w-4" />;
    default:
      return <Minus className="h-4 w-4" />;
  }
}

export function ConsensusMultitf({
  h1Signal,
  h4Signal,
  d1Signal,
}: ConsensusMultitfProps) {
  const timeframes = [
    { label: "H1", signal: h1Signal },
    { label: "H4", signal: h4Signal },
    { label: "D1", signal: d1Signal },
  ];

  const allSame = h1Signal && h4Signal && d1Signal && h1Signal === h4Signal && h4Signal === d1Signal;

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Consensus Multi-Timeframe
        </h3>
        {allSame && (
          <span className="rounded-full bg-green-500/10 px-2.5 py-0.5 text-[10px] font-bold text-green-500">
            ALIGNED
          </span>
        )}
      </div>

      <div className="grid grid-cols-3 gap-3">
        {timeframes.map((tf) => {
          const colors = getSignalColor(tf.signal);
          const displaySignal = tf.signal || "NEUTRAL";
          return (
            <div
              key={tf.label}
              className={`flex flex-col items-center gap-2 rounded-lg border p-4 ${colors.bg} ${colors.border}`}
            >
              <span className="text-[10px] font-bold uppercase text-muted-foreground">
                {tf.label}
              </span>
              <SignalIcon signal={tf.signal} />
              <span className={`text-sm font-bold ${colors.text}`}>
                {displaySignal}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
