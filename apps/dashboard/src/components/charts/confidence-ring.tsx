"use client";

interface ConfidenceRingProps {
  value: number; // 0-100
  size?: number;
  strokeWidth?: number;
  label?: string;
}

/**
 * Animated SVG ring chart untuk menampilkan confidence score.
 * Warna berubah berdasarkan value:
 *   < 40 → red
 *   40-70 → yellow/amber
 *   > 70 → green
 */
export function ConfidenceRing({
  value,
  size = 120,
  strokeWidth = 10,
  label = "Confidence",
}: ConfidenceRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const clampedValue = Math.max(0, Math.min(100, value));
  const offset = circumference - (clampedValue / 100) * circumference;

  const color =
    clampedValue >= 70
      ? "#22c55e" // green-500
      : clampedValue >= 40
        ? "#eab308" // yellow-500
        : "#ef4444"; // red-500

  return (
    <div className="flex flex-col items-center gap-1">
      <svg
        width={size}
        height={size}
        className="-rotate-90"
        role="img"
        aria-label={`${label}: ${clampedValue}%`}
      >
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--secondary))"
          strokeWidth={strokeWidth}
        />
        {/* Foreground arc */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          className="transition-all duration-700 ease-out"
        />
      </svg>
      <div
        className="absolute flex flex-col items-center justify-center"
        style={{ width: size, height: size }}
      >
        <span
          className="text-2xl font-bold"
          style={{ color }}
        >
          {clampedValue}%
        </span>
        <span className="text-[10px] text-muted-foreground">
          {label}
        </span>
      </div>
    </div>
  );
}
