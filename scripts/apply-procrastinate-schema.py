"""GATED — applies (or removes) the durable-queue schema on the live database.

Do NOT run until the generated SQL has been reviewed and approved
(see scripts/show-procrastinate-schema.py). Uses DIRECT_URL (session mode, :5432).
Idempotent-ish: re-applying a full install on an existing schema will error on
duplicate objects — use --uninstall first for a clean reinstall.

  Apply    :  .venv/Scripts/python scripts/apply-procrastinate-schema.py
  Verify   :  .venv/Scripts/python scripts/apply-procrastinate-schema.py --verify
  Uninstall:  .venv/Scripts/python scripts/apply-procrastinate-schema.py --uninstall
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tools.runtime import schema_sql  # noqa: E402
from tools.runtime.app import SCHEMA_NAME  # noqa: E402
from tools.utils.db import connect  # noqa: E402


def _count_objects() -> dict[str, int]:
    with connect() as conn:
        tables = conn.execute(
            "SELECT count(*) FROM pg_tables WHERE schemaname = %s", (SCHEMA_NAME,)
        ).fetchone()[0]
        funcs = conn.execute(
            "SELECT count(*) FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace "
            "WHERE n.nspname = %s", (SCHEMA_NAME,)
        ).fetchone()[0]
    return {"tables": tables, "functions": funcs}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--uninstall", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    if args.verify:
        c = _count_objects()
        print(f"schema {SCHEMA_NAME!r}: tables={c['tables']} functions={c['functions']}")
        ok = c["tables"] >= 4 and c["functions"] >= 10
        print("OK — durable-queue schema present." if ok else "MISSING — not installed.")
        return 0 if ok else 1

    sql = schema_sql.uninstall_sql() if args.uninstall else schema_sql.install_sql()
    action = "UNINSTALL" if args.uninstall else "INSTALL"
    print(f"== {action} durable-queue schema (DIRECT_URL) ==")
    with connect(autocommit=False) as conn:
        with conn.transaction():
            conn.execute(sql)
    print("  done.")
    c = _count_objects()
    print(f"  schema {SCHEMA_NAME!r}: tables={c['tables']} functions={c['functions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
