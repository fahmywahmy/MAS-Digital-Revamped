-- pgvector: extension + embedding column + ivfflat index + retrieval function.
-- Ordered AFTER 0000_init (which creates "VectorMemory"), fixing the legacy
-- bug where the pgvector migration ran before the table existed. The
-- `embedding` column is intentionally NOT in schema.prisma (Prisma has no
-- native vector type); all vector ops go through psycopg in the Python tools.
-- Every statement is idempotent so this is safe to re-run.

CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE "VectorMemory"
  ADD COLUMN IF NOT EXISTS embedding vector(1024);

CREATE INDEX IF NOT EXISTS "VectorMemory_embedding_idx"
  ON "VectorMemory"
  USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 100);

CREATE OR REPLACE FUNCTION match_vector_memory(
    query_embedding vector(1024),
    match_brand_id  text,
    match_count     int DEFAULT 5,
    source_filter   text DEFAULT NULL
)
RETURNS TABLE (
    id          text,
    brand_id    text,
    source_type text,
    source_id   text,
    content     text,
    metadata    jsonb,
    similarity  float
)
LANGUAGE sql STABLE
AS $$
    SELECT
        vm.id,
        vm."brandId"    AS brand_id,
        vm."sourceType" AS source_type,
        vm."sourceId"   AS source_id,
        vm.content,
        vm.metadata,
        1 - (vm.embedding <=> query_embedding) AS similarity
    FROM "VectorMemory" vm
    WHERE vm."brandId" = match_brand_id
      AND (source_filter IS NULL OR vm."sourceType" = source_filter)
      AND vm.embedding IS NOT NULL
    ORDER BY vm.embedding <=> query_embedding
    LIMIT match_count;
$$;
