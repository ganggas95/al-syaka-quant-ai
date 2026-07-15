"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Key, Sliders, Shield, Globe, Bell, Zap, Database, FileText, Info,
  CheckCircle2, XCircle, RotateCcw, Eye, EyeOff, Sun, Moon,
} from "lucide-react";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

type SettingsTab =
  | "api-keys" | "preferences" | "risk" | "data-sources"
  | "notifications" | "auto-trade" | "database" | "system";

const SETTINGS_MENU: { id: SettingsTab; label: string; icon: any }[] = [
  { id: "api-keys", label: "API Keys", icon: Key },
  { id: "preferences", label: "Preferences", icon: Sliders },
  { id: "risk", label: "Risk Management", icon: Shield },
  { id: "data-sources", label: "Data Sources", icon: Globe },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "auto-trade", label: "Auto Trading", icon: Zap },
  { id: "database", label: "Database", icon: Database },
  { id: "system", label: "System Info", icon: Info },
];

export default function SettingsPage() {
  const [tab, setTab] = useState<SettingsTab>("api-keys");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Settings</h1>
        <p className="text-muted-foreground">Platform configuration & management</p>
      </div>

      <div className="flex gap-6">
        {/* Sidebar */}
        <div className="hidden w-52 shrink-0 lg:block">
          <nav className="space-y-1">
            {SETTINGS_MENU.map((item) => {
              const Icon = item.icon;
              return (
                <button key={item.id} onClick={() => setTab(item.id)}
                  className={`flex w-full items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                    tab === item.id
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-secondary hover:text-foreground"
                  }`}>
                  <Icon className="h-4 w-4" /> {item.label}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Mobile tabs */}
        <div className="flex gap-1 overflow-x-auto lg:hidden">
          {SETTINGS_MENU.map((item) => {
            const Icon = item.icon;
            return (
              <button key={item.id} onClick={() => setTab(item.id)}
                className={`flex shrink-0 items-center gap-1 rounded-md px-3 py-2 text-xs font-medium ${
                  tab === item.id ? "bg-primary text-primary-foreground" : "bg-secondary text-muted-foreground"
                }`}>
                <Icon className="h-3 w-3" /> {item.label}
              </button>
            );
          })}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          {tab === "api-keys" && <ApiKeysSection />}
          {tab === "preferences" && <PreferencesSection />}
          {tab === "risk" && <RiskSection />}
          {tab === "data-sources" && <DataSourcesSection />}
          {tab === "notifications" && <NotificationsSection />}
          {tab === "auto-trade" && <AutoTradeSection />}
          {tab === "database" && <DatabaseSection />}
          {tab === "system" && <SystemSection />}
        </div>
      </div>
    </div>
  );
}

// ==================== API KEYS ====================
function ApiKeysSection() {
  const [keys, setKeys] = useState({
    polygon: "",
    alpha_vantage: "",
    massive: "",
    mt5_account: "",
    mt5_password: "",
    mt5_server: "",
  });
  const [saved, setSaved] = useState(false);
  const [showPass, setShowPass] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/settings/keys`).then(r => r.json()).then(d => {
      // Don't pre-fill with masked values
    }).catch(() => {});
  }, []);

  const save = async () => {
    const params = new URLSearchParams(keys);
    await fetch(`${API_URL}/api/v1/settings/keys?${params}`, { method: "POST" });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <SectionCard title="API Keys" desc="Configure API keys for data providers">
      <div className="space-y-4">
        <InputField label="Polygon.io API Key" placeholder="Enter your Polygon API key"
          value={keys.polygon} onChange={(v) => setKeys({ ...keys, polygon: v })} />
        <InputField label="Alpha Vantage API Key" placeholder="Enter your Alpha Vantage key"
          value={keys.alpha_vantage} onChange={(v) => setKeys({ ...keys, alpha_vantage: v })} />
        <InputField label="Massive API Key" placeholder="Enter your Massive API key"
          value={keys.massive} onChange={(v) => setKeys({ ...keys, massive: v })} />
        <div className="border-t pt-4">
          <p className="mb-2 text-sm font-medium text-muted-foreground">MetaTrader 5</p>
          <div className="grid gap-3 md:grid-cols-3">
            <InputField label="Account" placeholder="12345678"
              value={keys.mt5_account} onChange={(v) => setKeys({ ...keys, mt5_account: v })} />
            <div className="relative">
              <InputField label="Password" type={showPass ? "text" : "password"} placeholder="********"
                value={keys.mt5_password} onChange={(v) => setKeys({ ...keys, mt5_password: v })} />
              <button onClick={() => setShowPass(!showPass)}
                className="absolute right-2 top-8 text-muted-foreground hover:text-foreground">
                {showPass ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            <InputField label="Server" placeholder="ICMarkets-Demo"
              value={keys.mt5_server} onChange={(v) => setKeys({ ...keys, mt5_server: v })} />
          </div>
        </div>
        <SaveButton onClick={save} saved={saved} />
      </div>
    </SectionCard>
  );
}

// ==================== PREFERENCES ====================
function PreferencesSection() {
  const [prefs, setPrefs] = useState({
    default_symbol: "EURUSD", default_timeframe: "H1", account_balance: 10000, theme: "dark",
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/settings/preferences`).then(r => r.json()).then(setPrefs).catch(() => {});
  }, []);

  const save = async () => {
    const params = new URLSearchParams(prefs as any);
    await fetch(`${API_URL}/api/v1/settings/preferences?${params}`, { method: "POST" });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <SectionCard title="Trading Preferences" desc="Default settings for the platform">
      <div className="space-y-4">
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Default Symbol</label>
            <select value={prefs.default_symbol} onChange={(e) => setPrefs({ ...prefs, default_symbol: e.target.value })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm">
              {["EURUSD", "XAUUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD"].map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Default Timeframe</label>
            <select value={prefs.default_timeframe} onChange={(e) => setPrefs({ ...prefs, default_timeframe: e.target.value })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm">
              {["M5", "M15", "M30", "H1", "H4", "D1"].map(t => (
                <option key={t} value={t}>{t}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Account Balance ($)</label>
            <input type="number" value={prefs.account_balance}
              onChange={(e) => setPrefs({ ...prefs, account_balance: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Theme</label>
            <div className="flex gap-2">
              <button onClick={() => setPrefs({ ...prefs, theme: "dark" })}
                className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm ${
                  prefs.theme === "dark" ? "bg-primary text-primary-foreground" : "bg-secondary"
                }`}>
                <Moon className="h-4 w-4" /> Dark
              </button>
              <button onClick={() => setPrefs({ ...prefs, theme: "light" })}
                className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm ${
                  prefs.theme === "light" ? "bg-primary text-primary-foreground" : "bg-secondary"
                }`}>
                <Sun className="h-4 w-4" /> Light
              </button>
            </div>
          </div>
        </div>
        <SaveButton onClick={save} saved={saved} />
      </div>
    </SectionCard>
  );
}

// ==================== RISK ====================
function RiskSection() {
  const [risk, setRisk] = useState({
    default_risk_percent: 1.0, max_position_size: 1.0, max_drawdown_percent: 10.0, max_daily_loss: 500,
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/settings/risk`).then(r => r.json()).then(setRisk).catch(() => {});
  }, []);

  const save = async () => {
    const params = new URLSearchParams(risk as any);
    await fetch(`${API_URL}/api/v1/settings/risk?${params}`, { method: "POST" });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <SectionCard title="Risk Management" desc="Default risk parameters for trading">
      <div className="space-y-4">
        <div className="grid gap-3 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Default Risk per Trade (%)</label>
            <input type="number" step="0.1" min="0.1" max="5" value={risk.default_risk_percent}
              onChange={(e) => setRisk({ ...risk, default_risk_percent: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
            <p className="mt-1 text-xs text-muted-foreground">Recommended: 1-2%</p>
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Max Position Size (lots)</label>
            <input type="number" step="0.1" min="0.01" max="10" value={risk.max_position_size}
              onChange={(e) => setRisk({ ...risk, max_position_size: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Max Drawdown (%)</label>
            <input type="number" step="0.5" min="1" max="50" value={risk.max_drawdown_percent}
              onChange={(e) => setRisk({ ...risk, max_drawdown_percent: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Max Daily Loss ($)</label>
            <input type="number" step="50" min="50" value={risk.max_daily_loss}
              onChange={(e) => setRisk({ ...risk, max_daily_loss: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
        </div>
        <SaveButton onClick={save} saved={saved} />
      </div>
    </SectionCard>
  );
}

// ==================== DATA SOURCES ====================
function DataSourcesSection() {
  const [sources, setSources] = useState({ priority: "yahoo,alpha_vantage,polygon", yahoo_enabled: true });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/settings/data-sources`).then(r => r.json()).then(d =>
      setSources({ priority: d.priority?.join(",") || "yahoo", yahoo_enabled: d.yahoo_enabled })
    ).catch(() => {});
  }, []);

  const save = async () => {
    const params = new URLSearchParams({ ...sources, yahoo_enabled: String(sources.yahoo_enabled) });
    await fetch(`${API_URL}/api/v1/settings/data-sources?${params}`, { method: "POST" });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <SectionCard title="Data Sources" desc="Configure market data provider priority">
      <div className="space-y-4">
        <div>
          <label className="mb-1 block text-sm text-muted-foreground">Provider Priority (comma-separated)</label>
          <input value={sources.priority}
            onChange={(e) => setSources({ ...sources, priority: e.target.value })}
            className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          <p className="mt-1 text-xs text-muted-foreground">Order: yahoo, alpha_vantage, polygon</p>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={sources.yahoo_enabled}
            onChange={(e) => setSources({ ...sources, yahoo_enabled: e.target.checked })}
            className="rounded border-gray-600" />
          Yahoo Finance Enabled (free, no API key needed)
        </label>
        <SaveButton onClick={save} saved={saved} />
      </div>
    </SectionCard>
  );
}

// ==================== NOTIFICATIONS ====================
function NotificationsSection() {
  const [notif, setNotif] = useState({
    signal_alerts: true, sl_tp_alerts: true, daily_summary: false, error_alerts: true,
  });
  return (
    <SectionCard title="Notifications" desc="Configure platform alerts">
      <div className="space-y-3">
        {[
          { id: "signal_alerts", label: "Signal Alerts", desc: "Notify when new trading signal is generated" },
          { id: "sl_tp_alerts", label: "SL/TP Alerts", desc: "Notify when stop loss or take profit is hit" },
          { id: "daily_summary", label: "Daily Summary", desc: "Receive end-of-day performance summary" },
          { id: "error_alerts", label: "Error Alerts", desc: "Notify on system errors or connection issues" },
        ].map((item) => (
          <label key={item.id} className="flex items-start gap-3 rounded-md bg-secondary/30 p-3">
            <input type="checkbox" checked={(notif as any)[item.id]}
              onChange={(e) => setNotif({ ...notif, [item.id]: e.target.checked })}
              className="mt-0.5 rounded border-gray-600" />
            <div>
              <p className="text-sm font-medium">{item.label}</p>
              <p className="text-xs text-muted-foreground">{item.desc}</p>
            </div>
          </label>
        ))}
      </div>
    </SectionCard>
  );
}

// ==================== AUTO TRADE ====================
function AutoTradeSection() {
  const [cfg, setCfg] = useState({
    enabled: false, min_confidence: 65, max_daily_trades: 5, allowed_symbols: "EURUSD,XAUUSD,GBPUSD,USDJPY",
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/settings/auto-trade`).then(r => r.json()).then(d =>
      setCfg({ ...d, allowed_symbols: d.allowed_symbols?.join(",") || "EURUSD" })
    ).catch(() => {});
  }, []);

  const save = async () => {
    const params = new URLSearchParams({
      enabled: String(cfg.enabled),
      min_confidence: String(cfg.min_confidence),
      max_daily_trades: String(cfg.max_daily_trades),
      allowed_symbols: cfg.allowed_symbols,
    });
    await fetch(`${API_URL}/api/v1/settings/auto-trade?${params}`, { method: "POST" });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <SectionCard title="Auto Trading" desc="Configuration for automated signal execution">
      <div className="space-y-4">
        <label className="flex items-center gap-3 rounded-md bg-secondary/30 p-3">
          <input type="checkbox" checked={cfg.enabled}
            onChange={(e) => setCfg({ ...cfg, enabled: e.target.checked })}
            className="rounded border-gray-600" />
          <div>
            <p className="text-sm font-medium">Enable Auto Trading</p>
            <p className="text-xs text-muted-foreground">Automatically execute high-confidence signals</p>
          </div>
        </label>
        <div className="grid gap-3 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Min Confidence (%)</label>
            <input type="number" value={cfg.min_confidence} min={50} max={100}
              onChange={(e) => setCfg({ ...cfg, min_confidence: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Max Daily Trades</label>
            <input type="number" value={cfg.max_daily_trades} min={1} max={20}
              onChange={(e) => setCfg({ ...cfg, max_daily_trades: Number(e.target.value) })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
          <div>
            <label className="mb-1 block text-sm text-muted-foreground">Allowed Symbols</label>
            <input value={cfg.allowed_symbols}
              onChange={(e) => setCfg({ ...cfg, allowed_symbols: e.target.value })}
              className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
          </div>
        </div>
        <SaveButton onClick={save} saved={saved} />
      </div>
    </SectionCard>
  );
}

// ==================== DATABASE ====================
function DatabaseSection() {
  const [db, setDb] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchDb = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/v1/settings/db-status`);
      setDb(await res.json());
    } catch {} finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchDb(); }, [fetchDb]);

  return (
    <SectionCard title="Database" desc="Database tables and statistics">
      {loading ? (
        <p className="text-sm text-muted-foreground">Loading...</p>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm">
            {db?.connected ? (
              <><CheckCircle2 className="h-4 w-4 text-green-500" /> <span className="text-green-500">Connected</span></>
            ) : (
              <><XCircle className="h-4 w-4 text-red-500" /> <span className="text-red-500">Disconnected</span></>
            )}
          </div>
          {db?.tables && (
            <div className="grid gap-2 md:grid-cols-2">
              {Object.entries(db.tables).map(([name, count]: [string, any]) => (
                <div key={name} className="flex items-center justify-between rounded-md bg-secondary/30 px-4 py-3 text-sm">
                  <span className="font-medium">{name}</span>
                  <span className="font-mono text-muted-foreground">{count?.toLocaleString() || 0} rows</span>
                </div>
              ))}
            </div>
          )}
          <button onClick={fetchDb}
            className="flex items-center gap-1 rounded-md bg-secondary px-3 py-2 text-sm hover:bg-secondary/80">
            <RotateCcw className="h-3 w-3" /> Refresh
          </button>
        </div>
      )}
    </SectionCard>
  );
}

// ==================== SYSTEM ====================
function SystemSection() {
  const [info, setInfo] = useState<any>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/settings/system-info`).then(r => r.json()).then(setInfo).catch(() => {});
  }, []);

  return (
    <SectionCard title="System Info" desc="Platform version and details">
      {info && (
        <div className="space-y-3">
          {[
            { label: "Platform", value: info.platform },
            { label: "Version", value: info.version },
            { label: "Sprint", value: info.sprint },
            { label: "Python", value: info.python_version },
            { label: "Description", value: info.description },
          ].map((item) => (
            <div key={item.label} className="flex items-center justify-between rounded-md bg-secondary/30 px-4 py-3 text-sm">
              <span className="text-muted-foreground">{item.label}</span>
              <span className="font-medium">{item.value}</span>
            </div>
          ))}
        </div>
      )}
    </SectionCard>
  );
}

// ==================== SHARED COMPONENTS ====================

function SectionCard({ title, desc, children }: { title: string; desc: string; children: React.ReactNode }) {
  return (
    <div className="rounded-lg border bg-card">
      <div className="border-b px-6 py-4">
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{desc}</p>
      </div>
      <div className="p-6">{children}</div>
    </div>
  );
}

function InputField({ label, placeholder, value, onChange, type = "text" }: {
  label: string; placeholder: string; value: string; onChange: (v: string) => void; type?: string;
}) {
  return (
    <div>
      <label className="mb-1 block text-sm text-muted-foreground">{label}</label>
      <input type={type} placeholder={placeholder} value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-md border bg-background px-3 py-2 text-sm" />
    </div>
  );
}

function SaveButton({ onClick, saved }: { onClick: () => void; saved: boolean }) {
  return (
    <button onClick={onClick}
      className={`flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium transition-colors ${
        saved ? "bg-green-500/20 text-green-500" : "bg-primary text-primary-foreground hover:bg-primary/90"
      }`}>
      {saved ? <><CheckCircle2 className="h-4 w-4" /> Saved!</> : "Save Changes"}
    </button>
  );
}
