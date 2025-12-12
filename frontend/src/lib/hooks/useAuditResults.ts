"use client";

import { useEffect, useState } from "react";

import { fetchJson, postJson } from "@/lib/api";
import type { AuditResultCreate, AuditResultResponse } from "@/types/api";

interface UseAuditResultsOptions {
  invoiceId?: string;
  contractId?: string;
  skip?: number;
  limit?: number;
}

export function useAuditResults(options: UseAuditResultsOptions = {}) {
  const [auditResults, setAuditResults] = useState<AuditResultResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const skip = options.skip ?? 0;
  const limit = options.limit ?? 100;

  useEffect(() => {
    let cancelled = false;

    const loadAuditResults = async () => {
      try {
        setLoading(true);
        let path = `/audit-results?skip=${skip}&limit=${limit}`;

        if (options.invoiceId) {
          path = `/audit-results/search/invoice/${options.invoiceId}?skip=${skip}&limit=${limit}`;
        } else if (options.contractId) {
          path = `/audit-results/search/contract/${options.contractId}?skip=${skip}&limit=${limit}`;
        }

        const data = await fetchJson<AuditResultResponse[]>(path);
        if (!cancelled) {
          setAuditResults(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load audit results");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadAuditResults();

    return () => {
      cancelled = true;
    };
  }, [options.invoiceId, options.contractId, skip, limit]);

  return { auditResults, loading, error };
}

export async function createAuditResult(data: AuditResultCreate): Promise<AuditResultResponse> {
  return postJson<AuditResultResponse>("/audit-results", data);
}

export async function getAuditResult(id: string): Promise<AuditResultResponse> {
  return fetchJson<AuditResultResponse>(`/audit-results/${id}`);
}
