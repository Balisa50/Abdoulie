"use client";

import { useEffect, useState } from "react";

import type { Client, Invoice, Contract, AuditResult } from "@/types";
import { apiGet } from "@/lib/api";

export default function DashboardPage() {
  const [stats, setStats] = useState({
    clients: 0,
    invoices: 0,
    contracts: 0,
    audits: 0,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const [clients, invoices, contracts, audits] = await Promise.all([
          apiGet<Client[]>("/api/clients").then((data) => data.length),
          apiGet<Invoice[]>("/api/invoices").then((data) => data.length),
          apiGet<Contract[]>("/api/contracts").then((data) => data.length),
          apiGet<AuditResult[]>("/api/audit-results").then((data) => data.length),
        ]);

        setStats({
          clients,
          invoices,
          contracts,
          audits,
        });
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load dashboard");
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-14">
      <div className="mb-12">
        <h1 className="text-4xl font-semibold tracking-tight text-gray-900">
          Dashboard
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Overview of your freight audit system
        </p>
      </div>

      {loading ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">Error loading dashboard:</p>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      ) : (
        <>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <p className="text-sm font-medium text-gray-600">Total Clients</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats.clients}
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <p className="text-sm font-medium text-gray-600">Total Invoices</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats.invoices}
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <p className="text-sm font-medium text-gray-600">Total Contracts</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats.contracts}
              </p>
            </div>
            <div className="rounded-lg border border-gray-200 bg-white p-6">
              <p className="text-sm font-medium text-gray-600">Audit Results</p>
              <p className="mt-2 text-3xl font-bold text-gray-900">
                {stats.audits}
              </p>
            </div>
          </div>

          <div className="mt-12 rounded-lg border border-gray-200 bg-white p-8">
            <h2 className="text-lg font-semibold text-gray-900 mb-6">
              Getting Started
            </h2>
            <div className="grid gap-6 md:grid-cols-2">
              <div className="border-l-4 border-indigo-600 pl-4">
                <h3 className="font-semibold text-gray-900">1. Add Clients</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Create customer accounts to start managing invoices
                </p>
              </div>
              <div className="border-l-4 border-indigo-600 pl-4">
                <h3 className="font-semibold text-gray-900">2. Upload Contracts</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Set up rate agreements and contract terms
                </p>
              </div>
              <div className="border-l-4 border-indigo-600 pl-4">
                <h3 className="font-semibold text-gray-900">3. Upload Invoices</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Submit freight invoices for processing
                </p>
              </div>
              <div className="border-l-4 border-indigo-600 pl-4">
                <h3 className="font-semibold text-gray-900">4. Run Audits</h3>
                <p className="mt-1 text-sm text-gray-600">
                  Detect billing errors and discrepancies automatically
                </p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
