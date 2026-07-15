"use client";

interface RegimeProbabilityProps {
  regime: string;
  reason?: string;
}

/**
 * Regime badge dengan probability bar.
 * Menampilkan regime saat ini dan kemungkinan regime alternatif.
 * Karena API hanya mengembalikan regime tunggal, kita tampilkan
 * sebagai bar visual dengan indikator confidence.
 */
export function RegimeProbability({
  regime,
  reason,
}: RegimeProbabilityProps) {
  const regimes = [
    { label: "TRENDING", color: "bg-blue-500", textColor: "text-blue-500" },
    { label: "RANGE", color: "bg-yellow-500", textColor: "text-yellow-500" },
    { label: "VOLATILE", color: "bg-red-500", textColor: "text-red-500" },
    { label: "REVERSAL", color: "bg-purple-500", textColor: "text-purple-500" },
  ];

  const currentRegime = regimes.find(
    (r) => r.label === regime?.toUpperCase(),
  );

  return (
    <div className="rounded-lg border bg-card p-4">
      <h3 className="mb-3 text-sm font-medium">Market Regime</h3>

      {/* Current regime badge */}
      <div className="mb-3 flex items-center gap-3">
        <span
          className={`rounded-lg px-3 py-1.5 text-sm font-bold ${
            currentRegime
              ? `${currentRegime.color}/10 ${currentRegime.textColor}`
              : "bg-secondary text-muted-foreground"
          }`}
        >
          {regime || "N/A"}
        </span>
      </div>

      {/* Regime probability bars */}
      <div className="space-y-2">
        {regimes.map((r) => {
          const isActive = r.label === regime?.toUpperCase();
          return (
            <div key={r.label} className="space-y-0.5">
              <div className="flex items-center justify-between text-xs">
                <span
                  className={`font-medium ${
                    isActive ? r.textColor : "text-muted-foreground"
                  }`}
                >
                  {r.label.charAt(0) + r.label.slice(1).toLowerCase()}
                </span>
                <span className="text-muted-foreground">
                  {isActive ? "✓ Active" : ""}
                </span>
              </div>
              <div className="relative h-2 w-full overflow-hidden rounded-full bg-secondary">
                <div
                  className={`absolute inset-y-0 left-0 rounded-full transition-all duration-500 ${
                    isActive ? r.color : "bg-secondary"
                  }`}
                  style={{
                    width: isActive ? "100%" : "0%",
                    opacity: isActive ? 1 : 0.3,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Reason */}
      {reason && (
        <p className="mt-3 text-xs text-muted-foreground">{reason}</p>
      )}
    </div>
  );
}
