# Learnings — migrate

> **Per-skill, cross-project memory** — lessons for skill `migrate` usable across every project (Bulk transformation)
>
> **What to keep here:**
> - Regex / AST patterns covering edge cases of past migrations (e.g. native `<select>` → `USelect` must handle `value`, `v-model`, `@change`, nested `<option>`)
> - Optimal batch size that allows verify to keep up (tried 50 files/batch once, overwhelmed verification)
> - Cascading error patterns (e.g. migrating inline schema with incomplete imports breaks types elsewhere)
> - Post-batch verification technique (tsc --noEmit, grep cross-pattern, build check)
> - Rollback strategy when migration breaks mid-way
> - Anti-pattern: impatient point-fix migration without planning — must always discover/scope/plan/execute

>
> **What NOT to keep here:**
> - List of files migrated in a specific project (one-shot info — git log has it)
> - Project-specific path / shared/schemas/ structure (that → project memory)
>
> **When to read:** every time during Pre-flight of skill `migrate` — especially Phase 0 Discover
> **When to append:** after a migration completes if a pattern/technique reusable across other migrations was found

---

## Format per entry

```markdown
## <kebab-case-slug>

**Tags:** transform-type, framework, technique
**Date:** YYYY-MM-DD

**Context:** migrate what → what, scale (how many files)
**Lesson:** pattern/regex/technique that worked + edge case nearly missed
**How to apply:** which migration shapes this fits
**Anti-pattern avoided:** the mistake nearly made
**Related:** [[other-learning-slug]]
```

---

## Entries

<!-- newest on top -->

## grep-multiline-attrs-vue-template

**Tags:** regex, vue-template, scan, cross-verify, multi-line
**Date:** 2026-05-16

**Context:** Migrate native `<select>` → `USelect` (34 sites) — scan with loose regex `<select` returned 34; scan with strict regex `<select[\s>]` returned 31 → mismatch on 3 files
**Lesson:** Vue template attributes can break across lines — a regex requiring whitespace/`>` immediately after the tag name (e.g. `<select[\s>]`) will **miss** the case where attributes wrap to a new line (`<select\n  v-model="x"`). The loose regex `<select` catches it but may false-positive (e.g. `<selection>` substring)
**How to apply:**
- **Always cross-verify ≥ 2 regex patterns** in Discover phase:
  - loose: `<select` (catches every case including false positives)
  - strict: `<select(\s|>)` (more accurate true positives but misses multi-line)
- 2-pattern match = trust scan; mismatch = manually diff the list to find what got missed
- Just do: `diff <(rg -l "<select" --type vue) <(rg -l "<select(\s|>)" --type vue)`
- Best regex for a Vue tag: `<TagName(?=[\s/>]|$)` — match Tag before whitespace/self-close/end-of-line (won't match `<TagNameX>`)
**Anti-pattern avoided:** trusting one regex as "scan complete" — every Vue template migration must use dual-regex
**Related:** [[vue-multi-line-attribute-pattern]]

## wave-migration-6-step-workflow

**Tags:** workflow, batch, planning, verify, rollback
**Date:** 2026-05-16

**Context:** Migrate 80+ native `<input>` → `<UInput>` in one shot → tsc broke with 200+ cascading errors → rollback hard → spent 3 hours recovering
**Lesson:** Every bulk migration must pass through 6 phases — no skipping:
1. **Discover** — scan with dual regex + count + list files
2. **Scope** — split batches by risk (dead code → low traffic → high traffic → critical)
3. **Plan** — write mechanical rule (search-replace pattern) + manual edge case list
4. **Execute** — 5-15 files per batch (depends on complexity) — never > 20 files/batch
5. **Verify per batch** — `tsc --noEmit` + `curl` the touched page + dev log clean **before** the next batch
6. **Final re-scan + cleanup** — original pattern = 0 project-wide + remove unused imports
**How to apply:**
- Batch size 5-15 files — fewer wastes cycle time, more outpaces verification
- Batch order: dead code first (trial pattern without user impact) → low-traffic page → critical flow
- During execute → commit per batch in git (easy rollback if any batch breaks)
- If verify on batch N fails → **stop immediately**, don't start batch N+1 — fix or rollback batch N first
**Anti-pattern avoided:** migrate the whole project in one round and verify at the end — cascading errors make root cause hard to find
**Related:** [[tsc-noemit-per-batch-verify]]

## tsc-noemit-per-batch-verify

**Tags:** typescript, verify, batch, build
**Date:** 2026-05-16

**Context:** Migrate inline valibot schema → shared/schemas/ batch 3 — final tsc raised 47 errors cascading from batch 1
**Lesson:** TypeScript errors cascade through import chains — if batch 1 changes a shared API type → batch 2 importing it breaks → batch 3 too. Checking only at the end = at fix time you don't know which batch caused which error
**How to apply:**
- Run `tsc --noEmit` **after every batch** before starting the next
- If batch N errors > 0 → never proceed to batch N+1
- If errors come from batch N+something (not yet migrated) → cascade from earlier batch → revisit earlier batch
- Tip: capture baseline error count before starting (`tsc --noEmit | wc -l`) — every batch must not increase it
- Build pipeline command: `yarn nuxt prepare && yarn tsc --noEmit` (prepare regenerates auto-import types before tsc)
**Anti-pattern avoided:** verifying once at the end of migration → no idea which batch caused the cascade
**Related:** [[wave-migration-6-step-workflow]]
