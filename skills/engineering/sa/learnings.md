# Learnings — sa

> **Per-skill, cross-project memory** — บทเรียนของ skill `sa` ที่ใช้ได้ข้ามทุก project (System Analysis + Security Audit)
>
> **เก็บอะไรที่นี่:**
> - Edge case ที่มัก enumerate หลุดบ่อย (concurrent submit, network fail mid-flight, partial success, idempotency)
> - State machine pattern ที่ pop up บ่อย (loading/empty/error/success/partial/unauthorized/max boundary)
> - OWASP / security pattern (IDOR check, auth boundary, secret leakage point, SSRF surface)
> - Question template ที่ดึง requirement ออกจาก user ได้ดี (เช่น "ถ้า X เกิดพร้อม Y ระบบทำยังไง")
> - Diagram pattern ที่สื่อ flow ซับซ้อนได้ตรงประเด็น (sequence vs state vs ER เมื่อไหร่ใช้อะไร)
>
> **ไม่เก็บที่นี่:**
> - Data model เฉพาะ domain (เช่น Booking entity ของโปรเจกต์ใดโปรเจกต์หนึ่ง → project memory)
> - Security finding เฉพาะ codebase (อันนั้นเข้า project memory + fix ใน code)
> - Stakeholder name / business term เฉพาะ project
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Pre-flight ของ skill `sa` (ทั้ง Mode A Analyze และ Mode B Audit)
> **เมื่อไหร่ append:** หลังจบงานถ้าเจอบทเรียน generalize ได้ (ดู format ใน `_template/learnings.md`)

---

## Format ต่อ entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Mode:** analyze | audit | both
**Date:** YYYY-MM-DD

**Context:** สิ่งที่ทำตอนเจอบทเรียน — **1 บรรทัดเท่านั้น**
**Lesson:** กฎ + เหตุผล
**How to apply:** ทำยังไงครั้งหน้า
```

---

## Entries

<!-- ใหม่สุดอยู่บน -->

## enumerate-7-visual-states-checklist

**Tags:** state-machine, ui-state, edge-case, handoff-to-ux
**Mode:** analyze
**Date:** 2026-05-16

**Context:** ส่ง spec ให้ `ux` แล้ว design ขาด empty / unauthorized state — ux ต้อง yield กลับมาขอ spec ต่อ
**Lesson:** ทุก spec ที่มี UI ต้อง enumerate visual state ครบ **7 ตัว** อย่างน้อย ก่อนส่ง ux: `loading`, `empty`, `error`, `success`, `partial`, `unauthorized`, `max-boundary` (เช่น list ถึง limit, input ครบ character limit) — ถ้า skip ตัวใด → ux จะเดาเอง → ตีความผิด → rework
**How to apply:**
- ตอนเขียน state machine ของหน้า/component ใหม่ → ใช้ 7-state checklist เป็น minimum
- บาง state อาจ collapse ได้ (เช่น `unauthorized` = redirect ไม่ต้อง render) — แต่ต้อง **state ออกมา** ว่า collapse ไม่ใช่ ignore
- เขียน `state: <name>` ลงใน Mermaid state diagram ทุกตัว — ห้ามให้ ux ต้องเดา


## concurrent-submit-race-condition

**Tags:** edge-case, race-condition, form, idempotency, concurrent
**Mode:** analyze
**Date:** 2026-05-16

**Context:** spec form submit ที่กดปุ่มเร็วๆ ติดกัน → ส่ง request 2 ครั้ง → DB เกิด duplicate row หรือ payment ถูกชาร์จ 2 ครั้ง
**Lesson:** ทุก mutating action ต้องระบุใน spec:
1. **Optimistic disable** — disable ปุ่ม + lock form หลัง click จนกว่า response กลับ
2. **Idempotency key** — frontend generate UUID ส่งกับ request, backend reject duplicate ที่ key เดิมภายใน window N นาที
3. **Server-side dedupe** — DB constraint หรือ business rule ที่กัน double-write (เช่น `UNIQUE(user_id, order_id, action)`)
ขาดข้อใดข้อหนึ่ง = ช่องโหว่
**How to apply:**
- ทุกครั้งที่ enumerate edge case ของ form/action → ใส่ "concurrent submit" เป็น default check
- ส่งให้ fe พร้อม UUID generation pattern + ส่งให้ backend audit (mode B) ว่ามี dedupe layer
- ตัวอย่าง flow ที่เสี่ยงสูง: payment, OTP request, order create, booking confirm


## idor-test-pattern

**Tags:** owasp, idor, authz, audit, attack-scenario
**Mode:** audit
**Date:** 2026-05-16

**Context:** Audit route `/api/order/[id]` พบว่า authenticate ผ่าน middleware แต่ไม่เช็คว่า user เป็นเจ้าของ order
**Lesson:** Authentication (logged in) ≠ Authorization (owns this resource) — IDOR เกิดทุกครั้งที่ "เช็คว่า logged in แล้ว fetch resource by id จาก URL/body โดยไม่เช็ค ownership"
**How to apply:**
- ทุก route ที่มี `[id]` / `:id` ใน path หรือ `id` ใน body → ต้อง audit ว่า:
  1. มี ownership check ที่ระดับ DB query (`WHERE user_id = currentUser.id`) หรือ
  2. มี role check (`if user.role !== 'admin' && resource.owner !== user.id`)
- Attack scenario report เสมอ: "Attacker login เป็น user A → GET /api/order/<user B's order id> → ดูข้อมูล user B"
- Fix: ห้าม trust `id` จาก URL — scope query ด้วย session/JWT subject เสมอ

