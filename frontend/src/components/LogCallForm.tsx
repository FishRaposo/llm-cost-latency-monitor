"use client";

// "Log a call" demo form -> POST /log. On success, refreshes the dashboard.
// When the backend is unreachable, surfaces a friendly demo-mode notice instead
// of failing silently.

import { useState } from "react";
import { Send, CheckCircle2, FlaskConical } from "lucide-react";
import { apiClient } from "@/lib/api";
import type { TelemetryPayload } from "@/types";

type Status =
  | { kind: "idle" }
  | { kind: "submitting" }
  | { kind: "success" }
  | { kind: "demo" }
  | { kind: "error"; message: string };

const DEFAULTS: TelemetryPayload = {
  model: "gpt-4o",
  prompt_length: 512,
  input_tokens: 320,
  output_tokens: 180,
  cost_usd: 0.0042,
  latency_ms: 740,
  prompt_version: "v3-summarize",
  error: null,
};

export function LogCallForm({ onLogged }: { onLogged?: () => void }) {
  const [form, setForm] = useState<TelemetryPayload>(DEFAULTS);
  const [status, setStatus] = useState<Status>({ kind: "idle" });

  function update<K extends keyof TelemetryPayload>(
    key: K,
    value: TelemetryPayload[K]
  ) {
    setForm((f) => ({ ...f, [key]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setStatus({ kind: "submitting" });
    try {
      await apiClient.logTelemetry({
        ...form,
        prompt_version: form.prompt_version || null,
        error: form.error || null,
      });
      setStatus({ kind: "success" });
      onLogged?.();
    } catch {
      // Backend unreachable — in demo mode there is nothing to persist to.
      setStatus({ kind: "demo" });
    }
  }

  return (
    <div className="card" data-testid="log-call-form">
      <h3 className="mb-1 text-sm font-semibold text-gray-800">Log a call</h3>
      <p className="mb-4 text-xs text-gray-400">
        Send a telemetry record to <code>POST /log</code>.
      </p>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Model">
            <input
              type="text"
              required
              value={form.model}
              onChange={(e) => update("model", e.target.value)}
              className="input"
            />
          </Field>
          <Field label="Prompt version">
            <input
              type="text"
              value={form.prompt_version ?? ""}
              onChange={(e) => update("prompt_version", e.target.value)}
              className="input"
              placeholder="unversioned"
            />
          </Field>
          <Field label="Input tokens">
            <input
              type="number"
              min={0}
              required
              value={form.input_tokens}
              onChange={(e) =>
                update("input_tokens", Number(e.target.value))
              }
              className="input"
            />
          </Field>
          <Field label="Output tokens">
            <input
              type="number"
              min={0}
              required
              value={form.output_tokens}
              onChange={(e) =>
                update("output_tokens", Number(e.target.value))
              }
              className="input"
            />
          </Field>
          <Field label="Cost (USD)">
            <input
              type="number"
              min={0}
              step="0.000001"
              required
              value={form.cost_usd}
              onChange={(e) => update("cost_usd", Number(e.target.value))}
              className="input"
            />
          </Field>
          <Field label="Latency (ms)">
            <input
              type="number"
              min={0}
              step="0.1"
              required
              value={form.latency_ms}
              onChange={(e) => update("latency_ms", Number(e.target.value))}
              className="input"
            />
          </Field>
          <Field label="Error (optional)">
            <input
              type="text"
              value={form.error ?? ""}
              onChange={(e) => update("error", e.target.value)}
              className="input"
              placeholder="leave blank for success"
            />
          </Field>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={status.kind === "submitting"}
            className="btn-primary inline-flex items-center gap-2 disabled:opacity-60"
          >
            <Send className="h-4 w-4" />
            {status.kind === "submitting" ? "Logging…" : "Log call"}
          </button>

          {status.kind === "success" && (
            <span
              className="inline-flex items-center gap-1.5 text-sm text-emerald-600"
              data-testid="log-success"
            >
              <CheckCircle2 className="h-4 w-4" />
              Logged to backend.
            </span>
          )}
          {status.kind === "demo" && (
            <span
              className="inline-flex items-center gap-1.5 text-sm text-amber-600"
              data-testid="log-demo"
            >
              <FlaskConical className="h-4 w-4" />
              Demo mode — backend unreachable, nothing was persisted.
            </span>
          )}
          {status.kind === "error" && (
            <span className="text-sm text-red-600" data-testid="log-error">
              {status.message}
            </span>
          )}
        </div>
      </form>
    </div>
  );
}

function Field({
  label,
  children,
}: {
  label: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1 block text-xs font-medium text-gray-600">
        {label}
      </span>
      {children}
    </label>
  );
}
