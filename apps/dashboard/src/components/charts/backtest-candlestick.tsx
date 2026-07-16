"use client";

import {
    CandlestickData,
    createChart,
    IChartApi,
    ISeriesApi,
    LineData,
    Time,
    UTCTimestamp,
} from "lightweight-charts";
import { useEffect, useRef, useState } from "react";

// ─── Types ──────────────────────────────────────────────────────────────────

interface OHLCBlock {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface TradePlot {
  entry_time: string;
  exit_time?: string;
  signal: string;
  entry: number;
  exit?: number;
  sl?: number;
  tp?: number;
  result: string;
  profit: number;
}

interface BacktestCandlestickProps {
  ohlc: OHLCBlock[];
  trades: TradePlot[];
  height?: number;
}

// ─── Helpers ────────────────────────────────────────────────────────────────

const TF_OPTIONS = [
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: 365 },
  { label: "ALL", days: Infinity },
] as const;

function parseTime(ts: string): UTCTimestamp {
  return (new Date(ts).getTime() / 1000) as UTCTimestamp;
}

function isTimeInRange(time: number, start: number, end: number) {
  return time >= start && time <= end;
}

// ─── Component ──────────────────────────────────────────────────────────────

export function BacktestCandlestick({
  ohlc,
  trades,
  height = 500,
}: BacktestCandlestickProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const lineSeriesRef = useRef<ISeriesApi<"Line">[]>([]);
  const [timeRange, setTimeRange] = useState<number>(TF_OPTIONS[4].days); // Default ALL

  // Clear previous line series
  const clearLines = () => {
    lineSeriesRef.current.forEach((s) => {
      try {
        chartRef.current?.removeSeries(s);
      } catch {}
    });
    lineSeriesRef.current = [];
  };

  useEffect(() => {
    if (!containerRef.current || ohlc.length === 0) return;

    // ── Create chart ────────────────────────────────────────────────────
    const chart = createChart(containerRef.current, {
      layout: {
        background: { color: "transparent" },
        textColor: "#9ca3af",
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.04)" },
        horzLines: { color: "rgba(255,255,255,0.04)" },
      },
      width: containerRef.current.clientWidth,
      height,
      crosshair: { mode: 0 },
      timeScale: {
        borderColor: "rgba(255,255,255,0.08)",
        timeVisible: true,
        secondsVisible: false,
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.08)",
      },
    });
    chartRef.current = chart;

    // ── Candlestick series ──────────────────────────────────────────────
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderDownColor: "#ef4444",
      borderUpColor: "#22c55e",
      wickDownColor: "#ef4444",
      wickUpColor: "#22c55e",
    });
    candleSeriesRef.current = candleSeries;

    const formattedCandles: CandlestickData[] = ohlc.map((d) => ({
      time: parseTime(d.timestamp),
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candleSeries.setData(formattedCandles);

    // ── Trade overlay ───────────────────────────────────────────────────
    // Filter trades: only show closed trades with entry/exit prices
    const validTrades = trades
      .filter(
        (t) => t.entry != null && (t.exit != null || t.result === "PENDING"),
      )
      .slice(0, 100);

    // Sort by entry time
    validTrades.sort(
      (a, b) => parseTime(a.entry_time) - parseTime(b.entry_time),
    );

    // Entry/exit markers
    const markers: any[] = [];
    validTrades.forEach((t) => {
      const entryTime = parseTime(t.entry_time);
      const isBuy = t.signal === "BUY" || t.signal === "BULLISH";
      const markerColor = isBuy ? "#22c55e" : "#ef4444";

      // Entry marker
      markers.push({
        time: entryTime as Time,
        position: isBuy ? ("belowBar" as const) : ("aboveBar" as const),
        color: markerColor,
        shape: isBuy ? ("arrowUp" as const) : ("arrowDown" as const),
        text: `${t.signal} ${t.profit > 0 ? "+" : ""}$${t.profit?.toFixed(0) || "0"}`,
      });

      // Exit marker (if exited)
      if (t.exit_time && t.exit != null) {
        const exitTime = parseTime(t.exit_time);
        markers.push({
          time: exitTime as Time,
          position: "inBar" as const,
          color: t.result === "WIN" ? "#22c55e" : "#ef4444",
          shape: "circle" as const,
          text: `Exit $${t.exit.toFixed(2)}`,
        });
      }
    });

    // Limit markers to avoid performance issues
    if (markers.length > 200) {
      markers.length = 200;
    }
    candleSeries.setMarkers(markers);

    // ── SL/TP lines (only for trades visible in current range) ─────────
    clearLines();

    // We draw lines after chart is ready — use setTimeout to ensure chart state
    setTimeout(() => {
      const visibleRange = chart.timeScale().getVisibleRange();
      if (!visibleRange) return;

      const visStart = visibleRange.from as number;
      const visEnd = visibleRange.to as number;

      validTrades.forEach((t) => {
        const entryTime = parseTime(t.entry_time);
        const exitTime = t.exit_time
          ? parseTime(t.exit_time)
          : entryTime + 86400;

        // Only draw if trade is (partially) in visible range
        if (
          !isTimeInRange(entryTime, visStart, visEnd) &&
          !isTimeInRange(exitTime, visStart, visEnd)
        ) {
          return;
        }

        // SL line
        if (t.sl != null) {
          const slLine = chart.addLineSeries({
            color: "#ef4444",
            lineWidth: 1,
            lineStyle: 2,
            lastValueVisible: false,
            priceLineVisible: false,
          });
          const slData: LineData[] = [
            { time: entryTime as UTCTimestamp, value: t.sl },
            { time: exitTime as UTCTimestamp, value: t.sl },
          ];
          slLine.setData(slData);
          lineSeriesRef.current.push(slLine);
        }

        // TP line
        if (t.tp != null) {
          const tpLine = chart.addLineSeries({
            color: "#22c55e",
            lineWidth: 1,
            lineStyle: 2,
            lastValueVisible: false,
            priceLineVisible: false,
          });
          const tpData: LineData[] = [
            { time: entryTime as UTCTimestamp, value: t.tp },
            { time: exitTime as UTCTimestamp, value: t.tp },
          ];
          tpLine.setData(tpData);
          lineSeriesRef.current.push(tpLine);
        }
      });
    }, 50);

    // ── Fit content ────────────────────────────────────────────────────
    chart.timeScale().fitContent();

    // ── Time range selector handler ────────────────────────────────────
    // (Handled externally via setTimeRange)

    // ── Resize handler ─────────────────────────────────────────────────
    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      clearLines();
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
    };
  }, [ohlc, trades, height]);

  // ── Apply time range filter ──────────────────────────────────────────
  useEffect(() => {
    if (!chartRef.current || !candleSeriesRef.current || ohlc.length === 0)
      return;

    if (timeRange === Infinity) {
      chartRef.current.timeScale().fitContent();
      return;
    }

    const nowTs = Date.now() / 1000;
    const fromTs = nowTs - timeRange * 86400;
    const lastTs = parseTime(ohlc[ohlc.length - 1].timestamp);

    // Find the closest candle time to `fromTs`
    let fromIdx = 0;
    for (let i = 0; i < ohlc.length; i++) {
      if (parseTime(ohlc[i].timestamp) >= fromTs) {
        fromIdx = i;
        break;
      }
    }

    const fromTime = parseTime(ohlc[fromIdx]?.timestamp || ohlc[0].timestamp);

    chartRef.current.timeScale().setVisibleRange({
      from: Math.max(fromTime, lastTs - timeRange * 86400 * 1.1) as Time,
      to: lastTs as Time,
    });
  }, [timeRange, ohlc]);

  // ── Empty state ──────────────────────────────────────────────────────
  if (ohlc.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg border bg-card text-sm text-muted-foreground">
        No price data available
      </div>
    );
  }

  return (
    <div className="rounded-xl border bg-card p-5">
      {/* Header */}
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-sm font-medium text-muted-foreground">
          Price Chart with Trades
        </h3>
        <div className="flex items-center gap-1.5">
          {TF_OPTIONS.map((opt) => (
            <button
              key={opt.label}
              onClick={() => setTimeRange(opt.days)}
              className={`rounded-md px-2.5 py-1 text-[10px] font-bold transition-all ${
                timeRange === opt.days
                  ? "bg-green-500 text-black"
                  : "bg-secondary text-muted-foreground hover:bg-secondary/80"
              }`}
            >
              {opt.label}
            </button>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="mb-3 flex flex-wrap gap-4 text-[10px] text-muted-foreground">
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-green-500" />
          <span>BUY (Win)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full bg-red-500" />
          <span>SELL (Loss)</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 border-t border-dashed border-red-400" />
          <span>Stop Loss</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 border-t border-dashed border-green-400" />
          <span>Take Profit</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-muted-foreground" />
          <span>Exit</span>
        </div>
      </div>

      {/* Chart */}
      <div ref={containerRef} className="w-full" />
    </div>
  );
}
