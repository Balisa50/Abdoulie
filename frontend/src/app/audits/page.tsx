"use client";

import { useEffect, useState } from "react";

import type { AuditResult } from "@/types";
import { apiGet } from "@/lib/api";

export default function AuditsPage() {
  const [audits, setAudits] = useState<AuditResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAudits = async () => {
      try {
        setLoading(true);
        const data = await apiGet<AuditResult[]>("/api/audit-results");
        setAudits(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to fetch audit results");
        setAudits([]);
      } finally {
        setLoading(false);
      }
    };

    fetchAudits();
  }, []);

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-14">
      <div className="mb-8">
        <h1 className="text-4xl font-semibold tracking-tight text-gray-900">
          Audit Results
        </h1>
        <p className="mt-2 text-lg text-gray-600">
          Review and manage invoice audit results
        </p>
      </div>

      {loading ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-600">Loading audit results...</p>
        </div>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4">
          <p className="text-sm font-medium text-red-800">Error loading audits:</p>
          <p className="text-sm text-red-700 mt-1">{error}</p>
        </div>
      ) : audits.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-8 text-center">
          <p className="text-gray-600">No audit results found</p>
          <p className="mt-2 text-sm text-gray-500">
            Run an audit to generate results
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-gray-200">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50">
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Rule ID
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Invoice ID
                </th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                  Created
                </th>
              </tr>
            </thead>
            <tbody>
              {audits.map((audit) => (
                <tr
                  key={audit.id}
                  className="border-b border-gray-200 hover:bg-gray-50"
                >
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">
                    {audit.rule_id}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <span
                      className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                        audit.status === "passed"
                          ? "bg-green-100 text-green-800"
                          : audit.status === "failed"
                            ? "bg-red-100 text-red-800"
                            : "bg-yellow-100 text-yellow-800"
                      }`}
                    >
                      {audit.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {audit.invoice_id ? audit.invoice_id.slice(0, 8) : "—"}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(audit.created_at).toLocaleDateString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
