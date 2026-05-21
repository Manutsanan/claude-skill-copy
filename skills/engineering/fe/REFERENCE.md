# fe — Reference (syntax, examples, tables)

> โหลดเมื่อต้องการ syntax/example จริงๆ — ไม่โหลดอัตโนมัติพร้อม SKILL.md

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
