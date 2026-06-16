import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Env comes from the repo-root .env, loaded by the root `npm run dev` script
  // (dotenv -e .env) and inherited via process.env — never a webapp ../.env.
};

export default nextConfig;
