# Porting Plan — legacy → revamped

Derived from [`docs/ARCHITECTURE_REVIEW.md`](docs/ARCHITECTURE_REVIEW.md) §5–6, calibrated to the
**agency-tool** thesis. Rule of thumb: **port the engine, drop the SaaS scaffolding, and fix the
known bug *as you port it* — never copy a bug across.**

Legacy repo: `../MAS-Digital-System` (read-only source; nothing here imports from it at runtime).

---

## A. PORT (keep — the good ~60%)

- [x] **LLM gateway** — `tools/utils/claude_client.py` (+ `cost_logger.py`, `registry.py`, `config.py`).
      *Fix-on-port done:* cost writes to Postgres `CostLog` as primary (see §C1); the dashboard
      read endpoint `/api/costs` lands with the console slice (§D5).
- [ ] **Tools layer** — `tools/**` (research, creative, seo, paid, utils). Port by vertical slice,
      not all at once (see §D ordering).
- [ ] **Eval gate** — the ≥18/25 rubric harness. Keep as a hard pre-publish floor.
- [ ] **Learning loop** — brand-voice regenerator + `embed.py` + `retrieve.py` over pgvector.
      *Fix-on-port:* add a circuit-breaker so a bad regen can't silently degrade generation.
- [ ] **Data layer** — `webapp/prisma/schema.prisma` + the clean bootstrapped Supabase DB
      (`joieivimjvfnjkepcjbe`). *Fix-on-port:* drop the legacy `plan` column and the dead
      `Tenant`/tier tables (see §B) before first migrate.
- [ ] **App-layer authz** — `webapp/src/lib/auth.ts` helpers. *Fix-on-port:* collapse the 3 copies
      of the brand-access predicate into one shared function.
- [ ] **Dashboard console bones** — the pages that actually `spawn()` tools behind auth gates,
      and the cold-start UX (empty states that print the CLI command). Consolidate IA on the way in.

## B. DROP (leave behind — dead weight for an agency tool)

- [ ] **Postgres RLS subsystem** (migrations 0011/0099/0105 + `withUserContext`). Decide in §C2.
- [ ] **`Tenant` / `TenantTier` / `TenantOnboardingState` / tier-gate** (3 copies). `Brand` is the unit.
- [ ] **Onboarding wizard + invite skeleton** — onboarding is a trusted manual step at this scale.
- [ ] **Per-brand budget overrides + BYOK credential registry** — one env-backed credential door instead.
- [ ] **Platform-grade paid-media depth** — collapse `AdSet`/`Ad`/`AttributionTouch`/multi-touch to
      `Campaign` + `Conversion` last-click unless/until paid volume demands more.
- [ ] **The 4 pipeline representations** — collapse to ONE (YAML) on port (see §C3).
- [ ] **354-line Constitution + reviewer-subagent ceremony** — replace with a handful of *enforced* rules.
- [ ] **Drifted docs** (DASHBOARD_GUIDE/SECURITY/DATA_MODEL describing things that don't exist) —
      regenerate from code, don't port.

## C. FIX-ON-PORT (bake the trust fixes in from day one)

1. [ ] **Cost ledger = Postgres.** `cost_logger` writes `CostLog`; `/api/costs` reads it; run totals
       accumulate real per-call spend onto `AgentRun`; real pre-call kill-switch (not `print()`).
2. [ ] **RLS decision:** for ≤10 trusted clients, ship with **app-layer authz as the boundary** and
       say so in the docs — *or* wire RLS honestly (least-priv DB role + one Prisma `$extends`
       injecting `app.current_user_id` + a cross-brand leak test). Pick one; no inert third copy.
3. [ ] **One pipeline source of truth (YAML)** + a drift-guard test asserting every workflow names its
       backing manifest. Delete the hardcoded orchestrator step list.
4. [ ] **Durable content pipeline** on Procrastinate via one typed `deferJob()` helper with `pg_notify`.
       No fire-and-forget; a restart must not orphan a run.
5. [ ] **One `BaseAdsClient` + `AdSpendDAO`** instead of copy-pasted per-platform clients (if paid ports).
6. [ ] **Doc/route parity test** — every route named in docs/sidebar resolves to a real directory.

## D. Suggested porting order (vertical slices, prove the spine first)

1. [x] **Foundation**: independent repo, hooks, CI stub, env template, founding docs.
2. [x] **Data layer**: port the pruned Prisma schema; point at the existing Supabase; `migrate`.
3. [x] **LLM gateway + cost ledger (fixed)**: `claude_client` writing real cost to `CostLog`;
       `scripts/prove-gateway.py` proves a call logs non-zero spend, accumulates onto the run, and
       the kill-switch aborts a run over budget.
4. [ ] **One end-to-end vertical**: trends → strategy → creative → **eval gate** → persisted artifact,
       run from one YAML manifest on the durable queue. This proves the whole spine on a small surface.
5. [ ] **Console for that slice**: list + run + view, behind app-layer authz, with the `/insights` hub.
6. [ ] **Expand horizontally**: bring remaining tool verticals across, each with its eval + manifest.

## Definition of done for the revamp's first milestone

A single content run, triggered from the console, executes on the durable queue, passes the eval
gate, persists its artifact **and its real cost**, survives a worker restart, and is visible to the
right brand only — with CI green on enforced rules and docs that match what exists. That milestone is
worth more than re-porting the entire surface, because it proves the architecture is *honest*.
