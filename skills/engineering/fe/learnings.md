# Learnings — fe

> **Per-skill, cross-project memory** — บทเรียนของ skill `fe` ที่ใช้ได้ข้ามทุก project Vue/Nuxt/React/TypeScript
>
> **เก็บอะไรที่นี่:**
> - Vue 3 / Nuxt (v3 + v4) reactivity pitfall (ตัวอย่าง: destructure reactive object, watch on ref vs reactive, computed ที่ side-effect)
> - TypeScript pattern (generics, type narrowing, infer)
> - valibot schema convention (เช่น `InferInput` vs `InferOutput` ตอนไหนใช้ไหน)
> - Nuxt UI component quirk (UButton color/variant, UModal slot, USelect items shape) — ระบุ version ใน entry ถ้า quirk เฉพาะ version
> - Pinia / composable convention ที่ใช้ซ้ำได้ทุก project
> - Anti-pattern ที่เคยเขียนแล้วต้อง refactor (เช่น prop drilling deep, useState ผิดที่)
>
> **ไม่เก็บที่นี่:**
> - Convention เฉพาะ project (เช่น "โปรเจกต์นี้ใช้ shared/schemas/" → project memory)
> - Path / file structure เฉพาะ codebase
> - Business term ของ project นั้นๆ
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Pre-flight ของ skill `fe`
> **เมื่อไหร่ append:** หลังจบงานถ้าเจอบทเรียน generalize ได้ (ดู format ใน `_template/learnings.md`)

---

## Format ต่อ entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Date:** YYYY-MM-DD

**Context:** สิ่งที่ทำตอนเจอบทเรียน — **1 บรรทัดเท่านั้น**
**Lesson:** กฎ + เหตุผล
**How to apply:** ทำยังไงครั้งหน้า
```

---

## Entries

<!-- ใหม่สุดอยู่บน -->

## select-item-value-must-not-be-empty-string

**Tags:** nuxt-ui, reka-ui, USelect, USelectMenu, runtime-error
**Date:** 2026-05-16

**Context:** ใช้ `USelect` / `USelectMenu` แล้ว throw `SelectItem must have a value prop that is not an empty string` ตอน mount
**Lesson:** Reka UI (เบื้องหลังของ Nuxt UI v3+ select component) ห้าม `value: ''` ใน `items` array เพราะ empty string สงวนไว้สำหรับ "no selection" ภายใน Radix/Reka — ถ้าใส่ `''` runtime จะ throw ทันที
**How to apply:**
- ห้ามใช้ `''` เป็น placeholder option — ใช้ `null`, `undefined`, หรือ omit ไปเลยแทน
- ถ้าต้องการ "ทุกค่า / all" → ใช้ string sentinel ที่ไม่ใช่ `''` เช่น `'__ALL__'`
- ตอน migrate native `<select>` ที่มี `<option value="">` → map เป็น `null` ก่อนใส่ items
- Scan ทั้ง single + double quote: `rg "value: ['\"]['\"]"` ก่อนคิดว่า safe

## slot-existence-not-reactive-in-template-vif

**Tags:** vue3, slot, reactivity, template
**Date:** 2026-05-16

**Context:** ใช้ `<template v-if="$slots.actions">...</template>` เพื่อ render section เฉพาะเมื่อมี slot — แต่ section หาย/โผล่ผิดเวลาในบาง render
**Lesson:** Vue 3 `$slots.<name>` ไม่ reliably reactive ใน `<template v-if>` — มันคือ object reference ที่ Vue ไม่ track เป็น dep ของ effect ปกติ ทำให้ re-evaluate ไม่ทันเมื่อ parent re-render
**How to apply:**
- อย่าใช้ `v-if="$slots.X"` เพื่อ branch UI สำคัญ
- ถ้าต้องเช็ค slot existence — ใช้ `computed(() => !!slots.X)` ใน `<script setup>` แล้ว reference computed นั้นใน template
- หรือ design ให้ parent ส่ง prop `:showActions="boolean"` ชัด ๆ แทนเช็ค slot


## destructure-reactive-loses-reactivity

**Tags:** vue3, reactive, ref, composable, reactivity
**Date:** 2026-05-16

**Context:** เขียน composable ที่ return `reactive({ count, items })` แล้ว consumer `const { count } = useFoo()` — UI ไม่ update ตอน count เปลี่ยน
**Lesson:** Destructure ตัวออกจาก `reactive()` ทำให้ได้ "primitive snapshot" — สาย reactive ขาดทันที (Vue track proxy ของ object ไม่ใช่ value ที่ destructure ออกมา)
**How to apply:**
- Composable return `reactive({...})` → consumer ต้อง destructure ผ่าน `toRefs()` หรือ `toRef()`
  ```ts
  // ❌ const { count } = useFoo()
  // ✅ const { count } = toRefs(useFoo())
  // ✅ const count = toRef(useFoo(), 'count')
  ```
- Best practice: composable return `refs` ตรงๆ ตั้งแต่ต้น — `return { count: ref(0), items: ref([]) }` แทน `reactive({...})` — consumer destructure ได้ตรง ๆ ไม่ต้อง toRefs
- React equivalent pitfall: ส่ง `{...state}` เข้า useState — primitive snapshot คนละแบบ แต่ปัญหา conceptual คล้ายกัน

