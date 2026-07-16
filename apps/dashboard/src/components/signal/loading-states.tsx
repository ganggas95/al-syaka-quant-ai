"use client";

import { AlertCircle, RefreshCw, SignalIcon } from "lucide-react";

// ─── Skeleton Block ─────────────────────────────────────────────────────────

function SkeletonBlock({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-secondary/60 ${className}`}
    />
  );
}

// ─── Initial Loading State (full skeleton) ──────────────────────────────────

export function InitialLoadingState() {
  return (
    <div className="space-y-6 pb-10">
      {/* Header skeleton */}
      <div className="rounded-lg border bg-card p-6">
        <SkeletonBlock className="mb-4 h-8 w-48" />
        <div className="flex flex-wrap gap-4">
          <SkeletonBlock className="h-10 w-32" />
          <SkeletonBlock className="h-10 w-48" />
          <SkeletonBlock className="h-10 w-36" />
        </div>
      </div>

      {/* Signal banner skeleton */}
      <div className="rounded-xl border bg-card p-6">
        <div className="flex flex-wrap items-center gap-6">
          <SkeletonBlock className="h-14 w-28" />
          <div className="flex-1 space-y-2">
            <SkeletonBlock className="h-5 w-72" />
            <SkeletonBlock className="h-4 w-48" />
          </div>
          <SkeletonBlock className="h-24 w-24 rounded-full" />
        </div>
      </div>

      {/* Parameter row skeleton */}
      <div className="grid grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <SkeletonBlock key={i} className="h-20 w-full rounded-xl" />
        ))}
      </div>

      {/* Main grid skeleton */}
      <div className="grid gap-6 lg:grid-cols-12">
        <div className="space-y-6 lg:col-span-3">
          <SkeletonBlock className="h-80 w-full rounded-xl" />
          <SkeletonBlock className="h-64 w-full rounded-xl" />
        </div>
        <div className="space-y-6 lg:col-span-6">
          <SkeletonBlock className="h-64 w-full rounded-xl" />
          <SkeletonBlock className="h-96 w-full rounded-xl" />
        </div>
        <div className="space-y-6 lg:col-span-3">
          <SkeletonBlock className="h-64 w-full rounded-xl" />
          <SkeletonBlock className="h-64 w-full rounded-xl" />
          <SkeletonBlock className="h-32 w-full rounded-xl" />
        </div>
      </div>
    </div>
  );
}

// ─── Refresh Indicator (subtle bar) ─────────────────────────────────────────

export function RefreshIndicator() {
  return (
    <div className="flex items-center gap-2 rounded-lg bg-blue-500/10 px-3 py-1.5 text-xs text-blue-500">
      <RefreshCw className="h-3 w-3 animate-spin" />
      <span className="font-medium">Refreshing signal...</span>
    </div>
  );
}

// ─── Error State ────────────────────────────────────────────────────────────

interface ErrorStateProps {
  message: string;
  onRetry: () => void;
}

export function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-red-500/20 bg-card p-8 text-center">
      <AlertCircle className="mb-3 h-10 w-10 text-red-500" />
      <h3 className="mb-1 text-lg font-semibold">Failed to Load Signal</h3>
      <p className="mb-4 max-w-md text-sm text-muted-foreground">
        {message}
      </p>
      <button
        onClick={onRetry}
        className="flex items-center gap-2 rounded-lg bg-red-500 px-5 py-2 text-sm font-bold text-white hover:bg-red-400 transition-colors"
      >
        <RefreshCw className="h-4 w-4" />
        Try Again
      </button>
    </div>
  );
}

// ─── Empty State ────────────────────────────────────────────────────────────

export function EmptyState() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border bg-card p-12 text-center">
      <SignalIcon className="mb-4 h-12 w-12 text-muted-foreground/40" />
      <h3 className="mb-2 text-lg font-semibold">No Signal Yet</h3>
      <p className="max-w-md text-sm text-muted-foreground">
        Select a symbol and timeframe above, and the system will automatically
        analyze the market and generate a trading signal.
      </p>
    </div>
  );
}
