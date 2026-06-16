# MAS Digital — Revamped

A clean-room rebuild of the MAS Digital marketing system, built to the **lean agency-tool**
target defined in [`docs/ARCHITECTURE_REVIEW.md`](docs/ARCHITECTURE_REVIEW.md). This repo
exists to keep the genuinely good engine (LLM gateway, tools layer, eval gate, learning loop,
app-layer authz) and **leave behind the self-serve-SaaS scaffolding** the product never used.

> **Status:** foundation only. The engine is being ported in from the legacy repo per
> [`PORTING_PLAN.md`](PORTING_PLAN.md). Nothing here runs end-to-end yet — and this README
> will say so honestly until it does. No feature is documented as "shipped" before it is.

## Thesis (the one decision the build must agree with)

- **Agency tool, multi-client.** You onboard and trust each client; clients do **not** self-serve.
- **Scale:** ≤ ~10 brands/clients, 1–3 operators. Human-paced, low concurrency.
- **`Brand` is the tenancy unit.** No `Tenant`/tier/billing layer above it.
- **App-layer authorization is the real boundary** (`auth.ts` helpers + `brandId` scoping),
  not Postgres RLS. If RLS is ever added, it is belt-and-suspenders with a real cross-brand
  leak test — never a third, inert copy.

## Non-negotiables (trust-first — these are why the legacy build felt unsound)

1. **Honest instruments.** Cost is written to the database the dashboard reads, accumulates
   onto every run, and a real (not `print()`) kill-switch aborts a run that breaches budget.
2. **One source of truth per concern.** One pipeline representation, one cost ledger, one
   credential door, one brand-access predicate. No "second copy" that silently drifts.
3. **Enforced CI.** A rule that isn't enforced by a check is deleted, not faked with `|| true`.
4. **Durable runtime.** Long jobs run on a durable queue and survive a restart — no
   fire-and-forget that orphans a run as permanently `RUNNING`.
5. **Storage discipline.** Commit early and often; a pre-push hook refuses uncommitted
   schema/migrations. (This repo should ultimately live off OneDrive — see review §6 Phase 0.)

## Independence (no parent-directory dependencies)

This project is fully self-contained:
- Its **own `.env`** at the repo root — never `../.env`.
- Its **own** `package.json` / `requirements.txt` / `node_modules` / `.venv`.
- Its **own** git history and remote.
- It can be moved or zipped and still build. The only external dependencies are *services*
  (Supabase, Anthropic, etc.), configured via this repo's `.env`.

It reuses the **clean Supabase project provisioned 2026-06-14** (`joieivimjvfnjkepcjbe`,
eu-west-1) as its data layer — that DB is fresh and correctly bootstrapped, so there's nothing
to redo there. Copy `.env.example` to `.env` and fill it in (or carry over the working values).

## Layout (grows as the engine is ported — no empty cargo-cult dirs)

```
.
├─ docs/ARCHITECTURE_REVIEW.md   # founding verdict + remediation plan
├─ PORTING_PLAN.md               # what to port, what to drop, in what order
├─ .githooks/pre-push            # uncommitted-migration guard
├─ .github/workflows/ci.yml      # gateway-enforcement + doc/route parity (grows with code)
└─ .env.example                  # self-contained config template
```
