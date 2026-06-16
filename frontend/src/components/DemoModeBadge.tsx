// Visible indicator that the dashboard is showing bundled demo data because
// the live backend was unreachable.

import { FlaskConical, Radio } from "lucide-react";
import type { DataSource } from "@/lib/api";

export function DemoModeBadge({ source }: { source: DataSource }) {
  if (source === "live") {
    return (
      <span
        className="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-2.5 py-1 text-xs font-medium text-emerald-700"
        data-testid="source-badge-live"
        title="Connected to the live backend"
      >
        <Radio className="h-3.5 w-3.5" />
        Live
      </span>
    );
  }

  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-2.5 py-1 text-xs font-medium text-amber-700"
      data-testid="source-badge-demo"
      title="Backend unreachable — showing bundled demo data"
    >
      <FlaskConical className="h-3.5 w-3.5" />
      Demo mode
    </span>
  );
}

/** Full-width banner shown at the top of a page when in demo mode. */
export function DemoModeBanner({ source }: { source: DataSource }) {
  if (source !== "demo") return null;
  return (
    <div
      className="flex items-center gap-2 rounded-lg border border-amber-200 bg-amber-50 px-4 py-2.5 text-sm text-amber-800"
      data-testid="demo-banner"
      role="status"
    >
      <FlaskConical className="h-4 w-4 shrink-0" />
      <span>
        <strong className="font-semibold">Demo mode.</strong> The backend at{" "}
        <code className="rounded bg-amber-100 px-1 py-0.5 text-xs">
          {process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
        </code>{" "}
        is unreachable, so the dashboard is showing bundled sample data.
      </span>
    </div>
  );
}
