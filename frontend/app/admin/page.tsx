"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, RotateCcw, ShieldCheck, Trash2 } from "lucide-react";
import { useSession } from "next-auth/react";

type ChatLog = {
  id: number;
  user_email: string | null;
  user_name: string | null;
  city_name: string;
  prompt_text: string;
  ai_response: string;
  model: string;
  created_at: string;
};

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export default function AdminPage() {
  const { data: session, status } = useSession();
  const [logs, setLogs] = useState<ChatLog[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const isAdmin = session?.user?.role === "ADMIN";

  async function loadLogs() {
    if (!session?.user?.email || !isAdmin) {
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${apiBaseUrl}/admin/logs`, {
        headers: {
          "x-user-email": session.user.email
        }
      });
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }
      setLogs(await response.json());
    } catch (caught) {
      setMessage(caught instanceof Error ? caught.message : "Could not load logs.");
    } finally {
      setLoading(false);
    }
  }

  async function clearLogs() {
    if (!session?.user?.email || !isAdmin) {
      return;
    }
    setLoading(true);
    setMessage("");
    try {
      const response = await fetch(`${apiBaseUrl}/admin/logs`, {
        method: "DELETE",
        headers: {
          "x-user-email": session.user.email
        }
      });
      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }
      const result = await response.json();
      setLogs([]);
      setMessage(`Cleared ${result.deleted} log entries.`);
    } catch (caught) {
      setMessage(caught instanceof Error ? caught.message : "Could not clear logs.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadLogs();
  }, [isAdmin, session?.user?.email]);

  if (status === "loading") {
    return <main className="min-h-screen bg-[#f6f4ef] p-6" />;
  }

  if (!isAdmin) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#f6f4ef] px-4">
        <section className="w-full max-w-md rounded-lg border border-stone-200 bg-white p-6 text-center shadow-soft">
          <ShieldCheck className="mx-auto mb-3 text-brass" size={28} />
          <h1 className="text-xl font-semibold text-ink">Admin Access Required</h1>
          <p className="mt-2 text-sm leading-6 text-stone-600">Sign in with the configured admin email.</p>
          <Link className="mt-5 inline-flex h-10 items-center gap-2 rounded-md bg-ink px-3 text-sm font-medium text-white" href="/">
            <ArrowLeft aria-hidden="true" size={16} />
            Return
          </Link>
        </section>
      </main>
    );
  }

  return (
    <main className="min-h-screen px-4 py-5 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-5 flex flex-col gap-4 border-b border-stone-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-brass">Safety & Governance</p>
            <h1 className="mt-1 text-2xl font-semibold text-ink">Interaction Logs</h1>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Link className="inline-flex h-10 items-center gap-2 rounded-md border border-stone-300 bg-white px-3 text-sm font-medium text-ink shadow-sm hover:bg-stone-50" href="/">
              <ArrowLeft aria-hidden="true" size={16} />
              Console
            </Link>
            <button
              className="inline-flex h-10 items-center gap-2 rounded-md border border-stone-300 bg-white px-3 text-sm font-medium text-ink shadow-sm hover:bg-stone-50"
              disabled={loading}
              onClick={loadLogs}
              type="button"
            >
              <RotateCcw aria-hidden="true" size={16} />
              Refresh
            </button>
            <button
              className="inline-flex h-10 items-center gap-2 rounded-md bg-red-700 px-3 text-sm font-medium text-white shadow-sm hover:bg-red-800 disabled:bg-stone-300"
              disabled={loading}
              onClick={clearLogs}
              type="button"
            >
              <Trash2 aria-hidden="true" size={16} />
              Clear Logs
            </button>
          </div>
        </header>

        {message ? <p className="mb-4 rounded-md bg-white px-3 py-2 text-sm text-stone-700 shadow-sm">{message}</p> : null}

        <div className="overflow-hidden rounded-lg border border-stone-200 bg-white shadow-soft">
          <div className="grid grid-cols-[90px_1fr_140px_180px] gap-4 border-b border-stone-200 px-4 py-3 text-xs font-semibold uppercase tracking-wide text-stone-500">
            <span>ID</span>
            <span>User</span>
            <span>City</span>
            <span>Created</span>
          </div>
          {logs.length === 0 ? (
            <div className="px-4 py-10 text-center text-sm text-stone-500">{loading ? "Loading..." : "No logs yet."}</div>
          ) : (
            <div className="divide-y divide-stone-200">
              {logs.map((log) => (
                <article className="px-4 py-4" key={log.id}>
                  <div className="grid gap-3 text-sm sm:grid-cols-[90px_1fr_140px_180px]">
                    <span className="font-medium text-ink">#{log.id}</span>
                    <span className="text-stone-700">{log.user_email ?? "anonymous"}</span>
                    <span className="text-stone-700">{log.city_name}</span>
                    <span className="text-stone-500">{new Date(log.created_at).toLocaleString()}</span>
                  </div>
                  <div className="mt-3 grid gap-3 lg:grid-cols-2">
                    <div className="rounded-md bg-stone-50 p-3">
                      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">Prompt</h2>
                      <pre className="max-h-56 overflow-auto whitespace-pre-wrap text-xs leading-5 text-stone-700">{log.prompt_text}</pre>
                    </div>
                    <div className="rounded-md bg-stone-50 p-3">
                      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wide text-stone-500">Response</h2>
                      <pre className="max-h-56 overflow-auto whitespace-pre-wrap text-xs leading-5 text-stone-700">{log.ai_response}</pre>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

