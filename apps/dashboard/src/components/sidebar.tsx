"use client";

import { cn } from "@/lib/utils";
import {
    BarChart3,
    Bot,
    History,
    LayoutDashboard,
    LineChart,
    Radio,
    Settings,
    TrendingUp
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/", label: "Overview", icon: LayoutDashboard },
  { href: "/market-data", label: "Market Data", icon: TrendingUp },
  { href: "/signals", label: "Signals", icon: Radio },
  { href: "/backtesting", label: "Backtesting", icon: BarChart3 },
  { href: "/replay", label: "Replay", icon: History },
  { href: "/paper-trading", label: "Paper Trading", icon: LineChart },
  { href: "/mt5", label: "MT5 Bridge", icon: Radio },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-64 flex-col border-r bg-card">
      {/* Logo */}
      <div className="flex h-14 items-center gap-2 border-b px-6">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
          <Bot className="h-5 w-5 text-primary-foreground" />
        </div>
        <div>
          <p className="text-sm font-semibold">Al-Syaka</p>
          <p className="text-[10px] text-muted-foreground">Quant AI</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-4">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-secondary hover:text-foreground",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Bottom */}
      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">v0.1.0 • Sprint 1</p>
      </div>
    </aside>
  );
}
