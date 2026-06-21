"""The one credential door (CLAUDE.md §2.2).

Everything reads `get_credential()`; nothing loads `../.env` (CI-enforced). The
repo-root `.env` is resolved relative to THIS file so the toolchain works from
any CWD.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# tools/utils/config.py → repo root is three parents up.
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"


@lru_cache(maxsize=1)
def _load() -> None:
    """Load the repo-root .env exactly once. Never a parent directory."""
    load_dotenv(ENV_PATH)


class MissingCredential(RuntimeError):
    """A required credential / env var is not set."""


def get_credential(name: str, *, required: bool = True, default: str | None = None) -> str | None:
    """Read a single env-backed credential. Fail-closed when required and unset."""
    _load()
    value = os.getenv(name, default)
    if required and not value:
        raise MissingCredential(
            f"{name} is not set. Add it to {ENV_PATH} (see .env.example)."
        )
    return value


def database_dsn() -> str:
    """Direct (session-mode, :5432) DSN for the Python tools.

    Prisma's `DATABASE_URL` carries `?pgbouncer=true`, a Prisma-only flag libpq
    rejects — so the tools use `DIRECT_URL` (the same endpoint the migrations
    use). At this scale (≤10 brands, 1–3 operators) session connections are
    fine; revisit a pgbouncer-safe pooled DSN only if connection volume grows.
    """
    return get_credential("DIRECT_URL")  # type: ignore[return-value]
