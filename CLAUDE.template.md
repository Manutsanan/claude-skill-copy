@RTK.md

# Universal Phase 0 — Every task, every project, every command

> **Universal rule enforced before everything** — regardless of task size, whether a skill is invoked, or which project you're in.
>
> This Phase 0 is the **base layer** of the system — if a task invokes a skill, that skill's Phase 0 will **extend** (add skill learnings), not replace this one.

## 1. Load memory hierarchy (mandatory — always run first)

Load in order, 2 tiers (global → project):

### Global memory — `~/.claude/memory/MEMORY.md`
- Cross-project lessons + user preferences + workflow conventions used across all projects
- If file exists → filter entries with `metadata.scope: global` + relevant to the task
- If file missing → skip + note in reasoning

### Project memory — `~/.claude/projects/<id>/memory/MEMORY.md`
- `<id>` = working directory converted to project id by replacing `/` with `-`
  - working dir `/Users/X/Project/Y` → id `-Users-X-Project-Y`
  - working dir `/Users/X` (home) → id `-Users-X`
- Project-specific patterns, history, findings, constraints
- If missing → skip + note "no project memory"

**Stale memory guard (Fix 2 — mandatory before applying any memory entry):**
Any memory entry that names a specific file path, function name, flag, or component → **verify existence before recommending**:
- Names a file path → `Read` the file (confirm it exists)
- Names a function/symbol → `rg "<name>"` (confirm it's still in use)
- Names a feature flag / env var → check current config
If not found → mark as stale, do not recommend it, update or delete the memory entry

### Phase checkpoint — `~/.claude/projects/<id>/memory/project_phase_checkpoint_*.md`
- After loading project memory → scan for files named `project_phase_checkpoint_*.md` in the same folder
- If a checkpoint with `status: in_progress` is found → echo it to the user + ask whether to **resume** (load artifact from checkpoint) or **start fresh** (mark checkpoint as `abandoned`)
- If no checkpoint or all checkpoints are `status: complete` → skip

### Skill trigger vocabulary — `~/.claude/memory/skill_trigger_vocabulary.md`
- Thai/natural-language triggers mapped to skills — grows via distill pipeline from corrected invocations
- If file exists → load Thai keyword lists; use alongside decision matrix in step 3
- Cap: 30-50 entries/skill — pruned by `/distill-memory` when exceeded

## 2. Echo & Conflict check

- Echo top 3-5 relevant entries back to the user **before** starting work — required format: `[type] slug — one-line hook` **max 1 line per entry, never quote the entry body**
- If memory records a past mistake → state explicitly how you will avoid it (1 line)
- If proposing something that conflicts with memory → **stop and ask the user first**, never proceed silently
- If no relevant memory at all → short note: "no relevant memory — fresh start"

## 2.5 Token efficiency (mandatory — applies to every skill, every turn)

- **Quality gate output:** show only items that **fail**; if all pass → `✅ quality gates passed` (1 line). Never print the full checklist when there's no failure
- **Handoff output:** summarize as ≤ 10 bullets; for long artifacts, compress into key-value form, not prose
- **Shell commands:** `yarn` and `npm` are NOT auto-filtered by RTK → always use `rtk proxy yarn ...` / `rtk proxy npm ...`; same for `pnpm` → `rtk proxy pnpm ...`

## 3. Evaluate decision matrix → pick skill

Refer to the "Quick decision matrix" table in the Skill orchestration section below:
- Match user intent to the appropriate skill — cross-check `skill_trigger_vocabulary.md` Thai phrases (loaded in step 1) before deciding
- Falls under an exception (config / docs / typo / general question) → do not invoke a skill, handle directly
- Invoking a skill → that skill will run **Phase 0.5** itself (loads `~/.claude/skills/<skill>/learnings.md`)
- **Soft confirmation (mandatory on invoke):** first line of response must be `→ invoking \`[skill]\` ([reason ≤5 words])` — 1 line only, no header, no bold, no extra formatting

**Pipeline task tracking (Fix 1 — mandatory for multi-step pipelines):**
If selected pipeline has ≥ 2 steps (sa→ux, ux→fe, sa→ux→fe, sa→fe, etc.) → **immediately create tasks** using `TaskCreate` with each step as a separate task before starting Phase 1. Mark `in_progress` when starting a step, `completed` when its artifact is saved. This replaces relying on memory alone — tasks survive context compression.

## 4. Universal save triggers (mandatory — force save mid-turn)

Save memory **immediately** — do not wait for the user to ask, do not wait for session end — when any of these events occur:

1. **User corrects direction / says wrong** — ("not like that", "change to...", "stop") → save `feedback_*` + **Why** + **How to apply**
2. **User confirms a non-obvious pattern** — ("yes, that's right", accepts unusual approach without pushback) → save as validated
3. **Any error / mistake encountered** — runtime, type, logic, approach failure → save root cause + correct approach
4. **Task succeeded with a new approach that actually works** → save as reusable pattern
5. **Bug found with traceable root cause** → save root cause + ripple list (all files that may repeat the pattern)
6. **Constraint found that isn't in the code** — "API rate limit X", "field deprecated" → save `project_*`
7. **Same pattern corrected ≥ 2 times** in one task — repeated correction = must save
8. **When session is long** (> 20 turns or many large files loaded in sequence) → save pending lessons immediately; don't wait for compaction — once it happens it's too late
9. **After a pipeline phase completes** (sa / ux / fe each phase done) → save phase artifact to project memory before handoff, using this format:
   - **Filename:** `project_phase_checkpoint_<phase>_YYYY-MM-DD.md` (e.g. `project_phase_checkpoint_sa_2026-05-20.md`)
   - **frontmatter:** `phase: sa|ux|fe` + `status: in_progress` → change to `complete` when handoff is done
   - **content:** primary artifact the next phase needs — spec for ux, design plan for fe, implementation summary for verify
10. **Skill invoke corrected by user** ("ไม่ใช่ sa", "ควรเป็น fe", "debug ไม่ใช่ fe") → save `feedback_skill_trigger_*` to global memory immediately with: phrase used + wrong skill + correct skill; distill pipeline consolidates into `skill_trigger_vocabulary.md`
11. **After full pipeline completes** (sa→ux→fe, sa→fe, ux→fe — all steps done, verify passed) → suggest to user at end of turn (1 line only): `Tip: run \`/distill-memory\` to promote new patterns to skill learnings.` — say this once per pipeline, not per turn

### Save where?

| Lesson type | Destination |
|---|---|
| User behavior / preference / cross-project rule | **Global** `~/.claude/memory/` |
| Project-specific pattern / finding / constraint | **Project** `~/.claude/projects/<id>/memory/` |
| Skill-internal pitfall (Vue reactivity, Tailwind JIT, OWASP pattern) applicable across all projects | **Skill learnings** `~/.claude/skills/<skill>/learnings.md` |
| Conflicts with a rule already in CLAUDE.md | **Do not save** — restating duplicates = noise |

## 5. Skip rules (when part of Phase 0 can be skipped)

- **Trivial conversational task** (greeting, asking a CLI flag, requesting a 1-line explanation): glance MEMORY.md quickly — if no relevant entry, answer directly without echoing
- **Task that touches code / file / shared state**: never skip — mandatory full load + echo

Never skip because "it's a small task, unlikely to have memory" — bugs happen most often in tasks that seem small.

---

# Skill orchestration — sa / ux / fe + migrate / debug

Every frontend project uses 3 core skills as the main pipeline — `sa` (think first) → `ux` (design) → `fe` (write code) — supplemented by 2 specialist skills:
- **`migrate`** — bulk transformation across many files (legacy → new pattern)
- **`debug`** — diagnose runtime errors / unexpected behavior, find root cause not symptom

All sections below work as one system, not as independent rules.

---

## Quick decision matrix

| User intent | Skill to invoke | Order |
|---|---|---|
| "analyze / inspect / audit / find bug / find vulnerability / spec system" | `sa` | standalone |
| "adjust color / spacing / animation / responsive / accessibility" (visual only) | `ux` | standalone |
| "debug reactivity / refactor logic / fix schema / state not working" (logic only) | `fe` | standalone |
| "redesign + refactor this page (spec already exists)" | `ux` → `fe` | 2 steps |
| "implement new page from mockup" | `ux` → `fe` | 2 steps |
| "analyze requirements + build new page" | `sa` → `ux` → `fe` | 3 steps |
| "add new feature where fields/flow are unknown" | `sa` → `ux` → `fe` | 3 steps |
| "audit security flow then fix" | `sa` → `fe` | 2 steps (skip ux) |
| "analyze bug then fix" | `sa` → `fe` | 2 steps (skip ux) |
| "encountered error / runtime crash / X broken / X not working + have error stack" | `debug` | standalone |
| "after debug, need to redesign data model" | `debug` → `sa` → `fe` | 3 steps |
| "migrate / convert / refactor many files by pattern" (e.g. native select → USelect) | `migrate` | standalone |
| "migration that needs data shape change" | `sa` → `migrate` | 2 steps |
| "verify a fix / confirm feature works / test in real app" | `verify` | standalone (after fe/debug) |
| "run / launch app / open dev server / see screenshot" | `run` | standalone |
| "simplify / reduce code / find duplication after fixing" | `simplify` | standalone (after fe) |
| "write PR / draft PR description / create PR / เขียน PR / สร้าง PR / เปิด PR" | `pr` | standalone |
| "review PR / code review / view PR #X" | `review` | standalone |
| "security review of current branch / audit before merge" | `security-review` | standalone |
| "perf audit / a11y audit / lighthouse score" | `audit` | standalone |
| Short / ambiguous command / intent unclear (spec / design / code / unknown starting point) | invoke no skill | ask 1 question first, then return to pick pipeline |
| "config / package.json / docs / typo" | invoke no skill | — |

**Universal rules:**
- Order `sa → ux → fe` **must never be reversed** — spec must finish before design, design before code
- A step can be skipped only when **its input already exists** (e.g. clear spec → skip sa; no UI changes → skip ux)
- Every step must **hand off an artifact the next step can actually use** (see Handoff contracts in each skill's SKILL.md)
- **If no row matches** — ask 1 question first: "Do you need [spec / design / implementation] or which step to start from?" Never guess and pick the wrong pipeline
- **Ambiguous Thai phrases** (ช่วยดู / ช่วยทำ / ลอง / ปรับ / แก้ไข / เพิ่ม / เปลี่ยน — with no context object) → always call `AskUserQuestion` with 2-4 skill options; never assume

---

## Triggers per skill

### `sa` — System Analyst + Security Audit (think before writing / audit after writing)

Trigger when:
- User mentions: analyze, inspect, audit, security, threat model, OWASP, vulnerability, IDOR, XSS, CSRF, SSRF, SQLi, find bug, find vulnerability
- User mentions: gather requirements, create spec, use case, user story, sequence diagram, flow diagram, ER diagram, data model, API spec, state machine, edge case, acceptance criteria
- User asks: "how does this system work?", "what does this page do?", "what's the flow?", "ready for prod?", "is it secure enough?"
- Tasks that require understanding the full system before deciding — not editing a specific file directly

### `ux` — Visual / Interaction Design

Trigger when:
- User mentions: design, redesign, adjust UI, improve appearance, make it look better, modern, polish, responsive, mobile, layout, color, button, animation, transition, accessibility, mockup
- About to edit `.vue` / `.tsx` / `.jsx` / `.html` / `.css` / `.scss` in the template / style / class section
- User sends mockup / image / Figma link → if Figma URL, run `mcp__figma__add_figma_file` immediately before designing (see Figma MCP section)
- Task to implement a new page/component with UI

### `fe` — Frontend Code (logic / structure / type)

Trigger when:
- User mentions: write page, create component, refactor, write composable, store, API, schema, validate, fetch, state, reactivity, props, emit, type, TypeScript, Nuxt, Vue, valibot, Pinia, useState, useFetch, middleware, route guard, SSR, hydration
- About to edit `.vue` / `.ts` / `.tsx` / `.js` / `.jsx` in the `<script>` / logic section
- Task to review code for anti-patterns / dead code / naming / reactivity bugs
- Writing/editing valibot schema, Pinia store, composable, server route

### `migrate` — Bulk transformation across many files

Trigger when:
- User mentions: migrate, move, convert, refactor entire project, change X to Y everywhere, cleanup all occurrences, codemod, replace all
- Work where a repeated pattern is scattered across many files (e.g. native `<select>` → `USelect` project-wide, inline schema → `shared/schemas/`, deprecated API → new API)
- **Never use** for single-file edits (use `fe`) or designing new patterns (use `sa` first)

### `debug` — Bug diagnosis & fix

Trigger when:
- User mentions: debug, bug, broken, error, not working, strange behavior, why X, find root cause, diagnose, button not responding, page flickering, infinite loop
- User sends error stack / log / screenshot of console error
- Must trace to **root cause** not symptom; scan ripple of the same pattern elsewhere

### `pr` — Write & publish GitHub PR descriptions

Trigger when:
- User mentions: เขียน PR, สร้าง PR, draft PR, เปิด PR, ทำ PR, PR description, write PR, create PR, open PR, draft pull request, submit PR
- Branch has commits ready to merge and a PR needs to be opened or updated
- **Do not invoke** when user wants to review an existing PR → use `review` skill

---

## Pipeline: `sa → ux → fe → verify`

`sa` (spec) → `ux` (design) → `fe` (code) → `verify` — handoff checklist is in each skill's SKILL.md

**Flow rules:**
- Each step starts from the previous step's artifact, never from zero
- ux/fe encounters a spec gap → yield back to sa first, never guess
- fe finds a design that can't be implemented → yield back to ux to adjust, never hack
- Every step echoes what it received (1 line) before continuing

---

## Mid-task yield (switch skill mid-task)

While working in any step, if an issue outside the current skill's scope is found — **stop, identify the issue, then yield to the appropriate skill** — never continue with the wrong skill.

Examples:
- Running `fe` and finds a security vulnerability → **yield to `sa` mode B audit** before fixing
- Running `ux` and finds spec is incomplete (unknown what empty state should render) → **yield to `sa` mode A** to gather spec before designing
- Running `sa` analyzing a bug and finds the root cause is reactivity → **yield to `fe` review mode** to go into code detail

**Yield rules:**
- Tell the user clearly where you are yielding and why (1 line)
- Complete the yielded step before returning to the original skill
- On returning — apply the yield's result (never act as if the yield didn't happen)

**Checkpoint-before-yield (Fix 5 — mandatory, prevents context loss):**
Before switching to a yielded skill → save a project memory checkpoint immediately:
1. Write `project_phase_checkpoint_<current-phase>_YYYY-MM-DD.md` with `status: in_progress`
2. Body must include: what was completed so far + what the yield needs to resolve + where to resume
3. Only then announce the yield and switch skill
On returning from yield → read the checkpoint file to restore context before continuing (do not rely on conversation memory alone — it may have been compressed)

---

## Highest caution (cross-skill rule)

**"Fix one spot → break another"** must NEVER happen — enforced across all 3 skills.

Before **inspecting / proposing a fix / implementing** anything that touches existing code:

1. **trace caller / consumer** — prefer `mcp__codegraph__callers <symbol>` (semantic graph, instant); fallback to `rg "symbol"` for symbols created this session (index lag ~1-2s) or literal string patterns
2. **trace shared invariant** — is there shared state, type, schema, or route gate in use?
3. **trace persistence** — will old values in localStorage / DB / cache corrupt if the shape changes?
4. **trace cross-tab / cross-page sync** — any `storage` listeners / WebSocket / SSE that broadcast changes?
5. **list ripple files** — every file that must change together, named explicitly before starting

Full details in the `sa` skill section "Highest caution" — `fe` and `ux` must follow this same principle whenever touching existing code.

---

## General exceptions (do not invoke a skill)

- Config tasks (Nuxt config, package.json, env, CI/CD)
- Docs / pure markdown work
- Pure backend work that isn't part of the frontend stack
- General questions answerable from universal knowledge without reading code
- Trivial typo / comment / formatting fixes

---

## Skill memory loop — make skills smarter over time

> Core load/save logic lives in **Universal Phase 0** at the top of this file — this section covers only skill-specific conventions

### Memory hierarchy (3 tiers)

| Tier | Path | Scope | Loaded when |
|---|---|---|---|
| **Global** | `~/.claude/memory/` | Cross-project, user preference, workflow rule | Every task (Universal Phase 0) |
| **Project** | `~/.claude/projects/<id>/memory/` | Project-specific finding/pattern/constraint | Every task (Universal Phase 0) |
| **Skill learnings** | `~/.claude/skills/<skill>/learnings.md` | Cross-project per-skill pitfall (Vue reactivity, Tailwind JIT, OWASP pattern) | Only when skill is invoked (SKILL.md Phase 0.5) |

### Save triggers
See **Universal Phase 0 #4** above (9 triggers + table of where to save)

### Load logic
See **Universal Phase 0 #1-2** above (global → project → echo → conflict check)

### Skill tag convention in memory frontmatter

When saving a new memory → set the `skill:` field in `metadata` so each skill's Phase 0 can filter:

```yaml
---
name: feedback-uselect-empty-value
description: ...
metadata:
  type: feedback
  skill: fe              # or sa, ux, debug, migrate
  topic: nuxt-ui         # optional: extra filter keyword
---
```

Allowed values for `skill:`
- `fe` — frontend code logic / patterns
- `ux` — visual / design / interaction
- `sa` — requirement / spec / security
- `debug` — bug pattern / root cause / runtime error
- `migrate` — bulk migration / codemod
- `pr` — PR description writing / publishing
- `cross` — applicable to multiple skills (e.g. `feedback_verify_before_claiming_done`)

**Rule:** if the skill tag is omitted → defaults to `cross` (visible to every skill) — but always set it explicitly for proper filtering

### Graduation pipeline — promote repeated lessons up a tier

```
project memory (specific to one project)
    ↓ if recurring across ≥ 2 projects
global memory (~/.claude/memory/ — cross-project rule)
    ↓ if recurring across ≥ 3 projects with the same skill
skill learnings (~/.claude/skills/<skill>/learnings.md — per-skill rule)
    ↓ if the rule is load-bearing enough that the skill must always enforce it
SKILL.md rule (write directly into the skill)
    ↓
delete the source tier on promotion — already covered by the higher tier, no duplication
```

User runs `/distill-memory` (manual) to review + promote — Claude does NOT promote automatically (drift risk)

---

# MCP integrations — runtime observability layer

> Full per-MCP guides live at `~/.claude/mcp-guides/<name>.md` (loaded on-demand by skills that need them). The terse decision rules below are sufficient for most turns; skills consult their respective guide when going deep.

## When to consult which MCP

| Trigger | MCP | Full guide |
|---|---|---|
| Navigate / click / screenshot / console / network / evaluate / interact | **playwright-chromium** (default) | `~/.claude/mcp-guides/browser.md` |
| Lighthouse / perf trace / memory heap | **chrome-devtools** only | `~/.claude/mcp-guides/browser.md` |
| Cross-browser engine test (Firefox / WebKit) | **playwright-firefox / playwright-webkit** | `~/.claude/mcp-guides/browser.md` |
| Ripple check / call path / impact of editing existing symbol | **codegraph** | `~/.claude/mcp-guides/codegraph.md` |
| Live library docs (Nuxt UI, Valibot, Pinia, ...) | **context7** | `~/.claude/mcp-guides/context7.md` |
| Figma design file / nodes / comments | **figma** | `~/.claude/mcp-guides/figma.md` |

## Cross-MCP decision shortcuts

- **Browser MCP default = `playwright-chromium`.** Reserve `chrome-devtools` only for Lighthouse / perf trace / memory heap — tools unavailable in Playwright.
- **Existing symbol → `codegraph__callers` first**, fallback `rg` for new-session symbols or literal patterns; cross-verify both for high-risk changes.
- **External library API → `context7__query-docs` narrow** (1 feature per call) before guessing syntax. Skip if pattern already in `learnings.md`.
- **Figma URL → `add_figma_file` first**, then `view_node` for specific components. Notify user before `post_comment` / `reply_to_comment`.

## Quality preservation (cross-cutting)

- **Broad-vs-narrow:** never narrow-query (`evaluate_script` / `get_*`) without a hypothesis. Use one broad call (`take_snapshot` / `list_*`) first if unsure.
- **Caller-trace before declaring "no ripple":** `codegraph__callers` alone is not enough for type-contract / auth-gate changes — cross-verify with `rg`.
- **Token discipline:** see per-MCP guide for tool-by-tool token cost references. Open browser only when verify / reproduce / proof is required, never on every UI turn.

→ When a skill needs the full integration spec (Browser MCP token-saving toolkit, CodeGraph quality rules, Context7 schemas, Figma URL parsing), read the corresponding `~/.claude/mcp-guides/*.md` file.
