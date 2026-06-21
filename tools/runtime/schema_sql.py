"""Builds the dedicated-schema install/uninstall SQL for the durable queue.

Single source of truth = Procrastinate's own bundled `schema.sql` (version-pinned
in requirements.txt). We wrap it with a `CREATE SCHEMA` + `search_path` prologue so
every `procrastinate_*` object lands in the dedicated `procrastinate` schema and
NONE of it touches the Prisma-owned `public` tables. This is deliberately NOT a
Prisma migration — the Prisma chain (guarded by the pre-push hook) stays untouched.
"""
from __future__ import annotations

import importlib.metadata
import pathlib

import procrastinate

from tools.runtime.app import SCHEMA_NAME

_VERSION = importlib.metadata.version("procrastinate")


def bundled_schema_path() -> pathlib.Path:
    return pathlib.Path(procrastinate.__file__).parent / "sql" / "schema.sql"


def install_sql() -> str:
    body = bundled_schema_path().read_text(encoding="utf-8")
    return (
        f"-- GENERATED — do not hand-edit. Source: procrastinate {_VERSION} bundled schema.\n"
        f"-- Regenerate: python scripts/show-procrastinate-schema.py\n"
        f"-- Installs the durable-queue objects into a DEDICATED `{SCHEMA_NAME}` schema,\n"
        f"-- isolated from the Prisma-owned public tables. NOT part of the Prisma chain.\n"
        f"-- Reversible: scripts/apply-procrastinate-schema.py --uninstall\n\n"
        f"CREATE SCHEMA IF NOT EXISTS {SCHEMA_NAME};\n"
        f"SET search_path TO {SCHEMA_NAME};\n\n"
        f"{body}"
    )


def uninstall_sql() -> str:
    return (
        f"-- Removes the entire durable-queue schema. Destructive: drops all queued\n"
        f"-- jobs/history. The Prisma `public` tables are untouched.\n"
        f"DROP SCHEMA IF EXISTS {SCHEMA_NAME} CASCADE;\n"
    )
