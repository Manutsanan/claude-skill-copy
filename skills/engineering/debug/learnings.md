# Learnings — debug

> **Per-skill, cross-project memory** — lessons for skill `debug` that apply across all projects (Bug diagnosis & fix)
>
> **What to keep here:**
> - Symptom → root cause mappings that generalize across projects (e.g. `SelectItem must have a value prop that is not an empty string` → items array contains `value: ''`)
> - Framework-specific bug patterns (Vue reactivity loss, Nuxt hydration mismatch, Pinia store re-init)
> - Console error messages that are misleading + how to trace the real cause
> - Debug techniques that work especially well with this stack (Vue Devtools tip, network panel filter, source map config)
> - Anti-patterns in debugging that have caused mistakes (fixing symptom instead of root cause, forgetting to scan ripple)
>
> **What not to keep here:**
> - Bugs specific to project business logic (those → project memory)
> - One-shot fix commits that are not a pattern (git log has those)
>
> **When to read:** every time in Pre-flight of skill `debug` — grep with keywords from the error message or symptom
> **When to append:** after finishing work if root cause is a generalizable pattern (see format below)

---

## Per-entry format (focus on symptom → root cause)

```markdown
## <kebab-case-symptom-slug>

**Tags:** framework, component, error-type, ...
**Date:** YYYY-MM-DD

**Symptom:** what user/console sees (1 line)
**Root cause:** actual cause (not the symptom)
**Fix pattern:** fix that works for the same pattern
**Detection:** how to find this bug (grep pattern, devtools step, log location)
```

---

## Entries

<!-- newest on top -->

## ssr-cannot-read-getSSRProps-undefined-directive

**Tags:** nuxt3, vue3, ssr, custom-directive, migration
**Date:** 2026-05-20

**Symptom:** SSR crash: `Cannot read properties of undefined (reading 'getSSRProps')` — page fails to render server-side
**Root cause:** A custom directive (e.g. `v-guard`) is applied in a template but was **never registered** via plugin. During SSR, Vue resolves the directive name → gets `undefined` → tries `undefined.getSSRProps(...)` → throws. No optional chaining protects this call.
**Fix pattern:**
1. Create `directives/<name>.ts` with the directive logic + add `getSSRProps: () => ({})` for SSR no-op
2. Register via `plugins/<name>.ts`: `nuxtApp.vueApp.directive("name", directive)`
3. Plugin does NOT need `.client.ts` suffix — `mounted`/`unmounted` hooks auto-skip on server; `getSSRProps` handles the server render path

```ts
// directives/inputGuard.ts
export default {
  getSSRProps: () => ({}),  // ← required for SSR compatibility
  mounted(el, binding) { ... },
  unmounted(el) { ... },
}

// plugins/inputGuard.ts
import inputGuard from "../directives/inputGuard"
export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive("guard", inputGuard)
})
```
**Detection:**
- Grep for `v-<name>` in templates, then grep `directive("<name>"` in plugins — if no match, directive is unregistered
- Error always says `getSSRProps` specifically → points to directive, not component


## thai-api-name-field-localized

**Tags:** api-mapping, thailand, composable, dropdown, Select
**Date:** 2026-05-20

**Symptom:** Dropdown shows badge/code correctly, but the text name beside it is empty — some fields render, some do not
**Root cause:** Thai API convention splits localized fields apart — not a single `name`:
- `name_th` = full Thai name
- `name_abb_th` = abbreviated Thai name
- `name_en` = full English name
- `code` = code (used as headerName badge)

Mapping `name: item.name` returns undefined → empty text
**Fix pattern:**
```ts
// Don't assume the field name
{ id: item.id, name: item.name }

// Check v2 model/composable first
{ id: item.id, name: item.name_th, headerName: item.code }
```
**Detection:**
- Open dropdown → badge/code renders but name text empty = wrong `name` field
- Check `models/<domain>/<entity>.model.ts` in v2 for the actual field
- Check `composables/api/<entity>.ts` in v2 to see which field is mapped


## api-empty-array-overwrites-fallback

**Tags:** vue3, composable, fallback, api-mapping, defensive-coding
**Date:** 2026-05-20

**Symptom:** Fallback data renders correctly at first but disappears after the API call — dropdown becomes empty
**Root cause:** `if (res.data)` is `true` for an empty array `[]` (truthy in JavaScript) → overwrites fallback with `[].map(...)` = `[]`
**Fix pattern:**
```ts
// Using if (res.data) — overwrites fallback with []
if (res.data) {
  list.value = res.data.map(...)
}

// Always check length first
if (res.data?.length > 0) {
  list.value = res.data.map(...)
}
```
**Detection:**
- Dropdown shows data → becomes empty after API call completes
- console.log `res.data` → `[]` but fallback was overwritten
**Related:** [[thai-api-name-field-localized]]

## duplicate-api-call-from-composable-side-effect-race

**Tags:** vue3, nuxt, composable, side-effect, race-condition, singleton, fetch-dedup
**Date:** 2026-05-20

**Symptom:** API endpoint is called twice back-to-back (visible in Network tab DevTools) when user navigates to a page using middleware/auth — both calls return 200 with timing close together (e.g. 108ms + 88ms)
**Root cause:** **Composable factory has a side-effect that schedules an async API call** (e.g. `nextTick(async () => { await setTimeout(100); await fetchProfile() })`) — racing with the caller (middleware) hitting the same API simultaneously. **In-flight promise guard is broken** because `promise = (async () => {})()` reassigns on every call without checking the existing one → no dedupe
**Fix pattern:**
- **True singleton guard:** `if (inFlightPromise) return inFlightPromise` before reassigning
  ```ts
  const fetchProfile = async () => {
    if (inFlightPromise) return inFlightPromise   // ← reuse in-flight
    inFlightPromise = (async () => { ... })()
    try { return await inFlightPromise }
    finally { inFlightPromise = null }
  }
  ```
- **Remove initial fetch from factory side-effect** — let the caller (middleware/page setup) own initial fetch; watchers in the factory should only be for event-driven checks (focus/visibility/interval)
- **Early return** if state already exists — e.g. `if (store.userInfo?.id && currentUserId === lastUserId) return true`
- Avoid pattern `await fetch(); if (!data) await fetch()` — if first call fails, the second fails for the same reason
**Detection:**
- Open DevTools → Network → Fetch/XHR → see the same endpoint called multiple times close together on the timeline
- Trace caller flow: middleware/route guard, composable factory, component mount, watcher initial check — especially `setTimeout` / `nextTick` in the factory that schedules async fetch
- Check the in-flight promise variable for `if (promise) return promise` before reassignment

## invalid-end-tag-vue-template

**Tags:** vue3, template, compiler-error, migration, wrapper
**Date:** 2026-05-16

**Symptom:** Vite/Vue compiler error: `Invalid end tag` or `Element is missing end tag` usually points to `</template>` on the last line of the file (misleading — the reported line is not the real fault)
**Root cause:** Wrapper element (`<div class="container">...</div>`) deleted **on one side only** — opening still there but closing removed (or vice versa) → Vue compiler nesting count mismatches → error bubbles up to `</template>`
**Fix pattern:**
- Always delete wrapper open + close **together** (select the matching pair before deleting)
- When migrating `<div>` → `<UCard>` → search-replace both in one pass, not line by line
- Run formatter (Prettier/Volar) reformat before commit — wrong indent becomes obvious when pairs break
**Detection:**
- Grep the file: `<div`, `<template`, `<UCard` count must equal `</div`, `</template`, `</UCard` count
- Check Vue devtools / Volar inline diagnostic — it usually highlights the unmatched tag
- If error points to `</template>` on the last line → search backward for the most recently edited wrapper

## select-item-empty-string-value-throws

**Tags:** nuxt-ui, reka-ui, USelect, USelectMenu, runtime-throw
**Date:** 2026-05-16

**Symptom:** Runtime error: `SelectItem must have a value prop that is not an empty string` on component mount — error originates from Reka UI internals (stack does not point directly at the items array)
**Root cause:** `items` array of `USelect` / `USelectMenu` contains an element with `value: ''` (empty string) — Reka UI reserves `''` as the sentinel for "no selection"
**Fix pattern:**
- Change `value: ''` → `value: null` or `value: undefined` (if the component can handle it)
- For an "All" option → use a string sentinel like `'__ALL__'` and map back to undefined in a computed
- When migrating native `<select><option value="">...</option></select>` → never map straight to `{ value: '' }`
**Detection:**
- Grep cross-pattern (both single + double quotes): `rg "value:\s*['\"]['\"]" --type ts --type vue`
- Dev console error → Reka UI throw → inspect component tree for the active `USelect` on that page

## multi-tab-reload-loop-on-401

**Tags:** auth, reload-loop, location-reload, session, multi-tab
**Date:** 2026-05-16

**Symptom:** Page flickers / reloads itself repeatedly until the browser freezes — happens frequently when the session expires
**Root cause:** The 401 error handler calls `location.reload()` → page reload → original request fires again → 401 again → reload again → loop
**Fix pattern:**
- 401 handler must not call `location.reload()` — redirect to `/login` via `router.push('/login')` or `navigateTo('/login')` instead
- To refresh data after re-auth → use `refresh()` from `useFetch` or invalidate the specific Pinia store, not a full page reload
- Set a guard: check `route.path` before redirecting — if already on `/login`, do not redirect again (prevents infinite loop when the login page itself returns 401)
**Detection:**
- Network tab → same request fires repeatedly in a short window
- Grep `location.reload()` in auth handler / interceptor / middleware
- Console: 401 response loop + "Navigation cancelled" warning from Vue Router

