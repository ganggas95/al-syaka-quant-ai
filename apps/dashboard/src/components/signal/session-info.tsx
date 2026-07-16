"use client";

import { Clock } from "lucide-react";

interface SessionInfoProps {
  /** Current trading session */
  session?: string;
  /** Macro events impacting the market */
  macroEvents?: string[];
}

// Session time ranges (approximate, in UTC)
const SESSION_TIMES: Record<string, { utcStart: string; utcEnd: string }> = {
  "Sydney": { utcStart: "22:00", utcEnd: "07:00" },
  "Tokyo": { utcStart: "00:00", utcEnd: "09:00" },
  "London": { utcStart: "07:00", utcEnd: "16:00" },
  "New York": { utcStart: "13:00", utcEnd: "22:00" },
};

function isSessionActive(sessionName: string): boolean {
  const times = SESSION_TIMES[sessionName];
  if (!times) return false;

  const now = new Date();
  const utcMinutes = now.getUTCHours() * 60 + now.getUTCMinutes();

  const [startH, startM] = times.utcStart.split(":").map(Number);
  const [endH, endM] = times.utcEnd.split(":").map(Number);
  const startMinutes = startH * 60 + startM;
  const endMinutes = endH * 60 + endM;

  if (startMinutes <= endMinutes) {
    return utcMinutes >= startMinutes && utcMinutes < endMinutes;
  }
  // Crosses midnight
  return utcMinutes >= startMinutes || utcMinutes < endMinutes;
}

function getSessionStatus(sessionName: string): { label: string; className: string } {
  if (isSessionActive(sessionName)) {
    return { label: "ACTIVE", className: "text-green-500" };
  }
  return { label: "CLOSED", className: "text-muted-foreground" };
}

export function SessionInfo({
  session,
  macroEvents,
}: SessionInfoProps) {
  const detectedSession = session || detectCurrentSession();

  return (
    <div className="rounded-xl border bg-card p-5">
      <div className="mb-4 flex items-center gap-2">
        <Clock className="h-5 w-5 text-muted-foreground" />
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Session
        </h3>
      </div>

      {/* Active session */}
      <div className="mb-4">
        {detectedSession ? (
          <div className="flex items-center justify-between rounded-lg bg-secondary/30 p-3">
            <div>
              <p className="text-sm font-bold">{detectedSession}</p>
              <p className="text-[10px] text-muted-foreground">
                {SESSION_TIMES[detectedSession]
                  ? `${SESSION_TIMES[detectedSession].utcStart} - ${SESSION_TIMES[detectedSession].utcEnd} UTC`
                  : "Current session"}
              </p>
            </div>
            <span
              className={`text-[10px] font-bold uppercase ${getSessionStatus(detectedSession).className}`}
            >
              {getSessionStatus(detectedSession).label}
            </span>
          </div>
        ) : (
          <div className="rounded-lg bg-secondary/30 p-3">
            <p className="text-xs text-muted-foreground">No session data</p>
          </div>
        )}
      </div>

      {/* All sessions overview */}
      <div className="space-y-1.5">
        <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
          Global Market Sessions
        </h4>
        {Object.entries(SESSION_TIMES).map(([name, times]) => {
          const status = getSessionStatus(name);
          return (
            <div
              key={name}
              className={`flex items-center justify-between rounded-md px-2.5 py-1.5 text-xs ${
                status.label === "ACTIVE" ? "bg-green-500/5 ring-1 ring-green-500/10" : ""
              }`}
            >
              <span className="font-medium">{name}</span>
              <div className="flex items-center gap-2">
                <span className="text-muted-foreground">
                  {times.utcStart}-{times.utcEnd} UTC
                </span>
                <span className={`text-[9px] font-bold uppercase ${status.className}`}>
                  {status.label}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Macro events */}
      {macroEvents && macroEvents.length > 0 && (
        <div className="mt-4 space-y-2">
          <h4 className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
            Economic Events
          </h4>
          <ul className="space-y-1">
            {macroEvents.map((event, i) => (
              <li
                key={i}
                className="rounded-md bg-secondary/20 px-2.5 py-1.5 text-[11px] text-muted-foreground"
              >
                {event}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

/** Detect the current trading session based on UTC time */
function detectCurrentSession(): string | undefined {
  const sessionOrder = ["Sydney", "Tokyo", "London", "New York"];
  return sessionOrder.find((name) => isSessionActive(name));
}
