# Learnings — pr

> **Per-skill, cross-project memory** — lessons of this skill itself that apply across every project
>
> **How is this different from project memory?**
> | | Project memory (`~/.claude/projects/<id>/memory/`) | Skill learnings (this file) |
> |---|---|---|
> | Scope | only that project | across every project that uses this skill |
> | Content | business rule, codebase convention, user preference | technical pitfall, anti-pattern, skill defaults |
> | Example | "this repo uses squash-merge only" | "gh pr create fails silently when branch not pushed" |
>
> **When to append a new entry:**
> - after every task this skill performs **if** you find a lesson that generalizes
> - a pitfall this skill often misses
> - a default this skill should use as first choice next time
> - **do not append** project-specific rules (those → project memory)
>
> **When to read:** every Pre-flight — grep tag/keyword of current task → apply before starting
>
> **Pruning:** stale entries → mark `~~deprecated~~`

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

---

## Entries

<!-- newest on top — append new entries here -->
