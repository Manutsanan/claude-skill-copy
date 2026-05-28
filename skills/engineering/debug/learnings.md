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

## validate-root-cause-before-invasive-edits

**Tags:** debug-discipline, bulk-edit, revert-flip, hypothesis-testing
**Date:** 2026-05-27 (graduated from boonphone project memory)

**Symptom:** A bug suggests a fix that would touch many files (10+) or requires reverting / un-reverting a recent commit. Pattern of "edit-revert-edit" oscillation on the same commit.
**Root cause:** Acting on an unverified hypothesis. The "obvious" cause is often a symptom; the real fix is usually architectural (a few central files) not scattershot (many leaf files).
**Fix pattern:**
- Before any bulk edit, state the hypothesis explicitly. List ≥ 2 alternative root causes. Propose 1 cheap verification step (single-file probe, browser test, doc check, codegraph callers) before committing to the bulk change.
- When tempted to revert→un-revert→revert: stop. Each oscillation costs trust. Lay out the trade-offs of each side and let the user pick.
- Default preference: architectural fix touching few central files > scattered fixes across many leaves. When both are plausible, the central fix is closer to the real root cause.
**Detection:**
- About to use Edit on > 10 files within one task → trigger this check
- Considering `git revert` on a commit you also recently authored → trigger this check
- User pushback like "เหมือนจะแก้ๆไปๆมาๆนะ / วิเคราะห์ให้ดีก่อนปรับแก้ไหม" → already past the violation
**See also:** [[feedback-verify-multi-pattern-before-claiming]] (global) — verify after the fix; this rule covers verify before the fix
