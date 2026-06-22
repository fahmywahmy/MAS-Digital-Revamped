import Link from "next/link";
import { getCurrentUser, isEmailAllowed } from "@/lib/auth";
import { prisma } from "@/lib/prisma";
import { Shell } from "@/components/shell";

export const dynamic = "force-dynamic";

type Stats =
  | { ok: true; brands: number; users: number; runs: number; brandList: { id: string; name: string; slug: string; vertical: string }[] }
  | { ok: false; error: string };

async function getStats(): Promise<Stats> {
  try {
    const [brands, users, runs, brandList] = await Promise.all([
      prisma.brand.count(),
      prisma.user.count(),
      prisma.agentRun.count(),
      prisma.brand.findMany({
        orderBy: { createdAt: "asc" },
        take: 50,
        select: { id: true, name: true, slug: true, vertical: true },
      }),
    ]);
    return { ok: true, brands, users, runs, brandList };
  } catch (e) {
    return { ok: false, error: (e as Error).message.split("\n")[0] };
  }
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-hairline bg-panel px-4 py-3">
      <div className="text-2xl font-semibold text-ink tabular">{value}</div>
      <div className="text-xs text-subtle mt-0.5">{label}</div>
    </div>
  );
}

export default async function Home() {
  const user = await getCurrentUser();
  const allowed = user && isEmailAllowed(user.email);

  // Unauthed / not-allowlisted: a focused gate, no console chrome.
  if (!allowed) {
    return (
      <main className="min-h-screen grid place-items-center px-4">
        <div className="w-full max-w-sm rounded-lg border border-hairline bg-panel p-6 text-center">
          <div className="flex items-center justify-center gap-2 mb-4">
            <span className="size-2.5 rounded-full bg-brand" aria-hidden />
            <span className="font-semibold tracking-tight text-ink">MAS Console</span>
          </div>
          {!user ? (
            <>
              <p className="text-sm text-subtle">Operator console — sign in to continue.</p>
              <Link
                href="/auth/sign-in"
                className="mt-4 inline-block rounded-md bg-brand px-4 py-2 text-sm font-medium text-brand-ink hover:bg-brand-hover"
              >
                Sign in
              </Link>
            </>
          ) : (
            <p className="text-sm text-danger">{user.email} is not on the operator allowlist.</p>
          )}
        </div>
      </main>
    );
  }

  const stats = await getStats();

  return (
    <Shell active="overview" title="Overview" email={user!.email}>
      <div className="space-y-6">
        <section>
          <h2 className="text-sm font-medium text-subtle mb-3">At a glance</h2>
          {stats.ok ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              <Stat label="Brands" value={stats.brands} />
              <Stat label="Operators" value={stats.users} />
              <Stat label="Runs" value={stats.runs} />
            </div>
          ) : (
            <p className="text-sm text-danger">Database unreachable: {stats.error}</p>
          )}
        </section>

        <section>
          <h2 className="text-sm font-medium text-subtle mb-3">Brands</h2>
          <div className="rounded-lg border border-hairline bg-panel divide-y divide-[color:var(--color-hairline)]">
            {stats.ok && stats.brandList.length === 0 && (
              <p className="px-4 py-6 text-sm text-faint">
                No brands yet. Brand management lands in this console shortly (P3).
              </p>
            )}
            {stats.ok &&
              stats.brandList.map((b) => (
                <div key={b.id} className="flex items-center gap-3 px-4 py-2.5">
                  <span className="text-sm text-ink font-medium">{b.name}</span>
                  <span className="text-xs text-faint tabular">/{b.slug}</span>
                  <span className="ml-auto text-xs text-subtle">{b.vertical}</span>
                </div>
              ))}
          </div>
        </section>

        <section>
          <div className="flex items-center gap-2 rounded-lg border border-hairline bg-panel px-4 py-3">
            <span className="size-2 rounded-full bg-success" aria-hidden />
            <span className="text-sm text-subtle">
              Engine online · durable queue + cost ledger live ·{" "}
              <span className="text-faint">Runs &amp; Costs views are next in P2.</span>
            </span>
          </div>
        </section>
      </div>
    </Shell>
  );
}
