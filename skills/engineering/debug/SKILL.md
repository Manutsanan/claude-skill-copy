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

- **Frontend (prefer chrome-devtools MCP):** dev server up → `navigate_page` → reproduce trigger → `list_console_messages` + `list_network_requests` + `evaluate_script` (inspect state at fail point) — see **Chrome DevTools playbook** below
- **API:** curl with the user's payload
- **State:** construct the triggering state

Cannot reproduce → tell user directly + request steps/screenshot/log.

**Reproduce rule:** ห้ามข้าม Step 3 ไปเดา root cause — bug ที่ reproduce ไม่ได้ = ยังไม่เข้าใจ fail path

### Step 4 — Identify root cause (falsify-first)

**Golden rule:** ask yourself "if I only fix this — will the bug surface elsewhere?"

Use **5 Whys** from symptom → mechanism → context → why-no-test → why-not-caught.

#### 4a. Ranked hypotheses (≥ 3)

- write **3–5 hypotheses** ranked by likelihood
- single-hypothesis thinking = anchoring bias
- cannot think of ≥ 3 = fail path not understood → back to Step 2

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

## Chrome DevTools MCP playbook (ใช้แทนการเดาจาก stack)

> เปิดใช้เมื่อมี MCP `chrome-devtools` พร้อม + bug เป็น frontend / runtime — token discipline ดูใน `~/.claude/CLAUDE.md` section "Chrome DevTools MCP integration"

### Reproduce flow (มาตรฐาน)

```
1. new_page (ถ้ายังไม่มี) + navigate_page <localhost url>
2. wait_for <selector ที่บ่งบอกว่าโหลดเสร็จ>     ← กัน flake จาก async/hydration
3. ทำ action ที่ trigger bug (click / fill / press_key)
4. list_console_messages                          ← error / warning จริง
5. list_network_requests                          ← XHR fail / 4xx / 5xx
6. evaluate_script "JSON.stringify(<state>)"     ← inspect runtime state ที่จุดพัง
7. (optional) take_screenshot                     ← proof สำหรับ user
```

### Tool selection guide (เลือกตาม goal — token-aware)

| ต้องการรู้อะไร | Tool | Token cost | หมายเหตุ |
|---|---|---|---|
| Error message + warning ที่ปรากฏ | `list_console_messages` / `get_console_message` | 500-2k | **เริ่มจากนี่เสมอ** — ถูก + ตรงประเด็น |
| Network fail / status code | `list_network_requests` → `get_network_request <id>` | 500-5k | ตรวจ XHR/Fetch ที่ silent fail |
| Runtime state (Vue/React reactive, computed, store) | `evaluate_script` | 100-2k | inspect ตรงจุด ไม่ต้องเดา |
| Element มีอยู่ไหม + uid | `take_snapshot` | 5-20k | ใช้เฉพาะเมื่อต้อง interact ต่อ |
| ภาพหน้าจอตอน bug | `take_screenshot` | 1-3k | proof สำหรับ user, ไม่ใช่ debug |
| Memory leak / heap growth | `take_memory_snapshot` | 2-5k | ใช้คู่กับ reproduce ซ้ำๆ |
| Jank / infinite loop / slow render | `performance_start_trace` → `stop` → `analyze_insight` | 5-15k | trace 3-5 วินาทีพอ |

### Pattern-specific reproduce recipes

| Symptom | MCP recipe |
|---|---|
| Reactivity ไม่ update | `evaluate_script` "ดู ref/computed ก่อนและหลัง trigger" → ถ้าค่าไม่เปลี่ยน = source ไม่ reactive (ดู `Vue reactivity` table) |
| Hydration mismatch | `list_console_messages` → หา `Hydration ... mismatch` → `evaluate_script` เทียบ SSR vs client output |
| Infinite loop / page freeze | `performance_start_trace` 3 sec → `analyze_insight` หา function ที่ self-recurse |
| 401 cascade / auth loop | `list_network_requests` → ดู order ของ request → หา request ที่ fire ก่อน token พร้อม |
| Multi-tab desync | เปิด 2 page → `evaluate_script` set localStorage ที่ tab 1 → ดู tab 2 ผ่าน `evaluate_script` ว่า sync ไหม |
| Click no response | `take_snapshot` → ดู uid ของปุ่ม → `click uid=X` → `list_console_messages` ดู handler error |

### Anti-patterns เฉพาะ MCP (อย่าทำ)

- **`take_snapshot` ทุก step** — กิน 15-20k tokens/ครั้ง; ใช้เมื่อต้องการ uid เท่านั้น
- **`take_screenshot` แทน console check** — ภาพไม่บอก error; ใช้ `list_console_messages` ก่อน
- **เปิด browser แล้วไม่ปิด** — `close_page` หลังจบ session กัน state ค้าง
- **Snapshot ก่อน `wait_for`** — async ยังไม่เสร็จ = อ่านได้ผิด state
- **ใช้ `evaluate_script` รัน fix logic** — `evaluate_script` ใช้ inspect เท่านั้น ไม่ใช่ patch โค้ดเป็นทางการ

### Fallback เมื่อ MCP ใช้ไม่ได้

- ขอ user paste screenshot + steps to reproduce + console log
- บอกตรงๆ ว่า "debug ด้วย stack + source อย่างเดียว — ไม่ได้ reproduce ใน browser จริง"
- อย่า declare root cause ถ้ายังไม่ได้ reproduce — เก็บ progress tracker Step 3 ค้างไว้

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
