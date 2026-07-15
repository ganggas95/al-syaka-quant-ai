"use client";

import { Download, FileJson, ImageIcon } from "lucide-react";
import { useRef, useState } from "react";

interface ExportSignalProps {
  data: Record<string, unknown>;
  signalId?: string;
}

/**
 * Export button untuk menyimpan signal data.
 * - PNG: screenshot area signal
 * - JSON: export raw data
 */
export function ExportSignal({ data, signalId }: ExportSignalProps) {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Save canvas as PNG
  const exportPNG = async () => {
    setExporting(true);
    try {
      // Find the signal result container
      const el = document.querySelector("[data-signal-container]");
      if (!el) {
        // Fallback: download a simple text file
        const blob = new Blob(
          [JSON.stringify(data, null, 2)],
          { type: "text/plain" },
        );
        downloadBlob(blob, `signal-${signalId || "export"}.txt`);
        return;
      }

      // Try to use html-to-image if available
      try {
        const { toPng } = await import("html-to-image");
        const pngData = await toPng(el as HTMLElement, {
          backgroundColor: "#09090b",
          pixelRatio: 2,
        });
        const link = document.createElement("a");
        link.download = `signal-${signalId || "export"}.png`;
        link.href = pngData;
        link.click();
      } catch {
        // Fallback: download JSON
        exportJSON();
      }
    } finally {
      setExporting(false);
      setOpen(false);
    }
  };

  // Export raw JSON data
  const exportJSON = () => {
    const blob = new Blob(
      [JSON.stringify(data, null, 2)],
      { type: "application/json" },
    );
    downloadBlob(blob, `signal-${signalId || "export"}.json`);
    setOpen(false);
  };

  const downloadBlob = (blob: Blob, filename: string) => {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative" ref={menuRef}>
      <button
        onClick={() => setOpen(!open)}
        disabled={exporting}
        className="flex items-center gap-1.5 rounded-md bg-secondary px-3 py-1.5 text-xs font-medium transition-colors hover:bg-secondary/80 disabled:opacity-50"
      >
        <Download className="h-3.5 w-3.5" />
        {exporting ? "Exporting..." : "Export"}
      </button>

      {open && (
        <div className="absolute right-0 top-full z-50 mt-1 w-40 overflow-hidden rounded-lg border bg-popover shadow-lg">
          <button
            onClick={exportJSON}
            className="flex w-full items-center gap-2 px-3 py-2 text-xs font-medium transition-colors hover:bg-secondary/50"
          >
            <FileJson className="h-3.5 w-3.5 text-blue-500" />
            Export JSON
          </button>
          <button
            onClick={exportPNG}
            className="flex w-full items-center gap-2 px-3 py-2 text-xs font-medium transition-colors hover:bg-secondary/50"
          >
            <ImageIcon className="h-3.5 w-3.5 text-green-500" />
            Export PNG
          </button>
        </div>
      )}

      {/* Click outside to close */}
      {open && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setOpen(false)}
        />
      )}
    </div>
  );
}
