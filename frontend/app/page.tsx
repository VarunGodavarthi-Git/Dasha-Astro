import Link from "next/link";
import { ShieldCheck } from "lucide-react";

import { AuthButtons } from "@/components/auth-buttons";
import { ChartChat } from "@/components/chart-chat";

export default function HomePage() {
  return (
    <main className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-5 flex flex-col gap-4 border-b border-stone-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brass">Dasha Astro</p>
            <h1 className="mt-1 text-2xl font-semibold text-ink">Chart Console</h1>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <Link
              className="inline-flex h-10 items-center gap-2 rounded-md border border-stone-300 bg-white px-3 text-sm font-medium text-ink shadow-sm hover:bg-stone-50"
              href="/admin"
            >
              <ShieldCheck aria-hidden="true" size={16} />
              Admin
            </Link>
            <AuthButtons />
          </div>
        </header>
        <ChartChat />
      </div>
    </main>
  );
}
