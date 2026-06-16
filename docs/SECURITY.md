# Security — MAS Digital Revamped

> **Partial — describes only what's decided/built.** Full doc lands with the webapp/authz
> port. Per `CLAUDE.md §2.5` it states only what is true.

**Model (decided):**
- **Auth:** Supabase Auth; `User.id` mirrors `auth.uid()`. An **email allowlist** gates
  access; a `User` row is created first-touch on allowlisted sign-in.
- **Tenant isolation:** **app-layer `brandId` scoping is the boundary** — one shared
  brand-access predicate, enforced in every list/mutation path. **No Postgres RLS
  enforcement** (the legacy RLS was inert: the owner DB role bypassed it). If RLS is
  added later it's belt-and-suspenders, gated by a real cross-brand leak test.
- **Secrets:** one credential door (`get_credential()`), env-backed; `.env` is the
  repo-root file, gitignored, never committed, never `../.env`.

**Not yet built:** the authz helpers, the leak test, rate limiting, CSRF — ported with
the webapp. See [`ARCHITECTURE.md`](ARCHITECTURE.md) → "Security & tenancy" and
[`../PORTING_PLAN.md`](../PORTING_PLAN.md).
