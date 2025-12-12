"use client";

import { useEffect, useState } from "react";

import { fetchJson, postJson } from "@/lib/api";
import type { AuditLogCreate, AuditLogResponse } from "@/types/api";

interface UseAuditLogsOptions {
  clientId?: string;
  entityId?: string;
  skip?: number;
  limit?: number;
}

export function useAuditLogs(options: UseAuditLogsOptions = {}) {
  const [auditLogs, setAuditLogs] = useState<AuditLogResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const skip = options.skip ?? 0;
  const limit = options.limit ?? 100;

  useEffect(() => {
    let cancelled = false;

    const loadAuditLogs = async () => {
      try {
        setLoading(true);
        let path = `/audit-logs?skip=${skip}&limit=${limit}`;

        if (options.clientId) {
          path = `/audit-logs/search/client/${options.clientId}?skip=${skip}&limit=${limit}`;
        } else if (options.entityId) {
          path = `/audit-logs/search/entity/${options.entityId}?skip=${skip}&limit=${limit}`;
        }

        const data = await fetchJson<AuditLogResponse[]>(path);
        if (!cancelled) {
          setAuditLogs(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load audit logs");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadAuditLogs();

    return () => {
      cancelled = true;
    };
  }, [options.clientId, options.entityId, skip, limit]);

  return { auditLogs, loading, error };
}

export async function createAuditLog(data: AuditLogCreate): Promise<AuditLogResponse> {
  return postJson<AuditLogResponse>("/audit-logs", data);
}

export async function getAuditLog(id: string): Promise<AuditLogResponse> {
  return fetchJson<AuditLogResponse>(`/audit-logs/${id}`);
}
