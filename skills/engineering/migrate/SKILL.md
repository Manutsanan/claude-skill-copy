---
name: migrate
description: Use for bulk transformations / migrations across many files — converting legacy patterns to new patterns (e.g. native <select> → USelect, inline schemas → shared schemas, class-based components → composition API, deprecated API → new API). Plans the migration in phases, applies in batches, verifies after each batch, recovers from cascading errors. Trigger on Thai keywords migrate/ย้าย/แปลง/refactor ทั้งโปรเจกต์/เปลี่ยน X เป็น Y ทั้งหมด/cleanup ทุกที่ and English keywords migrate/migration/bulk transform/codemod/refactor across files/replace all/convert all. Examples "migrate native select เป็น USelect ทั้งโปรเจกต์", "ย้าย inline schema ไป shared/", "เปลี่ยน v-model:open เป็น defineModel ทุกที่", "refactor service layer ทั้งหมด", "ลบ deprecated API call ทุกจุด". DO NOT use for single-file edits (use `fe` instead) or schema design (use `sa` first).
---

# migrate — Bulk transformation orchestrator

ใช้กับงานที่ **แตะหลายไฟล์ตาม pattern ซ้ำๆ** — บังคับ Discover → Plan → Execute → Cross-verify ตามลำดับ ห้าม shortcut

**กฎหลัก:** "ใจร้อนแก้ทีละจุด" คือ root cause ของ migration พลาดเกือบทุกครั้ง

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (ดู `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: migrate | cross` + target pattern keyword (เช่น `USelect`, `valibot`, `wrapper-element`)
- **Learnings filter:** อ่าน `~/.claude/skills/migrate/learnings.md` เฉพาะ entry ที่ Tags match keyword (max 5); ไม่มี match → "fresh — Discover ละเอียดเป็นพิเศษ"
- **Conflict check:** ถ้า migration ขัด memory → หยุดถาม user
- **Save triggers:** ตาม 8 universal triggers — เน้น "pattern + regex + gotcha" ที่ generalize ได้

---

## Handoff

**รับจาก `sa`** (ถ้ามี): target pattern + reason + ripple list

**ส่งให้ `fe`**: file:line ที่ migrate แบบ mechanical ไม่ได้ + edge case + suggestion

**Yield กลับ `sa`** เมื่อ migration กระทบ data model / API contract / ต้องการ data migration script

**ทำเองได้** เมื่อ pattern mechanical + ไม่กระทบ logic + verify ผ่านทุก batch

---

## ลำดับการคิด (ห้าม skip ขั้นใด)

### Phase 0 — Discover & Scope

1. **Scan ด้วย ≥ 2 patterns** (หลวม + เข้ม) — ผลต้องตรงกัน (ไม่ตรง = regex เข้มผิด)
2. List ไฟล์ทั้งหมด + count per file
3. **จำแนกประเภท:** pattern เดียวกันหรือหลายแบบ? mechanical หรือ context-dependent?
4. **Map dependencies:** ไฟล์ไหนอ้างไฟล์ไหน, ลำดับแก้ต้องเป็นยังไง

### Phase 1 — Plan

1. **เสนอแผนเป็น phase ให้ user เห็นก่อนเริ่ม:**
   - Phase A: low-risk / dead code (ลองวิธีบน scope เล็ก)
   - Phase B: active production
   - Phase C: edge cases / context-dependent
2. ระบุ **verify step** ของแต่ละ phase
3. **ขอ confirm** ถ้า scope > 10 ไฟล์ หรือกระทบ shared code

### Phase 2 — Execute by batch

ทีละ batch (ไม่ใช่ทีละไฟล์ ไม่ใช่ทั้งหมดรวด):

1. Migrate **3–5 ไฟล์** ใน batch แรก
2. **Verify ทันทีหลัง batch:**
   - `tsc --noEmit` (ถ้า TS)
   - `curl http://localhost:3000/<page>` HTTP 200
   - dev log ไม่มี error/warn ใหม่
3. Error → หยุด, fix, แล้วค่อย batch ต่อ
4. OK → batch ถัดไป

### Phase 3 — Cross-verify final

1. **Re-scan** ด้วย pattern เดิม (หลวม + เข้ม) — ผลต้อง = 0 ทั้งคู่
2. **Manual spot-check 2–3 ไฟล์** — อ่านจริงยืนยัน
3. **Build full** — `nuxt build` / `tsc --noEmit` ทั้งโปรเจกต์ pass
4. **Update memory** — pattern + regex + gotcha ที่เจอ

---

## Tools / techniques

**Bulk regex replace** (Bash + node script) — ใช้เมื่อ pattern เหมือนทุกจุด + จะต้อง Edit > 30 ครั้ง

กฎ: ทุก script ต้อง (1) print "files modified" + "matches replaced", (2) run 1 ไฟล์ก่อน verify, (3) git commit/stash ก่อนรัน

**Edit tool** — เมื่อ context-dependent หรือ < 10 จุด

**Explore agent** — discover phase ที่ scope ใหญ่ (เร็วกว่า grep ทีละครั้ง)

---

## Anti-patterns (เคยพังมาแล้ว)

- ❌ **Edit ทีละจุดโดยไม่ scan ก่อน** → ตกหล่นเสมอ; บังคับ Discover ก่อน Plan ก่อน Execute
- ❌ **Regex pattern เดียวเช็คผล** → `<tag[ >]` miss multi-line attrs; cross-verify หลวม + เข้มเสมอ
- ❌ **ลบ wrapper element ครึ่งทาง** → เหลือ `</div>` ค้าง = "Invalid end tag"; Edit ที่รวม open + close + content เป็น `old_string` เดียว
- ❌ **Migrate Reka UI item ด้วย `value=""` / `value: ''`** → runtime error; scan ทั้ง single + double quote, เปลี่ยนเป็น `null` / sentinel
- ❌ **เคลม "0 left" จาก scan รอบเดียว** → quality gates ทุกข้อก่อนเคลม

---

## Quality gates (ก่อนปิดงาน)

- [ ] **Memory scanned + updated** ถ้าเจอ pattern/gotcha ใหม่
- [ ] **Discover ครบ** — ≥ 2 regex patterns ผลตรงกัน
- [ ] **Per-batch verify ผ่าน** — `tsc --noEmit` + Vite compile + dev log clean ทุก batch
- [ ] **Final re-scan = 0** (หลวม + เข้ม)
- [ ] **Manual spot-check 2–3 ไฟล์**
- [ ] **Build full success**
- [ ] **Skill learnings updated** ถ้า regex/AST/batch-size/recovery technique generalize ได้ → append `learnings.md`
- [ ] **ห้ามเคลม "เสร็จ / ครบ / 0 left"** จาก scan รอบเดียว — user ต้องสั่ง "ตรวจอีก" = scan แรกไม่ดีพอ

---

## Output style

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
