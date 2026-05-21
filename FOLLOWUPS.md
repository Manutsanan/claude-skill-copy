# Follow-ups

Open items ที่ commit แล้วแต่ยังไม่ verify ผลในการใช้งานจริง — review ตามวันที่กำกับ

---

## 1. Measure mantra / hypothesis ledger (debug skill)

**Added:** 2026-05-21 (commit ที่เพิ่ม mantra recital + 4a ranked hypotheses + 4b falsify-first + 4c breadcrumb ledger ใน `skills/engineering/debug/SKILL.md`)

**Why review:** กฎเหล่านี้ import มาจาก 9arm-skills (`debug-mantra`) ไม่ใช่ graduate จากการเจ็บของโปรเจกต์เอง — ถ้าไม่ catch bug ที่เคยพลาด = ceremony เปล่ากิน token

**Review target: 2026-06-04** (2 สัปดาห์)

**ถามตัวเองวันนั้น:**
- 2 สัปดาห์ที่ผ่านมา debug skill ถูกเรียกกี่ครั้ง?
- กรณีไหน ranked hypotheses ≥ 3 ทำให้ avoid anchoring จริง?
- กรณีไหน disproof-first ทำให้พบว่า hypothesis ที่ดูดี = ผิด?
- กรณีไหน breadcrumb ledger ทำให้ converge เร็วกว่าปกติ?
- ถ้านึกไม่ออก ≥ 1 กรณี → **rollback** กฎเหล่านี้ (revert commit) อย่าเก็บเพราะ "ดูดี"
- ถ้านึกออก ≥ 1 กรณี → graduate เป็น learnings entry + เก็บกฎไว้

**Rollback คำสั่ง:**
```bash
cd ~/Project/claude-skill-copy
git revert <commit-sha-ของ-mantra/ledger>
# หรือ partial rollback: Edit ตัด section Mantra + 4a/4b/4c ออก แล้ว commit ใหม่
```

---

## 2. Measure simpler-way gate (sa skill Mode A)

**Added:** 2026-05-21 (Step 0 — Intent + simpler-way gate ใน `skills/engineering/sa/SKILL.md`)

**Why review:** บังคับให้ ratio "do nothing / existing / smaller / different layer" ทุกครั้งก่อน spec — ถ้าผู้ใช้รำคาญหรือ skip ทุกข้อ = noise

**Review target: 2026-06-04**

**ถามตัวเองวันนั้น:**
- sa Mode A ถูกเรียกกี่ครั้ง?
- กรณีไหน 4 ทางเลือกทำให้พบ approach ที่ดีกว่า spec เดิม?
- กรณีไหน user เลือก "do nothing" / "use existing" จริง (ไม่ใช่ผ่าน rationale แบบ formal)?
- ถ้าทุกครั้งเลือก spec เดิมเหมือนกัน 0 ครั้งใช้ทางเลือกอื่น → ceremony ตัด

**Rollback คำสั่ง:**
- partial: Edit ตัด Step 0 ออกจาก `sa/SKILL.md` Mode A
- หรือเลื่อนเป็น "optional gate" ไม่บังคับ

---

## 3. Quarterly memory distillation

**กำหนดทำ:** ทุก 3 เดือน (next: **2026-08-21**)

**Why:** 8 save triggers + ไม่มี auto-prune → memory จะกลายเป็น graveyard. Entry ที่จริงเมื่อ 6 เดือนก่อนอาจไม่จริงแล้ว แต่ยังถูก echo ทุก turn → quality degrade เงียบ

**ขั้นตอน:**
1. `/distill-memory` (ถ้ามี skill นี้ available) — หรือ manual review
2. เปิด `~/.claude/memory/MEMORY.md` + project memory ที่ active
3. ทุก entry ถาม: "ยังจริงไหมตอนนี้? code ที่อ้างยังมีไหม?"
4. Entry ที่ไม่ตรง → ลบ หรือ update
5. Entry ที่ซ้ำ ≥ 2 projects → promote ขึ้น global (ถ้ายังไม่ขึ้น)
6. Entry ที่ซ้ำ ≥ 3 projects + skill เดียวกัน → promote ขึ้น skill learnings
7. Commit + push (ถ้า memory อยู่ใน repo)

**Calendar reminder:** ตั้งเองใน calendar app หรือ `/schedule` ถ้าใช้ได้

---

## Maintenance log

ใส่ entry ทุกครั้งที่ review หรือทำ follow-up เสร็จ:

```
[YYYY-MM-DD] <action> — <outcome>
```

- 2026-05-21 — Initial setup: bucket repo + Phase 2 symlink + slim SKILL.md 36% + add this file
