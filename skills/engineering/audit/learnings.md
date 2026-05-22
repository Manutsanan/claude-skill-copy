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

<!-- example (delete when real entries exist):

## full-lodash-import-bloat-pattern

**Tags:** performance, bundle, lodash, vue, nuxt

**Date:** 2026-05-18

**Context:** scanned a Nuxt 4 project and found `import _ from 'lodash'` in 30+ files, adding +71KB to initial bundle
**Lesson:** nearly every Vue/Nuxt project audited has this pattern — `lodash` whole import used for only 1-2 functions
**How to apply:** Phase 2 dimension Performance — start with `rg "import \w+ from ['\"]lodash['\"]"` (not `lodash-es`) as the first scan
**Related:** project memory of projects where user accepted it as "intentional"

-->
