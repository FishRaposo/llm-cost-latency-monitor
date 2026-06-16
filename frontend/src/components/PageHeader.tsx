// Page header with title, subtitle, optional source badge and actions.

import type { ReactNode } from "react";
import type { DataSource } from "@/lib/api";
import { DemoModeBadge } from "@/components/DemoModeBadge";

export function PageHeader({
  title,
  subtitle,
  source,
  actions,
}: {
  title: string;
  subtitle?: string;
  source?: DataSource;
  actions?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-start justify-between gap-3">
      <div>
        <div className="flex items-center gap-3">
          <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
          {source && <DemoModeBadge source={source} />}
        </div>
        {subtitle && <p className="mt-1 text-sm text-gray-500">{subtitle}</p>}
      </div>
      {actions && <div className="flex items-center gap-2">{actions}</div>}
    </div>
  );
}
