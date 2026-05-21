# Learnings — migrate

> **Per-skill, cross-project memory** — บทเรียนของ skill `migrate` ที่ใช้ได้ข้ามทุก project (Bulk transformation)
>
> **เก็บอะไรที่นี่:**
> - Regex / AST pattern ที่ครอบคลุม edge case ของการ migrate ที่เคยทำ (เช่น native `<select>` → `USelect` ต้องดู `value`, `v-model`, `@change`, nested `<option>`)
> - Batch size ที่ optimal สำหรับ verify ได้ทัน (เคยลอง 50 ไฟล์/batch แล้วล้นความตรวจ)
> - Cascading error pattern (เช่น migrate inline schema แล้ว import ไม่ครบ ส่งผลต่อ type ที่อื่น)
> - Verification technique หลัง batch (tsc --noEmit, grep cross-pattern, build check)
> - Rollback strategy เมื่อ migration พัง mid-way
> - Anti-pattern: ใจร้อน migrate ทีละจุดโดยไม่ plan ก่อน — ต้อง discover/scope/plan/execute เสมอ
>
> **ไม่เก็บที่นี่:**
> - List ไฟล์ที่ migrate ใน project นั้น (ข้อมูล one-shot — git log มี)
> - Project-specific path / shared/schemas/ structure (อันนั้น → project memory)
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Pre-flight ของ skill `migrate` — โดยเฉพาะ Phase 0 Discover
> **เมื่อไหร่ append:** หลังจบ migration ถ้าเจอ pattern/technique ที่ใช้ซ้ำได้กับ migration อื่น

---

## Format ต่อ entry

```markdown
## <kebab-case-slug>

**Tags:** transform-type, framework, technique
**Date:** YYYY-MM-DD

**Context:** migrate อะไร → อะไร, scale (กี่ไฟล์)
**Lesson:** pattern/regex/technique ที่ work + edge case ที่เกือบ miss
**How to apply:** ใช้กับ migration ลักษณะไหนได้บ้าง
**Anti-pattern avoided:** สิ่งที่เกือบทำผิด
**Related:** [[other-learning-slug]]
```

---

## Entries

<!-- ใหม่สุดอยู่บน -->

## grep-multiline-attrs-vue-template

**Tags:** regex, vue-template, scan, cross-verify, multi-line
**Date:** 2026-05-16

**Context:** Migrate native `<select>` → `USelect` (34 จุด) — scan ด้วย regex หลวม `<select` ได้ 34; scan ด้วย regex เข้ม `<select[\s>]` ได้ 31 → ผลไม่ตรง 3 ไฟล์
**Lesson:** Vue template attribute สามารถ break บรรทัดได้ — regex ที่บังคับ whitespace/`>` ติดท้ายชื่อ tag (เช่น `<select[\s>]`) จะ **miss** กรณี attribute ขึ้นบรรทัดใหม่ (`<select\n  v-model="x"`) ตรงนั้น regex หลวม `<select` จะจับได้ แต่อาจ false positive (เช่น `<selection>` substring)
**How to apply:**
- **Cross-verify ≥ 2 regex patterns เสมอ** ใน Discover phase:
  - หลวม: `<select` (จับได้ทุกกรณีรวม false positive)
  - เข้ม: `<select(\s|>)` (จับ true positive แม่นกว่า แต่ miss multi-line)
- ผล 2 pattern ตรง = trust scan; ไม่ตรง = manual diff list หาว่าหายไปที่ไหน
- ทำเลย: `diff <(rg -l "<select" --type vue) <(rg -l "<select(\s|>)" --type vue)`
- Best regex สำหรับ Vue tag: `<TagName(?=[\s/>]|$)` — match Tag ก่อน whitespace/self-close/end-of-line (ไม่ match `<TagNameX>`)
**Anti-pattern avoided:** trust regex ตัวเดียวว่า "scan ครบ" — ทุกครั้งที่ migrate ใน Vue template ต้อง dual-regex
**Related:** [[vue-multi-line-attribute-pattern]]

## wave-migration-6-step-workflow

**Tags:** workflow, batch, planning, verify, rollback
**Date:** 2026-05-16

**Context:** Migrate 80+ native `<input>` → `<UInput>` แบบเหมาทีเดียว → tsc พัง 200+ errors cascading → rollback ยาก → ใช้เวลา recover 3 ชม.
**Lesson:** Bulk migration **ทุกตัว**ต้องผ่าน 6 phases — ห้ามข้าม:
1. **Discover** — scan ด้วย dual regex + count + list ไฟล์
2. **Scope** — แบ่ง batch ตาม risk (dead code → low traffic → high traffic → critical)
3. **Plan** — เขียน mechanical rule (search-replace pattern) + manual edge case list
4. **Execute** — batch ละ 5-15 ไฟล์ (ขึ้นกับ complexity) — ห้าม > 20 ไฟล์/batch
5. **Verify per batch** — `tsc --noEmit` + `curl` หน้าที่แตะ + dev log clean **ก่อน** batch ถัดไป
6. **Final re-scan + cleanup** — pattern เดิม = 0 ทั่ว project + ลบ import ที่ไม่ใช้แล้ว
**How to apply:**
- Batch size 5-15 ไฟล์ — ถ้าน้อยกว่าเสียเวลา cycle, ถ้ามากกว่า verify ไม่ทัน
- ลำดับ batch: dead code ก่อน (ทดสอบ pattern โดยไม่กระทบ user) → low-traffic page → critical flow
- ระหว่าง execute → commit per batch ใน git (rollback ง่ายถ้า batch ใดพัง)
- ถ้า verify batch N พัง → **stop ทันที** อย่าทำ batch N+1 — fix หรือ rollback batch N ก่อน
**Anti-pattern avoided:** เหมา migrate ทั้ง project ในรอบเดียว แล้วค่อย verify ท้าย — error cascading จะหา root cause ยาก
**Related:** [[tsc-noemit-per-batch-verify]]

## tsc-noemit-per-batch-verify

**Tags:** typescript, verify, batch, build
**Date:** 2026-05-16

**Context:** Migrate inline valibot schema → shared/schemas/ batch 3 — tsc รอบสุดท้ายขึ้น 47 errors ที่ cascade จาก batch 1
**Lesson:** TypeScript error cascade ผ่าน import chain — ถ้า migrate batch 1 ทำให้ type ของ shared API เปลี่ยน → batch 2 ที่ import จะพัง → batch 3 อีก ตรวจรอบเดียวท้ายงาน = ตอน fix ไม่รู้ว่า error มาจาก batch ไหน
**How to apply:**
- รัน `tsc --noEmit` **หลังทุก batch** ก่อนเริ่ม batch ถัดไป
- ถ้า batch N errors > 0 → ไม่ proceed batch N+1 ห้ามเด็ดขาด
- ถ้า errors มาจาก batch N+something (ที่ยังไม่ migrate) → cascading จาก batch ก่อนหน้า → revisit batch ก่อนหน้า
- Tip: เก็บ baseline error count ก่อนเริ่ม (`tsc --noEmit | wc -l`) — ทุก batch ต้องไม่เพิ่ม
- Build pipeline command: `yarn nuxt prepare && yarn tsc --noEmit` (prepare regen auto-import types ก่อน tsc)
**Anti-pattern avoided:** verify รอบเดียวท้าย migration → ไม่รู้ว่า cascade เกิดจาก batch ไหน
**Related:** [[wave-migration-6-step-workflow]]
