---
name: review
description: Use for code review or PR review — inspect existing code or an open PR for bugs, anti-patterns, type safety, and logic errors. Trigger on Thai: review, code review, ดู PR, ตรวจโค้ด, review code, ดูโค้ดนี้, PR นี้เป็นยังไง, view PR. English: review, code review, review PR, look at this code, review this PR, PR #X. Do NOT use for writing PR descriptions (use `pr`) or full security audit (use `sa` Mode B).
---

# review — Code Review

**Principle:** find real problems, not style opinions — every finding must have: file:line + what breaks + why

**Scope:** read-only inspection — does not write code; yield to `fe` for fixes

---

## Phase 0.5 — Skill learnings

Load `~/.claude/skills/review/learnings.md` — grep tags matching stack detected (vue, nuxt, ts, react)

---

## Progress tracker

```
Review progress:
- [ ] Scope set — PR #N or file list confirmed
- [ ] Logic review — correctness + edge cases + error paths
- [ ] Type safety — TS strict + nullable + schema coverage
- [ ] Reactivity review (Vue/Nuxt) — ref/reactive/computed/watch misuse
- [ ] Security spot check — auth gate, input trust, secret exposure
- [ ] Performance spot check — N+1, rerender, unnecessary payload
- [ ] Ripple check — callers of changed symbols updated?
- [ ] Findings presented with severity
- [ ] Memory updated if reviewable pattern found
```

---

## Thinking order

**0. Pre-flight — set scope**

- PR: `gh pr view <N> --json title,body,additions,deletions,files` → `gh pr diff <N>`
- Branch: `git diff main...HEAD --stat` → `git diff main...HEAD`
- File: read directly
- Ask user if scope is unclear — never guess branch/PR number

**1. Logic review**

- Main path: does the code do what it claims? Trace once
- Error paths: every async/await has a catch? No silent swallow?
- Edge cases: empty input, null/undefined, zero, max, concurrent call, network fail
- Race conditions: any `await` inside `v-for` / `forEach` / Promise.all that can interleave destructively?

**2. Type safety**

- `any` / `as X` cast without comment — flag unless the comment explains why
- Nullable field used without guard (e.g. `user.profile.name` without `?.`)
- Valibot schema: does it cover every field the real API returns?
- `InferInput` vs `InferOutput` used correctly? (InferOutput is post-transform, use for component props)

**3. Vue/Nuxt reactivity**

- Destructured `reactive()` without `toRefs()` — reactivity lost
- `$slots.<name>` in `v-if` — not reactive; use `computed(() => !!slots.X)` in `<script setup>`
- `watch` on a non-reactive value — effect never re-runs
- Template expression with side effect inside `computed` — computed must be pure
- `useState` keyed same as another composable — SSR hydration conflict

**4. Security spot check** (flag for `sa` Mode B if suspicious — this is not a full audit)

- User input used in: `v-html`, URL fetch, SQL/NoSQL query, file path → flag immediately
- Auth check at UI level only, no server-side guard → flag
- API response includes fields never displayed (potential over-exposure) → note
- Secret in source / response body → Critical

**5. Performance spot check**

- `v-for` list without `:key` → Vue can't diff correctly
- Composable that calls an API on every mount instead of using a singleton guard → duplicate calls
- `watch` with `deep: true` on a large object → expensive; check if specific path watch suffices
- Response payload much larger than what's rendered → suggest backend projection

**6. Ripple check for changed symbols**

For every symbol modified in the diff:
- `mcp__codegraph__callers <symbol>` — any caller not updated to match the new interface?
- Changed return type → destructuring callers still valid?
- Changed validation rule → old data in DB/localStorage will fail new rule?

---

## Output format per finding

```
### [Severity: Critical | High | Medium | Low | Nit]
**File:** `path/to/file.ts:42`
**Problem:** 1-sentence — what is wrong
**Impact:** what breaks / what attacker can do / what fails
**Suggestion:** concrete fix (code snippet preferred over description)
```

**Severity guide:**
- Critical — exploitable immediately or data loss on golden path
- High — likely bug, silent fail, or will break under normal use
- Medium — edge case failure under specific conditions
- Low — missing guard for rare/unlikely case
- Nit — style/clarity only; include only if it obscures correctness

If nothing Critical/High found → "No Critical/High findings. [N] Medium/Low below."

---

## Handoff

- Findings → yield to `fe` for implementation
- Security finding at High+ → yield to `sa` Mode B for full audit before `fe` fixes

---

## Do not

- ❌ **report style preference as a bug** — unless it causes a correctness issue, it's a Nit at most
- ❌ **read partial diff** — always read the full diff before concluding
- ❌ **report false positives** — trace ≥ 1 caller hop before claiming a bug
- ❌ **fix code during review** — review only; yield to `fe` for changes
- ❌ **full security audit in review** — spot check only; escalate to `sa` Mode B for deep audit
