# Architecture — MAS Digital Revamped (TARGET)

> **Status: target design, not as-built.** This is the system we are *building*,
> calibrated to the agency-tool thesis. What exists today is marked ✅ BUILT;
> everything else is 🔲 PLANNED (order in [`../PORTING_PLAN.md`](../PORTING_PLAN.md)).
> Per `CLAUDE.md §2.5` this is a contract, not a description of running code — when a
> component ships, its real behavior moves into its own (mirror) doc.

## Build status

| Component | Status |
|---|---|
| Data layer — Prisma schema + Supabase + migration chain | ✅ BUILT |
| Webapp launcher (`Launch/Stop Webapp.bat` + splash) | ✅ BUILT (waiting on the webapp) |
| LLM gateway — `claude_client` + Postgres cost ledger | ✅ BUILT |
| Pipeline runner — one YAML source of truth (drift-guarded) | ✅ BUILT |
| Content vertical — trends → strategy → creative → eval gate | ✅ BUILT |
| Eval gate (≥ quality floor before publish) | ✅ BUILT |
| Tools — remaining verticals (seo / paid / community) | 🔲 PLANNED |
| Durable job queue — Procrastinate (`deferJob` + `pg_notify`) | 🔲 PLANNED (next) |
| Webapp / operator console | 🔲 PLANNED |
| Learning loop — brand-voice regen + pgvector retrieval | 🔲 PLANNED |

## The shape (lean version)

One operator, a handful of trusted clients. Optimize for *shipping and running*, not
for platform scale:

- **One execution substrate** — a single long-lived Node host running the webapp +
  Python toolchain. Every background job (incl. the content pipeline) goes on
  **Procrastinate** via one typed `deferJob()` helper that emits `pg_notify`. The
  webapp is a **control/read plane**: enqueue + poll `AgentRun`. Runs survive restarts.
- **One pipeline representation** — YAML manifests are the single source of truth.
  No parallel hardcoded orchestrator, no "documentary" copy. A drift test asserts every
  workflow names its backing manifest.
- **One cost ledger** — `cost_logger` writes Postgres `CostLog` as primary; `/api/costs`
  reads what the tools write; run totals accumulate real spend; a real pre-call
  kill-switch aborts a run over budget.
- **One credential door** — everything reads `get_credential()` (env-backed).
- **Authz = app layer only** — one shared brand-access predicate; one end-to-end
  cross-brand leak test is worth more than the whole legacy RLS subsystem.

## Data model (✅ BUILT)

`prisma/schema.prisma` is the source of truth — 35 tables, 25 enums.
- **`Brand` is the tenancy unit** (`Brand.userId` owner + `BrandMember` for shared
  operator access). No `Tenant`/tier layer.
- Brand-scoped content lifecycle: `TrendScan → StrategyBrief → CreativeBrief →
  ContentPiece → ContentCopy/MediaAsset → PublishJob`, plus paid (`Campaign…`),
  conversion, reviews/GBP, analytics, agent/cost logs.
- **pgvector** on `VectorMemory.embedding` (added by `0001_pgvector`, not in the Prisma
  schema — vector ops go through psycopg in the Python tools).
- Migration chain is self-contained & replayable: `0000_init` then `0001_pgvector`
  (extension/column ordered *after* the table — the legacy bug, fixed).

## Pipeline (✅ BUILT — content vertical)

One YAML manifest is the single source of truth (`pipelines/content.yaml`). The runner
(`tools/pipeline/runner.py`) walks the manifest's steps — there is **no** parallel
hardcoded orchestrator — resolving each through one step registry. The CI guard
`scripts/check-pipeline-drift.py` asserts every manifest step resolves *and* the runner
names no step literals.

The content vertical runs **trends → strategy → creative → eval gate**: each step calls
the gateway with the run's id (so real cost accrues), uses structured outputs for
schema-valid JSON, and persists its artifact (`TrendScan → StrategyBrief → CreativeBrief
→ ContentPiece + ContentCopy`). The **eval gate** is a hard floor: a score ≥ the
manifest's `min_score` (18/25) marks the `ContentPiece` publishable (`IN_REVIEW`); below
it the piece is `FAILED` and cannot publish. A step error (incl. the kill-switch
tripping) fails the whole `AgentRun`. `scripts/run-content-pipeline.py` proves it
end-to-end for a disposable brand.

## Execution & runtime (partially built)

The pipeline runs **synchronously** today (the runner executes in-process). The next
step is durability: long/expensive runs deferred to **Procrastinate** via one typed
`deferJob()` helper so a restart can't orphan a run as permanently `RUNNING`
(🔲 PLANNED). The webapp (Next.js) will deploy as the control plane on the same host;
artifacts persist to storage, not ephemeral local disk.

## Cost & observability (✅ BUILT — fix-on-port)

The legacy's headline `$80/mo` control was fiction (the DB table the UI read was never
written). Here the cost ledger is wired correctly and **verified end-to-end**:

- **One door to Anthropic** — `tools/utils/claude_client.py` is the only file that
  imports `anthropic` (CI-enforced). Everything calls `complete()`.
- **DB-primary ledger** — every call writes a `CostLog` row (the table `/api/costs`
  will read), priced from the one model table `tools/utils/registry.py` across all four
  token buckets (input / output / cache-read / cache-write).
- **Run-total accumulation** — per-call spend accumulates onto the owning `AgentRun`
  (`costUsd` / `tokensUsed`) in the same transaction as the `CostLog` write, so the
  ledger and the run total cannot drift.
- **Real kill-switch** — `cost_logger.check_budget()` runs **before** each call and
  raises `BudgetExceededError` to abort a run already over budget. Not a `print()`.

`python scripts/prove-gateway.py` proves all four with real (sub-cent) calls: non-zero
`CostLog` rows, an accumulating `AgentRun` total, and a third call aborted pre-spend by
the kill-switch — then it deletes the disposable rows it created.

## Security & tenancy (partially built)

- **Auth:** Supabase Auth, `User.id` mirrors `auth.uid()`; an email allowlist gates
  access; a `User` row is created first-touch on allowlisted sign-in.
- **Isolation:** app-layer `brandId` scoping is the boundary. **No Postgres RLS
  enforcement** (the legacy RLS was inert — owner role bypassed it). If added later,
  it's belt-and-suspenders with a real leak test.

## Deliberately NOT built

Self-serve signup · `Tenant`/tier/billing · RLS-as-enforcement · multiple pipeline
representations · an AI-aggregator framework (one direct path per provider) ·
platform-grade multi-touch attribution (last-click until volume demands more) ·
enterprise governance ceremony.
