# Learnings — review

> **Per-skill, cross-project memory** — lessons for skill `review` usable across every project
>
> **What to store here:**
> - False-positive patterns to watch for (e.g. "vue-tsc doesn't count `<script setup>` macros as callers → check manually")
> - High-signal review heuristics (e.g. "every `any` cast is a finding until explained")
> - Review patterns specific to Vue/Nuxt/React/TS that commonly surface bugs
> - Patterns that look fine but hide a bug (e.g. `if (res.data)` truthy with empty array)
>
> **What NOT to store here:**
> - Findings from a specific PR (one-shot — git log / PR comments have it)
> - Project-specific code conventions already in project memory
>
> **When to read:** every Pre-flight of skill `review`
> **When to append:** after a review if a finding pattern generalizes across projects

---

## Format per entry

```markdown
## <kebab-case-slug>

**Tags:** framework, bug-type, severity-signal
**Date:** YYYY-MM-DD

**Context:** what kind of review surfaced this — 1 line
**Lesson:** pattern + why it's a real finding
**How to apply:** what to check next time / signal to look for
```

---

## Entries

<!-- newest on top -->
