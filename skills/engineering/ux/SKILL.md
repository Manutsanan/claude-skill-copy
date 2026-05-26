---
name: ux
description: ALWAYS use for ANY task involving website/app design, UI changes, or visual appearance — designing new components, building/editing pages, styling, layout, colors, spacing, animations, responsive breakpoints, accessibility, mockup-to-code, redesigns, polish work, or any request to "make it look better/nicer/modern". Trigger on Thai keywords ออกแบบ/ดีไซน์/ปรับหน้าตา/ปรับ UI/แต่ง UI/ทำให้สวย/ทำให้ดูดี/ทันสมัย/responsive/หน้าจอ/หน้าเว็บ/component/ปุ่ม/สี/layout/animation/ลูกเล่น and English keywords design/redesign/restyle/UI/UX/style/styling/layout/look/appearance/visual/component/page/screen/responsive/mobile/tablet/desktop/animation/transition/polish/modern/aesthetic/Tailwind/CSS. Use proactively WITHOUT being asked whenever editing .vue/.tsx/.jsx/.html/.css files for visual changes, or when user mentions wanting things to look different/better/modern/responsive. Examples: "ปรับ UI ให้สวย", "ทำหน้านี้ใหม่", "redesign this page", "review accessibility", "implement this mockup", "improve UX", "เพิ่ม animation", "ทำให้ responsive", "ปรับสี", "จัด layout".
---

# ux — Visual / Interaction Design

3 modes (pick by intent):

1. **Design from spec/mockup** — user sends mockup / image / description
2. **Review UI** — user asks to inspect / analyze / find issues
3. **Improve UX** — user asks for improvement without specifying a problem

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (see `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: ux | cross` + keyword (component, page, theme, animation, responsive, a11y)
- **Learnings filter:** `~/.claude/skills/ux/learnings.md` by Tags (max 5)
- **Conflict check:** never redesign anything that memory says "convention is X" — ask user first
- **Pre-flight:** read project CLAUDE.md (design system, theme config) + existing components + theme config (`app.config.ts` intended variant)

---

## Progress tracker

Copy this block into your first response. Tick boxes as you go — do not declare "done / it's pretty" before every box is ticked.

```
UX progress:
- [ ] Memory + theme config + existing components scanned
- [ ] Mode picked (1: design from mockup / 2: review UI / 3: improve UX)
- [ ] Design directions explored (4-5 HTML stubs) — or explicitly skipped with reason
- [ ] Reusable components / utilities checked before writing new
- [ ] Semantic HTML chosen before styling
- [ ] Design system used before custom CSS
- [ ] Visual states covered (loading/empty/error/success/partial/unauthorized/max)
- [ ] Responsive plan (sm/md/lg/xl) with string literal classes
- [ ] Interaction spec (hover/focus/active/disabled/loading)
- [ ] Animation spec (or explicitly "no animation")
- [ ] Accessibility (a11y) checked (aria-label, contrast, focus ring, reduced-motion)
- [ ] Handoff checklist ux→fe ticked (if handing off)
- [ ] Quality gates passed (Vite compile / 375–1440 viewports / no horizontal scroll)
- [ ] Cross-browser visual verified (Firefox + WebKit) — or explicitly skipped with reason
```

---

## Handoff (ux is the middle stage of pipeline `sa → ux → fe`)

**Receive from `sa`** (if any): user story + state machine + data constraint + acceptance criteria
- design visuals covering every state (loading/empty/error/success/partial/unauthorized/max-boundary)
- if a spec gap is found during design that cannot be self-answered → **yield back to `sa`**, do not guess

**Send to `fe`** when design is complete:
- component map — which Nuxt UI component to use
- Tailwind class plan — actual string literals (so JIT can scan)
- visual state map — state ↔ data state
- animation spec — property / duration / easing / trigger
- responsive plan — class set for each breakpoint
- interaction spec — hover / focus / active / disabled / loading

**Checklist ux → fe (all ticked before handoff):**
- [ ] component map complete
- [ ] Tailwind classes are string literals (no values from variables)
- [ ] visual state map covers every state from sa
- [ ] responsive plan for every breakpoint (sm/md/lg/xl)
- [ ] interaction spec complete (hover/focus/active/disabled/loading)
- [ ] animation spec, or explicitly state "no animation"

**Receive back from `fe`** when design is not feasible → adjust and resend

---

## Mode 1: Design from mockup

**Step 0: Design direction exploration (when design is open-ended)**

Before implementing a single direction — generate 4-5 lightweight HTML stubs with distinct design personalities:
- Each stub: full-page or component layout, real Tailwind classes (CDN), named theme (e.g., `minimal`, `brutalist`, `tokyo-fintech`, `warm-card`, `data-dense`)
- Each stub is independently openable in browser via MCP `navigate_page` — user clicks through to pick
- User picks a direction; only then begin full implementation
- Skip this step when: mockup is fully explicit (pixel-perfect spec given), or user says "implement as-is"

Naming convention: `design-direction-<slug>.html` — save to project root or `/tmp/` for session use

1. **Read every detail of the mockup** — color, font, size, spacing, radius, shadow, gradient — do not guess
2. **Look for reusable components / utilities** in the project before writing new
3. **Semantic HTML before styling** — `<button>` not `<div onClick>`; `<nav>`, `<img alt>`
4. **Use design system before custom CSS** — Nuxt UI / shadcn / MUI
5. **Map colors directly** — do not arbitrarily convert to a "close" token
6. **Outer → inner** — big layout first, then component, then detail

**Post-write checklist:** match mockup on every element / icon-only buttons have aria-label / disabled is clear / hover-active-focus complete / main responsive breakpoints viewable

---

## Mode 2: Review UI

Always read the real code before commenting

**Accessibility:** icon-only has `aria-label` / img has `alt` (alt="" if decorative) / input has `<label for>` / contrast ≥ 4.5:1 / focus ring visible / modal has focus trap + Esc closes / `lang="th"` on html

**Responsive:** test 375/768/1280px / tap target ≥ 44×44 / body font ≥ 14px / input ≥ 16px (iOS no-zoom) / no horizontal scroll / overflow uses `truncate` / `line-clamp`

**Hierarchy:** heading order matches importance / consistent spacing scale (4/8/12/16/24) / alignment coherent within groups

**States:** loading = skeleton/spinner / empty = message + guidance / error = readable message + retry / success = immediate feedback

Report: list issues + **severity** (blocker / major / minor) + file:line

---

## Mode 3: Improve UX

Find friction points:
1. **Too many clicks/taps** — how many steps does the task take? can it be reduced?
2. **Unclear affordance** — does color/shadow/cursor signal that it's clickable?
3. **Unclear system state** — loading/progress/toast after action
4. **Hard reading order** — does visual hierarchy lead the eye to the most important thing first?
5. **Inconsistency** — same kind of button/spacing differs?
6. **Edge cases missed** — long text overflow / empty / slow network

Propose as **small patches one spot at a time** — do not overhaul unless necessary

---

## Universal principles

- **Mobile-first in mind** — write base mobile, enhance with up-breakpoints
- **Consistent spacing scale** — 4/8/12/16/24/32, not random values
- **Touch target ≥ 44×44px** on mobile
- **Contrast ≥ 4.5:1** body text
- **Never use color as the sole signal** — add icon/label for color blindness
- **Animation ≤ 300ms** UI feedback; 0ms if `prefers-reduced-motion`
- **Clear z-index** — modal > dropdown > tooltip > sticky > content

---

## Modern aesthetic

**Looks modern, clean, tasteful** — neither pure flat nor skeuomorphic

- **Airy spacing** — 16/24/32 over 8/12 to let content breathe
- **Consistent border radius** — pick one scale (`rounded-lg` 8px / `rounded-xl` 12 / `rounded-2xl` 16), never mix
- **Soft & layered shadow** — `shadow-sm` / `shadow-md`, not heavy black; depth via blur
- **Typography hierarchy via weight** — `font-semibold`/`font-bold` + scale 14/16/20/24/32; `leading-relaxed` body
- **Limited color palette** — 1 primary + neutral + 1 accent (success/warning/danger are separate); ≤ 5 families per screen
- **Gradient & glass in moderation** — gradient only for hero/CTA; `backdrop-blur` only for overlay/header
- **Thin border** — `border` 1px, neutral tones (`border-slate-200` / `border-white/10`)
- **Dark mode** — semantic tokens (`bg-background` `text-foreground`), do not hardcode

**Polish:**
- Hover: bg change + shadow lift + scale 1.01–1.02 (no more)
- Focus: `ring-2 ring-primary/50 ring-offset-2`
- Skeleton loading instead of bare spinner
- Empty state: large illustration/icon + inviting copy + CTA

---

## Animation

**Principle:** enhance UX, do not steal attention — if the user notices it = too prominent

**When to animate:** state change (modal/accordion/tab/toast), feedback (button press, hover), continuity (FLIP, reorder), loading (skeleton, progress), attention (pulse badge — use sparingly)

**Do not animate:** scrolling content, page load every time, decorative bg loop, fade-in every line of text

**Timing:**
- micro (hover, press): **100–150ms**
- small (tooltip, dropdown): **150–200ms**
- medium (modal, drawer): **200–300ms**
- large (hero): **300–500ms**, rarely used

**Easing:**
- `ease-out` enter (fast start, slow end — feels responsive)
- `ease-in` exit (slow start, fast end — disappears quickly)
- `ease-in-out` loop
- avoid `linear` except for progress
- playful: `cubic-bezier(0.34, 1.56, 0.64, 1)` (overshoot)

**Properties (GPU-cheap):** `transform` (translate/scale/rotate), `opacity`, `filter` (watch out, heavy)
**Avoid:** animating `width`/`height`/`top`/`left`/`margin` — janks → use `transform`

**Patterns:**
- Fade + slide: modal/drawer (`opacity 0→1` + `translateY 8px→0`)
- Scale + fade: dropdown/popover (`scale 0.95→1` + `opacity 0→1`, transform-origin at trigger)
- Stagger list: children enter every 30–50ms (≤ 5 items)
- Spring physics: drag/swipe — Motion / Framer Motion / Vue equivalent
- View Transitions API: page/route transition (native, modern)

**Tools Vue/Nuxt:** `<Transition>`, `<TransitionGroup>`, `@vueuse/motion`, CSS `@keyframes`, Tailwind `transition-*` + `duration-*` + `ease-*`

**Accessibility:** respect `prefers-reduced-motion` — every non-essential animation must be wrapped in a media query / JS check; no autoplay that grabs attention; loops must be pausable

**Animation checklist:** ≤ 300ms / mostly `transform` + `opacity` / enter `ease-out`, exit `ease-in` / respect reduced-motion / no idle CPU/GPU loops / smooth 60fps on mobile

---

## Responsive (mandatory for every page, every component)

**Principle:** every design supports every size — mobile-first always

**Breakpoints (Tailwind):** `< 640px` mobile / `sm:` 640 / `md:` 768 / `lg:` 1024 / `xl:` 1280 / `2xl:` 1536

**Standing rules:**
- **Layout:** `flex` / `grid` + `flex-wrap` / `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` — do not hardcode px
- **Width:** `w-full` + `max-w-*` instead of `w-[480px]`
- **Responsive padding/gap:** `p-4 md:p-6 lg:p-8`, `gap-3 md:gap-4 lg:gap-6`
- **Responsive font:** `text-base md:text-lg`, heading `text-2xl md:text-3xl lg:text-4xl`
- **Hidden/show:** `hidden md:block` (desktop nav), `md:hidden` (mobile drawer trigger)
- **Image:** `w-full h-auto object-cover` or `aspect-video` / `aspect-square`
- **Container:** `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8` (or project pattern)
- **Touch target ≥ 44×44px** mobile / **Input ≥ 16px** mobile (no iOS auto-zoom)

**Common patterns:**
- Nav: desktop horizontal → mobile hamburger + drawer
- Table: desktop full → mobile card list or horizontal scroll
- Sidebar: desktop fixed → mobile drawer / bottom sheet
- 2-col form: `grid-cols-1 md:grid-cols-2 gap-4`
- Modal: desktop center → mobile full-screen / bottom sheet
- Card grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`
- Hero: desktop side-by-side → mobile stack

**Edge cases to verify:**
- Very long text — `truncate` / `line-clamp-2` / `break-words`
- Narrow screen (< 360px) — multiple buttons wrap/stack
- Wide screen (> 1920px) — `max-w-*` cap
- Landscape mobile — modal/sheet scrolls internally
- 200% zoom — layout does not break unrecoverably
- Sticky header + virtual keyboard — input may be obscured

---

## Quality gates (before closing work, every mode)

- [ ] **Memory scanned** — quote relevant `feedback_*` UI/design entries
- [ ] **Convention check** — matches design system / theme config, no parallel pattern created
- [ ] **Vite compile** (if template edited) — `curl /<page>` HTTP 200 + dev log has no `Invalid end tag`
- [ ] **Reka UI item value** (USelect/USelectMenu) — items have no `value: ""` / `value: ''` (scan both single + double quote)
- [ ] **Responsive test** at **375 / 390 / 768 / 1024 / 1440px** — MCP `resize_page` + screenshot (preferred) or user screenshot fallback
- [ ] no unintended horizontal scroll
- [ ] tap target ≥ 44×44 mobile
- [ ] text does not overflow/overlap at any breakpoint
- [ ] image not distorted/overflowing
- [ ] nav works on both mobile (hamburger) + desktop
- [ ] modal/drawer works on mobile (within viewport, scroll inside)
- [ ] form fillable on mobile (input not hidden by keyboard)
- [ ] **Skill learnings updated** when finding a lesson that generalizes across projects (Tailwind JIT, Nuxt UI v4 quirk, animation timing, recurring a11y)
- [ ] never declare "done / it's pretty" before passing the checklist — user saying "it looks off" = first scan was not good enough

---

## Chrome DevTools MCP playbook (visual verification after style changes)

> Enable when MCP `chrome-devtools` is available + the task involves visual / responsive / a11y changes — token discipline see `~/.claude/CLAUDE.md`

### When to open browser

- **After finishing a style batch** (not every edit!) — verify visuals before claiming done
- **Before handoff ux → fe** — confirm design intent in browser
- **When implementing responsive plan** — test every real breakpoint, do not guess
- **During a11y review** (Mode 2) — vendor lighthouse score instead of manual inspection

### Visual verification flow (standard)

```
1. navigate_page <localhost url of the edited page>
2. wait_for <selector indicating load complete>
3. take_screenshot                                  ← desktop default 1280
4. resize_page 375 → take_screenshot               ← mobile
5. resize_page 768 → take_screenshot               ← tablet
6. resize_page 1440 → take_screenshot              ← wide desktop
7. (if hover/focus state exists) hover uid=X → take_screenshot
8. close_page when done
```

### Tool selection guide (token-aware — `take_screenshot` first, not `take_snapshot`)

| Need | Tool | Token cost | Rule |
|---|---|---|---|
| View appearance + compare mockup | `take_screenshot` | 1-3k | **ux default** |
| Test breakpoint | `resize_page` + `take_screenshot` | 1-3k/each | Do for every key breakpoint |
| Test real device | `emulate` (mobile/tablet) + screenshot | 1-3k | iPhone/iPad emulation |
| Check a11y score + violations | `lighthouse_audit` (a11y category) | 3-10k | Mode 2 review — always |
| Check hover / focus state | `hover uid=X` → `take_screenshot` | 6-23k | Need uid → snapshot first |
| Check contrast / computed CSS | `evaluate_script "getComputedStyle(...)"` | 100-500 | When unsure if class is applied |
| ❌ Visual + structural | `take_snapshot` | 5-20k | **Forbidden** as screenshot replacement |

### Responsive testing recipe (replaces manual DevTools)

```
For every page with style changes → loop:
- 375 (iPhone SE) → screenshot → check no horizontal scroll, tap target ≥ 44
- 390 (iPhone 14)  → screenshot → check text overflow
- 768 (iPad)      → screenshot → check layout transition
- 1024 (iPad Pro)  → screenshot → check sidebar/nav switch
- 1440 (desktop)   → screenshot → check max-width cap
```

Add results to progress tracker `Responsive plan` with screenshot link or "verified at 375/768/1024/1440"

### A11y audit recipe (Mode 2 review)

```
1. navigate_page <url>
2. lighthouse_audit category=accessibility
3. read violations list → filter blockers (color contrast, missing aria, focus trap)
4. per violation: evaluate_script check real element → quote class/attribute that is wrong
5. report severity + file:line + fix proposal
```

### Anti-patterns (MCP for ux)

- **`take_snapshot` instead of `take_screenshot`** — ux cares about visual, not DOM uid; use snapshot only when need to interact
- **Screenshot every edit** — 1 batch = 1 round of screenshots; not every class change
- **Opening browser without testing responsive** — testing only at desktop = not verified
- **Running lighthouse on every page every task** — only for Mode 2 review or before production claim

### Fallback when MCP is unavailable

- Ask user to send screenshots from every specified breakpoint
- Ask user to open DevTools → toggle device → send screenshot
- State plainly: "design verified at code-level only — not tested in browser"

---

## Playwright MCP playbook (cross-browser visual verification)

> Use after chrome-devtools screenshots pass — validate rendering in Firefox engine + WebKit/Safari engine
> Skip for: color / spacing tweaks that do not involve CSS properties known to differ across engines

### When cross-browser visual check is required (not optional)

- `gap` / `flex` / `grid` / `subgrid` — Firefox and Safari have historically had engine-specific rendering differences
- `position: sticky` + `overflow` combinations
- Custom scroll behavior / `-webkit-overflow-scrolling`
- Font rendering at small sizes — WebKit anti-aliasing differs from Chromium
- `backdrop-filter` / `clip-path` — WebKit support and rendering differs
- `@container` queries — behavior at breakpoint boundaries varies between Firefox, Safari, and Chromium

### Cross-browser visual flow (run after chrome-devtools screenshots pass)

```
1. playwright-chromium: browser_navigate → browser_take_screenshot (baseline — should match chrome-devtools)
2. playwright-firefox:  browser_navigate → browser_take_screenshot (compare vs Chromium)
3. playwright-webkit:   browser_navigate → browser_take_screenshot (compare vs Chromium — WebKit as Safari proxy)
4. For each breakpoint with layout change: browser_resize <width> → browser_take_screenshot × 3 browsers
5. Flag any visual diff → identify CSS property causing it → fix
```

### Decision: chrome-devtools vs Playwright for ux

| Need | Use |
|---|---|
| Lighthouse a11y score | `chrome-devtools` — Playwright has no lighthouse |
| Performance trace (Web Vitals) | `chrome-devtools` — Playwright has no perf trace |
| Device emulation (iPhone / iPad exact model) | `chrome-devtools` — `emulate` tool |
| Interactive a11y tree (uid + hover / focus state) | `chrome-devtools` — `take_snapshot` |
| Cross-browser engine rendering diff | `playwright-firefox` + `playwright-webkit` |
| Responsive at multiple breakpoints per engine | Playwright — `browser_resize` × 3 browsers |

### Anti-patterns (Playwright for ux)

- **Running cross-browser check before chrome-devtools passes** — fix Chromium rendering first, then cross-browser
- **Cross-browser check for every task** — only for CSS properties listed above; color / spacing / font-size tweaks do not need it
- **Treating WebKit screenshot as exact Safari** — WebKit MCP is a proxy; close but not 100% identical to Safari on iOS

### Fallback when Playwright MCP is unavailable

- State: "cross-browser verified in Chromium only via chrome-devtools"
- Ask user to test in Safari / Firefox + send screenshots if CSS properties listed above were touched

---

## Kiosk / display projects

Kiosk screens have fixed size **but the code must still be responsive** — test on laptop, change screen models, demo on iPad

Lock resolution → `transform: scale()` on a fixed container — do not hardcode px everywhere

---

## When "do not" tweak

- Existing pattern + consistent → do not change because "I have different taste"
- Mockup is explicit → follow the mockup
- UX is already good and user did not ask → do not over-engineer

Deciding against the mockup / existing design → notify user + reason, let user choose
