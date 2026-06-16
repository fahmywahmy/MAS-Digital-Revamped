# Data Model — MAS Digital Revamped

> The data model **is** [`../prisma/schema.prisma`](../prisma/schema.prisma) — that is
> the source of truth (35 tables, 25 enums, `Brand` as the tenancy unit, pgvector on
> `VectorMemory`). A narrative/diagram version will be **generated from the schema** when
> it's worth maintaining; until then, read the schema and
> [`ARCHITECTURE.md`](ARCHITECTURE.md) → "Data model" for the high-level shape.
>
> Per `CLAUDE.md §2.5`, this doc will not hand-describe tables ahead of (or out of sync
> with) the schema.
