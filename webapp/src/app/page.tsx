import Link from "next/link";
import { getCurrentUser, isEmailAllowed } from "@/lib/auth";
import { prisma } from "@/lib/prisma";

export const dynamic = "force-dynamic";

type Stats =
  | { ok: true; brands: number; users: number; brandList: { id: string; name: string; slug: string; vertical: string }[] }
  | { ok: false; error: string };

async function getStats(): Promise<Stats> {
  try {
    const [brands, users, brandList] = await Promise.all([
      prisma.brand.count(),
      prisma.user.count(),
      prisma.brand.findMany({
        orderBy: { createdAt: "asc" },
        take: 50,
        select: { id: true, name: true, slug: true, vertical: true },
      }),
    ]);
    return { ok: true, brands, users, brandList };
  } catch (e) {
    return { ok: false, error: (e as Error).message.split("\n")[0] };
  }
}

export default async function Home() {
  const user = await getCurrentUser();
  const stats = await getStats();
  const allowed = user && isEmailAllowed(user.email);

  return (
    <main className="wrap">
      <h1>MAS Digital <span className="dim">Revamped</span></h1>

      {!user && (
        <>
          <p className="dim">Operator console — sign in to continue.</p>
          <Link className="btn" href="/auth/sign-in">Sign in</Link>
        </>
      )}

      {user && !allowed && (
        <p className="err">{user.email} is not on the operator allowlist.</p>
      )}

      {allowed && (
        <>
          <p className="dim">Signed in as {user!.email}</p>
          <section className="card">
            <h2>Brands {stats.ok ? `(${stats.brands})` : ""}</h2>
            {stats.ok && stats.brandList.length === 0 && (
              <p className="dim small">No brands yet — seed one once the onboarding tool is ported.</p>
            )}
            {stats.ok &&
              stats.brandList.map((b) => (
                <div key={b.id} className="row">
                  <strong>{b.name}</strong> <span className="dim">/{b.slug} · {b.vertical}</span>
                </div>
              ))}
            {!stats.ok && <p className="err small">{stats.error}</p>}
          </section>
        </>
      )}

      <section className="card">
        <h2>System</h2>
        <div className="row">
          Database:{" "}
          {stats.ok ? <span className="ok">connected</span> : <span className="err">unreachable</span>}
        </div>
        {stats.ok && <div className="row dim small">brands={stats.brands} · users={stats.users}</div>}
        <div className="row dim small">Foundation build — engine ports next (see PORTING_PLAN.md).</div>
      </section>
    </main>
  );
}
