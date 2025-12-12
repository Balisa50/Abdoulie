"use client";

import { useEffect, useState } from "react";

import type { Client } from "@/types";
import { apiGet } from "@/lib/api";

export default function ClientsPage() {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClients = async () => {
      try {
        setLoading(true);
        const data = await apiGet<Client[]>("/api/clients");
        setClients(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch clients");
        setClients([]);
      } finally {
        setLoading(false);
      }
    };

    fetchClients();
  }, []);

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-14">
      <div className="mb-8">
        <h1 className="text-4xl font-semibold tracking-tight text-gray-900">
          Clients
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Manage your customer accounts
        </p>
      </div>

      {loading ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-600">Loading clients...</p>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">Error loading clients:</p>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      ) : clients.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-600">No clients found</p>
          <p className="mt-2 text-sm text-gray-500">
            Create your first client to get started
          </p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {clients.map((client) => (
            <div
              key={client.id}
              className="rounded-lg border border-gray-200 bg-white p-6 hover:shadow-lg transition-shadow"
            >
              <h3 className="text-lg font-semibold text-gray-900">
                {client.name}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{client.email}</p>
              {client.phone && (
                <p className="mt-1 text-sm text-gray-600">{client.phone}</p>
              )}
              {client.address && (
                <p className="mt-2 text-sm text-gray-500 line-clamp-2">
                  {client.address}
                </p>
              )}
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-xs text-gray-500">
                  Created: {new Date(client.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
