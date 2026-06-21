# DESIGN.md — Operator Console Design Language

> The crafted, bilingual (AR/EN) design system for the MAS operator console. The brief:
> read as **Linear / Vercel / Stripe-tier craft**, be **Arabic-native** (not bolted-on),
> and never look like generic **AI slop**. This is binding for P2 (see
> [`MASTERPLAN.md`](MASTERPLAN.md)). Every rule traces to the design research in this
> session; the through-line is **replace every framework default with a decision.**

---

## 1. Foundations

### Typography
- **Latin UI/body:** **Geist Sans** (fallback: Inter — acceptable for dense data only).
- **Numerals & code:** **Geist Mono**, with `font-feature-settings: "tnum"` (tabular) on
  every number — costs, run IDs, scores, dates align in columns.
- **Arabic:** **IBM Plex Sans Arabic** — a true multi-script superfamily metrically matched
  to its Latin counterpart (the single best way to avoid "bolted-on" Arabic). Fallback:
  Noto Sans Arabic. **Avoid Cairo** (reads generic); **do not use Rubik for Arabic**
  (self-hosting subsetting is unreliable).
- **Hierarchy from weight + size, not color or chrome.** Three weights only: 400 body /
  500 UI / 600 headings. **Size-dependent tracking:** ~−0.04em on display, ~−0.01em body,
  0 on small text.
- **Arabic specifics:** size +10–15% over Latin; line-height ~1.8 (vs ~1.5) for tashkeel;
  **never `letter-spacing` Arabic** (breaks cursive joins); **no faux-bold** (load real
  weights); no `word-break`/hyphenation; `text-decoration-skip-ink: auto`.

### Color — neutral-led, ONE accent, no AI-purple
Build on **Radix Colors** (12-step, light+dark pairing + APCA contrast for free).
- **Neutral:** `slate` (cool) or `sage` (with teal accent).
- **Accent (default):** **Teal `#12A594`** (Radix Teal 9) — 2026 "crafted" signature.
  Alternative: refined **Blue `#0090FF`** (Radix Blue 9). One accent, used **only for
  meaning** (active, primary action, selection) — never decoration.
- **Semantic:** success `#30A46C` · warning `#FFC53D` (dark text) · error `#E5484D` ·
  info = accent.
- **Step contract:** 1–2 backgrounds · 3–5 component bg (rest/hover/press) · 6–8 borders
  (subtle/interactive/focus) · 9–10 solid fills · 11 muted text · 12 high-contrast text.
  Body text = step 12 on 1/2; muted = 11. Text is **never pure black/white**.
- **Dark mode:** base `~#121212–#1E1E1E` (not pure black); depth = **surface + hairline
  border**, not shadow.
- **HARD AVOID:** `#6366f1`/`#7C3AED` indigo-violet, purple→blue gradients on near-black,
  ambient blurry gradient blobs/mesh — the literal "AI built this" tells.

### Tokens (drop-in)
```css
/* spacing — 4px base, 8px rhythm */
--space-1:4px; --space-2:8px; --space-3:12px; --space-4:16px;
--space-6:24px; --space-8:32px; --space-12:48px; --space-16:64px;
/* radius — tight = tool, not toy */
--radius-sm:4px; --radius-md:6px; --radius-lg:8px; --radius-full:9999px;
/* borders/elevation — dark leans on border, light on shadow */
--border-subtle:1px solid rgb(255 255 255 /.08);
--border-strong:1px solid rgb(255 255 255 /.15);
--shadow-sm:0 1px 2px rgb(0 0 0 /.05);
--shadow-md:0 4px 6px -1px rgb(0 0 0 /.1);
/* motion — feedback, not decoration */
--motion-fast:140ms; --motion-base:200ms; --motion-slow:260ms;
--ease-out:cubic-bezier(0.23,1,0.32,1);
--ease-drawer:cubic-bezier(0.32,0.72,0,1);
```
Animate **`transform`/`opacity` only**, sub-300ms, `ease-out`. Never animate Cmd-K or
high-frequency surfaces. Stagger lists 30–80ms. Honor `prefers-reduced-motion` (reduce to
~0.01ms + drop parallax; keep fades/skeletons/state feedback).

---

## 2. Component & tech stack
- **Components:** shadcn/ui (own the code) on Radix; Base UI as escape hatch.
- **Styling:** Tailwind v4 (CSS-first `@theme`). Rewrite `globals.css` tokens, non-default
  base color + radius + fonts (never the default shadcn look).
- **Charts:** Recharts (default) · Tremor (dashboard blocks) · visx isolated for ≤2 hero charts.
- **Tables:** TanStack Table + TanStack Virtual (dense run/cost ledgers).
- **Command palette:** cmdk. **Forms:** react-hook-form + zod. **Toasts:** sonner.
  **Icons:** Lucide or Phosphor — **never emoji-as-icons.**

---

## 3. Patterns for this app
- **Run/job monitoring:** status = **dot + text + entity name** (never color alone);
  **animate only while in-flight**, freeze on terminal. **Kill-switch-aborted is its own
  outcome**, not "failed." Optimistic trigger (queued instantly). Stream logs inline,
  grouped per stage (errors red / warnings yellow).
- **Cost dashboard:** cost attached **at the leaf span, totals derived**; prefer real
  ingested cost, infer-from-price only as a **labelled** fallback; slice by **`brandId` +
  `run`** (never per-user/tier); **live spent/cap bar on the run itself** (the kill-switch's
  visual home); break cost by token type (uncached in / cache read / cache write / output).
- **Pipeline viz:** a **tree** (structure) + a **timeline/Gantt waterfall** (where time/cost
  went); each bar one click to its stage logs.
- **Artifact review (human-in-the-loop):** show **the artifact + a diff vs last approved** —
  never "agent will publish X." **Approve-with-edits**, not binary. Approval = durable
  pause/resume on a run ID the UI re-attaches to (survives restart).
- **Empty/loading:** skeletons mirroring real layout for full loads; spinner for one module;
  nothing under ~300ms. Empty states do a job ("No runs yet" → links to trigger).
- **Navigation:** **Cmd+K is the product** (jump to brand, trigger run, kill run) + single-key
  shortcuts; sidebar recedes (dimmed, smaller icons).

---

## 4. RTL + Arabic (native, not mirrored)
- **Logical properties everywhere** — Tailwind `ms-*/me-*/ps-*/pe-*/start-*/end-*`, never
  `ml/mr/left/right`. One stylesheet both directions; reserve `rtl:`/`ltr:` only for physical
  cases (transforms, directional icon flips).
- **`dir` + `lang` on `<html>`**; flex/grid auto-mirror.
- **`transform: translateX()` does NOT auto-flip** — handle in RTL explicitly.
- **Mixed-direction is the #1 bug:** wrap every dynamic Latin/number/hashtag/mention token
  in **`<bdi>`** (or `dir="auto"`) so it can't spill direction onto an Arabic run.
- **Western numerals (0–9)** in the dashboard (operator + KPI expectation).
- **Fonts:** two `next/font/google` calls → `--font-latin`, `--font-arabic`
  (`subsets:['arabic']`, `display:'swap'`), self-hosted at build.

---

## 5. Accessibility & the "10 rules"
- Design with **APCA** (Lc 60 content min, 90 body); ship against **WCAG 2.x AA**. Don't
  claim "WCAG 3."
- `:focus-visible` always (never `outline:none` without a ≥3:1 replacement ring).
- Tab order = DOM = reading order; composite widgets get **roving tabindex** (one tab stop +
  arrows). Cmd-K: arrows move, Enter activates, **Esc closes + restores focus**, focus trapped.

**The 10 rules (the checklist P2 is graded against):**
1. One accent, only for meaning; text never pure black/white; no purple/gradient-on-black.
2. Color on Radix 12-step semantics, not raw hex.
3. Three weights, size-dependent tracking, tabular figures (Geist + IBM Plex Sans Arabic).
4. Tight everything (4px spacing, 4/6/8 radii, hairline borders, separators removed).
5. Motion is feedback (sub-300ms, ease-out, transform/opacity only, reduced-motion honored).
6. Status = dot + text + entity; animate only in-flight; kill-switch-aborted is its own state.
7. One cost ledger: cost at the leaf, totals derived, sliced by brand+run; live spent/cap bar.
8. Review artifact + diff, never the verb; approve-with-edits; durable pause/resume.
9. Arabic is native (logical props, `<bdi>`, Western numerals, bigger size/leading, never
   letter-spaced, never faux-bold).
10. Cmd-K is the product; real data density is the craft. Every default → a decision.
