import Link from "next/link";
import { LayoutDashboard, ListChecks, Building2, Receipt, type LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

type NavKey = "overview" | "runs" | "brands" | "costs";

const NAV: { key: NavKey; label: string; href: string; icon: LucideIcon; ready: boolean }[] = [
  { key: "overview", label: "Overview", href: "/", icon: LayoutDashboard, ready: true },
  { key: "runs", label: "Runs", href: "/runs", icon: ListChecks, ready: false },
  { key: "brands", label: "Brands", href: "/brands", icon: Building2, ready: false },
  { key: "costs", label: "Costs", href: "/costs", icon: Receipt, ready: false },
];

/** The console frame: a receding sidebar + a quiet topbar. Nav surfaces the
 *  planned IA but only links routes that exist — unbuilt ones read "soon",
 *  never a dead link. */
export function Shell({
  active,
  title,
  email,
  children,
}: {
  active: NavKey;
  title: string;
  email?: string | null;
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen grid-cols-[220px_1fr]">
      {/* Sidebar — dimmed, recedes; the work stays in focus */}
      <aside className="flex flex-col border-r border-hairline bg-panel/40">
        <div className="flex items-center gap-2 px-4 h-14 border-b border-hairline">
          <span className="size-2.5 rounded-full bg-brand" aria-hidden />
          <span className="font-semibold tracking-tight text-ink">MAS Console</span>
        </div>
        <nav className="flex-1 px-2 py-3 space-y-0.5">
          {NAV.map((item) => {
            const Icon = item.icon;
            const isActive = item.key === active;
            const base = "flex items-center gap-2.5 rounded-md px-2.5 py-2 text-sm transition-colors";
            if (!item.ready) {
              return (
                <div
                  key={item.key}
                  className={cn(base, "text-faint cursor-default select-none")}
                  aria-disabled
                >
                  <Icon className="size-4" />
                  <span>{item.label}</span>
                  <span className="ml-auto text-[10px] uppercase tracking-wide text-faint/80">soon</span>
                </div>
              );
            }
            return (
              <Link
                key={item.key}
                href={item.href}
                aria-current={isActive ? "page" : undefined}
                className={cn(
                  base,
                  isActive
                    ? "bg-panel-2 text-ink"
                    : "text-subtle hover:bg-panel-2 hover:text-ink",
                )}
              >
                <Icon className={cn("size-4", isActive && "text-brand")} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-hairline px-4 py-3 text-xs text-faint truncate">
          {email ?? "not signed in"}
        </div>
      </aside>

      {/* Main column */}
      <div className="flex flex-col min-w-0">
        <header className="flex items-center h-14 px-6 border-b border-hairline">
          <h1 className="text-sm font-medium text-ink">{title}</h1>
          <kbd className="ml-auto rounded-sm border border-hairline px-1.5 py-0.5 text-[11px] text-faint tabular">
            ⌘K
          </kbd>
        </header>
        <main tabIndex={-1} className="flex-1 px-6 py-6 max-w-[1100px] w-full">
          {children}
        </main>
      </div>
    </div>
  );
}
