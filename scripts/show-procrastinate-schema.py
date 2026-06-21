"""APPROVAL ARTIFACT — generates the durable-queue schema SQL and summarizes it.

Touches NO database. Run this to review exactly what would be applied to Supabase
before approving the live step (`apply-procrastinate-schema.py`). It also sanity-
checks that the runtime app constructs and the pipeline task is registered, without
opening a connection.

Run:  .venv/Scripts/python scripts/show-procrastinate-schema.py
Writes: db/procrastinate/install.generated.sql + uninstall.generated.sql
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

from tools.runtime import schema_sql  # noqa: E402
from tools.runtime.app import SCHEMA_NAME, app  # noqa: E402

OUT_DIR = REPO_ROOT / "db" / "procrastinate"


def main() -> int:
    install = schema_sql.install_sql()
    uninstall = schema_sql.uninstall_sql()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "install.generated.sql").write_text(install, encoding="utf-8")
    (OUT_DIR / "uninstall.generated.sql").write_text(uninstall, encoding="utf-8")

    # Object inventory — what lands in the dedicated schema.
    objects: dict[str, list[str]] = {}
    for kind, name in re.findall(
        r"CREATE (TABLE|TYPE|FUNCTION|INDEX|TRIGGER)\s+(?:IF NOT EXISTS\s+)?([a-zA-Z0-9_]+)",
        install,
    ):
        objects.setdefault(kind, []).append(name)

    print("== Durable-queue schema (APPROVAL ARTIFACT — nothing applied) ==")
    print(f"  target schema : {SCHEMA_NAME}  (isolated from the Prisma `public` tables)")
    print(f"  written to    : {OUT_DIR / 'install.generated.sql'}")
    print(f"  reversible by : {OUT_DIR / 'uninstall.generated.sql'}")
    print(f"  NOT part of   : the Prisma migration chain (pre-push hook untouched)")
    print()
    print("  Objects created (all prefixed procrastinate_*, all inside the schema):")
    for kind in ("TYPE", "TABLE", "INDEX", "FUNCTION", "TRIGGER"):
        names = objects.get(kind, [])
        if names:
            print(f"    {kind:9}({len(names):2}): {', '.join(names[:6])}{' …' if len(names) > 6 else ''}")
    print()

    # Static sanity: app constructs, task registered — no DB connection opened.
    # The worker imports these at startup via app.import_paths; do it explicitly
    # here so the registry is populated for the check.
    import importlib

    for path in app.import_paths:
        importlib.import_module(path)
    task_names = sorted(app.tasks.keys())
    print("  Runtime wiring (constructed, no connection opened):")
    print(f"    app connector : {type(app.connector).__name__}")
    print(f"    tasks         : {task_names}")
    assert "run_pipeline" in task_names, "FAIL: run_pipeline task not registered"
    print()
    print("== Review db/procrastinate/install.generated.sql, then approve to apply. ==")
    print("   Apply (after approval):  .venv/Scripts/python scripts/apply-procrastinate-schema.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
