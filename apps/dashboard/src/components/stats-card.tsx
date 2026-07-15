import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down";
  icon: React.ReactNode;
}

export function StatsCard({ title, value, change, trend, icon }: StatsCardProps) {
  return (
    <div className="rounded-lg border bg-card p-4 transition-colors hover:bg-secondary/50">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">{title}</p>
        <div
          className={cn(
            "rounded-md p-2",
            trend === "up" ? "bg-green-500/10 text-green-500" : "bg-red-500/10 text-red-500"
          )}
        >
          {icon}
        </div>
      </div>
      <p className="mt-2 text-2xl font-bold">{value}</p>
      <p
        className={cn(
          "mt-1 text-sm",
          trend === "up" ? "text-green-500" : "text-red-500"
        )}
      >
        {change}
      </p>
    </div>
  );
}
