---
name: debug
description: Use when diagnosing a bug, runtime error, or unexpected behavior — especially when error stack/log/screenshot is provided, or when user reports "X ไม่ทำงาน / X พัง / ทำไม X / เจอ error". Trace error → identify root cause (not symptom) → reproduce → fix → verify no regression. Trigger on Thai keywords debug/bug/พัง/error/ไม่ทำงาน/แปลกๆ/ทำไม/หา root cause/diagnose/วินิจฉัย and English keywords debug/bug/error/crash/broken/fix/diagnose/troubleshoot/why does X/X doesn't work/regression/edge case. Examples "ทำไม login ไม่ได้", "เจอ error 500 ตอน submit", "ปุ่มกดไม่ติด", "มี runtime error ใน console", "page กระพริบ", "loop infinite", "ดู error stack นี้ให้หน่อย". DO NOT use for designing fixes from scratch (use `sa` first to spec the fix), or for cosmetic UI bugs that aren't really errors (use `ux`).
---

# debug — Bug diagnosis & fix

> หลักการ: **หา root cause ก่อนแก้ — อย่าแก้แค่ symptom**
> ตัวอย่างที่เคยพังในโปรเจกต์นี้:
> - `Invalid end tag` — symptom = error ที่ `</template>` line สุดท้าย, root cause = ลืม `</div>` ตอน migrate wrapper
> - `SelectItem must have a value prop that is not an empty string` — symptom = Reka UI throw, root cause = items array มี `value: ''`
> - Multi-tab reload loop — symptom = หน้ากระพริบ, root cause = `location.reload()` ใน 401 handler

---

## Mantra — recite verbatim, as the first thing in the first response

ก่อนเริ่ม debug ทุก session ให้ **ท่องท่อนนี้ตรงตามตัวอักษร** (ห้าม paraphrase, ห้ามย่อ, ห้ามข้ามบรรทัด) แล้วค่อยเข้า Phase 0:

> **Debug mantra:**
> 1. **First is reproducibility.** Can the issue be reproduced reliably?
> 2. **Know the fail path.** Debugger / dev log first; then source trace + knob enumeration; then in-code instrumentation.
> 3. **Question your hypothesis.** What would disprove it? Run disproof before proof.
> 4. **Every run is a breadcrumb.** Maintain the ledger. Cross-reference every entry.

แล้วค่อย start work — apply 4 ข้อนี้ **ตามลำดับ** ใน Step 1–5 ด้านล่าง

**กฎ recital:**
- recite **ครั้งเดียวต่อ session** ใน response แรก (ไม่ recite ซ้ำกลาง session)
- recite **verbatim** เท่านั้น — ห้าม paraphrase / shorten / skip บรรทัด
- ถ้า user บอก "ข้าม mantra" → ข้าม recital แต่ยังต้อง **apply 4 ข้อในใจ** เงียบๆ
- ห้ามเสนอ fix ก่อน #1 (มี reliable repro)
- ห้าม test hypothesis ก่อน #2 (narrow fail path แล้ว)
- ห้าม commit hypothesis ก่อน #3 (พยายาม disprove แล้ว)
- ห้ามประกาศ root cause ก่อน #4 (cross-check ทุก breadcrumb แล้ว)

---

## Phase 0 — Load memory hierarchy (mandatory — extend Universal Phase 0)

ลำดับ:

1. **Load global memory** — `~/.claude/memory/MEMORY.md`
   - filter: `metadata.skill: debug` หรือ `skill: cross` หรือ `skill: fe` (bug ส่วนใหญ่อยู่ฝั่ง fe)
   - filter ต่อด้วย **error message keyword** (เช่น "SelectItem", "Invalid end tag", "Hydration mismatch")
   - ถ้าไม่มีไฟล์ → ข้าม + หมายเหตุ "ไม่มี global memory"

2. **Load project memory** — `~/.claude/projects/<project-id>/memory/MEMORY.md`
   - project id = working directory แปลง `/` → `-`
   - filter เดียวกับ global memory
   - ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory — fresh debug"

3. **Echo top 3-5 entries** กลับให้ user เห็นก่อน diagnose:
   ```
   📚 Memory ที่ตรงกับ error pattern นี้ (debug):
   - [project] feedback_select_item_value_empty_string — root cause มัก = items มี value=''
   - [project] feedback_dangling_tag_after_wrapper_removal — มัก = ลืม </div> ตอน migrate

   จะตรวจสมมติฐานนี้ก่อน หา caller / scan pattern เดียวกัน
   ```

4. **Pattern match** — ถ้า error pattern ตรงกับ memory → root cause มักจะเป็น pattern เดียวกัน → verify ก่อนแก้ (อย่าด่วนสรุป)

5. **หลังจบงาน** — save lesson ตาม **8 universal save triggers** ใน `~/.claude/CLAUDE.md` Universal Phase 0 #4 — โดยเฉพาะ "root cause + ripple list"

### Memory ที่ `debug` ต้องเช็คทุกครั้ง (ถ้ามีใน project)

- `feedback_select_item_value_empty_string.md` — Reka UI runtime error
- `feedback_dangling_tag_after_wrapper_removal.md` — Invalid end tag
- `feedback_grep_multiline_attrs.md` — regex pitfall ใน Vue templates
- `feedback_vite_cache_stuck_after_syntax_error.md` — HMR ไม่ recover
- `feedback_template_vif_slot_reactivity.md` — slot existence ไม่ reactive

### Pre-flight อื่นๆ (ทำคู่กับ Phase 0)

1. **อ่าน error message + stack trace ทั้งหมด** — อย่าอ่านแค่บรรทัดแรก
2. **อ่าน CLAUDE.md ของโปรเจกต์** — บางครั้ง bug เกิดจากการไม่ตาม convention
3. **อ่าน dev server log** ถ้ามี (เช่น `tail /tmp/.../tasks/<id>.output`)

> ดู `~/.claude/CLAUDE.md` Universal Phase 0 สำหรับ load/save logic เต็ม + skill tag convention

---

## Phase 0.5 — Load skill learnings (mandatory)

ลำดับ:

1. **Extract symptom keywords** — จาก error message / stack trace / user description: ชื่อ error (`Invalid end tag`, `SelectItem`, `hydration mismatch`), component ที่ throw, pattern (`reload loop`, `reactivity`, `ssr`, `race`)
2. **อ่าน** `~/.claude/skills/debug/learnings.md` — scan เฉพาะ **Tags:** field ของแต่ละ entry
3. **Load เฉพาะ entry ที่ตรง** — entry ผ่านถ้า Tags มี ≥1 keyword ตรง **และ header ไม่มี `~~`**; ถ้าไม่มี tag ตรงหรือ header มี `~~` (deprecated) → skip
4. **Max 5 entries** — ถ้าตรงมากกว่า 5 → เลือก 5 ที่ keyword match สูงสุด; tie → เลือกที่ Date ใหม่กว่า
5. **Apply ทันที** — quote entry ที่ตรง + apply fix pattern ก่อน trace จากศูนย์ (ประหยัด 10x)
6. **ถ้าไม่มี entry ตรง** → หมายเหตุ "ไม่มี skill learning ตรง — trace ใหม่" (ห้าม fallback โหลดทั้งไฟล์)
7. **หลังจบงาน** → ถ้า root cause เป็น pattern → append เข้า learnings.md (ดู Quality gates)

---

## Handoff

**ทำเองได้** เมื่อ:
- Bug มี error message ชัด + reproducible
- Root cause อยู่ในไฟล์ที่ระบุได้
- Fix เป็น code-level ไม่ต้อง redesign

**Yield ไป `sa`** เมื่อ:
- Bug บอกว่า requirement กำกวม (ไม่ใช่ implementation bug)
- Fix ต้องการเปลี่ยน data model / API contract / state machine

**Yield ไป `ux`** เมื่อ:
- Bug เป็น visual issue (layout broken, animation jank) ไม่ใช่ logic
- Fix ต้องการปรับ design

**Yield ไป `migrate`** เมื่อ:
- Bug ปรากฏหลายไฟล์เพราะ pattern เดียวกัน → เปลี่ยน scope จาก fix เดียวเป็น bulk migration

**Handoff checklist: debug → sa / ux / fe / migrate (ติ๊กครบก่อน yield — ติ๊กไม่ครบ = diagnose ต่อ)**
- [ ] root cause ระบุได้ที่ file:line + ผ่าน 5 Whys แล้ว (ไม่ใช่ "น่าจะเป็น X")
- [ ] ripple list ระบุแล้ว: ทุกไฟล์ที่มี pattern เดียวกัน (หรือระบุว่า "scan แล้ว 0 ที่อื่น")
- [ ] pre-brief ชัดพอที่ skill ถัดไปเริ่มงานได้ทันที: root cause + ripple files + fix direction
- [ ] ถ้า yield ไป `migrate` → pattern ที่ต้อง transform ระบุชัด (regex + expected output)

---

## ลำดับการคิด (mandatory)

### Step 1 — Read the error literally

อ่าน error message **ตามตัวอักษร** ไม่ตีความเอง:

```
A <SelectItem /> must have a value prop that is not an empty string.
```

หมายความตรงตัว: SelectItem ตัวใดตัวหนึ่งมี `value=""` — ไม่ใช่ "Reka UI bug" / "Vue version ไม่ตรง" / สิ่งอื่น

### Step 2 — Locate the source

ดู stack trace **bottom-up** เพื่อหา **caller จากโค้ดเรา**:

```
at setup (SelectItem.vue:129)             ← Reka UI internal (ข้าม)
at callWithErrorHandling (...)             ← Vue internal (ข้าม)
...
at FormProductBrand.vue:132                ← OUR CODE — เริ่มที่นี่
```

อ่าน FormProductBrand.vue:132 → หา USelect ที่ใกล้ที่สุด → ดู items prop

### Step 3 — Reproduce locally (ถ้าทำได้)

- **Frontend bug:** เปิด dev server, navigate to page, สังเกต console + network
- **API bug:** curl endpoint ด้วย payload ที่ user ส่ง
- **State bug:** ลองสร้าง state ที่ทำให้เกิด

ถ้า reproduce ไม่ได้ — บอก user ตรงๆ + ขอข้อมูลเพิ่ม (steps to reproduce, screenshot, network log)

### Step 4 — Identify root cause (ไม่ใช่ symptom) — falsify-first

**กฎทอง:** ถามตัวเอง "ถ้าฉันแก้แค่นี้ — bug จะไปโผล่ที่อื่นไหม?"

ตัวอย่าง:
- ❌ Symptom fix: ลบ USelectMenu ที่ error ทิ้ง
- ✅ Root cause fix: หา `value: ''` ใน items แล้วเปลี่ยนเป็น `null` / sentinel

ลองคิด **5 Whys**:
- Why error? → SelectItem มี value=""
- Why มี value=""? → items array มี `{ value: '' }`
- Why มี value=""? → เคยเขียนตอน migrate native `<select>` ใน option "ทั้งหมด"
- Why ใช้ ''? → copy pattern จาก native select `<option value="">`
- Why ไม่รู้ว่า Reka UI ห้าม? → ไม่ได้อ่าน Reka UI doc → **memory ไม่บันทึก** → ทำซ้ำ

#### 4a. Generate ranked hypotheses (mandatory — อย่าผูกใจกับ idea แรก)

- เขียน **3–5 hypotheses** ที่อธิบาย symptom ได้ — เรียงตาม likelihood (high → low)
- single-hypothesis thinking = anchoring bias → ตกหลุมง่าย
- ถ้านึก ≥ 3 ไม่ออก = ยังเข้าใจ fail path ไม่พอ → กลับ Step 2

#### 4b. Falsify before test (mandatory — ห้าม run proof ก่อน disproof)

สำหรับ hypothesis #1 ที่ rank สูงสุด ถามตัวเอง **ก่อน** เขียน fix:

- **End-to-end check:** hypothesis นี้อธิบาย symptom ได้ครบ flow ไหม (input → trigger → fail point → observable)?
- **Cleanest disproof:** ทดลองอะไรที่ **ถ้า hypothesis ถูก ผลต้องเป็น X, ถ้าผิด ผลต้องเป็น Y** — สองผลแยกกันชัดเจน?
- **Run disproof first.** ถ้า hypothesis ผ่าน disproof = ของจริง; ถ้า disproof ทะลุ = ทิ้ง hypothesis นี้, ลำดับ #2 ขึ้นมา
- ห้าม run "proof" (ลอง fix เลยดูว่าหาย) — เพราะ fix อาจหาย bug ด้วยเหตุผลอื่นที่ไม่ใช่ hypothesis ของเรา

#### 4c. Breadcrumb ledger (mandatory — running log ของ session นี้)

เก็บ ledger ตลอด session — 1 entry ต่อ 1 experiment:

```
| # | What changed / probed         | What happened              | Rules in / out          |
|---|-------------------------------|----------------------------|-------------------------|
| 1 | flip USelectMenu items[0].value '' → null | error หาย       | rules IN: items[0]='' = root |
| 2 | revert + add console.log on mount         | error fire on mount only | rules OUT: race condition  |
```

**กฎ ledger:**
- ทุก hypothesis ใหม่ → walk ทั้ง ledger ก่อน adopt: hypothesis นี้สอดคล้องกับ **ทุก** entry ก่อนหน้าไหม?
- ถ้า entry เก่าขัด hypothesis ใหม่ → hypothesis ผิดหรือไม่ครบ → refine หรือทิ้ง
- ถ้าค้าง 3+ entries แล้วยังไม่ converge → ออกแบบ **single experiment** ที่ผล pass/fail แยก hypothesis ที่เหลือออกจากกันให้เด็ดขาด แล้ว run อันนั้นก่อนทำต่อ
- update ledger หลังทุก experiment ทันที — ledger คือ memory ของ session, อย่าเชื่อหัวอย่างเดียว

### Step 5 — Fix + verify no regression

1. **แก้ที่ root cause** — ไม่ใช่ workaround
2. **Verify ทันที:**
   - ทำ scenario ที่ trigger error เดิมซ้ำ → error หายไหม
   - ทำ scenario ปกติ → behavior ยังถูกไหม (regression check)
3. **Trace ripple** — bug pattern นี้มีที่อื่นไหม? (ดู Step 6)
4. **Update memory** — เพิ่ม `feedback_<topic>.md` ถ้าเป็น pattern ใหม่

### Step 6 — Trace ripple (เผื่อ bug pattern เดียวกันที่อื่น)

ถ้า root cause เป็น pattern (เช่น "items มี value=''") — **scan ทั้งโปรเจกต์**:

```bash
# scan ทั้ง single + double quote (กัน miss แบบที่เคยเจอ)
grep -rn 'value: ""' app/ --include="*.vue" --include="*.ts"
grep -rn "value: ''" app/ --include="*.vue" --include="*.ts"
```

ถ้าเจอที่อื่น — **fix ทุกจุด** ไม่รอให้ user เจออีก. ถ้า scope ใหญ่ → yield ไป `migrate` skill

---

## Common error patterns (ดูก่อนเริ่ม diagnose)

### Reka UI / Nuxt UI 4

| Error | Root cause | Fix |
|---|---|---|
| `SelectItem must have a value prop that is not an empty string` | items มี `value: ''` หรือ `value: ""` | เปลี่ยนเป็น `null` หรือ sentinel — ดู `feedback_select_item_value_empty_string.md` |
| `Cannot read properties of null (reading 'type')` ใน patchElement | DOM node ถูก unmount ระหว่าง patch (race) | มัก follow up หลัง error อื่น — fix root error ก่อน |

### Vue template

| Error | Root cause | Fix |
|---|---|---|
| `Invalid end tag` | ลบ wrapper element ครึ่งทาง เหลือ `</div>` ค้าง | นับ `<div\b` vs `</div>` แล้วหาจุดเกิน — ดู `feedback_dangling_tag_after_wrapper_removal.md` |
| `Unexpected token` ใน template | syntax error ใน expression | อ่านบรรทัดที่ Vite ชี้ + 5 บรรทัดรอบๆ |

### Vue reactivity

| Error | Root cause | Fix |
|---|---|---|
| `computed` ไม่ update | source ไม่ reactive (destructure `reactive` ตรงๆ) | ใช้ `toRefs()` หรือ `storeToRefs()` |
| `watch` ไม่ fire | source เป็น primitive ที่ไม่ reactive หรือ getter ผิด | ใช้ getter form: `watch(() => obj.foo, ...)` |
| Infinite loop ใน watch | watch แล้ว mutate source | ใช้ `flush: 'post'` หรือ refactor logic |

### Auth / Multi-tab

| Symptom | Root cause | Fix |
|---|---|---|
| Reload loop | `location.reload()` หลัง redirect | ลบ reload — `navigateTo()` พอ |
| Tab desync | localStorage write โดยไม่มี cross-tab strategy | Pinia plugin persistedstate + `multitab` option (ถ้ารองรับ) หรือ BroadcastChannel |

### Network / API

| Symptom | Root cause | Fix |
|---|---|---|
| 401 cascade | Layout `getProfile()` ไม่มี token guard → fail → reload → ลูป | ใส่ guard `if (!token) return` ก่อน API call |
| CORS error | server ไม่ allow origin | ตรวจ backend config |
| Empty response | API ส่ง 204 No Content แต่ frontend คาด JSON | check status ก่อน parse |

---

## Anti-patterns (ห้ามทำ)

### ❌ Symptom fix แทน root cause
**ตัวอย่าง:** เห็น error ที่ component A → ลบ component A ทิ้ง
**แก้:** หา why จริงๆ ก่อนแก้

### ❌ ใส่ try-catch เพื่อกลบ error
**ตัวอย่าง:** `try { ... } catch {}` เพื่อให้ error log เงียบ
**แก้:** Error เกิดเพราะมีสาเหตุ — กลบ = bug ฝังลึก

### ❌ บอก "อาจจะเป็น..." โดยไม่ verify
**ตัวอย่าง:** "อาจเป็นเพราะ network slow"
**แก้:** ดู Network tab + reproduce + ระบุชัด

### ❌ แก้ 1 จุดแล้วไม่ scan ที่อื่น
**ตัวอย่าง:** แก้ `value: ""` ที่ไฟล์ A — ลืม scan ไฟล์ B
**แก้:** Step 6 — trace ripple ทั้งโปรเจกต์ก่อนปิด ticket

---

## Quality gates ก่อนปิดงาน (mandatory)

- [ ] **Mantra recited** — verbatim ใน response แรก (หรือ user สั่งข้าม)
- [ ] **Memory scanned** — quote feedback memory ที่ตรงกับ error pattern
- [ ] **Hypotheses ranked ≥ 3** — ไม่ผูกใจกับ idea แรก
- [ ] **Disproof ran ก่อน proof** — hypothesis ผ่าน falsification, ไม่ใช่ "fix แล้วหาย"
- [ ] **Breadcrumb ledger ครบ** — ทุก experiment มี entry + cross-check แล้ว
- [ ] **Root cause identified** — ผ่าน 5 Whys + ระบุได้ที่ file:line + สอดคล้อง ledger ทุก entry
- [ ] **Reproduced ก่อนแก้** — confirm fix targeted ถูกที่
- [ ] **Verify หลังแก้** — error หาย + ไม่มี regression
- [ ] **Ripple traced** — scan ทั้งโปรเจกต์ pattern เดียวกัน, fix ทุกจุด หรือ yield ไป `migrate`
- [ ] **Project memory updated** — ถ้าเป็น bug pattern เฉพาะ project นี้ → เพิ่ม `feedback_<topic>.md` + ลิงก์ใน `MEMORY.md` พร้อมเหตุผลและวิธีกันเกิดซ้ำ
- [ ] **Skill learnings updated** ที่ `~/.claude/skills/debug/learnings.md` ถ้า symptom → root cause mapping generalize ข้าม project ได้ (framework-level bug, misleading error, debug technique) — append entry ตาม format ในไฟล์ (เน้น symptom → root cause + detection)
- [ ] **Build / dev server clean** — `tsc --noEmit` 0 errors + `curl` หน้าที่แตะ HTTP 200 + dev log ไม่มี warn/error ใหม่
- [ ] **ห้ามเคลม "fixed"** ก่อนผ่านทุกข้อ — ถ้า user เจอ error ซ้ำ = root cause ไม่ใช่ของจริง → กลับไป Step 4

---

## Output style

```markdown
### Bug
- **Symptom:** <ที่เห็น>
- **Error message:** <quote ตามตัวอักษร>
- **Where:** file:line จาก stack

### Root cause
- **5 Whys:** Why → Why → Why → ...
- **ที่จริง:** <root cause + ทำไมเกิด>
- **Memory check:** <quote feedback memory ที่ตรง — ถ้ามี>

### Fix
- **What changed:** file:line + diff
- **Why this fixes it:** <connect ไป root cause>

### Ripple check
- **Pattern scan:** <regex + result>
- **Other places affected:** <list หรือ "none">

### Verify
- ✓ Error หายเมื่อทำซ้ำ scenario
- ✓ tsc 0 errors
- ✓ curl /<page> HTTP 200
- ✓ dev log clean

### Memory update
- ✓ เพิ่ม feedback_<topic>.md (หรือ "ไม่จำเป็น เพราะ X")
```
