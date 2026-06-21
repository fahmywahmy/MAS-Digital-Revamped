import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Env comes from the repo-root .env, loaded by the root `npm run dev` script
  // (dotenv -e .env) and inherited via process.env — never a parent-dir .env
  // climbed to from the webapp.
};

export default nextConfig;
