---
name: _template
description: Template สำหรับสร้าง skill ใหม่ — copy ทั้งไฟล์แล้วแก้ section ตามต้องการ ห้ามแก้ structure เพราะ pipeline orchestration พึ่งโครงสร้างนี้
---

# {skill-name} — {one-line purpose}

> This structure is mandatory for every skill to enforce:
> 1. **consistent triggers** — Claude picks the right skill
> 2. **pre-flight checks** — use saved memory, do not repeat bugs
> 3. **handoff contract** — pipeline `sa → ux → fe` passes work without misinterpretation
> 4. **quality gates** — do not close work before full verification

---

## Trigger เรียกเมื่อ

User mentions any of:
- **Thai**: keyword1, keyword2, keyword3
- **English**: keyword1, keyword2, keyword3

Or working on a task that:
- Case A: ...
- Case B: ...

**Do not invoke** when:
- Out of this skill's scope — yield to another skill (see "Mid-task yield" in CLAUDE.md)

---

## Pre-flight (mandatory before every task)

1. **Read project CLAUDE.md** (at working directory) — understand business domain, convention, stack
2. **Scan project memory** at `~/.claude/projects/<project-id>/memory/MEMORY.md`:
   - find feedback memory whose keyword matches current task
   - quote relevant memory in reasoning before proposing implementation
   - if memory conflicts with intended change → ask user to confirm before editing
3. **Scan skill learnings** at `~/.claude/skills/<skill-name>/learnings.md` (per-skill, cross-project):
   - different from project memory — this file stores lessons of the **skill itself** that apply across every project
   - grep tag/keyword matching current task → apply lesson before starting
   - quote applied entry in reasoning (e.g., "per learnings#vue-destructure-loses-reactivity use toRefs")
   - if no matching entry → note "no matching learning — fresh start"
4. **Read relevant code** — do not analyze from assumptions (see "หลักความรอบคอบขั้นสูงสุด" in CLAUDE.md)
5. **Define scope** — if scope is larger than expected → tell user before proceeding

---

## Handoff (skill input/output)

**Input** — received from previous skill in pipeline:
- from `sa` (if this skill is ux/fe): spec / state machine / data model
- from `ux` (if this skill is fe): component map / Tailwind plan / interaction spec

**Output** — passed to next skill:
- specify exact artifact the next stage needs, no ambiguity
- use structured format (table / yaml-like list) that is ready-to-consume

**Mid-task yield** — if an out-of-scope issue is hit mid-task:
1. stop at that point
2. tell user in 1 line: "yield to skill `<X>` because <reason>"
3. complete the yielded step before returning

---

## Thinking order (varies per skill)

1. Step 1 — ...
2. Step 2 — ...
3. Step 3 — ...

---

## Output style

- use **mermaid** for every diagram
- use **table** for comparisons / structured lists
- use Thai for business terms, English for technical terms
- always cite **file:line** when referencing code

---

## Quality gates (mandatory before closing work)

Do not report "done / complete / 0 left" before completing every item:

- [ ] **Cross-verify ≥ 2 patterns** — e.g., scan with loose + strict regex, results must match (see `feedback_grep_multiline_attrs.md`)
- [ ] **Manual spot-check 2-3 spots** — read real files to confirm scan result
- [ ] **Build/compile verify** (if code changed) — `tsc --noEmit` + Vite compile (see `feedback_dangling_tag_after_wrapper_removal.md`)
- [ ] **Trace caller ≥ 1 hop** before claiming "dead code" / "safe" (see CLAUDE.md "ความรอบคอบขั้นสูงสุด")
- [ ] **Update project memory** if a new pattern worth preventing is found — add `feedback_<topic>.md` + link in MEMORY.md
- [ ] **Update skill learnings** at `~/.claude/skills/<skill-name>/learnings.md` if the lesson generalizes across projects — append new entry per format (newest on top); do not dump project-specific business rules (those go to project memory)

If user has to say "are you sure / re-check" = the first scan was not thorough → memo + adjust method immediately.

---

## Do not do (anti-patterns)

- **do not work out of scope** — yield to another skill instead
- **do not declare "done" from a single scan** — must pass quality gates
- **do not use vague wording** — "might / consider" → state "what, where, what impact"
- **do not touch existing code** before tracing caller chain — prevent "fix one spot → bug elsewhere"

---

## How to clone the template

```bash
cp -r ~/.claude/skills/_template ~/.claude/skills/<new-skill-name>
# then edit:
# 1. SKILL.md frontmatter (name + description with triggers)
# 2. SKILL.md body — fill in skill-specific content
```
