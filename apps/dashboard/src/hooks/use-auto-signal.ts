"use client";

import { api, Candle, SignalHistoryEntry, UnifiedSignalResponse } from "@/lib/api";
import { useCallback, useEffect, useRef, useState } from "react";

// ─── Config ─────────────────────────────────────────────────────────────────

const DEBOUNCE_MS = 300;
const MAX_HISTORY = 20;
const AUTO_REFRESH_MS = 300_000; // 5 minutes

// ─── Hook Return Type ───────────────────────────────────────────────────────

export interface UseAutoSignalReturn {
  /** Current signal result (or cached data during refresh) */
  result: UnifiedSignalResponse | null;
  /** Candle data for the price chart */
  candleData: Candle[];
  /** Signal history list */
  signalHistory: SignalHistoryEntry[];
  /** True only during the very first load */
  loading: boolean;
  /** True when auto-refreshing (previously had data) */
  isRefreshing: boolean;
  /** Error message if any */
  error: string | null;
  /** Manually retry fetching */
  retry: () => void;
  /** Seconds remaining until next auto-refresh */
  countdown: number;
}

// ─── Hook ───────────────────────────────────────────────────────────────────

export function useAutoSignal(
  symbol: string,
  timeframe: string,
  includeAI: boolean
): UseAutoSignalReturn {
  const [result, setResult] = useState<UnifiedSignalResponse | null>(null);
  const [candleData, setCandleData] = useState<Candle[]>([]);
  const [signalHistory, setSignalHistory] = useState<SignalHistoryEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [countdown, setCountdown] = useState(AUTO_REFRESH_MS / 1000);

  // Refs for performance & cancellation
  const abortRef = useRef<AbortController | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestIdRef = useRef(0);
  const hasLoadedRef = useRef(false);
  const cachedResultRef = useRef<UnifiedSignalResponse | null>(null);
  const cachedCandleRef = useRef<Candle[]>([]);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const isTabVisibleRef = useRef(true);

  // ── Fetch signal ───────────────────────────────────────────────────────

  const fetchData = useCallback(
    async (sym: string, tf: string, ai: boolean) => {
      // Cancel previous request
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;

      const requestId = ++requestIdRef.current;

      // If we already have data, enter "refreshing" mode instead of full loading
      if (hasLoadedRef.current) {
        setIsRefreshing(true);
      } else {
        setLoading(true);
      }

      setError(null);

      try {
        // Fetch signal
        const signalResult = await api.unifiedSignal(sym, tf, ai, controller.signal);

        // Guard: discard if a newer request has been made
        if (requestId !== requestIdRef.current) return;

        // Update cache
        cachedResultRef.current = signalResult;
        hasLoadedRef.current = true;

        setResult(signalResult);

        // Reset countdown after successful fetch
        setCountdown(AUTO_REFRESH_MS / 1000);

        // Update history
        setSignalHistory((prev) => {
          const exists = prev.some((e) => e.signal_id === signalResult.signal_id);
          if (exists) return prev;
          const entry: SignalHistoryEntry = {
            signal_id: signalResult.signal_id,
            symbol: signalResult.symbol,
            signal: signalResult.signal,
            confidence: signalResult.confidence,
            timestamp: signalResult.timestamp || new Date().toISOString(),
            timeframe: tf,
          };
          return [entry, ...prev].slice(0, MAX_HISTORY);
        });

        // Fetch OHLC in parallel
        const ohlcResult = await api.ohlc(sym, tf, 120, controller.signal);

        if (requestId !== requestIdRef.current) return;
        const candles = ohlcResult.ohlc || ohlcResult.data || [];
        cachedCandleRef.current = candles;
        setCandleData(candles);
      } catch (e: any) {
        if (e.name === "AbortError") return; // Silently ignore aborted requests
        if (requestId !== requestIdRef.current) return;

        // If we have cached data, keep showing it instead of showing error
        if (cachedResultRef.current) {
          setResult(cachedResultRef.current);
          setCandleData(cachedCandleRef.current);
        }

        setError(e.message || "Failed to fetch signal");
      } finally {
        if (requestId === requestIdRef.current) {
          setLoading(false);
          setIsRefreshing(false);
        }
      }
    },
    []
  );

  // ── Debounced fetch on symbol/timeframe change ─────────────────────────

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    debounceRef.current = setTimeout(() => {
      fetchData(symbol, timeframe, includeAI);
    }, DEBOUNCE_MS);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [symbol, timeframe, includeAI, fetchData]);

  // ── Auto-refresh interval ──────────────────────────────────────────────
  // Polls every second for countdown, triggers fetch when countdown hits 0.
  // Pauses when browser tab is not visible.

  useEffect(() => {
    // Clear any previous interval
    if (intervalRef.current) clearInterval(intervalRef.current);

    intervalRef.current = setInterval(() => {
      if (!isTabVisibleRef.current) return; // pause when tab hidden

      setCountdown((prev) => {
        if (prev <= 1) {
          // Time to refresh — trigger fetch asynchronously
          fetchData(symbol, timeframe, includeAI);
          return AUTO_REFRESH_MS / 1000; // reset
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [symbol, timeframe, includeAI, fetchData]);

  // ── Page Visibility API: pause/resume auto-refresh ─────────────────────

  useEffect(() => {
    const handleVisibility = () => {
      isTabVisibleRef.current = !document.hidden;
    };
    document.addEventListener("visibilitychange", handleVisibility);
    return () => document.removeEventListener("visibilitychange", handleVisibility);
  }, []);

  // ── Cleanup on unmount ─────────────────────────────────────────────────

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      if (debounceRef.current) clearTimeout(debounceRef.current);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, []);

  // ── Retry ──────────────────────────────────────────────────────────────

  const retry = useCallback(() => {
    fetchData(symbol, timeframe, includeAI);
  }, [symbol, timeframe, includeAI, fetchData]);

  return {
    result,
    candleData,
    signalHistory,
    loading,
    isRefreshing,
    error,
    retry,
    countdown,
  };
}
