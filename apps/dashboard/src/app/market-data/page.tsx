"use client";

import { useState, useEffect, useCallback } from "react";
import {
  RefreshCw, Download, Table2, BarChart3, Activity, AlertTriangle,
  TrendingUp, TrendingDown, Minus, LayoutGrid, Globe, CalendarDays,
} from "lucide-react";
import { CandleChart } from "@/components/candle-chart";
import { SymbolPicker } from "@/components/symbol-picker";
import { OHLCTable } from "@/components/ohlc-table";
import { MarketMovers } from "@/components/market-movers";
import { EconCalendar } from "@/components/econ-calendar";
import { ExportButton } from "@/components/export-button";
import { MiniChart } from "@/components/mini-chart";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TIMEFRAMES = ["M5", "M15", "M30", "H1", "H4", "D1"] as const;
type Timeframe = (typeof TIMEFRAMES)[number];
type Section = "chart" | "overview" | "watchlist" | "calendar";

const WATCHLIST_SYMBOLS = ["EURUSD", "XAUUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "BTCUSD"];

interface OHLCData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface TickerItem {
  symbol: string;
  bid: number;
  change: number;
  high: number;
  low: number;
  volume: number;
}

export default function MarketDataPage() {
  const [symbol, setSymbol] = useState("EURUSD");
  const [timeframe, setTimeframe] = useState<Timeframe>("H1");
  const [limit, setLimit] = useState(100);
  const [data, setData] = useState<OHLCData[]>([]);
  const [tickers, setTickers] = useState<TickerItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [view, setView] = useState<"chart" | "table">("chart");
  const [section, setSection] = useState<Section>("chart");
  const [indicatorLines, setIndicatorLines] = useState<any[]>([]);
  const [showSMA, setShowSMA] = useState(false);
  const [showEMA, setShowEMA] = useState(false);
  const [showSession, setShowSession] = useState(false);
  const [watchlistData, setWatchlistData] = useState<Record<string, OHLCData[]>>({});
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string>("");

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(
        `${API_URL}/api/v1/market/ohlc/${symbol}?timeframe=${timeframe}&limit=${limit}`
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json.data || []);
      setLastUpdate(new Date().toLocaleTimeString());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [symbol, timeframe, limit]);

  const fetchTickers = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/market/ticker`);
      const json = await res.json();
      setTickers(json.tickers || []);
    } catch {}
  }, []);

  const fetchIndicators = useCallback(async () => {
    if (!showSMA && !showEMA && !showSession) {
      setIndicatorLines([]);
      return;
    }
    try {
      const res = await fetch(
        `${API_URL}/api/v1/indicators/${symbol}?timeframe=${timeframe}&limit=${limit}`
      );
      if (!res.ok) return;
      const json = await res.json();
      const ind = json.indicators || {};
      const timestamps = json.timestamps || [];
      const lines: any[] = [];
      if (showSMA && ind.sma_20) {
        lines.push({ label: "SMA 20", color: "#f59e0b",
          data: timestamps.map((t: string, i: number) => ({ time: t, value: ind.sma_20[i] || 0 })) });
      }
      if (showEMA && ind.ema_20) {
        lines.push({ label: "EMA 20", color: "#3b82f6",
          data: timestamps.map((t: string, i: number) => ({ time: t, value: ind.ema_20[i] || 0 })) });
      }
      setIndicatorLines(lines);
    } catch {}
  }, [symbol, timeframe, limit, showSMA, showEMA, showSession]);

  const fetchWatchlist = useCallback(async () => {
    const results: Record<string, OHLCData[]> = {};
    await Promise.all(
      WATCHLIST_SYMBOLS.map(async (sym) => {
        try {
          const res = await fetch(`${API_URL}/api/v1/market/ohlc/${sym}?timeframe=H1&limit=30`);
          const json = await res.json();
          results[sym] = json.data || [];
        } catch {}
      })
    );
    setWatchlistData(results);
  }, []);

  // Initial fetch
  useEffect(() => { fetchData(); }, [fetchData]);
  useEffect(() => { fetchTickers(); }, [fetchTickers]);
  useEffect(() => { fetchIndicators(); }, [fetchIndicators]);
  useEffect(() => { if (section === "watchlist") fetchWatchlist(); }, [section, fetchWatchlist]);

  // Auto-refresh: polling setiap 30 detik
  useEffect(() => {
    if (!autoRefresh) return;
    const interval = setInterval(() => {
      fetchData();
      fetchTickers();
      if (showSMA || showEMA) fetchIndicators();
    }, 30_000);
    return () => clearInterval(interval);
  }, [autoRefresh, fetchData, fetchTickers, fetchIndicators, showSMA, showEMA]);

  const latest = data[data.length - 1];
  const prev = data[data.length - 2];
  const change = latest && prev
    ? ((latest.close - prev.close) / prev.close * 100).toFixed(2) : "0.00";
  const isUp = latest && prev ? latest.close >= prev.close : true;

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Market Data</h1>
          <p className="text-muted-foreground">
            Real-time quotes <span className="text-xs">(auto-refresh every 30s)</span>
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`flex items-center gap-1.5 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              autoRefresh
                ? "bg-green-500/20 text-green-500 hover:bg-green-500/30"
                : "bg-secondary text-muted-foreground hover:text-foreground"
            }`}
          >
            <span className={`h-2 w-2 rounded-full ${autoRefresh ? "bg-green-500 animate-pulse" : "bg-gray-500"}`} />
            {autoRefresh ? "LIVE" : "Auto Refresh"}
          </button>
          <ExportButton symbol={symbol} timeframe={timeframe} data={data} />
          <button onClick={() => { fetchData(); fetchTickers(); }}
            className="flex items-center gap-1 rounded-md bg-secondary px-3 py-2 text-sm hover:bg-secondary/80">
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} /> Refresh
          </button>
        </div>
      </div>

      {/* Last Update Indicator */}
      {lastUpdate && (
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className={`h-1.5 w-1.5 rounded-full ${autoRefresh ? "bg-green-500 animate-pulse" : "bg-gray-500"}`} />
          Last updated: {lastUpdate}
          {autoRefresh && <span className="text-green-500">• Auto-refreshing every 30s</span>}
        </div>
      )}

      {/* Ticker Bar */}
      {tickers.length > 0 && (
        <div className="flex gap-3 overflow-x-auto rounded-lg border bg-card p-3">
          {tickers.slice(0, 8).map((t) => (
            <div key={t.symbol} className="flex shrink-0 items-center gap-2 text-sm">
              <span className="font-medium">{t.symbol}</span>
              <span className="font-mono">{t.bid.toFixed(5)}</span>
              <span className={`flex items-center text-xs ${
                t.change > 0 ? "text-green-500" : t.change < 0 ? "text-red-500" : "text-muted-foreground"
              }`}>
                {t.change > 0 ? <TrendingUp className="h-3 w-3" /> :
                 t.change < 0 ? <TrendingDown className="h-3 w-3" /> : <Minus className="h-3 w-3" />}
                {t.change > 0 ? "+" : ""}{t.change}%
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Section Tabs */}
      <div className="flex gap-1 rounded-lg bg-secondary p-1">
        {[
          { id: "chart" as Section, label: "Chart", icon: BarChart3 },
          { id: "overview" as Section, label: "Overview", icon: Globe },
          { id: "watchlist" as Section, label: "Watchlist", icon: LayoutGrid },
          { id: "calendar" as Section, label: "Calendar", icon: CalendarDays },
        ].map((s) => {
          const Icon = s.icon;
          return (
            <button key={s.id} onClick={() => setSection(s.id)}
              className={`flex items-center gap-1.5 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                section === s.id ? "bg-background text-foreground shadow" : "text-muted-foreground hover:text-foreground"
              }`}>
              <Icon className="h-4 w-4" /> {s.label}
            </button>
          );
        })}
      </div>

      {/* ==================== CHART SECTION ==================== */}
      {section === "chart" && (
        <>
          <div className="flex flex-wrap items-end gap-3 rounded-lg border bg-card p-4">
            <div className="w-40">
              <label className="mb-1 block text-xs text-muted-foreground">Symbol</label>
              <SymbolPicker value={symbol} onChange={setSymbol} />
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Timeframe</label>
              <div className="flex gap-1">
                {TIMEFRAMES.map((tf) => (
                  <button key={tf} onClick={() => setTimeframe(tf)}
                    className={`rounded-md px-3 py-2 text-xs font-medium transition-colors ${
                      timeframe === tf ? "bg-primary text-primary-foreground" : "bg-secondary text-muted-foreground hover:text-foreground"
                    }`}>{tf}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Limit</label>
              <select value={limit} onChange={(e) => setLimit(Number(e.target.value))}
                className="rounded-md border bg-background px-3 py-2 text-sm">
                {[50, 100, 200, 500].map((n) => (<option key={n} value={n}>{n}</option>))}
              </select>
            </div>
          </div>

          {latest && (
            <div className="grid gap-3 md:grid-cols-6">
              <PriceStat label="Open" value={latest.open.toFixed(5)} />
              <PriceStat label="High" value={latest.high.toFixed(5)} color="text-green-500" />
              <PriceStat label="Low" value={latest.low.toFixed(5)} color="text-red-500" />
              <PriceStat label="Close" value={latest.close.toFixed(5)} bold color={isUp ? "text-green-500" : "text-red-500"} />
              <PriceStat label="Change" value={`${isUp ? "+" : ""}${change}%`} color={isUp ? "text-green-500" : "text-red-500"} />
              <PriceStat label="Range" value={`${(latest.high - latest.low).toFixed(5)}`} />
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="flex gap-1 rounded-lg bg-secondary p-1">
              <button onClick={() => setView("chart")}
                className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-xs ${view === "chart" ? "bg-background shadow" : "text-muted-foreground"}`}>
                <BarChart3 className="h-3.5 w-3.5" /> Candlestick
              </button>
              <button onClick={() => setView("table")}
                className={`flex items-center gap-1 rounded-md px-3 py-1.5 text-xs ${view === "table" ? "bg-background shadow" : "text-muted-foreground"}`}>
                <Table2 className="h-3.5 w-3.5" /> Table
              </button>
            </div>
            <div className="flex flex-wrap gap-3">
              <label className="flex items-center gap-1.5 text-xs">
                <input type="checkbox" checked={showSMA} onChange={(e) => setShowSMA(e.target.checked)} className="rounded" />
                <span className="h-2 w-2 rounded-full bg-amber-500" /> SMA 20
              </label>
              <label className="flex items-center gap-1.5 text-xs">
                <input type="checkbox" checked={showEMA} onChange={(e) => setShowEMA(e.target.checked)} className="rounded" />
                <span className="h-2 w-2 rounded-full bg-blue-500" /> EMA 20
              </label>
              <label className="flex items-center gap-1.5 text-xs">
                <input type="checkbox" checked={showSession} onChange={(e) => setShowSession(e.target.checked)} className="rounded" />
                <Globe className="h-3 w-3 text-muted-foreground" /> Sessions
              </label>
            </div>
          </div>

          {error && (
            <div className="flex items-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-500">
              <AlertTriangle className="h-4 w-4" /> {error}
            </div>
          )}

          {view === "chart" && (
            <div className="rounded-lg border bg-card p-4">
              {loading ? (
                <div className="flex h-[450px] items-center justify-center text-muted-foreground">
                  <Activity className="mr-2 h-4 w-4 animate-pulse" /> Loading...
                </div>
              ) : data.length > 0 ? (
                <CandleChart
                  data={data.map(d => ({ time: d.timestamp, open: d.open, high: d.high, low: d.low, close: d.close, volume: d.volume }))}
                  indicators={indicatorLines}
                  height={450}
                />
              ) : (
                <div className="flex h-[450px] items-center justify-center text-muted-foreground">No data available</div>
              )}
            </div>
          )}

          {view === "table" && (
            <div className="rounded-lg border bg-card">
              {data.length > 0 ? <OHLCTable data={data} /> : (
                <div className="flex h-40 items-center justify-center text-muted-foreground">No data available</div>
              )}
            </div>
          )}
        </>
      )}

      {/* ==================== OVERVIEW SECTION ==================== */}
      {section === "overview" && (
        <div className="grid gap-4 lg:grid-cols-3">
          <div className="lg:col-span-2 space-y-4">
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Market Overview</h3>
              <div className="grid gap-3 md:grid-cols-2">
                {tickers.slice(0, 8).map((t) => {
                  const isUp = t.change >= 0;
                  return (
                    <button key={t.symbol} onClick={() => { setSymbol(t.symbol); setSection("chart"); }}
                      className="flex items-center justify-between rounded-md bg-secondary/30 p-3 text-left hover:bg-secondary/50 transition-colors">
                      <div>
                        <p className="text-sm font-medium">{t.symbol}</p>
                        <p className="font-mono text-lg">{t.bid.toFixed(5)}</p>
                      </div>
                      <div className="text-right">
                        <p className={`font-bold ${isUp ? "text-green-500" : "text-red-500"}`}>
                          {isUp ? "+" : ""}{t.change}%
                        </p>
                        <p className="text-xs text-muted-foreground">Vol: {t.volume?.toLocaleString() || "-"}</p>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Today&apos;s Range</h3>
              <div className="space-y-2">
                {tickers.slice(0, 6).map((t) => {
                  const range = t.high - t.low;
                  return (
                    <div key={t.symbol} className="flex items-center gap-3 text-sm">
                      <span className="w-16 font-medium">{t.symbol}</span>
                      <div className="flex-1">
                        <div className="relative h-2 rounded-full bg-secondary">
                          <div className="absolute h-full rounded-full bg-primary/50"
                            style={{ left: `${(t.low / (t.low + range)) * 100}%`, right: `${100 - ((t.high / (t.low + range)) * 100)}%` }} />
                        </div>
                      </div>
                      <span className="w-20 text-right font-mono text-xs text-muted-foreground">
                        {t.low.toFixed(4)} - {t.high.toFixed(4)}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <MarketMovers tickers={tickers} />
            <EconCalendar />
          </div>
        </div>
      )}

      {/* ==================== WATCHLIST SECTION ==================== */}
      {section === "watchlist" && (
        <div>
          <div className="mb-3 flex items-center justify-between">
            <h2 className="text-lg font-semibold">Watchlist</h2>
            <button onClick={fetchWatchlist}
              className="flex items-center gap-1 rounded-md bg-secondary px-3 py-1.5 text-xs hover:bg-secondary/80">
              <RefreshCw className="h-3 w-3" /> Refresh
            </button>
          </div>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {WATCHLIST_SYMBOLS.map((sym) => {
              const symData = watchlistData[sym] || [];
              const last = symData[symData.length - 1];
              const ticker = tickers.find((t) => t.symbol === sym);
              return (
                <button key={sym} onClick={() => { setSymbol(sym); setSection("chart"); }}
                  className="rounded-lg border bg-card p-3 text-left hover:bg-secondary/30 transition-colors">
                  <div className="mb-2 flex items-center justify-between">
                    <span className="font-medium">{sym}</span>
                    {ticker && (
                      <span className={`text-sm font-mono ${ticker.change >= 0 ? "text-green-500" : "text-red-500"}`}>
                        {ticker.change >= 0 ? "+" : ""}{ticker.change}%
                      </span>
                    )}
                  </div>
                  {last && (
                    <p className="mb-1 font-mono text-lg">{last.close.toFixed(5)}</p>
                  )}
                  {symData.length > 0 && (
                    <MiniChart symbol={sym} data={symData.map(d => ({
                      time: d.timestamp, open: d.open, high: d.high, low: d.low, close: d.close,
                    }))} height={60} />
                  )}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* ==================== CALENDAR SECTION ==================== */}
      {section === "calendar" && (
        <div className="grid gap-4 lg:grid-cols-2">
          <EconCalendar />
          <div className="rounded-lg border bg-card p-4">
            <h3 className="mb-3 text-sm font-medium">This Week&apos;s Key Events</h3>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-3 rounded-md bg-red-500/5 p-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-500/10">
                  <AlertTriangle className="h-5 w-5 text-red-500" />
                </div>
                <div>
                  <p className="font-medium">Fed Interest Rate Decision</p>
                  <p className="text-xs text-muted-foreground">Today 14:30 • High Impact • USD</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-md bg-orange-500/5 p-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-orange-500/10">
                  <AlertTriangle className="h-5 w-5 text-orange-500" />
                </div>
                <div>
                  <p className="font-medium">US Non-Farm Payrolls</p>
                  <p className="text-xs text-muted-foreground">Friday 08:30 • High Impact • USD</p>
                </div>
              </div>
              <div className="flex items-center gap-3 rounded-md bg-blue-500/5 p-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-500/10">
                  <BarChart3 className="h-5 w-5 text-blue-500" />
                </div>
                <div>
                  <p className="font-medium">German Industrial Production</p>
                  <p className="text-xs text-muted-foreground">Tuesday 09:00 • Medium Impact • EUR</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function PriceStat({ label, value, color, bold }: { label: string; value: string; color?: string; bold?: boolean }) {
  return (
    <div className="rounded-lg border bg-card p-3">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`font-mono text-lg ${bold ? "font-bold" : ""} ${color || ""}`}>{value}</p>
    </div>
  );
}
