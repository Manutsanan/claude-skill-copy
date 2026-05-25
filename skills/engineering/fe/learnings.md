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

