-- Removes the entire durable-queue schema. Destructive: drops all queued
-- jobs/history. The Prisma `public` tables are untouched.
DROP SCHEMA IF EXISTS procrastinate CASCADE;
