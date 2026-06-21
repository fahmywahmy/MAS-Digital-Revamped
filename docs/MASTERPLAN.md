# MASTERPLAN — Finishing MAS Digital Revamped

> **Purpose:** the single execution plan to take this repo from "proven spine" to a
> **state-of-the-art, genuinely-working system for delivering consistent digital growth
> to Gulf travel agencies (Kuwait · KSA · UAE).** Research-grounded, scope-explicit, and
> built to be driven autonomously via `/goal` with a crash-safe resume protocol.
>
> Companion docs: [`DESIGN.md`](DESIGN.md) (UX/UI language) · [`PROGRESS.md`](PROGRESS.md)
> (the living resume ledger) · [`STATUS.md`](STATUS.md) (point-in-time build status) ·
> [`ARCHITECTURE.md`](ARCHITECTURE.md) · [`../PORTING_PLAN.md`](../PORTING_PLAN.md).

---

## 0. The honesty contract (binding for every phase)

This rebuild exists to escape the legacy system's #1 failure — **fiction** (docs and
dashboards describing things that didn't exist). Every phase obeys:

1. **No feature is "done" until proven end-to-end** with a runnable script or test whose
   output is shown. A green checkbox in `PROGRESS.md` must point at that proof.
2. **No fake output, no stub a caller treats as real.** If an integration isn't live
   (no credentials), it runs in a **clearly-labelled non-live mode** (export/manual) —
   never a silent pretend-success.
3. **Honest delta at every checkpoint** — *Shipped / Left on the table / Surprised by*.
4. **Docs follow code.** `STATUS.md` and the mirror docs describe only what exists.
5. **The instruments stay honest** — real cost in `CostLog`, a real kill-switch, durable
   runs. Never a second cost ledger the UI reads (that was the legacy rot).
6. **Brutal honesty on limits** (see §7) — including the limits of my own autonomy.

---

## 1. Mission & definition of done

**Mission.** A lean **agency tool** (1–3 operators, ~10 trusted travel-agency brands)
that, for each brand, runs an AI content/marketing pipeline calibrated to the Gulf market
— bilingual Arabic/English, dialect-aware, demand-calendar-driven, compliance-guarded —
and presents it through a **crafted operator console** where a human reviews, edits, and
approves before anything ships. Every run is brand-scoped, cost-tracked, and quality-gated.

**Definition of done (the autonomously-achievable target).** A single operator can, from
the console:
1. Pick a brand and trigger a content run (or accept a calendar-suggested one).
2. Watch it execute **on the durable queue** (survives a restart), stage-by-stage, with
   live cost accumulating against a budget and a real kill-switch.
3. See the generated artifact (bilingual, format-correct, compliance-checked), **review a
   diff, edit, and approve** — or send it back.
4. Export/publish the approved artifact (**live** where platform credentials exist;
   **export-ready** otherwise — honestly labelled).
5. See cost, eval scores, and run history per brand — all reading the one ledger.
With CI green on enforced rules, the console accessible only to allow-listed operators,
and brand isolation proven by a real cross-brand leak test.

**Explicitly NOT claimed as autonomously deliverable by me** (see §7): standing up live
Meta / Google Ads / Snapchat / TikTok / WhatsApp-Business / GBP API access — those require
*your* business accounts, OAuth consent, approvals, and spend. The system is built
**integration-ready** (clean adapters); each goes live only when you supply credentials.

---

## 2. Inputs & decisions (gather once — defaults let me proceed without pestering)

Legend: **[BLOCKING]** = I will confirm before building the affected phase ·
**[DEFAULTED]** = I proceed on the stated default unless you override.

| # | Decision | My default (if you don't override) | Status |
|---|---|---|---|
| I1 | **Integration boundary** — what "working" means | **Generate → eval → review → approve → export.** Platform adapters built; go live only where creds exist; non-live = labelled export/manual. No fake publishing. | **[BLOCKING]** |
| I2 | **Target brand** | Use the `.env` `BRAND_*` brand if it's a real client; otherwise I author one realistic **Kuwait travel-agency demo brand**, clearly labelled demo, swappable later. | **[BLOCKING]** |
| I3 | **v1 vertical scope** (beyond the always-in core) | Core = content + console + durable runtime + brand identity/voice + demand calendar + compliance guard + learning loop. Optional = SEO/GEO, paid planning, community/replies, analytics. | **[BLOCKING]** |
| I4 | **Console accent / theme** | Dark-default, **teal `#12A594`** accent on a sage/slate neutral (WGSN 2026 + anti-AI-slop). | **[BLOCKING]** (taste) |
| I5 | **Console product name** | "MAS Console" until you name it. | [DEFAULTED] |
| I6 | **Operator-UI language** | **English** operator UI; **bilingual AR/EN content** rendered RTL-correct. | [DEFAULTED] |
| I7 | **Apply Procrastinate to Supabase** | Yes, in a **dedicated `procrastinate` schema**; I show the exact SQL for approval before applying (dry-run). | **[BLOCKING]** (live DB) |
| I8 | **Eval judge model** | Judge ≠ generator: generator Opus 4.8, **judge = a different model + locked rubric + deterministic guards + human-calibrated gold set** (fixes the 25/25 leniency). | [DEFAULTED] |
| I9 | **Autonomous build spend ceiling** (real LLM $ during the build) | Cap at **$50**; I track spend in the ledger and stop/flag at the cap. | **[BLOCKING]** |
| I10 | **Deployment** | **Local Windows host** via NSSM services (replacing the `.bat` launchers), designed cloud-portable (systemd). | [DEFAULTED] |
| I11 | **Growth KPI priority** | Lead-gen via **WhatsApp (click-to-WhatsApp / catalog)** + organic reach/engagement, calendar-paced. | [DEFAULTED] |
| I12 | **Credentials you can provide** | Build adapters; I use whatever keys land in `.env`. Already present: Anthropic, Google AI, OpenAI, Brave, Apify, Perplexity, Pexels, Pixabay, Freesound, Langfuse. | [DEFAULTED] |

---

### 2a. Decisions locked (2026-06-21)
- **I1 Integration boundary:** Generate → eval → review → approve → **export**. Platform
  adapters go live only with your creds; non-live = labelled export. **No fake publishing.**
- **I2 Brand:** a **real client** — the brand brief is the one remaining upfront input
  (requested separately; until it lands I scaffold brand-agnostic infra in P1/P2).
- **I3 v1 scope:** the always-in core **plus the full growth suite** — SEO/GEO, paid-media
  planning, analytics ingestion, community/replies, **trend research, keyword research,
  viral-post research, competitor monitoring, and copywriting**. Sequenced across P4–P5.
- **I4 Accent:** **Teal `#12A594`** (locked in [`DESIGN.md`](DESIGN.md)).
- **Non-blocking defaults stand:** console name "MAS Console"; English UI + bilingual AR/EN
  content; dedicated `procrastinate` schema with SQL shown for approval first; **$50** spend
  cap (pending your confirm — adjustable up); local Windows/NSSM; WhatsApp lead-gen KPI.

## 3. Architecture & stack decisions (research-grounded)

| Area | Decision | Why (1-line) |
|---|---|---|
| Durable queue | **Procrastinate** on Postgres, dedicated schema | Postgres-only, transactional enqueue, `pg_notify`+polling fallback, built-in stalled-job recovery. |
| Worker connection | Listener on **direct 5432**; auto-degrade to polling on the pooler | Supabase transaction pooler (6543) can't `LISTEN/NOTIFY`; Procrastinate polls as fallback. |
| TS ↔ Python | Webapp **enqueues via one typed `deferJob()` helper**; polls `AgentRun` | True transactional enqueue, one queue/DB, no extra hot-path service. |
| Process supervision | **NSSM** (Windows) → **systemd** (cloud) | Restart-on-failure + auto-start; replaces `.bat`; PM2-as-service is flaky on Win Server. |
| Console stack | **Next.js 16 App Router + shadcn/ui on Radix + Tailwind v4** | Own-the-code components; the 2026 craft standard. See [`DESIGN.md`](DESIGN.md). |
| Charts / tables / palette | **Recharts** (+ Tremor blocks) · **TanStack Table+Virtual** · **cmdk** · **sonner** | Maintained, dense-data-friendly, the references top teams use. |
| Eval gate | **DeepEval `GEval`** rubric (threshold 0.72 = 18/25), judge ≠ generator, + deterministic guards, calibrated vs human gold set; **promptfoo** for red-team | Rubric-as-judge, CI-enforceable, counters grade inflation. |
| Cost / observability | **Postgres `CostLog` canonical**; **Langfuse** for traces/latency only | Kill-switch & `/api/costs` read Postgres; Langfuse never a control input. |
| Testing | **pytest** (mock DB/LLM in CI; integration host-only) + **Playwright** (ephemeral Postgres in CI) | No `\|\| true` fakes; ephemeral PG covers schema/authz. |

**Gulf-domain decisions baked into the product** (from the market research):
- **WhatsApp is the conversion core** — generate click-to-WhatsApp / catalog / broadcast assets, not just feed posts.
- **Arabic-primary, dialect-aware** — Khaleeji for B2C social, MSA for corporate; bilingual mirrors; separate AR/EN keyword sets; RTL-correct rendering.
- **Per-market channel routing** — KSA → Snapchat + TikTok + Reels; UAE → Facebook + YouTube + WhatsApp + Google; Kuwait → Instagram-first + Snapchat secondary.
- **Demand-calendar engine** — Islamic dates (Ramadan/Eid/Hajj, ~−11 days/yr), National Days, school breaks, seasonal pushes (Umrah year-round + Ramadan peak; summer Europe/Caucasus/SE-Asia; winter inbound).
- **Compliance guardrail** — KSA imagery modesty + no alcohol/gambling even indirect; UAE/Kuwait alcohol-ad ban; paid-partnership labelling; influencer-permit awareness (UAE Mu'lin, KSA Mawthooq); PDPL consent.
- **Right-sized GEO/AEO** — structured-data + cited-answer content as a rising hedge, not the main channel.
- **Instrument the brand's own performance** — present external benchmarks as directional, with sources; trust the client's own data once flowing.

---

## 4. Phased roadmap

Each phase: **Goal → Deliverables → Proof → Exit criteria.** Phases ship in order; each
ends with a commit and a `PROGRESS.md` update. Optional phases (P5) are scope-gated (I3).

### ✅ P0 — Spine (DONE)
Foundation, data layer, LLM gateway, cost ledger + kill-switch, manifest pipeline, content
vertical, eval gate, drift guard. *Proof: `prove-gateway.py`, `run-content-pipeline.py`.*

### P1 — Durable runtime + trustworthy eval
- **Deliverables:** Procrastinate (dedicated schema) + one typed `deferJob()` helper +
  `pg_notify`/polling worker; `AgentRun` lifecycle hardened (no orphaned `RUNNING`);
  NSSM service wrappers; **eval-gate calibration** — judge ≠ generator, locked rubric
  bands, deterministic guards (length / banned-claims / required-sections), a 20–40-item
  human-scored gold set, threshold 0.72.
- **Proof:** a run deferred, worker killed mid-run, restarted → run **completes, not
  orphaned**; gold-set calibration report shows judge↔human correlation; a deliberately
  weak artifact is **blocked** by the gate (the FAIL path the P0 proof never exercised).
- **Exit:** restart-survival demonstrated; gate no longer rubber-stamps.

### P2 — Operator console (the UX/UI investment) — see [`DESIGN.md`](DESIGN.md)
- **Deliverables:** Next.js console implementing the design system: auth-gated shell;
  **brand switcher**; **run list + run detail** (live status dot, per-stage timeline,
  streamed logs, **live spent/cap budget bar**, cost broken by token type); **artifact
  review** (bilingual RTL render, diff vs last approved, **approve-with-edits**); **trigger
  run**; `/api/costs` reading the one ledger; **Cmd+K** palette; light/dark; reduced-motion.
  Plus the **app-layer brand-access predicate** (one shared function) + **cross-brand leak
  test**.
- **Proof:** Playwright E2E — sign in (allow-listed), trigger a run, watch it to COMPLETE,
  review + approve an artifact; leak test proves brand B's operator cannot read brand A.
- **Exit:** an operator can drive a full run from the UI; isolation proven; it looks
  crafted (DESIGN.md checklist met), not AI-slop.

### P3 — Brand identity, voice & the Gulf intelligence layer
- **Deliverables:** brand identity management (the 12-section context + structured voice
  fields) editable in the console; **demand-calendar engine** (Islamic + seasonal,
  per-market) that suggests the right campaign for the week; **compliance guardrail**
  layer (per-country rules) that flags/blocks non-compliant creative pre-approval;
  **learning loop** — embed approved artifacts → pgvector retrieval → brand-voice
  few-shot, with a **circuit-breaker** so a bad regen can't silently degrade output.
- **Proof:** calendar suggests a correct seasonal push for a given date; a non-compliant
  draft (e.g. alcohol reference for a KSA brand) is flagged; an approved artifact measurably
  shifts the next generation's voice; circuit-breaker trips on a degenerate regen.
- **Exit:** generations are brand-true, calendar-aware, and compliance-safe.

### P4 — Multi-format, multi-platform, multi-market content
- **Deliverables:** per-market channel routing (I11); formats — Reels/short-form (primary),
  carousels, **WhatsApp catalog/CTWA/broadcast**, Snapchat/TikTok variants; media-generation
  hooks (image via the `.env` providers); **publish/export adapters** behind one interface
  (live where creds exist, labelled export otherwise).
- **Proof:** one brief fans out to platform-correct variants for KSA/UAE/Kuwait; a WhatsApp
  asset set is generated; an adapter exports an approved post (and, if creds exist, posts it
  to a sandbox — clearly real vs. labelled-export).
- **Exit:** the system produces the channel mix the market research says actually converts.

### P5 — Growth suite (all selected; external slices are creds-gated)
Each is an independent slice with its own eval + proof; non-live where creds are absent:
- **Research tools:** trend research, **keyword research** (separate AR/EN sets, not
  translated), **viral-post research** (what's working in the niche/region), **competitor
  monitoring** (track named competitors' content/cadence). These feed the strategy step.
- **Copywriting:** a dedicated copy tool (hooks, captions, CTWA scripts, ad copy) with the
  brand-voice few-shot from the learning loop — beyond the inline pipeline copy.
- **SEO/GEO:** Google Business Profile optimization + AI-citation probing (Perplexity/
  ChatGPT/Gemini) for "best travel agency in…" queries.
- **Paid-media planning:** budget allocation + dayparting recommendations per market, with
  Ramadan CPM inflation and post-iftar timing (planning/recommendations, not live buying).
- **Community/replies:** sentiment-tagging + brand-voice reply drafts for approval →
  approved-reply corpus feeds the learning loop.
- **Analytics ingestion:** the brand's *own* numbers replacing borrowed benchmarks
  (creds-gated).

### P6 — Hardening & handover
Langfuse tracing wired (traces only) · promptfoo red-team suite · full pytest + Playwright
in CI (ephemeral Postgres) · expand CI guards (doc/route parity) · operator runbook ·
mirror docs regenerated as-built · final honest `STATUS.md`.

---

## 5. The `/goal` statements

**Master resume goal** (paste into `/goal` to run/continue the whole build):

> Execute `docs/MASTERPLAN.md` autonomously. First read `docs/PROGRESS.md` and resume from
> the first incomplete task. Obey the §0 honesty contract and the §2 decisions (do not ask
> for input already decided there). After each verified sub-phase: show the proof output,
> commit, and update `docs/PROGRESS.md`. If you hit a usage/session limit, stop cleanly —
> the work and the ledger are committed, and re-invoking this goal resumes from the ledger.

**Per-phase goals** (for running one phase at a time):
- `/goal Execute MASTERPLAN phase P1 (durable runtime + eval calibration). Read PROGRESS.md, do only P1, prove + commit + update the ledger.`
- …same pattern for `P2`, `P3`, `P4`, `P5`, `P6`.

---

## 6. Resume / refresh protocol (crash-safe continuity)

- **`docs/PROGRESS.md` is the source of truth for "where we are"** — a checklist of every
  phase's tasks with status + the commit that proved each. I update it as I go.
- **Commit after every verified sub-phase** so a stop never loses work (the pre-push hook
  already protects schema/migrations on synced storage).
- **On resume**, the master goal re-reads `PROGRESS.md` + `git log` and continues from the
  first unchecked task — no re-derivation, no duplicate work.
- **Within a live session** I can chain work and use background tasks/scheduled wakeups.
  **Across a hard usage/plan cap I cannot self-continue** — see §7. The "refresh trigger"
  is you re-invoking the master goal; the ledger makes that a clean continuation.

---

## 7. Brutal-honesty caveats (read this twice)

- **I do not run unattended for days.** I act when invoked. I can work through a long
  session and resume cleanly via the ledger, but a usage/plan limit hard-stops me until
  **you** re-invoke the goal. Any plan promising "nonstop multi-day autonomous execution
  with no human in the loop" would be fiction — this protocol is the honest best version.
- **Live ad/publishing/WhatsApp-Business/GBP integration is not something I can stand up
  alone.** It needs your business accounts, OAuth apps, platform approvals, and spend. I
  build the adapters and prove the export path; going live is a credentialed step you take.
- **LLM spend is real.** Generation + eval calibration + repeated test runs over a full
  build cost real money (each content run ≈ $0.09; calibration and red-teaming add more).
  The I9 ceiling bounds it; I'll report spend at each checkpoint.
- **The eval gate is only as honest as its calibration.** The P0 run scored 25/25 — a sign
  of judge leniency, not perfection. P1 fixes this; until then, treat gate passes as
  provisional.
- **Market benchmarks are directional.** Regional cost/conversion figures come from agency
  reports, not audited data; the product instruments the brand's *own* numbers rather than
  hard-coding borrowed ones.

---

## 8. Research basis (key sources)

- **Gulf travel digital:** DataReportal Digital 2025 (KSA/Kuwait/UAE); Snap×Publicis &
  Snap-for-Business GCC ROI; Meta/Forrester click-to-WhatsApp; GASTAT Umrah; Wego/TradeArabia
  seasonal; Al Tamimi (UAE Mu'lin permit); Chambers (KSA Mawthooq, Kuwait Decree-Law 10/2026);
  IAPP (Saudi PDPL).
- **Console UX/UI:** Linear & Vercel/Geist design writeups; Radix Colors; Emil Kowalski on
  motion; APCA contrast; Next.js `next/font`; W3C bidi/`<bdi>`; RTL styling guides.
- **Architecture:** Procrastinate docs (stalled-job recovery, cron, discussions); Supavisor
  `LISTEN/NOTIFY` issue #85; DeepEval G-Eval; promptfoo LLM-as-judge; Langfuse cost tracking;
  Playwright-vs-Cypress 2026.

*(Full per-claim source lists live in the research briefs captured in this session's history.)*
