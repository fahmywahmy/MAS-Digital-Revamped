"""Reset the public schema to empty: drop app tables, enums, and functions, while
keeping extensions (pgvector) and Supabase grants. Idempotent.

  DESTRUCTIVE — this wipes ALL data in the public schema. Intended only for a
  fresh/dirty dev database before `npm run db:deploy`.

Loads the repo-root .env (DIRECT_URL = session-mode pooler). Portable: resolves
.env relative to this file, so it works from any clone path.
"""
import os, sys, time
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

RESET = r"""
DO $$
DECLARE r RECORD;
BEGIN
  FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname='public') LOOP
    EXECUTE format('DROP TABLE IF EXISTS public.%I CASCADE', r.tablename);
  END LOOP;
  FOR r IN (SELECT t.typname FROM pg_type t JOIN pg_namespace n ON n.oid=t.typnamespace
            WHERE n.nspname='public' AND t.typtype='e') LOOP
    EXECUTE format('DROP TYPE IF EXISTS public.%I CASCADE', r.typname);
  END LOOP;
  FOR r IN (SELECT p.proname, pg_get_function_identity_arguments(p.oid) AS args
            FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE n.nspname='public'
              AND NOT EXISTS (SELECT 1 FROM pg_depend d WHERE d.objid=p.oid AND d.deptype='e')) LOOP
    EXECUTE format('DROP FUNCTION IF EXISTS public.%I(%s) CASCADE', r.proname, r.args);
  END LOOP;
END $$;
"""

conn = None
for attempt in range(1, 7):
    try:
        conn = psycopg.connect(dsn, connect_timeout=20, autocommit=True)
        break
    except Exception as e:
        print(f"connect attempt {attempt} failed: {str(e).splitlines()[0][:80]}")
        time.sleep(3)
if conn is None:
    print("ERROR: could not connect (outbound Postgres 5432 blocked? switch networks)"); sys.exit(1)

with conn, conn.cursor() as cur:
    cur.execute(RESET)
    cur.execute("SELECT count(*) FROM pg_tables WHERE schemaname='public'")
    tables = cur.fetchone()[0]
    cur.execute("SELECT extname, extversion FROM pg_extension WHERE extname='vector'")
    vec = cur.fetchone()
print(f"reset complete -> public tables={tables}, vector_ext={vec}")
