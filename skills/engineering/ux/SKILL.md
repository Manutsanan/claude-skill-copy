---
name: ux
description: ALWAYS use for ANY task involving website/app design, UI changes, or visual appearance — designing new components, building/editing pages, styling, layout, colors, spacing, animations, responsive breakpoints, accessibility, mockup-to-code, redesigns, polish work, or any request to "make it look better/nicer/modern". Trigger on Thai keywords ออกแบบ/ดีไซน์/ปรับหน้าตา/ปรับ UI/แต่ง UI/ทำให้สวย/ทำให้ดูดี/ทันสมัย/responsive/หน้าจอ/หน้าเว็บ/component/ปุ่ม/สี/layout/animation/ลูกเล่น and English keywords design/redesign/restyle/UI/UX/style/styling/layout/look/appearance/visual/component/page/screen/responsive/mobile/tablet/desktop/animation/transition/polish/modern/aesthetic/Tailwind/CSS. Use proactively WITHOUT being asked whenever editing .vue/.tsx/.jsx/.html/.css files for visual changes, or when user mentions wanting things to look different/better/modern/responsive. Examples: "ปรับ UI ให้สวย", "ทำหน้านี้ใหม่", "redesign this page", "review accessibility", "implement this mockup", "improve UX", "เพิ่ม animation", "ทำให้ responsive", "ปรับสี", "จัด layout".
---

# ux — Visual / Interaction Design

3 modes (เลือกตาม intent):

1. **Design จาก spec/mockup** — user ส่ง mockup / รูป / description
2. **Review UI** — user ขอตรวจ / วิเคราะห์ / หา issue
3. **Improve UX** — user ขอปรับให้ดีขึ้น ไม่ระบุปัญหาเจาะจง

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (ดู `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: ux | cross` + keyword (component, page, theme, animation, responsive, a11y)
- **Learnings filter:** `~/.claude/skills/ux/learnings.md` by Tags (max 5)
- **Conflict check:** ห้าม redesign สิ่งที่ memory บอก "convention คือ X" — ต้องถาม user ก่อน
- **Pre-flight:** อ่าน CLAUDE.md ของ project (design system, theme config) + existing components + theme config (`app.config.ts` variant ที่ตั้งใจ)

---

## Handoff (ux เป็นขั้นกลางของ pipeline `sa → ux → fe`)

**รับจาก `sa`** (ถ้ามี): user story + state machine + data constraint + acceptance criteria
- ออกแบบ visual ครอบคลุมทุก state (loading/empty/error/success/partial/unauthorized/max-boundary)
- ระหว่าง design เจอช่องว่าง spec ที่ตอบเองไม่ได้ → **yield กลับ `sa`** อย่าเดา

**ส่งให้ `fe`** เมื่อ design เสร็จ:
- component map — ใช้ Nuxt UI component ตัวไหน
- Tailwind class plan — string literal จริง (กัน JIT scan ไม่เจอ)
- visual state map — state ↔ data state
- animation spec — property / duration / easing / trigger
- responsive plan — class set ของแต่ละ breakpoint
- interaction spec — hover / focus / active / disabled / loading

**Checklist ux → fe (ติ๊กครบก่อนส่ง):**
- [ ] component map ครบ
- [ ] Tailwind class เป็น string literal (ไม่มีค่าจาก variable)
- [ ] visual state map ครบทุก state ของ sa
- [ ] responsive plan ทุก breakpoint (sm/md/lg/xl)
- [ ] interaction spec ครบ (hover/focus/active/disabled/loading)
- [ ] animation spec หรือระบุชัด "ไม่มี animation"

**รับจาก `fe` กลับ** เมื่อ design ไม่ feasible → ปรับแล้วส่งใหม่

---

## Mode 1: Design จาก mockup

1. **อ่าน mockup ทุกรายละเอียด** — สี ฟอนต์ ขนาด spacing radius shadow gradient อย่าเดา
2. **หา component / utility ที่ reuse ได้** ในโปรเจกต์ก่อนเขียนใหม่
3. **Semantic HTML ก่อน styling** — `<button>` ไม่ใช่ `<div onClick>`; `<nav>`, `<img alt>`
4. **ใช้ design system ก่อน custom CSS** — Nuxt UI / shadcn / MUI
5. **Map สีตรงๆ** อย่าแปลงเป็น token ใกล้เคียงโดยพลการ
6. **Outer → inner** — layout ใหญ่ก่อน, component, detail

**Post-write checklist:** match mockup ทุก element / icon-only button มี aria-label / disabled ชัด / hover-active-focus ครบ / responsive breakpoint หลักดูได้

---

## Mode 2: Review UI

อ่านโค้ดจริงก่อน comment เสมอ

**Accessibility:** icon-only มี `aria-label` / img มี `alt` (alt="" ถ้า decorative) / input มี `<label for>` / contrast ≥ 4.5:1 / focus ring มองเห็น / modal มี focus trap + Esc ปิด / `lang="th"` ที่ html

**Responsive:** test 375/768/1280px / tap target ≥ 44×44 / body font ≥ 14px / input ≥ 16px (iOS no-zoom) / ไม่มี horizontal scroll / overflow ใช้ `truncate` / `line-clamp`

**Hierarchy:** heading ลำดับชั้นตาม importance / spacing scale คงที่ (4/8/12/16/24) / alignment สอดคล้องในกลุ่ม

**States:** loading = skeleton/spinner / empty = ข้อความ + คำแนะนำ / error = ข้อความเข้าใจได้ + ลองใหม่ / success = feedback ทันที

รายงาน: list issue + **severity** (blocker / major / minor) + file:line

---

## Mode 3: Improve UX

หา friction points:
1. **คลิก/แตะมากเกิน** — task ใช้กี่ step? ลดได้ไหม
2. **affordance ไม่ชัด** — สี/shadow/cursor บอกว่ากดได้ไหม
3. **ระบบทำอะไรอยู่ไม่ชัด** — loading/progress/toast หลัง action
4. **อ่านลำดับยาก** — visual hierarchy ดึงสายตาไปสิ่งสำคัญที่สุดก่อน
5. **ไม่สม่ำเสมอ** — ปุ่ม/spacing แบบเดียวกันต่างกันไหม
6. **edge case หลุด** — text ยาวล้น / empty / network ช้า

เสนอเป็น **patch เล็กๆ ทีละจุด** อย่ารื้อใหญ่โดยไม่จำเป็น

---

## Universal principles

- **Mobile-first ในใจ** — เขียน base mobile, enhance ด้วย breakpoint ขึ้น
- **Spacing scale คงที่** — 4/8/12/16/24/32 ไม่ใช่ค่าสุ่ม
- **Touch target ≥ 44×44px** บน mobile
- **Contrast ≥ 4.5:1** body text
- **อย่าใช้ color เป็น signal เดียว** — เพิ่ม icon/label เผื่อตาบอดสี
- **Animation ≤ 300ms** UI feedback; 0ms ถ้า `prefers-reduced-motion`
- **z-index ชัดเจน** — modal > dropdown > tooltip > sticky > content

---

## Modern aesthetic

**ดูทันสมัย สะอาด มีรสนิยม** — ไม่ flat เฉยๆ และไม่ skeuomorphic

- **Spacing โปร่ง** — 16/24/32 มากกว่า 8/12 ให้ content หายใจ
- **Border radius สม่ำเสมอ** — เลือก scale เดียว (`rounded-lg` 8px / `rounded-xl` 12 / `rounded-2xl` 16) ห้ามผสม
- **Shadow soft & layered** — `shadow-sm` / `shadow-md` ไม่ใช่ดำจัด; depth ผ่าน blur
- **Typography hierarchy ผ่านน้ำหนัก** — `font-semibold`/`font-bold` + scale 14/16/20/24/32; `leading-relaxed` body
- **Color palette จำกัด** — primary 1 + neutral + accent 1 (success/warning/danger คนละตัว); ≤ 5 family ต่อจอ
- **Gradient & glass แต่พอดี** — gradient เฉพาะ hero/CTA; `backdrop-blur` เฉพาะ overlay/header
- **Border บาง** — `border` 1px, สีโทน neutral (`border-slate-200` / `border-white/10`)
- **Dark mode** — semantic token (`bg-background` `text-foreground`) ไม่ hardcode

**Polish:**
- Hover: bg เปลี่ยน + shadow lift + scale 1.01–1.02 (ไม่เกิน)
- Focus: `ring-2 ring-primary/50 ring-offset-2`
- Skeleton loading แทน spinner เปล่า
- Empty state: illustration/icon ใหญ่ + เชิญชวน + CTA

---

## Animation

**หลัก:** เสริม UX ไม่ใช่ขโมย attention — ถ้า user สังเกตว่ามี = เด่นเกิน

**When to animate:** state change (modal/accordion/tab/toast), feedback (button press, hover), continuity (FLIP, reorder), loading (skeleton, progress), attention (pulse badge — ใช้น้อย)

**อย่า animate:** scrolling content, page load ทุกครั้ง, decorative bg loop, text ทุกบรรทัด fade-in

**Timing:**
- micro (hover, press): **100–150ms**
- small (tooltip, dropdown): **150–200ms**
- medium (modal, drawer): **200–300ms**
- large (hero): **300–500ms** ไม่ค่อยใช้

**Easing:**
- `ease-out` enter (เร็วต้น ช้าปลาย — รู้สึก responsive)
- `ease-in` exit (ช้าต้น เร็วปลาย — หายเร็ว)
- `ease-in-out` loop
- หลีกเลี่ยง `linear` ยกเว้น progress
- playful: `cubic-bezier(0.34, 1.56, 0.64, 1)` (overshoot)

**Properties (GPU-cheap):** `transform` (translate/scale/rotate), `opacity`, `filter` (ระวังหนัก)
**หลีกเลี่ยง:** animate `width`/`height`/`top`/`left`/`margin` — กระตุก → ใช้ `transform`

**Patterns:**
- Fade + slide: modal/drawer (`opacity 0→1` + `translateY 8px→0`)
- Scale + fade: dropdown/popover (`scale 0.95→1` + `opacity 0→1`, transform-origin ที่ trigger)
- Stagger list: child เข้าทีละ 30–50ms (≤ 5 ตัว)
- Spring physics: drag/swipe — Motion / Framer Motion / Vue equivalent
- View Transitions API: page/route transition (native, modern)

**Tools Vue/Nuxt:** `<Transition>`, `<TransitionGroup>`, `@vueuse/motion`, CSS `@keyframes`, Tailwind `transition-*` + `duration-*` + `ease-*`

**Accessibility:** เคารพ `prefers-reduced-motion` — ทุก non-essential animation ต้อง wrap ด้วย media query / JS check; ห้าม autoplay ที่ดึง attention; loop ต้อง pause ได้

**Animation checklist:** ≤ 300ms / `transform` + `opacity` เป็นหลัก / enter `ease-out`, exit `ease-in` / เคารพ reduced-motion / ไม่มี loop กิน CPU/GPU idle / ลื่น 60fps mobile

---

## Responsive (บังคับทุกหน้า ทุก component)

**หลัก:** ทุก design รองรับทุกขนาด — mobile-first เสมอ

**Breakpoints (Tailwind):** `< 640px` mobile / `sm:` 640 / `md:` 768 / `lg:` 1024 / `xl:` 1280 / `2xl:` 1536

**กฎประจำ:**
- **Layout:** `flex` / `grid` + `flex-wrap` / `grid-cols-1 md:grid-cols-2 lg:grid-cols-3` — อย่า hardcode px
- **Width:** `w-full` + `max-w-*` แทน `w-[480px]`
- **Padding/gap responsive:** `p-4 md:p-6 lg:p-8`, `gap-3 md:gap-4 lg:gap-6`
- **Font responsive:** `text-base md:text-lg`, heading `text-2xl md:text-3xl lg:text-4xl`
- **Hidden/show:** `hidden md:block` (desktop nav), `md:hidden` (mobile drawer trigger)
- **Image:** `w-full h-auto object-cover` หรือ `aspect-video` / `aspect-square`
- **Container:** `mx-auto max-w-7xl px-4 sm:px-6 lg:px-8` (หรือ pattern โปรเจกต์)
- **Touch target ≥ 44×44px** mobile / **Input ≥ 16px** mobile (no iOS auto-zoom)

**Patterns เจอบ่อย:**
- Nav: desktop horizontal → mobile hamburger + drawer
- Table: desktop full → mobile card list หรือ horizontal scroll
- Sidebar: desktop fixed → mobile drawer / bottom sheet
- Form 2-col: `grid-cols-1 md:grid-cols-2 gap-4`
- Modal: desktop center → mobile full-screen / bottom sheet
- Card grid: `grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4`
- Hero: desktop side-by-side → mobile stack

**Edge cases ต้องเช็ค:**
- Text ยาวมาก — `truncate` / `line-clamp-2` / `break-words`
- จอแคบ (< 360px) — ปุ่มหลายตัว wrap/stack
- จอกว้าง (> 1920px) — `max-w-*` จำกัด
- Landscape mobile — modal/sheet scroll ภายใน
- Zoom 200% — layout ไม่พังกู้ไม่ได้
- Sticky header + virtual keyboard — input อาจถูกบัง

---

## Quality gates (ก่อนปิดงาน ทุก mode)

- [ ] **Memory scanned** — quote `feedback_*` UI/design ที่ relevant
- [ ] **Convention check** — ตรงกับ design system / theme config ไม่สร้าง parallel pattern
- [ ] **Vite compile** (ถ้าแก้ template) — `curl /<page>` HTTP 200 + dev log ไม่มี `Invalid end tag`
- [ ] **Reka UI item value** (USelect/USelectMenu) — items ไม่มี `value: ""` / `value: ''` (scan ทั้ง single + double quote)
- [ ] **DevTools responsive test** ที่ **375 / 390 / 768 / 1024 / 1440px**
- [ ] ไม่มี horizontal scroll ที่ไม่ตั้งใจ
- [ ] tap target ≥ 44×44 mobile
- [ ] text ไม่ล้น/ทับ ทุก breakpoint
- [ ] image ไม่บิด/ล้น
- [ ] nav ใช้งานได้ทั้ง mobile (hamburger) + desktop
- [ ] modal/drawer ใช้งานได้ mobile (ไม่เกินจอ, scroll ใน)
- [ ] form กรอกได้ครบ mobile (input ไม่ถูก keyboard บัง)
- [ ] **Skill learnings updated** ถ้าเจอบทเรียน generalize ข้าม project (Tailwind JIT, Nuxt UI v4 quirk, animation timing, a11y recurring)
- [ ] ห้ามประกาศ "เสร็จ / สวยแล้ว" ก่อนผ่าน checklist — user สั่ง "แปลกๆ" = scan แรกไม่ดีพอ

---

## Kiosk / display projects

หน้าจอ kiosk fix ขนาด **แต่โค้ดยังต้อง responsive** — test laptop, เปลี่ยนรุ่นจอ, demo บน iPad

Lock resolution → `transform: scale()` กับ container fixed — ไม่ hardcode px ทุกที่

---

## เมื่อไหร่ "ไม่ต้อง" ปรับ

- Pattern เดิม + สม่ำเสมอ → อย่าเปลี่ยนเพราะ "ฉันมีรสนิยมต่าง"
- Mockup ระบุชัด → ทำตาม mockup
- UX ดีอยู่แล้ว user ไม่ขอปรับ → อย่า over-engineer

ตัดสินใจตรงข้ามกับ mockup/ของเดิม → แจ้ง user + เหตุผล ให้ user เลือก
