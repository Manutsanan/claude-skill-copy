---
name: simplify
description: Use after fe or debug completes to reduce code surface — dead code, duplication, over-complex logic. Trigger on Thai: simplify, ลด code, clean up, หา duplication, refactor ให้สั้นลง, เอา code ซ้ำออก, tidy up, ลด complexity. English: simplify, clean up, reduce duplication, remove dead code, tidy. Do NOT invoke for new feature work or bug fixes — use fe/debug for those.
---

# simplify — Reduce Code Surface

**Principle:** fix first, then clean — never simplify and debug in the same pass

**Scope:** working code only — if broken, yield to `debug` first

---

## Phase 0.5 — Skill learnings

Load `~/.claude/skills/simplify/learnings.md` — grep tags matching current file types (vue, ts, composable, store)

---

## Progress tracker

```
Simplify progress:
- [ ] Pre-flight: code confirmed working (no known bugs in scope)
- [ ] Dead code scan — unused imports / vars / components / commented blocks
- [ ] Duplication scan — repeated blocks ≥ 3 lines in ≥ 2 places
- [ ] Complexity scan — deep nesting / long functions / inline template logic
- [ ] Ripple check — callers verified before every extraction
- [ ] tsc --noEmit green after every extraction
- [ ] Memory updated if reusable pattern found
```

---

## Thinking order

**0. Pre-flight**

- Confirm code in scope is working (no active bug report / no failing test)
- Confirm scope boundary — file, component, or feature? whole project = too broad → ask user to narrow
- If scope is ambiguous → ask before scanning

**1. Dead code**

Look for:
- Unused imports — TS unused-import warnings + `rg "^import .* from" <file>` cross-ref usage
- Variables/functions declared but never referenced in template or logic
- Unused components in `components/` — no `<ComponentName>` in any template
- Commented-out code blocks (not TODO markers)
- Constant-false branches: `if (false)`, `if (0)`, `if (null)`

**2. Duplication**

Look for (rule: 2 copies = note, 3+ copies = extract):
- Repeated fetch + transform pattern in ≥ 2 composables → extract shared composable
- Repeated valibot field (e.g. `v.pipe(v.string(), v.trim(), v.minLength(1))`) in ≥ 3 schemas → extract named schema helper
- Repeated template block ≥ 3 lines in ≥ 2 components → extract sub-component
- Repeated Tailwind class group ≥ 3 uses → extract into component or `@apply` token

**3. Complexity**

Look for:
- Function > 40 lines → candidate to split
- Nesting > 3 levels → candidate for early-return / guard clause
- Computed with side effect → split into computed + watch
- Template expression > 1 line → move to computed
- Chained `.then()` → convert to `async/await`
- Long ternary in template → move to computed named clearly

**4. Extraction — strict rules**

Before extracting anything:
1. `mcp__codegraph__callers <symbol>` — list all callers; fallback `rg "<symbol>"` for new-session symbols
2. Name the extraction in < 4 words — if you can't, the boundary is wrong
3. Extract one thing at a time
4. Run `tsc --noEmit` after each extraction before the next
5. Never create a new file just to hold one function — extend an existing composable/helper first

---

## Quality gates

- [ ] `tsc --noEmit` green before and after every extraction
- [ ] Behavior is identical — no logic changed, only structure
- [ ] Ripple check run before every extraction
- [ ] Duplication removed — `rg "<old-pattern>"` returns 0
- [ ] Dead code removed — no unused import warning
- [ ] Memory updated if a reusable simplification pattern found

---

## Do not

- ❌ **simplify and fix bugs in the same pass** — two changes + one failure = can't isolate root cause
- ❌ **extract at 2 copies** — 2 copies is a note, 3+ copies is an action
- ❌ **rename without checking callers** — rename = breaking change for all consumers
- ❌ **delete "dead-looking" code** without checking test files, dynamic imports, and string references
- ❌ **scope to whole project in one pass** — file or feature boundary only; ask user if wider
