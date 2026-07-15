"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Radio,
  Activity,
  DollarSign,
  AlertTriangle,
  Shield,
  Zap,
  Power,
  PowerOff,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  XCircle,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function MT5Page() {
  const [tab, setTab] = useState<"account" | "trading" | "safety">("account");
  const [account, setAccount] = useState<any>(null);
  const [positions, setPositions] = useState<any>(null);
  const [safety, setSafety] = useState<any>(null);
  const [autoStatus, setAutoStatus] = useState<any>(null);
  const [signals, setSignals] = useState<any[]>([]);

  const fetchAll = useCallback(async () => {
    const fetches = [
      fetch(`${API_URL}/api/v1/mt5/account`).then(r => r.json()).then(setAccount).catch(() => {}),
      fetch(`${API_URL}/api/v1/mt5/positions`).then(r => r.json()).then(setPositions).catch(() => {}),
      fetch(`${API_URL}/api/v1/mt5/safety`).then(r => r.json()).then(setSafety).catch(() => {}),
      fetch(`${API_URL}/api/v1/mt5/auto/status`).then(r => r.json()).then(setAutoStatus).catch(() => {}),
      fetch(`${API_URL}/api/v1/mt5/executed-signals`).then(r => r.json()).then(d => setSignals(d.signals || [])).catch(() => {}),
    ];
    await Promise.all(fetches);
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  const toggleKillSwitch = async () => {
    const engage = !safety?.kill_switch;
    await fetch(`${API_URL}/api/v1/mt5/safety/kill-switch?engage=${engage}`, { method: "POST" });
    fetchAll();
  };

  const toggleAutoTrade = async () => {
    if (autoStatus?.enabled) {
      await fetch(`${API_URL}/api/v1/mt5/auto/stop`, { method: "POST" });
    } else {
      await fetch(`${API_URL}/api/v1/mt5/auto/start`, { method: "POST" });
    }
    fetchAll();
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">MT5 Bridge</h1>
          <p className="text-muted-foreground">MetaTrader 5 — connection, auto trading & safety</p>
        </div>
        <div className="flex gap-2">
          <button onClick={toggleAutoTrade}
            className={`flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium ${
              autoStatus?.enabled
                ? "bg-red-500/20 text-red-500 hover:bg-red-500/30"
                : "bg-green-500/20 text-green-500 hover:bg-green-500/30"
            }`}>
            {autoStatus?.enabled ? <PowerOff className="h-3 w-3" /> : <Power className="h-3 w-3" />}
            {autoStatus?.enabled ? "Stop Auto" : "Start Auto"}
          </button>
          <button onClick={toggleKillSwitch}
            className={`flex items-center gap-1 rounded-md px-3 py-2 text-sm font-medium ${
              safety?.kill_switch ? "bg-red-500 text-white" : "bg-secondary hover:bg-secondary/80"
            }`}>
            <Shield className="h-3 w-3" />
            {safety?.kill_switch ? "Kill Switch ON" : "Kill Switch OFF"}
          </button>
          <button onClick={fetchAll}
            className="flex items-center gap-1 rounded-md bg-secondary px-3 py-2 text-sm hover:bg-secondary/80">
            <RefreshCw className="h-3 w-3" /> Refresh
          </button>
        </div>
      </div>

      {/* Status Bar */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatusCard
          title="Connection"
          value={account?.connected ? "Connected" : "Disconnected"}
          icon={<Radio className="h-4 w-4" />}
          ok={account?.connected}
        />
        <StatusCard
          title="Auto Trading"
          value={autoStatus?.enabled ? "Active" : "Inactive"}
          icon={<Zap className="h-4 w-4" />}
          ok={autoStatus?.enabled}
        />
        <StatusCard
          title="Safety"
          value={safety?.can_trade ? "OK" : "Blocked"}
          icon={<Shield className="h-4 w-4" />}
          ok={safety?.can_trade}
        />
        <StatusCard
          title="Open Positions"
          value={positions?.count || 0}
          icon={<Activity className="h-4 w-4" />}
          ok={(positions?.count || 0) > 0}
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 rounded-lg bg-secondary p-1">
        {[
          { id: "account", label: "Account" },
          { id: "trading", label: "Trading" },
          { id: "safety", label: "Safety" },
        ].map((t) => (
          <button key={t.id} onClick={() => setTab(t.id as any)}
            className={`flex-1 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
              tab === t.id ? "bg-background text-foreground shadow" : "text-muted-foreground hover:text-foreground"
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Account Tab */}
      {tab === "account" && account && (
        <div className="rounded-lg border bg-card p-6">
          <h2 className="mb-4 text-lg font-semibold">Account Info</h2>
          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <p className="text-sm text-muted-foreground">Login</p>
              <p className="text-lg font-bold">{account.login}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Server</p>
              <p className="text-lg font-bold">{account.server}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Leverage</p>
              <p className="text-lg font-bold">1:{account.leverage}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Balance</p>
              <p className="text-2xl font-bold">${account.balance?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Equity</p>
              <p className={`text-2xl font-bold ${account.equity >= account.balance ? "text-green-500" : "text-red-500"}`}>
                ${account.equity?.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Free Margin</p>
              <p className="text-2xl font-bold">${account.margin_free?.toFixed(2)}</p>
            </div>
          </div>
        </div>
      )}

      {/* Trading Tab */}
      {tab === "trading" && (
        <div className="space-y-4">
          {/* Auto Trading Status */}
          {autoStatus && (
            <div className="rounded-lg border bg-card p-4">
              <h3 className="mb-3 text-sm font-medium">Auto Trading Config</h3>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Daily Trades</span>
                  <p className="font-medium">{autoStatus.daily_trades} / {autoStatus.max_daily}</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Min Confidence</span>
                  <p className="font-medium">{autoStatus.min_confidence * 100}%</p>
                </div>
                <div>
                  <span className="text-muted-foreground">Allowed Symbols</span>
                  <p className="font-medium">{autoStatus.allowed_symbols?.join(", ")}</p>
                </div>
              </div>
            </div>
          )}

          {/* Open Positions */}
          <div className="rounded-lg border bg-card">
            <div className="border-b px-4 py-3 text-sm font-medium">Open Positions</div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="px-4 py-2 text-left">Ticket</th>
                    <th className="px-4 py-2 text-left">Symbol</th>
                    <th className="px-4 py-2 text-left">Type</th>
                    <th className="px-4 py-2 text-right">Volume</th>
                    <th className="px-4 py-2 text-right">Open</th>
                    <th className="px-4 py-2 text-right">Current</th>
                    <th className="px-4 py-2 text-right">SL</th>
                    <th className="px-4 py-2 text-right">TP</th>
                    <th className="px-4 py-2 text-right">Profit</th>
                  </tr>
                </thead>
                <tbody>
                  {positions?.positions?.map((p: any) => (
                    <tr key={p.ticket} className="border-b last:border-0 hover:bg-secondary/30">
                      <td className="px-4 py-2 font-mono text-xs">{p.ticket}</td>
                      <td className="px-4 py-2 font-medium">{p.symbol}</td>
                      <td className="px-4 py-2">
                        <span className={p.type === "BUY" ? "text-green-500" : "text-red-500"}>{p.type}</span>
                      </td>
                      <td className="px-4 py-2 text-right">{p.volume}</td>
                      <td className="px-4 py-2 text-right font-mono">{p.price_open?.toFixed(5)}</td>
                      <td className="px-4 py-2 text-right font-mono">{p.price_current?.toFixed(5)}</td>
                      <td className="px-4 py-2 text-right font-mono text-red-500">{p.sl?.toFixed(5)}</td>
                      <td className="px-4 py-2 text-right font-mono text-green-500">{p.tp?.toFixed(5)}</td>
                      <td className={`px-4 py-2 text-right font-mono ${p.profit >= 0 ? "text-green-500" : "text-red-500"}`}>
                        ${p.profit?.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                  {(!positions?.positions || positions.positions.length === 0) && (
                    <tr><td colSpan={9} className="px-4 py-8 text-center text-muted-foreground">No open positions</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>

          {/* Executed Signals */}
          <div className="rounded-lg border bg-card">
            <div className="border-b px-4 py-3 text-sm font-medium">Recent Executed Signals</div>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="px-4 py-2 text-left">Time</th>
                    <th className="px-4 py-2 text-left">Symbol</th>
                    <th className="px-4 py-2 text-left">Signal</th>
                    <th className="px-4 py-2 text-right">Confidence</th>
                    <th className="px-4 py-2 text-right">Price</th>
                    <th className="px-4 py-2 text-right">Volume</th>
                  </tr>
                </thead>
                <tbody>
                  {signals.map((s: any, i: number) => (
                    <tr key={i} className="border-b last:border-0 hover:bg-secondary/30">
                      <td className="px-4 py-2 text-xs text-muted-foreground">
                        {new Date(s.time).toLocaleTimeString()}
                      </td>
                      <td className="px-4 py-2 font-medium">{s.symbol}</td>
                      <td className="px-4 py-2">
                        <span className={s.signal === "BUY" ? "text-green-500" : "text-red-500"}>{s.signal}</span>
                      </td>
                      <td className="px-4 py-2 text-right">{s.confidence}%</td>
                      <td className="px-4 py-2 text-right font-mono">{s.price?.toFixed(5)}</td>
                      <td className="px-4 py-2 text-right">{s.volume}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Safety Tab */}
      {tab === "safety" && safety && (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="rounded-lg border bg-card p-6">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <Shield className="h-5 w-5 text-primary" /> Safety Status
            </h2>
            <div className="space-y-3">
              <SafetyRow label="Can Trade" value={safety.can_trade ? "Yes" : "No"} ok={safety.can_trade} />
              <SafetyRow label="Kill Switch" value={safety.kill_switch ? "Engaged ⛔" : "Disarmed ✅"} ok={!safety.kill_switch} />
              <SafetyRow label="Circuit Breaker" value={safety.circuit_breaker_active ? "Active" : "Inactive"} ok={!safety.circuit_breaker_active} />
              <SafetyRow label="Drawdown" value={`${safety.drawdown_percent}%`} ok={safety.drawdown_percent < 10} />
              <SafetyRow label="Daily Loss" value={`$${safety.daily_loss} / $${safety.max_daily_loss}`} ok={safety.daily_loss < safety.max_daily_loss} />
              <SafetyRow label="Consecutive Losses" value={`${safety.consecutive_losses} / ${safety.max_consecutive_losses}`} ok={safety.consecutive_losses < safety.max_consecutive_losses} />
            </div>
          </div>

          <div className="rounded-lg border bg-card p-6">
            <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold">
              <DollarSign className="h-5 w-5 text-primary" /> Account Health
            </h2>
            <div className="space-y-3">
              <SafetyRow label="Current Balance" value={`$${safety.current_balance?.toLocaleString()}`} ok />
              <SafetyRow label="Peak Balance" value={`$${safety.peak_balance?.toLocaleString()}`} ok />
              <SafetyRow label="Drawdown from Peak" value={`${safety.drawdown_percent}%`} ok={safety.drawdown_percent < 5} />
              <div className="mt-4 rounded-md bg-secondary/50 p-3">
                <p className="text-xs text-muted-foreground">Protection Layers Active:</p>
                <ul className="mt-2 space-y-1 text-xs">
                  <li className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-green-500" /> Kill Switch (Manual Emergency)
                  </li>
                  <li className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-green-500" /> Circuit Breaker ({safety.max_consecutive_losses} consecutive losses)
                  </li>
                  <li className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-green-500" /> Max Daily Loss (${safety.max_daily_loss})
                  </li>
                  <li className="flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3 text-green-500" /> Max Drawdown ({safety.max_drawdown_percent || 10}%)
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatusCard({ title, value, icon, ok }: { title: string; value: any; icon: React.ReactNode; ok: boolean }) {
  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{title}</p>
        <div className={`rounded-md p-2 ${ok ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"}`}>{icon}</div>
      </div>
      <p className={`mt-1 text-xl font-bold ${ok ? "" : "text-red-500"}`}>{value}</p>
    </div>
  );
}

function SafetyRow({ label, value, ok }: { label: string; value: any; ok: boolean }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-muted-foreground">{label}</span>
      <div className="flex items-center gap-2">
        <span className={ok ? "text-green-500" : "text-red-500"}>{value}</span>
        {ok ? <CheckCircle2 className="h-3 w-3 text-green-500" /> : <XCircle className="h-3 w-3 text-red-500" />}
      </div>
    </div>
  );
}
