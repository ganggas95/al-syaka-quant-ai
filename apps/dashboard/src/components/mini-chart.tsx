"use client";

import { useEffect, useRef } from "react";
import { createChart, IChartApi, ISeriesApi, CandlestickData, UTCTimestamp } from "lightweight-charts";

interface MiniChartProps {
  symbol: string;
  data: { time: string; open: number; high: number; low: number; close: number }[];
  height?: number;
  onClick?: () => void;
}

export function MiniChart({ symbol, data, height = 80, onClick }: MiniChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

    const chart = createChart(containerRef.current, {
      layout: { background: { color: "transparent" }, textColor: "transparent" },
      grid: { vertLines: { color: "transparent" }, horzLines: { color: "transparent" } },
      width: containerRef.current.clientWidth,
      height,
      crosshair: { mode: 0 },
      timeScale: { visible: false },
      rightPriceScale: { visible: false },
      handleScroll: false,
      handleScale: false,
    });

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#22c55e", downColor: "#ef4444",
      borderDownColor: "#ef4444", borderUpColor: "#22c55e",
      wickDownColor: "#ef4444", wickUpColor: "#22c55e",
    });

    candleSeries.setData(data.map((d) => ({
      time: (new Date(d.time).getTime() / 1000) as UTCTimestamp,
      open: d.open, high: d.high, low: d.low, close: d.close,
    })));
    chart.timeScale().fitContent();
    chartRef.current = chart;

    return () => chart.remove();
  }, [data, height]);

  return (
    <div ref={containerRef} className="w-full cursor-pointer" onClick={onClick} />
  );
}
