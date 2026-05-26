---
name: fe
description: Use when working on frontend code (Nuxt/Vue/React/TypeScript) — writing components, composables, Nuxt pages/layouts/middleware/server routes, state management, reactivity, type-safety, valibot validation, Nuxt UI components; or reviewing existing frontend code for anti-patterns, reactivity bugs, mutation issues, prop drilling, dead code, unclean naming. Trigger on tasks involving component implementation, composable design, state stores (Pinia/Zustand/useState), `ref`/`reactive`/`computed`/`watch`, props/emits, TypeScript generics, valibot schemas, Nuxt UI (UButton, UModal, UForm, ...), route guards, SSR/hydration, performance. Examples: "เขียน composable นี้ให้หน่อย", "review โค้ด component นี้", "state จัดการยังไงดี", "refactor ให้คลีน", "เขียน schema validate", "ทำไม reactivity ไม่ทำงาน", "หา anti-pattern".
---

# fe — Frontend code helper

2 modes (pick by intent):
1. **Build / refactor** — write or adjust component / composable / store
2. **Review / audit** — find anti-patterns, bugs, dead code, duplication

**Scope:** logic / type / state / reactivity / performance — styling/layout/a11y goes to skill `ux`

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (see `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: fe | cross` + keyword (component, library, error pattern, framework)
- **Learnings filter:** `~/.claude/skills/fe/learnings.md` by Tags (max 5)
- **Conflict check:** conflicts with memory → stop and ask user first
- **Pre-flight:** detect Nuxt version (see below) + read project CLAUDE.md + read existing code first (capture patterns, naming, immutability) + check type definitions before guessing shape

---

## Progress tracker

Copy this block into your first response. Tick boxes as you go — never claim "done" until every box is ticked.

```
fe progress:
- [ ] Memory + project CLAUDE.md + existing code scanned
- [ ] Stack detected (Nuxt 3 / 4 / 3+v4-compat) — quoted in reasoning
- [ ] Mode picked (1: build/refactor / 2: review/audit)
- [ ] Handoff input from sa/ux quoted (1–2 lines) if applicable
- [ ] State location decided (local / composable / store / server)
- [ ] Side-effect lifecycle decided + cleanup planned
- [ ] Types defined before implementation body
- [ ] Validation at boundaries only (valibot safeParse/parse)
- [ ] Nuxt UI used before raw elements (where applicable)
- [ ] Ripple traced (caller ≥ 1 hop): `mcp__codegraph__callers <symbol>` first; fallback `rg` for new-session symbols or literal patterns
- [ ] Context7: library API verified (if implementing new Nuxt UI / Valibot / external lib feature)
- [ ] Quality gates: tsc 0 errors + Vite compile + dev log clean
- [ ] UI verify (if UI changed): golden path + ≥ 2 edge cases + 375px mobile
- [ ] Memory updated (project pattern / skill learnings)
```

---

## Stack default

If project does not enforce a different stack, **default to:**

- **Framework:** Nuxt (v3 / v4) + Vue 3 + `<script setup lang="ts">`
- **UI:** Nuxt UI (`UButton`, `UInput`, `UModal`, `UForm`, ...)
- **Validation:** valibot (not zod / yup)
- **State:** `useState()` primarily; Pinia when large/persist/complex
- **Styling:** Tailwind (ships with Nuxt UI)
- **Type imports:** `#shared`, `#imports`

### Version detection (mandatory in Pre-flight)

| Signal | Conclusion |
|---|---|
| `package.json` `nuxt: "^4.x"` + has `app/` dir | **Nuxt 4** — v4 patterns |
| `package.json` `nuxt: "^3.x"` + no `app/` dir | **Nuxt 3 classic** — v3 patterns |
| `nuxt: "^3.x"` + `compatibilityVersion: 4` + has `app/` dir | **Nuxt 3 + v4 opt-in** — v4 patterns |

Quote detection in reasoning, e.g.: *"This project is Nuxt 3 + v4 compat → use v4 patterns"*

If project uses React/Next/Svelte → follow project; but default mental model = Nuxt + Nuxt UI + valibot

---

## Handoff (fe is downstream of pipeline `sa → ux → fe`)

**Receive from `sa`** (source of truth, do not rename fields arbitrarily):
- API spec, data model, state shape, security finding + ripple list — every file in the list must change together

**Receive from `ux`** (implement as-is, do not reinterpret):
- component map → use the specified Nuxt UI
- Tailwind class plan → exact string literal (JIT-safe)
- visual state map → bind data → visual per ux spec
- animation spec / responsive plan / interaction spec

**Yield back** when gaps appear:
- data model misses edge case → yield `sa`
- design unimplementable → yield `ux`
- security hole found mid-implementation → yield `sa` mode B
- **never hack to ship on your own** — always return to upstream skill

**Before every implementation** — quote spec/design 1-2 lines to prevent drift from sa/ux

---

## Mode 1: Build / refactor

### Order of thinking

1. **where does state live?** — local / composable / store / server — pick the lowest level that works
2. **what is the side effect tied to?** — mount / value change (`watch`) / event / interval — cleanup on unmount
3. **derive before store** — if computable from other state → `computed`/selector, don't duplicate
4. **immutable update** — `[...arr, x]`, `arr.map(...)`, `{ ...obj, k }`, no direct mutation
5. **consistent return shape** — `{ ok: true, data } | { ok: false, error }` across the project
6. **type before implementation** — signature before body

### Vue 3 reactivity essentials

- **`ref` vs `reactive`** — default `ref` (consistent unwrap); `reactive` risks losing reactivity on destructure
- **`computed` must be pure** — no side effects (fetch / mutation) → use `watch`/`watchEffect` instead
- **`watch` vs `watchEffect`** — default `watch` (explicit deps + old value); `watchEffect` when auto-tracking
- **`<script setup>`** — `defineProps` / `defineEmits` / `defineExpose` / `defineModel<T>()` (Vue 3.4+)
- **Props default** (Vue 3.5+): `const { foo = 'bar' } = defineProps<Props>()` — reactive-safe; below 3.5 use `withDefaults`
- **emits typed** — `defineEmits<{ submit: [value: string] }>()`
- **provide/inject** — `InjectionKey<T>` + default value

### Nuxt expertise

See REFERENCE.md sections (load on-demand):
- `#nuxt-directory` — directory structure v3 vs v4
- `#nuxt-auto-imports` — things you must not import because they auto-import
- `#nuxt-state` — `useState` vs Pinia
- `#nuxt-data-fetching` — `useFetch` / `useAsyncData` / `$fetch` + v3/v4 reactivity diff
- `#nuxt-routing` — `navigateTo`, middleware, `definePageMeta`
- `#nuxt-server` — `defineEventHandler`, `readBody`, `createError`
- `#nuxt-ssr` — `import.meta.client/server`, `<ClientOnly>`, hydration

### Composable convention

- Name `useXxx`, return ref/object — only call inside `<script setup>`
- Use `useState` inside composable for shared state — **no module-level `ref`** (leaks between users on SSR)
- Cleanup via `onScopeDispose()` (works outside component lifecycle)
- Return the same operation result shape

### TypeScript

- **Avoid `any`** — use `unknown` then narrow; external lib without types → `.d.ts` shim
- **`as` is an escape hatch** — `as any` then `as Foo` = wrong path
- **discriminated union** for multi-mode state — `{ status: 'idle' } | { status: 'loading' } | { status: 'error', error } | { status: 'success', data: T }`
- **`satisfies`** — `const config = { ... } satisfies Config` (shape-check without widening)
- **generic component** — `<script setup lang="ts" generic="T">` in Vue

### Validation — valibot (default)

- Derive type from schema: `type X = v.InferOutput<typeof XSchema>`, no parallel type declarations
- Schema named `XSchema`, type named `X`; schemas → `shared/schemas/`, types → `shared/types/`
- Validate at **boundaries** only: form input, API response, localStorage parse
- `v.safeParse` at boundary; `v.parse` in server route (auto-throws 400)
- Thai error messages: `v.minLength(8, 'ต้องอย่างน้อย 8 ตัวอักษร')`
- Syntax/examples → REFERENCE.md `#valibot`

### Nuxt UI

Before writing raw elements — check if Nuxt UI provides it: `UButton` / `UInput` / `USelect` / `UForm` + `UFormField` / `UModal` / `UCard` / `UTable` / `UBadge` / `UAlert` / `UTabs` / `UTooltip` / `useToast()`

- `UForm` + `UFormField` + valibot schema directly (`@submit` returns typed data)
- Icon: `icon="i-lucide-check"` (Iconify) — no SVG imports
- Theming: `app.config.ts` → `ui: { colors: { primary: 'blue', neutral: 'slate' } }`
- Full table + UForm code → REFERENCE.md `#nuxt-ui`

---

## Clean code

### Naming
- **Convey meaning, not type** — `tickets` not `arr`; `pendingCount` not `n`
- **boolean prefix `is/has/can/should`** — `isLoading`, `canSubmit`
- **function = verb** — `fetchTickets`, `validateForm`; no generic `data()`, `process()`, `handle()`
- **template handler prefix `on`** — `onSubmit`, `onClick`
- **don't abbreviate into nonsense** — `cnt`/`tk`/`usr` → `count`/`ticket`/`user`
- **file/component** — `kebab-case.vue` or `PascalCase.vue` per project (don't mix)

### Function shape
- **1 responsibility** — if explanation needs "and" = should split
- **early return** to avoid deep nesting
- **arguments ≤ 3** — beyond that take an object: `createTicket({ serviceId, customerName })`
- **> 40 lines** is a signal it does too many things

### Comment
- **default is don't write one** — name things to convey meaning instead
- Write only the **"why"** that the code cannot reveal (external bug workaround, business rule constraint, magic number with source)
- No "what" comments / `// removed` / `// deprecated` / `// TODO without ticket` / dangling `// FIXME`

### Template (Vue)
- **short expressions** — anything more complex than `a && b` → extract to `computed`
- **`v-for` + `v-if` on separate elements** — priority conflicts
- **stable `:key`** — use id, not index, if list can reorder
- **no logic in template** — no long `.filter().map().reduce()` inside `v-for`

### Magic value
- extract constant: `const MAX_RETRIES = 3`
- enum/const object for string unions used in multiple places
- no dangling `setTimeout(fn, 300)` — `const TOAST_DURATION_MS = 300`

### `<script setup>` order
1. `import`
2. `definePageMeta` / `defineProps` / `defineEmits` / `defineModel`
3. composable / store (`const route = useRoute()`)
4. local state (`ref`, `reactive`)
5. computed
6. function (handler, helper)
7. watch / lifecycle (`onMounted`)

Don't shuffle — readers find things faster

### Performance (when needed)
- profile before optimizing (Vue Devtools / React Profiler / Chrome Performance), don't guess
- list rendering: stable unique `key`
- lazy load: route-level + large components not needed immediately
- debounce/throttle: `@vueuse/core` `useDebounceFn`
- virtualize list > ~100 items: `@tanstack/vue-virtual` / `vue-virtual-scroller`

---

## Mode 2: Review / audit

Read the real code before commenting, always cite file:line

### Reactivity bugs
- [ ] direct mutation of array/object (`.push`, `arr[0] = x`, `obj.foo = y`) — per project convention
- [ ] destructure `reactive()` then use — reactivity lost
- [ ] read `.value` in template (auto-unwrap)
- [ ] `computed` with side effect
- [ ] `watch` missing cleanup
- [ ] missing effect dependency (React) — eslint-plugin-react-hooks

### State management
- [ ] duplicated state (derivable but stored separately = desync)
- [ ] state at wrong level (local that should be shared / global that should be local)
- [ ] scattered mutations — should centralize
- [ ] missing `persist()` after mutate (if project has persist convention)
- [ ] inconsistent error shape (throw / null / `{ ok, error }`)

### Type safety
- [ ] `any` / `@ts-ignore` without comment
- [ ] type parallel to schema (declared + zod separately) — derive instead
- [ ] deep `as` cast hiding bugs
- [ ] props without types

### Component design
- [ ] component > ~200-300 lines — can it split?
- [ ] unused prop / emit without listener
- [ ] prop drilling > 3 levels — provide/inject or store
- [ ] logic duplicated template + script — extract `computed`
- [ ] template with complex business logic — extract to `computed`/method
- [ ] inline handler with long logic — extract a method
- [ ] `v-for` + `v-if` on the same element

### Dead / suspicious
- [ ] commented-out code (git history exists)
- [ ] leftover `console.log` debug
- [ ] unused import
- [ ] variable assigned and unused
- [ ] unreachable branch
- [ ] try/catch silently swallows error

### SSR / hydration (Nuxt/Next)
- [ ] calling `window`/`document`/`localStorage` in setup without guard
- [ ] hydration mismatch (date locale, random, time)
- [ ] `import.meta.client/server` guards complete
- [ ] `useState` initialized to a value directly (should be factory function — prevents value leak between users)
- [ ] `useFetch` without stable `key` → duplicate fetches
- [ ] using `$fetch` directly in setup (should use `useFetch`/`useAsyncData`)
- [ ] importing things Nuxt already auto-imports

### Valibot
- [ ] type declared parallel to schema
- [ ] `v.parse` at boundary where `v.safeParse` should be used
- [ ] default English error messages in a Thai app
- [ ] inline nested schema instead of extracting to const

### Nuxt UI
- [ ] `<button class="...">` instead of `UButton`
- [ ] custom modal overlay when `UModal`/`USlideover` exists
- [ ] inline SVG icon instead of `UIcon` + Iconify
- [ ] hardcoded color instead of `color="primary"` (won't follow theme)
- [ ] form with hand-rolled label+error instead of `UForm` + `UFormField`
- [ ] custom alert/banner instead of `useToast()`

### Convention adherence
- [ ] use the same pattern as elsewhere
- [ ] naming matches (camelCase / PascalCase / kebab-case)
- [ ] use the designated lib (validation, http, date)
- [ ] alias imports (`#shared`, `~/`, `@/`)

### Clean code
- [ ] name by type (`arr`, `data`) instead of meaning
- [ ] boolean without `is/has/can/should`
- [ ] function doing many things (needs "and")
- [ ] nesting > 3 levels (early return possible)
- [ ] arguments > 3 not using object
- [ ] long/nested template expressions
- [ ] comments explaining "what" / leftover comment-out
- [ ] dangling magic number/string

### Reporting
List issues + **severity** (blocker = data loss / real bug, major = main anti-pattern, minor = polish) + **file:line** + **suggestion**

Don't quick-fix immediately if user only asked for review — report first, wait for confirm

---

## Agent-native verification (for UI components)

**Principle (from Anthropic internal practice):** embed verification into the artifact itself — not as a separate test file. Components expose their current state via `data-*` attributes so the agent reads DOM directly — no scraping, no guessing.

### When to add data-* attributes

Add on components that have:
- Loading / error / empty / success states
- Form validity or submission state
- Item count / pagination
- Auth / permission gates
- Any state the `verify` skill or MCP needs to confirm

### data-* contract convention

```html
<!-- Loading / async state -->
<div data-state="loading | error | empty | success">

<!-- Item count -->
<ul data-item-count="5">

<!-- Form -->
<form data-form-valid="true | false" data-submitting="true | false">

<!-- Auth gate -->
<div data-auth="authenticated | guest | unauthorized">
```

**Rule:** breaking the `data-*` contract = verification failure — even if the app still works visually. This is intentional: contract integrity ≠ visual correctness.

### 3-surface verification pattern

| Surface | How | When |
|---|---|---|
| Human | Open browser, visually inspect | Manual QA / demo |
| Agent (MCP) | `evaluate_script("document.querySelector('[data-state]').dataset.state")` | During fe quality gate |
| Headless (CI) | `bun verify` / Playwright headless reads data attributes | Pre-merge pipeline |

All 3 surfaces read the same DOM contract — no parallel test logic.

---

## Chrome DevTools MCP playbook (opt-in — runtime verification)

> Enable only when MCP `chrome-devtools` is available + the task requires verifying runtime behavior — **not the fe default** because most logic can be verified with `tsc` + tests

### When to open browser (opt-in trigger)

| Situation | Why MCP is worth it |
|---|---|
| Refactor reactivity / state — suspected reactivity bug | `tsc` doesn't catch reactivity lost; need to click + inspect real state |
| Fix hydration mismatch | Error lives in runtime console, invisible to static check |
| Verify composable side-effect / cleanup | Does `onScopeDispose` fire? → need to perform action + check |
| Suspected memory leak (modal open/close repeat) | Need `take_memory_snapshot` to compare heap |
| UI changed → before claiming done | Golden path verify (replaces "ask user to try") |
| Cross-browser hydration / reactivity difference | Need real Firefox / WebKit engine — use Playwright MCP instead |

**Do not use MCP for:** writing schema, type, composable design pattern, valibot validation — verify with tests, it's faster

### Verification recipes (token-aware)

**A. Reactivity verify (after refactor, need confidence):**
```
1. navigate_page <url of that component>
2. wait_for <element>
3. perform action that should trigger reactivity (click button / change input)
4. evaluate_script "check if computed/ref value changed"
5. list_console_messages — look for warnings like `[Vue warn] Mutating a prop`
```

**B. Hydration mismatch verify:**
```
1. navigate_page <url>
2. list_console_messages → grep "Hydration"
3. if found → evaluate_script compare rendered value
4. inspect source: locale-dependent date, Math.random(), Date.now() in setup
```

**C. Memory leak verify (composable cleanup):**
```
1. take_memory_snapshot ← baseline
2. perform action 5-10 times (e.g. open/close modal using composable)
3. take_memory_snapshot ← after
4. heap growth > 5MB / detached listener > 10 = leak; check onScopeDispose
```

**D. Golden path verify (replaces "ask user to try"):**
```
1. navigate_page → click per spec → fill form → submit
2. list_console_messages — clean
3. list_network_requests — no unintended 4xx/5xx
4. take_screenshot — proof
```

**E. Cross-browser verify (Playwright — when chrome-devtools passes but user reports Firefox / Safari issue):**
```
1. playwright-firefox / playwright-webkit: browser_navigate <url>
2. browser_wait_for <element>
3. browser_console_messages — look for hydration errors specific to that engine
4. browser_evaluate "() => JSON.stringify(<reactive state>)" — compare with Chromium value
5. browser_take_screenshot — visual proof of difference
Note: use chrome-devtools for memory / perf trace; Playwright is for engine-specific behavior only
```

### Tool selection (lean — fe does not care about visual)

| Need | Tool | Token cost |
|---|---|---|
| Console error / Vue warn | `list_console_messages` | 500-2k ⭐ fe default |
| Network fail | `list_network_requests` | 500-5k |
| Inspect ref / computed / store | `evaluate_script` | 100-2k ⭐ verify reactivity |
| Element exists + uid (before clicking) | `take_snapshot` | 5-20k — use only when needed |
| Memory leak | `take_memory_snapshot` ×2 | 4-10k |
| Visual proof for user | `take_screenshot` | 1-3k |

**Rule:** fe defaults to `list_console_messages` + `evaluate_script` — not `take_snapshot`/`take_screenshot` like ux

### Anti-patterns (MCP for fe)

- **Opening browser for every fe task** — fe = code logic; open only for runtime behavior verification
- **Skipping `tsc` + tests and using MCP only** — MCP supplements, does not replace static check; `tsc` 0 errors first
- **`take_screenshot` instead of console check** — fe cares about warnings, not visual appearance
- **Verifying with 1 click** — golden path ≥ 2 edge cases (empty, error) before claiming done

### Fallback when MCP is unavailable

- Ask user to paste console log + steps to reproduce + screenshot
- State plainly: "verified with tsc + test only — runtime not verified"
- Never claim "reactivity fix works" without testing in browser

---

## Context7 MCP integration (opt-in — library API verification)

> Use when implementing **new** API from an external library — Nuxt UI props, Valibot methods, Pinia options, useFetch parameters. Skip if the pattern already exists in `fe/learnings.md`.

### When to query

| Situation | Action |
|---|---|
| First time using a specific Nuxt UI component prop | `resolve-library-id nuxt/ui` → `query-docs "/nuxt/ui <component> <prop>"` |
| Valibot method with uncertain signature | `resolve-library-id fabian-hiller/valibot` → `query-docs "/fabian-hiller/valibot <method>"` |
| Pattern already confirmed in `fe/learnings.md` | Skip — use cached pattern |
| Internal custom composable / no external library | Skip |

### Query discipline (narrow always)

```
# ✅ Good — ~500 tokens
mcp__context7__resolve-library-id libraryName="nuxt/ui"
mcp__context7__query-docs libraryId="/nuxt/ui" query="UButton loading prop"

# ❌ Bad — ~5-10k tokens
mcp__context7__query-docs libraryId="/nuxt/ui" query="Nuxt UI"
```

**After confirming pattern:** save to `~/.claude/skills/fe/learnings.md` → skip query on future occurrences.

---

## When "don't" refactor

- Existing pattern isn't "textbook best" but is consistent → don't introduce inconsistency
- Micro-optimization that profiling doesn't help → don't add unnecessary `useMemo`/`computed`
- Abstraction that "looks clean" but is hard to debug → simple = better

---

## Quality gates (before claiming "done")

### Build / verify (if code was changed)
- [ ] **`tsc --noEmit`** 0 errors
- [ ] **Vite compile** of touched pages — `curl /<page>` HTTP 200 + dev log free of `Invalid end tag`, `SelectItem must have a value prop`
- [ ] **`rtk proxy yarn nuxt prepare`** succeeds (refresh auto-imports + types)

### UI verify (when UI changed)
- [ ] golden path verified — `verify` skill or chrome-devtools MCP playbook section D
- [ ] edge cases ≥ 2 from spec (empty, error) — verify in real browser
- [ ] network tab clean — `list_network_requests` no unintended 4xx/5xx
- [ ] console clean — `list_console_messages` no error/warn regression
- [ ] mobile 375px not broken — `resize_page 375` + screenshot
- [ ] **Agent-native contract** — key visual states expose `data-*` attributes (`data-state` / `data-item-count` / `data-form-valid`) readable via `evaluate_script`

If dev server isn't ready → tell user "cannot verify manually — please test: [steps]" **never claim "done" silently**

### Pattern verification (if scan/migrate/refactor)
- [ ] **Cross-verify with ≥ 2 regex** — loose (`<tag`) + strict (`<tag[\s>]`), results must match
- [ ] **Manual spot-check 2-3 files** before claiming "0 left"
- [ ] **Reka UI value scan** — if using USelect/USelectMenu items: scan both single + double quote for `value: ""` / `value: ''`

### Ripple verification (if shared code was changed)
- [ ] **Trace caller ≥ 1 hop** before claiming "no impact" / "dead code"
- [ ] **Type usage trace** — every consumer compiles + behaves correctly
- [ ] **Wrapper migration** — remove wrapper open + close together

### Memory update
- [ ] **Project memory** if a project-specific pattern/bug appears — add `feedback_<topic>.md`
- [ ] **Skill learnings** if a lesson generalizes across projects (Vue reactivity, TS pattern, Nuxt UI quirk)
- [ ] user says "sure? / check again" = first scan/verify wasn't thorough enough → memo + adjust pattern

### Golden rules

> **Vite compile success + clean dev log = source of truth** for template/runtime
> **`tsc --noEmit` 0 errors = source of truth** for types
> **regex heuristic is not a source of truth** — multi-line constructs skew the count

Never claim "0 left / complete / done" from a single scan
