"use client";

import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

interface OHLCData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface OHLCTableProps {
  data: OHLCData[];
}

export function OHLCTable({ data }: OHLCTableProps) {
  const [sortField, setSortField] = useState<string>("timestamp");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);
  const perPage = 15;

  const sorted = [...data].sort((a, b) => {
    const aVal = (a as any)[sortField];
    const bVal = (b as any)[sortField];
    const cmp = aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
    return sortDir === "asc" ? cmp : -cmp;
  });

  const totalPages = Math.ceil(sorted.length / perPage);
  const paged = sorted.slice(page * perPage, (page + 1) * perPage);

  const toggleSort = (field: string) => {
    if (sortField === field) {
      setSortDir((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortField(field);
      setSortDir("desc");
    }
  };

  const SortIcon = ({ field }: { field: string }) => {
    if (sortField !== field) return null;
    return sortDir === "asc" ? (
      <ChevronUp className="inline h-3 w-3" />
    ) : (
      <ChevronDown className="inline h-3 w-3" />
    );
  };

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b text-muted-foreground">
              <Th onClick={() => toggleSort("timestamp")}><SortIcon field="timestamp" /> Time</Th>
              <Th onClick={() => toggleSort("open")}><SortIcon field="open" /> Open</Th>
              <Th onClick={() => toggleSort("high")}><SortIcon field="high" /> High</Th>
              <Th onClick={() => toggleSort("low")}><SortIcon field="low" /> Low</Th>
              <Th onClick={() => toggleSort("close")}><SortIcon field="close" /> Close</Th>
              <Th onClick={() => toggleSort("volume")}><SortIcon field="volume" /> Vol</Th>
            </tr>
          </thead>
          <tbody>
            {paged.map((row, i) => (
              <tr key={i} className="border-b last:border-0 hover:bg-secondary/30">
                <td className="px-3 py-1.5 text-muted-foreground">
                  {new Date(row.timestamp).toLocaleString()}
                </td>
                <td className="px-3 py-1.5 font-mono">{row.open.toFixed(5)}</td>
                <td className="px-3 py-1.5 font-mono text-green-500">{row.high.toFixed(5)}</td>
                <td className="px-3 py-1.5 font-mono text-red-500">{row.low.toFixed(5)}</td>
                <td className={`px-3 py-1.5 font-mono font-medium ${
                  row.close >= row.open ? "text-green-500" : "text-red-500"
                }`}>
                  {row.close.toFixed(5)}
                </td>
                <td className="px-3 py-1.5 font-mono text-right">{row.volume.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex items-center justify-between border-t px-3 py-2 text-xs text-muted-foreground">
        <span>{sorted.length} rows</span>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className="rounded px-2 py-1 hover:bg-secondary disabled:opacity-30"
          >
            Prev
          </button>
          <span>
            {page + 1} / {totalPages || 1}
          </span>
          <button
            onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
            disabled={page >= totalPages - 1}
            className="rounded px-2 py-1 hover:bg-secondary disabled:opacity-30"
          >
            Next
          </button>
        </div>
      </div>
    </div>
  );
}

function Th({ children, onClick }: { children: React.ReactNode; onClick: () => void }) {
  return (
    <th
      onClick={onClick}
      className="cursor-pointer px-3 py-2 text-left font-medium hover:text-foreground"
    >
      {children}
    </th>
  );
}
