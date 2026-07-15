"use client";

import { useState, useEffect, useRef } from "react";
import { Search, Star } from "lucide-react";

interface SymbolItem {
  id: number;
  name: string;
  base: string;
  quote: string;
  active: boolean;
}

interface SymbolPickerProps {
  value: string;
  onChange: (symbol: string) => void;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function SymbolPicker({ value, onChange }: SymbolPickerProps) {
  const [symbols, setSymbols] = useState<SymbolItem[]>([]);
  const [search, setSearch] = useState("");
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch(`${API_URL}/api/v1/market/symbols`)
      .then((r) => r.json())
      .then((d) => setSymbols(d.symbols || []))
      .catch(() => {});
  }, []);

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  const filtered = symbols.filter(
    (s) =>
      s.name.toLowerCase().includes(search.toLowerCase()) ||
      s.base.toLowerCase().includes(search.toLowerCase())
  );

  const selected = symbols.find((s) => s.name === value);
  const [favorites, setFavorites] = useState<string[]>(["EURUSD", "XAUUSD", "GBPUSD", "USDJPY"]);

  const toggleFavorite = (name: string) => {
    setFavorites((prev) =>
      prev.includes(name) ? prev.filter((f) => f !== name) : [...prev, name]
    );
  };

  return (
    <div ref={ref} className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex w-full items-center gap-2 rounded-md border bg-background px-3 py-2 text-sm hover:bg-secondary/50"
      >
        <span className="text-base font-bold">{value}</span>
        <span className="text-xs text-muted-foreground">
          {selected ? `${selected.base}/${selected.quote}` : ""}
        </span>
        <Search className="ml-auto h-3.5 w-3.5 text-muted-foreground" />
      </button>

      {open && (
        <div className="absolute z-50 mt-1 w-72 rounded-lg border bg-card shadow-lg">
          <div className="border-b p-2">
            <input
              autoFocus
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search symbol..."
              className="w-full rounded-md bg-background px-3 py-1.5 text-sm outline-none"
            />
          </div>

          {/* Favorites */}
          {search === "" && favorites.length > 0 && (
            <div className="border-b px-2 py-1.5">
              <p className="mb-1 px-2 text-[10px] font-medium text-muted-foreground uppercase">
                Favorites
              </p>
              {favorites.map((f) => {
                const sym = symbols.find((s) => s.name === f);
                if (!sym) return null;
                return (
                  <button
                    key={f}
                    onClick={() => { onChange(f); setOpen(false); }}
                    className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-secondary/50 ${
                      value === f ? "bg-primary/10 text-primary" : ""
                    }`}
                  >
                    <Star
                      className="h-3 w-3 fill-yellow-500 text-yellow-500"
                      onClick={(e) => { e.stopPropagation(); toggleFavorite(f); }}
                    />
                    <span className="font-medium">{f}</span>
                    <span className="text-xs text-muted-foreground">{sym.base}/{sym.quote}</span>
                  </button>
                );
              })}
            </div>
          )}

          {/* Symbol List */}
          <div className="max-h-64 overflow-y-auto p-2">
            {filtered.map((s) => (
              <button
                key={s.id}
                onClick={() => { onChange(s.name); setOpen(false); }}
                className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-secondary/50 ${
                  value === s.name ? "bg-primary/10 text-primary" : ""
                }`}
              >
                <Star
                  className={`h-3 w-3 ${favorites.includes(s.name) ? "fill-yellow-500 text-yellow-500" : "text-muted-foreground"}`}
                  onClick={(e) => { e.stopPropagation(); toggleFavorite(s.name); }}
                />
                <span className="font-medium">{s.name}</span>
                <span className="text-xs text-muted-foreground">{s.base}/{s.quote}</span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
