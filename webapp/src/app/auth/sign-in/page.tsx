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
    // Mirror the User row into the app DB, then go home.
    try {
      await fetch("/api/auth/ensure-user", { method: "POST" });
    } catch {
      /* non-fatal */
    }
    router.push("/");
    router.refresh();
  }

  return (
    <main className="wrap">
      <div className="card" style={{ maxWidth: 380 }}>
        <h1>Sign in</h1>
        <p className="dim small">Operator console — allowlisted emails only.</p>
        <form onSubmit={onSubmit} className="form">
          <input
            type="email"
            placeholder="you@example.com"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            autoComplete="email"
          />
          <input
            type="password"
            placeholder="Password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
          {err && <p className="err small">{err}</p>}
          <button disabled={loading}>{loading ? "…" : "Sign in"}</button>
        </form>
        <p className="dim small" style={{ marginTop: "1rem" }}>
          No password yet? Set one in Supabase → Authentication → Users.
        </p>
      </div>
    </main>
  );
}
