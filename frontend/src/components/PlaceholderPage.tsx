import Link from "next/link";

import { getPublicApiBaseUrl } from "@/lib/api";

type Props = {
  title: string;
  description?: string;
};

export function PlaceholderPage({ title, description }: Props) {
  const apiBaseUrl = getPublicApiBaseUrl();

  return (
    <div className="mx-auto w-full max-w-4xl px-6 py-10">
      <h1 className="text-3xl font-semibold text-gray-900">{title}</h1>
      <p className="mt-3 text-gray-600">
        {description ?? "This section is not wired up yet."}
      </p>

      <div className="mt-6 flex flex-wrap gap-3">
        <Link
          href="/dashboard"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          Back to Dashboard
        </Link>
        <a
          href={`${apiBaseUrl}/docs`}
          target="_blank"
          rel="noreferrer"
          className="rounded-md border border-black/10 bg-white px-4 py-2 text-sm font-semibold text-gray-900 hover:bg-black/5"
        >
          View API Docs
        </a>
      </div>
    </div>
  );
}
