// Friendly empty + error states shared across data views.

import { Inbox, WifiOff, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";

export function EmptyState({
  title = "Nothing here yet",
  message = "No data is available for this view.",
  icon,
}: {
  title?: string;
  message?: string;
  icon?: ReactNode;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border border-dashed border-gray-300 bg-gray-50 p-10 text-center"
      data-testid="empty-state"
    >
      <div className="mb-3 text-gray-400">
        {icon ?? <Inbox className="h-9 w-9" />}
      </div>
      <h3 className="mb-1 text-sm font-semibold text-gray-700">{title}</h3>
      <p className="max-w-sm text-sm text-gray-500">{message}</p>
    </div>
  );
}

export function ErrorState({
  title = "Couldn't load data",
  message = "Something went wrong while fetching this view.",
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className="flex flex-col items-center justify-center rounded-lg border border-red-200 bg-red-50 p-10 text-center"
      data-testid="error-state"
    >
      <WifiOff className="mb-3 h-9 w-9 text-red-400" />
      <h3 className="mb-1 text-sm font-semibold text-red-800">{title}</h3>
      <p className="mb-4 max-w-sm text-sm text-red-600">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="inline-flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700"
        >
          <RefreshCw className="h-4 w-4" />
          Retry
        </button>
      )}
    </div>
  );
}
