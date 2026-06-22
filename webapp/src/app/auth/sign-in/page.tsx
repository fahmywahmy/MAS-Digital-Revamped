"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export default function SignIn() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setErr(null);
    const supabase = createSupabaseBrowserClient();
    const { error } = await supabase.auth.signInWithPassword({ email, password });
    setLoading(false);
    if (error) {
      setErr(error.message);
      return;
    }
    try {
      await fetch("/api/auth/ensure-user", { method: "POST" });
    } catch {
      /* non-fatal */
    }
    router.push("/");
    router.refresh();
  }

  return (
    <main className="min-h-screen grid place-items-center px-4">
      <div className="w-full max-w-sm rounded-lg border border-hairline bg-panel p-6">
        <div className="flex items-center gap-2 mb-5">
          <span className="size-2.5 rounded-full bg-brand" aria-hidden />
          <span className="font-semibold tracking-tight text-ink">MAS Console</span>
        </div>
        <h1 className="text-lg font-semibold text-ink">Sign in</h1>
        <p className="text-sm text-subtle mt-1">Allowlisted operator emails only.</p>
        <form onSubmit={onSubmit} className="mt-5 flex flex-col gap-3">
          <input
            type="email"
            placeholder="you@example.com"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
            className="rounded-md border border-hairline bg-canvas px-3 py-2 text-sm text-ink placeholder:text-faint focus:border-brand"
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
            className="rounded-md border border-hairline bg-canvas px-3 py-2 text-sm text-ink placeholder:text-faint focus:border-brand"
          />
          {err && <p className="text-sm text-danger">{err}</p>}
          <button
            disabled={loading}
            className="mt-1 rounded-md bg-brand px-3 py-2 text-sm font-medium text-brand-ink transition-colors hover:bg-brand-hover disabled:opacity-50"
          >
            {loading ? "…" : "Sign in"}
          </button>
        </form>
        <p className="text-xs text-faint mt-4">
          No password yet? Set one in Supabase → Authentication → Users.
        </p>
      </div>
    </main>
  );
}
