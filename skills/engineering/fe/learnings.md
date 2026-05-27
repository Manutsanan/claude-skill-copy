# Learnings — fe

> **Per-skill, cross-project memory** — lessons for skill `fe` that apply across every Vue/Nuxt/React/TypeScript project
>
> **Store here:**
> - Vue 3 / Nuxt (v3 + v4) reactivity pitfalls (e.g., destructure reactive object, watch on ref vs reactive, computed with side effect)
> - TypeScript patterns (generics, type narrowing, infer)
> - valibot schema conventions (e.g., `InferInput` vs `InferOutput` — when to use which)
> - Nuxt UI component quirks (UButton color/variant, UModal slot, USelect items shape) — note version in entry if quirk is version-specific
> - Pinia / composable conventions reusable across projects
> - Anti-patterns once written and later refactored (e.g., deep prop drilling, useState in wrong place)
>
> **Don't store here:**
> - Project-specific conventions (e.g., "this project uses shared/schemas/" → project memory)
> - Codebase-specific paths / file structure
> - Project-specific business terms
>
> **When to read:** every time during Pre-flight of skill `fe`
> **When to append:** after a task if a generalizable lesson appears (see format in `_template/learnings.md`)

---

## Entry format

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** what you were doing when the lesson appeared — **1 line only**
**Lesson:** rule + reason
**How to apply:** what to do next time
```

---

## Entries

<!-- newest on top -->

## valibot-shared-schemas-convention

**Tags:** valibot, schema, nuxt, auto-import, shared, project-structure
**Date:** 2026-05-27 (graduated from mcop-web-manage-v2 + mcop-web-manage + welfate)

**Context:** Valibot schemas duplicated across pages/composables in 3+ Nuxt projects; each project independently converged on a `shared/schemas/` directory pattern
**Lesson:** In Nuxt projects with Valibot, schemas shared across ≥2 callers belong in `shared/schemas/<domain>/<feature>.ts` (or `shared/types/` for TypeScript types). Nuxt auto-imports everything under `shared/` — no explicit import needed in composables or pages.
**How to apply:**
- New schema that is used in only 1 file → define inline; if a second caller appears → extract to `shared/schemas/`
- Naming: `shared/schemas/<domain>/<feature>.ts` e.g. `shared/schemas/member/memberInfo.ts`
- TypeScript types inferred from schemas go in `shared/types/<domain>.ts`
- Canonical examples (mcop-web-manage-v2 PR #3096): `shared/schemas/auth/auth.ts`, `shared/schemas/auth/login.ts`
- Never duplicate a schema across files — `InferInput` / `InferOutput` from the single shared file is the source of truth

## http-200-and-content-grep-is-not-visual-verify

**Tags:** verify, pdf, advisor, false-confidence, layout
**Date:** 2026-05-23

**Context:** built a PDF receipt page from a Figma mockup; verified by `curl HTTP 200` + grep of expected Thai strings in rendered HTML — advisor caught a real bug in the same turn: table footer `<td colspan="4">` should have been `colspan="3"` so the "รวม / total_amount / total_remaining" cells aligned under the right column headers
**Lesson:** content presence ≠ structural correctness. A page can return HTTP 200 with every expected string rendered and *still* be visually wrong (wrong colspan/rowspan, swapped column order, mis-aligned grid). HTTP 200 + grep only proves the page didn't crash and the data binding flowed — it proves nothing about layout fidelity to a mockup.
**How to apply:**
- When building from a mockup (Figma/PNG/PDF), the verify step must be **visual** — open in a browser and eyeball it against the mockup, or take a screenshot. Never substitute curl + grep.
- For tables specifically — re-count colspan/rowspan against the visual cell grid before declaring done. The mockup's footer cells dictate colspan, not the data fields.
- Call `advisor` *before* the visual verify (not after) when you can't visually verify yourself — advisor reads structure too and can catch the colspan-class bugs that curl can't.

## select-item-value-must-not-be-empty-string

**Tags:** nuxt-ui, reka-ui, USelect, USelectMenu, runtime-error
**Date:** 2026-05-16

**Context:** used `USelect` / `USelectMenu` and got `SelectItem must have a value prop that is not an empty string` thrown at mount
**Lesson:** Reka UI (the engine behind Nuxt UI v3+ select components) forbids `value: ''` in `items` array because empty string is reserved for "no selection" inside Radix/Reka — passing `''` throws at runtime immediately
**How to apply:**
- Never use `''` as a placeholder option — use `null`, `undefined`, or omit it entirely instead
- For "any value / all" → use a string sentinel that isn't `''`, e.g. `'__ALL__'`
- When migrating native `<select>` with `<option value="">` → map to `null` before passing into items
- Scan both single + double quote: `rg "value: ['\"]['\"]"` before assuming safe

## slot-existence-not-reactive-in-template-vif

**Tags:** vue3, slot, reactivity, template
**Date:** 2026-05-16

**Context:** used `<template v-if="$slots.actions">...</template>` to render a section only when the slot exists — but the section disappears/appears at the wrong time on some renders
**Lesson:** Vue 3 `$slots.<name>` is not reliably reactive inside `<template v-if>` — it's an object reference Vue does not track as a dep of normal effects, so it fails to re-evaluate when parent re-renders
**How to apply:**
- Don't use `v-if="$slots.X"` to branch important UI
- If you must check slot existence — use `computed(() => !!slots.X)` in `<script setup>` and reference that computed in the template
- Or design the parent to pass an explicit `:showActions="boolean"` prop instead of probing slots


## destructure-reactive-loses-reactivity

**Tags:** vue3, reactive, ref, composable, reactivity
**Date:** 2026-05-16

**Context:** wrote a composable that returns `reactive({ count, items })` then a consumer did `const { count } = useFoo()` — UI doesn't update when count changes
**Lesson:** Destructuring a value out of `reactive()` yields a "primitive snapshot" — the reactive link breaks immediately (Vue tracks the proxy of the object, not the value destructured out)
**How to apply:**
- Composable returns `reactive({...})` → consumer must destructure via `toRefs()` or `toRef()`
  ```ts
  // ❌ const { count } = useFoo()
  // ✅ const { count } = toRefs(useFoo())
  // ✅ const count = toRef(useFoo(), 'count')
  ```
- Best practice: composable returns `refs` directly from the start — `return { count: ref(0), items: ref([]) }` instead of `reactive({...})` — consumers can destructure straight without toRefs
- React equivalent pitfall: passing `{...state}` into useState — different primitive snapshot, but conceptually similar problem

## nuxt-icon-collections-must-match-source

**Tags:** nuxt-icon, iconify, bundle, missing-collection, dev-server-restart
**Date:** 2026-05-27 (graduated from mcop-web-manage + mcop-web-manage-v2)

**Context:** A `<Icon :name="collection:icon">` references an Iconify collection that isn't installed as `@iconify-json/<collection>` → icon renders empty → buttons look invisible → user sees a blank cell where there should be an action button. Independently happened in 2 Nuxt projects.
**Lesson:** Every Iconify collection prefix used in source must have its matching `@iconify-json/<collection>` package installed AND the dev server restarted after install (Nuxt Icon discovers collections at server start only, not via HMR).
**How to apply:**
- After adding a new `<Icon name="...">`, after migrating components from another repo, or after pulling a branch that introduces new icons → scan + reconcile before claiming done
- Use multiple scan patterns — single-quote, double-quote, multi-line `<Icon\n  name="...">`, dynamic `:name="\`prefix:${var}\`"`, data arrays `icon: "..."`, custom-icon-class props
- Similar-looking prefixes are **different packages**: `bx` ≠ `bxs`, `streamline` ≠ `streamline-ultimate`, `fa6-brands` ≠ `fa6-solid`
- After `yarn add @iconify-json/*` → restart dev server (HMR will not pick up new collection registry)
- Production acid test: `rm -rf .nuxt .output && yarn build` — if build succeeds, every referenced icon has a registered data source
- See full scan-pattern playbook + detection scripts in source project memories (mcop-web-manage-v2/`feedback_icon_bundling_workflow`, mcop-web-manage/`feedback_iconify_packages_must_match_usage`)

## vite-cache-recovery-rules

**Tags:** vite, nuxt, dev-server, cache, hmr, dep-install, syntax-error
**Date:** 2026-05-27 (graduated from mcop-web-manage + mcop-web-manage-v2)

**Context:** Two distinct but related Vite/Nuxt dev-server cache pitfalls that recurred across 2 projects — `Re-optimizing dependencies` after `yarn add` doesn't invalidate all pre-bundled chunks; and Vite caches a module's parse error across HMR cycles, refusing to re-parse even after the disk content is fixed.
**Lesson:** Vite's dev-server cache is not always trustworthy. Some state changes require a full process restart, not HMR.
**How to apply:**

| Trigger | Action |
|---|---|
| Ran `yarn add` / `yarn workspace <app> add` while dev server was running | Stop server → `rm -rf .nuxt node_modules/.cache` → restart |
| Added a new Iconify collection package | Same as above (Nuxt Icon discovers on startup only) |
| Added a new `@source` path in Tailwind config | Restart dev server (JIT scans paths at startup) |
| Vite reports a syntax error pointing at line content that **doesn't match the disk** anymore | TaskStop + restart dev server. HMR cannot recover — touching, re-saving, deleting+recreating the file all fail |
| Same error after cache clear (hash changed but message identical) | Suspect corrupt install — check `ls node_modules/<pkg>/dist/` exists; if not, nuke `node_modules` at workspace root + apps/* + packages/* and reinstall |

- Pure source-code HMR edits do NOT require a restart — cache is valid in that case
- See full detection scripts + escalation playbook in source project memories (mcop-web-manage/`project_vite_cache_after_install`, mcop-web-manage-v2/`feedback_vite_cache_stuck_after_syntax_error`)

