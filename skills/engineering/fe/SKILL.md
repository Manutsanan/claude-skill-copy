---
name: fe
description: Use when working on frontend code (Nuxt/Vue/React/TypeScript) — writing components, composables, Nuxt pages/layouts/middleware/server routes, state management, reactivity, type-safety, valibot validation, Nuxt UI components; or reviewing existing frontend code for anti-patterns, reactivity bugs, mutation issues, prop drilling, dead code, unclean naming. Trigger on tasks involving component implementation, composable design, state stores (Pinia/Zustand/useState), `ref`/`reactive`/`computed`/`watch`, props/emits, TypeScript generics, valibot schemas, Nuxt UI (UButton, UModal, UForm, ...), route guards, SSR/hydration, performance. Examples: "เขียน composable นี้ให้หน่อย", "review โค้ด component นี้", "state จัดการยังไงดี", "refactor ให้คลีน", "เขียน schema validate", "ทำไม reactivity ไม่ทำงาน", "หา anti-pattern".
---

# fe — Frontend code helper

ครอบคลุม 2 mode — เลือกใช้ตาม intent:

1. **Build / refactor** — เขียนหรือปรับ component / composable / store
2. **Review / audit** — ตรวจหา anti-pattern, bug, dead code, ของซ้ำซ้อน

> ขอบเขตของ skill นี้คือ **โค้ด** (logic, type, state, reactivity, performance) — ส่วน **UI/UX** (styling, layout, a11y, animation) ใช้ skill `ux`

## Handoff (fe เป็นปลายน้ำของ pipeline `sa → ux → fe`)

**รับจาก `sa`** (ถ้า sa ทำมาก่อน — ใช้เป็น source of truth ห้ามเปลี่ยน field name โดยพลการ):

- API spec → endpoint, method, request/response shape, error shape, auth requirement
- data model → entity + field + type + validation rule (เขียน TS type + valibot schema ตรงตามนี้)
- state shape + transition (เขียน composable/store ตามนี้)
- security finding + ripple list — **ทุกไฟล์ใน list ต้องแก้พร้อมกัน** ไม่แก้แค่จุดเดียว

**รับจาก `ux`** (ถ้า ux ทำมาก่อน — implement ตามไม่ตีความเอง):

- component map → ใช้ Nuxt UI component ที่ ux ระบุ อย่าเขียน `<button>` เปล่าถ้า ux บอก `UButton`
- Tailwind class plan → string literal ตรงตาม plan (กัน JIT ไม่เห็น) ห้ามประกอบจาก variable
- visual state map → bind data state → visual state ตามที่ ux กำหนด
- animation spec → ใช้ `<Transition>` / `transition-*` / GSAP ตามที่ ux เลือก
- responsive plan → Tailwind class set ของแต่ละ breakpoint
- interaction spec → hover/focus/active/disabled/loading state

**Yield กลับ** เมื่อเจอช่องว่าง:

- field/edge case ที่ data model ไม่ครอบคลุม → yield ไป `sa` ขอปรับ ER ก่อน
- design ที่ implement ไม่ได้ (component ไม่มีใน Nuxt UI / animation ชน performance) → yield ไป `ux` ขอปรับ
- เจอช่องโหว่ security ระหว่างเขียน → yield ไป `sa` mode B audit ก่อน fix
- **ห้าม hack เพื่อให้ผ่านเอง** — กลับไป skill ต้นน้ำเสมอ

**ก่อน implement ทุกครั้ง** — quote spec/design ที่กำลังจะ implement (1-2 บรรทัด) เพื่อกัน drift จาก artifact ของ sa/ux

ดู "Skill orchestration" ใน `~/.claude/CLAUDE.md` สำหรับ pipeline เต็ม

---

## Stack default ของ skill นี้

ถ้า user ไม่ได้ระบุเป็นอย่างอื่น และโปรเจกต์ไม่ได้บังคับเป็นอย่างอื่น **ให้เลือก stack นี้เป็น default:**

- **Framework**: **Nuxt** (รองรับทุก major version — 3, 4, และ version ใหม่ในอนาคต) + Vue 3 + `<script setup lang="ts">`
- **UI library**: **Nuxt UI** (`UButton`, `UInput`, `UModal`, `UForm`, `UFormField`, `UCard`, `UTable`, ...) — อย่าเขียน `<button class="...">` เปล่าๆ ถ้ามี `UButton` ใช้ได้
- **Validation**: **valibot** (ไม่ใช่ zod / yup)
- **State**: `useState()` ของ Nuxt สำหรับ shared state ธรรมดา; Pinia เฉพาะ state ที่ใหญ่/ซับซ้อน/ต้อง persist อย่าง auth
- **Styling**: Tailwind utility classes (มากับ Nuxt UI)
- **Type imports**: ใช้ alias ของ Nuxt (`#shared`, `#imports`) ถ้ามี

### Version detection (mandatory — ทำใน Pre-flight)

ก่อน implement ใดๆ — **detect Nuxt version ของ project ปัจจุบัน** เพื่อเลือก pattern ที่ถูก:

1. **อ่าน `package.json`** — ดู `nuxt` ใน `dependencies` / `devDependencies` → version major (`^3.x.x` vs `^4.x.x`)
2. **อ่าน `nuxt.config.ts`** — `compatibilityVersion: 4` ใน `future: {}` block = Nuxt 3 เปิด opt-in สำหรับ v4 behavior
3. **ดู directory layout จริง** — มี `app/` directory ที่ root ไหม? → v4 layout; ไม่มี → v3 layout

| Signal | Conclusion |
|---|---|
| `package.json` `nuxt: "^4.x"` + มี `app/` dir | **Nuxt 4** — ใช้ v4 patterns ตรงๆ |
| `package.json` `nuxt: "^3.x"` + ไม่มี `app/` dir | **Nuxt 3 classic** — ใช้ v3 patterns (pages/, components/ ที่ root) |
| `package.json` `nuxt: "^3.x"` + `compatibilityVersion: 4` + มี `app/` dir | **Nuxt 3 with v4 opt-in** — ใช้ v4 patterns |

ใน reasoning ของ skill — quote ให้ user เห็นว่า detect ได้อะไร เช่น: *"Project นี้คือ Nuxt 3 + v4 compatibility (มี `app/` dir, `compatibilityVersion: 4`) → จะใช้ v4 patterns"*

ถ้าโปรเจกต์ใช้ stack อื่น (React/Next, Svelte, ฯลฯ) ให้ตามโปรเจกต์เป็นหลัก — แต่ default mental model ของ skill นี้คือ Nuxt + Nuxt UI + valibot

---

## Phase 0 — Load memory hierarchy (mandatory — extend Universal Phase 0)

ลำดับ:

1. **Load global memory** — `~/.claude/memory/MEMORY.md`
   - filter: `metadata.skill: fe` หรือ `skill: cross`
   - filter ต่อด้วย keyword: component name, library, error pattern, framework, validation
   - ถ้าไม่มีไฟล์ → ข้าม + หมายเหตุ "ไม่มี global memory"

2. **Load project memory** — `~/.claude/projects/<project-id>/memory/MEMORY.md`
   - project id = working directory แปลง `/` → `-` (เช่น `/Users/X/Project/Y` → `-Users-X-Project-Y`)
   - filter เดียวกับ global memory
   - ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory — fresh start"

3. **Echo top 3-5 entries** กลับให้ user เห็นก่อนเริ่ม:
   ```
   📚 Memory ที่ relevant กับงานนี้ (fe):
   - [global] user-prefers-valibot — default stack: Nuxt + Nuxt UI + valibot
   - [project] feedback-x — one-line summary
   - [project] project-y — one-line summary
   ```

4. **Conflict check** — ถ้าจะ propose สิ่งที่ขัด memory → หยุดถาม user ก่อน + override → update memory ให้สะท้อน อย่าทิ้ง memory เก่าไว้ขัดแย้ง

5. **หลังจบงาน** — save lesson ตาม **8 universal save triggers** ใน `~/.claude/CLAUDE.md` Universal Phase 0 #4 (อ้างตารางว่า save ไป global หรือ project)

### Memory ที่ `fe` ต้องเช็คทุกครั้ง (ถ้ามีใน project)

- `feedback_select_item_value_empty_string.md` — USelect/USelectMenu items ห้ามมี value=''
- `feedback_grep_multiline_attrs.md` — regex pattern เมื่อ scan template
- `feedback_dangling_tag_after_wrapper_removal.md` — migration ของ wrapper element
- `feedback_verify_before_claiming_done.md` — ก่อนเคลม "เสร็จ"
- `feedback_template_vif_slot_reactivity.md` — Vue 3 slot existence ไม่ reliably reactive

### Pre-flight อื่นๆ (ทำคู่กับ Phase 0)

1. **Detect Nuxt version** — อ่าน `package.json` + `nuxt.config.ts` + directory layout เพื่อระบุว่า v3 classic / v4 / v3 + opt-in (ดู "Version detection" ใน Stack default)
2. **อ่านโค้ดที่มีอยู่ก่อน** — จับ pattern ของโปรเจกต์ (state shape, naming, immutability rule, error shape, validation lib) อย่าสร้าง pattern ใหม่ขนานกัน
3. **อ่าน CLAUDE.md** ของโปรเจกต์ — มัก spell out convention ที่ต้องตาม (เช่น "ใช้ valibot ไม่ใช่ zod")
4. **ดู type definitions** ก่อนเดา shape ของข้อมูล — อย่าเขียน `any` เพื่อข้ามความขี้เกียจ
5. **เช็คว่ามี Nuxt UI component อยู่แล้วไหม** ก่อนเขียน HTML element ดิบ — `UButton` ดีกว่า `<button>`, `UModal` ดีกว่าสร้าง overlay เอง

> ดู `~/.claude/CLAUDE.md` Universal Phase 0 สำหรับ load/save logic เต็ม + skill tag convention

---

## Phase 0.5 — Load skill learnings (mandatory)

ลำดับ:

1. **Extract task keywords** — ดึง keyword จาก request ของ user: ชื่อ component (`USelect`, `UModal`), library (`valibot`, `pinia`), error type, pattern (`reactivity`, `composable`, `hydration`, `ssr`)
2. **อ่าน** `~/.claude/skills/fe/learnings.md` — scan เฉพาะ **Tags:** field ของแต่ละ entry
3. **Load เฉพาะ entry ที่ตรง** — entry ผ่านถ้า Tags มี ≥1 keyword ตรง **และ header ไม่มี `~~`**; ถ้าไม่มี tag ตรงหรือ header มี `~~` (deprecated) → skip ทั้ง entry
4. **Max 5 entries** — ถ้าตรงมากกว่า 5 → เลือก 5 ที่ keyword match สูงสุด; tie → เลือกที่ Date ใหม่กว่า
5. **Quote** entry ที่ใช้ใน reasoning — เช่น "ตาม learnings#destructure-reactive-loses-reactivity จะใช้ toRefs แทน"
6. **ถ้าไม่มี entry ตรง** → หมายเหตุ "ไม่มี skill learning ตรง — fresh start" (ห้าม fallback โหลดทั้งไฟล์)
7. **หลังจบงาน** → ถ้าเจอบทเรียน generalize ได้ → append เข้า learnings.md (ดู Quality gates)

---

## Mode 1: Build / refactor

ลำดับการคิด:

1. **state อยู่ที่ไหน?** — local component / composable shared / store global / server. เลือกระดับต่ำสุดที่ทำงานได้
2. **side effect ผูกกับอะไร?** — mount lifecycle / value change (`watch`) / event listener / interval. cleanup ที่ unmount เสมอ
3. **derive ก่อน store** — ถ้าค่าคำนวณจาก state อื่นได้ ใช้ `computed` / selector อย่าเก็บซ้ำ (จะ desync)
4. **immutable update** — `[...arr, x]`, `arr.map(...)`, `{ ...obj, k: v }` ไม่ mutate ตรงๆ (กัน reactivity หลุด + กัน bug ที่หา root cause ยาก)
5. **return shape คงเส้นคงวา** — operation ที่ fail ได้ใช้ pattern เดียวกันทั้งโปรเจกต์ (เช่น `{ ok: true, data } | { ok: false, error }`)
6. **type ก่อน implementation** — เขียน signature ก่อน body ช่วย clarify intent

### Vue 3 reactivity (พื้นฐานก่อน Nuxt)

> Nuxt 3 รองรับ Vue 3.3+ (ส่วน Nuxt 3.10+ มัก ship กับ Vue 3.4); Nuxt 4 ship กับ Vue 3.5+ — ระบุ minimum version เมื่อใช้ feature ใหม่

- **`ref` vs `reactive`** — default ใช้ `ref` (consistent การ unwrap, ใช้กับ primitive/object ได้เหมือนกัน). `reactive` เฉพาะกรณีต้อง destructure แล้วยังต้อง reactive (ซึ่งหายาก) — แต่ระวัง: destructure `reactive` ทำลาย reactivity
- **`computed` กับ side effect** — `computed` ต้อง pure ห้ามมี side effect (fetch, mutation). ถ้าต้องตอบสนองต่อ change แล้วทำ side effect ใช้ `watch` / `watchEffect`
- **`watch` vs `watchEffect`** — `watch(source, cb)` เมื่อต้องระบุ dependency ชัด + เข้าถึง old value; `watchEffect` เมื่อ track auto ทุกตัวที่อ่านใน callback. default `watch` (ชัดเจนกว่า)
- **`<script setup>`** — default; ใช้ `defineProps` / `defineEmits` / `defineExpose` / `defineModel` (Vue 3.4+ — Nuxt 3.10+ มีอยู่แล้ว)
- **props default** (Vue 3.5+ feature — Nuxt 4 ได้ตรงๆ, Nuxt 3 ต้องเช็คว่า Vue ≥ 3.5): destructure default `const { foo = 'bar' } = defineProps<Props>()` (reactive-safe). ถ้า Vue < 3.5 ต้อง fall back เป็น `withDefaults(defineProps<Props>(), { foo: 'bar' })`
- **emits typed** — `defineEmits<{ submit: [value: string] }>()` ไม่ใช่ array of strings
- **`defineModel<T>()`** (Vue 3.4+) — สำหรับ two-way binding (`v-model`) แทน prop+emit pair
- **provide/inject** — ใช้ `InjectionKey<T>` เพื่อ type-safe; default value กัน undefined

---

## Nuxt expertise (รองรับ v3 + v4)

ต้องชำนาญทั้ง 3 ด้าน: **directory structure**, **auto-imports**, **data fetching**

> **ก่อนเขียน path ใดๆ — confirm version จาก Pre-flight detection ก่อน** ดู section "Version detection" ด้านบน
>
> ความต่างสำคัญ v3 vs v4 ที่กระทบ skill นี้:
> | | Nuxt 3 (classic) | Nuxt 4 (หรือ v3 + `compatibilityVersion: 4`) |
> |---|---|---|
> | Source root | root ของ project (`pages/`, `components/` ที่ root) | `app/` directory (`app/pages/`, `app/components/`) |
> | `data` ของ `useAsyncData` | deep reactive (default) | shallow reactive (default — perf better, แต่ต้องระวัง mutate object ลึก) |
> | `<NuxtPage>` lifecycle | re-render ตาม route change | เหมือนเดิม |
> | TypeScript project structure | tsconfig เดียว | แยก tsconfig (app + server) — auto-generated |
> | Default fetch behavior | deep watch | shallow ref — รู้ตัวเมื่อ assign object ใหม่ |

### Directory structure

ตารางด้านล่างใช้ path ของ **Nuxt 4** (มี `app/` prefix) — ถ้า project เป็น Nuxt 3 classic ให้ตัด `app/` ออก (เช่น `app/pages/` → `pages/`):

| Dir (v4 / v3-with-opt-in) | Dir (v3 classic)     | Purpose                            | Auto                                                              |
| ------------------------- | -------------------- | ---------------------------------- | ----------------------------------------------------------------- |
| `app/pages/`              | `pages/`             | file-based routing                 | route auto                                                        |
| `app/layouts/`            | `layouts/`           | shared shell                       | `definePageMeta({ layout: 'foo' })`                               |
| `app/components/`         | `components/`        | components                         | auto-import (PascalCase, nested = prefix)                         |
| `app/composables/`        | `composables/`       | `use*` functions                   | auto-import                                                       |
| `app/middleware/`         | `middleware/`        | route guards                       | named or `.global.ts`                                             |
| `app/plugins/`            | `plugins/`           | runtime plugin                     | run at app start; `.client.ts`/`.server.ts` ต่อท้ายเพื่อจำกัด env |
| `app/utils/`              | `utils/`             | pure helper                        | auto-import                                                       |
| `app/assets/`             | `assets/`            | bundled assets (SCSS, fonts)       | import path                                                       |
| `public/`                 | `public/`            | static (served as-is at `/`)       | URL `/foo.png`                                                    |
| `server/api/`             | `server/api/`        | API routes                         | auto `/api/*`                                                     |
| `server/routes/`          | `server/routes/`     | non-`/api` server routes           | auto                                                              |
| `server/middleware/`      | `server/middleware/` | server-side middleware             | auto run ทุก request                                              |
| `shared/`                 | `shared/` (v3.10+)   | type/util ใช้ได้ทั้ง client+server | import via `#shared`                                              |

### Auto-imports — ใช้ให้ครบ อย่า import เกิน

**ห้ามเขียน import** สิ่งเหล่านี้ (มัน auto):

- Vue: `ref`, `reactive`, `computed`, `watch`, `watchEffect`, `onMounted`, `onUnmounted`, `nextTick`, `shallowRef`, `triggerRef`, ...
- Nuxt: `useState`, `useFetch`, `useAsyncData`, `useRoute`, `useRouter`, `useRuntimeConfig`, `useCookie`, `useHead`, `useSeoMeta`, `navigateTo`, `createError`, `defineNuxtConfig`, `defineNuxtPlugin`, `defineEventHandler`, `defineNuxtRouteMiddleware`, ...
- Component ใน components directory (`app/components/` ใน v4, `components/` ใน v3 classic) — ใช้ tag ตรงๆ (PascalCase) ใน template
- Composable ใน composables directory (`app/composables/` ใน v4, `composables/` ใน v3) — เรียกตรงๆ
- Util ใน utils directory (`app/utils/` ใน v4, `utils/` ใน v3) — เรียกตรงๆ

**Type imports** ใช้ `import type { Foo } from '#shared/types'` (จาก `shared/types/`)

### State (Nuxt-specific)

- **`useState(key, init)`** — SSR-safe shared ref. ตัวเลือกแรกสำหรับ shared business state. **key ต้อง unique ทั่วแอป** (ชนกัน = ค่ากระโดด). init เป็น function ไม่ใช่ value (กัน serialize on SSR)
- **`useState` vs Pinia** — `useState` เพียงพอ 80% ของ shared state. ใช้ Pinia เมื่อ: (1) ต้อง persist (กับ `pinia-plugin-persistedstate`), (2) มี action/getter ซับซ้อน, (3) state graph ใหญ่ที่ต้อง devtools tracing
- **persist localStorage** — wrap `process.client` / `import.meta.client` guard เสมอ ห้ามอ่าน `localStorage` ตอน SSR

### Data fetching

- **`useFetch(url)`** — wrapper บน `useAsyncData` + `$fetch` รวม URL เป็น key auto. ใช้สำหรับ data ผูกกับ page/component
- **`useAsyncData(key, fn)`** — เมื่อ logic ซับซ้อนกว่า fetch URL เดียว (เช่น เรียก 2 endpoint แล้ว combine)
- **`$fetch(url)`** — imperative call (ใน event handler, ใน server route). **ไม่** SSR-cache ไม่ dedupe — ถ้าใช้ใน `setup` จะ fetch ซ้ำที่ client
- **`server: false`** — เลี่ยง SSR fetch (สำหรับ data ที่ต้อง auth client-side)
- **`lazy: true`** — ไม่ block navigation, render UI ก่อน data มา
- **`watch: [refs]`** — refetch เมื่อ ref เปลี่ยน
- **Error handling** — `const { data, error, status, refresh } = await useFetch(...)`. ตรวจ `error.value` ใน template, `status.value` มี `'idle' | 'pending' | 'success' | 'error'`

**v3 vs v4 — `data` reactivity behavior**

- **Nuxt 3 classic:** `data` เป็น **deep reactive** ref — mutate field ลึก (เช่น `data.value.user.name = 'X'`) จะ trigger re-render
- **Nuxt 4 (หรือ v3 + `compatibilityVersion: 4`):** `data` เป็น **shallow ref** by default — mutate field ลึกจะ **ไม่** trigger re-render; ต้อง assign reference ใหม่ทั้ง object (`data.value = { ...data.value, user: { ...data.value.user, name: 'X' } }`)
- ถ้าต้องการ deep reactive ใน v4 — pass `{ deep: true }` เข้า `useAsyncData` / `useFetch` options
- ผลกระทบ: pattern เก่าที่ `data.value.someField = x` ใน v3 → ต้องเขียนใหม่ใน v4 หรือ opt-in deep

### Routing & navigation

- **Dynamic route**: `pages/counter/[id].vue` → `useRoute().params.id`
- **Catch-all**: `[...slug].vue` → array of segments
- **`navigateTo(path)`** — ใช้แทน `router.push` ใน Nuxt (รองรับ SSR redirect ผ่าน `{ redirectCode: 302 }`)
- **`definePageMeta({ middleware: 'auth', layout: 'admin' })`** — page-level config
- **Middleware**: `defineNuxtRouteMiddleware((to, from) => { ... })` — return `navigateTo()` หรือ `abortNavigation()` หรือ `undefined` (allow)

### Server routes (`server/api/`)

- **File-based**: `server/api/users/[id].get.ts` → `GET /api/users/:id`
- **`defineEventHandler(async (event) => { ... })`**
- **อ่าน body**: `await readBody(event)` (POST/PUT/PATCH)
- **อ่าน query**: `getQuery(event)`
- **อ่าน param**: `getRouterParam(event, 'id')`
- **Throw**: `throw createError({ statusCode: 400, statusMessage: 'ข้อความไทย' })`
- **runtime config**: `useRuntimeConfig()` (server-side มี private + public; client เห็นแค่ `public`)

### SSR / hydration ระวัง

- ห้ามเรียก `window`, `document`, `localStorage`, `navigator` ตอน setup โดยไม่ guard
- ใช้ `import.meta.client` / `import.meta.server` (Nuxt 3.10+) แทน `process.client`
- `<ClientOnly>` wrap ส่วนที่ render เฉพาะ client (gauge, chart, ฯลฯ)
- `onMounted()` รันเฉพาะ client เสมอ — ใส่ logic ที่ต้องการ DOM ตรงนี้ได้
- date/time/random ที่อาจต่างระหว่าง server กับ client → คำนวณใน `onMounted` หรือ wrap `<ClientOnly>`

### SEO / head

- **`useSeoMeta({ title, description, ogImage, ... })`** — type-safe กว่า `useHead`
- **`useHead({ link, script, ... })`** — สำหรับ tag อื่นๆ

### Composable convention

- ตั้งชื่อ `useXxx`, return ref/object — เรียกใน `<script setup>` เท่านั้น
- ใช้ `useState` ใน composable ถ้าต้องการ state shared ระหว่าง caller — ห้ามใช้ module-level `ref` (จะ leak ระหว่าง user บน SSR)
- Cleanup ผ่าน `onScopeDispose()` (รองรับนอก component lifecycle ด้วย)
- คืน operation result เป็น shape เดียวกันทั้ง composable: เช่น `{ ok: true, data } | { ok: false, error: string }` — ตามที่ project กำหนด

### React patterns — ดู `~/.claude/skills/fe/REFERENCE.md#react`

### TypeScript patterns

- **เลี่ยง `any`** — ใช้ `unknown` แล้ว narrow; ถ้าเป็น external lib ที่ไม่มี type ให้ใส่ `.d.ts` shim
- **`as` คือ escape hatch** — ใช้เมื่อรู้แน่ว่า type ตรงแต่ TS เดาไม่ออก. ถ้าเริ่มเขียน `as any` แล้ว `as Foo` แสดงว่าผิดทาง
- **discriminated union** สำหรับ state ที่มีหลายโหมด — `{ status: 'idle' } | { status: 'loading' } | { status: 'error', error: string } | { status: 'success', data: T }` — แทนที่ flag bool หลายตัว
- **`satisfies`** เมื่อต้องการ check shape โดยไม่ widen type — `const config = { ... } satisfies Config`
- **generic component** — `<script setup lang="ts" generic="T">` ใน Vue; `function Component<T>(props: Props<T>)` ใน React
- **type vs interface** — interface สำหรับ object shape ที่ extend ได้, type สำหรับ union/intersection/utility — ใช้ตามที่อ่านง่าย ไม่ต้องเคร่ง

### Validation — **valibot** (default)

- derive type จาก schema: `type X = v.InferOutput<typeof XSchema>` — ห้ามประกาศ type คู่ขนาน
- schema ชื่อ `XSchema`, type ชื่อ `X`; เก็บใน `shared/schemas/`, types ใน `shared/types/`
- validate ที่ **boundary** เท่านั้น: form input, API response, localStorage parse
- ใช้ `v.safeParse` เป็น default ที่ boundary; `v.parse` ใน server route (throw 400 อัตโนมัติ)
- error message ภาษาไทย: `v.minLength(8, 'ต้องอย่างน้อย 8 ตัวอักษร')`

→ syntax, code examples, pipe actions ดูใน `~/.claude/skills/fe/REFERENCE.md#valibot`

### Nuxt UI v4 — ใช้ component แทน HTML ดิบเสมอ

ก่อนเขียน element ดิบ — เช็คก่อนว่า Nuxt UI มีไหม: `UButton` / `UInput` / `USelect` / `UForm` + `UFormField` / `UModal` / `UCard` / `UTable` / `UBadge` / `UAlert` / `UTabs` / `UTooltip` / `useToast()`

- `UForm` + `UFormField` + valibot schema รองรับกันตรงๆ (`@submit` event ได้ typed data)
- Icon: `icon="i-lucide-check"` (Iconify) — ไม่ต้อง import SVG
- Theming: `app.config.ts` → `ui: { colors: { primary: 'blue', neutral: 'slate' } }`

→ full component table + UForm code example ดูใน `~/.claude/skills/fe/REFERENCE.md#nuxt-ui`

### Clean code — เขียนให้คนอ่านเข้าใจทันที

**เป้าหมาย**: คนที่ไม่ได้เขียนโค้ดนี้ เปิดมาแล้วเข้าใจใน < 30 วินาที โดยไม่ต้องไล่ที่อื่น

#### Naming

- **ชื่อตัวแปรบอกความหมาย ไม่ใช่ type** — `tickets` ดีกว่า `arr`, `pendingCount` ดีกว่า `n`
- **boolean ขึ้นต้นด้วย `is/has/can/should`** — `isLoading`, `hasError`, `canSubmit`, `shouldRedirect`
- **function = verb** — `fetchTickets`, `validateForm`, `mapToView`. ห้าม `data()`, `process()`, `handle()` แบบ generic
- **handler ใน template** — `onSubmit`, `onSelectCounter`, `onClickRecall` — เริ่มด้วย `on` ให้รู้ว่าเป็น event handler
- **อย่าย่อจนงง** — `cnt`/`tk`/`usr` ไม่ช่วยอะไร, `count`/`ticket`/`user` อ่านได้เลย
- **ชื่อสะกดถูก ใช้ภาษาเดียวกันทั้งไฟล์** — อย่ามั่ว `customerLst`, `ticketLst`, `count` ปนกัน
- **ไฟล์/component**: `kebab-case.vue` หรือ `PascalCase.vue` ตามที่โปรเจกต์ใช้ — อย่าผสม

#### Function shape

- **ฟังก์ชัน 1 หน้าที่** — ถ้าอธิบายต้องใช้ "และ" แสดงว่าควรแยก
- **early return** กัน nesting ลึก:
  ```ts
  // ❌
  function call(t) {
    if (t) {
      if (t.status === 'waiting') {
        if (counter.isOpen) { ... }
      }
    }
  }
  // ✅
  function call(t) {
    if (!t) return
    if (t.status !== 'waiting') return
    if (!counter.isOpen) return
    ...
  }
  ```
- **argument ≤ 3** — เกินกว่านี้รับเป็น object: `createTicket({ serviceId, customerName, priority })`
- **ความยาว** — function > 40 บรรทัดเป็นสัญญาณว่าทำหลายอย่าง (ไม่ใช่กฎตายตัว)

#### Comment

- **default คือไม่เขียน** — ตั้งชื่อให้สื่อแทน
- เขียนเฉพาะกรณี **"ทำไม"** ที่อ่านโค้ดแล้วเดาไม่ออก:
  - workaround ของ bug ภายนอก
  - constraint จาก business rule
  - magic number ที่มี source (`// 8h, ตาม spec security 2026-Q1`)
- ห้ามเขียน comment ที่บอก "อะไร" — โค้ดบอกได้เอง
  ```ts
  // ❌ // เพิ่ม ticket เข้า array
  tickets.value = [...tickets.value, t];
  // ❌ // ตรวจว่า user login หรือยัง
  if (!auth.isLoggedIn) return;
  ```
- ห้าม `// removed`, `// deprecated`, `// TODO without ticket` — ลบทิ้งไปเลย หรือผูกกับ issue
- ห้าม `// FIXME` ลอยๆ — ถ้ารู้ว่าผิด แก้เลย; ถ้าแก้ไม่ได้ ระบุ issue/PR

#### Template (Vue)

- **expression ใน template สั้นๆ** — ถ้าซับซ้อนกว่า `a && b` ดึงเป็น `computed`
  ```vue
  <!-- ❌ -->
  <div v-if="user && user.role === 'admin' && ticket.status !== 'closed' && !isLoading">
  <!-- ✅ -->
  <div v-if="canManage">
  ```
- **`v-for` + `v-if` แยก element** — ห้ามใส่บน element เดียวกัน (priority ตีกัน)
- **`:key` เสถียร** — ใช้ id ไม่ใช่ index ถ้า list reorder ได้
- **ไม่มี logic ใน template** — ไม่มี `.filter().map().reduce()` ยาวๆ ใน `v-for`; ดึงเป็น computed

#### Magic value

- ดึง constant ออกมา: `const MAX_RETRIES = 3`, `const TICKET_PREFIX = 'A'`
- ใช้ enum/const object สำหรับ string union ที่ใช้หลายที่
- ห้าม `setTimeout(fn, 300)` ลอยๆ — `const TOAST_DURATION_MS = 300`

#### Code organization in `<script setup>`

ลำดับที่อ่านง่ายที่สุด:

1. `import`
2. `definePageMeta` / `defineProps` / `defineEmits` / `defineModel`
3. composable / store ที่ใช้ (`const route = useRoute()`)
4. local state (`ref`, `reactive`)
5. computed
6. function (handler, helper)
7. watch / lifecycle (`onMounted`)

**อย่าสลับ** — คนอ่านจะหาของเจอเร็ว

---

### Performance (เมื่อจำเป็น)

- ก่อน optimize: **profile ก่อน** (Vue Devtools, React Profiler, Chrome Performance) — อย่าเดา
- **list rendering**: ใช้ `key` ที่เสถียรและ unique (ไม่ใช่ index ถ้า list reorder ได้)
- **lazy load**: route-level (`defineAsyncComponent` / dynamic import); component ใหญ่ที่ไม่ใช้ทันที
- **debounce / throttle** input handler ที่ trigger บ่อย (`@vueuse/core` มี `useDebounceFn`)
- **virtualize** list ที่ยาวเกิน ~100 items (`@tanstack/vue-virtual` / `vue-virtual-scroller`)

---

## Mode 2: Review / audit

ตรวจตามหมวดต่อไปนี้ — **อ่านโค้ดจริง** ก่อน comment, **อ้างไฟล์:บรรทัด** เสมอ

### Reactivity bugs

- [ ] mutate array/object ตรงๆ (`.push`, `arr[0] = x`, `obj.foo = y`) — Vue ref-based + Pinia: ok แต่ต้องระวัง localStorage sync; **immutable convention ของโปรเจกต์ไหนใช้ตามนั้น**
- [ ] destructure `reactive()` แล้วใช้ตัวที่ destructure — สูญ reactivity
- [ ] อ่าน `.value` ใน template — ไม่ต้อง (auto-unwrap)
- [ ] `computed` มี side effect (fetch, console.log แบบ depend on time, mutation)
- [ ] `watch` ลืม cleanup (interval, listener, subscription)
- [ ] effect dependency หาย (React) — eslint-plugin-react-hooks เตือน

### State management

- [ ] state ซ้ำซ้อน — ค่าหนึ่ง derive ได้จากอีกค่า แต่เก็บแยก (จะ desync)
- [ ] state อยู่ผิดระดับ — local state ที่ควร share / global state ที่ควร local
- [ ] mutation กระจายหลายที่ — ควร centralize ใน store/composable
- [ ] ลืม `persist()` หลัง mutate (ถ้าโปรเจกต์มี persist convention)
- [ ] error shape ไม่ consistent — บางที่ throw, บางที่ return null, บางที่ return `{ ok, error }`

### Type safety

- [ ] `any` หรือ `// @ts-ignore` ที่ไม่มี comment ว่าทำไม
- [ ] type คู่ขนานกับ schema (declared type + zod schema แยก) — derive จาก schema แทน
- [ ] `as` cast ที่ลึก ๆ ซ่อน bug
- [ ] props ไม่มี type / ใช้ default `any`

### Component design

- [ ] component ใหญ่เกิน ~200-300 บรรทัด — แตกได้ไหม
- [ ] prop ที่ไม่ใช้ / emit ที่ไม่มี listener
- [ ] prop drilling ลึก > 3 ชั้น — ใช้ provide/inject หรือ store แทน
- [ ] logic ซ้ำใน template + script — extract เป็น computed
- [ ] template ทำ business logic ซับซ้อน (`v-if` ซ้อนหลายชั้น, expression ยาวๆ) — ดึงเป็น computed/method
- [ ] inline event handler มี logic ยาว — แยก method
- [ ] `v-for` + `v-if` บน element เดียว — split loop ออก

### Dead / suspicious code

- [ ] commented-out code — ลบ (มี git history แล้ว)
- [ ] `console.log` debug ค้าง
- [ ] import ไม่ใช้
- [ ] variable ที่ assign แล้วไม่ได้ใช้
- [ ] branch ที่ไม่มีทาง execute (`if (false)`, dead else)
- [ ] feature flag / disabled prop ที่ไม่มีจุด toggle จริงๆ
- [ ] try/catch ที่กลืน error เงียบ ๆ ไม่ log ไม่ rethrow

### Convention adherence (ดู CLAUDE.md ก่อน)

- [ ] ใช้ pattern เดียวกับที่อื่นในโปรเจกต์
- [ ] naming ตรง convention (camelCase / PascalCase / kebab-case ตามที่)
- [ ] ใช้ lib ที่กำหนด (validation, http client, date) ไม่เอาตัวอื่นมาเสริม
- [ ] import path ใช้ alias ที่กำหนด (`#shared`, `~/`, `@/`)

### SSR / hydration (ถ้าใช้ Nuxt/Next)

- [ ] เรียก `window` / `document` / `localStorage` ตอน setup โดยไม่ guard — เจอ SSR error
- [ ] hydration mismatch — render ต่างระหว่าง server กับ client (date locale, random, time-dependent)
- [ ] `import.meta.client` / `import.meta.server` guard ครบสำหรับ browser-only API
- [ ] `useState` init เป็น value ตรง (ควรเป็น factory function) — ทำให้ค่ารั่วระหว่าง user
- [ ] `useFetch` ไม่มี `key` ที่เสถียรเมื่อ args เปลี่ยน → fetch ซ้ำ
- [ ] ใช้ `$fetch` ใน setup โดยตรง (ควรใช้ `useFetch`/`useAsyncData` เพื่อ SSR-cache)
- [ ] import สิ่งที่ Nuxt auto-import อยู่แล้ว (`ref`, `useState`, `navigateTo`, ฯลฯ) — เป็น noise

### Valibot

- [ ] type ประกาศซ้ำกับ schema (ควร `v.InferOutput<typeof Schema>`)
- [ ] ใช้ `v.parse` ใน boundary ที่ควรใช้ `v.safeParse` (อยากได้ explicit error)
- [ ] error message เป็นภาษาอังกฤษ default ในแอปภาษาไทย
- [ ] schema ซ้อน inline แทน extract เป็น const (อ่านยาก reuse ไม่ได้)
- [ ] import `import * as v` ทั้งก้อนทั้งที่ใช้ 2-3 ตัว — เสีย tree-shake (ถ้ารู้สึกชัด)

### Nuxt UI

- [ ] เขียน `<button class="...">` แทน `UButton` (มี variant/size/loading/icon ในตัว)
- [ ] ทำ overlay modal เองทั้งที่ `UModal`/`USlideover` มีอยู่
- [ ] ใส่ icon ด้วย inline SVG แทน `UIcon` + Iconify name
- [ ] hard-code สีแทนใช้ `color="primary"` / `color="error"` ของ Nuxt UI (ไม่ติด theme)
- [ ] form ทำ label+error markup เอง แทน `UForm` + `UFormField` (ขาด a11y/error binding)
- [ ] ตั้ง toast ผ่าน alert/banner เอง แทน `useToast()`

### Clean code / readability

- [ ] ตัวแปรตั้งชื่อตาม type (`arr`, `obj`, `data`) แทนตามความหมาย
- [ ] boolean ไม่มี prefix `is/has/can/should`
- [ ] function ทำหลายอย่าง (อธิบายต้องใช้ "และ")
- [ ] nesting ลึกกว่า 3 ชั้น (ใช้ early return ได้)
- [ ] argument > 3 ตัวต่อกันโดยไม่ใช้ object
- [ ] expression ใน template ยาว/ซ้อนหลายเงื่อนไข (ดึงเป็น `computed`)
- [ ] comment อธิบาย "อะไร" (ตั้งชื่อใหม่แทน) หรือ comment-out code ค้าง
- [ ] magic number/string ลอยๆ (extract เป็น const)

### รายงานผล

list issue เป็นข้อๆ พร้อม:

- **severity**: blocker (bug จริง / data loss) / major (anti-pattern หลัก) / minor (ปรับให้ดีขึ้น)
- **file:line** เสมอ
- **suggestion** สั้นๆ ว่าควรเป็นยังไง

อย่าทำ `quick fix` ทันทีถ้าผู้ใช้ขอให้ review เฉยๆ — รายงานก่อน รอ confirm

---

## เมื่อไหร่ "ไม่ต้อง" ปรับ

- pattern เดิมแม้จะไม่ใช่ที่ "ดีที่สุดในตำรา" แต่สม่ำเสมอทั้งโปรเจกต์ → อย่าทำให้ไม่สม่ำเสมอ
- micro-optimization ที่ profile แล้วไม่ช่วย → อย่าใส่ `useMemo` / `computed` ที่ไม่จำเป็น
- abstraction ที่ "ดูสะอาด" แต่ทำให้ debug ยากขึ้น → simple = better

แจ้งผู้ใช้เสมอเมื่อ propose พังของเดิมขนาดใหญ่ ให้เลือกก่อนลงมือ

---

## Quality gates (mandatory ก่อนปิดงาน — ห้ามเคลม "เสร็จ" ก่อนผ่าน)

### Build / verify gates (ถ้าแก้โค้ด)

- [ ] **`tsc --noEmit`** ผ่าน 0 errors
- [ ] **Vite compile** ทุกหน้า/component ที่แตะ — `curl http://localhost:3000/<page>` HTTP 200 + ดู dev log ไม่มี `Invalid end tag`, `SelectItem must have a value prop`, ฯลฯ
- [ ] **`rtk proxy yarn nuxt prepare`** สำเร็จ (refresh auto-imports + types)

### UI verify (mandatory เมื่อมี UI เปลี่ยน — ก่อนเคลม "เสร็จ")

- [ ] รัน `verify` skill — เปิด browser หน้าที่แก้ ทดสอบ golden path จริงๆ
- [ ] ทดสอบ edge case ≥ 2 จาก spec (เช่น empty state, error state)
- [ ] เช็ค network tab ไม่มี 4xx/5xx ที่ไม่ตั้งใจ
- [ ] ไม่มี console error ที่เป็น regression จากงานนี้
- [ ] เช็ค mobile breakpoint (375px) ไม่แตก

ถ้า dev server ไม่พร้อม / verify เองไม่ได้ → แจ้ง user ตรงๆ ว่า "verify ด้วยตนเองไม่ได้ — กรุณาทดสอบ: [list golden path steps]" **ห้ามเคลม "เสร็จ" เงียบๆ**

### Pattern verification (ถ้า scan / migrate / refactor)

- [ ] **Cross-verify ≥ 2 regex patterns** — หลวม + เข้ม ผลต้องตรงกัน
  - หลวม: `<tag` ไม่ติด trailing char (กัน multi-line attributes ที่ตามด้วย newline)
  - เข้ม: `<tag[\s>]` (regex ที่บังคับ whitespace/`>`)
  - ถ้าผลไม่เท่า = pattern เข้มผิด
- [ ] **Manual spot-check 2-3 ไฟล์** — อ่านไฟล์จริงยืนยันผล scan ก่อนเคลม "0 left"
- [ ] **Reka UI item value** — ถ้าใช้ USelect/USelectMenu items: scan **ทั้ง single + double quote** หา `value: ""` / `value: ''` (ดู `feedback_select_item_value_empty_string.md`)

### Ripple verification (ถ้าแก้ shared code)

- [ ] **Trace caller ≥ 1 hop** ก่อนเคลม "ไม่กระทบใคร" / "dead code"
- [ ] **Type usage trace** — ทุก consumer ของ type/schema ที่แก้ ยัง compile + behavior ถูก
- [ ] **Migration ของ wrapper element** — ลบ wrapper `<div>` open + close พร้อมกัน ห้ามลบฝั่งเดียว (ดู `feedback_dangling_tag_after_wrapper_removal.md`)

### Memory update

- [ ] **บันทึก project memory** ถ้าเจอ pattern/bug/anti-pattern ใหม่ที่เฉพาะ project — เพิ่ม `feedback_<topic>.md` + ลิงก์ใน `MEMORY.md`
- [ ] **Update skill learnings** ที่ `~/.claude/skills/fe/learnings.md` ถ้าเจอบทเรียนที่ generalize ข้าม project (Vue reactivity pitfall, TypeScript pattern, Nuxt UI quirk ที่ใช้ได้กับ project อื่น) — append entry ตาม format ในไฟล์
- [ ] ถ้า user ต้องสั่ง "ชัวไหม / ตรวจอีกรอบ / ยังเจอ X" = scan/verify รอบแรกไม่ดีพอ → memo + ปรับ pattern ทันที

### กฎทอง

> **Vite compile success + dev log clean = source of truth** สำหรับ template/runtime
> **`tsc --noEmit` 0 errors = source of truth** สำหรับ type
> **regex heuristic ไม่ใช่ source of truth** — multi-line construct (self-closing div, JSX-like) ทำให้ count เพี้ยน

ห้ามเคลม "0 left / ครบ / เสร็จ" จาก scan รอบเดียว — verify หลายมุมก่อนเสมอ
