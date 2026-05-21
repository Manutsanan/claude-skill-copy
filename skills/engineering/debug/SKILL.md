---
name: debug
description: Use when diagnosing a bug, runtime error, or unexpected behavior — especially when error stack/log/screenshot is provided, or when user reports "X ไม่ทำงาน / X พัง / ทำไม X / เจอ error". Trace error → identify root cause (not symptom) → reproduce → fix → verify no regression. Trigger on Thai keywords debug/bug/พัง/error/ไม่ทำงาน/แปลกๆ/ทำไม/หา root cause/diagnose/วินิจฉัย and English keywords debug/bug/error/crash/broken/fix/diagnose/troubleshoot/why does X/X doesn't work/regression/edge case. Examples "ทำไม login ไม่ได้", "เจอ error 500 ตอน submit", "ปุ่มกดไม่ติด", "มี runtime error ใน console", "page กระพริบ", "loop infinite", "ดู error stack นี้ให้หน่อย". DO NOT use for designing fixes from scratch (use `sa` first to spec the fix), or for cosmetic UI bugs that aren't really errors (use `ux`).
---

# debug — Bug diagnosis & fix

**หลักการ:** หา root cause ก่อนแก้ — อย่าแก้แค่ symptom

---

## Mantra — recite verbatim, first thing in first response

ก่อนเริ่ม debug ทุก session ให้ **ท่องท่อนนี้ตรงตามตัวอักษร** (ห้าม paraphrase, ห้ามย่อ, ห้ามข้ามบรรทัด):

> **Debug mantra:**
> 1. **First is reproducibility.** Can the issue be reproduced reliably?
> 2. **Know the fail path.** Debugger / dev log first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it? Run disproof before proof.
> 4. **Every run is a breadcrumb.** Maintain the ledger. Cross-reference every entry.

**กฎ recital:**
- recite **ครั้งเดียวต่อ session** ใน response แรก (ไม่ recite ซ้ำกลาง session)
- recite **verbatim** เท่านั้น — ห้าม paraphrase / shorten / skip บรรทัด
- user บอก "ข้าม mantra" → ข้าม recital แต่ยัง **apply 4 ข้อในใจ** เงียบๆ
- ห้ามเสนอ fix ก่อน #1 (มี reliable repro)
- ห้าม test hypothesis ก่อน #2 (narrow fail path แล้ว)
- ห้าม commit hypothesis ก่อน #3 (พยายาม disprove แล้ว)
- ห้ามประกาศ root cause ก่อน #4 (cross-check ทุก breadcrumb แล้ว)

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (ดู `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: debug | cross | fe` + error message keyword (เช่น `SelectItem`, `Invalid end tag`, `Hydration mismatch`)
- **Learnings filter:** `~/.claude/skills/debug/learnings.md` by Tags (symptom keyword, max 5)
- **Pattern match:** ถ้า error pattern ตรงกับ memory → root cause มักจะเป็น pattern เดียวกัน → verify ก่อนแก้ (อย่าด่วนสรุป)
- **Pre-flight:** อ่าน error message + stack trace ทั้งหมด, CLAUDE.md ของ project, dev server log

---

## Handoff

- **ทำเองได้** — error message ชัด + reproducible + root cause อยู่ในไฟล์ที่ระบุได้ + fix เป็น code-level
- **Yield `sa`** — requirement กำกวม / fix ต้องเปลี่ยน data model / API contract / state machine
- **Yield `ux`** — visual issue (layout, animation jank) ไม่ใช่ logic
- **Yield `migrate`** — bug ปรากฏหลายไฟล์เพราะ pattern เดียวกัน

**Checklist ก่อน yield (ติ๊กครบ — ติ๊กไม่ครบ = diagnose ต่อ):**
- [ ] root cause file:line + ผ่าน 5 Whys (ไม่ใช่ "น่าจะเป็น X")
- [ ] ripple list ระบุแล้ว (หรือ "scan แล้ว 0 ที่อื่น")
- [ ] pre-brief พอให้ skill ถัดไปเริ่มได้ทันที
- [ ] ถ้า yield ไป `migrate` → pattern (regex + expected output) ชัดเจน

---

## ลำดับการคิด

### Step 1 — Read error literally

อ่าน error message **ตามตัวอักษร** ไม่ตีความเอง

ตัวอย่าง `A <SelectItem /> must have a value prop that is not an empty string.` → SelectItem ตัวใดตัวหนึ่งมี `value=""` — ไม่ใช่ "Reka UI bug" / "Vue version ผิด"

### Step 2 — Locate source (bottom-up stack)

ดู stack **bottom-up** หา **caller จากโค้ดเรา** (ข้าม internal frame ของ library)

### Step 3 — Reproduce locally

- Frontend: dev server + navigate + observe console/network
- API: curl ด้วย payload จาก user
- State: สร้าง state ที่ trigger

Reproduce ไม่ได้ → บอก user ตรงๆ + ขอ steps/screenshot/log

### Step 4 — Identify root cause (falsify-first)

**กฎทอง:** ถามตัวเอง "ถ้าแก้แค่นี้ — bug จะไปโผล่ที่อื่นไหม?"

ใช้ **5 Whys** ไล่จาก symptom → mechanism → context → why-no-test → why-not-caught

#### 4a. Ranked hypotheses (≥ 3)

- เขียน **3–5 hypotheses** เรียงตาม likelihood
- single-hypothesis thinking = anchoring bias
- นึก ≥ 3 ไม่ออก = ยังเข้าใจ fail path ไม่พอ → กลับ Step 2

#### 4b. Falsify before test (run disproof first)

สำหรับ hypothesis #1:
- **End-to-end check:** อธิบาย symptom ครบ flow (input → trigger → fail → observable)?
- **Cleanest disproof:** ทดลองที่ผล X = ถูก, Y = ผิด แยกชัด
- **Run disproof first.** ผ่าน disproof = ของจริง; ทะลุ = ทิ้ง, ใช้ #2
- ห้าม run "proof" (ลอง fix ดู) — fix อาจหาย bug ด้วยเหตุผลอื่น

#### 4c. Breadcrumb ledger (running log)

```
| # | What changed / probed         | What happened              | Rules in / out          |
|---|-------------------------------|----------------------------|-------------------------|
| 1 | flip items[0].value '' → null | error หาย                  | rules IN: items[0]='' = root |
| 2 | revert + console.log on mount | error fire on mount only   | rules OUT: race condition |
```

- ทุก hypothesis ใหม่ → walk ทั้ง ledger ก่อน adopt
- entry เก่าขัด hypothesis ใหม่ → refine หรือทิ้ง
- ค้าง 3+ entries ไม่ converge → ออกแบบ **single experiment** ที่แยก hypothesis ที่เหลือเด็ดขาด
- update ledger ทันทีหลังทุก experiment

### Step 5 — Fix + verify

1. แก้ที่ root cause ไม่ใช่ workaround
2. Verify: ทำ scenario เดิมซ้ำ → หาย; ทำ scenario ปกติ → ยังถูก (regression)
3. Trace ripple (Step 6)
4. Update memory ถ้าเป็น pattern ใหม่

### Step 6 — Trace ripple

ถ้า root cause = pattern (เช่น `value: ''`) → scan ทั้งโปรเจกต์:

```bash
grep -rn 'value: ""' app/ --include="*.vue" --include="*.ts"
grep -rn "value: ''" app/ --include="*.vue" --include="*.ts"
```

scan ทั้ง single + double quote เสมอ; เจอที่อื่น → fix ทุกจุด หรือ yield `migrate`

---

## Common error patterns (scan ก่อน diagnose)

### Reka UI / Nuxt UI 4
| Error | Root cause | Fix |
|---|---|---|
| `SelectItem must have a value prop that is not an empty string` | items มี `value: ''` หรือ `""` | เปลี่ยนเป็น `null` / sentinel |
| `Cannot read properties of null (reading 'type')` ใน patchElement | DOM unmount ระหว่าง patch (race) | follow up หลัง error อื่น — fix root error ก่อน |

### Vue template
| Error | Root cause | Fix |
|---|---|---|
| `Invalid end tag` | ลบ wrapper element ครึ่งทาง เหลือ `</div>` ค้าง | นับ `<div\b` vs `</div>` หาจุดเกิน |
| `Unexpected token` ใน template | syntax error ใน expression | อ่านบรรทัดที่ Vite ชี้ + 5 บรรทัดรอบๆ |

### Vue reactivity
| Error | Root cause | Fix |
|---|---|---|
| `computed` ไม่ update | source ไม่ reactive (destructure `reactive`) | ใช้ `toRefs()` / `storeToRefs()` |
| `watch` ไม่ fire | source เป็น primitive / getter ผิด | getter form: `watch(() => obj.foo, ...)` |
| Infinite loop ใน watch | watch แล้ว mutate source | `flush: 'post'` หรือ refactor |

### Auth / Multi-tab
| Symptom | Root cause | Fix |
|---|---|---|
| Reload loop | `location.reload()` หลัง redirect | ลบ reload — `navigateTo()` พอ |
| Tab desync | localStorage write ไม่มี cross-tab strategy | persistedstate `multitab` หรือ BroadcastChannel |

### Network / API
| Symptom | Root cause | Fix |
|---|---|---|
| 401 cascade | Layout `getProfile()` ไม่มี token guard | `if (!token) return` ก่อน API call |
| CORS error | server ไม่ allow origin | ตรวจ backend config |
| Empty response | API ส่ง 204 แต่ FE คาด JSON | check status ก่อน parse |

---

## Anti-patterns

- ❌ **Symptom fix แทน root cause** — เห็น error → ลบ component ทิ้ง; หา why ก่อน
- ❌ **try-catch กลบ error** — `try { ... } catch {}` ให้เงียบ; bug ฝังลึก
- ❌ **"อาจจะเป็น..." ไม่ verify** — ดู Network tab + reproduce + ระบุชัด
- ❌ **แก้ 1 จุดไม่ scan ที่อื่น** — Step 6 trace ripple ก่อนปิด ticket

---

## Quality gates (ก่อนปิดงาน)

- [ ] **Mantra recited** verbatim (หรือ user สั่งข้าม)
- [ ] **Memory scanned** — quote feedback ที่ตรง error pattern
- [ ] **Hypotheses ranked ≥ 3**
- [ ] **Disproof ran ก่อน proof** — ไม่ใช่ "fix แล้วหาย"
- [ ] **Breadcrumb ledger ครบ** + cross-checked
- [ ] **Root cause file:line + 5 Whys + สอดคล้อง ledger**
- [ ] **Reproduced ก่อนแก้**
- [ ] **Verify หลังแก้** — error หาย + ไม่มี regression
- [ ] **Ripple traced** — scan ทั้งโปรเจกต์ pattern เดียวกัน
- [ ] **Project memory updated** ถ้าเป็น bug pattern เฉพาะ project
- [ ] **Skill learnings updated** ถ้า symptom→root cause generalize ข้าม project
- [ ] **Build clean** — `tsc --noEmit` 0 errors + `curl /<page>` HTTP 200 + dev log clean
- [ ] **ห้ามเคลม "fixed"** ก่อนผ่านทุกข้อ — user เจอซ้ำ = root cause ผิด → กลับ Step 4

---

## Output style

```markdown
### Bug
- **Symptom:** <ที่เห็น>
- **Error message:** <quote literal>
- **Where:** file:line จาก stack

### Root cause
- **5 Whys:** Why → Why → Why → ...
- **ที่จริง:** <root cause + ทำไมเกิด>
- **Memory check:** <quote feedback ที่ตรง / "none">

### Fix
- **What changed:** file:line + diff
- **Why this fixes it:** <connect ไป root cause>

### Ripple check
- **Pattern scan:** <regex + result>
- **Other places affected:** <list / "none">

### Verify
- ✓ Error หายเมื่อทำซ้ำ scenario
- ✓ tsc 0 errors / curl HTTP 200 / dev log clean

### Memory update
- ✓ เพิ่ม feedback_<topic>.md (หรือ "ไม่จำเป็น เพราะ X")
```
