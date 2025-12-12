"use client";

import { useEffect, useState } from "react";

import { fetchJson, postJson } from "@/lib/api";
import type { InvoiceCreate, InvoiceResponse } from "@/types/api";

interface UseInvoicesOptions {
  clientId?: string;
  status?: string;
  skip?: number;
  limit?: number;
}

export function useInvoices(options: UseInvoicesOptions = {}) {
  const [invoices, setInvoices] = useState<InvoiceResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const skip = options.skip ?? 0;
  const limit = options.limit ?? 100;

  useEffect(() => {
    let cancelled = false;

    const loadInvoices = async () => {
      try {
        setLoading(true);
        let path = `/invoices?skip=${skip}&limit=${limit}`;

        if (options.clientId) {
          path = `/invoices/search/client/${options.clientId}?skip=${skip}&limit=${limit}`;
        } else if (options.status) {
          path = `/invoices/search/status/${options.status}?skip=${skip}&limit=${limit}`;
        }

        const data = await fetchJson<InvoiceResponse[]>(path);
        if (!cancelled) {
          setInvoices(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load invoices");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    loadInvoices();

    return () => {
      cancelled = true;
    };
  }, [options.clientId, options.status, skip, limit]);

  return { invoices, loading, error };
}

export async function createInvoice(data: InvoiceCreate): Promise<InvoiceResponse> {
  return postJson<InvoiceResponse>("/invoices", data);
}

export async function getInvoice(id: string): Promise<InvoiceResponse> {
  return fetchJson<InvoiceResponse>(`/invoices/${id}`);
}
