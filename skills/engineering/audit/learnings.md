# Learnings — audit

> **Per-skill, cross-project memory** — audit lessons usable across every project
>
> **How does this differ from project memory?**
> | | Project memory (`~/.claude/projects/<id>/memory/`) | Skill learnings (this file) |
> |---|---|---|
> | Scope | only that project | across every project using audit |
> | Content | "finding X user accepted as intentional" | "audit default heuristic / pitfall / false-positive pattern" |
> | Example | "intentional dead code in legacy/ — being migrated" | "Vue tests asserting toBe(true) are usually weak in every project" |
>
> **When to append a new entry:**
> - After every audit run **if** you found:
>   - a reusable heuristic — e.g. "every Nuxt project tends to bloat from full lodash"
>   - a false-positive pattern — e.g. "vue-tsc doesn't count `<script setup>` macros as callers → wrong trace"
>   - a default tool choice that works well — e.g. "`pnpm why` beats `pnpm ls` for duplicate transitive"
>   - a signal that flags better than the previous method
> - **Do not append** business rules / user preferences for a single project (those → project memory)
>
> **When to read:** every time in Phase 0.5 — grep tags/keywords of the stack detected in Phase 1 → apply before starting scan
>
> **Pruning:** stale entries (tool deprecated, framework API changed) → delete or mark `~~deprecated~~`

---

## Format per entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** situation where the lesson came up (1-2 lines)
**Lesson:** rule + short reason why
**How to apply:** what to do next time when a similar situation arises
**Related:** [[other-learning-slug]] or link to project memory if any
```

---

## Entries

<!-- newest on top — append new entries here -->

## console-log-in-production-grep

**Tags:** dead-code, logging, production, nuxt, vue
**Date:** 2026-05-26

**Context:** common oversight across nearly every project audited — `console.log` left in production build
**Lesson:** `console.log` / `console.warn` / `console.error` used for debugging almost always survive to production unless a lint rule or build config strips them. They leak internal data shapes to browser DevTools.
**How to apply:**
- Phase 2 dead-code scan: `rg "console\.(log|warn|error|debug|info)" --type ts --type vue` — ignore only lines inside `.catch` or explicit error boundaries (those are intentional)
- Flag any `console.log` that outputs API response, user data, or internal state as **High**; others as **Low**
- Fix: use a logger utility that respects `process.env.NODE_ENV`, or configure Vite's `drop: ['console']` in production build


## lodash-full-import-bundle-bloat

**Tags:** performance, bundle, lodash, lodash-es, vue, nuxt
**Date:** 2026-05-26

**Context:** every Vue/Nuxt project audited has at least one file doing `import _ from 'lodash'` for only 1-2 functions
**Lesson:** full `lodash` import adds ~71KB (minified) to the bundle. `lodash-es` is tree-shakeable but requires named imports per function. Most projects use whole-lodash because it was copy-pasted from a StackOverflow snippet.
**How to apply:**
- Start every performance scan with: `rg "import \w+ from ['\"]lodash['\"]"` (whole import — not `lodash-es`)
- Flag every hit as **Medium** (bundle bloat)
- Fix per case: `import debounce from 'lodash-es/debounce'` (named) or replace with native alternative if simple


## script-setup-macro-false-negative-in-tsc-unused

**Tags:** vue3, script-setup, tsc, false-positive, unused-variable
**Date:** 2026-05-26

**Context:** `tsc --noEmit` reported 0 unused variables, but audit found `defineProps`, `defineEmits`, `withDefaults` used in `<script setup>` that vue-tsc doesn't always count as "callers" of imported types
**Lesson:** vue-tsc / standard tsc don't fully understand `<script setup>` compiler macros as callers. An import used only inside a macro (e.g. `const props = defineProps<MyProps>()`) may be reported as unused by some tsc versions.
**How to apply:**
- Never trust `tsc --noEmit` alone for "unused export" findings in Vue files — always cross-verify with `rg "<TypeName>" --type vue`
- Only flag an export as dead code when BOTH tsc reports it AND `rg` finds no template/script consumer


## missing-lazy-image-and-explicit-size

**Tags:** performance, lighthouse, image, a11y, nuxt, vue
**Date:** 2026-05-26

**Context:** Lighthouse performance scan flags images without explicit width/height and without `loading="lazy"` on below-fold images across most projects
**Lesson:** Two image attributes are almost universally missing in Vue/Nuxt projects:
1. `loading="lazy"` on images below the fold — causes render-blocking image loads
2. Explicit `width` + `height` — causes Cumulative Layout Shift (CLS) score penalty
**How to apply:**
- Performance scan: `rg "<img" --type vue | grep -v "loading="` — flag hits as **Medium**
- `rg "<img" --type vue | grep -v "width="` — flag hits as **Medium** (CLS risk)
- For Nuxt: `<NuxtImg>` from `@nuxt/image` handles both automatically — suggest migration if the module is already installed
- Exception: hero images above the fold should NOT have `loading="lazy"` (they should load immediately)


## unused-env-variables-in-dotenv

**Tags:** security, config, env, secret, dead-code
**Date:** 2026-05-26

**Context:** audited `.env.example` and `nuxt.config.ts` runtimeConfig — found variables defined in env but never referenced in code, and variables referenced in code but missing from `.env.example`
**Lesson:** env variable drift is common: dev adds `NUXT_SECRET_X` to `.env.local`, uses it, but forgets to add it to `.env.example`. Later a new dev doesn't know it's needed. Conversely, old env vars that are no longer used stay in `.env.example` forever.
**How to apply:**
- Two-way check:
  1. Every key in `.env.example` → `rg "process.env.<KEY>|runtimeConfig.<key>" --type ts` — if 0 hits → flag as dead env var
  2. Every `runtimeConfig` key in `nuxt.config.ts` → must exist in `.env.example` — if missing → flag as undocumented requirement
- Security: flag any env key with `SECRET`, `KEY`, `TOKEN`, `PASSWORD` that appears in `public` section of runtimeConfig (exposed to client)
