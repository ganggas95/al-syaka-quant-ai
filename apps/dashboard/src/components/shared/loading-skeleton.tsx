"use client";

/**
 * Animated loading skeleton untuk halaman signals.
 * Menampilkan placeholder shapes yang mirror layout charts.
 */

function SkeletonBlock({ className = "" }: { className?: string }) {
  return (
    <div
      className={`animate-pulse rounded-lg bg-secondary/60 ${className}`}
    />
  );
}

export function SignalSkeleton() {
  return (
    <div className="space-y-4">
      {/* Signal banner skeleton */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex flex-wrap items-center gap-6">
          <SkeletonBlock className="h-12 w-24" />
          <div className="flex-1 space-y-2">
            <SkeletonBlock className="h-5 w-64" />
            <SkeletonBlock className="h-4 w-40" />
          </div>
          <SkeletonBlock className="h-24 w-24 rounded-full" />
          <SkeletonBlock className="h-24 w-48" />
        </div>
      </div>

      {/* Grid skeleton */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <div className="space-y-2">
          <SkeletonBlock className="h-64 w-full" />
          <SkeletonBlock className="h-48 w-full" />
        </div>
        <div className="space-y-2">
          <SkeletonBlock className="h-48 w-full" />
          <SkeletonBlock className="h-64 w-full" />
        </div>
        <div className="space-y-2">
          <SkeletonBlock className="h-56 w-full" />
          <SkeletonBlock className="h-56 w-full" />
        </div>
      </div>
    </div>
  );
}
