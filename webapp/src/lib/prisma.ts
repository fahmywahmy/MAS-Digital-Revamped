import { PrismaClient } from "@prisma/client";

// Singleton — avoids exhausting the connection pool during dev hot-reload.
const g = globalThis as unknown as { prisma?: PrismaClient };
export const prisma = g.prisma ?? new PrismaClient();
if (process.env.NODE_ENV !== "production") g.prisma = prisma;
