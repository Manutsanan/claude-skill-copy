# Learnings — ux

> **Per-skill, cross-project memory** — lessons for skill `ux` usable across every project (Visual/Interaction Design)
>
> **What to store here:**
> - Tailwind CSS pitfalls (e.g. class string literal vs template literal for JIT scan)
> - Nuxt UI v4 component composition patterns (UCard + UForm + UFormField, UModal animation override)
> - Accessibility checklist items often missed (focus ring, ARIA label, color contrast ratio)
> - Animation timing/easing defaults that look good (duration, ease curve, stagger)
> - Responsive breakpoint patterns (mobile-first, when to use container query)
> - Color/spacing token systems that scale (semantic naming vs literal)
> - State visual defaults (when to use loading skeleton vs spinner)
>
> **What NOT to store here:**
> - Brand color / typography specific to a project (that → project memory)
> - Layout structure specific to a project page
> - Mockup-to-code mapping for a specific page
>
> **When to read:** every Pre-flight of skill `ux` (all 3 modes)
> **When to append:** after finishing work, when a generalizable lesson is found (see format in `_template/learnings.md`)

---

## Format per entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** what you were doing when the lesson surfaced — **one line only**
**Lesson:** rule + reason
**How to apply:** what to do next time
```

---

## Entries

<!-- newest on top -->

## figma-thumbnail-unclear-must-search-or-ask

**Tags:** figma, design-reading, thumbnail, node-id, assumption
**Date:** 2026-05-20

**Context:** implemented dashboard stat cards from a top-level Figma node thumbnail that was small and low-res — misread layout in all 3 spots (each stat should be a separate card, icon+% on opposite sides, with bottom color bar) because of guessing from an unclear image
**Lesson:** Figma top-level node thumbnails are often low resolution — child component layout cannot be read accurately. Must search for the node ID that directly shows that component, or ask the user first. Never implement by guessing.
**How to apply:**
- when given a Figma node that is a top-level page → thumbnail gives the overview but child component details are unclear
- before implementing any component → try viewing nearby node IDs (e.g. +1, +2, ...) or nodes whose name/content matches that component
- if a clear node cannot be found → ask the user for the node ID for that component directly
- never conclude "probably like this" and implement — if unsure = must ask

## nuxt-layout-system-must-verify-before-claiming-done

**Tags:** nuxt, layout, app-vue, NuxtLayout, design-verify
**Date:** 2026-05-19

**Context:** implemented a login page with a layout file but forgot to check whether `app.vue` had `<NuxtLayout>` — result: layout not applied, card not centered, bg gradient missing; user had to point out the design was off
**Lesson:** having the layout file + `definePageMeta({ layout: 'x' })` is not enough — `app.vue` must wrap `<NuxtPage>` with `<NuxtLayout>`. Without it, it's as if there is no layout at all (no error, no warning — silent fail)
**How to apply:**
- every time a new layout is created or a page using a layout is implemented → **always check `app.vue` first**
- checklist before claiming design/layout is done:
  1. does `app.vue` have `<NuxtLayout><NuxtPage /></NuxtLayout>`?
  2. does `layouts/<name>.vue` actually exist?
  3. does `definePageMeta({ layout: '<name>' })` in the page match the file name?
  4. **open the browser and look** — `nuxt prepare` passing does not mean the visual is correct
- never trust just type-check or "dev server has no error" — layouts can always silently fail


## tailwind-class-must-be-string-literal

**Tags:** tailwind, jit, class-name, dynamic-class
**Date:** 2026-05-16

**Context:** wrote a design plan like `class="bg-${color}-500"` or composed class from a variable → Tailwind did not generate the CSS → UI did not render the color
**Lesson:** Tailwind JIT scans **string literals** in the source file — it does not evaluate template literals / runtime string concat. If a class is composed from a variable → JIT cannot see it → no CSS rule is emitted
**How to apply:**
- hand class plans to `fe` as full string literals only — never template literals
  ```vue
  <!-- bad :class="`bg-${color}-500`" -->
  <!-- good :class="color === 'red' ? 'bg-red-500' : 'bg-blue-500'" -->
  ```
- if the design genuinely needs dynamic → use a map object containing literals for every option:
  ```ts
  const colorClass = { red: 'bg-red-500', blue: 'bg-blue-500' }[color]
  ```
- alternative: use inline `style` when the value truly comes from runtime (`:style="{ background: color }"`)


## animation-no-pulse-on-stable-ui

**Tags:** animation, ux-principle, kiosk, attention
**Date:** 2026-05-16

**Context:** added `animate-pulse` to the main button of a kiosk page to "draw attention" — users reported it was annoying + felt the page was "stuck"
**Lesson:** Pulse / heartbeat animation on a stable UI element (not a loading state) communicates the wrong thing — users associate it with "loading / processing", not "clickable"
**How to apply:**
- `animate-pulse`, `animate-ping`, `animate-bounce` → use only for **transient state** (loading skeleton, new notification badge)
- to draw attention to a CTA → use **static contrast** (prominent color, larger size, prominent position) + **subtle hover animation** (scale 1.02, shadow elevate) instead
- Kiosk / display screens where the user does not directly interact → no looping animation, as it strains the eyes


## responsive-mobile-first-default

**Tags:** responsive, mobile-first, tailwind, breakpoint
**Date:** 2026-05-16

**Context:** wrote class `lg:grid-cols-3 grid-cols-1` starting the design from desktop → shrinking to mobile → layout broke because default styling was not optimized for small
**Lesson:** Tailwind is mobile-first — `md:`, `lg:`, `xl:` are overrides for **larger** screens, not smaller. Therefore the default class (no prefix) is "mobile size" — design mobile first
**How to apply:**
- class writing order: mobile default → tablet (`md:`) → desktop (`lg:`) → wide (`xl:`)
  ```vue
  <!-- good mobile-first -->
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:gap-6">
  ```
- design plan must spec mobile layout as default — not "desktop, then hide some elements on mobile"
- test order: 375px → 768px → 1024px → 1440px (iPhone SE, iPad, laptop, desktop)
- Touch target ≥ 44×44px on every interactive element on mobile
