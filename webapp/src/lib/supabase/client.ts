import { createBrowserClient } from "@supabase/ssr";

/** Browser-side Supabase client (used by the sign-in form). */
export function createSupabaseBrowserClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
  );
}
