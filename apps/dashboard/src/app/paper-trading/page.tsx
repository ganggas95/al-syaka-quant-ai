"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Plus,
  X,
  RotateCcw,
  TrendingUp,
  TrendingDown,
  DollarSign,
  BarChart3,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  BookOpen,
  RefreshCw,
  List,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface AccountInfo {
  account_name: string;
  initial_balance: number;
  current_balance: number;
  total_return_pct: number;
  current_drawdown_pct: number;
  daily_pnl: number;
  open_pnl: number;
  realized_pnl: number;
  consecutive_wins: number;
  consecutive_losses: number;
}

interface Position {
  id: string;
  symbol: string;
  direction: string;
  entry: number;
  current: number;
  sl: number;
  tp: number;
  lot: number;
  profit: number | null;
  status: string;
}

export default function PaperTradingPage() {
  const [tab, setTab] = useState<"positions" | "journal" | "analytics">("positions");
  const [accountInfo, setAccountInfo] = useState<AccountInfo | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [journal, setJournal] = useState<any[]>([]);
  const [analytics, setAnalytics] = useState<any>(null);
  const [showNewTrade, setShowNewTrade] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const [accRes, posRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/paper-trading/account`),
        fetch(`${API_URL}/api/v1/paper-trading/positions?include_closed=true`),
      ]);
      setAccountInfo(await accRes.json());
      const posData = await posRes.json();
      setPositions(posData.positions || []);
    } catch {}
  }, []);

  const fetchJournal = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/api/v1/paper-trading/journal?limit=30`);
      setJournal((await res.json()).entries || []);
    } catch {}
  }, []);

  const fetchAnalytics = useCallback(async () => {
    try {
      const [anRes, sigRes] = await Promise.all([
        fetch(`${API_URL}/api/v1/paper-trading/analytics`),
        fetch(`${API_URL}/api/v1/paper-trading/signal-performance`),
      ]);
      setAnalytics({ ...(await anRes.json()), signal_performance: await sigRes.json() });
    } catch {}
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Paper Trading</h1>
          <p className="text-muted-foreground">Virtual trading simulation</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => { fetchData(); fetchJournal(); fetchAnalytics(); }}
            className="flex items-center gap-1 rounded-md bg-secondary px-3 py-2 text-sm hover:bg-secondary/80">
            <RefreshCw className="h-3 w-3" /> Refresh
          </button>
          <button onClick={() => setShowNewTrade(true)}
            className="flex items-center gap-1 rounded-md bg-primary px-3 py-2 text-sm text-primary-foreground">
            <Plus className="h-3 w-3" /> New Trade
          </button>
        </div>
      </div>

      {/* Account Summary */}
      {accountInfo && (
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-lg border bg-card p-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Balance</p>
              <DollarSign className="h-4 w-4 text-muted-foreground" />
            </div>
            <p className="mt-1 text-2xl font-bold">${accountInfo.current_balance.toLocaleString()}</p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Return</p>
            <p className={`mt-1 text-2xl font-bold ${accountInfo.total_return_pct >= 0 ? "text-green-500" : "text-red-500"}`}>
              {accountInfo.total_return_pct >= 0 ? "+" : ""}{accountInfo.total_return_pct}%
            </p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Open P&L</p>
            <p className={`mt-1 text-2xl font-bold ${accountInfo.open_pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
              ${accountInfo.open_pnl.toFixed(2)}
            </p>
          </div>
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">Daily P&L</p>
            <p className={`mt-1 text-2xl font-bold ${accountInfo.daily_pnl >= 0 ? "text-green-500" : "text-red-500"}`}>
              ${accountInfo.daily_pnl.toFixed(2)}
            </p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-secondary p-1">
        {[
          { id: "positions", label: "Positions", icon: List },
          { id: "journal", label: "Journal", icon: BookOpen },
          { id: "analytics", label: "Analytics", icon: BarChart3 },
        ].map((t) => {
          const Icon = t.icon;
          return (
            <button key={t.id} onClick={() => { setTab(t.id as any); if (t.id === "journal") fetchJournal(); if (t.id === "analytics") fetchAnalytics(); }}
              className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
                tab === t.id ? "bg-background text-foreground shadow" : "text-muted-foreground hover:text-foreground"
              }`}>
              <Icon className="h-4 w-4" /> {t.label}
            </button>
          );
        })}
      </div>

      {/* Positions Tab */}
      {tab === "positions" && (
        <div className="rounded-lg border bg-card">
          <div className="border-b px-4 py-3 text-sm font-medium">Open & Recent Positions</div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="px-4 py-2 text-left">ID</th>
                  <th className="px-4 py-2 text-left">Symbol</th>
                  <th className="px-4 py-2 text-left">Dir</th>
                  <th className="px-4 py-2 text-right">Entry</th>
                  <th className="px-4 py-2 text-right">Current</th>
                  <th className="px-4 py-2 text-right">SL</th>
                  <th className="px-4 py-2 text-right">TP</th>
                  <th className="px-4 py-2 text-right">Lot</th>
                  <th className="px-4 py-2 text-right">Profit</th>
                  <th className="px-4 py-2 text-center">Status</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((p) => (
                  <tr key={p.id} className="border-b last:border-0 hover:bg-secondary/30">
                    <td className="px-4 py-2 font-mono text-xs">{p.id}</td>
                    <td className="px-4 py-2 font-medium">{p.symbol}</td>
                    <td className="px-4 py-2">
                      <span className={p.direction === "LONG" ? "text-green-500" : "text-red-500"}>
                        {p.direction === "LONG" ? "▲" : "▼"}
                      </span>
                    </td>
                    <td className="px-4 py-2 text-right font-mono">{p.entry.toFixed(5)}</td>
                    <td className="px-4 py-2 text-right font-mono">{p.current?.toFixed(5) || "-"}</td>
                    <td className="px-4 py-2 text-right font-mono text-red-500">{p.sl.toFixed(5)}</td>
                    <td className="px-4 py-2 text-right font-mono text-green-500">{p.tp.toFixed(5)}</td>
                    <td className="px-4 py-2 text-right">{p.lot}</td>
                    <td className={`px-4 py-2 text-right font-mono ${p.profit !== null ? (p.profit >= 0 ? "text-green-500" : "text-red-500") : ""}`}>
                      {p.profit !== null ? `$${p.profit.toFixed(2)}` : "-"}
                    </td>
                    <td className="px-4 py-2 text-center">
                      <span className={`rounded-full px-2 py-0.5 text-xs ${
                        p.status === "OPEN" ? "bg-blue-500/10 text-blue-500" :
                        p.profit && p.profit > 0 ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
                      }`}>{p.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Journal Tab */}
      {tab === "journal" && (
        <div className="rounded-lg border bg-card">
          <div className="border-b px-4 py-3 text-sm font-medium">Trade Journal</div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="px-4 py-2 text-left">Time</th>
                  <th className="px-4 py-2 text-left">Symbol</th>
                  <th className="px-4 py-2 text-left">Signal</th>
                  <th className="px-4 py-2 text-right">Entry</th>
                  <th className="px-4 py-2 text-right">Exit</th>
                  <th className="px-4 py-2 text-right">Profit</th>
                  <th className="px-4 py-2 text-center">Result</th>
                  <th className="px-4 py-2 text-left">Reasons</th>
                  <th className="px-4 py-2 text-left">Tags</th>
                </tr>
              </thead>
              <tbody>
                {journal.map((e: any) => (
                  <tr key={e.id} className="border-b last:border-0 hover:bg-secondary/30">
                    <td className="px-4 py-2 text-xs text-muted-foreground">
                      {e.entry_time ? new Date(e.entry_time).toLocaleDateString() : "-"}
                    </td>
                    <td className="px-4 py-2 font-medium">{e.symbol}</td>
                    <td className="px-4 py-2">
                      <span className={e.signal === "BUY" ? "text-green-500" : "text-red-500"}>{e.signal}</span>
                    </td>
                    <td className="px-4 py-2 text-right font-mono">{e.entry_price?.toFixed(5)}</td>
                    <td className="px-4 py-2 text-right font-mono">{e.exit_price?.toFixed(5) || "-"}</td>
                    <td className={`px-4 py-2 text-right font-mono ${e.profit >= 0 ? "text-green-500" : "text-red-500"}`}>
                      ${e.profit.toFixed(2)}
                    </td>
                    <td className="px-4 py-2 text-center">
                      {e.result === "WIN" ? <CheckCircle2 className="mx-auto h-4 w-4 text-green-500" /> :
                       e.result === "LOSS" ? <XCircle className="mx-auto h-4 w-4 text-red-500" /> : "-"}
                    </td>
                    <td className="px-4 py-2 text-xs text-muted-foreground max-w-[200px] truncate">
                      {e.reasons?.join("; ") || "-"}
                    </td>
                    <td className="px-4 py-2">
                      <div className="flex flex-wrap gap-1">
                        {e.tags?.map((t: string, i: number) => (
                          <span key={i} className="rounded bg-secondary px-1.5 py-0.5 text-[10px]">{t}</span>
                        ))}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Analytics Tab */}
      {tab === "analytics" && analytics && (
        <div className="space-y-4">
          {/* Overall Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <StatBox label="Total Trades" value={analytics.overall?.total_trades || 0} />
            <StatBox label="Win Rate" value={`${analytics.overall?.win_rate || 0}%`} positive={(analytics.overall?.win_rate || 0) >= 50} />
            <StatBox label="Profit Factor" value={analytics.overall?.profit_factor || 0} positive={(analytics.overall?.profit_factor || 0) >= 1.5} />
            <StatBox label="Net Profit" value={`$${analytics.overall?.net_profit || 0}`} positive={(analytics.overall?.net_profit || 0) > 0} />
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            {/* Win Rate by Pair */}
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Win Rate by Pair</h3>
              {analytics.by_pair && Object.entries(analytics.by_pair).map(([pair, data]: [string, any]) => (
                <div key={pair} className="mb-2 flex items-center justify-between text-sm">
                  <span>{pair}</span>
                  <div className="text-right">
                    <span className={data.win_rate >= 50 ? "text-green-500" : "text-red-500"}>{data.win_rate}%</span>
                    <span className="ml-2 text-xs text-muted-foreground">({data.total})</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Win Rate by Session */}
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Win Rate by Session</h3>
              {analytics.by_session && Object.entries(analytics.by_session).map(([session, data]: [string, any]) => (
                <div key={session} className="mb-2 flex items-center justify-between text-sm">
                  <span className="capitalize">{session}</span>
                  <div className="text-right">
                    <span className={data.win_rate >= 50 ? "text-green-500" : "text-red-500"}>{data.win_rate}%</span>
                    <span className="ml-2 text-xs text-muted-foreground">({data.total})</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Signal Performance */}
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Signal Performance</h3>
              {analytics.signal_performance?.confusion_matrix && (
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Accuracy</span>
                    <span>{analytics.signal_performance.confusion_matrix.accuracy}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Precision</span>
                    <span>{analytics.signal_performance.confusion_matrix.precision}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">F1 Score</span>
                    <span>{analytics.signal_performance.confusion_matrix.f1_score}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Total Signals</span>
                    <span>{analytics.signal_performance.confusion_matrix.total_signals}</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Drawdown */}
          {analytics.drawdown && (
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Drawdown Analysis</h3>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Max Drawdown</span>
                  <p className="text-lg font-bold text-red-500">{analytics.drawdown.max_drawdown}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Avg Drawdown</span>
                  <p className="text-lg font-bold">{analytics.drawdown.avg_drawdown}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Current</span>
                  <p className="text-lg font-bold">{analytics.drawdown.current_drawdown}%</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* New Trade Modal */}
      {showNewTrade && (
        <NewTradeForm onClose={() => setShowNewTrade(false)} onSuccess={() => { setShowNewTrade(false); fetchData(); }} />
      )}
    </div>
  );
}

function StatBox({ label, value, positive }: { label: string; value: any; positive?: boolean }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <p className="text-sm text-muted-foreground">{label}</p>
      <p className={`mt-1 text-xl font-bold ${positive !== undefined ? (positive ? "text-green-500" : "text-red-500") : ""}`}>{value}</p>
    </div>
  );
}

function NewTradeForm({ onClose, onSuccess }: { onClose: () => void; onSuccess: () => void }) {
  const [symbol, setSymbol] = useState("EURUSD");
  const [direction, setDirection] = useState("LONG");
  const [entry, setEntry] = useState("1.0800");
  const [sl, setSl] = useState("1.0780");
  const [tp, setTp] = useState("1.0840");
  const [lot, setLot] = useState("0.1");
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    setLoading(true);
    try {
      await fetch(
        `${API_URL}/api/v1/paper-trading/positions/open` +
        `?symbol=${symbol}&direction=${direction}&entry_price=${entry}` +
        `&stop_loss=${sl}&take_profit=${tp}&lot_size=${lot}&signal=${direction === "LONG" ? "BUY" : "SELL"}`,
        { method: "POST" }
      );
      onSuccess();
    } catch {} finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg border bg-card p-6 shadow-lg">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">New Trade</h2>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground"><X className="h-4 w-4" /></button>
        </div>
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Symbol</label>
              <select value={symbol} onChange={e => setSymbol(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm">
                {["EURUSD", "XAUUSD", "GBPUSD", "USDJPY", "AUDUSD"].map(s => <option key={s} value={s}>{s}</option>)}
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Direction</label>
              <div className="flex gap-2">
                <button onClick={() => setDirection("LONG")}
                  className={`flex-1 rounded-md px-3 py-2 text-sm font-medium ${direction === "LONG" ? "bg-green-500/20 text-green-500" : "bg-secondary"}`}>
                  ▲ LONG
                </button>
                <button onClick={() => setDirection("SHORT")}
                  className={`flex-1 rounded-md px-3 py-2 text-sm font-medium ${direction === "SHORT" ? "bg-red-500/20 text-red-500" : "bg-secondary"}`}>
                  ▼ SHORT
                </button>
              </div>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="mb-1 block text-xs text-muted-foreground">Entry</label>
              <input value={entry} onChange={e => setEntry(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm font-mono" />
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground text-red-500">SL</label>
              <input value={sl} onChange={e => setSl(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm font-mono" />
            </div>
            <div>
              <label className="mb-1 block text-xs text-muted-foreground text-green-500">TP</label>
              <input value={tp} onChange={e => setTp(e.target.value)}
                className="w-full rounded-md border bg-background px-3 py-2 text-sm font-mono" />
            </div>
          </div>
          <div>
            <label className="mb-1 block text-xs text-muted-foreground">Lot Size</label>
            <input value={lot} onChange={e => setLot(e.target.value)}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
          <button onClick={submit} disabled={loading}
            className="w-full rounded-md bg-primary py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50">
            {loading ? "Opening..." : "Open Position"}
          </button>
        </div>
      </div>
    </div>
  );
}
