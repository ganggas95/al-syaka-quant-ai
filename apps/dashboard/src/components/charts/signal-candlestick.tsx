"use client";

import { useEffect, useRef } from "react";
import {
  createChart,
  IChartApi,
  ISeriesApi,
  CandlestickData,
  LineData,
  UTCTimestamp,
} from "lightweight-charts";

interface CandleData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface SignalCandlestickProps {
  data: CandleData[];
  entryPrice?: number | null;
  stopLoss?: number | null;
  takeProfit?: number | null;
  signal?: string | null; // BUY or SELL
  height?: number;
}

/**
 * Candlestick chart dengan overlay entry/SL/TP lines untuk halaman Signal.
 */
export function SignalCandlestick({
  data,
  entryPrice,
  stopLoss,
  takeProfit,
  signal,
  height = 380,
}: SignalCandlestickProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!containerRef.current || data.length === 0) return;

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

    // Candlestick series
    const candleSeries = chart.addCandlestickSeries({
      upColor: "#22c55e",
      downColor: "#ef4444",
      borderDownColor: "#ef4444",
      borderUpColor: "#22c55e",
      wickDownColor: "#ef4444",
      wickUpColor: "#22c55e",
    });

    const formattedData: CandlestickData[] = data.map((d) => ({
      time: (new Date(d.time).getTime() / 1000) as UTCTimestamp,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));

    candleSeries.setData(formattedData);
    candleSeriesRef.current = candleSeries;

    // Entry line (blue dashed)
    if (entryPrice != null) {
      const entryLine = chart.addLineSeries({
        color: "#3b82f6",
        lineWidth: 1,
        lineStyle: 2, // Dashed
        lastValueVisible: true,
        priceLineVisible: false,
        title: "Entry",
      });
      const entryData: LineData[] = formattedData.map((d) => ({
        time: d.time,
        value: entryPrice,
      }));
      entryLine.setData(entryData);
    }

    // Stop Loss line (red dashed)
    if (stopLoss != null) {
      const slLine = chart.addLineSeries({
        color: "#ef4444",
        lineWidth: 1,
        lineStyle: 2,
        lastValueVisible: true,
        priceLineVisible: false,
        title: "SL",
      });
      const slData: LineData[] = formattedData.map((d) => ({
        time: d.time,
        value: stopLoss,
      }));
      slLine.setData(slData);
    }

    // Take Profit line (green dashed)
    if (takeProfit != null) {
      const tpLine = chart.addLineSeries({
        color: "#22c55e",
        lineWidth: 1,
        lineStyle: 2,
        lastValueVisible: true,
        priceLineVisible: false,
        title: "TP",
      });
      const tpData: LineData[] = formattedData.map((d) => ({
        time: d.time,
        value: takeProfit,
      }));
      tpLine.setData(tpData);
    }

    // Marker for signal
    if (signal && formattedData.length > 0) {
      const lastTime = formattedData[formattedData.length - 1].time;
      const lastCandle = data[data.length - 1];
      const markerColor = signal === "BUY" ? "#22c55e" : "#ef4444";
      candleSeries.setMarkers([
        {
          time: lastTime,
          position: signal === "BUY" ? "belowBar" : "aboveBar",
          color: markerColor,
          shape: signal === "BUY" ? "arrowUp" : "arrowDown",
          text: signal,
        },
      ]);
    }

    chart.timeScale().fitContent();
    chartRef.current = chart;

    const handleResize = () => {
      if (containerRef.current) {
        chart.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, [data, entryPrice, stopLoss, takeProfit, signal, height]);

  if (data.length === 0) {
    return (
      <div className="flex h-64 items-center justify-center rounded-lg border bg-card text-sm text-muted-foreground">
        No price data available
      </div>
    );
  }

  return (
    <div className="rounded-lg border bg-card p-1">
      <div ref={containerRef} className="w-full" />
    </div>
  );
}
