import { NextResponse } from "next/server";
import { getCurrentUser, isEmailAllowed, ensureUserRow } from "@/lib/auth";

// Called right after a successful sign-in to create the app `User` row.
export async function POST() {
  const user = await getCurrentUser();
  if (!user?.email || !isEmailAllowed(user.email)) {
    return NextResponse.json({ error: "forbidden" }, { status: 403 });
  }
  await ensureUserRow({ userId: user.id, email: user.email });
  return NextResponse.json({ ok: true });
}
