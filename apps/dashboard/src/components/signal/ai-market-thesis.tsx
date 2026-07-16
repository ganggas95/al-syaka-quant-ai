"use client";

import { BrainCircuit, TrendingUp, TrendingDown, Minus } from "lucide-react";

interface AiMarketThesisProps {
  /** Array of reasons from the signal engine */
  reasons?: string[];
  /** Human-readable explanation */
  explanationReason?: string;
  /** Market regime detected */
  marketRegime?: string;
  /** Reason for the regime classification */
  regimeReason?: string;
  /** Macro bias */
  macroBias?: string;
  /** Macro explanation */
  macroReason?: string;
}

function getSignalIcon(signal?: string) {
  switch (signal) {
    case "BULLISH":
    case "BUY":
      return <TrendingUp className="h-5 w-5 text-green-500" />;
    case "BEARISH":
    case "SELL":
      return <TrendingDown className="h-5 w-5 text-red-500" />;
    default:
      return <Minus className="h-5 w-5 text-amber-500" />;
  }
}

function getSignalColor(signal?: string) {
  switch (signal) {
    case "BULLISH":
    case "BUY":
      return "text-green-500 border-green-500/20 bg-green-500/10";
    case "BEARISH":
    case "SELL":
      return "text-red-500 border-red-500/20 bg-red-500/10";
    default:
      return "text-amber-500 border-amber-500/20 bg-amber-500/10";
  }
}

export function AiMarketThesis({
  reasons,
  explanationReason,
  marketRegime,
  regimeReason,
  macroBias,
  macroReason,
}: AiMarketThesisProps) {
  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex items-center gap-2">
        <BrainCircuit className="h-5 w-5 text-purple-500" />
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          AI Market Thesis
        </h3>
      </div>

      {/* Explanation */}
      {explanationReason && (
        <p className="mb-4 text-sm leading-relaxed text-foreground/90">
          {explanationReason}
        </p>
      )}

      {/* Regime + Macro tags */}
      <div className="mb-4 flex flex-wrap gap-2">
        {marketRegime && (
          <span
            className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase ${getSignalColor(marketRegime)}`}
          >
            {marketRegime}
          </span>
        )}
        {macroBias && (
          <span
            className={`rounded-full border px-3 py-1 text-[10px] font-bold uppercase ${getSignalColor(macroBias)}`}
          >
            Macro: {macroBias}
          </span>
        )}
      </div>

      {/* Regime reason */}
      {regimeReason && (
        <div className="mb-3 flex items-start gap-2">
          {getSignalIcon(marketRegime)}
          <p className="text-xs text-muted-foreground">{regimeReason}</p>
        </div>
      )}

      {/* Macro reason */}
      {macroReason && (
        <div className="mb-3 flex items-start gap-2">
          {getSignalIcon(macroBias)}
          <p className="text-xs text-muted-foreground">{macroReason}</p>
        </div>
      )}

      {/* Reasons list */}
      {reasons && reasons.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Key Reasons
          </h4>
          <ul className="space-y-1.5">
            {reasons.map((reason, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-muted-foreground">
                <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-primary" />
                {reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
