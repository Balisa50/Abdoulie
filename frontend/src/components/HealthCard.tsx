"use client";

import { useEffect, useState } from "react";

import { fetchJson } from "@/lib/api";
import type { HealthResponse } from "@/types/health";

type Props = {
  compact?: boolean;
};

export function HealthCard({ compact = false }: Props) {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    const run = async () => {
      try {
        const data = await fetchJson<HealthResponse>("/health");
        if (!cancelled) {
          setHealth(data);
        }
      } catch {
        if (!cancelled) {
          setError("Failed to connect to backend");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    run();

    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <section className="rounded-xl border border-black/10 bg-white p-6 shadow-sm">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-gray-900">Backend Status</h2>
          <p className="text-sm text-gray-600">/health</p>
        </div>

        {loading ? (
          <div className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
        ) : null}
      </div>

      {error ? (
        <div className="mt-4 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          <p className="font-semibold">{error}</p>
          <p className="mt-1 text-red-600">
            Make sure the backend is running and NEXT_PUBLIC_API_URL is set
            correctly.
          </p>
        </div>
      ) : null}

      {health ? (
        <dl className={compact ? "mt-4 grid grid-cols-2 gap-3" : "mt-4 space-y-2"}>
          <div className={compact ? "" : "flex items-center justify-between"}>
            <dt className="text-sm font-medium text-gray-700">Status</dt>
            <dd className="text-sm font-semibold text-green-700">
              ✓ {health.status}
            </dd>
          </div>
          <div className={compact ? "" : "flex items-center justify-between"}>
            <dt className="text-sm font-medium text-gray-700">Version</dt>
            <dd className="text-sm text-gray-700">{health.version}</dd>
          </div>
          {!compact ? (
            <div className="flex items-center justify-between">
              <dt className="text-sm font-medium text-gray-700">App</dt>
              <dd className="text-sm text-gray-700">{health.app}</dd>
            </div>
          ) : null}
          {!compact ? (
            <div className="flex items-center justify-between">
              <dt className="text-sm font-medium text-gray-700">Timestamp</dt>
              <dd className="text-sm text-gray-700">
                {new Date(health.timestamp).toLocaleString()}
              </dd>
            </div>
          ) : null}
        </dl>
      ) : null}
    </section>
  );
}
