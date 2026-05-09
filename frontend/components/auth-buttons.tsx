"use client";

import { LogIn, LogOut } from "lucide-react";
import { useState } from "react";
import { signIn, signOut, useSession } from "next-auth/react";

export function AuthButtons() {
  const { data: session, status } = useSession();
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  if (status === "loading") {
    return <div className="h-10 w-44 rounded-md bg-stone-200" />;
  }

  if (session?.user) {
    return (
      <div className="flex items-center gap-3">
        <div className="hidden text-right text-sm sm:block">
          <div className="font-medium text-ink">{session.user.name ?? session.user.email}</div>
          <div className="text-stone-500">{session.user.role}</div>
        </div>
        <button
          className="inline-flex h-10 items-center gap-2 rounded-md border border-stone-300 bg-white px-3 text-sm font-medium text-ink shadow-sm hover:bg-stone-50"
          onClick={() => signOut()}
          type="button"
        >
          <LogOut aria-hidden="true" size={16} />
          Sign out
        </button>
      </div>
    );
  }

  const handleLocalLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const result = await signIn("credentials", {
        username,
        password,
        redirect: false,
      });
      if (result?.ok) {
        setShowLoginModal(false);
        setUsername("");
        setPassword("");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <button
          className="inline-flex h-10 items-center gap-2 rounded-md bg-ink px-3 text-sm font-medium text-white shadow-sm hover:bg-stone-800"
          onClick={() => setShowLoginModal(true)}
          type="button"
        >
          <LogIn aria-hidden="true" size={16} />
          Admin
        </button>
        <button
          className="inline-flex h-10 items-center gap-2 rounded-md bg-ink px-3 text-sm font-medium text-white shadow-sm hover:bg-stone-800"
          onClick={() => signIn("google")}
          type="button"
        >
          <LogIn aria-hidden="true" size={16} />
          Google
        </button>
        <button
          className="inline-flex h-10 items-center gap-2 rounded-md border border-stone-300 bg-white px-3 text-sm font-medium text-ink shadow-sm hover:bg-stone-50"
          onClick={() => signIn("facebook")}
          type="button"
        >
          <LogIn aria-hidden="true" size={16} />
          Facebook
        </button>
      </div>

      {showLoginModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-sm rounded-lg bg-white p-6 shadow-lg">
            <h2 className="mb-4 text-lg font-semibold text-ink">Admin Login</h2>
            <form onSubmit={handleLocalLogin} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium text-stone-700">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="mt-1 w-full rounded-md border border-stone-300 px-3 py-2 text-sm shadow-sm focus:border-ink focus:outline-none"
                  placeholder="admin"
                />
              </div>
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-stone-700">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 w-full rounded-md border border-stone-300 px-3 py-2 text-sm shadow-sm focus:border-ink focus:outline-none"
                  placeholder="••••••"
                />
              </div>
              <div className="flex gap-2 pt-2">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="flex-1 rounded-md bg-ink px-3 py-2 text-sm font-medium text-white shadow-sm hover:bg-stone-800 disabled:bg-stone-400"
                >
                  {isLoading ? "Signing in..." : "Sign In"}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowLoginModal(false);
                    setUsername("");
                    setPassword("");
                  }}
                  className="flex-1 rounded-md border border-stone-300 bg-white px-3 py-2 text-sm font-medium text-ink shadow-sm hover:bg-stone-50"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

