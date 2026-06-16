# Architecture Review & Remediation Plan

> **Date:** 2026-06-16
> **Reviewer:** External second opinion (grounded code audit — 10 dimensions, claims re-verified against the source tree)
> **Status:** Verdict + starting plan. Point-in-time snapshot; revisit after Phase 1.

---

## 0. Context this verdict is calibrated to

The recommendation below is **not generic** — it is tuned to the operator's stated intent, captured 2026-06-16:

| Question | Answer |
|---|---|
| **Who is it for / how far** | **Agency, multi-client** — run marketing for multiple external clients from one console; clients do **not** log in themselves. |
| **Scale (6–12 mo)** | **≤ ~10 brands/clients, 1–3 operators.** Human-paced, low concurrency. |
| **Where it hurts** | Too complex to operate · dashboard UX doesn't fit · can't tell if it works end-to-end · over-built for actual needs · **gap between claimed scope and what's actually delivered.** |
| **Appetite for change** | **No attachment — wants the honest call**, rip-and-replace where warranted. |

The single most important consequence: this is an **agency tool, not a self-serve SaaS**. Every "tenant" is a client *you* onboard and trust at the database level. That fact alone reclassifies a large fraction of the current build from "smart future-proofing" to "dead weight."

---

## 1. The verdict (TL;DR)

**Keep the engine. Demolish the showroom around it. Fix the instruments first.**

- **Would I build it this way?** No.
- **Would I rewrite it from scratch?** Also no — that throws away the genuinely good 60%.
- **The move:** keep ~60%, delete ~30% of SaaS scaffolding, and **repair the trust layer before anything else** — because the broken trust layer is the actual reason the architecture *feels* unsound and can't be judged from the inside.

One-sentence diagnosis: **a real, well-built marketing engine wrapped in the scaffolding of a multi-tenant SaaS company that doesn't exist — and the scaffolding is mostly hollow.** This is not an architecture problem so much as a **truth-in-reporting problem wearing an architecture costume**, which is exactly why it was so hard to point at.

---

## 2. The core finding — claimed scope ≫ delivered scope

This was the operator's sharpest instinct, and it is the audit's strongest finding. Each row below was **re-verified directly against the source tree** (see Appendix A):

| Claimed | Reality |
|---|---|
| **"$80/mo cost control" is the headline KPI** | Dashboard reads the `CostLog` table; **nothing writes it** (`costLog.create`: **0 callers**). Every `AgentRun` persists `costUsd: 0`. The "BUDGET EXCEEDED — PAUSED" guard is a `print()`, not an action. **The number you'd manage the system by is fiction.** |
| **"Defense-in-depth RLS — even a wrong WHERE clause is filtered to your brands"** | RLS migrations exist, but their session variable is set only by `withUserContext()`, which has **zero real callers**. And the app connects as the Postgres **owner role, which bypasses RLS unconditionally**. **The backstop does not exist** — and naively "turning it on" would return empty result sets everywhere and break the app (the two layers were never co-tested). |
| **Docs describe a working console** | `DASHBOARD_GUIDE` documents `/dashboard/whatsapp`; `PRODUCT.md` lists `/dashboard/insights` (the *primary* "what changed this week" page) as shipped. **Neither directory exists.** `SECURITY.md` describes middleware that was never built. |
| **`CONSTITUTION.md`: "a rule not enforced by a test is a wish… mechanically enforced"** | **11 `\|\| true` guards** in `constitution.yml` make 8 of 9 checks report green **even when they fail**. The governance meant to prevent self-deception is itself unenforced. |
| Ledgers: "38 models / 89 tools" | Reality: **39 models / 178 `.py` files.** Bookkeeping drifted because nothing forces it honest. |

**This is why "you can't tell if it works end-to-end":** the instruments are broken. That is a *fixable defect*, not a vibe — and repairing it is the highest-ROI work in the system.

---

## 3. Root cause — SaaS scaffolding on an agency tool

The recurring pattern across every dimension: **the second copy of things keeps getting built, and the second copy is the hollow one.**

- Two cost ledgers (JSONL written; `CostLog` DB read — but unwritten).
- Two RLS layers (app-layer authz that works; Postgres RLS that's inert).
- Four representations of "a pipeline" (markdown SOP, 43KB hardcoded `pipeline-orchestrator.ts`, declarative `pipelines/*.yaml` whose own header says its args are "documentary", agent persona docs) — with no drift guard, already partially diverged.
- Two tool-resolution systems (the `registry.resolve()` indirection is bypassed — workflows hardcode `python tools/creative/generate_script.py`, the exact coupling the registry claims to prevent).

**The duplication is the disease; the SaaS ambition is the vector.** You keep maintaining and testing scaffolding the product doesn't use — that is the "recon treadmill."

### Dead weight the moment this is *not* a self-serve SaaS

| Built for SaaS | What it actually is for an agency tool | 
|---|---|
| **Postgres RLS** (3 migrations, 27+ tables) | Inert (owner role bypasses; zero context callers). Maintenance + a lying doc + outage risk if "fixed." |
| **`Tenant` / `TenantTier` / `TenantOnboardingState` / tier-gate (3 copies)** | A workspace layer above `Brand` — but **`Brand` is already the real tenancy unit.** `tenantId` nullable, backfill unverified, `plan` column dead. |
| **Onboarding wizard + invite skeleton** | Onboarding a client is still a manual `psql INSERT`. Half-built UX that can't onboard anyone. |
| **Per-brand budget overrides + BYOK credential registry** | `cost_logger` only reads the flat env var; DB lookup "not yet wired." |
| **Full paid-media normalization** (Campaign→AdSet→Ad→AdCreative, 6-value multi-touch attribution) | Platform-grade depth ahead of demonstrated use; last-click already covered. |
| **354-line Constitution + reviewer-subagent ceremony** | Enterprise governance on a bus-factor-1 repo — and mostly unenforced (`\|\| true`). |

---

## 4. What's genuinely good — preserve this, do **not** rewrite it

A teardown must not talk you into burning the 60% that works.

- **`tools/utils/claude_client.py` is the best-engineered thing in the repo** — a single LLM choke point with model routing, correct cache-cost accounting, retry/backoff, cost logging, tracing, brand-context injection. The only flaw is one tool that bypasses it (enforce the choke point in CI).
- **The tools layer (178 files) is cohesive library+CLI code**, not throwaway scripts — pure logic separated from CLI shells, low duplication, real behavioral tests where they exist.
- **The eval gate (≥18/25 before publish)** is a genuine differentiator and is actually wired in.
- **The learning loop** (nightly brand-voice regen from top performers + pgvector few-shot retrieval) — the single most defensible "gets smarter with use" story. Keep it; add a circuit-breaker.
- **App-layer authorization (`auth.ts`)** — consistent `brandId` scoping across 64 route files, a pure testable permission predicate. **This — not RLS — is your real tenant boundary, and it's sound.**
- **The dashboard is a real console**, not a mockup — buttons `spawn()` the Python tools behind auth gates; every empty state prints the exact CLI command to populate it.
- **The honesty culture** — the RLS-loss postmortem named its own cause; the project has cut 14 things to converge. The fix is to make *enforcement* match the honesty already present.

---

## 5. Keep / Fix / Delete — for the agency-tool thesis

| Subsystem | Call |
|---|---|
| Tools layer + `claude_client` gateway | **KEEP** (enforce the gateway in CI) |
| Eval gate, learning loop, app-layer authz | **KEEP** — these are the product |
| Cost tracking (JSONL ↔ `CostLog` seam) | **FIX** — DB is the ledger; wire run totals; real kill-switch |
| Postgres RLS | **DECIDE: wire honestly _or_ delete.** For ≤10 trusted clients, app-layer authz is the boundary — wire RLS only as belt-and-suspenders (least-priv role + Prisma `$extends` + a cross-brand leak test), otherwise delete it and tell the truth in docs |
| `Tenant` / tier / onboarding-wizard | **COLLAPSE** — `Tenant` = client; drop tiers/billing/self-serve |
| 4 pipeline representations | **COLLAPSE to one** (YAML — the one with a real engine) + drift-guard test |
| Execution runtime (in-process Python, fire-and-forget on Vercel) | **FIX** — move the content pipeline onto the durable queue (Procrastinate) you already run |
| Raw-SQL Procrastinate enqueues (×11) | **REFACTOR** — one typed `deferJob()` helper with `pg_notify` |
| Paid-media depth / AI-aggregator framework | **REFACTOR** — keep if paid is live; otherwise collapse to last-click + one direct media path |
| Constitution `\|\| true` ceremony | **REMOVE the guards** — make rules actually block |
| Dashboard IA (34 pages / 10 categories) | **CONSOLIDATE to ~3 hubs** + build the `/insights` page (your actual primary job) |
| Docs (DATA_MODEL / SECURITY / DASHBOARD) | **REGENERATE from code** + route-parity test |
| **Source on OneDrive** | **MOVE OFF — immediately** |

---

## 6. How to start working on it — sequenced plan

**Sequencing principle: trust fixes before feature work.** You cannot judge (or safely change) the architecture while the instruments lie. Phases are ordered by leverage, not by how interesting the work is.

### Phase 0 — Stop the bleeding (do first; ~½–1 day)

> The source tree physically loses work and the loss condition is live right now.

- [ ] **Move the repo off OneDrive** to a plain local path (e.g. `C:\dev\MAS-Digital-System`) with a GitHub remote.
- [ ] **Commit the current dirty tree** (the `directUrl` / `schema.prisma` change) so it is not lost.
- [ ] **Add a pre-push hook** that refuses a push when `schema.prisma` or `prisma/migrations/**` have uncommitted changes.
- [ ] **Enforce the LLM gateway in CI** — fail the build if any file under `tools/` imports `anthropic` directly instead of going through `claude_client.py` (one tool currently bypasses it).

**Acceptance:** repo at a non-synced path with a remote; pushing with an uncommitted migration is blocked; a direct `anthropic.Anthropic()` import fails CI.
**Why first:** OneDrive dehydration already silently destroyed the `0099` RLS migration (≈4 weeks undetected). Until this is fixed, **no "shipped" claim is trustworthy.**

### Phase 1 — Make the instruments honest (~3–5 days)

> So "done" means done and you can trust what the dashboard shows.

- [ ] **Unify the cost ledger.** `cost_logger` writes to Postgres `CostLog` as primary (JSONL becomes an optional debug mirror); `/api/costs` reads what the tools write; pipeline run totals accumulate real per-call spend onto `AgentRun`.
- [ ] **Add a real kill-switch** — check accumulated spend *before* the next Claude call and abort the run (not a `print()`).
- [ ] **Remove the 11 `\|\| true` guards** from `constitution.yml` (or honestly downgrade rules you can't yet enforce). Then fix whatever turns red — that is how you find the *next* hidden gap.
- [ ] **Add a doc/route parity test** — every route named in the docs (and sidebar) must resolve to a real directory. Regenerate `DATA_MODEL.md` / `SECURITY.md` / `DASHBOARD_GUIDE.md` from the code.

**Acceptance:** a real pipeline run shows **non-zero cost** in the dashboard and on its `AgentRun` row; CI **fails** when an assertion fails; the parity test is green and docs match reality.

### Phase 2 — Commit to one thesis & prune (~1–2 weeks)

> Decide it is an **agency tool**, then make the build agree with the thesis.

- [ ] **Decide RLS: wire it honestly _or_ delete it.** Recommended for ≤10 trusted clients: delete the inert RLS subsystem and update `SECURITY.md` to state that **app-layer authz is the boundary** — *or*, if you want belt-and-suspenders, add a least-privilege DB role + a single Prisma `$extends` that injects `app.current_user_id` (not 46 hand-wrapped routes). **Pick one; do not keep a dead third option.**
- [ ] **Add the one test worth more than all of RLS:** seed 2 brands / 2 users, hit every list route, assert **zero cross-brand leakage.**
- [ ] **Collapse the tenancy layer** — keep `Tenant` = client; drop `TenantTier` / tier-gate / billing / self-serve onboarding; make `tenantId` non-null with a verified backfill or remove it.
- [ ] **Consolidate the 3 copies of the brand-access predicate** into one.

**Acceptance:** the cross-brand leak test passes; the `Tenant`/tier scaffolding is either finished or gone (no half-built middle); `SECURITY.md` describes what actually runs.

### Phase 3 — Collapse duplication & harden the runtime (~1–2 weeks)

- [ ] **One pipeline representation.** Make `pipelines/*.yaml` the single source of truth; delete the hardcoded orchestrator step list (or generate it); add a drift-guard test asserting every workflow names its backing manifest.
- [ ] **Durability.** Move the content pipeline onto Procrastinate so a restart/deploy can't orphan a run as permanently `RUNNING`.
- [ ] **One typed `deferJob()` helper** with `pg_notify`, replacing the 11 copy-pasted raw-SQL enqueues; **one `BaseAdsClient` + `AdSpendDAO`** replacing the copy-paste ad clients.

**Acceptance:** editing the YAML changes what runs; a worker restart mid-run resumes or fails cleanly (no zombie `RUNNING` rows); no route hand-writes `INSERT INTO procrastinate_jobs`.

### Phase 4 — UX & scope honesty (~1 week)

- [ ] **Consolidate the dashboard IA** from 34 pages / 10 categories to ~3 hubs and **build the `/insights` page** (your stated primary "what changed this week" job).
- [ ] **Reconcile the ledgers** (`super_plan.md`, README counts) with reality — and keep them honest with the Phase 1 parity test.

**Acceptance:** the daily ~6-step operator loop maps to ≤3 hubs; `/insights` exists and renders real artifacts; doc counts match `git`-countable reality.

---

## 7. Start here (first sitting)

If you do nothing else this week, do Phase 0 and the cost-ledger item of Phase 1:

1. Copy the repo to `C:\dev\MAS-Digital-System`, `git init` status check, push to a private GitHub remote.
2. Commit the pending `schema.prisma` change.
3. Add the pre-push hook (uncommitted-migration guard).
4. Wire `cost_logger` → `CostLog` and confirm one run shows real cost in the dashboard.

That sequence converts the system from "I can't tell if it's sound" to "the instruments are honest, now I can judge it" — which is the whole point.

---

## Appendix A — Evidence (independently re-verified 2026-06-16)

| Claim | Check | Result |
|---|---|---|
| Cost table is never written | `grep costLog.create webapp/` | **0 occurrences** |
| RLS context never set | `grep withUserContext webapp/src/` | defined in `prisma.ts:45`, referenced only in its own doc-comment example → **no real callers** |
| Owner role bypasses RLS | `DATABASE_URL` user = `postgres.<ref>` (table owner); Postgres `ENABLE ROW LEVEL SECURITY` does not apply to owners without `FORCE` | **RLS inert at runtime** |
| Constitution unenforced | `grep "\|\| true" .github/workflows/constitution.yml` | **11 occurrences** |
| Documented routes missing | `webapp/src/app/dashboard/{whatsapp,insights,intake,pipelines}/` | **none exist** |
| Ledger drift | models in `schema.prisma` vs docs; `.py` count vs docs | **39 / 178** actual vs **38 / 89** claimed |

## Appendix B — Review method

Grounded audit across 10 dimensions (product/jobs, WAT layering, data model, tenancy/security, dashboard UX, AI orchestration/cost, runtime/queue, integrations, tooling quality, ops/health), each conducted by reading the actual files and reporting strengths / over-engineering / under-engineering / coupling / redesign options, followed by an intent-conditional synthesis. The most consequential claims were re-verified by hand (Appendix A). This is a point-in-time assessment — re-run after Phase 1, when the instruments are trustworthy enough to measure against.
