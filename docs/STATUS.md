# Build Status — MAS Digital Revamped

> **Point-in-time snapshot — 2026-06-21, at commit `b0c10eb`.** This is a state
> report, not a contract. It *will* drift; re-derive it from the code and
> `PORTING_PLAN.md` rather than trusting it after later commits. Status reflects
> what is actually built and verified as of this commit — no forward claims.

Legend: ✅ complete & verified · 🟡 built but unverified / unproven path ·
🟠 partial · 🔲 missing

---

## 1. System intent

A **clean-room rebuild** of the legacy `MAS-Digital-System` as a lean **agency
tool**, not a SaaS platform. Defining constraints (from `CLAUDE.md`):

- **Who it's for:** 1–3 operators running ~10 trusted, manually-onboarded client
  **brands**. No self-serve, no tiers / billing / onboarding layer.
- **Tenancy:** `Brand` is the unit. **App-layer `brandId` scoping is the security
  boundary** — not Postgres RLS.
- **The whole point is honest instruments:** a real cost ledger the dashboard
  reads, a real kill-switch, durable runs that survive restarts, one source of
  truth per concern, CI that actually blocks, and docs that describe only what
  exists. The legacy system's #1 failure was fiction — dashboards and "shipped"
  claims describing things that didn't exist; this rebuild exists to escape that.

**Functional arc it must deliver:** take a brand + a trigger → run a content
pipeline (**trends → strategy → creative → eval gate → publish**), plus adjacent
verticals (SEO/GEO, paid, community, analytics, a learning loop), all
brand-scoped, cost-tracked, quality-gated, and operable from a console.

---

## 2. Module status

### Foundation & trust enforcement

| # | Module | Status | Notes |
|---|---|---|---|
| 0.1 | Repo scaffold, `.gitattributes`, repo-root `.env` door | ✅ | |
| 0.2 | Git hooks (pre-push schema guard) | ✅ | |
| 0.3 | CI guards (gateway-door · no `../.env` · no `\|\|true` · pipeline-drift) | ✅ | 4 guards, all blocking |
| 0.4 | Founding docs (CLAUDE / ARCHITECTURE / PORTING_PLAN / SETUP + honest mirror stubs) | ✅ | |

### Data

| # | Module | Status | Notes |
|---|---|---|---|
| 1.1 | Prisma schema (35 tables, 25 enums), migration chain, Supabase, pgvector col + match fn | ✅ | DB reachable, schema applied |
| 1.2 | DB verify / reset scripts | ✅ | |

### Engine core

| # | Module | Status | Notes |
|---|---|---|---|
| 2.1 | LLM gateway — single Anthropic door, structured outputs | ✅ | `thinking`/`effort` params wired but **unexercised** (🟡) |
| 2.2 | Cost ledger **write** — CostLog + AgentRun accumulation + real kill-switch | ✅ | proven; uses `DIRECT_URL` session conns (fine at this scale) |
| 2.3 | Credential door (`get_credential`) + model/pricing registry | ✅ | prices cached 2026-06 |

### Pipeline

| # | Module | Status | Notes |
|---|---|---|---|
| 3.1 | Manifest representation + loader + drift guard (one source of truth) | ✅ | |
| 3.2 | Runner — **synchronous** | ✅ | |
| 3.3 | Content vertical steps (trends / strategy / creative) | ✅ | proven end-to-end, $0.087 real cost |
| 3.4 | Eval gate (≥18/25 floor) | 🟡 | **pass** path proven; **block** path implemented but never hit live; 25/25 score hints reviewer leniency — rubric needs calibration review |
| 3.5 | Artifact persistence (TrendScan → … → ContentPiece + ContentCopy) | ✅ | |
| 3.6 | **Durable queue** (Procrastinate · `deferJob` · `pg_notify` · worker · restart-survival) | 🔲 | **the other half of §D4; a `CLAUDE.md §2.4` non-negotiable** |

### Other verticals — *schema tables exist; tool code does not*

| # | Module | Status |
|---|---|---|
| 4.1 | Research depth (beyond trends) | 🔲 |
| 4.2 | SEO / GEO (`GeoAudit`, `LLMCitation`) | 🔲 |
| 4.3 | Paid / SEM (`Campaign`, `AdCreative`, …) | 🔲 |
| 4.4 | Community / interactions + approved replies | 🔲 |
| 4.5 | Reviews / GBP | 🔲 |
| 4.6 | Analytics snapshots | 🔲 |
| 4.7 | Media generation (image / video / audio → `MediaAsset`) | 🔲 |
| 4.8 | Publishing (`PublishJob`, multi-channel) | 🔲 |

### Learning loop

| # | Module | Status | Notes |
|---|---|---|---|
| 5.1 | Brand-voice regen + `embed.py` / `retrieve.py` over pgvector + circuit-breaker | 🔲 | pgvector column exists, no code |

### Control plane (webapp)

| # | Module | Status | Notes |
|---|---|---|---|
| 6.1 | Auth — Supabase, allowlist, ensure-user, session middleware | 🟡 | code present, **never run / verified** |
| 6.2 | Landing page (brand list + DB-status) | 🟡 | built, unverified |
| 6.3 | App-layer authz — one shared **brand-access predicate** + cross-brand **leak test** | 🟠 | user/allowlist helpers exist; the brand predicate + leak test are missing |
| 6.4 | Operator **console** — list / run / view runs, trigger pipeline, `/insights` hub | 🔲 | missing |
| 6.5 | **`/api/costs`** read endpoint (the UI that reads the ledger) | 🔲 | missing — the ledger has no reader yet |
| 6.6 | Launcher bats + splash | ✅ | prints "webapp not found" until console lands |

### Quality

| # | Module | Status | Notes |
|---|---|---|---|
| 7.1 | Automated tests beyond proof scripts (pytest, webapp build / typecheck in CI) | 🔲 | only the drift guard runs in CI; no unit tests |

---

## 3. Summary

The **spine is built and proven** end-to-end:

```
data layer → LLM gateway → cost ledger → manifest pipeline → eval gate → persisted artifact (+ real cost)
```

What remains splits into three buckets:

- **Durability** — 3.6 (Procrastinate). A non-negotiable; runs are synchronous today.
- **Visibility** — 6.3–6.5 (console + `/api/costs`). The ledger is written but **nothing reads it yet**.
- **Breadth** — 4.x verticals and 5.1 learning loop (schema exists, no tool code).

**Needs-review** items: the unverified webapp (6.1–6.2) and the eval-gate
calibration (3.4).

---

## 4. Recommended next step

**Durable queue next, with the Supabase change dry-run for approval first.**

- It is a **hard non-negotiable** (`CLAUDE.md §2.4`) and it **completes §D4**.
  Until a restart can't orphan a run as permanently `RUNNING`, the spine isn't
  trustworthy — which is the whole thesis.
- It is **small and contained** relative to the console, verticals, and learning
  loop.
- **The flag:** Procrastinate stores its job state **in the same Supabase
  Postgres** (that's what makes jobs survive a restart), so it adds its own
  tables/functions in their own namespace. It does **not** touch the Prisma
  tables or any data, and it is reversible — but it is a change to the live DB,
  so the schema SQL should be shown for approval before applying (the "dry-run").

**Honest counter-argument:** the cost ledger's entire purpose is "the table the
UI reads," and **there is no UI reading it yet** (6.5). If *seeing the system
work* matters more right now than restart-survival, build the console +
`/api/costs` (6.4–6.5) instead — that also forces verification of the webapp
(6.1–6.2).

Both are correct. The lean is durability because it's the non-negotiable and it's
cheap; the alternative is console-first for visibility.
