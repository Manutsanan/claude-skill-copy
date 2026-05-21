---
name: ux
description: ALWAYS use for ANY task involving website/app design, UI changes, or visual appearance — designing new components, building/editing pages, styling, layout, colors, spacing, animations, responsive breakpoints, accessibility, mockup-to-code, redesigns, polish work, or any request to "make it look better/nicer/modern". Trigger on Thai keywords ออกแบบ/ดีไซน์/ปรับหน้าตา/ปรับ UI/แต่ง UI/ทำให้สวย/ทำให้ดูดี/ทันสมัย/responsive/หน้าจอ/หน้าเว็บ/component/ปุ่ม/สี/layout/animation/ลูกเล่น and English keywords design/redesign/restyle/UI/UX/style/styling/layout/look/appearance/visual/component/page/screen/responsive/mobile/tablet/desktop/animation/transition/polish/modern/aesthetic/Tailwind/CSS. Use proactively WITHOUT being asked whenever editing .vue/.tsx/.jsx/.html/.css files for visual changes, or when user mentions wanting things to look different/better/modern/responsive. Examples: "ปรับ UI ให้สวย", "ทำหน้านี้ใหม่", "redesign this page", "review accessibility", "implement this mockup", "improve UX", "เพิ่ม animation", "ทำให้ responsive", "ปรับสี", "จัด layout".
---

# UX

ครอบคลุม 3 mode — เลือกใช้ตาม intent ของผู้ใช้:

1. **Design จาก spec/mockup** → ผู้ใช้ส่ง mockup, รูป, หรือ description
2. **Review UI ที่มีอยู่** → ผู้ใช้ขอตรวจ / วิเคราะห์ / หา issue
3. **Improve UX** → ผู้ใช้ขอปรับให้ดีขึ้น โดยไม่ได้ระบุปัญหาเจาะจง

## Phase 0 — Load memory hierarchy (mandatory — extend Universal Phase 0)

ลำดับ:

1. **Load global memory** — `~/.claude/memory/MEMORY.md`
   - filter: `metadata.skill: ux` หรือ `skill: cross`
   - filter ต่อด้วย keyword: component, page, theme, animation, responsive, a11y
   - ถ้าไม่มีไฟล์ → ข้าม + หมายเหตุ "ไม่มี global memory"

2. **Load project memory** — `~/.claude/projects/<project-id>/memory/MEMORY.md`
   - project id = working directory แปลง `/` → `-` (เช่น `/Users/X/Project/Y` → `-Users-X-Project-Y`)
   - filter เดียวกับ global memory
   - ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory — fresh start"

3. **Echo top 3-5 entries** กลับให้ user เห็นก่อนเริ่ม design:
   ```
   📚 Memory ที่ relevant กับงานนี้ (ux):
   - [global] feedback-modern-aesthetic — spacing scale 4/8/16, ห้ามใช้ค่าสุ่ม
   - [project] project_design_system — modern card pattern + Tailwind keyframes
   - [project] feedback_modern_page_header — ใช้ <PageHeader> shared component
   ```

4. **Conflict check** — ห้าม redesign สิ่งที่ memory บอก "convention คือ X" — อยากเปลี่ยน ต้องถาม user ก่อน + override → update memory ให้สะท้อน

5. **หลังจบงาน** — save lesson ตาม **8 universal save triggers** ใน `~/.claude/CLAUDE.md` Universal Phase 0 #4 (อ้างตารางว่า save ไป global หรือ project)

### Memory ที่ `ux` ต้องเช็คทุกครั้ง (ถ้ามีใน project)

- `project_design_system.md` — design tokens, animation timing, card pattern
- `feedback_modern_page_header.md` — shared `<PageHeader>` standard
- `feedback_section_nav_menu_pattern.md` — TOC sidebar pattern
- `feedback_no_pulse_animations.md` / `feedback_kiosk_hover_style.md` — animation/hover conventions

### Pre-flight อื่นๆ (ทำคู่กับ Phase 0)

1. **อ่าน CLAUDE.md ของโปรเจกต์** — design system, theme config (เช่น `app/app.config.ts` ใน Nuxt UI), spacing scale
2. **อ่าน existing component / page ที่เกี่ยวข้อง** — จับ pattern ที่มีอยู่ (design system, spacing scale, color tokens) อย่าสร้าง pattern ใหม่ขนานกัน
3. **ตรวจ theme config** (เช่น `app.config.ts`) ว่ามี variant ที่ตั้งใจใช้แล้ว — เช่น `variant="card"` ของโปรเจกต์ปัจจุบัน

> ดู `~/.claude/CLAUDE.md` Universal Phase 0 สำหรับ load/save logic เต็ม + skill tag convention

---

## Phase 0.5 — Load skill learnings (mandatory)

ลำดับ:

1. **Extract task keywords** — ดึง keyword จาก request ของ user: component (`UModal`, `USelect`, `UTable`), technique (`animation`, `responsive`, `a11y`, `tailwind-jit`), topic (`hover`, `dark-mode`, `skeleton`, `transition`)
2. **อ่าน** `~/.claude/skills/ux/learnings.md` — scan เฉพาะ **Tags:** field ของแต่ละ entry
3. **Load เฉพาะ entry ที่ตรง** — entry ผ่านถ้า Tags มี ≥1 keyword ตรง **และ header ไม่มี `~~`**; ถ้าไม่มี tag ตรงหรือ header มี `~~` (deprecated) → skip ทั้ง entry
4. **Max 5 entries** — ถ้าตรงมากกว่า 5 → เลือก 5 ที่ keyword match สูงสุด; tie → เลือกที่ Date ใหม่กว่า
5. **Quote** entry ที่ใช้ใน reasoning — เช่น "ตาม learnings#tailwind-class-must-be-literal จะเขียน class เป็น string literal ทั้งหมด"
6. **ถ้าไม่มี entry ตรง** → หมายเหตุ "ไม่มี skill learning ตรง — fresh start" (ห้าม fallback โหลดทั้งไฟล์)
7. **หลังจบงาน** → ถ้าเจอบทเรียน generalize ได้ → append เข้า learnings.md (ดู Quality gates)

## Handoff (ux เป็นขั้นกลางของ pipeline `sa → ux → fe`)

**รับจาก `sa`** (ถ้า sa ทำมาก่อน — ใช้เป็นจุดเริ่ม ไม่เริ่มจากศูนย์):
- user story / use case + state machine — ออกแบบ visual ครอบคลุมทุก state (loading/empty/error/success/partial/unauthorized/max boundary)
- data constraint ที่กระทบ layout (เช่น "code ยาวสุด 5 ตัว" → ออกแบบ slot ให้พอ)
- acceptance criteria — UI ต้องทำให้ test pass ได้

ถ้า sa ไม่ได้ทำมา (งาน design ตรงๆ ไม่มี requirement gap) — เริ่ม design ได้เลย แต่ถ้าระหว่างทำเจอช่องว่าง spec ที่ตอบเองไม่ได้ → **yield กลับไป sa** ก่อน อย่าเดา

**ส่งให้ `fe`** เมื่อเสร็จ design (output ต้องชัดพอที่ fe เอาไป implement ได้โดยไม่ต้องตีความ):
- component map — แต่ละส่วนใช้ Nuxt UI component อะไร (`UButton`, `UCard`, `UModal`, `UForm`, `UFormField`, ...)
- Tailwind class plan — class string literal จริง (กัน JIT scan ไม่เจอ)
- visual state map — visual state ↔ data state (ผูกกับ state machine ของ sa)
- animation spec — property, duration, easing, trigger
- responsive plan — class set ของแต่ละ breakpoint (sm/md/lg/xl)
- interaction spec — hover/focus/active/disabled/loading

**Handoff checklist: ux → fe (ติ๊กครบก่อนส่ง — ติ๊กไม่ครบ = ทำต่อ ห้าม handoff)**
- [ ] component map ครบ: ทุกส่วนของหน้าระบุ Nuxt UI component ที่ใช้
- [ ] Tailwind class plan เป็น string literal จริง ไม่มีค่าที่ประกอบจาก variable
- [ ] visual state map ครบ: ทุก visual state ↔ data state ผูกกัน (ครบตาม state machine ของ sa)
- [ ] responsive plan ระบุ class set ของแต่ละ breakpoint ที่ใช้ (sm/md/lg/xl)
- [ ] interaction spec ครบ: hover / focus / active / disabled / loading state
- [ ] animation: ระบุ spec (property/duration/easing) หรือระบุชัดว่า "ไม่มี animation"

**รับจาก `fe` กลับมา** เมื่อ design ไม่ feasible (component ไม่มีใน Nuxt UI v4 / animation ชน performance / layout ทับซ้อน) — ปรับแล้วส่งใหม่

ดู "Skill orchestration" ใน `~/.claude/CLAUDE.md` สำหรับ pipeline เต็ม

---

## Mode 1: Design จาก spec / mockup

ลำดับการคิด:

1. **อ่าน mockup ทุกรายละเอียด** — สี, ฟอนต์, ขนาด, spacing, border radius, shadow, รัศมีโค้ง, gradient direction. อย่าเดา
2. **หา component / utility ที่ reuse ได้** ในโปรเจกต์ก่อนเขียนใหม่
3. **เลือก semantic HTML ก่อน styling** — `<button>` ไม่ใช่ `<div onClick>`, `<nav>` ไม่ใช่ `<div class="nav">`, `<img alt>` ไม่ใช่ background-image สำหรับ content
4. **ใช้ design system ของโปรเจกต์ก่อน custom CSS** — Nuxt UI, shadcn, MUI ฯลฯ
5. **Map สีตาม mockup ตรงๆ** — อย่าแปลงเป็น token ที่ใกล้เคียงโดยพลการ ถ้า mockup ใช้ `#7a1818` ก็ใช้ตาม
6. **ทำตามลำดับ outer → inner** — layout ใหญ่ก่อน, แล้วค่อยใส่ component, ค่อยใส่ detail

หลังเขียน checklist:

- [ ] match mockup ทุก element หรือยัง? (ตำแหน่ง, ขนาด, สี, ฟอนต์)
- [ ] icon-only button มี `aria-label` หรือ `title`?
- [ ] disabled state ดูชัดเจน (opacity ต่ำ + cursor-not-allowed)?
- [ ] hover/active/focus state มีครบ?
- [ ] responsive ที่ breakpoint หลัก (mobile/tablet/desktop) ดูได้?

---

## Mode 2: Review UI

ตรวจตามหมวดต่อไปนี้ **อ่านโค้ดจริง** ก่อน comment:

### Accessibility

- icon-only button → ต้องมี `aria-label`
- รูป → ต้องมี `alt` (alt="" ถ้า decorative)
- form input → มี `<label>` ผูก `for` หรือ `aria-labelledby`
- color contrast text/bg ≥ 4.5:1 (3:1 สำหรับตัวใหญ่ ≥18px bold หรือ ≥24px regular)
- focus ring มองเห็นได้ (อย่า `outline-none` โดยไม่ใส่อะไรแทน)
- modal / dialog → focus trap, Esc ปิดได้, return focus หลังปิด
- เนื้อหาภาษาไทย → `lang="th"` ที่ html

### Responsive

- ตรวจ breakpoint mobile (375px), tablet (768px), desktop (1280px+)
- ปุ่มใหญ่พอแตะ (≥ 44×44px ที่ mobile)
- font-size ≥ 14px ที่ body, ≥ 16px ถ้าเป็น input (กัน iOS auto-zoom)
- horizontal scroll ไม่ควรมี (ยกเว้น carousel)
- text overflow มี `truncate` / `line-clamp` ชัดเจน

### Hierarchy & spacing

- heading ลำดับชั้นชัด (h1 > h2 > h3 ตาม importance ไม่ใช่แค่ size)
- spacing scale คงที่ (4 / 8 / 12 / 16 / 24 ...) ไม่มั่ว
- alignment สอดคล้องกันในกลุ่มเดียวกัน

### States

- loading: skeleton หรือ spinner — ไม่ใช่จออะไรก็ไม่มี
- empty: มีข้อความ + คำแนะนำว่าทำยังไงต่อ
- error: ข้อความเข้าใจได้ (ไม่ใช่ "Error 500") + ปุ่มลองใหม่
- success: feedback ทันทีหลัง action

รายงานผล: list issue ที่เจอเป็นข้อๆ พร้อม **severity** (blocker / major / minor) และไฟล์:บรรทัด

---

## Mode 3: Improve UX

หา friction points:

1. **คลิก/แตะมากเกิน** — task นี้ใช้กี่ step? ลดได้ไหม
2. **ไม่ชัดว่ากดอะไรได้** — affordance ของปุ่มเด่นพอไหม (สี / shadow / cursor)
3. **ไม่ชัดว่าระบบทำอะไรอยู่** — มี loading indicator / progress / toast หลัง action
4. **อ่านลำดับยาก** — visual hierarchy ดึงสายตาไปสิ่งสำคัญที่สุดก่อนหรือเปล่า
5. **ความไม่สม่ำเสมอ** — ปุ่มแบบเดียวกันมี style ต่างกันไหม spacing ของหัวข้อแบบเดียวกันต่างกันไหม
6. **edge case ที่หลุด** — text ยาวล้นไหม, empty list บอกอะไรไหม, network ช้าเห็น state อะไร

เสนอปรับเป็น **patch เล็กๆ ทีละจุด** อย่ารื้อใหญ่โดยไม่จำเป็น

---

## Universal principles

- **Mobile-first ในใจ** — ออกแบบ mobile ก่อน แล้ว enhance ด้วย breakpoint ขึ้นไป
- **Spacing scale คงที่** — ใช้ 4/8/12/16/24/32... ไม่ใช่ค่าสุ่ม
- **Touch target ≥ 44×44px** สำหรับ tap target บน mobile
- **Contrast ≥ 4.5:1** สำหรับ body text
- **อย่าใช้ color เป็นสัญลักษณ์อย่างเดียว** — เพิ่ม icon / label เผื่อคนตาบอดสี
- **Animation ≤ 300ms** สำหรับ UI feedback (เกินกว่านี้รู้สึกอืด); 0ms ถ้า user ตั้ง `prefers-reduced-motion`
- **ลำดับ z-index ชัดเจน** — modal > dropdown > tooltip > sticky > content
- **อย่าซ่อน scrollbar บน desktop** — กัน user งง

---

## Modern aesthetic

เป้าหมาย: **ดูทันสมัย สะอาด มีรสนิยม** — ไม่ใช่ flat เฉยๆ และไม่ใช่ skeuomorphic หรูหราเกิน

### Visual language

- **Spacing โปร่ง** — ใช้ padding/gap เผื่อมากกว่าที่คิดเล็กน้อย (16/24/32 มากกว่า 8/12) ให้ content หายใจได้
- **Border radius สม่ำเสมอ** — เลือก scale เดียวทั้ง app (เช่น `rounded-lg` 8px / `rounded-xl` 12px / `rounded-2xl` 16px) อย่าผสม
- **Shadow แบบ soft & layered** — ใช้ shadow โทนอ่อน (`shadow-sm` / `shadow-md` ของ Tailwind) ไม่ใช่ดำจัด; depth ผ่าน blur ไม่ใช่ความเข้ม
- **Typography hierarchy ชัดผ่านน้ำหนัก ไม่ใช่ขนาดอย่างเดียว** — `font-semibold` / `font-bold` กับ scale 14/16/20/24/32; line-height โปร่ง (`leading-relaxed` สำหรับ body)
- **Color palette จำกัด** — primary 1 สี + neutral scale + accent 1 สี (success/warning/danger คนละตัว) อย่าใช้สีเกิน 5 family ในจอเดียว
- **Gradient & glass ใช้แต่พอดี** — gradient สำหรับ hero / CTA สำคัญเท่านั้น; `backdrop-blur` กับ semi-transparent bg ดูทันสมัยแต่ใช้เฉพาะ overlay/header
- **Border บางกว่า 1px** ถ้ารองรับ (`border` Tailwind = 1px ok); สีโทน neutral อ่อน (`border-slate-200` / `border-white/10` บน dark)
- **Dark mode support** — ถ้าโปรเจกต์มี ใช้ semantic token (`bg-background` `text-foreground`) ไม่ใช่ hardcode

### Polish

- **Hover state ละเอียด** — เปลี่ยน bg เล็กน้อย + lift shadow + scale 1.01-1.02 (ไม่เกิน)
- **Focus ring สวย** — `ring-2 ring-primary/50 ring-offset-2` แทน outline default
- **Skeleton loading** แทน spinner เปล่าๆ ในจอ list/card — ดูพรีเมียมกว่า
- **Empty state มี illustration หรือ icon ใหญ่** + ข้อความเชิญชวน + CTA

---

## Animation

หลัก: **เสริม UX ไม่ใช่ขโมย attention** — ถ้าผู้ใช้สังเกตว่ามี animation แสดงว่าเด่นเกิน

### When to animate

- **State change** — modal เปิด/ปิด, accordion expand, tab switch, toast เข้า/ออก
- **Feedback** — ปุ่มกดแล้ว (scale ลงนิด), hover (bg/shadow transition), success checkmark
- **Continuity** — element ขยับจากที่หนึ่งไปอีกที่ (FLIP), list reorder
- **Loading** — skeleton shimmer, progress bar, indeterminate spinner
- **Attention (ใช้น้อย)** — pulse บน notification badge, bounce บน CTA สำคัญครั้งเดียว

อย่า animate: scrolling content, page load ทุกครั้ง, decorative bg loop ที่ไม่หยุด, text ทุกบรรทัด fade-in

### Timing & easing

- **Duration**:
  - micro (hover, button press): **100-150ms**
  - small (tooltip, dropdown): **150-200ms**
  - medium (modal, drawer, page transition): **200-300ms**
  - large (full-screen takeover, hero): **300-500ms** (ไม่ค่อยใช้)
- **Easing**:
  - `ease-out` สำหรับ enter (เร็วต้น ช้าปลาย — รู้สึก responsive)
  - `ease-in` สำหรับ exit (ช้าต้น เร็วปลาย — หายไปเร็ว)
  - `ease-in-out` สำหรับ loop / continuous
  - หลีกเลี่ยง `linear` ยกเว้น progress bar / loading
  - custom curve สำหรับ playful: `cubic-bezier(0.34, 1.56, 0.64, 1)` (overshoot นิดๆ)

### Properties ที่ animate ได้ "ฟรี" (GPU)

- `transform` (translate, scale, rotate)
- `opacity`
- `filter` (blur, brightness — ระวังหนัก)

หลีกเลี่ยง animate `width`/`height`/`top`/`left`/`margin` — กระตุก ใช้ `transform` แทน

### Patterns ที่ดูดี

- **Fade + slide** สำหรับ modal/drawer (`opacity 0→1` + `translateY 8px→0`)
- **Scale + fade** สำหรับ dropdown/popover (`scale 0.95→1` + `opacity 0→1`, transform-origin ที่ trigger)
- **Stagger list** — child เข้าทีละ 30-50ms (ไม่เกิน 5 ตัว ไม่งั้นช้า)
- **Spring physics** สำหรับ playful interaction (drag, swipe) — ใช้ Motion / Framer Motion / Vue equivalent
- **View Transitions API** สำหรับ page/route transition (modern, native)

### Tools ใน Vue/Nuxt

- **`<Transition>` / `<TransitionGroup>`** — built-in, พอสำหรับ enter/leave ส่วนใหญ่
- **`@vueuse/motion`** หรือ **Motion for Vue** — สำหรับ spring, gesture, scroll-triggered
- **CSS `@keyframes`** + `animate-*` classes — สำหรับ loop (pulse, shimmer, spin)
- **Tailwind `transition-*` + `duration-*` + `ease-*`** — เพียงพอสำหรับ micro-interaction

### Accessibility

- **เคารพ `prefers-reduced-motion`** เสมอ — wrap ทุก non-essential animation ใน:
  ```css
  @media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
      animation-duration: 0.01ms !important;
      transition-duration: 0.01ms !important;
    }
  }
  ```
  หรือเช็คใน JS: `window.matchMedia('(prefers-reduced-motion: reduce)').matches`
- **อย่า autoplay** animation ที่ดึง attention (flash, shake) บน user ที่ตั้ง reduce
- **Loop animation** ที่ไม่หยุด ต้องสามารถ pause ได้ (เช่น carousel)

### Checklist หลังใส่ animation

- [ ] ทุก animation ≤ 300ms (ยกเว้น hero/onboarding)
- [ ] ใช้ `transform` + `opacity` เป็นหลัก ไม่ใช่ `width`/`height`
- [ ] enter ใช้ `ease-out`, exit ใช้ `ease-in`
- [ ] เคารพ `prefers-reduced-motion`
- [ ] ไม่มี loop animation ที่กิน CPU/GPU ตลอดเวลาในจอที่ idle
- [ ] ทดสอบบน mobile แล้วยังลื่น 60fps

---

## Responsive design (บังคับเสมอ ทุกหน้า ทุก component)

หลัก: **ทุกสิ่งที่ออกแบบต้องรองรับทุกขนาดจอ** — ไม่มี "หน้านี้ใช้แค่ desktop" หรือ "อันนี้เดี๋ยวค่อยทำ mobile". ถ้าไม่ได้ระบุ scope, ตั้งสมมติฐานว่าผู้ใช้จะเปิดบน mobile ก่อน

### Breakpoints มาตรฐาน (Tailwind)

- `< 640px` — mobile (default, no prefix)
- `sm:` ≥ 640px — large mobile / small tablet portrait
- `md:` ≥ 768px — tablet
- `lg:` ≥ 1024px — small desktop / tablet landscape
- `xl:` ≥ 1280px — desktop
- `2xl:` ≥ 1536px — large desktop

ออกแบบ **mobile-first** เสมอ — เขียน base style สำหรับ mobile, แล้ว enhance ขึ้นด้วย `sm:` `md:` `lg:` ฯลฯ ไม่ใช่เขียน desktop ก่อนแล้ว override ลง mobile

### กฎประจำสำหรับทุก component

- **Layout**: ใช้ `flex` / `grid` + `flex-wrap` / `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` — อย่า hardcode width เป็น px
- **Width**: prefer `w-full` + `max-w-*` แทน `w-[480px]` คงที่
- **Padding/gap responsive**: `p-4 md:p-6 lg:p-8`, `gap-3 md:gap-4 lg:gap-6` — spacing ใหญ่ขึ้นตามจอ
- **Font size responsive**: `text-base md:text-lg`, heading `text-2xl md:text-3xl lg:text-4xl`
- **Hidden/show ตามจอ**: `hidden md:block` (desktop nav), `md:hidden` (mobile drawer trigger) — ไม่ใช่เอา component หาย
- **Image/media**: `w-full h-auto object-cover` หรือ `aspect-video` / `aspect-square` — อย่า fixed wxh
- **Container**: `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8` (หรือ pattern ที่โปรเจกต์ใช้อยู่)
- **Touch target ≥ 44×44px** บน mobile (ปุ่มเล็กบน desktop ก็ได้ แต่ mobile ต้องใหญ่)
- **Input font-size ≥ 16px** บน mobile (กัน iOS auto-zoom เวลา focus)

### Pattern ที่เจอบ่อย

- **Nav**: desktop horizontal menu → mobile hamburger + drawer/sheet
- **Table**: desktop full table → mobile card list หรือ horizontal scroll (`overflow-x-auto`)
- **Sidebar**: desktop fixed sidebar → mobile collapsible drawer / bottom sheet
- **Form 2 column**: `grid-cols-1 md:grid-cols-2 gap-4`
- **Modal**: desktop center dialog → mobile full-screen หรือ bottom sheet (slide up)
- **Card grid**: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`
- **Hero**: desktop side-by-side text + image → mobile stack (text บน, image ล่าง หรือกลับกัน)
- **Long text + sidebar**: desktop 2-column → mobile stack, sidebar เลื่อนลงล่างหรือเป็น collapse

### Edge cases ที่ต้องเช็คเสมอ

- **Text ยาวมาก** — `truncate` / `line-clamp-2` / `break-words` กัน layout แตก
- **จำนวน item เยอะ** — list scroll, pagination, virtualize
- **จอแคบมาก (< 360px)** — ปุ่มหลายตัวเรียงกันต้อง wrap หรือ stack ได้
- **จอกว้างมาก (> 1920px)** — content ไม่ยืดเต็มจนอ่านยาก ใช้ `max-w-*` จำกัด
- **Landscape mobile** (height สั้น) — modal/sheet ที่ใหญ่ต้อง scroll ภายในได้
- **Zoom 200%** (accessibility) — layout ไม่ควรพังแบบกู้ไม่ได้
- **Sticky header + virtual keyboard** บน mobile — input ที่อยู่บน sticky อาจถูกบัง

### Quality gates (บังคับก่อนปิดงาน — ทั้ง 3 mode)

- [ ] **Memory scanned** — quote `feedback_*` UI/design memory ที่ relevant ใน proposal
- [ ] **Convention check** — design ตรงกับ design system / theme config (เช่น `app.config.ts`)? ไม่สร้าง pattern parallel
- [ ] **Vite compile** (ถ้าแก้ template) — `curl http://localhost:3000/<page>` HTTP 200 + ดู dev log ไม่มี `Invalid end tag` (ดู `feedback_dangling_tag_after_wrapper_removal.md`)
- [ ] **Reka UI item value check** (ถ้าใช้ USelect/USelectMenu) — items ไม่มี `value: ""` หรือ `value: ''` (ดู `feedback_select_item_value_empty_string.md`) — scan ทั้ง single + double quote
- [ ] เปิด DevTools responsive mode ทดสอบที่ **375px** (iPhone SE), **390px** (iPhone 14), **768px** (iPad), **1024px**, **1440px**
- [ ] ไม่มี horizontal scroll ที่ไม่ตั้งใจ (ยกเว้น carousel/table)
- [ ] ปุ่มทุกตัว tap ได้สบายบน mobile (≥ 44×44)
- [ ] text ไม่ล้น ไม่ทับกัน ทุก breakpoint
- [ ] image ไม่บิด ไม่ล้น (aspect ratio คงที่)
- [ ] nav/menu ใช้งานได้ทั้ง mobile (hamburger) และ desktop (horizontal)
- [ ] modal/drawer ใช้งานได้บน mobile (ไม่เกินจอ, scroll ภายในได้)
- [ ] form กรอกได้ครบบน mobile (ไม่มี input ถูกบัง, keyboard ไม่ปิดปุ่ม submit)
- [ ] **ห้ามประกาศ "เสร็จ / สวยแล้ว"** ก่อนผ่าน checklist — ถ้าผู้ใช้ต้องสั่ง "แปลกๆ / ตรงไหนผิด" = scan แรกไม่ดีพอ → update memory
- [ ] **Update skill learnings** ที่ `~/.claude/skills/ux/learnings.md` ถ้าเจอบทเรียนที่ generalize ข้าม project (Tailwind JIT pitfall, Nuxt UI v4 component quirk, animation timing default, a11y miss ที่ recurring) — append entry ตาม format ในไฟล์

### หมายเหตุสำหรับโปรเจกต์ kiosk / display

หน้าจอ kiosk / display อาจ fix ขนาดจริง — แต่โค้ดยัง **ต้อง responsive** เผื่อ:

- ทดสอบบน laptop/dev machine ที่จอเล็กกว่า
- เปลี่ยนรุ่นจอในอนาคต
- ผู้ใช้ภายใน demo บน iPad

ถ้าต้อง lock ที่ resolution หนึ่ง ใช้ `transform: scale()` กับ container fixed (ดู `app/pages/customer/kiosk.vue` เป็น reference) — ไม่ใช่ hardcode px ทุกที่

---

## เมื่อไหร่ "ไม่ต้อง" ปรับ

- pattern ที่มีอยู่ใช้งานได้ + สม่ำเสมอกับโปรเจกต์ → อย่าเปลี่ยนเพราะ "ฉันมีรสนิยมต่าง"
- mockup ระบุชัด → ทำตาม mockup อย่าเอารสนิยมส่วนตัวมาทับ
- UX ที่ดีพอแล้ว และผู้ใช้ไม่ได้ขอปรับ → อย่า over-engineer

แจ้งผู้ใช้เสมอเมื่อตัดสินใจตรงข้ามกับ mockup / ของเดิม พร้อมเหตุผล — ให้ผู้ใช้เลือก
