"use client";

interface IndicatorStatusProps {
  indicators: string[];
}

/**
 * Indicator status badges yang dikelompokkan berdasarkan kategori.
 * Visual: colored chips dengan icon status.
 */
export function IndicatorStatus({ indicators }: IndicatorStatusProps) {
  const categories: Record<string, { regex: RegExp; color: string }> = {
    Trend: { regex: /^(EMA|SMA|MA|ICHIMOKU|VWAP)/i, color: "bg-blue-500/10 text-blue-500 border-blue-500/20" },
    Momentum: { regex: /^(RSI|MACD|STOCH|CCI|WILLIAMS)/i, color: "bg-purple-500/10 text-purple-500 border-purple-500/20" },
    Volatility: { regex: /^(ATR|BOLLINGER|BB|KC)/i, color: "bg-orange-500/10 text-orange-500 border-orange-500/20" },
    Structure: { regex: /^(SUPPORT|RESISTANCE|SWING|FVG|LIQUIDITY|BOS|CHOCH)/i, color: "bg-cyan-500/10 text-cyan-500 border-cyan-500/20" },
    Volume: { regex: /^VOLUME/i, color: "bg-green-500/10 text-green-500 border-green-500/20" },
  };

  if (!indicators || indicators.length === 0) {
    return (
      <div className="rounded-lg border bg-card p-4">
        <h3 className="text-sm font-medium">Indicators</h3>
        <p className="mt-2 text-xs text-muted-foreground">None used</p>
      </div>
    );
  }

  const grouped: Record<string, string[]> = {};
  for (const ind of indicators) {
    let found = false;
    for (const [cat, def] of Object.entries(categories)) {
      if (def.regex.test(ind)) {
        if (!grouped[cat]) grouped[cat] = [];
        grouped[cat].push(ind);
        found = true;
        break;
      }
    }
    if (!found) {
      if (!grouped["Other"]) grouped["Other"] = [];
      grouped["Other"].push(ind);
    }
  }

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-medium">Indicators</h3>
      <div className="space-y-2">
        {Object.entries(grouped).map(([category, items]) => {
          const catDef = categories[category];
          const chipColor = catDef?.color ?? "bg-secondary text-muted-foreground border-border";
          return (
            <div key={category}>
              <p className="mb-1 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
                {category}
              </p>
              <div className="flex flex-wrap gap-1.5">
                {items.map((ind) => (
                  <span
                    key={ind}
                    className={`rounded-md border px-2 py-0.5 text-xs font-medium ${chipColor}`}
                  >
                    {ind}
                  </span>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
