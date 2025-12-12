import type { Metadata } from "next";
import Link from "next/link";

import { HealthCard } from "@/components/HealthCard";
import { getPublicApiBaseUrl } from "@/lib/api";

export const metadata: Metadata = {
  title: "Home | Tesseract",
  description: "Tesseract SaaS MVP frontend.",
};

export default function HomePage() {
  const apiBaseUrl = getPublicApiBaseUrl();

  return (
    <div className="mx-auto w-full max-w-6xl px-6 py-14">
      <div className="grid grid-cols-1 items-start gap-10 md:grid-cols-2">
        <section>
          <h1 className="text-4xl font-semibold tracking-tight text-gray-900 sm:text-5xl">
            Tesseract SaaS MVP
          </h1>
          <p className="mt-4 text-lg text-gray-600">
            Next.js frontend scaffolded with Tailwind and ready to be wired to the
            FastAPI backend.
          </p>

          <div className="mt-7 flex flex-wrap gap-3">
            <Link
              href="/dashboard"
              className="rounded-md bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
            >
              Open dashboard
            </Link>
            <a
              href={`${apiBaseUrl}/docs`}
              target="_blank"
              rel="noreferrer"
              className="rounded-md border border-black/10 bg-white px-5 py-2.5 text-sm font-semibold text-gray-900 hover:bg-black/5"
            >
              Backend API docs
            </a>
          </div>

          <div className="mt-10 grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-900">Scaffolded pages</h2>
              <p className="mt-1 text-sm text-gray-600">
                Clients, invoices, contracts, and audits are stubbed and ready
                for API integration.
              </p>
            </div>
            <div className="rounded-xl border border-black/10 bg-white p-5 shadow-sm">
              <h2 className="text-sm font-semibold text-gray-900">API helper</h2>
              <p className="mt-1 text-sm text-gray-600">
                A small typed fetch wrapper centralizes base URL handling.
              </p>
            </div>
          </div>
        </section>

        <div className="md:pt-3">
          <HealthCard />
        </div>
      </div>
    </div>
  );
}
