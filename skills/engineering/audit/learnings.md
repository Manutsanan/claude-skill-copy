# Learnings — audit

> **Per-skill, cross-project memory** — บทเรียนของ audit ที่ใช้ได้ข้ามทุก project
>
> **ต่างจาก project memory ยังไง?**
> | | Project memory (`~/.claude/projects/<id>/memory/`) | Skill learnings (ไฟล์นี้) |
> |---|---|---|
> | Scope | เฉพาะ project นั้น | ข้ามทุก project ที่ใช้ audit |
> | เนื้อหา | "finding X user accept แล้วว่าตั้งใจ" | "default heuristic ของ audit / pitfall / false-positive pattern" |
> | ตัวอย่าง | "intentional dead code ใน legacy/ — กำลัง migrate" | "Vue test ที่ assert toBe(true) มัก weak ทุก project" |
>
> **เมื่อไหร่ append entry ใหม่:**
> - หลังจบงาน audit ทุกครั้ง **ถ้า** เจอ:
>   - heuristic ที่ใช้ซ้ำได้ — เช่น "ทุก Nuxt project มัก bloat จาก full lodash"
>   - false-positive pattern — เช่น "vue-tsc ไม่นับ `<script setup>` macros เป็น caller → trace ผิด"
>   - default tool choice ที่ work ดี — เช่น "`pnpm why` ดีกว่า `pnpm ls` สำหรับ duplicate transitive"
>   - signal ที่ flag ดีกว่าวิธีเดิม
> - **อย่า append** business rule / user preference ของ project ใด project หนึ่ง (อันนั้น → project memory)
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Phase 0.5 — grep tag/keyword ของ stack ที่ตรวจเจอใน Phase 1 → apply ก่อนเริ่ม scan
>
> **Pruning:** entry ที่ล้าสมัย (tool ถูก deprecate, framework เปลี่ยน API) → ลบหรือ mark `~~deprecated~~`

---

## Format ต่อ entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** สถานการณ์ที่เจอบทเรียน (1-2 บรรทัด)
**Lesson:** กฎ + เหตุผลสั้น ๆ ว่าทำไม
**How to apply:** ทำยังไงครั้งหน้าเมื่อเจอสถานการณ์คล้ายกัน
**Related:** [[other-learning-slug]] หรือ link ไป project memory ถ้ามี
```

---

## Entries

<!-- ใหม่สุดอยู่บน — append entry ใหม่ที่นี่ -->

<!-- ตัวอย่าง (ลบเมื่อมี entry จริง):

## full-lodash-import-bloat-pattern

**Tags:** performance, bundle, lodash, vue, nuxt
**Date:** 2026-05-18

**Context:** scan Nuxt 4 project แล้วเจอ `import _ from 'lodash'` 30+ ไฟล์ทำให้ initial bundle +71KB
**Lesson:** เกือบทุก Vue/Nuxt project ที่เคย audit มี pattern นี้ — `lodash` whole import ใช้แค่ 1-2 ฟังก์ชัน
**How to apply:** Phase 2 dimension Performance — เริ่มจาก `rg "import \w+ from ['\"]lodash['\"]"` (ไม่ใช่ `lodash-es`) เป็นอันดับแรก
**Related:** project memory ของ project ที่ user accept ไว้ว่า "ตั้งใจ"

-->
