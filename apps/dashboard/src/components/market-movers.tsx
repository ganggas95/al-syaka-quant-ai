"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface Mover {
  symbol: string;
  bid: number;
  change: number;
  volume: number;
}

export function MarketMovers({ tickers }: { tickers: Mover[] }) {
  if (!tickers || tickers.length === 0) return null;

  const sorted = [...tickers].sort((a, b) => Math.abs(b.change) - Math.abs(a.change));
  const top = sorted.slice(0, 6);

  return (
    <div className="rounded-lg border bg-card">
      <div className="border-b px-4 py-3">
        <h3 className="text-sm font-medium">Market Movers</h3>
      </div>
      <div className="divide-y">
        {top.map((t) => (
          <div key={t.symbol} className="flex items-center justify-between px-4 py-2.5 text-sm">
            <div className="flex items-center gap-2">
              <span className={`rounded-full p-1 ${
                t.change > 0 ? "bg-green-500/10 text-green-500" :
                t.change < 0 ? "bg-red-500/10 text-red-500" : "bg-secondary text-muted-foreground"
              }`}>
                {t.change > 0 ? <TrendingUp className="h-3 w-3" /> :
                 t.change < 0 ? <TrendingDown className="h-3 w-3" /> :
                 <Minus className="h-3 w-3" />}
              </span>
              <span className="font-medium">{t.symbol}</span>
            </div>
            <div className="text-right">
              <p className="font-mono">{t.bid.toFixed(5)}</p>
              <p className={`text-xs ${t.change > 0 ? "text-green-500" : "text-red-500"}`}>
                {t.change > 0 ? "+" : ""}{t.change}%
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
