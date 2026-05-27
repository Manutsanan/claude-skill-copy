---
name: migrate
description: Use for bulk transformations / migrations across many files — converting legacy patterns to new patterns (e.g. native <select> → USelect, inline schemas → shared schemas, class-based components → composition API, deprecated API → new API). Plans the migration in phases, applies in batches, verifies after each batch, recovers from cascading errors. Trigger on Thai keywords migrate/ย้าย/แปลง/refactor ทั้งโปรเจกต์/เปลี่ยน X เป็น Y ทั้งหมด/cleanup ทุกที่ and English keywords migrate/migration/bulk transform/codemod/refactor across files/replace all/convert all. Examples "migrate native select เป็น USelect ทั้งโปรเจกต์", "ย้าย inline schema ไป shared/", "เปลี่ยน v-model:open เป็น defineModel ทุกที่", "refactor service layer ทั้งหมด", "ลบ deprecated API call ทุกจุด". DO NOT use for single-file edits (use `fe` instead) or schema design (use `sa` first).
user-invocable: false
---

# migrate — Bulk transformation orchestrator

Use on tasks that **touch many files following a repeating pattern** — enforce Discover → Plan → Execute → Cross-verify in order, no shortcut

**Core rule:** "impatient point-fix" is the root cause of nearly every failed migration

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (see `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: migrate | cross` + target pattern keyword (e.g. `USelect`, `valibot`, `wrapper-element`)
- **Learnings filter:** read `~/.claude/skills/migrate/learnings.md` only for entries whose Tags match keyword (max 5); no match → "fresh — be extra thorough in Discover"
- **Conflict check:** if migration conflicts with memory → stop and ask user
- **Save triggers:** per the 8 universal triggers — emphasize "pattern + regex + gotcha" that generalize

---

## Progress tracker

Copy this block into your first response and tick boxes as each phase finishes. Skipping a phase = the "impatient point-fix" anti-pattern.

```
Migration progress:
- [ ] Phase 0: Discover — ≥ 2 regex (loose + strict), results match
- [ ] Phase 0: Scope listed (files + per-file count + classification)
- [ ] Phase 1: Plan proposed (batches A/B/C) + user confirmed if > 10 files
- [ ] Phase 2: Batch 1 executed + verified (tsc / curl / dev log)
- [ ] Phase 2: All remaining batches verified
- [ ] Phase 3: Re-scan = 0 (loose + strict both)
- [ ] Phase 3: Manual spot-check 2–3 files
- [ ] Phase 3: Full build success
- [ ] Memory updated (pattern + regex + gotcha)
```

---

## Handoff

**Receive from `sa`** (if any): target pattern + reason + ripple list

**Hand to `fe`**: file:line that cannot be migrated mechanically + edge case + suggestion

**Yield back to `sa`** when migration affects data model / API contract / requires data migration script

**Do it solo** when pattern is mechanical + does not affect logic + every batch verifies clean

---

## Order of thinking (do not skip any phase)

### Phase 0 — Discover & Scope

1. **Scan for occurrences** — for named symbols: `mcp__codegraph__callers <symbol>` first (semantic graph, preferred); then confirm with ≥ 2 regex patterns (loose + strict) — results must match (mismatch = strict regex wrong)
2. List all files + count per file
3. **Classify:** single pattern or multiple shapes? mechanical or context-dependent?
4. **Map dependencies:** which files reference which, what edit order is required
5. **If migrating library version** → `mcp__context7__resolve-library-id` + `mcp__context7__query-docs "migration guide v{old} to v{new}"` before scanning — confirms official migration path and prevents migrating to an already-deprecated target pattern

### Phase 1 — Plan

1. **Propose plan as phases to user before starting:**
   - Phase A: low-risk / dead code (trial the approach on a small scope)
   - Phase B: active production
   - Phase C: edge cases / context-dependent
2. State the **verify step** of each phase
3. **Ask for confirm** if scope > 10 files or touches shared code

### Phase 2 — Execute by batch

One batch at a time (not one file at a time, not the whole set in one shot):

1. Migrate **3–5 files** in the first batch
2. **Verify immediately after batch:**
   - `tsc --noEmit` (if TS)
   - `curl http://localhost:3000/<page>` HTTP 200
   - dev log has no new error/warn
3. Error → stop, fix, then proceed to next batch
4. OK → next batch

### Phase 3 — Cross-verify final

1. **Re-scan** with the same patterns (loose + strict) — both must = 0
2. **Manual spot-check 2–3 files** — read them and confirm
3. **Build full** — `nuxt build` / `tsc --noEmit` across the whole project passes
4. **Update memory** — pattern + regex + gotcha encountered

---

## Tools / techniques

**Bulk regex replace** (Bash + node script) — use when pattern is identical at every site + would require > 30 Edit calls

Rule: every script must (1) print "files modified" + "matches replaced", (2) run on 1 file first to verify, (3) git commit/stash before running

**Edit tool** — when context-dependent or < 10 sites

**CodeGraph MCP** — `mcp__codegraph__callers <symbol>` for named symbols (faster than Explore agent when name is known); `mcp__codegraph__explore <sym1> <sym2>` for multi-symbol source dump

**Explore agent** — discover phase at large scope (faster than grep one-by-one)

---

## Anti-patterns (already burned by these)

- ❌ **Edit one site at a time without scanning first** → always miss some; enforce Discover → Plan → Execute
- ❌ **Verify with a single regex pattern** → `<tag[ >]` misses multi-line attrs; always cross-verify loose + strict
- ❌ **Delete wrapper element halfway** → orphan `</div>` left = "Invalid end tag"; Edit must combine open + close + content into a single `old_string`
- ❌ **Migrate Reka UI item with `value=""` / `value: ''`** → runtime error; scan both single + double quote, replace with `null` / sentinel
- ❌ **Claim "0 left" from a single scan pass** → run all quality gates before claiming

---

## Quality gates (before closing the task)

- [ ] **Memory scanned + updated** if any new pattern/gotcha
- [ ] **Discover complete** — ≥ 2 regex patterns with matching results
- [ ] **Per-batch verify passed** — `tsc --noEmit` + Vite compile + dev log clean for every batch
- [ ] **Final re-scan = 0** (loose + strict)
- [ ] **Manual spot-check 2–3 files**
- [ ] **Build full success**
- [ ] **Skill learnings updated** if regex/AST/batch-size/recovery technique generalizes → append `learnings.md`
- [ ] **Do not claim "done / complete / 0 left"** from a single scan — if user has to say "check again" then the first scan was insufficient

---

## Output style

```markdown
### Phase 0 — Discover
- Scope: 34 sites across 13 files
- Pattern types: 2 shapes (filter / form field)

### Phase 1 — Plan
- Batch A (dead code, 7 files)
- Batch B (active production, 6 files)

### Phase 2 — Execute Batch A
- ✓ Migrated 3 files
- ✓ tsc passes
- ✓ curl /xxx HTTP 200
- → Batch B

### Phase 3 — Final verify
- ✓ Re-scan: 0 left (loose + strict patterns match)
- ✓ Build success
- ✓ Memory updated: feedback_<topic>.md
```
