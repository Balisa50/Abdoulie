"use client";

import { useCallback, useEffect, useState } from "react";

import { fetchJson, postJson } from "@/lib/api";
import type { ClientResponse } from "@/types/api";

interface UseClientsOptions {
  skip?: number;
  limit?: number;
}

export function useClients(options: UseClientsOptions = {}) {
  const [clients, setClients] = useState<ClientResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const skip = options.skip ?? 0;
  const limit = options.limit ?? 100;

  useEffect(() => {
    let cancelled = false;

    const loadClients = async () => {
      try {
        setLoading(true);
        const data = await fetchJson<ClientResponse[]>(`/clients?skip=${skip}&limit=${limit}`);
        if (!cancelled) {
          setClients(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load clients");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadClients();

    return () => {
      cancelled = true;
    };
  }, [skip, limit]);

  return { clients, loading, error };
}

export async function createClient(data: {
  name: string;
  email: string;
  phone?: string;
  address?: string;
}): Promise<ClientResponse> {
  return postJson<ClientResponse>("/clients", data);
}
