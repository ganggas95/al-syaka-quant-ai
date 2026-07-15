"use client";

import { AlertTriangle, CalendarDays } from "lucide-react";

const SAMPLE_EVENTS = [
  { time: "Today 14:30", event: "Fed Interest Rate Decision", impact: "high", currency: "USD" },
  { time: "Today 16:00", event: "FOMC Press Conference", impact: "high", currency: "USD" },
  { time: "Fri 08:30", event: "US Non-Farm Payrolls", impact: "high", currency: "USD" },
  { time: "Fri 10:00", event: "GDP QoQ", impact: "medium", currency: "EUR" },
  { time: "Mon 03:30", event: "RBA Interest Rate Decision", impact: "high", currency: "AUD" },
  { time: "Tue 09:00", event: "German Industrial Production", impact: "medium", currency: "EUR" },
];

export function EconCalendar() {
  return (
    <div className="rounded-lg border bg-card">
      <div className="flex items-center justify-between border-b px-4 py-3">
        <h3 className="flex items-center gap-2 text-sm font-medium">
          <CalendarDays className="h-4 w-4 text-muted-foreground" />
          Economic Calendar
        </h3>
        <span className="text-xs text-muted-foreground">This Week</span>
      </div>
      <div className="divide-y">
        {SAMPLE_EVENTS.map((ev, i) => (
          <div key={i} className="flex items-center justify-between px-4 py-2.5 text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className={`h-3 w-3 shrink-0 ${
                ev.impact === "high" ? "text-red-500" : "text-yellow-500"
              }`} />
              <div>
                <p className="text-xs text-muted-foreground">{ev.time}</p>
                <p className="text-sm">{ev.event}</p>
              </div>
            </div>
            <span className="rounded bg-secondary px-2 py-0.5 text-xs font-medium">
              {ev.currency}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
