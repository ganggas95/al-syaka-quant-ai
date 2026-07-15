"use client";

interface SessionData {
  trades: number;
  wins: number;
  losses: number;
  win_rate: number;
  net_profit: number;
  avg_trade: number;
}

interface SessionBreakdownProps {
  data: {
    asia: SessionData;
    london: SessionData;
    newyork: SessionData;
  };
}

/**
 * Session breakdown cards — performa per session trading.
 */
export function SessionBreakdown({ data }: SessionBreakdownProps) {
  const sessions = [
    {
      key: "asia",
      label: "Asia",
      icon: "🌙",
      time: "00:00 – 07:00 UTC",
      ...data.asia,
    },
    {
      key: "london",
      label: "London",
      icon: "🇬🇧",
      time: "07:00 – 12:00 UTC",
      ...data.london,
    },
    {
      key: "newyork",
      label: "New York",
      icon: "🇺🇸",
      time: "12:00 – 20:00 UTC",
      ...data.newyork,
    },
  ];

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-4 text-sm font-medium">Session Breakdown</h3>
      <div className="grid gap-4 md:grid-cols-3">
        {sessions.map((s) => {
          const hasTrades = s.trades > 0;
          return (
            <div
              key={s.key}
              className={`rounded-lg border p-4 ${
                s.key === "asia"
                  ? "border-yellow-500/20 bg-yellow-500/5"
                  : s.key === "london"
                    ? "border-blue-500/20 bg-blue-500/5"
                    : "border-green-500/20 bg-green-500/5"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-lg">{s.icon}</span>
                {hasTrades && (
                  <span
                    className={`text-xs font-bold ${
                      s.net_profit > 0 ? "text-green-500" : "text-red-500"
                    }`}
                  >
                    {s.net_profit > 0 ? "+" : ""}${s.net_profit.toFixed(0)}
                  </span>
                )}
              </div>
              <p className="mt-1 text-sm font-bold">{s.label}</p>
              <p className="text-[10px] text-muted-foreground">{s.time}</p>

              {hasTrades ? (
                <div className="mt-3 space-y-1 text-xs">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Trades</span>
                    <span className="font-medium">{s.trades}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Win Rate</span>
                    <span className="font-medium text-green-500">{s.win_rate}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Avg Trade</span>
                    <span className="font-medium">${s.avg_trade.toFixed(2)}</span>
                  </div>
                  <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-secondary">
                    <div
                      className="h-full rounded-full bg-green-500"
                      style={{ width: `${s.win_rate}%` }}
                    />
                  </div>
                </div>
              ) : (
                <p className="mt-3 text-[10px] text-muted-foreground italic">
                  No trades in this session
                </p>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
