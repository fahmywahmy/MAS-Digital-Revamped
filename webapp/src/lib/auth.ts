import { prisma } from "@/lib/prisma";
import { createSupabaseServerClient } from "@/lib/supabase/server";

/** Current authenticated Supabase user, or null. Server-only. */
export async function getCurrentUser(): Promise<{ id: string; email: string | null } | null> {
  try {
    const supabase = await createSupabaseServerClient();
    const {
      data: { user },
    } = await supabase.auth.getUser();
    if (!user) return null;
    return { id: user.id, email: user.email ?? null };
  } catch {
    return null;
  }
}

/** Comma-separated operator allowlist from env (fail-closed if unset). */
export function getAllowlist(): string[] {
  return (process.env.DASHBOARD_ALLOWLIST_EMAILS || "")
    .split(",")
    .map((s) => s.trim().toLowerCase())
    .filter(Boolean);
}

export function isEmailAllowed(email?: string | null): boolean {
  if (!email) return false;
  const list = getAllowlist();
  return list.length > 0 && list.includes(email.toLowerCase());
}

/** First-touch: ensure an app `User` row exists for this Supabase auth user. */
export async function ensureUserRow(p: { userId: string; email: string; name?: string | null }): Promise<void> {
  await prisma.user.upsert({
    where: { id: p.userId },
    update: { email: p.email, name: p.name ?? null },
    create: { id: p.userId, email: p.email, name: p.name ?? null },
  });
}
