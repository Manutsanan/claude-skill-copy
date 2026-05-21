# Learnings — {skill-name}

> **Per-skill, cross-project memory** — บทเรียนของ skill ตัวนี้เองที่ใช้ได้ข้ามทุก project
>
> **ต่างจาก project memory ยังไง?**
> | | Project memory (`~/.claude/projects/<id>/memory/`) | Skill learnings (ไฟล์นี้) |
> |---|---|---|
> | Scope | เฉพาะ project นั้น | ข้ามทุก project ที่ใช้ skill นี้ |
> | เนื้อหา | business rule, codebase convention, user preference | technical pitfall, anti-pattern, default ของ skill |
> | ตัวอย่าง | "โปรเจกต์นี้ใช้ partner-scoped routes" | "Vue destructure reactive object → reactivity หาย" |
>
> **เมื่อไหร่ append entry ใหม่:**
> - หลังจบงานทุกครั้งที่ skill นี้ทำ **ถ้า** เจอ:
>   - บทเรียนที่ generalize ได้ — ไม่ใช่ business rule เฉพาะ project (อันนั้น → project memory)
>   - pitfall ที่ skill นี้พลาดบ่อย
>   - default ที่ skill นี้ควรใช้เป็น first choice ครั้งหน้า
> - **อย่า append** business rule, user preference ทั่วไป, หรือสิ่งที่ derive ได้จากโค้ด/git history
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Pre-flight — grep tag/keyword ของงานปัจจุบัน → apply ก่อนเริ่ม
>
> **Pruning:** entry ที่ล้าสมัย (framework เปลี่ยน, API ถูก deprecate) → ลบหรือ mark `~~deprecated~~`

---

## Format ต่อ entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** สิ่งที่กำลังทำตอนเจอบทเรียน — **1 บรรทัดเท่านั้น**
**Lesson:** กฎ + เหตุผลสั้นๆ ว่าทำไม
**How to apply:** ทำยังไงครั้งหน้าเมื่อเจอสถานการณ์คล้ายกัน
```

**Deprecation:** เมื่อ entry ล้าสมัย (API เปลี่ยน, component deprecated, pattern ไม่ work) → เปลี่ยน header เป็น `## ~~slug~~` — Phase 0.5 จะ skip อัตโนมัติ ห้ามลบทิ้งเพราะยังเป็น history

---

## Entries

<!-- ใหม่สุดอยู่บน — append entry ใหม่ที่นี่ -->

<!-- ตัวอย่าง (ลบเมื่อมี entry จริง):

## sample-lesson-slug

**Tags:** example, placeholder
**Date:** 2026-05-16

**Context:** เริ่มใช้ pattern learnings.md
**Lesson:** เก็บบทเรียน cross-project ที่ generalize ได้ ไม่ปนกับ project memory
**How to apply:** ทุกครั้งจบงาน — ถามตัวเองว่า "บทเรียนนี้ใช้กับ project อื่นได้ไหม" ถ้าได้ → ที่นี่; ถ้าไม่ → project memory

-->
