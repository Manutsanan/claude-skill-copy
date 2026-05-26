---
name: distill-memory
description: Guided memory distillation — review memories across all tiers, consolidate duplicates, prune stale entries, and promote lessons up the tier (project → global → skill learnings). Trigger on Thai: distill-memory, จัดการ memory, clean up memory, ทำ memory, prune memory, review memory, ดู memory. English: distill memory, clean memory, review memory, distill, memory audit.
---

# distill-memory — Memory Distillation Pipeline

**Principle:** noisy memory is worse than no memory — stale/duplicate entries cost tokens every turn and actively mislead

**Scope:** meta-task — reads memory files, proposes changes, waits for confirmation before writing anything

---

## No Phase 0.5

This skill IS the memory maintenance task — no learnings to load.

---

## Progress tracker

```
Distill progress:
- [ ] Global memory audited — stale / duplicate / contradictory entries flagged
- [ ] All project memories scanned — cross-project repeat patterns identified
- [ ] Skill trigger vocabulary — entries per skill counted; over-cap list prepared
- [ ] All skill learnings audited — duplicate cross-skill entries found
- [ ] Promotion candidates table shown to user
- [ ] Pruning candidates table shown to user
- [ ] User confirmation received
- [ ] Confirmed changes written
- [ ] All MEMORY.md indexes updated
```

---

## Thinking order

**1. Load all memory tiers**

```bash
# List all project memory files
find ~/.claude/projects -name "MEMORY.md"

# List all skill learnings
ls ~/.claude/skills/*/learnings.md

# Global memory
cat ~/.claude/memory/MEMORY.md
```

Read every file — not just the index. The index can be stale.

**2. Detect duplicates**

- Same rule stated twice (even in different words) — keep the more specific one, remove the generic
- Same lesson in both `fe/learnings.md` and `debug/learnings.md` (or other skill pairs) → keep in the most relevant skill, add `[[cross-ref]]` link in the other
- Two global memory entries that contradict each other → flag as conflict, ask user which to keep
- Trigger vocabulary phrase that appears in ≥ 2 skills → move to "ambiguous" section

**3. Detect stale entries**

Signals of a stale entry:
- References a library version that's been bumped (check `package.json` if available)
- References a component/API that no longer exists in the project
- Date older than 6 months AND about a fast-moving API (Nuxt UI, Valibot, etc.)
- Says "this project uses X" but the project has migrated away from X

Action per stale entry: mark `~~deprecated~~` + note reason, or delete if clearly wrong

**4. Detect promotion candidates**

Graduation rule (match all conditions):
```
project memory → global:      same lesson in ≥ 2 different project memory folders
global → skill learnings:     entry is skill-specific (tagged sa/fe/ux/debug/migrate)
                              AND appears to apply to ≥ 3 projects
skill learnings → SKILL.md:   entry is load-bearing enough that the skill MUST always enforce it
                              (rare — usually a checklist item, not a learning)
```

**5. Trigger vocabulary overflow check**

Count entries per skill in `~/.claude/memory/skill_trigger_vocabulary.md`:
- Cap: 30-50 per skill
- If over cap → flag lowest-specificity triggers for pruning (keep unique/domain-specific; prune generic phrases already covered by CLAUDE.md's decision matrix)

**6. Present proposed changes — always before writing**

Show a table:

```
## Proposed changes (confirm before applying)

| Action | Tier | Entry | Reason |
|---|---|---|---|
| PROMOTE | project → global | feedback_X | same lesson in project A + B |
| PROMOTE | global → skill learnings | feedback_Y | skill-specific, 3+ projects |
| PRUNE | global | feedback_Z | duplicate of feedback_W (keep W — more specific) |
| PRUNE | global | feedback_Q | stale — references Nuxt UI v2, now on v3 |
| CROSS-LINK | fe + debug | select-empty-string | keep primary in fe, add [[cross-ref]] in debug |
| VOCAB PRUNE | sa triggers | "ดู" | too generic — conflicts with ambiguous list |
```

Ask: "Apply all? Or enter numbers to skip (e.g. 2,4):"

**7. Write confirmed changes**

- Write each change one at a time (not in batch)
- When promoting: write to destination → then delete from source (never leave both)
- When pruning: delete from index first, then delete the file
- Update MEMORY.md index last (after all file writes are done)
- Do not create new memory files — only move/edit/delete existing ones

---

## Quality gates

- [ ] No write without explicit user confirmation
- [ ] Every promoted entry deleted from source tier (no duplication)
- [ ] Every cross-linked entry uses `[[slug]]` format pointing to the primary
- [ ] MEMORY.md index updated after every change
- [ ] Over-cap vocab counts reduced to ≤ 50

---

## Do not

- ❌ **auto-promote without asking** — user must confirm every promotion and deletion
- ❌ **delete without showing content** — always show the entry text in the proposal table
- ❌ **promote based on similar wording** — same words ≠ same lesson; read the body
- ❌ **run partial distill** — must scan all 3 tiers; partial leaves contradictions alive
- ❌ **create new memory files during distill** — distill reorganizes; new lessons come from active tasks
