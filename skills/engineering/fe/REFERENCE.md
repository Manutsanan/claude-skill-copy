# fe — Reference (syntax, examples, tables)

> โหลดเมื่อต้องการ syntax/example จริงๆ — ไม่โหลดอัตโนมัติพร้อม SKILL.md

---

## Contents

- [#valibot](#valibot) — schema, pipe actions, parse vs safeParse
- [#nuxt-ui](#nuxt-ui) — component replacement table, `UForm` + valibot pattern
- [#react](#react) — React/Next patterns (when project is not Nuxt)
- [#nuxt-directory](#nuxt-directory) — v3 vs v4 directory map
- [#nuxt-auto-imports](#nuxt-auto-imports) — what NOT to import (auto-imported)
- [#nuxt-state](#nuxt-state) — `useState` vs Pinia, localStorage guard
- [#nuxt-data-fetching](#nuxt-data-fetching) — `useFetch` / `useAsyncData` / `$fetch`, v3 vs v4 reactivity
- [#nuxt-routing](#nuxt-routing) — `navigateTo`, middleware, `definePageMeta`
- [#nuxt-server](#nuxt-server) — `defineEventHandler`, body/query/param, `createError`
- [#nuxt-ssr](#nuxt-ssr) — `import.meta.client/server`, `<ClientOnly>`, SEO/head

---

## #valibot

valibot ใช้ pipe-based (ต่างจาก zod chain) — import เฉพาะที่ใช้ (tree-shake friendly, ~10x เล็กกว่า zod)

```ts
import * as v from "valibot";
// หรือ named imports
import { object, string, pipe, minLength, email, safeParse } from "valibot";
```

**Schema example:**
```ts
const UserSchema = v.object({
  id: v.pipe(v.string(), v.uuid()),
  email: v.pipe(v.string(), v.email("อีเมลไม่ถูกต้อง")),
  age: v.pipe(v.number(), v.minValue(18, "ต้องอายุ 18+")),
  role: v.picklist(["admin", "staff", "user"]),
  tags: v.array(v.string()),
  meta: v.optional(v.object({ note: v.string() })),
});
type User = v.InferOutput<typeof UserSchema>;
type UserInput = v.InferInput<typeof UserSchema>;
```

**Pipe actions:**
- string: `minLength`, `maxLength`, `length`, `email`, `url`, `uuid`, `regex`, `trim`, `toLowerCase`, `nonEmpty`
- number: `minValue`, `maxValue`, `integer`, `multipleOf`, `finite`
- array: `minLength`, `maxLength`, `length`, `nonEmpty`
- transform: `transform((v) => v.trim())`
- custom: `check((v) => predicate, 'message')`

**Parse vs safeParse:**
- `v.parse(schema, data)` — throw ถ้า invalid (ใช้ใน server route)
- `v.safeParse(schema, data)` — return `{ success, output } | { success: false, issues }` (ใช้ใน boundary ที่ต้อง handle error)

---

## #nuxt-ui

**Component replacement table:**

| ใช้ | แทน |
|---|---|
| `UButton` | `<button>` |
| `UInput` / `UTextarea` / `USelect` / `USelectMenu` | `<input>` / `<textarea>` / `<select>` |
| `UCheckbox` / `URadioGroup` / `USwitch` | `<input type=checkbox/radio>` |
| `UForm` + `UFormField` | `<form>` + label/error markup เอง |
| `UModal` / `USlideover` / `UDrawer` | overlay ทำมือ |
| `UCard` | wrapper border + shadow |
| `UTable` | `<table>` ทำเอง |
| `UBadge` / `UChip` | span สี |
| `UAlert` | banner ทำเอง |
| `UTooltip` / `UPopover` / `UDropdownMenu` | hover/click overlay |
| `UPagination` | next/prev ทำเอง |
| `UTabs` / `UAccordion` | tab/accordion ทำเอง |
| `UToast` (`useToast()`) | alert() / banner |
| `UIcon` (Iconify) | inline SVG / icon font |

**UForm + valibot pattern:**
```vue
<script setup lang="ts">
import * as v from "valibot";
import type { FormSubmitEvent } from "@nuxt/ui";

const LoginSchema = v.object({
  username: v.pipe(v.string(), v.nonEmpty("กรอกชื่อผู้ใช้")),
  password: v.pipe(v.string(), v.minLength(6, "อย่างน้อย 6 ตัวอักษร")),
});
type LoginInput = v.InferInput<typeof LoginSchema>;

const state = reactive<Partial<LoginInput>>({ username: "", password: "" });

async function onSubmit(event: FormSubmitEvent<LoginInput>) {
  await login(event.data);
}
</script>

<template>
  <UForm :schema="LoginSchema" :state="state" class="space-y-4" @submit="onSubmit">
    <UFormField label="ชื่อผู้ใช้" name="username">
      <UInput v-model="state.username" />
    </UFormField>
    <UFormField label="รหัสผ่าน" name="password">
      <UInput v-model="state.password" type="password" />
    </UFormField>
    <UButton type="submit" block>เข้าสู่ระบบ</UButton>
  </UForm>
</template>
```

---

## #react

React patterns (ใช้เมื่อ project เป็น React/Next — ไม่ใช่ Nuxt):

- **`useEffect` dependency** — ใส่ครบ; `[]` สำหรับ mount-only เท่านั้น
- **derived state** — คำนวณตรงๆ ใน render หรือ `useMemo`; อย่า sync ผ่าน `useEffect`
- **memoization** — ใส่ `useMemo`/`useCallback` เมื่อ profile แล้ว slow หรือเป็น dep ของ effect เท่านั้น
- **lift state up** — ลอง lift ไป common parent ก่อนใช้ context/store
- **server vs client component** (Next.js App Router) — default server; `'use client'` เฉพาะที่ต้อง interactivity

---

## #nuxt-directory

Path ของ Nuxt 4 (มี `app/` prefix) — ถ้า Nuxt 3 classic ตัด `app/` ออก:

| Dir (v4) | Dir (v3 classic) | Purpose | Auto |
|---|---|---|---|
| `app/pages/` | `pages/` | file-based routing | route auto |
| `app/layouts/` | `layouts/` | shared shell | `definePageMeta({ layout })` |
| `app/components/` | `components/` | components | auto-import (PascalCase, nested = prefix) |
| `app/composables/` | `composables/` | `use*` functions | auto-import |
| `app/middleware/` | `middleware/` | route guards | named or `.global.ts` |
| `app/plugins/` | `plugins/` | runtime plugin | `.client.ts`/`.server.ts` ต่อท้าย |
| `app/utils/` | `utils/` | pure helper | auto-import |
| `app/assets/` | `assets/` | bundled assets (SCSS, fonts) | import path |
| `public/` | `public/` | static (served at `/`) | URL `/foo.png` |
| `server/api/` | `server/api/` | API routes | auto `/api/*` |
| `server/routes/` | `server/routes/` | non-`/api` server routes | auto |
| `server/middleware/` | `server/middleware/` | server-side middleware | auto run ทุก request |
| `shared/` | `shared/` (v3.10+) | type/util client+server | import via `#shared` |

---

## #nuxt-auto-imports

**ห้ามเขียน import** สิ่งเหล่านี้ (auto):
- Vue: `ref`, `reactive`, `computed`, `watch`, `watchEffect`, `onMounted`, `onUnmounted`, `nextTick`, `shallowRef`, `triggerRef`
- Nuxt: `useState`, `useFetch`, `useAsyncData`, `useRoute`, `useRouter`, `useRuntimeConfig`, `useCookie`, `useHead`, `useSeoMeta`, `navigateTo`, `createError`, `defineNuxtConfig`, `defineNuxtPlugin`, `defineEventHandler`, `defineNuxtRouteMiddleware`
- Component ใน components dir — ใช้ tag ตรงๆ (PascalCase) ใน template
- Composable ใน composables dir — เรียกตรงๆ
- Util ใน utils dir — เรียกตรงๆ

**Type imports:** `import type { Foo } from '#shared/types'`

---

## #nuxt-state

- **`useState(key, init)`** — SSR-safe shared ref. ตัวเลือกแรกสำหรับ shared business state. **key ต้อง unique ทั่วแอป** (ชนกัน = ค่ากระโดด). `init` เป็น function (กัน serialize on SSR)
- **`useState` vs Pinia** — `useState` พอ 80%; ใช้ Pinia เมื่อ (1) ต้อง persist (`pinia-plugin-persistedstate`), (2) action/getter ซับซ้อน, (3) state graph ใหญ่ที่ต้อง devtools tracing
- **localStorage** — wrap `import.meta.client` เสมอ; ห้ามอ่าน `localStorage` ตอน SSR

---

## #nuxt-data-fetching

- **`useFetch(url)`** — wrapper บน `useAsyncData` + `$fetch` (URL เป็น key auto)
- **`useAsyncData(key, fn)`** — logic ซับซ้อนกว่า fetch URL เดียว
- **`$fetch(url)`** — imperative (event handler, server route) — **ไม่** SSR-cache, ไม่ dedupe
- **`server: false`** — เลี่ยง SSR fetch (data ต้อง auth client-side)
- **`lazy: true`** — ไม่ block navigation, render UI ก่อน data
- **`watch: [refs]`** — refetch เมื่อ ref เปลี่ยน
- **Error:** `const { data, error, status, refresh } = await useFetch(...)`; status: `'idle' | 'pending' | 'success' | 'error'`

**v3 vs v4 — `data` reactivity:**
- **Nuxt 3 classic:** `data` = **deep reactive** ref — mutate field ลึก trigger re-render
- **Nuxt 4 (หรือ v3 + `compatibilityVersion: 4`):** `data` = **shallow ref** — mutate ลึก **ไม่** trigger; ต้อง assign object ใหม่ (`data.value = { ...data.value, user: { ...data.value.user, name: 'X' } }`)
- Deep ใน v4 → pass `{ deep: true }` เข้า options
- Pattern เก่า `data.value.someField = x` ใน v3 → เขียนใหม่ใน v4 หรือ opt-in

---

## #nuxt-routing

- **Dynamic:** `pages/counter/[id].vue` → `useRoute().params.id`
- **Catch-all:** `[...slug].vue` → array of segments
- **`navigateTo(path)`** — ใช้แทน `router.push` (SSR redirect: `{ redirectCode: 302 }`)
- **`definePageMeta({ middleware: 'auth', layout: 'admin' })`** — page-level config
- **Middleware:** `defineNuxtRouteMiddleware((to, from) => { ... })` — return `navigateTo()` / `abortNavigation()` / `undefined`

---

## #nuxt-server

- **File-based:** `server/api/users/[id].get.ts` → `GET /api/users/:id`
- **`defineEventHandler(async (event) => { ... })`**
- **body:** `await readBody(event)` (POST/PUT/PATCH)
- **query:** `getQuery(event)`
- **param:** `getRouterParam(event, 'id')`
- **throw:** `throw createError({ statusCode: 400, statusMessage: 'ข้อความไทย' })`
- **runtime config:** `useRuntimeConfig()` (server มี private + public; client เห็นแค่ `public`)

---

## #nuxt-ssr

- ห้ามเรียก `window`, `document`, `localStorage`, `navigator` ตอน setup โดยไม่ guard
- ใช้ `import.meta.client` / `import.meta.server` (Nuxt 3.10+) แทน `process.client`
- `<ClientOnly>` wrap ส่วน render เฉพาะ client (gauge, chart)
- `onMounted()` รันเฉพาะ client เสมอ — logic ที่ต้องการ DOM
- date/time/random ที่ต่างระหว่าง server กับ client → คำนวณใน `onMounted` หรือ `<ClientOnly>`

**SEO/head:**
- `useSeoMeta({ title, description, ogImage })` — type-safe กว่า `useHead`
- `useHead({ link, script })` — สำหรับ tag อื่น
