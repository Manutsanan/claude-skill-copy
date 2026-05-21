# Learnings — ux

> **Per-skill, cross-project memory** — บทเรียนของ skill `ux` ที่ใช้ได้ข้ามทุก project (Visual/Interaction Design)
>
> **เก็บอะไรที่นี่:**
> - Tailwind CSS pitfall (เช่น class string literal vs template literal สำหรับ JIT scan)
> - Nuxt UI v4 component composition pattern (UCard + UForm + UFormField, UModal animation override)
> - Accessibility checklist ที่มัก miss (focus ring, ARIA label, color contrast ratio)
> - Animation timing/easing default ที่ดูดี (duration, ease curve, stagger)
> - Responsive breakpoint pattern (mobile-first, container query เมื่อไหร่ใช้)
> - Color/spacing token system ที่ scale ได้ (semantic naming vs literal)
> - State visual default (loading skeleton vs spinner เมื่อไหร่ใช้อะไร)
>
> **ไม่เก็บที่นี่:**
> - Brand color / typography เฉพาะ project (อันนั้น → project memory)
> - Layout structure เฉพาะ page ของ project
> - Mockup-to-code mapping เฉพาะหน้า
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Pre-flight ของ skill `ux` (ทั้ง 3 mode)
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

## figma-thumbnail-unclear-must-search-or-ask

**Tags:** figma, design-reading, thumbnail, node-id, assumption
**Date:** 2026-05-20

**Context:** implement stat cards ของ dashboard จาก top-level Figma node thumbnail ที่เล็กและ low-res — อ่าน layout ผิดทั้ง 3 จุด (แต่ละ stat ควรเป็น card แยก, icon+% อยู่คนละฝั่ง, มี bottom color bar) เพราะเดาจากภาพที่ไม่ชัด
**Lesson:** Figma top-level node thumbnail มักมีความละเอียดต่ำ — อ่าน layout ของ component ย่อยได้ไม่ถูกต้อง ต้องค้นหา node ID ที่แสดง component นั้นโดยตรงหรือถาม user ก่อนเสมอ ห้าม implement โดยเดา
**How to apply:**
- เมื่อได้รับ Figma node ที่เป็น top-level page → thumbnail ได้ภาพรวม แต่รายละเอียด component ย่อยไม่ชัด
- ก่อน implement component ใดๆ → ลอง view node ID ใกล้เคียง (เช่น +1, +2, ...) หรือ node ที่ชื่อ/เนื้อหาตรงกับ component นั้น
- ถ้าหา node ที่ชัดไม่ได้ → ถาม user ขอ node ID สำหรับ component นั้นโดยตรง
- ห้ามสรุปว่า "น่าจะประมาณนี้" แล้ว implement — ถ้าไม่แน่ใจ = ต้องถาม

## nuxt-layout-system-must-verify-before-claiming-done

**Tags:** nuxt, layout, app-vue, NuxtLayout, design-verify
**Date:** 2026-05-19

**Context:** implement หน้า login พร้อม layout file แต่ลืมตรวจว่า `app.vue` มี `<NuxtLayout>` ไหม — ผลคือ layout ไม่ถูก apply, card ไม่อยู่กลาง, bg gradient ไม่แสดง ต้องให้ user แจ้งเองว่า design ยังไม่ตรง
**Lesson:** การที่ layout file มีอยู่ + `definePageMeta({ layout: 'x' })` ครบ ยังไม่พอ — `app.vue` ต้องมี `<NuxtLayout>` ครอบ `<NuxtPage>` ด้วย ถ้าไม่มีก็เหมือนไม่มี layout เลย (ไม่มี error, ไม่มี warning — fail เงียบๆ)
**How to apply:**
- ทุกครั้งที่สร้าง layout ใหม่หรือ implement page ที่ใช้ layout → **ตรวจ `app.vue` ก่อนเสมอ**
- checklist ก่อนเคลม design/layout เสร็จ:
  1. `app.vue` มี `<NuxtLayout><NuxtPage /></NuxtLayout>` ไหม?
  2. `layouts/<name>.vue` มีอยู่จริงไหม?
  3. `definePageMeta({ layout: '<name>' })` ใน page ตรงกับชื่อ file ไหม?
  4. **เปิด browser ดูจริง** — `nuxt prepare` ผ่านไม่ได้แปลว่า visual ถูกต้อง
- อย่าเชื่อแค่ type check หรือ dev server ไม่ error — layout fail เงียบๆ ได้เสมอ


## tailwind-class-must-be-string-literal

**Tags:** tailwind, jit, class-name, dynamic-class
**Date:** 2026-05-16

**Context:** เขียน design plan แบบ `class="bg-${color}-500"` หรือประกอบ class จาก variable → Tailwind ไม่ generate CSS → UI ไม่ render สี
**Lesson:** Tailwind JIT scan **string literal** ในไฟล์ source — ไม่ evaluate template literal / string concat runtime ถ้า class ถูกประกอบจาก variable → JIT มองไม่เห็น → ไม่มี CSS rule ออกมา
**How to apply:**
- ส่ง class plan ให้ `fe` เป็น string literal เต็มเท่านั้น — ห้าม template literal
  ```vue
  <!-- ❌ :class="`bg-${color}-500`" -->
  <!-- ✅ :class="color === 'red' ? 'bg-red-500' : 'bg-blue-500'" -->
  ```
- ถ้า design ต้อง dynamic จริงๆ → ใช้ map object ที่มี literal ครบทุกตัวเลือก:
  ```ts
  const colorClass = { red: 'bg-red-500', blue: 'bg-blue-500' }[color]
  ```
- ทางเลือก: ใช้ inline `style` แทน เมื่อค่ามาจาก runtime จริง (`:style="{ background: color }"`)


## animation-no-pulse-on-stable-ui

**Tags:** animation, ux-principle, kiosk, attention
**Date:** 2026-05-16

**Context:** ใส่ `animate-pulse` บนปุ่มหลักของหน้า kiosk เพื่อ "ดึงความสนใจ" — ผู้ใช้รายงานว่าน่ารำคาญ + รู้สึกว่าเว็บ "ค้าง"
**Lesson:** Pulse / heartbeat animation บน UI element ที่ stable (ไม่ใช่ loading state) สื่อความหมายผิด — ผู้ใช้ associate กับ "กำลังโหลด / กำลัง process" ไม่ใช่ "กดได้"
**How to apply:**
- `animate-pulse`, `animate-ping`, `animate-bounce` → ใช้เฉพาะ **transient state** (loading skeleton, notification badge ใหม่)
- ดึงความสนใจปุ่ม CTA → ใช้ **static contrast** (สีเด่น, ขนาดใหญ่, position prominent) + **subtle hover animation** (scale 1.02, shadow elevate) แทน
- Kiosk / display screen ที่ user ไม่ interact ตรงๆ → ห้ามมี looping animation ใดๆ เพราะรบกวนสายตา


## responsive-mobile-first-default

**Tags:** responsive, mobile-first, tailwind, breakpoint
**Date:** 2026-05-16

**Context:** เขียน class `lg:grid-cols-3 grid-cols-1` เริ่ม design จาก desktop → พอย่อจอ mobile → layout เพี้ยน เพราะ default styling ไม่ถูก optimize ให้เล็ก
**Lesson:** Tailwind คือ mobile-first — `md:`, `lg:`, `xl:` คือ override สำหรับ **จอใหญ่ขึ้น** ไม่ใช่จอเล็กลง ดังนั้น default class (ไม่มี prefix) คือ "mobile size" — ต้อง design mobile ก่อน
**How to apply:**
- ลำดับการเขียน class: mobile default → tablet (`md:`) → desktop (`lg:`) → wide (`xl:`)
  ```vue
  <!-- ✅ mobile-first -->
  <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3 xl:gap-6">
  ```
- Design plan ต้อง spec mobile layout เป็น default — ไม่ใช่ "desktop แล้วค่อย hide บาง element บน mobile"
- Test ลำดับ: 375px → 768px → 1024px → 1440px (ตรงกับ iPhone SE, iPad, laptop, desktop)
- Touch target ≥ 44×44px ทุก interactive element บน mobile

