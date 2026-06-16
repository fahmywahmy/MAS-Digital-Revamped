# Setup — MAS Digital Revamped

> Covers **only what runs today** (the data layer). This grows as features land — it
> will never document a step that doesn't work yet (`CLAUDE.md §2.5`).

## Prerequisites

- **Node 20+**, **Python 3.12+**, and a **Supabase** project.
- A network with **outbound Postgres (5432/6543)**. Some corporate networks block these
  (TCP timeout to the pooler) — if `db:deploy` times out, switch to a hotspot/home
  network. (HTTPS/git keep working; only Postgres ports are blocked.)

## 1. Clone + configure

```bash
git clone https://github.com/fahmywahmy/MAS-Digital-Revamped.git
cd MAS-Digital-Revamped
cp .env.example .env          # then fill in Supabase + Anthropic values
```

The repo loads its **own** `.env` at the repo root — never `../.env`.

## 2. Install

```bash
npm install
```

## 3. Apply the database schema

```bash
npm run db:deploy             # applies prisma/migrations (0000_init + 0001_pgvector)
npm run db:status             # should report: "Database schema is up to date!"
```

For a **fresh or dirty** database, clear it first (⚠️ **destructive — wipes all data**):

```bash
python scripts/reset-db.py    # drops app tables/enums/functions; keeps extensions
npm run db:deploy
```

## 4. Verify

```bash
python scripts/verify-db.py   # expect 36 tables, pgvector present, clean 2-migration ledger
```

## What's NOT here yet

The webapp, tools, LLM gateway, and pipelines are not ported yet — see
[`../PORTING_PLAN.md`](../PORTING_PLAN.md). `Launch Webapp.bat` will print
"webapp not found" until the webapp lands (porting order section D, step 5).
