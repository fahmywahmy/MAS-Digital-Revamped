"""Verify the data layer after `npm run db:deploy`. Read-only.

Loads the repo-root .env (DIRECT_URL). Portable: resolves .env relative to this
file. Expect: 36 tables, 25 enums, no Tenant cluster, pgvector present, a clean
2-migration ledger, Brand table empty.
"""
import os, sys
from pathlib import Path
import psycopg
from dotenv import load_dotenv

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

load_dotenv(Path(__file__).resolve().parent.parent / ".env")
dsn = os.getenv("DIRECT_URL")
if not dsn:
    print("ERROR: DIRECT_URL not set in .env"); sys.exit(2)

def one(cur, q):
    cur.execute(q); return cur.fetchone()

with psycopg.connect(dsn, connect_timeout=20) as conn:
    with conn.cursor() as cur:
        print("== tables / enums ==")
        print("  public tables :", one(cur, "SELECT count(*) FROM pg_tables WHERE schemaname='public'")[0])
        print("  enum types    :", one(cur, "SELECT count(*) FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace WHERE n.nspname='public' AND t.typtype='e'")[0])
        print("== prune (all should be 0) ==")
        for t in ("Tenant", "TenantSiteArchitecture", "BrandConfig", "TenantOnboardingState"):
            print(f"  {t:24}:", one(cur, f"SELECT count(*) FROM pg_tables WHERE schemaname='public' AND tablename='{t}'")[0])
        print("== pgvector ==")
        print("  extension     :", one(cur, "SELECT extversion FROM pg_extension WHERE extname='vector'"))
        print("  embedding col :", one(cur, "SELECT udt_name FROM information_schema.columns WHERE table_name='VectorMemory' AND column_name='embedding'"))
        print("  match function:", one(cur, "SELECT proname FROM pg_proc WHERE proname='match_vector_memory'"))
        print("== migration ledger ==")
        cur.execute("SELECT migration_name, (finished_at IS NOT NULL AND rolled_back_at IS NULL) FROM _prisma_migrations ORDER BY started_at")
        for name, applied in cur.fetchall():
            print(f"  {name:20} applied={applied}")
        print("== sample ==")
        print("  Brand rows    :", one(cur, 'SELECT count(*) FROM "Brand"')[0])
print("OK")
