import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";

import { AppHeader } from "@/components/AppHeader";

import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "Tesseract",
    template: "%s",
  },
  description: "Tesseract SaaS MVP",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 antialiased`}
      >
        <AppHeader />
        <main>{children}</main>
        <footer className="border-t border-black/10 bg-white/60">
          <div className="mx-auto max-w-6xl px-6 py-6 text-sm text-gray-600">
            Tesseract SaaS MVP
          </div>
        </footer>
      </body>
    </html>
  );
}
