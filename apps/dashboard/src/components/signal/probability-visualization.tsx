"use client";

interface ProbabilityVisualizationProps {
  confidence: number;
  confidenceLabel?: string;
  decisionConfidence?: number;
}

function getConfidenceColor(value: number): string {
  if (value >= 70) return "text-green-500 stroke-green-500";
  if (value >= 40) return "text-blue-500 stroke-blue-500";
  return "text-red-500 stroke-red-500";
}

function getConfidenceBg(value: number): string {
  if (value >= 70) return "bg-green-500";
  if (value >= 40) return "bg-blue-500";
  return "bg-red-500";
}

function getConfidenceLabel(value: number): string {
  if (value >= 85) return "VERY HIGH";
  if (value >= 70) return "HIGH";
  if (value >= 55) return "MODERATE";
  if (value >= 40) return "MEDIUM";
  if (value >= 20) return "LOW";
  return "VERY LOW";
}

export function ProbabilityVisualization({
  confidence,
  confidenceLabel,
  decisionConfidence,
}: ProbabilityVisualizationProps) {
  const color = getConfidenceColor(confidence);
  const label = confidenceLabel || getConfidenceLabel(confidence);
  const radius = 70;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - confidence / 100);

  return (
    <div className="rounded-xl border bg-card p-5">
      <h3 className="mb-4 text-sm font-medium text-muted-foreground uppercase tracking-wider">
        Probability
      </h3>

      <div className="flex flex-col items-center">
        {/* Circular gauge */}
        <div className="relative flex items-center justify-center">
          <svg width="180" height="180" viewBox="0 0 180 180" className="-rotate-90">
            {/* Background circle */}
            <circle
              cx="90"
              cy="90"
              r={radius}
              fill="none"
              stroke="hsl(var(--secondary))"
              strokeWidth="14"
            />
            {/* Progress arc */}
            <circle
              cx="90"
              cy="90"
              r={radius}
              fill="none"
              stroke="currentColor"
              strokeWidth="14"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className={`transition-all duration-1000 ease-out ${color}`}
            />
          </svg>
          <div className="absolute flex flex-col items-center">
            <span className={`text-4xl font-black ${color}`}>
              {confidence.toFixed(0)}%
            </span>
            <span className="mt-1 text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
              {label}
            </span>
          </div>
        </div>

        {/* Decision confidence bar */}
        {decisionConfidence !== undefined && (
          <div className="mt-6 w-full space-y-1.5">
            <div className="flex justify-between text-[10px] text-muted-foreground">
              <span>Decision Confidence</span>
              <span className="font-mono font-medium">{decisionConfidence.toFixed(0)}%</span>
            </div>
            <div className="h-2 w-full overflow-hidden rounded-full bg-secondary">
              <div
                className={`h-full rounded-full transition-all duration-700 ${getConfidenceBg(decisionConfidence)}`}
                style={{ width: `${decisionConfidence}%` }}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
