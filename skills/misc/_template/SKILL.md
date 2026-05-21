---
name: _template
description: Template สำหรับสร้าง skill ใหม่ — copy ทั้งไฟล์แล้วแก้ section ตามต้องการ ห้ามแก้ structure เพราะ pipeline orchestration พึ่งโครงสร้างนี้
---

# {skill-name} — {one-line purpose}

> โครงสร้างนี้บังคับใช้กับทุก skill เพื่อ:
> 1. **consistent triggers** — Claude เลือก skill ถูก
> 2. **pre-flight checks** — ใช้ memory ที่บันทึกไว้แล้ว ไม่ทำ bug ซ้ำ
> 3. **handoff contract** — pipeline `sa → ux → fe` ส่งงานต่อไม่ตีความผิด
> 4. **quality gates** — ห้ามปิดงานก่อน verify ครบ

---

## Trigger เรียกเมื่อ

ผู้ใช้พูดถึงคำใดคำหนึ่ง:
- **Thai**: keyword1, keyword2, keyword3
- **English**: keyword1, keyword2, keyword3

หรือกำลังทำ task ที่:
- กรณี A: ...
- กรณี B: ...

**ห้ามเรียก** เมื่อ:
- ไม่ใช่ scope ของ skill นี้ — yield ไป skill อื่น (ดู "Mid-task yield" ใน CLAUDE.md)

---

## Pre-flight (ทำก่อนเริ่มงานทุกครั้ง — mandatory)

1. **อ่าน CLAUDE.md ของโปรเจกต์** (ที่ working directory) — เข้าใจ business domain, convention, stack
2. **Scan project memory** ที่ `~/.claude/projects/<project-id>/memory/MEMORY.md`:
   - หา feedback memory ที่ keyword ตรงกับงานปัจจุบัน
   - quote relevant memory ใน reasoning ก่อนเสนอ implementation
   - ถ้า memory ขัดกับสิ่งที่จะทำ → ถาม user confirm ก่อนแก้
3. **Scan skill learnings** ที่ `~/.claude/skills/<skill-name>/learnings.md` (per-skill, cross-project):
   - ต่างจาก project memory — ไฟล์นี้เก็บบทเรียนของ **ตัว skill เอง** ที่ใช้ได้ข้ามทุก project
   - grep tag/keyword ที่ตรงกับงานปัจจุบัน → apply lesson ก่อนเริ่ม
   - quote entry ที่ใช้ใน reasoning (เช่น "ตาม learnings#vue-destructure-loses-reactivity จะใช้ toRefs")
   - ถ้าไม่มี entry ตรง → หมายเหตุ "ไม่มี learning ตรง — fresh start"
4. **อ่านโค้ดที่เกี่ยวข้อง** — ไม่วิเคราะห์จากสมมติฐาน (ดู "หลักความรอบคอบขั้นสูงสุด" ใน CLAUDE.md)
5. **ระบุ scope** — ถ้า scope ใหญ่เกินคาด → บอก user ก่อนเดินหน้า

---

## Handoff (input/output ของ skill)

**Input** — รับจาก skill ก่อนหน้าใน pipeline:
- จาก `sa` (ถ้า skill นี้คือ ux/fe): spec / state machine / data model
- จาก `ux` (ถ้า skill นี้คือ fe): component map / Tailwind plan / interaction spec

**Output** — ส่งให้ skill ถัดไป:
- ระบุ artifact ที่ขั้นถัดไปต้องการให้ชัด ห้ามคลุมเครือ
- ใช้ structured format (table / yaml-like list) ที่อ่าน-แล้ว-เริ่มได้ทันที

**Mid-task yield** — ถ้าระหว่างทำพบประเด็นนอก scope:
1. หยุดที่จุดนั้น
2. บอก user 1 บรรทัด: "yield ไป skill `<X>` เพราะ <reason>"
3. ทำขั้น yield ให้จบก่อนกลับมา

---

## ลำดับการคิด (เปลี่ยนตาม skill)

1. ขั้นที่ 1 — ...
2. ขั้นที่ 2 — ...
3. ขั้นที่ 3 — ...

---

## Output style

- ใช้ **mermaid** สำหรับ diagram ทุกชนิด
- ใช้ **table** สำหรับข้อมูลเปรียบเทียบ / list ที่ structured
- ใช้ภาษาไทยสำหรับ business term, ภาษาอังกฤษสำหรับ technical term
- ระบุ **file:line** เสมอเมื่ออ้างถึงโค้ด

---

## Quality gates (mandatory ก่อนปิดงาน)

ห้ามรายงาน "เสร็จ / ครบ / 0 left" ก่อนทำทุกข้อ:

- [ ] **Cross-verify ≥ 2 patterns** — เช่น scan ด้วย regex หลวม + เข้ม ผลต้องตรง (ดู `feedback_grep_multiline_attrs.md`)
- [ ] **Manual spot-check 2-3 จุด** — อ่านไฟล์จริง confirm ผล scan
- [ ] **Build/compile verify** (ถ้าแก้โค้ด) — `tsc --noEmit` + Vite compile (ดู `feedback_dangling_tag_after_wrapper_removal.md`)
- [ ] **Trace caller ≥ 1 hop** ก่อนเคลม "dead code" / "ปลอดภัย" (ดู CLAUDE.md "ความรอบคอบขั้นสูงสุด")
- [ ] **Update project memory** ถ้าเจอ pattern ใหม่ที่ควรกันเกิดซ้ำ — เพิ่ม `feedback_<topic>.md` + ลิงก์ใน MEMORY.md
- [ ] **Update skill learnings** ที่ `~/.claude/skills/<skill-name>/learnings.md` ถ้าเจอบทเรียนที่ generalize ข้าม project ได้ — append entry ใหม่ตาม format (ใหม่สุดบน) ห้าม dump สิ่งที่เป็น business rule เฉพาะ project (อันนั้นไป project memory)

ถ้า user ต้องสั่ง "ชัวไหม / ตรวจซ้ำ" = scan แรกไม่ละเอียดพอ → memo + ปรับวิธีทันที

---

## ห้ามทำ (anti-patterns)

- **อย่าทำงานนอก scope** — yield ไป skill อื่นแทน
- **อย่าประกาศ "เสร็จ" จาก scan รอบเดียว** — ต้องผ่าน quality gates
- **อย่าใช้คำคลุมเครือ** — "อาจมี / ควรพิจารณา" → ระบุ "อะไร ที่ไหน ผลกระทบยังไง"
- **อย่า touch โค้ดเดิม** ก่อน trace caller chain — กัน "fix หนึ่งจุด → bug อีกจุด"

---

## วิธี clone template

```bash
cp -r ~/.claude/skills/_template ~/.claude/skills/<new-skill-name>
# แล้วแก้:
# 1. SKILL.md frontmatter (name + description with triggers)
# 2. SKILL.md body — ใส่เนื้อหาเฉพาะของ skill
```
