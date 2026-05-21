---
name: fe
description: Use when working on frontend code (Nuxt/Vue/React/TypeScript) — writing components, composables, Nuxt pages/layouts/middleware/server routes, state management, reactivity, type-safety, valibot validation, Nuxt UI components; or reviewing existing frontend code for anti-patterns, reactivity bugs, mutation issues, prop drilling, dead code, unclean naming. Trigger on tasks involving component implementation, composable design, state stores (Pinia/Zustand/useState), `ref`/`reactive`/`computed`/`watch`, props/emits, TypeScript generics, valibot schemas, Nuxt UI (UButton, UModal, UForm, ...), route guards, SSR/hydration, performance. Examples: "เขียน composable นี้ให้หน่อย", "review โค้ด component นี้", "state จัดการยังไงดี", "refactor ให้คลีน", "เขียน schema validate", "ทำไม reactivity ไม่ทำงาน", "หา anti-pattern".
---

# fe — Frontend code helper

2 modes (เลือกตาม intent):
1. **Build / refactor** — เขียนหรือปรับ component / composable / store
2. **Review / audit** — ตรวจหา anti-pattern, bug, dead code, ของซ้ำซ้อน

**ขอบเขต:** logic / type / state / reactivity / performance — ส่วน styling/layout/a11y ใช้ skill `ux`

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (ดู `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: fe | cross` + keyword (component, library, error pattern, framework)
- **Learnings filter:** `~/.claude/skills/fe/learnings.md` by Tags (max 5)
- **Conflict check:** ขัด memory → หยุดถาม user ก่อน
- **Pre-flight:** detect Nuxt version (ดูล่าง) + อ่าน CLAUDE.md ของ project + อ่านโค้ดที่มีอยู่ก่อน (จับ pattern, naming, immutability) + ดู type definitions ก่อนเดา shape

---

## Stack default

ถ้า project ไม่บังคับ stack อื่น **default ใช้:**

- **Framework:** Nuxt (v3 / v4) + Vue 3 + `<script setup lang="ts">`
- **UI:** Nuxt UI (`UButton`, `UInput`, `UModal`, `UForm`, ...)
- **Validation:** valibot (ไม่ใช่ zod / yup)
- **State:** `useState()` เป็นหลัก; Pinia เมื่อใหญ่/persist/ซับซ้อน
- **Styling:** Tailwind (มากับ Nuxt UI)
- **Type imports:** `#shared`, `#imports`

### Version detection (mandatory ใน Pre-flight)

| Signal | Conclusion |
|---|---|
| `package.json` `nuxt: "^4.x"` + มี `app/` dir | **Nuxt 4** — v4 patterns |
| `package.json` `nuxt: "^3.x"` + ไม่มี `app/` dir | **Nuxt 3 classic** — v3 patterns |
| `nuxt: "^3.x"` + `compatibilityVersion: 4` + มี `app/` dir | **Nuxt 3 + v4 opt-in** — v4 patterns |

Quote detection ใน reasoning เช่น: *"Project นี้ Nuxt 3 + v4 compat → ใช้ v4 patterns"*

ถ้า project ใช้ React/Next/Svelte → ตาม project; แต่ default mental model = Nuxt + Nuxt UI + valibot

---

## Handoff (fe เป็นปลายน้ำของ pipeline `sa → ux → fe`)

**รับจาก `sa`** (source of truth ห้ามเปลี่ยน field name พลการ):
- API spec, data model, state shape, security finding + ripple list — ทุกไฟล์ใน list ต้องแก้พร้อมกัน

**รับจาก `ux`** (implement ตามไม่ตีความเอง):
- component map → ใช้ Nuxt UI ที่ระบุ
- Tailwind class plan → string literal ตรง (กัน JIT)
- visual state map → bind data → visual ตามที่ ux กำหนด
- animation spec / responsive plan / interaction spec

**Yield กลับ** เมื่อเจอช่องว่าง:
- data model ไม่ครอบคลุม edge case → yield `sa`
- design implement ไม่ได้ → yield `ux`
- เจอช่องโหว่ security ระหว่างเขียน → yield `sa` mode B
- **ห้าม hack เพื่อให้ผ่านเอง** — กลับไป skill ต้นน้ำเสมอ

**ก่อน implement ทุกครั้ง** — quote spec/design 1-2 บรรทัด เพื่อกัน drift จาก sa/ux

---

## Mode 1: Build / refactor

### ลำดับการคิด

1. **state อยู่ที่ไหน?** — local / composable / store / server — เลือกระดับต่ำสุดที่ทำงานได้
2. **side effect ผูกกับอะไร?** — mount / value change (`watch`) / event / interval — cleanup ที่ unmount
3. **derive ก่อน store** — คำนวณจาก state อื่นได้ → `computed`/selector อย่าเก็บซ้ำ
4. **immutable update** — `[...arr, x]`, `arr.map(...)`, `{ ...obj, k }` ไม่ mutate ตรงๆ
5. **return shape consistent** — `{ ok: true, data } | { ok: false, error }` ทั้ง project
6. **type ก่อน implementation** — signature ก่อน body

### Vue 3 reactivity essentials

- **`ref` vs `reactive`** — default `ref` (consistent unwrap); `reactive` ระวัง destructure ทำลาย reactivity
- **`computed` ต้อง pure** — ห้าม side effect (fetch / mutation) → ใช้ `watch`/`watchEffect` แทน
- **`watch` vs `watchEffect`** — default `watch` (dependency ชัด + old value); `watchEffect` ตอน track auto
- **`<script setup>`** — `defineProps` / `defineEmits` / `defineExpose` / `defineModel<T>()` (Vue 3.4+)
- **Props default** (Vue 3.5+): `const { foo = 'bar' } = defineProps<Props>()` — reactive-safe; ต่ำกว่า 3.5 ใช้ `withDefaults`
- **emits typed** — `defineEmits<{ submit: [value: string] }>()`
- **provide/inject** — `InjectionKey<T>` + default value

### Nuxt expertise

ดู REFERENCE.md sections (โหลด on-demand):
- `#nuxt-directory` — directory structure v3 vs v4
- `#nuxt-auto-imports` — สิ่งที่ห้าม import เพราะ auto
- `#nuxt-state` — `useState` vs Pinia
- `#nuxt-data-fetching` — `useFetch` / `useAsyncData` / `$fetch` + v3/v4 reactivity diff
- `#nuxt-routing` — `navigateTo`, middleware, `definePageMeta`
- `#nuxt-server` — `defineEventHandler`, `readBody`, `createError`
- `#nuxt-ssr` — `import.meta.client/server`, `<ClientOnly>`, hydration

### Composable convention

- ตั้งชื่อ `useXxx`, return ref/object — เรียกใน `<script setup>` เท่านั้น
- ใช้ `useState` ใน composable สำหรับ shared state — **ห้าม module-level `ref`** (leak ระหว่าง user บน SSR)
- Cleanup ผ่าน `onScopeDispose()` (รองรับนอก component lifecycle)
- คืน operation result shape เดียวกัน

### TypeScript

- **เลี่ยง `any`** — ใช้ `unknown` แล้ว narrow; external lib ไม่มี type → `.d.ts` shim
- **`as` คือ escape hatch** — `as any` แล้ว `as Foo` = ผิดทาง
- **discriminated union** สำหรับ state หลายโหมด — `{ status: 'idle' } | { status: 'loading' } | { status: 'error', error } | { status: 'success', data: T }`
- **`satisfies`** — `const config = { ... } satisfies Config` (check shape ไม่ widen)
- **generic component** — `<script setup lang="ts" generic="T">` ใน Vue

### Validation — valibot (default)

- derive type จาก schema: `type X = v.InferOutput<typeof XSchema>` ห้ามประกาศ type คู่ขนาน
- schema ชื่อ `XSchema`, type ชื่อ `X`; schema → `shared/schemas/`, types → `shared/types/`
- validate ที่ **boundary** เท่านั้น: form input, API response, localStorage parse
- `v.safeParse` ที่ boundary; `v.parse` ใน server route (throw 400 อัตโนมัติ)
- error message ภาษาไทย: `v.minLength(8, 'ต้องอย่างน้อย 8 ตัวอักษร')`
- syntax/example → REFERENCE.md `#valibot`

### Nuxt UI

ก่อนเขียน element ดิบ — เช็คก่อนว่า Nuxt UI มีไหม: `UButton` / `UInput` / `USelect` / `UForm` + `UFormField` / `UModal` / `UCard` / `UTable` / `UBadge` / `UAlert` / `UTabs` / `UTooltip` / `useToast()`

- `UForm` + `UFormField` + valibot schema ตรงๆ (`@submit` ได้ typed data)
- Icon: `icon="i-lucide-check"` (Iconify) — ไม่ import SVG
- Theming: `app.config.ts` → `ui: { colors: { primary: 'blue', neutral: 'slate' } }`
- Full table + UForm code → REFERENCE.md `#nuxt-ui`

---

## Clean code

### Naming
- **บอกความหมาย ไม่ใช่ type** — `tickets` ไม่ใช่ `arr`; `pendingCount` ไม่ใช่ `n`
- **boolean prefix `is/has/can/should`** — `isLoading`, `canSubmit`
- **function = verb** — `fetchTickets`, `validateForm`; ห้าม `data()`, `process()`, `handle()` generic
- **handler ใน template prefix `on`** — `onSubmit`, `onClick`
- **อย่าย่อจนงง** — `cnt`/`tk`/`usr` → `count`/`ticket`/`user`
- **ไฟล์/component** — `kebab-case.vue` หรือ `PascalCase.vue` ตาม project (อย่าผสม)

### Function shape
- **1 หน้าที่** — อธิบายต้องใช้ "และ" = ควรแยก
- **early return** กัน nesting ลึก
- **argument ≤ 3** — เกินรับเป็น object: `createTicket({ serviceId, customerName })`
- **> 40 บรรทัด** เป็นสัญญาณว่าทำหลายอย่าง

### Comment
- **default คือไม่เขียน** — ตั้งชื่อให้สื่อแทน
- เขียนเฉพาะ **"ทำไม"** ที่อ่านโค้ดเดาไม่ออก (workaround bug ภายนอก, business rule constraint, magic number มี source)
- ห้าม comment "อะไร" / `// removed` / `// deprecated` / `// TODO without ticket` / `// FIXME` ลอย

### Template (Vue)
- **expression สั้นๆ** — ซับซ้อนกว่า `a && b` → ดึงเป็น `computed`
- **`v-for` + `v-if` แยก element** — priority ตีกัน
- **`:key` เสถียร** — ใช้ id ไม่ใช่ index ถ้า list reorder ได้
- **ไม่มี logic ใน template** — ไม่มี `.filter().map().reduce()` ยาวๆ ใน `v-for`

### Magic value
- extract constant: `const MAX_RETRIES = 3`
- enum/const object สำหรับ string union หลายที่
- ห้าม `setTimeout(fn, 300)` ลอย — `const TOAST_DURATION_MS = 300`

### `<script setup>` order
1. `import`
2. `definePageMeta` / `defineProps` / `defineEmits` / `defineModel`
3. composable / store (`const route = useRoute()`)
4. local state (`ref`, `reactive`)
5. computed
6. function (handler, helper)
7. watch / lifecycle (`onMounted`)

อย่าสลับ — คนอ่านจะหาของเจอเร็ว

### Performance (เมื่อจำเป็น)
- profile ก่อน optimize (Vue Devtools / React Profiler / Chrome Performance) อย่าเดา
- list rendering: `key` เสถียร unique
- lazy load: route-level + component ใหญ่ที่ไม่ใช้ทันที
- debounce/throttle: `@vueuse/core` `useDebounceFn`
- virtualize list > ~100 items: `@tanstack/vue-virtual` / `vue-virtual-scroller`

---

## Mode 2: Review / audit

อ่านโค้ดจริงก่อน comment, อ้าง file:line เสมอ

### Reactivity bugs
- [ ] mutate array/object ตรงๆ (`.push`, `arr[0] = x`, `obj.foo = y`) — ตาม project convention
- [ ] destructure `reactive()` แล้วใช้ — สูญ reactivity
- [ ] อ่าน `.value` ใน template (auto-unwrap)
- [ ] `computed` มี side effect
- [ ] `watch` ลืม cleanup
- [ ] effect dependency หาย (React) — eslint-plugin-react-hooks

### State management
- [ ] state ซ้ำซ้อน (derive ได้แต่เก็บแยก = desync)
- [ ] state อยู่ผิดระดับ (local ที่ควร share / global ที่ควร local)
- [ ] mutation กระจาย — ควร centralize
- [ ] ลืม `persist()` หลัง mutate (ถ้า project มี persist convention)
- [ ] error shape ไม่ consistent (throw / null / `{ ok, error }`)

### Type safety
- [ ] `any` / `@ts-ignore` ไม่มี comment
- [ ] type คู่ขนานกับ schema (declared + zod แยก) — derive แทน
- [ ] `as` cast ลึก ซ่อน bug
- [ ] props ไม่มี type

### Component design
- [ ] component > ~200-300 บรรทัด — แตกได้ไหม
- [ ] prop ไม่ใช้ / emit ไม่มี listener
- [ ] prop drilling > 3 ชั้น — provide/inject หรือ store
- [ ] logic ซ้ำ template + script — extract `computed`
- [ ] template มี business logic ซับซ้อน — ดึงเป็น `computed`/method
- [ ] inline handler มี logic ยาว — แยก method
- [ ] `v-for` + `v-if` บน element เดียว

### Dead / suspicious
- [ ] commented-out code (มี git history)
- [ ] `console.log` debug ค้าง
- [ ] import ไม่ใช้
- [ ] variable assign แล้วไม่ใช้
- [ ] branch ที่ไม่มีทาง execute
- [ ] try/catch กลืน error เงียบ

### SSR / hydration (Nuxt/Next)
- [ ] เรียก `window`/`document`/`localStorage` ตอน setup ไม่ guard
- [ ] hydration mismatch (date locale, random, time)
- [ ] `import.meta.client/server` guard ครบ
- [ ] `useState` init เป็น value ตรง (ควร factory function — กันค่ารั่วระหว่าง user)
- [ ] `useFetch` ไม่มี `key` เสถียร → fetch ซ้ำ
- [ ] ใช้ `$fetch` ใน setup โดยตรง (ควร `useFetch`/`useAsyncData`)
- [ ] import สิ่งที่ Nuxt auto-import อยู่แล้ว

### Valibot
- [ ] type ประกาศซ้ำกับ schema
- [ ] `v.parse` ใน boundary ที่ควร `v.safeParse`
- [ ] error message ภาษาอังกฤษ default ในแอปไทย
- [ ] schema ซ้อน inline แทน extract เป็น const

### Nuxt UI
- [ ] `<button class="...">` แทน `UButton`
- [ ] overlay modal เองทั้งที่ `UModal`/`USlideover` มี
- [ ] icon inline SVG แทน `UIcon` + Iconify
- [ ] hardcode สีแทน `color="primary"` (ไม่ติด theme)
- [ ] form ทำ label+error เอง แทน `UForm` + `UFormField`
- [ ] alert/banner เอง แทน `useToast()`

### Convention adherence
- [ ] ใช้ pattern เดียวกับที่อื่น
- [ ] naming ตรง (camelCase / PascalCase / kebab-case)
- [ ] ใช้ lib ที่กำหนด (validation, http, date)
- [ ] alias import (`#shared`, `~/`, `@/`)

### Clean code
- [ ] ชื่อตาม type (`arr`, `data`) แทนความหมาย
- [ ] boolean ไม่มี `is/has/can/should`
- [ ] function ทำหลายอย่าง (ต้องใช้ "และ")
- [ ] nesting > 3 ชั้น (early return ได้)
- [ ] argument > 3 ไม่ใช้ object
- [ ] expression template ยาว/ซ้อน
- [ ] comment อธิบาย "อะไร" / comment-out ค้าง
- [ ] magic number/string ลอย

### รายงานผล
List issue + **severity** (blocker = data loss / bug จริง, major = anti-pattern หลัก, minor = ปรับให้ดี) + **file:line** + **suggestion**

อย่า quick-fix ทันทีถ้า user ขอ review เฉยๆ — รายงานก่อน รอ confirm

---

## เมื่อไหร่ "ไม่ต้อง" ปรับ

- Pattern เดิมไม่ใช่ "ดีที่สุดในตำรา" แต่สม่ำเสมอ → อย่าทำให้ไม่สม่ำเสมอ
- Micro-optimization ที่ profile ไม่ช่วย → อย่าใส่ `useMemo`/`computed` ไม่จำเป็น
- Abstraction "ดูสะอาด" แต่ debug ยาก → simple = better

---

## Quality gates (ก่อนเคลม "เสร็จ")

### Build / verify (ถ้าแก้โค้ด)
- [ ] **`tsc --noEmit`** 0 errors
- [ ] **Vite compile** หน้าที่แตะ — `curl /<page>` HTTP 200 + dev log ไม่มี `Invalid end tag`, `SelectItem must have a value prop`
- [ ] **`rtk proxy yarn nuxt prepare`** สำเร็จ (refresh auto-imports + types)

### UI verify (เมื่อมี UI เปลี่ยน)
- [ ] รัน `verify` skill — เปิด browser, golden path
- [ ] edge case ≥ 2 จาก spec (empty, error)
- [ ] network tab ไม่มี 4xx/5xx ไม่ตั้งใจ
- [ ] console ไม่มี error regression
- [ ] mobile breakpoint (375px) ไม่แตก

dev server ไม่พร้อม → แจ้ง user "verify ด้วยตนเองไม่ได้ — กรุณาทดสอบ: [steps]" **ห้ามเคลม "เสร็จ" เงียบๆ**

### Pattern verification (ถ้า scan/migrate/refactor)
- [ ] **Cross-verify ≥ 2 regex** — หลวม (`<tag`) + เข้ม (`<tag[\s>]`) ผลต้องตรง
- [ ] **Manual spot-check 2-3 ไฟล์** ก่อนเคลม "0 left"
- [ ] **Reka UI value scan** — ถ้าใช้ USelect/USelectMenu items: scan ทั้ง single + double quote หา `value: ""` / `value: ''`

### Ripple verification (ถ้าแก้ shared code)
- [ ] **Trace caller ≥ 1 hop** ก่อนเคลม "ไม่กระทบใคร" / "dead code"
- [ ] **Type usage trace** — ทุก consumer compile + behavior ถูก
- [ ] **Wrapper migration** — ลบ wrapper open + close พร้อมกัน

### Memory update
- [ ] **Project memory** ถ้าเจอ pattern/bug เฉพาะ project — เพิ่ม `feedback_<topic>.md`
- [ ] **Skill learnings** ถ้าเจอบทเรียน generalize ข้าม project (Vue reactivity, TS pattern, Nuxt UI quirk)
- [ ] user สั่ง "ชัวไหม / ตรวจอีก" = scan/verify รอบแรกไม่ดีพอ → memo + ปรับ pattern

### กฎทอง

> **Vite compile success + dev log clean = source of truth** สำหรับ template/runtime
> **`tsc --noEmit` 0 errors = source of truth** สำหรับ type
> **regex heuristic ไม่ใช่ source of truth** — multi-line construct บิด count

ห้ามเคลม "0 left / ครบ / เสร็จ" จาก scan รอบเดียว
