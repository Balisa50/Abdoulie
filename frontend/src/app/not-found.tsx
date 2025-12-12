import Link from "next/link";

export default function NotFound() {
  return (
    <div className="mx-auto flex min-h-[60vh] w-full max-w-4xl flex-col justify-center px-6 py-16">
      <h1 className="text-3xl font-semibold text-gray-900">Page not found</h1>
      <p className="mt-2 text-gray-600">
        The page you&apos;re looking for doesn&apos;t exist.
      </p>
      <div className="mt-6">
        <Link
          href="/"
          className="rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-700"
        >
          Go home
        </Link>
      </div>
    </div>
  );
}
