---
name: debug
description: Use when diagnosing a bug, runtime error, or unexpected behavior — especially when error stack/log/screenshot is provided, or when user reports "X ไม่ทำงาน / X พัง / ทำไม X / เจอ error". Trace error → identify root cause (not symptom) → reproduce → fix → verify no regression. Trigger on Thai keywords debug/bug/พัง/error/ไม่ทำงาน/แปลกๆ/ทำไม/หา root cause/diagnose/วินิจฉัย and English keywords debug/bug/error/crash/broken/fix/diagnose/troubleshoot/why does X/X doesn't work/regression/edge case. Examples "ทำไม login ไม่ได้", "เจอ error 500 ตอน submit", "ปุ่มกดไม่ติด", "มี runtime error ใน console", "page กระพริบ", "loop infinite", "ดู error stack นี้ให้หน่อย". DO NOT use for designing fixes from scratch (use `sa` first to spec the fix), or for cosmetic UI bugs that aren't really errors (use `ux`).
---

# debug — Bug diagnosis & fix

**Principle:** find root cause before fixing — never just patch the symptom

---

## Mantra — recite verbatim, first thing in first response

Before starting every debug session, **recite this block verbatim** (no paraphrasing, no shortening, no skipping lines):

> **Debug mantra:**
> 1. **First is reproducibility.** Can the issue be reproduced reliably?
> 2. **Know the fail path.** Debugger / dev log first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it? Run disproof before proof.
> 4. **Every run is a breadcrumb.** Maintain the ledger. Cross-reference every entry.

**Recital rules:**
- recite **once per session** in the first response (do not re-recite mid-session)
- recite **verbatim** only — no paraphrasing / shortening / line skipping
- user says "skip mantra" → skip recital but still **apply all 4 silently**
- never propose a fix before #1 (have reliable repro)
- never test a hypothesis before #2 (fail path narrowed)
- never commit to a hypothesis before #3 (disproof attempted)
- never declare root cause before #4 (every breadcrumb cross-checked)

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (see `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: debug | cross | fe` + error message keyword (e.g. `SelectItem`, `Invalid end tag`, `Hydration mismatch`)
- **Learnings filter:** `~/.claude/skills/debug/learnings.md` by Tags (symptom keyword, max 5)
- **Pattern match:** if error pattern matches memory → root cause is usually the same pattern → verify before fixing (do not jump to conclusion)
- **Pre-flight:** read full error message + stack trace, project CLAUDE.md, dev server log

---

## Progress tracker

Copy this block into your first response and tick boxes as you go. Do **not** skip a box — incomplete = keep diagnosing.

```
Debug progress:
- [ ] Mantra recited (or user said skip)
- [ ] Step 1: Read error literally (quote the message)
- [ ] Step 2: Locate source (bottom-up stack → our code)
- [ ] Step 3: Reproduce locally (MCP if available, else asked user)
- [ ] Step 4a: ≥ 3 ranked hypotheses written
- [ ] Step 4b: Disproof ran before proof
- [ ] Step 4c: Breadcrumb ledger updated
- [ ] Step 5: Fix at root cause + regression verified (re-reproduce in browser if MCP)
- [ ] Step 6: Ripple traced (whole-project scan)
- [ ] Memory updated (project + skill learnings as applicable)
- [ ] Quality gates passed
```

---

## Handoff

- **Handle solo** — error message is clear + reproducible + root cause is locatable to a specific file + fix is code-level
- **Yield `sa`** — ambiguous requirement / fix requires changing data model / API contract / state machine
- **Yield `ux`** — visual issue (layout, animation jank), not logic
- **Yield `migrate`** — bug appears across many files because of the same pattern

**Checklist before yielding (all boxes — incomplete = keep diagnosing):**
- [ ] root cause file:line + passed 5 Whys (not "probably X")
- [ ] ripple list identified (or "scanned, 0 other sites")
- [ ] pre-brief sufficient for next skill to start immediately
- [ ] if yielding to `migrate` → pattern (regex + expected output) is concrete

---

## Thinking order

### Step 1 — Read error literally

Read the error message **literally**, do not interpret.

Example: `A <SelectItem /> must have a value prop that is not an empty string.` → one of the SelectItems has `value=""` — not "Reka UI bug" / "wrong Vue version".

### Step 2 — Locate source (bottom-up stack)

Read the stack **bottom-up** to find the **caller from our code** (skip library internal frames). For semantic call path from any symbol → use `mcp__codegraph__trace <symbol>` to see the full caller chain instantly.

### Step 3 — Reproduce locally

- **Frontend (single-browser Chromium — chrome-devtools MCP):** dev server up → `navigate_page` → reproduce trigger → `list_console_messages` + `list_network_requests` + `evaluate_script` (inspect state at fail point) — see **Chrome DevTools playbook** below
- **Frontend (cross-browser bug — Playwright MCP):** bug reported only in Firefox/Safari → use `playwright-firefox` / `playwright-webkit` to reproduce in the affected engine — see **Playwright MCP playbook** below
- **Interaction gap (chrome-devtools can't do):** dropdown select → `browser_select_option`; browser back → `browser_navigate_back`; multi-tab desync → `browser_tabs` — use Playwright MCP
- **API:** curl with the user's payload
- **State:** construct the triggering state

Cannot reproduce → tell user directly + request steps/screenshot/log.

**Reproduce rule:** never skip Step 3 to guess root cause — a bug that can't be reproduced = fail path not yet understood

### Step 4 — Identify root cause (falsify-first)

**Golden rule:** ask yourself "if I only fix this — will the bug surface elsewhere?"

Use **5 Whys** from symptom → mechanism → context → why-no-test → why-not-caught.

#### 4a. Ranked hypotheses (≥ 3)

- write **3–5 hypotheses** ranked by likelihood
- single-hypothesis thinking = anchoring bias
- cannot think of ≥ 3 = fail path not understood → back to Step 2
- if any hypothesis involves "library API changed / deprecated / version mismatch" → query `mcp__context7__query-docs` with the error pattern **before** running experiments — confirms known breaking changes at ~500 tokens vs wasted experiment runs

#### 4b. Falsify before test (run disproof first)

For hypothesis #1:
- **End-to-end check:** does it explain the symptom across the full flow (input → trigger → fail → observable)?
- **Cleanest disproof:** design an experiment where X = pass, Y = fail are clearly separated
- **Run disproof first.** passes disproof = real; fails through = discard, use #2
- never run "proof" (try the fix and see) — fix may mask the bug for another reason

#### 4c. Breadcrumb ledger (running log)

```
| # | What changed / probed         | What happened              | Rules in / out          |
|---|-------------------------------|----------------------------|-------------------------|
| 1 | flip items[0].value '' → null | error gone                 | rules IN: items[0]='' = root |
| 2 | revert + console.log on mount | error fires on mount only  | rules OUT: race condition |
```

- every new hypothesis → walk the entire ledger before adopting
- older entry contradicts new hypothesis → refine or discard
- stuck at 3+ entries without convergence → design a **single experiment** that decisively separates the remaining hypotheses
- update ledger immediately after every experiment

### Step 5 — Fix + verify

1. Fix at the root cause, not a workaround
2. Verify: replay the failing scenario → gone; replay normal scenario → still passes (regression)
3. Trace ripple (Step 6)
4. Update memory if pattern is new

### Step 6 — Trace ripple

If root cause = pattern (e.g. `value: ''`) → scan the whole project:

- **Named symbol** (function / composable / type) → `mcp__codegraph__callers <symbol>` first (semantic, instant)
- **Literal string pattern** (e.g. `value: ""`, `value: ''`) → grep always:

```bash
grep -rn 'value: ""' app/ --include="*.vue" --include="*.ts"
grep -rn "value: ''" app/ --include="*.vue" --include="*.ts"
```

Always scan both single + double quotes; if other sites are found → fix all or yield `migrate`.

---

## Chrome DevTools MCP playbook (use instead of guessing from stack)

> Enable when MCP `chrome-devtools` is available + bug is frontend / runtime — token discipline in `~/.claude/CLAUDE.md` section "Chrome DevTools MCP integration"

### Reproduce flow (standard)

```
1. new_page (if none exists) + navigate_page <localhost url>
2. wait_for <selector indicating page loaded>     ← prevent flake from async/hydration
3. perform action that triggers the bug (click / fill / press_key)
4. list_console_messages                          ← actual errors / warnings
5. list_network_requests                          ← XHR fail / 4xx / 5xx
6. evaluate_script "JSON.stringify(<state>)"     ← inspect runtime state at failure point
7. (optional) take_screenshot                     ← proof for user
```

### Tool selection guide (choose by goal — token-aware)

| What you need to know | Tool | Token cost | Notes |
|---|---|---|---|
| Error message + warnings shown | `list_console_messages` / `get_console_message` | 500-2k | **Always start here** — cheap + on-point |
| Network fail / status code | `list_network_requests` → `get_network_request <id>` | 500-5k | Check silently failing XHR/Fetch |
| Runtime state (Vue/React reactive, computed, store) | `evaluate_script` | 100-2k | Inspect at the exact failure point |
| Element exists + uid | `take_snapshot` | 5-20k | Use only when interaction is needed |
| Screenshot of bug | `take_screenshot` | 1-3k | Proof for user, not for debugging |
| Memory leak / heap growth | `take_memory_snapshot` | 2-5k | Use paired with repeated reproductions |
| Jank / infinite loop / slow render | `performance_start_trace` → `stop` → `analyze_insight` | 5-15k | 3-5 seconds is enough |

### Pattern-specific reproduce recipes

| Symptom | MCP recipe |
|---|---|
| Reactivity not updating | `evaluate_script` "inspect ref/computed before and after trigger" → if value unchanged = source not reactive (see `Vue reactivity` table) |
| Hydration mismatch | `list_console_messages` → find `Hydration ... mismatch` → `evaluate_script` compare SSR vs client output |
| Infinite loop / page freeze | `performance_start_trace` 3 sec → `analyze_insight` find self-recursing function |
| 401 cascade / auth loop | `list_network_requests` → check request order → find request that fires before token is ready |
| Multi-tab desync | open 2 pages → `evaluate_script` set localStorage in tab 1 → check tab 2 via `evaluate_script` to see if synced |
| Click no response | `take_snapshot` → find button uid → `click uid=X` → `list_console_messages` check handler error |

### Anti-patterns (MCP-specific — avoid)

- **`take_snapshot` on every step** — costs 15-20k tokens each time; use only when uid is needed
- **`take_screenshot` instead of console check** — image doesn't reveal errors; use `list_console_messages` first
- **Opening browser without closing** — run `close_page` after session ends to prevent stale state
- **Snapshot before `wait_for`** — async not finished = reading wrong state
- **Using `evaluate_script` to run fix logic** — `evaluate_script` is for inspection only, not for patching code

### Fallback when MCP is unavailable

- Ask user to paste screenshot + steps to reproduce + console log
- State plainly: "debugging from stack + source only — not reproduced in a real browser"
- Do not declare root cause if not yet reproduced — keep progress tracker Step 3 incomplete

---

## Playwright MCP playbook (cross-browser reproduce)

> Use when: bug is browser-engine-specific ("works in Chrome, broken in Firefox/Safari"), multi-tab desync, or form interactions that chrome-devtools cannot do (select, navigate back, drop)
>
> MCP names: `playwright-chromium`, `playwright-firefox`, `playwright-webkit` — each is a separate MCP server; Playwright MCP restarts are required after `.claude.json` is edited

### Chrome-devtools vs Playwright — decision rule

| Need | Use | Why |
|---|---|---|
| Single-browser Chromium: console / network / state inspect | `chrome-devtools` | More tools: lighthouse, perf trace, memory snapshot, uid interaction |
| Bug reproduced only in Firefox | `playwright-firefox` | Real Firefox engine — emulation cannot substitute |
| Bug reproduced only in Safari / WebKit | `playwright-webkit` | Real WebKit engine |
| Multi-tab (same user, same session) | `playwright-*` + `browser_tabs` | Tab management within same context — cookies/storage shared across tabs |
| Multi-session isolation (different users / cookies) | Separate Claude CLI terminals | Each terminal = isolated context (`--isolated`); do NOT use browser_tabs for session isolation |
| Dropdown / select interaction | `playwright-*` + `browser_select_option` | chrome-devtools has no native select tool |
| Navigate back in flow | `playwright-*` + `browser_navigate_back` | chrome-devtools cannot go back in history |
| Drag-and-drop complete flow | `playwright-*` + `browser_drop` | chrome-devtools drag only, no drop target |

### Cross-browser reproduce flow (standard)

```
1. Reproduce bug in chrome-devtools first — confirm it is browser-specific (not server/code issue)
2. Switch to playwright-firefox / playwright-webkit for the affected engine
3. browser_navigate <same url>
4. browser_wait_for <selector>
5. Perform same trigger action (browser_click / browser_fill / browser_select_option)
6. browser_console_messages              ← compare with Chromium output
7. browser_network_requests              ← check if different XHR/Fetch behavior
8. browser_evaluate "() => <state>"      ← inspect runtime state at failure point
9. browser_take_screenshot               ← visual proof of the difference
```

### Pattern-specific recipes

| Symptom | Playwright recipe |
|---|---|
| "Layout broken in Safari" | `playwright-webkit` → `browser_navigate` → `browser_take_screenshot` → compare with Chromium screenshot |
| "Dropdown doesn't work in Firefox" | `playwright-firefox` → `browser_navigate` → `browser_select_option` → `browser_console_messages` |
| "Multi-tab session mismatch (same user)" | `playwright-chromium` → `browser_tabs` → set state in tab 1 → check tab 2 via `browser_evaluate` |
| "Multi-session mismatch (different users)" | 2 separate Claude CLI terminals → each with own isolated context (`--isolated`) → reproduce in parallel |
| "Back button breaks state" | `playwright-*` → navigate flow → `browser_navigate_back` → `browser_evaluate` compare state |
| "Form submit fails only in Firefox" | `playwright-firefox` → fill form → `browser_select_option` on selects → submit → `browser_console_messages` |

### Anti-patterns (Playwright-specific — avoid)

- **Switching to Playwright for single-browser issues** — chrome-devtools has more tools (lighthouse, perf, memory); use Playwright only when engine-specific behavior is the question
- **Skipping chrome-devtools reproduce first** — always confirm in Chromium first; if it reproduces in Chromium too, the issue is not browser-specific
- **Treating Playwright as a replacement for chrome-devtools** — both MCPs serve different roles; they are complementary not alternatives

### Fallback when Playwright MCP is unavailable

- Ask user to test in Firefox / Safari manually + send screenshot + console log
- State: "cross-browser testing not available — verified in Chromium only"

---

## Common error patterns (scan before diagnosing)

### Reka UI / Nuxt UI 4
| Error | Root cause | Fix |
|---|---|---|
| `SelectItem must have a value prop that is not an empty string` | items contain `value: ''` or `""` | change to `null` / sentinel |
| `Cannot read properties of null (reading 'type')` in patchElement | DOM unmounted mid-patch (race) | follow-up to another error — fix the root error first |

### Vue template
| Error | Root cause | Fix |
|---|---|---|
| `Invalid end tag` | wrapper element half-deleted, leaving dangling `</div>` | count `<div\b` vs `</div>` to find the extra |
| `Unexpected token` in template | syntax error in expression | read the line Vite points to + 5 surrounding lines |

### Vue reactivity
| Error | Root cause | Fix |
|---|---|---|
| `computed` does not update | source not reactive (destructured `reactive`) | use `toRefs()` / `storeToRefs()` |
| `watch` does not fire | source is primitive / wrong getter | getter form: `watch(() => obj.foo, ...)` |
| Infinite loop in watch | watcher mutates its source | `flush: 'post'` or refactor |

### Auth / Multi-tab
| Symptom | Root cause | Fix |
|---|---|---|
| Reload loop | `location.reload()` after redirect | remove reload — `navigateTo()` is enough |
| Tab desync | localStorage write lacks cross-tab strategy | persistedstate `multitab` or BroadcastChannel |

### Network / API
| Symptom | Root cause | Fix |
|---|---|---|
| 401 cascade | Layout `getProfile()` lacks token guard | `if (!token) return` before API call |
| CORS error | server does not allow origin | check backend config |
| Empty response | API returns 204 but FE expects JSON | check status before parsing |

---

## Anti-patterns

- **Symptom fix instead of root cause** — see error → delete component; find why first
- **try-catch swallowing error** — `try { ... } catch {}` silences it; bug buried
- **"maybe it is..." without verifying** — check Network tab + reproduce + identify clearly
- **Fix 1 site without scanning others** — Step 6 trace ripple before closing ticket

---

## Quality gates (before closing)

- [ ] **Mantra recited** verbatim (or user said skip)
- [ ] **Memory scanned** — quote feedback matching the error pattern
- [ ] **Hypotheses ranked ≥ 3**
- [ ] **Disproof ran before proof** — not "fixed it and it worked"
- [ ] **Breadcrumb ledger complete** + cross-checked
- [ ] **Root cause file:line + 5 Whys + consistent with ledger**
- [ ] **Reproduced before fixing**
- [ ] **Verified after fixing** — error gone + no regression
- [ ] **Ripple traced** — scanned whole project for the same pattern
- [ ] **Project memory updated** if bug pattern is project-specific
- [ ] **Skill learnings updated** if symptom→root cause generalizes across projects
- [ ] **Build clean** — `tsc --noEmit` 0 errors + `curl /<page>` HTTP 200 + dev log clean
- [ ] **Never claim "fixed"** before all boxes pass — user hits it again = wrong root cause → back to Step 4

---

## Output style

```markdown
### Bug
- **Symptom:** <what is observed>
- **Error message:** <quote literal>
- **Where:** file:line from stack

### Root cause
- **5 Whys:** Why → Why → Why → ...
- **Actual cause:** <root cause + why it happens>
- **Memory check:** <quote matching feedback / "none">

### Fix
- **What changed:** file:line + diff
- **Why this fixes it:** <connect to root cause>

### Ripple check
- **Pattern scan:** <regex + result>
- **Other places affected:** <list / "none">

### Verify
- Error gone on scenario replay
- tsc 0 errors / curl HTTP 200 / dev log clean

### Memory update
- Added feedback_<topic>.md (or "not needed because X")
```
