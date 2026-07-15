"use client";

import { useEffect, useState } from "react";
import {
  TrendingUp,
  TrendingDown,
  BarChart3,
  Activity,
  DollarSign,
  AlertTriangle,
  BrainCircuit,
} from "lucide-react";
import { StatsCard } from "@/components/stats-card";
import { PriceChart } from "@/components/price-chart";
import { api, type MarketStructureResponse, type IndicatorsResponse } from "@/lib/api";

export default function DashboardPage() {
  const [healthStatus, setHealthStatus] = useState<string>("checking...");
  const [structure, setStructure] = useState<MarketStructureResponse | null>(null);
  const [indicators, setIndicators] = useState<IndicatorsResponse | null>(null);

  useEffect(() => {
    api.health()
      .then((data) => setHealthStatus(data.status))
      .catch(() => setHealthStatus("offline"));
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Market overview &amp; technical analysis
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-full bg-secondary px-4 py-2 text-sm">
          <span className={`h-2 w-2 rounded-full ${healthStatus === "ok" ? "bg-green-500" : "bg-red-500"}`} />
          API: {healthStatus}
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatsCard
          title="EUR/USD"
          value="1.0824"
          change="+0.15%"
          trend="up"
          icon={<TrendingUp className="h-4 w-4" />}
        />
        <StatsCard
          title="GBP/USD"
          value="1.2678"
          change="-0.08%"
          trend="down"
          icon={<TrendingDown className="h-4 w-4" />}
        />
        <StatsCard
          title="Active Signals"
          value="3"
          change="+1 today"
          trend="up"
          icon={<Activity className="h-4 w-4" />}
        />
        <StatsCard
          title="Market Trend"
          value={structure?.current_trend || "NEUTRAL"}
          change={structure ? "H4 Timeframe" : "Loading..."}
          trend={structure?.current_trend === "BULLISH" ? "up" : "down"}
          icon={<BrainCircuit className="h-4 w-4" />}
        />
      </div>

      {/* Main Content */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <PriceChart />
        </div>

        {/* Side Panel */}
        <div className="space-y-4">
          {/* Signals */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="mb-3 text-sm font-medium text-muted-foreground">
              RECENT SIGNALS
            </h3>
            <div className="space-y-3">
              {[
                { pair: "EURUSD", signal: "BUY", confidence: 84, reason: "Trend Bullish + Momentum" },
                { pair: "GBPUSD", signal: "SELL", confidence: 72, reason: "Resistance + RSI Overbought" },
                { pair: "USDJPY", signal: "BUY", confidence: 65, reason: "Support Bounce + FVG" },
              ].map((s, i) => (
                <div key={i} className="flex items-center justify-between rounded-md bg-secondary/50 p-3">
                  <div>
                    <p className="text-sm font-medium">{s.pair}</p>
                    <p className="text-xs text-muted-foreground">{s.reason}</p>
                  </div>
                  <div className="text-right">
                    <span className={`text-sm font-bold ${s.signal === "BUY" ? "text-green-500" : "text-red-500"}`}>
                      {s.signal}
                    </span>
                    <p className="text-xs text-muted-foreground">{s.confidence}%</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Market Structure Summary */}
          {structure && (
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium text-muted-foreground">
                MARKET STRUCTURE
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Trend</span>
                  <span className={`font-medium ${
                    structure.current_trend === "BULLISH" ? "text-green-500" : "text-red-500"
                  }`}>
                    {structure.current_trend}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Swing Highs</span>
                  <span>{structure.swing_highs.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Swing Lows</span>
                  <span>{structure.swing_lows.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Break of Structure</span>
                  <span>{structure.break_of_structure.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">FVG Detected</span>
                  <span>{structure.fair_value_gaps.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Liquidity Sweeps</span>
                  <span>{structure.liquidity_sweeps.length}</span>
                </div>
              </div>
            </div>
          )}

          {/* Economic Calendar */}
          <div className="rounded-lg border bg-card p-4">
            <h3 className="mb-3 text-sm font-medium text-muted-foreground">
              ECONOMIC CALENDAR
            </h3>
            <div className="space-y-2 text-sm">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3 w-3 text-yellow-500" />
                <span>Fed Interest Rate Decision</span>
                <span className="ml-auto text-muted-foreground">Today</span>
              </div>
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-3 w-3 text-orange-500" />
                <span>US Non-Farm Payrolls</span>
                <span className="ml-auto text-muted-foreground">Fri</span>
              </div>
              <div className="flex items-center gap-2">
                <BarChart3 className="h-3 w-3 text-blue-500" />
                <span>GDP QoQ</span>
                <span className="ml-auto text-muted-foreground">Next Week</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
