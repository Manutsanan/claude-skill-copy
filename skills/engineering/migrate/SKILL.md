---
name: migrate
description: Use for bulk transformations / migrations across many files — converting legacy patterns to new patterns (e.g. native <select> → USelect, inline schemas → shared schemas, class-based components → composition API, deprecated API → new API). Plans the migration in phases, applies in batches, verifies after each batch, recovers from cascading errors. Trigger on Thai keywords migrate/ย้าย/แปลง/refactor ทั้งโปรเจกต์/เปลี่ยน X เป็น Y ทั้งหมด/cleanup ทุกที่ and English keywords migrate/migration/bulk transform/codemod/refactor across files/replace all/convert all. Examples "migrate native select เป็น USelect ทั้งโปรเจกต์", "ย้าย inline schema ไป shared/", "เปลี่ยน v-model:open เป็น defineModel ทุกที่", "refactor service layer ทั้งหมด", "ลบ deprecated API call ทุกจุด". DO NOT use for single-file edits (use `fe` instead) or schema design (use `sa` first).
---

# migrate — Bulk transformation orchestrator

> Skill นี้ออกแบบมาสำหรับงานที่ **แตะหลายไฟล์ตาม pattern ซ้ำๆ** — ตัวอย่างที่เคยเจอในโปรเจกต์ frontend:
> - 22 inline valibot schemas → `shared/schemas/`
> - 80+ native `<input>` → `<UInput>` (partners pages)
> - 34 native `<select>` → `<USelect>` (ทั้งโปรเจกต์)
>
> **คนจริงทำผิดเพราะ "ใจร้อนแก้ทีละจุด"** — skill นี้บังคับวางแผน + verify ก่อนเดินทุกขั้น

---

## Phase 0 — Load memory hierarchy (mandatory — extend Universal Phase 0)

ลำดับ:

1. **Load global memory** — `~/.claude/memory/MEMORY.md`
   - filter: `metadata.skill: migrate` หรือ `skill: cross`
   - filter ต่อด้วย **target pattern** (เช่น "USelect", "valibot schema", "PageHeader")
   - ถ้าไม่มีไฟล์ → ข้าม + หมายเหตุ "ไม่มี global memory"

2. **Load project memory** — `~/.claude/projects/<project-id>/memory/MEMORY.md`
   - project id = working directory แปลง `/` → `-`
   - filter เดียวกับ global memory
   - ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory — fresh migrate"

3. **Echo top 3-5 entries** กลับให้ user เห็นก่อนเริ่ม plan:
   ```
   📚 Memory ที่ relevant กับ migration นี้:
   - [project] feedback_grep_multiline_attrs — Vue template ต้องใช้ <tag loose แล้ว verify
   - [project] feedback_wave_migration_pattern — 6-step wave migration workflow
   ```

4. **Conflict check** — ถ้าจะ migrate ขัด pattern เดิมที่ memory บอก → หยุดถาม user ก่อน + override → update memory

5. **หลังจบงาน** — save lesson ตาม **8 universal save triggers** ใน `~/.claude/CLAUDE.md` Universal Phase 0 #4 — โดยเฉพาะ "pattern ที่ scan/verify เจอใหม่"

### Memory ที่ `migrate` ต้องเช็คทุกครั้ง (ถ้ามีใน project)

- `feedback_grep_multiline_attrs.md` — Vue template multi-line attrs
- `feedback_verify_before_claiming_done.md` — ก่อนเคลม "ครบ"
- `feedback_dangling_tag_after_wrapper_removal.md` — wrapper migration
- `feedback_select_item_value_empty_string.md` — Reka UI migration
- `feedback_wave_migration_pattern.md` — wave-based 6-step workflow
- `feedback_thorough_cleanup.md` — 4-axes cleanup rule

### Pre-flight อื่นๆ (ทำคู่กับ Phase 0)

1. **อ่าน CLAUDE.md ของโปรเจกต์** — convention, stack, pattern เดิม
2. **Map scope ก่อนแก้** — ห้ามเริ่มแก้ก่อนรู้ว่ามีกี่ไฟล์ กี่ pattern
3. **อ่านโค้ดตัวอย่าง 2-3 จุด** — confirm ว่า pattern ที่จะ migrate มีรูปแบบเดียวกันจริง อย่าเหมา

> ดู `~/.claude/CLAUDE.md` Universal Phase 0 สำหรับ load/save logic เต็ม + skill tag convention

---

## Phase 0.5 — Load skill learnings (mandatory)

ลำดับ:

1. **Extract task keywords** — ดึง keyword จาก migration target: component (`USelect`, `UButton`), pattern (`inline-schema`, `wrapper-element`, `v-model`), technique (`wave`, `batch`, `regex`, `ast`)
2. **อ่าน** `~/.claude/skills/migrate/learnings.md` — scan เฉพาะ **Tags:** field ของแต่ละ entry
3. **Load เฉพาะ entry ที่ตรง** — entry ผ่านถ้า Tags มี ≥1 keyword ตรง **และ header ไม่มี `~~`**; ถ้าไม่มี tag ตรงหรือ header มี `~~` (deprecated) → skip
4. **Max 5 entries** — ถ้าตรงมากกว่า 5 → เลือก 5 ที่ keyword match สูงสุด; tie → เลือกที่ Date ใหม่กว่า
5. **Quote** entry ที่ใช้ใน reasoning — เช่น "ตาม learnings#vue-multiline-attr-regex จะใช้ pattern X"
6. **ถ้าไม่มี entry ตรง** → หมายเหตุ "ไม่มี skill learning ตรง — Discover phase ต้องละเอียดเป็นพิเศษ" (ห้าม fallback โหลดทั้งไฟล์)
7. **หลังจบงาน** → ถ้าเจอ regex/technique ที่ใช้ซ้ำได้ → append เข้า learnings.md (ดู Quality gates)

---

## Handoff

**รับจาก** `sa` (ถ้ามี):
- target pattern + reason ที่ต้อง migrate
- security/correctness constraint (เช่น "ห้ามเปลี่ยน behavior")
- ripple list — ไฟล์ที่ depend กับ pattern เก่า

**ส่งให้** `fe` (ถ้า migration ต้องการการตัดสินใจระดับโค้ดเฉพาะจุด):
- file:line ของจุดที่ migrate ไม่ได้แบบ mechanical (มี edge case)
- เหตุผล + suggestion

**ทำเองได้** (ไม่ yield) เมื่อ:
- pattern เป็น mechanical replacement (regex-able)
- ไม่กระทบ logic / behavior
- batch verify ผ่านทุก batch

**Yield กลับ `sa`** เมื่อเจอ:
- pattern ที่กระทบ data model / API contract
- migration ที่ต้องการ migration script ของข้อมูลเก่า

---

## ลำดับการคิด (mandatory — ห้าม skip ขั้นใด)

### Phase 0 — Discover & Scope

1. **Scan ด้วย ≥ 2 patterns** (หลวม + เข้ม) — ผลต้องตรงกัน
2. List ไฟล์ทั้งหมดที่ match พร้อม count per file
3. **จำแนกประเภท** — pattern เดียวกันหรือหลายแบบ? mechanical หรือ context-dependent?
4. **Map dependencies** — ไฟล์ไหนอ้างไฟล์ไหน, ลำดับการแก้ต้องเป็นยังไง

### Phase 1 — Plan

1. **เสนอแผนเป็น phase** ให้ user เห็นก่อนเริ่ม:
   - Phase A: low-risk / dead code (ลองวิธีบน scope เล็ก)
   - Phase B: active production
   - Phase C: edge cases / context-dependent
2. **ระบุ verify step** ของแต่ละ phase
3. **ขอ confirm** ถ้า scope > 10 ไฟล์ หรือกระทบ shared code

### Phase 2 — Execute by batch

ทำทีละ batch ไม่ใช่ทีละไฟล์ (เร็วกว่า + verify เป็นชุด):

1. **Migrate 3-5 ไฟล์** ใน batch แรก
2. **Verify ทันทีหลัง batch:**
   - `tsc --noEmit` (ถ้าเป็น TS)
   - `curl http://localhost:3000/<page>` ของหน้าที่แตะ (HTTP 200)
   - ดู dev log ไม่มี error
3. ถ้า error → หยุด, fix, แล้วค่อย batch ต่อ
4. ถ้า OK → batch ถัดไป

### Phase 3 — Cross-verify final

1. **Re-scan** ด้วย pattern เดิม (ทั้งหลวม + เข้ม) — ผลต้อง = 0
2. **Manual spot-check 2-3 ไฟล์** ที่ migrate แล้ว — confirm ผลถูก
3. **รัน build full** — `nuxt build` หรือ `tsc --noEmit` ทั้งโปรเจกต์
4. **บันทึก memory** — pattern ที่เจอ + วิธี migrate + gotcha

---

## Tools / techniques

### Bulk regex replace (สำหรับ pattern ง่าย)

ใช้ Bash + sed/perl/node script เมื่อ:
- pattern เหมือนกันทุกจุด (variable name เปลี่ยน, structure เหมือน)
- Edit ทีละไฟล์จะใช้ tool calls > 30 ครั้ง

```bash
# ตัวอย่าง: native input → UInput (multi-line)
node -e '
import { readFileSync, writeFileSync } from "node:fs"
const src = readFileSync(file, "utf8")
const out = src.replace(
  /<input type="text" v-model="([^"]+)" class="normal-input"[^/]*\/>/g,
  (_, model) => `<UInput v-model="${model}" variant="card" class="w-full" />`
)
writeFileSync(file, out)
'
```

**กฎ:** ทุก script ต้อง:
- print "files modified" + "matches replaced" ออกมา
- run บน 1 ไฟล์ก่อน verify ผล แล้วค่อย batch
- backup ผ่าน git (commit หรือ stash) ก่อนรัน

### Edit tool (สำหรับ context-dependent)

ใช้เมื่อ:
- แต่ละจุดมี surrounding context ต่างกัน (ต้องการ visual confirm)
- แก้ไม่กี่จุด (< 10) — ไม่คุ้มเขียน script

### Explore agent (สำหรับ scope ใหญ่)

ใช้ตอน discover ว่ามี pattern กี่จุด ในไฟล์ไหนบ้าง — เร็วกว่ารัน grep ทีละครั้ง

---

## Anti-patterns (ห้ามทำ — เคยพังมาแล้ว)

### ❌ ใจร้อน edit ทีละจุดโดยไม่ scan ก่อน
**ผลลัพธ์:** ตกหล่น 22 จุด user ต้องท้วง 3 รอบ
**แก้:** Phase 0 Discover ก่อน Phase 1 Plan ก่อน Phase 2 Execute เสมอ

### ❌ ใช้ regex pattern เดียวเช็คผล
**ผลลัพธ์:** `<select[ >]` miss native select ที่ตามด้วย newline
**แก้:** Cross-verify หลวม + เข้ม ผลต้องตรง (ดู `feedback_grep_multiline_attrs.md`)

### ❌ ลบ wrapper element ครึ่งทาง
**ผลลัพธ์:** เหลือ `</div>` ค้าง → Vite "Invalid end tag"
**แก้:** Edit ที่รวม wrapper open + close + content เป็น `old_string` เดียว (ดู `feedback_dangling_tag_after_wrapper_removal.md`)

### ❌ migrate ไป Reka UI item โดยใส่ value=""
**ผลลัพธ์:** runtime error "SelectItem must have a value prop that is not an empty string"
**แก้:** scan **ทั้ง single + double quote** ก่อน — เปลี่ยน `value: ""` / `value: ''` เป็น `value: null` หรือ sentinel (ดู `feedback_select_item_value_empty_string.md`)

### ❌ เคลม "0 left" จาก scan รอบเดียว
**ผลลัพธ์:** user ต้องสั่ง "ชัวไหม" ทุกครั้ง
**แก้:** quality gates ต่อไปนี้ก่อนเคลม

---

## Quality gates (mandatory ก่อนปิดงาน)

- [ ] **Memory scanned** — quote feedback memory ที่ใช้ + อัปเดต memory ใหม่ถ้าเจอ pattern/gotcha ใหม่
- [ ] **Discover ครบทั้ง project** — ใช้ ≥ 2 regex patterns, ผลตรงกัน
- [ ] **Per-batch verify ผ่าน** — `tsc --noEmit` 0 errors + Vite compile success ทุก batch
- [ ] **Final re-scan** — pattern เดิม = 0 ทั่วทั้งโปรเจกต์ (ตรวจหลวม + เข้ม)
- [ ] **Manual spot-check 2-3 ไฟล์** — อ่านไฟล์จริง confirm
- [ ] **Build success** — full `nuxt build` หรือเทียบเท่า ผ่าน
- [ ] **Dev server run-time clean** — `curl` หน้าที่แตะ + ดู dev log ไม่มี error/warn ใหม่
- [ ] **ห้ามเคลม "เสร็จ / ครบ / 0 left"** ก่อนผ่านทุกข้อ — ถ้า user ต้องสั่ง "ตรวจอีก" = scan แรกไม่ดีพอ → memo + แก้
- [ ] **Update skill learnings** ที่ `~/.claude/skills/migrate/learnings.md` ถ้าเจอ regex/AST pattern, batch size, recovery technique ที่ generalize ข้าม project ได้ — append entry ตาม format ในไฟล์

---

## Output style

ระหว่างทำงาน รายงานเป็น phases ชัดเจน:

```markdown
### Phase 0 — Discover
- Scope: 34 จุด ใน 13 ไฟล์
- Pattern types: 2 แบบ (filter / form field)

### Phase 1 — Plan
- Batch A (dead code, 7 ไฟล์)
- Batch B (active production, 6 ไฟล์)

### Phase 2 — Execute Batch A
- ✓ Migrated 3 ไฟล์
- ✓ tsc passes
- ✓ curl /xxx HTTP 200
- → Batch B

### Phase 3 — Final verify
- ✓ Re-scan: 0 left (loose + strict patterns match)
- ✓ Build success
- ✓ Memory updated: feedback_<topic>.md
```
