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

### Phase checkpoint — `~/.claude/projects/<id>/memory/project_phase_checkpoint_*.md`
- After loading project memory → scan for files named `project_phase_checkpoint_*.md` in the same folder
- If a checkpoint with `status: in_progress` is found → echo it to the user + ask whether to **resume** (load artifact from checkpoint) or **start fresh** (mark checkpoint as `abandoned`)
- If no checkpoint or all checkpoints are `status: complete` → skip

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
- Match user intent to the appropriate skill
- Falls under an exception (config / docs / typo / general question) → do not invoke a skill, handle directly
- Invoking a skill → that skill will run **Phase 0.5** itself (loads `~/.claude/skills/<skill>/learnings.md`)

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

# Chrome DevTools MCP integration — runtime observation layer

> **MCP `chrome-devtools` is Claude's "eyes + hands" in the browser** — transforms skills from "writing code blind" → "observe runtime + verify for real" for tasks touching UI / runtime behavior
>
> This section is mandatory for **both built-in skills (verify / run / security-review) that can't be edited directly** + **custom skills (debug / ux / audit / fe)** that have their own integration section

## When to open the browser (trigger map)

| Trigger | Skill | Primary tool |
|---|---|---|
| User requests verify / before declaring done when UI was touched | `verify` / all skills | `navigate_page` → `click` → `take_snapshot` → `list_console_messages` |
| Error stack / runtime crash / X broken / X not working | `debug` | reproduce → `list_console_messages` + `list_network_requests` + `evaluate_script` |
| User requests to open app / "show me it running" | `run` | `new_page` → `navigate_page` → `take_screenshot` |
| After finishing a style batch / before claiming ux done | `ux` | `take_screenshot` + `resize_page` + `emulate` + (optional) `lighthouse_audit` |
| User requests perf / a11y audit | `audit` | `lighthouse_audit` + `performance_start_trace`/`stop`/`analyze_insight` + `take_memory_snapshot` |
| Reviewing code that touches auth / cookie / CSP / CORS | `security-review` | `list_network_requests` (header) + `evaluate_script` (cookie/CSP) + `get_console_message` |
| Verifying reactivity / hydration / memory leak | `fe` (opt-in) | `evaluate_script` + `list_console_messages` + `take_memory_snapshot` |

**Do not open browser when:** spec/requirement (`sa` mode A), static codemod (`migrate`), backend-only logic, config/docs, typo, simplify, init

## Token cost reference (know the price before choosing a tool)

MCP token impact varies widely — know the price before choosing:

| Tool | Token cost | Use when |
|---|---|---|
| `take_snapshot` of large dashboard page | 15-20k 🔴 | Need uid of element to interact |
| `take_snapshot` of small page | 5-10k 🟡 | Need uid + a11y tree |
| `take_screenshot` (viewport) | 1-3k 🟢 | Need to see page / proof |
| `lighthouse_audit` (1 category) | 3-5k 🟡 | Check a11y/perf score |
| `lighthouse_audit` (all categories) | 10-15k 🔴 | Forbidden unless user asks for full audit |
| `performance_analyze_insight` (5s trace) | 5-10k 🟡 | Diagnose initial load |
| `performance_analyze_insight` (30s trace) | 15-30k 🔴 | Forbidden unless steady-state issue |
| `list_console_messages` | 500-2k 🟢 | Explore console |
| `list_network_requests` | 500-5k 🟢 | Explore network |
| `evaluate_script` | 100-2k 🟢 | Inspect specific value |
| `get_console_message <i>` / `get_network_request <id>` | 200-500 🟢 | Know index/id, narrow lookup |
| `take_memory_snapshot` | 2-5k 🟡 | Diagnose memory leak |

**Principle:** open browser only when necessary (verify / reproduce / proof) — never on every turn that touches UI

## Broad-vs-narrow decision rule (mandatory — apply before every browser tool call)

> **Core rule:** explore broad first, narrow later — never narrow from the start if you don't know what to ask

Before **every** browser tool call, answer one question internally: "Do I know what to look for?"

| Situation | Answer | Tool to use |
|---|---|---|
| Know exactly what to check (have hypothesis) | ✅ Yes — narrow | `evaluate_script` / `get_console_message` / `get_network_request` |
| Don't know, need to explore first (strange bug, first time on this page) | ❌ No — broad first | `take_snapshot` / `take_screenshot` / `list_console_messages` |
| Need proof to show user | ✅ Yes — but visual | `take_screenshot` |
| Check visual regression | ✅ Yes — but context | `take_screenshot` (full page) |

**Mandatory:** never use `evaluate_script` blindly on first debug — wrong query will miss the bug. Use a broad tool once to see the overall picture, then narrow.

## Token-saving toolkit (mandatory — apply on every browser tool call)

### 🟢 Safe-always (use anytime, no trade-off)

1. **Combine multiple checks in a single `evaluate_script`** — atomic state + ~80% savings
   ```js
   evaluate_script("JSON.stringify({
     state: <inspect 1>,
     errors: <inspect 2>,
     network: <inspect 3>
   })")
   ```

2. **Use `get_*` instead of `list_*` when index/id is known** — `get_console_message <i>`, `get_network_request <id>`

3. **`wait_for` a specific selector before observing** — prevents flake + reduces re-snapshots

4. **Specify Lighthouse category** — `category=performance` or `category=accessibility` separately (never run all 5 unless user asks for full audit)

5. **Performance trace 3-5 seconds + `reload: true`** — never exceed 10s unless diagnosing a steady-state issue

6. **Close page when task ends** — `close_page` before session ends

### 🟡 Context-dependent (use only in the stated context)

7. **Cache uid across calls** — OK for **static elements** (nav, header, app shell); **never** for list/dynamic/reactive components → re-snapshot whenever a component may remount

8. **Element-only screenshot (`uid=X`)** — use for component spec check; **never** for visual regression (needs full page)

9. **Batch actions before observing** — use for **success-path verify**; **never** during step-by-step debug (hides intermediate bugs)

10. **Same-page `navigate_page` instead of `new_page`** — use for continuous flow; **never** when isolation testing is required (auth, fresh state)

### 🔴 Avoid-by-default (forbidden unless truly necessary)

11. **`take_snapshot` on every step** — only when a fresh uid is needed; **never** as a replacement for screenshot
12. **`take_snapshot` on a large dashboard page** (> 50 components) — use a targeted `evaluate_script` query instead
13. **Lighthouse on every page** — pick 2-3 key pages (landing/dashboard/form) only
14. **Screenshot after every click** — observe only when you expect to have reached the target state

## Decision flow (mandatory — walk this flow before every tool call)

```
1. Do I know what to check?
   ├─ No → 1 broad tool call (snapshot/screenshot/list_*) → return to #1
   └─ Yes → go to #2

2. Which tool fits best?
   ├─ runtime value → evaluate_script (combine checks)
   ├─ console error → get_console_message <i> or list_console_messages
   ├─ network fail → get_network_request <id> or list_network_requests
   ├─ visual proof → take_screenshot
   └─ need to interact → take_snapshot (for uid) then cache

3. Is the tool on the 🔴 avoid list?
   ├─ Yes → return to #2, pick alternative
   └─ No → call

4. After call: did you get the data needed?
   ├─ Yes → continue
   └─ No → refine query (do NOT re-snapshot immediately)
```

## Quality preservation (prevent optimization from breaking quality)

Token-saving rules **do not reduce quality** when the decision rule above is followed. But forcing narrow from the start causes:

- **Missed bug** from wrong query direction → always broad first
- **Stale uid click** → re-snapshot whenever DOM may change
- **Layout regression invisible** → use full-page screenshot for visual regression
- **Intermediate bug hidden** → never batch during debug

If the user says "why didn't you see the bug" / "verify passed but it's broken in real run" / "why didn't you catch it" = optimization was too aggressive → return to broad scan + interrogate root cause

## Fallback when MCP is unavailable

If MCP `chrome-devtools` is offline / dev server isn't running / user disabled MCP — fall back in order:

1. Ask user to paste screenshot / console log instead (manual capture is more accurate for real-env visual state)
2. For verify → say plainly: "verify is code-level only (tsc + test) — not tested in a real browser". Never blanket-claim done
3. For debug → ask user for steps to reproduce + browser/version

## Manual paste vs MCP — use together, not either-or

- **Manual paste is more accurate for:** the user's real state (auth, cookie, prod data), env-specific bugs, user context (arrows, "this part")
- **MCP is more accurate for:** structural DOM (uid + a11y tree), runtime state (JS/network/console), reproduce + verify fix, responsive testing
- **Best workflow:** manual paste → start understanding the bug; MCP → dig out root cause + verify fix

## Skill integration reference

Custom skills with their own chrome-devtools section (read each skill's SKILL.md for specifics):
- `debug/SKILL.md` — reproduce + inspect runtime state instead of guessing from stack
- `ux/SKILL.md` — visual verification + responsive + a11y after a style batch
- `audit/SKILL.md` — lighthouse + perf trace + memory snapshot
- `fe/SKILL.md` — opt-in for reactivity/hydration verification

Built-in skills (verify / run / security-review) — use the trigger map + token discipline above as the guide, since these skills can't be edited directly

---

# CodeGraph MCP integration — codebase intelligence layer

> **MCP `codegraph` is the "semantic map" of the codebase** — transforms ripple checks from line-by-line grep → semantic graph traversal that knows call paths, impact, and callers instantly
>
> This section is mandatory for **every skill that needs a ripple check** (sa / fe / debug / migrate) before editing existing code

## Trigger map (which tool to use, when)

| Trigger | Skill | Tool |
|---|---|---|
| Ripple check before editing an existing symbol | all skills | `mcp__codegraph__callers <symbol>` |
| View call path / trace A calls B calls C | `debug` Step 2 | `mcp__codegraph__trace <symbol>` |
| Understand what this file/component does + connects to | `sa` mode A | `mcp__codegraph__context <file>` |
| Find a symbol whose name is uncertain | all skills | `mcp__codegraph__search <keyword>` |
| Analyze impact if this symbol changes | `sa` / `fe` | `mcp__codegraph__impact <symbol>` |
| View symbol details (type, location, signature) | all skills | `mcp__codegraph__node <symbol>` |
| View source of multiple symbols at once | `sa` / `migrate` | `mcp__codegraph__explore <sym1> <sym2>` |
| View what this symbol calls (outgoing) | `fe` / `debug` | `mcp__codegraph__callees <symbol>` |

## Decision rule (rg vs codegraph)

| Situation | Tool |
|---|---|
| Symbol created in this session (index lag ~1-2s) | `rg` always |
| Literal string / comment / non-code text | `rg` always |
| Existing symbol + need semantic callers | `mcp__codegraph__callers` first |
| Critical + high-risk change | cross-verify both: `mcp__codegraph__impact` + `rg` |

## Project index (must init before use in each project)

```bash
codegraph init -i   # run once in the project root dir
```

If not yet initialized → tools will error or return empty → fallback to `rg` immediately + tell user to run init

## Token cost reference

| Tool | Token cost | Use when |
|---|---|---|
| `codegraph__callers` | ~200-500 🟢 | Ripple check before every symbol change |
| `codegraph__trace` | ~200-500 🟢 | Call path from crash site |
| `codegraph__search` | ~100-300 🟢 | Symbol discovery |
| `codegraph__impact` | ~500-1k 🟡 | High-risk or cascading change |
| `codegraph__context` | ~1-3k 🟡 | Understanding a file's role |
| `codegraph__explore` | ~1-5k 🟡 | Multi-symbol source dump |

## Quality rules

- Never declare "no ripple" from `codegraph__callers` alone if the change is critical (type contract / auth gate) — cross-verify with `rg` too
- If `codegraph__callers` returns empty + the symbol should have callers → suspect stale index → run `rg` then tell user to run `codegraph init -i` again
- If project has no `.codegraph/codegraph.db` → do not reference codegraph — fallback to `rg` + tell user to init first

## Skill integration reference

Skills with their own CodeGraph section:
- `sa/SKILL.md` — context loading + impact analysis in reference tracing checklist
- `fe/SKILL.md` — callers check before touching existing code
- `debug/SKILL.md` — trace call path in Step 2 + callers in Step 6
- `migrate/SKILL.md` — callers discovery in Phase 0 Discover

---

# Context7 MCP integration — live library documentation layer

> **MCP `context7` is the "live docs" layer** — fetches real documentation for external libraries by version, injecting it into the prompt instead of relying on stale training data
>
> This section is mandatory for `fe` + `debug` + `migrate` + `sa` when the task involves **external library APIs** — not internal code

## Trigger map (which tool to use, when)

| Trigger | Skill | Tool |
|---|---|---|
| Writing code using a new external library API (Nuxt UI, Valibot, Pinia, useFetch) | `fe` | `resolve-library-id` → `query-docs` |
| Error pointing to library behavior / breaking change | `debug` Step 4a | `query-docs <error pattern>` |
| Migrating between library versions | `migrate` Phase 0 | `resolve-library-id` → `query-docs "migration guide"` |
| Specifying API that depends on external library (opt-in) | `sa` mode A | `query-docs <API feature>` |

## Tool names

- `mcp__context7__resolve-library-id` — convert library name → Context7-compatible library ID
- `mcp__context7__query-docs` — fetch docs by library ID + query

## Decision rule (query vs skip)

| Situation | Action |
|---|---|
| Library is internal / custom package | ❌ skip — no index |
| Pattern already exists in `learnings.md` | ⚠️ skip — cached |
| Library in default stack + unfamiliar new API | ✅ query |
| Error may be caused by library version change | ✅ query always |
| Migrating library major/minor version | ✅ query always |

## Token cost reference

| Tool | Token cost | Note |
|---|---|---|
| `resolve-library-id` | ~100-200 🟢 | Run once per library per session |
| `query-docs` (narrow query) | ~500-2k 🟢 | Keep query specific — "UButton loading prop" not "all of Nuxt UI" |
| `query-docs` (broad query) | ~2-10k 🔴 | Forbidden — adds tokens unnecessarily |

## Quality rules

- **Always query narrow** — 1 specific feature per call; never query just the library name
- **1 library per call** — never combine queries for multiple libraries in one call
- Library not in index → fallback to official docs from training data + tell user
- Confirmed patterns → save to `~/.claude/skills/<skill>/learnings.md` to skip querying next time

## Skill integration reference

- `fe/SKILL.md` — query before implementing new library-specific API
- `debug/SKILL.md` — query in Step 4a when hypothesis involves library breaking change
- `migrate/SKILL.md` — query in Phase 0 Discover when migrating library version
- `sa/SKILL.md` — query opt-in when spec depends on external library API

---

# Figma MCP integration — design source layer

> **MCP `figma` is the "design source" layer** — loads Figma design directly into context + views thumbnails of specific nodes + reads/writes design comments
>
> This section is mandatory for `ux` primarily + `sa` for requirement gathering from Figma comments

## Tool signatures (real — from schema)

| Tool | Required params | Returns |
|---|---|---|
| `mcp__figma__add_figma_file` | `url` (Figma file URL) | Design structure + file_key loaded into context |
| `mcp__figma__view_node` | `file_key`, `node_id` (`<n>:<n>`) | **Thumbnail image** of that node |
| `mcp__figma__read_comments` | `file_key` | All comments on the file |
| `mcp__figma__post_comment` | `file_key`, `message`, `x`, `y` (+ optional `node_id`) | Posts comment at coordinate |
| `mcp__figma__reply_to_comment` | `file_key`, `comment_id`, `message` | Reply to existing comment |

**Extract params from URL:**
- `file_key` — from `figma.com/file/<file_key>/...` or `figma.com/design/<file_key>/...`
- `node_id` — from URL param `?node-id=<n>-<n>` → convert `-` to `:` → `<n>:<n>`

## Trigger map (which tool to use, when)

| Trigger | Skill | Tool |
|---|---|---|
| User sends Figma URL (first time in session) | `ux` | `add_figma_file` — load full design structure first |
| Need visual of a specific component | `ux` | `view_node` (specify narrow node_id) |
| Read design comments / feedback | `sa` / `ux` | `read_comments` |
| Reply or post comment on Figma | `sa` | `reply_to_comment` / `post_comment` — **always notify user first** |

## Decision rule

| Situation | Action |
|---|---|
| User sends Figma URL | ✅ `add_figma_file` always — gets structured design data |
| Need visual confirmation of component after add | `view_node` with specific node_id only |
| Figma requires auth / incorrect URL | ❌ fallback → ask user for screenshot + description |
| Need live visual of Figma | `take_screenshot` via chrome-devtools on the Figma URL |

## Quality rules

- **Always `add_figma_file` first** when encountering a new Figma URL — never skip, even if "you think you know it"
- **`view_node` specifies a specific node** not the root node of the full page — cost grows with subtree size
- **Figma values are source of truth** — spacing/color/font from design → use directly, never estimate
- **Before post/reply comment** → notify user first every time, because it is visible to other designers

## Skill integration reference

- `ux/SKILL.md` — `add_figma_file` before designing from Figma + `view_node` to confirm specific components
- `sa/SKILL.md` — `read_comments` to gather requirements from design feedback
