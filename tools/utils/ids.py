"""The one id generator for raw-SQL inserts.

Prisma generates `cuid()`s for rows created through the client; the Python tools
insert directly, so they mint their own collision-resistant ids. These are
opaque `String @id` values — never parsed, only compared.
"""
from __future__ import annotations

import uuid


def new_id(prefix: str = "c") -> str:
    """A short, collision-resistant id with an optional readable prefix."""
    return f"{prefix}{uuid.uuid4().hex}"
