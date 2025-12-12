"use client";

import { useEffect, useState } from "react";

import { fetchJson, postJson } from "@/lib/api";
import type { ContractCreate, ContractResponse } from "@/types/api";

interface UseContractsOptions {
  clientId?: string;
  skip?: number;
  limit?: number;
}

export function useContracts(options: UseContractsOptions = {}) {
  const [contracts, setContracts] = useState<ContractResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const skip = options.skip ?? 0;
  const limit = options.limit ?? 100;

  useEffect(() => {
    let cancelled = false;

    const loadContracts = async () => {
      try {
        setLoading(true);
        let path = `/contracts?skip=${skip}&limit=${limit}`;

        if (options.clientId) {
          path = `/contracts/search/client/${options.clientId}?skip=${skip}&limit=${limit}`;
        }

        const data = await fetchJson<ContractResponse[]>(path);
        if (!cancelled) {
          setContracts(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load contracts");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadContracts();

    return () => {
      cancelled = true;
    };
  }, [options.clientId, skip, limit]);

  return { contracts, loading, error };
}

export async function createContract(data: ContractCreate): Promise<ContractResponse> {
  return postJson<ContractResponse>("/contracts", data);
}

export async function getContract(id: string): Promise<ContractResponse> {
  return fetchJson<ContractResponse>(`/contracts/${id}`);
}
