# Auto-trimmed entries from `debug` — 2026-05-28

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

**See primary:** [[select-item-value-must-not-be-empty-string]] in `fe/learnings.md` — full root cause, fix patterns, and migration guide live there

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
