# Learnings — debug

> **Per-skill, cross-project memory** — บทเรียนของ skill `debug` ที่ใช้ได้ข้ามทุก project (Bug diagnosis & fix)
>
> **เก็บอะไรที่นี่:**
> - Symptom → root cause mapping ที่ generalize ข้าม project (เช่น `SelectItem must have a value prop that is not an empty string` → items array มี `value: ''`)
> - Framework-specific bug pattern (Vue reactivity loss, Nuxt hydration mismatch, Pinia store re-init)
> - Console error message ที่ misleading + วิธี trace จริง
> - Debug technique ที่ work เป็นพิเศษกับ stack นี้ (Vue Devtools tip, network panel filter, source map config)
> - Anti-pattern ในการ debug ที่เคยพลาด (แก้ symptom ไม่แก้ root cause, ลืม scan ripple)
>
> **ไม่เก็บที่นี่:**
> - Bug เฉพาะ business logic ของ project (อันนั้น → project memory)
> - Fix commit แบบ one-shot ที่ไม่ใช่ pattern (อันนั้น git log มี)
>
> **เมื่อไหร่อ่าน:** ทุกครั้งใน Pre-flight ของ skill `debug` — grep ด้วย keyword จาก error message หรือ symptom
> **เมื่อไหร่ append:** หลังจบงานถ้า root cause เป็น pattern ที่ generalize ได้ (ดู format ด้านล่าง)

---

## Format ต่อ entry (เน้น symptom → root cause)

```markdown
## <kebab-case-symptom-slug>

**Tags:** framework, component, error-type, ...
**Date:** YYYY-MM-DD

**Symptom:** อาการที่ผู้ใช้/console เห็น (1 บรรทัด)
**Root cause:** สาเหตุจริง (ไม่ใช่ symptom)
**Fix pattern:** วิธีแก้ที่ใช้ได้กับ pattern เดียวกัน
**Detection:** วิธีหา bug นี้ (grep pattern, devtools step, log location)
```

---

## Entries

<!-- ใหม่สุดอยู่บน -->

## ssr-cannot-read-getSSRProps-undefined-directive

**Tags:** nuxt3, vue3, ssr, custom-directive, migration
**Date:** 2026-05-20

**Symptom:** SSR crash: `Cannot read properties of undefined (reading 'getSSRProps')` — page fails to render server-side
**Root cause:** A custom directive (e.g. `v-guard`) is applied in a template but was **never registered** via plugin. During SSR, Vue resolves the directive name → gets `undefined` → tries `undefined.getSSRProps(...)` → throws. No optional chaining protects this call.
**Fix pattern:**
1. Create `directives/<name>.ts` with the directive logic + add `getSSRProps: () => ({})` for SSR no-op
2. Register via `plugins/<name>.ts`: `nuxtApp.vueApp.directive("name", directive)`
3. Plugin does NOT need `.client.ts` suffix — `mounted`/`unmounted` hooks auto-skip on server; `getSSRProps` handles the server render path

```ts
// directives/inputGuard.ts
export default {
  getSSRProps: () => ({}),  // ← required for SSR compatibility
  mounted(el, binding) { ... },
  unmounted(el) { ... },
}

// plugins/inputGuard.ts
import inputGuard from "../directives/inputGuard"
export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive("guard", inputGuard)
})
```
**Detection:**
- Grep for `v-<name>` in templates, then grep `directive("<name>"` in plugins — if no match, directive is unregistered
- Error always says `getSSRProps` specifically → points to directive, not component


## thai-api-name-field-localized

**Tags:** api-mapping, thailand, composable, dropdown, Select
**Date:** 2026-05-20

**Symptom:** Dropdown แสดง badge/code ถูกต้อง แต่ text ชื่อข้างๆ ว่างเปล่า — บาง field แสดง บาง field ไม่แสดง
**Root cause:** Thai API convention แยก localized fields ออกจากกัน — ไม่ใช่ `name` เดียว:
- `name_th` = ชื่อเต็มภาษาไทย
- `name_abb_th` = ชื่อย่อภาษาไทย
- `name_en` = ชื่อเต็มภาษาอังกฤษ
- `code` = รหัส (ใช้เป็น headerName badge)

การ map `name: item.name` จะได้ undefined → text ว่าง
**Fix pattern:**
```ts
// ❌ สมมติ field name เอง
{ id: item.id, name: item.name }

// ✅ ดู v2 model/composable ก่อน
{ id: item.id, name: item.name_th, headerName: item.code }
```
**Detection:**
- เปิด dropdown → badge/code แสดง แต่ text ชื่อว่าง = `name` field ผิด
- ดู `models/<domain>/<entity>.model.ts` ใน v2 หา field จริง
- ดู `composables/api/<entity>.ts` ใน v2 ดูว่า map field ไหน


## api-empty-array-overwrites-fallback

**Tags:** vue3, composable, fallback, api-mapping, defensive-coding
**Date:** 2026-05-20

**Symptom:** Fallback data แสดงผลตอนแรกถูกต้อง แต่หายไปหลัง API call — dropdown กลายเป็นว่าง
**Root cause:** `if (res.data)` เป็น `true` สำหรับ empty array `[]` (truthy ใน JavaScript) → overwrite fallback ด้วย `[].map(...)` = `[]`
**Fix pattern:**
```ts
// ❌ ใช้ if (res.data) — overwrite fallback ด้วย []
if (res.data) {
  list.value = res.data.map(...)
}

// ✅ ตรวจ length ก่อนเสมอ
if (res.data?.length > 0) {
  list.value = res.data.map(...)
}
```
**Detection:**
- Dropdown แสดงข้อมูล → เปล่า หลัง API call เสร็จ
- console.log `res.data` → `[]` แต่ fallback ถูก overwrite
**Related:** [[thai-api-name-field-localized]]

## duplicate-api-call-from-composable-side-effect-race

**Tags:** vue3, nuxt, composable, side-effect, race-condition, singleton, fetch-dedup
**Date:** 2026-05-20

**Symptom:** API endpoint ถูกเรียก 2 ครั้งติดกัน (เห็นใน Network tab DevTools) ตอน user navigate ไปหน้าที่ใช้ middleware/auth — ทั้งสอง call status 200 ใช้เวลาใกล้กัน (เช่น 108ms + 88ms)
**Root cause:** **Composable factory มี side-effect ที่ schedule API call แบบ async** (เช่น `nextTick(async () => { await setTimeout(100); await fetchProfile() })`) — race กับ caller (middleware) ที่เรียก API ตัวเดียวกันพร้อมกัน. **In-flight promise guard เสีย** เพราะ assign `promise = (async () => {})()` ทุก call ไม่ check ของเดิม → ไม่ dedupe
**Fix pattern:**
- **True singleton guard:** `if (inFlightPromise) return inFlightPromise` ก่อน assign ใหม่
  ```ts
  const fetchProfile = async () => {
    if (inFlightPromise) return inFlightPromise   // ← reuse in-flight
    inFlightPromise = (async () => { ... })()
    try { return await inFlightPromise }
    finally { inFlightPromise = null }
  }
  ```
- **ลบ initial fetch จาก factory side-effect** — ปล่อยให้ caller (middleware/page setup) เป็นคนรับผิดชอบ initial fetch; watcher ใน factory มีไว้สำหรับ event-driven check (focus/visibility/interval) เท่านั้น
- **Early return** ถ้า state มีอยู่แล้ว — เช่น `if (store.userInfo?.id && currentUserId === lastUserId) return true`
- หลีกเลี่ยง pattern `await fetch(); if (!data) await fetch()` — ถ้า call แรก fail, call ที่ 2 ก็ fail ด้วยเหตุผลเดียวกัน
**Detection:**
- เปิด DevTools → Network → Fetch/XHR → ดู endpoint เดียวกันที่ถูกเรียกหลายครั้งใน timeline ใกล้กัน
- Trace caller flow: middleware/route guard, composable factory, component mount, watcher initial check — โดยเฉพาะ `setTimeout` / `nextTick` ใน factory ที่ schedule fetch async
- ตรวจ in-flight promise variable ว่ามี `if (promise) return promise` ก่อน assign ใหม่ไหม

## invalid-end-tag-vue-template

**Tags:** vue3, template, compiler-error, migration, wrapper
**Date:** 2026-05-16

**Symptom:** Vite/Vue compiler error: `Invalid end tag` หรือ `Element is missing end tag` มัก point ไปที่ `</template>` บรรทัดท้ายไฟล์ (misleading — บรรทัดที่ error ระบุ ไม่ใช่จุดที่ผิดจริง)
**Root cause:** ลบ wrapper element (`<div class="container">...</div>`) **ฝั่งเดียว** — เปิดยังอยู่แต่ปิดถูกลบ (หรือกลับกัน) → Vue compiler นับ nesting ไม่ตรง → bubble error ขึ้นจนถึง `</template>`
**Fix pattern:**
- ลบ wrapper เปิด-ปิด **พร้อมกัน** เสมอ (เลือก match pair ก่อนลบ)
- ถ้า migrate `<div>` → `<UCard>` → search-replace ทั้งคู่ในรอบเดียว ไม่ใช่ทีละบรรทัด
- ใช้ formatter (Prettier/Volar) reformat ก่อน commit — indent ผิดจะเด่นชัดเมื่อ pair ขาด
**Detection:**
- Grep ไฟล์หา `<div`, `<template`, `<UCard` count ต้อง = `</div`, `</template`, `</UCard` count
- เช็คใน Vue devtools / Volar inline diagnostic — มัก highlight tag ที่ unmatched
- ถ้า error message point ไปที่ `</template>` บรรทัด last → search backward หา wrapper ล่าสุดที่แก้

## select-item-empty-string-value-throws

**Tags:** nuxt-ui, reka-ui, USelect, USelectMenu, runtime-throw
**Date:** 2026-05-16

**Symptom:** Runtime error: `SelectItem must have a value prop that is not an empty string` ตอน component mount — error ขึ้นจาก Reka UI internals (stack ไม่ชี้ไป items array โดยตรง)
**Root cause:** `items` array ของ `USelect` / `USelectMenu` มี element ที่ `value: ''` (empty string) — Reka UI สงวน `''` เป็น sentinel ของ "no selection"
**Fix pattern:**
- เปลี่ยน `value: ''` → `value: null` หรือ `value: undefined` (ถ้า component handle ได้)
- ถ้าต้องการ "All / ทุกค่า" option → ใช้ string sentinel เช่น `'__ALL__'` แล้ว map กลับเป็น undefined ใน computed
- ตอน migrate native `<select><option value="">...</option></select>` → ห้าม map straight เป็น `{ value: '' }` 
**Detection:**
- Grep cross-pattern (ทั้ง single + double quote): `rg "value:\s*['\"]['\"]" --type ts --type vue`
- Console error ใน dev → Reka UI throw → ดู component tree หา `USelect` ที่ active ในหน้านั้น

## multi-tab-reload-loop-on-401

**Tags:** auth, reload-loop, location-reload, session, multi-tab
**Date:** 2026-05-16

**Symptom:** หน้ากระพริบ / reload ตัวเองวนซ้ำหลายครั้งจนเบราว์เซอร์ค้าง — เกิดบ่อยตอน session หมดอายุ
**Root cause:** ใน 401 error handler เรียก `location.reload()` → page reload → request เดิมถูกยิงซ้ำ → 401 อีก → reload อีก → loop
**Fix pattern:**
- 401 handler ห้าม `location.reload()` — redirect ไป `/login` ด้วย `router.push('/login')` หรือ `navigateTo('/login')` แทน
- ถ้าต้อง refresh data หลัง re-auth → ใช้ `refresh()` ของ `useFetch` หรือ invalidate Pinia store เฉพาะที่ ไม่ใช่ reload ทั้งหน้า
- ตั้ง guard: ตรวจ `route.path` ก่อน redirect — ถ้าอยู่ `/login` แล้ว ห้าม redirect ซ้ำ (กัน infinite ในกรณี login page เองคืน 401)
**Detection:**
- Network tab → request เดิมยิงซ้ำในช่วงสั้น ๆ
- Grep `location.reload()` ใน auth handler / interceptor / middleware
- Console: เห็น 401 response loop + "Navigation cancelled" warning จาก Vue Router

