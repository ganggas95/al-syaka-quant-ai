"use client";

import {
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  Activity,
  Target,
  GanttChartSquare,
  Zap,
  AlertTriangle,
  Trophy,
  Ban,
} from "lucide-react";

interface PerfStatsProps {
  metrics: {
    win_rate: number;
    net_profit: number;
    profit_factor: number;
    sharpe_ratio: number;
    sortino_ratio: number;
    calmar_ratio: number;
    max_drawdown_percent: number;
    avg_profit_per_trade: number;
    avg_win: number;
    avg_loss: number;
    total_trades: number;
    max_consecutive_wins: number;
    max_consecutive_losses: number;
    best_trade: number;
    worst_trade: number;
    expectancy?: number;
    recovery_factor?: number;
  };
}

export function PerfStats({ metrics }: PerfStatsProps) {
  const expectancy = metrics.avg_win * (metrics.win_rate / 100) - metrics.avg_loss * (1 - metrics.win_rate / 100);

  const cards = [
    {
      title: "Win Rate",
      value: `${metrics.win_rate.toFixed(1)}%`,
      icon: Target,
      positive: metrics.win_rate >= 50,
      neutral: false,
    },
    {
      title: "Net Profit",
      value: `$${metrics.net_profit.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`,
      icon: DollarSign,
      positive: metrics.net_profit > 0,
      neutral: false,
    },
    {
      title: "Profit Factor",
      value: metrics.profit_factor === Infinity ? "∞" : metrics.profit_factor.toFixed(2),
      icon: BarChart3,
      positive: metrics.profit_factor >= 1.5,
      neutral: metrics.profit_factor === Infinity,
    },
    {
      title: "Expectancy",
      value: `$${expectancy.toFixed(2)}`,
      icon: GanttChartSquare,
      positive: expectancy > 0,
      neutral: false,
    },
    {
      title: "Sharpe Ratio",
      value: metrics.sharpe_ratio.toFixed(2),
      icon: Activity,
      positive: metrics.sharpe_ratio >= 1,
      neutral: false,
    },
    {
      title: "Sortino Ratio",
      value: metrics.sortino_ratio.toFixed(2),
      icon: Zap,
      positive: metrics.sortino_ratio >= 1,
      neutral: false,
    },
    {
      title: "Max Drawdown",
      value: `${metrics.max_drawdown_percent.toFixed(2)}%`,
      icon: TrendingDown,
      positive: metrics.max_drawdown_percent < 10,
      neutral: false,
    },
    {
      title: "Calmar Ratio",
      value: metrics.calmar_ratio.toFixed(2),
      icon: AlertTriangle,
      positive: metrics.calmar_ratio >= 1,
      neutral: false,
    },
    {
      title: "Avg Trade",
      value: `$${metrics.avg_profit_per_trade.toFixed(2)}`,
      icon: TrendingUp,
      positive: metrics.avg_profit_per_trade > 0,
      neutral: false,
    },
    {
      title: "Best / Worst",
      value: `$${metrics.best_trade.toFixed(0)} / $${Math.abs(metrics.worst_trade).toFixed(0)}`,
      icon: Trophy,
      positive: metrics.best_trade > Math.abs(metrics.worst_trade),
      neutral: false,
    },
    {
      title: "Consecutive W/L",
      value: `${metrics.max_consecutive_wins} / ${metrics.max_consecutive_losses}`,
      icon: Activity,
      positive: metrics.max_consecutive_wins > metrics.max_consecutive_losses * 2,
      neutral: false,
    },
    {
      title: "Total Trades",
      value: metrics.total_trades.toString(),
      icon: Ban,
      positive: metrics.total_trades >= 30,
      neutral: false,
    },
  ];

  return (
    <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;
        return (
          <div
            key={card.title}
            className="rounded-lg border bg-card p-3 transition-colors hover:bg-secondary/20"
          >
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">{card.title}</p>
              <div
                className={`rounded-md p-1.5 ${
                  card.neutral
                    ? "bg-muted text-muted-foreground"
                    : card.positive
                      ? "bg-green-500/10 text-green-500"
                      : "bg-red-500/10 text-red-500"
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
              </div>
            </div>
            <p className="mt-1.5 text-lg font-bold">{card.value}</p>
          </div>
        );
      })}
    </div>
  );
}
