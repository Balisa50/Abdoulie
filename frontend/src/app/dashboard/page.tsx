import type { Metadata } from "next";
import Link from "next/link";

import { HealthCard } from "@/components/HealthCard";
import { getPublicApiBaseUrl } from "@/lib/api";

export const metadata: Metadata = {
  title: "Dashboard | Tesseract",
};

export default function DashboardPage() {
  const apiBaseUrl = getPublicApiBaseUrl();

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-10">
      <div className="flex flex-col items-start justify-between gap-4 sm:flex-row">
        <div>
          <h1 className="text-3xl font-semibold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Foundation UI for the Tesseract SaaS MVP.
          </p>
        </div>
        <div className="flex flex-wrap gap-3">
          <a
            href={`${apiBaseUrl}/docs`}
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-black/5"
          >
            API Docs
          </a>
          <a
            href={`${apiBaseUrl}/health`}
            target="_blank"
            rel="noreferrer"
            className="rounded-md border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-black/5"
          >
            Health JSON
          </a>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 md:grid-cols-2">
        <HealthCard />

        <section className="rounded-xl border border-black/10 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">Quick Links</h2>
          <p className="mt-1 text-sm text-gray-600">
            These pages are scaffolded and ready to be wired to real endpoints.
          </p>

          <div className="mt-4 grid grid-cols-2 gap-3">
            <Link
              href="/clients"
              className="rounded-lg border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-gray-900 hover:bg-black/5"
            >
              Clients
            </Link>
            <Link
              href="/invoices"
              className="rounded-lg border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-gray-900 hover:bg-black/5"
            >
              Invoices
            </Link>
            <Link
              href="/contracts"
              className="rounded-lg border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-gray-900 hover:bg-black/5"
            >
              Contracts
            </Link>
            <Link
              href="/audits"
              className="rounded-lg border border-black/10 bg-white px-4 py-3 text-sm font-semibold text-gray-900 hover:bg-black/5"
            >
              Audits
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
