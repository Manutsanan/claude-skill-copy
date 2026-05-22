# Learnings — {skill-name}

> **Per-skill, cross-project memory** — lessons of this skill itself that apply across every project
>
> **How is this different from project memory?**
> | | Project memory (`~/.claude/projects/<id>/memory/`) | Skill learnings (this file) |
> |---|---|---|
> | Scope | only that project | across every project that uses this skill |
> | Content | business rule, codebase convention, user preference | technical pitfall, anti-pattern, skill defaults |
> | Example | "this project uses partner-scoped routes" | "Vue destructure reactive object → reactivity lost" |
>
> **When to append a new entry:**
> - after every task this skill performs **if** you find:
>   - a lesson that generalizes — not a project-specific business rule (that → project memory)
>   - a pitfall this skill often misses
>   - a default this skill should use as first choice next time
> - **do not append** generic business rules, generic user preferences, or anything derivable from code/git history
>
> **When to read:** every Pre-flight — grep tag/keyword of current task → apply before starting
>
> **Pruning:** stale entries (framework changed, API deprecated) → delete or mark `~~deprecated~~`

---

## Per-entry format

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** what you were doing when the lesson was found — **1 line only**
**Lesson:** the rule + short reason why
**How to apply:** what to do next time when a similar situation appears
```

**Deprecation:** when an entry becomes stale (API changed, component deprecated, pattern no longer works) → change header to `## ~~slug~~` — Phase 0.5 skips it automatically; do not delete because it remains history.

---

## Entries

<!-- newest on top — append new entries here -->

<!-- example (remove when real entries exist):

## sample-lesson-slug

**Tags:** example, placeholder
**Date:** 2026-05-16

**Context:** started using the learnings.md pattern
**Lesson:** store cross-project lessons that generalize; do not mix with project memory
**How to apply:** at the end of every task — ask yourself "does this lesson apply to other projects?" if yes → here; if no → project memory

-->
