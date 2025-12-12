"use client";

import { useEffect, useState } from "react";

interface HealthResponse {
  status: string;
  app: string;
  version: string;
  timestamp: string;
}

export default function Home() {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const response = await fetch(
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/health"
        );
        const data = await response.json();
        setHealth(data);
      } catch (err) {
        setError("Failed to connect to backend");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <main className="flex flex-col items-center gap-8 text-center">
        <h1 className="text-6xl font-bold text-gray-900">
          Tesseract <span className="text-indigo-600">SaaS</span>
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl">
          Welcome to the Tesseract SaaS MVP - A modern full-stack application
          built with Next.js and FastAPI
        </p>

        <div className="mt-8 p-6 bg-white rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">
            Backend Status
          </h2>

          {loading && (
            <div className="flex justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
            </div>
          )}

          {error && (
            <div className="text-red-600">
              <p className="font-semibold">⚠️ {error}</p>
              <p className="text-sm mt-2">Make sure the backend is running</p>
            </div>
          )}

          {health && (
            <div className="space-y-2 text-left">
              <div className="flex justify-between">
                <span className="font-semibold text-gray-700">Status:</span>
                <span className="text-green-600">✓ {health.status}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-gray-700">App:</span>
                <span className="text-gray-600">{health.app}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-gray-700">Version:</span>
                <span className="text-gray-600">{health.version}</span>
              </div>
              <div className="flex justify-between">
                <span className="font-semibold text-gray-700">Timestamp:</span>
                <span className="text-gray-600 text-sm">
                  {new Date(health.timestamp).toLocaleString()}
                </span>
              </div>
            </div>
          )}
        </div>

        <div className="mt-8 flex gap-4">
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-semibold"
          >
            API Docs
          </a>
          <a
            href="https://nextjs.org/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors font-semibold"
          >
            Next.js Docs
          </a>
        </div>
      </main>
    </div>
  );
}
