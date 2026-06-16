// Reusable skeleton loaders for the dashboard's data views.

export function KpiCardSkeleton() {
  return (
    <div className="card animate-pulse" data-testid="kpi-skeleton">
      <div className="space-y-3">
        <div className="h-3 w-1/2 rounded bg-gray-200" />
        <div className="h-7 w-2/3 rounded bg-gray-200" />
        <div className="h-2 w-1/3 rounded bg-gray-100" />
      </div>
    </div>
  );
}

export function KpiGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: count }).map((_, i) => (
        <KpiCardSkeleton key={i} />
      ))}
    </div>
  );
}

export function ChartSkeleton({ height = 280 }: { height?: number }) {
  return (
    <div className="card animate-pulse" data-testid="chart-skeleton">
      <div className="mb-4 h-4 w-1/3 rounded bg-gray-200" />
      <div
        className="rounded bg-gray-100"
        style={{ height: `${height}px` }}
      />
    </div>
  );
}

export function TableSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="card animate-pulse" data-testid="table-skeleton">
      <div className="mb-4 h-4 w-1/3 rounded bg-gray-200" />
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, i) => (
          <div key={i} className="flex items-center justify-between">
            <div className="h-3 w-1/3 rounded bg-gray-200" />
            <div className="h-3 w-1/5 rounded bg-gray-100" />
            <div className="h-3 w-1/5 rounded bg-gray-100" />
          </div>
        ))}
      </div>
    </div>
  );
}
