"use client";

import { Download } from "lucide-react";

interface ExportButtonProps {
  symbol: string;
  timeframe: string;
  data: any[];
  format?: "csv" | "json";
}

export function ExportButton({ symbol, timeframe, data, format = "csv" }: ExportButtonProps) {
  if (!data || data.length === 0) return null;

  const exportCSV = () => {
    const headers = ["timestamp,open,high,low,close,volume"];
    const rows = data.map((d) =>
      `${d.timestamp},${d.open},${d.high},${d.low},${d.close},${d.volume}`
    );
    const csv = [...headers, ...rows].join("\n");
    download(csv, `${symbol}_${timeframe}.csv`, "text/csv");
  };

  const exportJSON = () => {
    const json = JSON.stringify(data, null, 2);
    download(json, `${symbol}_${timeframe}.json`, "application/json");
  };

  const download = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex gap-1">
      <button
        onClick={exportCSV}
        className="flex items-center gap-1 rounded-md bg-secondary px-3 py-1.5 text-xs hover:bg-secondary/80"
      >
        <Download className="h-3 w-3" /> CSV
      </button>
      <button
        onClick={exportJSON}
        className="flex items-center gap-1 rounded-md bg-secondary px-3 py-1.5 text-xs hover:bg-secondary/80"
      >
        <Download className="h-3 w-3" /> JSON
      </button>
    </div>
  );
}
