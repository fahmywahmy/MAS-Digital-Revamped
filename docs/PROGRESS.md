# PROGRESS.md — Live Resume Ledger

> **The source of truth for "where we are."** The master `/goal` reads this first and
> resumes from the first incomplete task. Updated after every verified sub-phase, with the
> commit that proved it. Status: `[ ]` todo · `[~]` in progress · `[x]` done (+ commit).
>
> Plan: [`MASTERPLAN.md`](MASTERPLAN.md) · Design: [`DESIGN.md`](DESIGN.md).

**Last updated:** 2026-06-21 · **HEAD at update:** `b0c10eb` · **Build spend so far:** ~$0.30 (proofs)

**Decisions locked:** I1 export-boundary · I2 real client (brief pending) · I3 full growth
suite · I4 teal (see MASTERPLAN §2a).
**Awaiting before content-quality phases (P3–P5):** the **brand brief** + spend-cap confirm.
P1 (durable runtime + eval calibration) and P2 (console) are brand-agnostic and can start
immediately on approval.

---

## ✅ P0 — Spine (DONE)
- [x] Foundation, hooks, CI guards — `e9250c2`/`8fd8689`/`f88cc8d`
- [x] Data layer (Prisma schema, migrations, Supabase, pgvector) — `84716ea`
- [x] LLM gateway + cost ledger + kill-switch — `56326a4`
- [x] Manifest pipeline + content vertical + eval gate + drift guard — `b0c10eb`

## P1 — Durable runtime + trustworthy eval  *(branch: feat/p1-durable-runtime)*
- [x] Procrastinate 3.9 installed; runtime module built (`tools/runtime/{app,defer,tasks,worker,recovery,aio,schema_sql}.py`)
- [x] Dedicated `procrastinate` schema generated, approved, **applied to Supabase** + function search_path hardening (footgun closed; Prisma `public` untouched)
- [x] One typed `defer_pipeline()` helper (durable enqueue + idempotent run provisioning, no orphan window)
- [x] Worker (`-m tools.runtime.worker`; async psycopg via SelectorEventLoop) + idempotent task + **self-heal recovery on startup**
- [ ] NSSM service wrappers (webapp + worker) — next (now that the schema is live)
- [x] **Restart-survival proof PASSED** (`scripts/prove-restart-survival.py`): worker killed mid-run → run stays RUNNING (not orphaned) → worker B recovers job [4] → COMPLETED, $0.0943 real cost
- [x] Eval calibration: judge ≠ generator (Sonnet judge vs Opus generator), locked rubric bands, deterministic guards (`tools/pipeline/eval_rubric.py`)
- [x] **FAIL-path + discrimination proof** (`scripts/check-eval-gate.py`): weak blocked (7/25), compliance violation hard-blocked, strong 23/25; live pipeline now scores 22/25 (no more 25/25 rubber-stamp)
- [ ] Human-scored gold set (20–40 real artifacts) + correlation report — needs the real brand + operator (P3 activity)

## P2 — Operator console (UX/UI) — graded against DESIGN.md §5 ten rules
- [ ] Console scaffold: Tailwind v4 tokens, fonts (Geist + IBM Plex Sans Arabic), theme, Cmd+K
- [ ] Auth-gated shell + brand switcher + app-layer brand-access predicate (one shared fn)
- [ ] Run list + run detail (live status, stage timeline, streamed logs, spent/cap bar, cost by token type)
- [ ] `/api/costs` reading the one ledger
- [ ] Artifact review (bilingual RTL render, diff vs last approved, approve-with-edits)
- [ ] Trigger run from UI (enqueues via deferJob)
- [ ] **Cross-brand leak test** (brand B operator cannot read brand A)
- [ ] Playwright E2E (sign in → trigger → COMPLETE → approve)

## P3 — Brand identity, voice & Gulf intelligence
- [ ] Brand identity + structured voice management (editable in console)
- [ ] Demand-calendar engine (Islamic + seasonal, per-market) suggesting the week's push
- [ ] Compliance guardrail layer (KSA/UAE/Kuwait rules) flagging/blocking pre-approval
- [ ] Learning loop: embed approved artifacts → pgvector retrieval → brand-voice few-shot + circuit-breaker
- [ ] Proofs: calendar suggestion, compliance block, voice shift, breaker trip

## P4 — Multi-format, multi-platform, multi-market
- [ ] Per-market channel routing (KSA/UAE/Kuwait)
- [ ] Formats: Reels/short-form, carousel, WhatsApp (CTWA/catalog/broadcast), Snapchat/TikTok
- [ ] Media-generation hooks (image via .env providers)
- [ ] Publish/export adapters (one interface; live where creds exist, labelled export otherwise)
- [ ] Proof: one brief → platform-correct variants + WhatsApp set + an export

## P5 — Growth suite (all selected; external = creds-gated)
- [ ] Research tools: trend · keyword (AR/EN) · viral-post · competitor monitoring
- [ ] Copywriting tool (hooks/captions/CTWA/ad copy on brand-voice few-shot)
- [ ] SEO/GEO (GBP + LLM-citation probing)
- [ ] Paid planning (budget/dayparting + Ramadan inflation)
- [ ] Community/replies (sentiment + approved-reply corpus)
- [ ] Analytics ingestion (brand's own numbers)

## P6 — Hardening & handover
- [ ] Langfuse tracing (traces only; CostLog stays canonical)
- [ ] promptfoo red-team suite
- [ ] Full pytest + Playwright in CI (ephemeral Postgres)
- [ ] Expand CI guards (doc/route parity) + operator runbook
- [ ] Mirror docs regenerated as-built; final honest STATUS.md
