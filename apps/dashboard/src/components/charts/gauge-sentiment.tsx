"use client";

interface GaugeSentimentProps {
  bias: string; // BULLISH, BEARISH, NEUTRAL
  confidence: number; // 0-100
  strength?: number; // 0-100
  size?: number;
}

/**
 * Gauge chart untuk menampilkan Macro Sentiment.
 * Needle mengarah ke BULLISH (kanan), BEARISH (kiri), atau NEUTRAL (tengah).
 * Warna arc menyesuaikan bias.
 */
export function GaugeSentiment({
  bias,
  confidence,
  strength,
  size = 180,
}: GaugeSentimentProps) {
  const cx = size / 2;
  const cy = size / 2;
  const radius = (size - 20) / 2;
  const startAngle = -180;
  const endAngle = 0;

  // Map bias to angle (degrees): BEARISH=left, NEUTRAL=center, BULLISH=right
  const angleMap: Record<string, number> = {
    BEARISH: -60,
    NEUTRAL: 0,
    BULLISH: 60,
  };
  const needleAngle = angleMap[bias] ?? 0;

  // Scale confidence to needle offset within ±30° range
  const needleOffset = ((confidence - 50) / 50) * 30;
  const finalAngle = needleAngle + needleOffset;

  // Color based on bias
  const colorMap: Record<string, string> = {
    BULLISH: "#22c55e",
    BEARISH: "#ef4444",
    NEUTRAL: "#a1a1aa",
  };
  const color = colorMap[bias] ?? "#a1a1aa";

  // Arc path (semi-circle)
  const polarToCartesian = (
    cx: number,
    cy: number,
    r: number,
    angleDeg: number,
  ) => {
    const rad = ((angleDeg - 90) * Math.PI) / 180;
    return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
  };

  const arcStart = polarToCartesian(cx, cy, radius, startAngle);
  const arcEnd = polarToCartesian(cx, cy, radius, endAngle);
  const arcPath = [
    `M ${arcStart.x} ${arcStart.y}`,
    `A ${radius} ${radius} 0 0 1 ${arcEnd.x} ${arcEnd.y}`,
  ].join(" ");

  // Needle endpoint
  const needleRad = ((finalAngle - 90) * Math.PI) / 180;
  const needleLen = radius * 0.7;
  const needleX = cx + needleLen * Math.cos(needleRad);
  const needleY = cy + needleLen * Math.sin(needleRad);

  return (
    <div className="flex flex-col items-center rounded-lg border bg-card p-4">
      <h3 className="mb-2 text-sm font-medium">Macro Sentiment</h3>
      <svg width={size} height={size / 2 + 30} role="img" aria-label={`${bias} sentiment, ${confidence}% confidence`}>
        {/* Arc background */}
        <path d={arcPath} fill="none" stroke="hsl(var(--secondary))" strokeWidth={12} />
        {/* Arc active (colored segment from center to needle) */}
        <path
          d={[
            `M ${cx} ${cy + radius}`,
            `A ${radius} ${radius} 0 0 ${finalAngle > 0 ? 1 : 0}`,
            ` ${needleX} ${needleY}`,
          ].join(" ")}
          fill="none"
          stroke={color}
          strokeWidth={12}
          strokeLinecap="round"
          className="transition-all duration-700 ease-out"
        />
        {/* Needle */}
        <line
          x1={cx}
          y1={cy}
          x2={needleX}
          y2={needleY}
          stroke={color}
          strokeWidth={2.5}
          strokeLinecap="round"
          className="transition-all duration-500 ease-out"
        />
        {/* Center dot */}
        <circle cx={cx} cy={cy} r={5} fill={color} />
        {/* Labels */}
        <text x={10} y={cy + radius + 10} fontSize={11} fill="#a1a1aa">Bearish</text>
        <text x={cx - 12} y={cy + radius + 10} fontSize={11} fill="#a1a1aa">Neutral</text>
        <text x={size - 65} y={cy + radius + 10} fontSize={11} fill="#a1a1aa">Bullish</text>
      </svg>
      <div className="mt-1 flex items-center gap-2">
        <span className="text-lg font-bold" style={{ color }}>
          {bias}
        </span>
        <span className="text-sm text-muted-foreground">
          {confidence.toFixed(0)}%
        </span>
      </div>
      {strength !== undefined && (
        <p className="text-xs text-muted-foreground">
          Strength: {strength.toFixed(0)}
        </p>
      )}
    </div>
  );
}
