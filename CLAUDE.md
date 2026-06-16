# CLAUDE.md — MAS Digital Revamped

Loaded into every Claude Code session in this repo. **Binding.** Read it before
acting. The *why* behind it is [`docs/ARCHITECTURE_REVIEW.md`](docs/ARCHITECTURE_REVIEW.md)
(the teardown of the legacy `MAS-Digital-System` this repo replaces) and
[`PORTING_PLAN.md`](PORTING_PLAN.md).

This is a **clean-room rebuild**: keep the legacy engine, leave its SaaS scaffolding
behind. The legacy system's #1 failure was **docs, dashboards, and "shipped" claims
describing things that didn't exist.** Do not recreate that here.

## 1. The thesis (binding — the build must agree with it)

- **Agency tool, multi-client.** You onboard and trust each client; clients do NOT
  self-serve. Ceiling: ~10 brands/clients, 1–3 operators.
- **`Brand` is the tenancy unit.** No `Tenant` / tier / billing / onboarding layer.
- **App-layer authorization is the boundary** (`brandId` scoping + auth helpers), NOT
  Postgres RLS. If RLS is ever added it is belt-and-suspenders with a real cross-brand
  leak test — never a third, inert copy.

If a task drifts toward self-serve SaaS, RLS-as-enforcement, tiers, or a Tenant layer:
**stop and confirm.** That drift is exactly what this repo exists to escape.

## 2. Non-negotiables (binding)

1. **Honest instruments.** Cost is written to the DB the dashboard reads, accumulates
   onto every run, and a real (not `print()`) kill-switch aborts a run over budget.
2. **One source of truth per concern.** One pipeline representation, one cost ledger,
   one credential door, one brand-access predicate. No second copy that drifts.
3. **Enforced CI only.** A rule not enforced by a check is deleted, not faked with
   `|| true` (see §4).
4. **Durable runtime.** Long jobs run on a durable queue and survive a restart.
5. **Docs follow code.** Describe only what exists. Decisions/contracts may state
   intent but must be labeled "target, not built." No fiction.

## 3. How to work here

- **No pseudo-fixes.** No TODO in place of a fix, no stub a caller treats as real, no
  "noted in the report" instead of resolved. Can't fix it this pass? Say so, and why.
- **"Fixed" means end-to-end** — every downstream reader of a changed contract behaves.
- **No silent triage.** Surface all N problems; ask before scoping down.
- **Honest delta at completion** — three lines: *Shipped* / *Left on the table* /
  *Surprised by*. Never celebratory while siblings are unresolved.
- **Port, don't copy bugs.** Porting from legacy = fix the known defect on the way in
  (e.g. cost ledger writes Postgres) — never carry the bug across.
- **Verify, don't assume.** Run it; show the output.

## 4. What CI + hooks actually enforce (these BLOCK — not wishes)

- `tools/` reach Anthropic ONLY via `claude_client.py` (no direct `anthropic` import).
- No code loads a parent-directory `.env` (`../.env`).
- No `|| true` escape hatches anywhere in `.github/workflows/`.
- `pre-push` refuses uncommitted `schema.prisma` / migrations.

Adding a rule? Wire it into `.github/workflows/ci.yml` or a git hook — or don't add it.

## 5. Do NOT re-grow the legacy rot

Inert Postgres RLS · `Tenant`/tier/onboarding layer · multiple pipeline representations
· cost tracking that doesn't write the table the UI reads · `|| true` CI guards · docs
describing unbuilt routes · the repo living on OneDrive · any tool calling the Anthropic
SDK directly.

## 6. Where to look

| For | Read |
|---|---|
| The verdict this rebuild is based on | [`docs/ARCHITECTURE_REVIEW.md`](docs/ARCHITECTURE_REVIEW.md) |
| What to port / drop / fix, in order | [`PORTING_PLAN.md`](PORTING_PLAN.md) |
| Target architecture (built vs planned) | [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) |
| How to run what exists today | [`docs/SETUP.md`](docs/SETUP.md) |
| Thesis + non-negotiables | [`README.md`](README.md) |

Mirror docs (operator guide, data model, dashboard, integrations, evals, security) are
stubs under `docs/` until their feature lands — written as built, never ahead of it.
