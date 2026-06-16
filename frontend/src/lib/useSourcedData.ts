"use client";

// Generic client hook that loads a Sourced<T> payload, tracking loading,
// error, and data-source ("live" | "demo") state. Because the API client
// already falls back to demo data on fetch failure, the error path here only
// trips on truly unexpected exceptions.

import { useCallback, useEffect, useState } from "react";
import type { Sourced, DataSource } from "@/lib/api";

export interface SourcedState<T> {
  data: T | null;
  source: DataSource | null;
  loading: boolean;
  error: string | null;
  reload: () => void;
}

export function useSourcedData<T>(
  loader: () => Promise<Sourced<T>>,
  deps: unknown[] = []
): SourcedState<T> {
  const [data, setData] = useState<T | null>(null);
  const [source, setSource] = useState<DataSource | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nonce, setNonce] = useState(0);

  const reload = useCallback(() => setNonce((n) => n + 1), []);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const memoLoader = useCallback(loader, deps);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    memoLoader()
      .then((res) => {
        if (cancelled) return;
        setData(res.data);
        setSource(res.source);
      })
      .catch((e: unknown) => {
        if (cancelled) return;
        setError(e instanceof Error ? e.message : "Failed to load data");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [memoLoader, nonce]);

  return { data, source, loading, error, reload };
}
