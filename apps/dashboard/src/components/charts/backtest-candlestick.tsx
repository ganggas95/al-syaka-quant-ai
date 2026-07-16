"use client";

import {
  CandlestickData,
  createChart,
  CrosshairMode,
  IChartApi,
  ISeriesApi,
  LineData,
  Time,
  UTCTimestamp,
} from "lightweight-charts";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
// TimeRange interface defined locally (not exported in lw-charts v4.2.1)
interface TimeRange {
  from: Time;
  to: Time;
}

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

// ─── Filters ───────────────────────────────────────────────────────────────

interface TradeFilters {
  result: "all" | "win" | "loss";
  signal: "all" | "BUY" | "SELL" | "BULLISH";
}

const DEFAULT_FILTERS: TradeFilters = { result: "all", signal: "all" };

// ─── Helpers ────────────────────────────────────────────────────────────────

const TF_OPTIONS = [
  { label: "1M", days: 30 },
  { label: "3M", days: 90 },
  { label: "6M", days: 180 },
  { label: "1Y", days: 365 },
  { label: "ALL", days: Infinity },
] as const;

// Zoom level thresholds (in visible bars)
const ZOOM = {
  FAR: 0,
  MEDIUM: 1,
  CLOSE: 2,
  VERY_CLOSE: 3,
} as const;

const ZOOM_THRESHOLDS = [
  { bars: 5000, level: ZOOM.FAR, name: "Far" },
  { bars: 1000, level: ZOOM.MEDIUM, name: "Medium" },
  { bars: 200, level: ZOOM.CLOSE, name: "Close" },
  { bars: 0, level: ZOOM.VERY_CLOSE, name: "Very Close" },
] as const;

function getZoomLevel(chart: IChartApi): number {
  const logicalRange = chart.timeScale().getVisibleLogicalRange();
  if (!logicalRange) return ZOOM.MEDIUM;
  const visibleBars = logicalRange.to - logicalRange.from;
  for (const t of ZOOM_THRESHOLDS) {
    if (visibleBars > t.bars) return t.level;
  }
  return ZOOM.VERY_CLOSE;
}

function parseTime(ts: string): UTCTimestamp {
  return (new Date(ts).getTime() / 1000) as UTCTimestamp;
}

function isTimeInRange(time: number, start: number, end: number) {
  return time >= start && time <= end;
}

// ── Cluster entry markers by time window (for MEDIUM zoom) ────────────
function clusterEntryMarkers(markers: any[], windowSec = 86400): any[] {
  const entryMarkers = markers.filter((m) => m.position !== "inBar");
  const exitMarkers = markers.filter((m) => m.position === "inBar");

  if (entryMarkers.length <= 3) return markers;

  entryMarkers.sort((a, b) => (a.time as number) - (b.time as number));

  const clusters: any[] = [];
  let batch: any[] = [entryMarkers[0]];
  let batchTime = entryMarkers[0].time as number;

  for (let i = 1; i < entryMarkers.length; i++) {
    const t = entryMarkers[i].time as number;
    if (t - batchTime <= windowSec) {
      batch.push(entryMarkers[i]);
    } else {
      const first = batch[0];
      clusters.push({
        time: first.time,
        position: first.position,
        color: batch.length > 1 ? "#a78bfa" : first.color, // purple for clusters
        shape: batch.length > 1 ? "square" : first.shape,
        text: batch.length > 1 ? `${batch.length}` : "",
      });
      batch = [entryMarkers[i]];
      batchTime = t;
    }
  }
  // Last batch
  if (batch.length > 0) {
    const first = batch[0];
    clusters.push({
      time: first.time,
      position: first.position,
      color: batch.length > 1 ? "#a78bfa" : first.color,
      shape: batch.length > 1 ? "square" : first.shape,
      text: batch.length > 1 ? `${batch.length}` : "",
    });
  }

  const result = [...clusters, ...exitMarkers];
  result.sort((a, b) => (a.time as number) - (b.time as number));
  return result;
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
  const winPathSeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const lossPathSeriesRef = useRef<ISeriesApi<"Line"> | null>(null);
  const allMarkersRef = useRef<any[]>([]);
  const viewportTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const zoomLevelRef = useRef<number>(ZOOM.MEDIUM);
  const pathHoverRef = useRef<"none" | "win" | "loss">("none");
  const [timeRange, setTimeRange] = useState<number>(TF_OPTIONS[4].days);
  const [zoomLabel, setZoomLabel] = useState<string>("");
  const [filters, setFilters] = useState<TradeFilters>(DEFAULT_FILTERS);
  const tradeTimeMapRef = useRef<Map<number, TradePlot[]>>(new Map());
  const [tooltipInfo, setTooltipInfo] = useState<{
    trades: TradePlot[];
    x: number;
    y: number;
  } | null>(null);
  const tooltipSetterRef = useRef(setTooltipInfo);
  tooltipSetterRef.current = setTooltipInfo;

  // ── Replay state ──────────────────────────────────────────────────────
  const replayTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const formattedCandlesRef = useRef<CandlestickData[]>([]);
  const [replayMode, setReplayMode] = useState<"off" | "playing" | "paused">(
    "off",
  );
  const [replayIndex, setReplayIndex] = useState<number>(0);
  const [replaySpeed, setReplaySpeed] = useState<number>(1);

  // Pre-compute formatted candles for replay slicing
  const formattedCandles: CandlestickData[] = useMemo(
    () =>
      ohlc
        .map((d) => ({
          time: parseTime(d.timestamp),
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }))
        .filter((d) => {
          const t = d.time as number;
          return !isNaN(t) && isFinite(t);
        }),
    [ohlc],
  );

  // ── Build trade time lookup map (for crosshair tooltip) ─────────────
  useEffect(() => {
    const map = new Map<number, TradePlot[]>();
    trades.forEach((t) => {
      const entryTime = parseTime(t.entry_time) as number;
      if (!map.has(entryTime)) map.set(entryTime, []);
      map.get(entryTime)!.push(t);

      if (t.exit_time) {
        const exitTime = parseTime(t.exit_time) as number;
        if (!map.has(exitTime)) map.set(exitTime, []);
        map.get(exitTime)!.push(t);
      }
    });
    tradeTimeMapRef.current = map;
  }, [trades]);

  // ── Build trade path data filtered by time (for replay) ──────────────
  const buildReplayTradePathData = useCallback(
    (upToTime: number) => {
      const winData: LineData[] = [];
      const lossData: LineData[] = [];

      const completedTrades = trades.filter((t) => {
        if (!t.exit_time) return false;
        const exitTime = parseTime(t.exit_time);
        return !isNaN(exitTime) && exitTime <= upToTime;
      });

      const sortedTrades = [...completedTrades].sort(
        (a, b) => parseTime(a.entry_time) - parseTime(b.entry_time),
      );

      sortedTrades.forEach((t) => {
        if (t.entry == null || t.exit == null || !t.exit_time) return;
        const entryTime = parseTime(t.entry_time);
        const exitTime = parseTime(t.exit_time);
        if (isNaN(entryTime) || isNaN(exitTime)) return;
        if (entryTime === exitTime) return;

        const data = t.profit >= 0 ? winData : lossData;
        data.push({ time: entryTime as UTCTimestamp, value: t.entry });
        data.push({ time: exitTime as UTCTimestamp, value: t.exit });
        data.push({ time: (exitTime + 1) as UTCTimestamp, value: NaN });
      });

      const sortByTime = (a: LineData, b: LineData) =>
        (a.time as number) - (b.time as number);
      winData.sort(sortByTime);
      lossData.sort(sortByTime);

      const dedupe = (arr: LineData[]) => {
        const seen = new Set<number>();
        return arr.filter((d) => {
          const t = d.time as number;
          if (seen.has(t)) return false;
          seen.add(t);
          return true;
        });
      };

      return { winData: dedupe(winData), lossData: dedupe(lossData) };
    },
    [trades],
  );

  // ── Replay timer effect ──────────────────────────────────────────────
  useEffect(() => {
    if (replayMode !== "playing") {
      if (replayTimerRef.current) {
        clearInterval(replayTimerRef.current);
        replayTimerRef.current = null;
      }
      return;
    }

    const speedMap: Record<number, number> = {
      1: 800,
      2: 400,
      5: 150,
      10: 80,
    };
    const interval = speedMap[replaySpeed] ?? 500;

    replayTimerRef.current = setInterval(() => {
      setReplayIndex((prev) => {
        const next = prev + 1;
        if (next >= ohlc.length - 1) {
          setReplayMode("paused");
          return prev;
        }
        return next;
      });
    }, interval);

    return () => {
      if (replayTimerRef.current) {
        clearInterval(replayTimerRef.current);
        replayTimerRef.current = null;
      }
    };
  }, [replayMode, replaySpeed, ohlc.length]);

  // ── Replay chart update effect ───────────────────────────────────────
  useEffect(() => {
    if (replayMode === "off" || !candleSeriesRef.current || !chartRef.current)
      return;

    const candles = formattedCandlesRef.current;
    if (candles.length === 0) return;

    const idx = Math.min(replayIndex, candles.length - 1);
    const sliced = candles.slice(0, idx + 1);
    candleSeriesRef.current.setData(sliced);

    // Update markers — only up to current candle time
    const currentTime = candles[idx].time as number;
    const allMarkers = allMarkersRef.current;
    const replayMarkers = allMarkers.filter(
      (m) => (m.time as number) <= currentTime,
    );
    candleSeriesRef.current.setMarkers(replayMarkers);

    // Update trade paths — only completed trades up to current time
    const { winData, lossData } = buildReplayTradePathData(currentTime);
    winPathSeriesRef.current?.setData(winData);
    lossPathSeriesRef.current?.setData(lossData);

    // Show paths in replay mode (override zoom-level visibility)
    winPathSeriesRef.current?.applyOptions({ visible: winData.length > 0 });
    lossPathSeriesRef.current?.applyOptions({ visible: lossData.length > 0 });

    // Auto-scroll to latest candle
    chartRef.current.timeScale().scrollToPosition(0, false);
  }, [replayIndex, replayMode, buildReplayTradePathData]);

  // Reset replay when ohlc/trades data changes
  useEffect(() => {
    setReplayMode("off");
    setReplayIndex(0);
  }, [ohlc, trades]);

  // Clear previous line series
  const clearLines = () => {
    lineSeriesRef.current.forEach((s) => {
      try {
        chartRef.current?.removeSeries(s);
      } catch {}
    });
    lineSeriesRef.current = [];
  };

  // ── Filter markers by visible range + zoom level ────────────────────
  const filterAndSetMarkers = useCallback((range?: TimeRange | null) => {
    const cs = candleSeriesRef.current;
    const c = chartRef.current;
    if (!cs || !c) return;

    // Calculate zoom level
    zoomLevelRef.current = getZoomLevel(c);
    setZoomLabel(ZOOM_THRESHOLDS[zoomLevelRef.current]?.name ?? "");

    // FAR zoom: no markers, clean lines
    if (zoomLevelRef.current === ZOOM.FAR) {
      cs.setMarkers([]);
      clearLines();
      return;
    }

    if (!range) {
      range =
        (c.timeScale().getVisibleRange() as TimeRange | undefined) ?? null;
    }

    if (!range) {
      cs.setMarkers(allMarkersRef.current);
      return;
    }

    const visStart = range.from as number;
    const visEnd = range.to as number;

    // Only show markers within visible range + 10% buffer
    const buffer = (visEnd - visStart) * 0.1;
    const filtered = allMarkersRef.current.filter((m) => {
      const t = m.time as number;
      return t >= visStart - buffer && t <= visEnd + buffer;
    });

    // MEDIUM zoom: cluster entry markers
    if (zoomLevelRef.current === ZOOM.MEDIUM) {
      const clustered = clusterEntryMarkers(filtered);
      cs.setMarkers(clustered);
      return;
    }

    // CLOSE+ zoom: full markers with text
    cs.setMarkers(filtered);

    // Show/hide trade path lines (CLOSE+ zoom)
    if (winPathSeriesRef.current && lossPathSeriesRef.current) {
      const showPaths = zoomLevelRef.current >= ZOOM.CLOSE;
      winPathSeriesRef.current.applyOptions({ visible: showPaths });
      lossPathSeriesRef.current.applyOptions({ visible: showPaths });
    }
  }, []);

  // ── Visible range change handler (debounced, zoom-aware) ─────────────
  const handleVisibleRange = useCallback(
    (range: TimeRange | null) => {
      if (viewportTimerRef.current) {
        clearTimeout(viewportTimerRef.current);
      }
      viewportTimerRef.current = setTimeout(() => {
        filterAndSetMarkers(range);
      }, 300);
    },
    [filterAndSetMarkers],
  );

  // ── Build markers from trades (with filters applied) ──────────────────
  const buildMarkers = useCallback(() => {
    let validTrades = trades.filter(
      (t) => t.entry != null && (t.exit != null || t.result === "PENDING"),
    );

    // Apply result filter
    if (filters.result === "win") {
      validTrades = validTrades.filter((t) => t.result === "WIN");
    } else if (filters.result === "loss") {
      validTrades = validTrades.filter((t) => t.result === "LOSS");
    }

    // Apply signal filter
    if (filters.signal !== "all") {
      validTrades = validTrades.filter((t) => t.signal === filters.signal);
    }

    validTrades.sort(
      (a, b) => parseTime(a.entry_time) - parseTime(b.entry_time),
    );

    const markers: any[] = [];
    validTrades.forEach((t) => {
      const entryTime = parseTime(t.entry_time);
      if (isNaN(entryTime)) return;
      const isBuy = t.signal === "BUY" || t.signal === "BULLISH";
      const markerColor = isBuy ? "#22c55e" : "#ef4444";

      // Entry marker (Phase 4: no permanent text — tooltip only)
      markers.push({
        time: entryTime as Time,
        position: isBuy ? ("belowBar" as const) : ("aboveBar" as const),
        color: markerColor,
        shape: isBuy ? ("arrowUp" as const) : ("arrowDown" as const),
        text: "",
      });

      // Exit marker — circle only, no text (Phase 4: tooltip only)
      if (t.exit_time && t.exit != null) {
        const exitTime = parseTime(t.exit_time);
        if (isNaN(exitTime)) return;
        markers.push({
          time: exitTime as Time,
          position: "inBar" as const,
          color: t.result === "WIN" ? "#22c55e" : "#ef4444",
          shape: "circle" as const,
          text: "",
        });
      }
    });

    return markers;
  }, [trades, filters]);

  // ── Build trade path data (win = green line, loss = red line) ──────
  const buildTradePathData = useCallback(() => {
    const winData: LineData[] = [];
    const lossData: LineData[] = [];

    // Sort trades by entry time to ensure ascending order
    const sortedTrades = [...trades].sort(
      (a, b) => parseTime(a.entry_time) - parseTime(b.entry_time),
    );

    sortedTrades.forEach((t) => {
      if (t.entry == null || t.exit == null || !t.exit_time) return;
      const entryTime = parseTime(t.entry_time);
      const exitTime = parseTime(t.exit_time);
      if (isNaN(entryTime) || isNaN(exitTime)) return;
      if (entryTime === exitTime) return;

      const data = t.profit >= 0 ? winData : lossData;
      data.push({ time: entryTime as UTCTimestamp, value: t.entry });
      data.push({ time: exitTime as UTCTimestamp, value: t.exit });
      data.push({ time: (exitTime + 1) as UTCTimestamp, value: NaN });
    });

    // Sort by time to ensure ascending order (handles overlapping trades)
    const sortByTime = (a: LineData, b: LineData) =>
      (a.time as number) - (b.time as number);
    winData.sort(sortByTime);
    lossData.sort(sortByTime);

    // Deduplicate by time (lightweight-charts requires unique timestamps)
    const dedupe = (arr: LineData[]) => {
      const seen = new Set<number>();
      return arr.filter((d) => {
        const t = d.time as number;
        if (seen.has(t)) return false;
        seen.add(t);
        return true;
      });
    };

    return { winData: dedupe(winData), lossData: dedupe(lossData) };
  }, [trades]);

  // ── Enter / Exit replay ──────────────────────────────────────────────
  const enterReplay = useCallback(() => {
    formattedCandlesRef.current = formattedCandles;
    setReplayIndex(0);
    setReplayMode("playing");
  }, [formattedCandles]);

  const exitReplay = useCallback(() => {
    setReplayMode("off");
    setReplayIndex(0);
    if (replayTimerRef.current) {
      clearInterval(replayTimerRef.current);
      replayTimerRef.current = null;
    }
    // Restore full chart data
    if (candleSeriesRef.current) {
      candleSeriesRef.current.setData(formattedCandles);
      candleSeriesRef.current.setMarkers(allMarkersRef.current);
    }
    const { winData, lossData } = buildTradePathData();
    winPathSeriesRef.current?.setData(winData);
    lossPathSeriesRef.current?.setData(lossData);
    chartRef.current?.timeScale().fitContent();
  }, [formattedCandles, buildTradePathData]);

  // ── Main effect: create chart, set data, set markers ──────────────────
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
      crosshair: { mode: CrosshairMode.Normal },
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

    formattedCandlesRef.current = formattedCandles;
    candleSeries.setData(formattedCandles);

    // ── Trade path series (win green, loss red) ──────────────────────
    const winPathSeries = chart.addLineSeries({
      color: "rgba(34, 197, 94, 0.5)",
      lineWidth: 2,
      lineStyle: 0,
      lastValueVisible: false,
      priceLineVisible: false,
      visible: false,
    });
    const lossPathSeries = chart.addLineSeries({
      color: "rgba(239, 68, 68, 0.5)",
      lineWidth: 2,
      lineStyle: 0,
      lastValueVisible: false,
      priceLineVisible: false,
      visible: false,
    });
    const { winData, lossData } = buildTradePathData();
    winPathSeries.setData(winData);
    lossPathSeries.setData(lossData);
    winPathSeriesRef.current = winPathSeries;
    lossPathSeriesRef.current = lossPathSeries;

    // ── Stage 1 (0ms): OHLC price data ────────────────────────────────
    candleSeries.setData(formattedCandles);

    // ── Stage 2 (50ms): Fit content — user sees price chart first ────
    const stage2 = setTimeout(() => {
      if (!chartRef.current) return;
      chartRef.current.timeScale().fitContent();
      zoomLevelRef.current = getZoomLevel(chartRef.current);
      setZoomLabel(ZOOM_THRESHOLDS[zoomLevelRef.current]?.name ?? "");
    }, 50);

    // ── Stage 3 (120ms): Build markers, trigger viewport filter ──────
    const stage3 = setTimeout(() => {
      allMarkersRef.current = buildMarkers();
      const cs = candleSeriesRef.current;
      const chart = chartRef.current;
      if (cs && chart) {
        const range = chart.timeScale().getVisibleRange() as TimeRange | null;
        filterAndSetMarkers(range);
      }
    }, 120);

    // ── Subscribe to visible range changes (Phase 1: Viewport Culling) ──
    chart.timeScale().subscribeVisibleTimeRangeChange(handleVisibleRange);

    // ── Crosshair handler: tooltip + path hover opacity ────────────────
    const crosshairHandler = (param: any) => {
      if (!param?.time || !param?.point) {
        tooltipSetterRef.current(null);
        // Reset path opacity when leaving chart
        if (pathHoverRef.current !== "none") {
          pathHoverRef.current = "none";
          winPathSeriesRef.current?.applyOptions({
            color: "rgba(34, 197, 94, 0.5)",
          });
          lossPathSeriesRef.current?.applyOptions({
            color: "rgba(239, 68, 68, 0.5)",
          });
        }
        return;
      }
      const time = param.time as number;
      const tradesAtTime = tradeTimeMapRef.current.get(time);
      if (tradesAtTime && tradesAtTime.length > 0) {
        tooltipSetterRef.current({
          trades: tradesAtTime,
          x: param.point.x,
          y: param.point.y,
        });
      } else {
        tooltipSetterRef.current(null);
      }

      // Path opacity on hover (guard: skip if state unchanged)
      const onWinPath = param.seriesData?.get(winPathSeriesRef.current);
      const onLossPath = param.seriesData?.get(lossPathSeriesRef.current);
      const nextHover = onWinPath ? "win" : onLossPath ? "loss" : "none";
      if (nextHover !== pathHoverRef.current) {
        pathHoverRef.current = nextHover;
        if (nextHover === "win") {
          winPathSeriesRef.current?.applyOptions({ color: "#22c55e" });
          lossPathSeriesRef.current?.applyOptions({
            color: "rgba(239, 68, 68, 0.5)",
          });
        } else if (nextHover === "loss") {
          lossPathSeriesRef.current?.applyOptions({ color: "#ef4444" });
          winPathSeriesRef.current?.applyOptions({
            color: "rgba(34, 197, 94, 0.5)",
          });
        } else {
          winPathSeriesRef.current?.applyOptions({
            color: "rgba(34, 197, 94, 0.5)",
          });
          lossPathSeriesRef.current?.applyOptions({
            color: "rgba(239, 68, 68, 0.5)",
          });
        }
      }
    };
    chart.subscribeCrosshairMove(crosshairHandler);

    // ── Resize handler ─────────────────────────────────────────────────
    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      clearTimeout(viewportTimerRef.current ?? undefined);
      viewportTimerRef.current = null;
      clearTimeout(stage2);
      clearTimeout(stage3);
      try {
        chart.timeScale().unsubscribeVisibleTimeRangeChange(handleVisibleRange);
      } catch {}
      try {
        chart.unsubscribeCrosshairMove(crosshairHandler);
      } catch {}
      window.removeEventListener("resize", handleResize);
      clearLines();
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      winPathSeriesRef.current = null;
      lossPathSeriesRef.current = null;
      allMarkersRef.current = [];
    };
  }, [
    ohlc,
    trades,
    height,
    buildMarkers,
    buildTradePathData,
    handleVisibleRange,
  ]);

  // ── Apply time range filter ──────────────────────────────────────────
  useEffect(() => {
    if (!chartRef.current || !candleSeriesRef.current || ohlc.length === 0)
      return;

    if (timeRange === Infinity) {
      chartRef.current.timeScale().fitContent();
      return;
    }

    // Find the last and first data timestamps
    const firstTs = parseTime(ohlc[0].timestamp);
    const lastTs = parseTime(ohlc[ohlc.length - 1].timestamp);
    const dataDuration = lastTs - firstTs; // total data span in seconds

    // Calculate "from" time based on data end, not Date.now()
    const fromTs = lastTs - Math.min(timeRange * 86400, dataDuration);

    chartRef.current.timeScale().setVisibleRange({
      from: fromTs as Time,
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
          {replayMode !== "off" ? "▶ Replay Mode" : "Price Chart with Trades"}
        </h3>
        <div className="flex items-center gap-2">
          {zoomLabel && (
            <span className="rounded bg-secondary/60 px-2 py-0.5 text-[9px] font-medium text-muted-foreground">
              {zoomLabel}
            </span>
          )}
          {replayMode === "off" ? (
            <div className="flex items-center gap-1.5">
              <button
                onClick={enterReplay}
                className="rounded-md bg-purple-500/20 px-2.5 py-1 text-[10px] font-bold text-purple-400 transition-all hover:bg-purple-500/30"
              >
                ▶ Replay
              </button>
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
          ) : (
            <div className="flex items-center gap-2">
              {/* Speed controls */}
              {[1, 2, 5, 10].map((speed) => (
                <button
                  key={speed}
                  onClick={() => setReplaySpeed(speed)}
                  className={`rounded-md px-2 py-1 text-[10px] font-bold transition-all ${
                    replaySpeed === speed
                      ? "bg-purple-500 text-white"
                      : "bg-secondary text-muted-foreground hover:bg-secondary/80"
                  }`}
                >
                  {speed}x
                </button>
              ))}
              <span className="text-[10px] text-muted-foreground">
                {Math.min(replayIndex + 1, formattedCandles.length)} /{" "}
                {formattedCandles.length}
              </span>
              {/* Play/Pause */}
              <button
                onClick={() =>
                  setReplayMode((m) => (m === "playing" ? "paused" : "playing"))
                }
                className={`rounded-md px-2.5 py-1 text-[11px] font-bold transition-all ${
                  replayMode === "playing"
                    ? "bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30"
                    : "bg-green-500/20 text-green-400 hover:bg-green-500/30"
                }`}
              >
                {replayMode === "playing" ? "⏸" : "▶"}
              </button>
              {/* Stop */}
              <button
                onClick={exitReplay}
                className="rounded-md bg-red-500/20 px-2.5 py-1 text-[10px] font-bold text-red-400 transition-all hover:bg-red-500/30"
              >
                ⏹
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Replay progress bar */}
      {replayMode !== "off" && (
        <div className="mb-3 h-1 w-full overflow-hidden rounded-full bg-secondary">
          <div
            className="h-full rounded-full bg-purple-500 transition-all duration-150"
            style={{
              width: `${((replayIndex + 1) / formattedCandles.length) * 100}%`,
            }}
          />
        </div>
      )}

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
          <span className="inline-block h-2.5 w-2.5 rounded-full border-2 border-muted-foreground" />
          <span>Exit</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 bg-green-500" />
          <span>Win Path</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="inline-block h-0.5 w-4 bg-red-500" />
          <span>Loss Path</span>
        </div>
      </div>

      {/* Filters */}
      <div className="mb-3 flex flex-wrap items-center gap-3 text-[10px]">
        {/* Result filter */}
        <div className="flex items-center gap-1">
          <span className="mr-1 text-muted-foreground">Result:</span>
          {(["all", "win", "loss"] as const).map((opt) => (
            <button
              key={opt}
              disabled={replayMode !== "off"}
              onClick={() => setFilters((f) => ({ ...f, result: opt }))}
              className={`rounded px-2 py-0.5 font-medium transition-all ${
                replayMode !== "off"
                  ? "cursor-not-allowed opacity-40"
                  : filters.result === opt
                    ? opt === "all"
                      ? "bg-secondary text-foreground"
                      : opt === "win"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    : "bg-secondary/40 text-muted-foreground hover:bg-secondary/60"
              }`}
            >
              {opt === "all" ? "ALL" : opt === "win" ? "WIN" : "LOSS"}
            </button>
          ))}
        </div>
        <span className="text-muted-foreground/40">|</span>
        {/* Signal filter */}
        <div className="flex items-center gap-1">
          <span className="mr-1 text-muted-foreground">Signal:</span>
          {(["all", "BUY", "SELL"] as const).map((opt) => (
            <button
              key={opt}
              disabled={replayMode !== "off"}
              onClick={() => setFilters((f) => ({ ...f, signal: opt }))}
              className={`rounded px-2 py-0.5 font-medium transition-all ${
                replayMode !== "off"
                  ? "cursor-not-allowed opacity-40"
                  : filters.signal === opt
                    ? opt === "all"
                      ? "bg-secondary text-foreground"
                      : opt === "BUY"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
                    : "bg-secondary/40 text-muted-foreground hover:bg-secondary/60"
              }`}
            >
              {opt}
            </button>
          ))}
        </div>
      </div>

      {/* Chart + Tooltip (Phase 4) */}
      <div className="relative">
        <div ref={containerRef} className="w-full" />
        {tooltipInfo && (
          <div
            className="pointer-events-none absolute z-50"
            style={{
              left: Math.min(
                tooltipInfo.x + 15,
                (containerRef.current?.clientWidth ?? 600) - 220,
              ),
              top: Math.max(tooltipInfo.y - 10, 0),
            }}
          >
            <div className="rounded-lg border border-border/60 bg-card/95 px-3 py-2 text-xs shadow-xl backdrop-blur-sm">
              {tooltipInfo.trades.slice(0, 3).map((t, i) => {
                const isBuy = t.signal === "BUY" || t.signal === "BULLISH";
                const entryTime = new Date(t.entry_time);
                const exitTime = t.exit_time ? new Date(t.exit_time) : null;
                const durationMs = exitTime
                  ? exitTime.getTime() - entryTime.getTime()
                  : 0;
                const durationHrs = Math.round(durationMs / 3600000);
                const rr =
                  t.sl != null && t.tp != null
                    ? Math.abs((t.tp - t.entry) / (t.entry - t.sl))
                    : null;
                return (
                  <div
                    key={i}
                    className={`${i > 0 ? "mt-1.5 border-t border-border/40 pt-1.5" : ""}`}
                  >
                    <div className="flex items-center gap-2">
                      <span
                        className={`font-semibold ${isBuy ? "text-green-400" : "text-red-400"}`}
                      >
                        {t.signal}
                      </span>
                      <span
                        className={`rounded px-1.5 py-0.5 text-[9px] font-bold ${
                          t.result === "WIN"
                            ? "bg-green-500/20 text-green-400"
                            : t.result === "LOSS"
                              ? "bg-red-500/20 text-red-400"
                              : "bg-yellow-500/20 text-yellow-400"
                        }`}
                      >
                        {t.result}
                      </span>
                    </div>
                    <div className="mt-0.5 grid grid-cols-2 gap-x-3 gap-y-0.5 text-muted-foreground">
                      <span>
                        Entry:{" "}
                        <span className="text-foreground">
                          ${t.entry.toFixed(2)}
                        </span>
                      </span>
                      <span>
                        Profit:{" "}
                        <span
                          className={
                            t.profit >= 0 ? "text-green-400" : "text-red-400"
                          }
                        >
                          {t.profit >= 0 ? "+" : ""}${t.profit.toFixed(2)}
                        </span>
                      </span>
                      {t.exit != null && (
                        <span>
                          Exit:{" "}
                          <span className="text-foreground">
                            ${t.exit.toFixed(2)}
                          </span>
                        </span>
                      )}
                      {t.sl != null && (
                        <span>
                          SL:{" "}
                          <span className="text-foreground">
                            ${t.sl.toFixed(2)}
                          </span>
                        </span>
                      )}
                      {t.tp != null && (
                        <span>
                          TP:{" "}
                          <span className="text-foreground">
                            ${t.tp.toFixed(2)}
                          </span>
                        </span>
                      )}
                      {durationHrs > 0 && (
                        <span>
                          Duration:{" "}
                          <span className="text-foreground">
                            {durationHrs}h
                          </span>
                        </span>
                      )}
                      {rr != null && (
                        <span>
                          RR:{" "}
                          <span className="text-foreground">
                            {rr.toFixed(2)}
                          </span>
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
              {tooltipInfo.trades.length > 3 && (
                <div className="mt-1 text-center text-[9px] text-muted-foreground">
                  +{tooltipInfo.trades.length - 3} more trades
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
