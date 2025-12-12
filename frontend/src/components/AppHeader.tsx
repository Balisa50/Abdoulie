"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { getPublicApiBaseUrl } from "@/lib/api";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/clients", label: "Clients" },
  { href: "/invoices", label: "Invoices" },
  { href: "/contracts", label: "Contracts" },
  { href: "/audits", label: "Audits" },
] as const;

export function AppHeader() {
  const pathname = usePathname();
  const apiBaseUrl = getPublicApiBaseUrl();

  return (
    <header className="border-b border-black/10 bg-white/70 backdrop-blur">
      <div className="mx-auto flex max-w-6xl items-center justify-between gap-6 px-6 py-4">
        <Link href="/" className="font-semibold text-gray-900">
          Tesseract
        </Link>

        <nav className="flex items-center gap-2 overflow-x-auto">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={
                  isActive
                    ? "rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-semibold text-white"
                    : "rounded-md px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-black/5"
                }
              >
                {item.label}
              </Link>
            );
          })}

          <a
            href={`${apiBaseUrl}/docs`}
            target="_blank"
            rel="noreferrer"
            className="rounded-md px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-black/5"
          >
            API Docs
          </a>
        </nav>
      </div>
    </header>
  );
}
