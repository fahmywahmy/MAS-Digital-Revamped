import { type NextRequest } from "next/server";
import { updateSession } from "@/lib/supabase/middleware";

// Keeps the Supabase session cookie fresh on every navigation. Page-level
// authz (allowlist) is enforced in the pages/routes themselves.
export async function middleware(request: NextRequest) {
  const { response } = await updateSession(request);
  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|ico)$).*)"],
};
