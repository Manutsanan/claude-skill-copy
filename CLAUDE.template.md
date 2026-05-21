@RTK.md

# Universal Phase 0 — ทุก task ทุก project ทุกคำสั่ง

> **กฎสากลที่บังคับใช้ก่อนทุกอย่าง** — ไม่ว่า task ใหญ่/เล็ก, ไม่ว่าจะเรียก skill หรือไม่, ไม่ว่าอยู่ project ไหน
>
> Phase 0 นี้คือ **layer ฐาน** ของระบบ — ถ้า task เรียก skill, Phase 0 ของ skill นั้นจะ **extend** (เพิ่ม skill learnings) ไม่ใช่ replace

## 1. Load memory hierarchy (mandatory — ทำเป็นอันแรกเสมอ)

โหลดตามลำดับ 2 ชั้น (global → project):

### Global memory — `~/.claude/memory/MEMORY.md`
- Cross-project lessons + user preference + workflow convention ที่ใช้ทุก project
- ถ้ามีไฟล์ → filter entries ที่ `metadata.scope: global` + relevant กับงาน
- ถ้าไม่มี → ข้าม + หมายเหตุใน reasoning

### Project memory — `~/.claude/projects/<id>/memory/MEMORY.md`
- `<id>` = working directory แปลงเป็น project id โดยแทน `/` ด้วย `-`
  - working dir `/Users/X/Project/Y` → id `-Users-X-Project-Y`
  - working dir `/Users/X` (home) → id `-Users-X`
- Project-specific patterns, history, finding, constraint
- ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory"

### Phase checkpoint — `~/.claude/projects/<id>/memory/project_phase_checkpoint_*.md`
- หลังโหลด project memory → scan ไฟล์ที่ชื่อ `project_phase_checkpoint_*.md` ใน folder เดียวกัน
- ถ้าเจอ checkpoint ที่ `status: in_progress` → echo ให้ user เห็น + ถามว่าจะ **resume** (โหลด artifact จาก checkpoint ต่อ) หรือ **เริ่มใหม่** (mark checkpoint เป็น `abandoned`)
- ถ้าไม่มี checkpoint หรือทุก checkpoint เป็น `status: complete` → ข้าม

## 2. Echo & Conflict check

- Echo top 3-5 entries ที่ relevant กลับให้ user เห็น **ก่อน** เริ่มงาน — format บังคับ: `[type] slug — one-line hook` **ห้ามเกิน 1 บรรทัดต่อ entry ห้าม quote body ของ entry**
- ถ้า memory บอกเคยทำผิด → ระบุชัดว่าจะหลีกเลี่ยงยังไง (1 บรรทัด)
- ถ้า propose สิ่งที่ขัด memory → **หยุดถาม user ก่อน** อย่าทำเงียบๆ
- ถ้าไม่มี memory เกี่ยวข้องเลย → หมายเหตุสั้น "ไม่มี memory ตรง — fresh start"

## 2.5 Token efficiency (mandatory — ใช้ทุก skill ทุก turn)

- **Quality gate output:** แสดงเฉพาะ item ที่ **fail**; ถ้าทุกข้อผ่าน → `✅ quality gates passed` (1 บรรทัด) ห้ามแสดง checklist เต็มเมื่อไม่มี failure
- **Handoff output:** สรุปเป็น bullet ≤ 10 จุด; ถ้า artifact ยาว → compress เป็น key-value ไม่ใช่ prose
- **Shell commands:** `yarn` และ `npm` ไม่ถูก RTK filter อัตโนมัติ → ใช้ `rtk proxy yarn ...` / `rtk proxy npm ...` เสมอ; `pnpm` ใช้ `rtk proxy pnpm ...` เช่นกัน

## 3. Evaluate decision matrix → เลือก skill

ดูตาราง "Quick decision matrix" ใน Skill orchestration section ด้านล่าง:
- จับคู่ intent ของ user กับ skill ที่เหมาะสม
- เข้าข้อยกเว้น (config / docs / typo / คำถามทั่วไป) → ไม่เรียก skill, ทำตรงๆ
- เรียก skill → skill จะทำ **Phase 0.5** เพิ่มเอง (load `~/.claude/skills/<skill>/learnings.md`)

## 4. Universal save triggers (mandatory — บังคับ save ระหว่าง turn)

Save memory **ทันที** ไม่รอ user สั่ง ไม่รอจบ session เมื่อเจอเหตุการณ์เหล่านี้:

1. **User แก้ทาง / บอกผิด** — ("ไม่ใช่แบบนั้น", "เปลี่ยนเป็น...", "stop") → save `feedback_*` + **Why** + **How to apply**
2. **User confirm pattern ที่ไม่ obvious** — ("ใช่ ถูกแล้ว", accept approach แปลกๆ โดยไม่ push back) → save ว่า validated
3. **เจอ error / ข้อผิดพลาด ทุกประเภท** — runtime, type, logic, approach ล้มเหลว → save root cause + วิธีที่ถูก
4. **งานสำเร็จด้วย approach ใหม่ที่ใช้ได้จริง** → save pattern ที่ใช้ซ้ำได้
5. **เจอ bug ที่หาที่มาได้** → save root cause + ripple list (ทุกไฟล์ที่อาจซ้ำ pattern)
6. **เจอ constraint ที่ไม่ได้อยู่ในโค้ด** — "API rate limit X", "field deprecated" → save `project_*`
7. **แก้ pattern เดิมซ้ำ ≥ 2 ครั้ง** ในงานเดียว — แก้ซ้ำ = ต้อง save แล้ว
8. **เมื่อ session ยาว** (> 20 turn หรือโหลดไฟล์ขนาดใหญ่หลายไฟล์ติดกัน) → save lesson ที่ค้างอยู่ทันที อย่ารอ compact ก่อน เพราะเมื่อ compact เกิดขึ้นแล้วสาย
9. **หลัง pipeline phase เสร็จ** (sa / ux / fe จบแต่ละ phase) → save phase artifact ลง project memory ก่อน handoff ด้วยรูปแบบ:
   - **ชื่อไฟล์:** `project_phase_checkpoint_<phase>_YYYY-MM-DD.md` (เช่น `project_phase_checkpoint_sa_2026-05-20.md`)
   - **frontmatter:** `phase: sa|ux|fe` + `status: in_progress` → เปลี่ยนเป็น `complete` เมื่อ handoff เสร็จแล้ว
   - **content:** artifact หลักที่ phase ถัดไปต้องใช้ — spec สำหรับ ux, design plan สำหรับ fe, implementation summary สำหรับ verify

### Save ไปที่ไหน?

| Lesson ประเภท | ปลายทาง |
|---|---|
| User behavior / preference / cross-project rule | **Global** `~/.claude/memory/` |
| Project-specific pattern / finding / constraint | **Project** `~/.claude/projects/<id>/memory/` |
| Skill-internal pitfall (Vue reactivity, Tailwind JIT, OWASP pattern) ที่ใช้ได้ทุก project | **Skill learnings** `~/.claude/skills/<skill>/learnings.md` |
| ขัดกับ rule ที่อยู่ใน CLAUDE.md แล้ว | **ไม่ save** — restate ซ้ำ = ขยะ |

## 5. Skip rules (เมื่อข้าม Phase 0 ได้บางส่วน)

- **Trivial conversational task** (ทักทาย, ถาม CLI flag, ขอ explanation 1 บรรทัด): glance MEMORY.md เร็วๆ — ถ้าไม่มี entry relevant ก็ตอบได้เลยโดยไม่ต้อง echo
- **Task ที่ touch code / file / shared state**: ห้าม skip — บังคับ load + echo เต็มขั้นตอน

ห้าม skip เพราะ "งานเล็กไม่น่าจะมี memory" — bug เกิดบ่อยที่สุดตรงงานที่คิดว่าเล็ก

---

# Skill orchestration — sa / ux / fe + migrate / debug

โปรเจกต์ frontend ทุกตัวใช้ skill 3 ตัวประสานกันเป็น pipeline หลัก — `sa` (คิดก่อน) → `ux` (ออกแบบ) → `fe` (เขียนโค้ด) — เสริมด้วย 2 skill เฉพาะทาง:
- **`migrate`** — bulk transformation หลายไฟล์ (legacy → new pattern)
- **`debug`** — diagnose runtime error / unexpected behavior, หา root cause ไม่ใช่ symptom

ทุก section ด้านล่างทำงานร่วมกันเป็นระบบเดียว ไม่ใช่ rule แยกอิสระ

---

## Quick decision matrix

| Intent ของผู้ใช้ | Skill ที่ต้องเรียก | ลำดับ |
|---|---|---|
| "วิเคราะห์ / ตรวจ / audit / หา bug / หาช่องโหว่ / spec ระบบ" | `sa` | เดี่ยว |
| "ปรับสี / spacing / animation / responsive / accessibility" (visual ล้วน) | `ux` | เดี่ยว |
| "debug reactivity / refactor logic / แก้ schema / state ไม่ทำงาน" (logic ล้วน) | `fe` | เดี่ยว |
| "redesign + refactor หน้านี้ (มี spec ชัดแล้ว)" | `ux` → `fe` | 2 ขั้น |
| "implement หน้าใหม่จาก mockup" | `ux` → `fe` | 2 ขั้น |
| "วิเคราะห์ requirement + ทำหน้าใหม่" | `sa` → `ux` → `fe` | 3 ขั้น |
| "เพิ่ม feature ใหม่ที่ยังไม่รู้ field/flow" | `sa` → `ux` → `fe` | 3 ขั้น |
| "ตรวจ security flow แล้ว fix" | `sa` → `fe` | 2 ขั้น (ข้าม ux) |
| "วิเคราะห์ bug แล้วแก้" | `sa` → `fe` | 2 ขั้น (ข้าม ux) |
| "เจอ error / runtime crash / X พัง / X ไม่ทำงาน + มี error stack" | `debug` | เดี่ยว |
| "debug แล้วต้องการ redesign data model" | `debug` → `sa` → `fe` | 3 ขั้น |
| "migrate / แปลง / refactor หลายไฟล์ตาม pattern" (เช่น native select → USelect) | `migrate` | เดี่ยว |
| "migrate ที่ต้องเปลี่ยน data shape" | `sa` → `migrate` | 2 ขั้น |
| คำสั่งสั้น / กำกวม / intent ไม่ชัดว่าต้องการ spec / design / code / ไม่รู้จะเริ่มขั้นไหน | ไม่เรียก skill | ถามก่อน 1 คำถาม แล้วกลับมาเลือก pipeline |
| "config / package.json / docs / typo" | ไม่เรียก skill ใด | — |

**กฎสากล:**
- ลำดับ `sa → ux → fe` **ห้ามสลับ** — spec ต้องเสร็จก่อน design, design ต้องเสร็จก่อน code
- ขั้นที่ skip ได้ คือขั้นที่ **input ของขั้นนั้นมีอยู่แล้ว** (เช่น มี spec ชัด → skip sa; ไม่มี UI เปลี่ยน → skip ux)
- ทุกขั้นต้อง **handoff artifact ที่ขั้นถัดไปใช้ได้จริง** (ดู Handoff contracts ด้านล่าง)
- **ถ้าไม่มีแถวตรง** — ถามก่อน 1 คำถาม: "ต้องการ [spec / design / implement] หรือเริ่มจากขั้นไหน?" อย่าเดาแล้วเลือก pipeline ผิด

---

## Trigger ของแต่ละ skill

### `sa` — System Analyst + Security Audit (คิดก่อนเขียน / ตรวจหลังเขียน)

เรียกเมื่อ:
- ผู้ใช้พูดถึง: วิเคราะห์, วิเคราะห์โปรเจ็ค, วิเคราะห์หน้านี้, วิเคราะห์ระบบ, วิเคราะห์ flow, วิเคราะห์ requirement, ตรวจสอบ, ตรวจหา, หา bug, หาช่องโหว่, audit, security, threat model, OWASP, vulnerability, IDOR, XSS, CSRF, SSRF, SQLi, analyze, find bug
- ผู้ใช้พูดถึง: เก็บ requirement, สร้าง spec, use case, user story, sequence diagram, flow diagram, ER diagram, data model, API spec, state machine, edge case, acceptance criteria
- ผู้ใช้ถาม "ระบบนี้ทำงานยังไง", "หน้านี้ทำอะไรบ้าง", "flow เป็นยังไง", "พร้อมขึ้น prod ไหม", "ปลอดภัยพอไหม"
- งานที่ต้องเข้าใจระบบทั้งหมดก่อนตัดสินใจ — ไม่ใช่แก้ไฟล์ใดไฟล์หนึ่งตรงๆ

### `ux` — Visual / Interaction Design

เรียกเมื่อ:
- ผู้ใช้พูดถึง: ออกแบบ, ดีไซน์, design, redesign, ปรับ UI, ปรับหน้าตา, ทำให้สวย, ทันสมัย, modern, polish, responsive, mobile, layout, สี, ปุ่ม, animation, transition, ลูกเล่น, accessibility, mockup
- กำลังจะแก้ `.vue` / `.tsx` / `.jsx` / `.html` / `.css` / `.scss` ในส่วน template / style / class
- ผู้ใช้ส่ง mockup / รูป / Figma link
- งาน implement หน้า/component ใหม่ที่มี UI

### `fe` — Frontend Code (logic / structure / type)

เรียกเมื่อ:
- ผู้ใช้พูดถึง: เขียนหน้า, สร้าง component, refactor, เขียน composable, store, API, schema, validate, fetch, state, reactivity, props, emit, type, TypeScript, Nuxt, Vue, valibot, Pinia, useState, useFetch, middleware, route guard, SSR, hydration
- กำลังจะแก้ `.vue` / `.ts` / `.tsx` / `.js` / `.jsx` ในส่วน `<script>` / logic
- งาน review โค้ดหา anti-pattern / dead code / naming / reactivity bug
- เขียน/แก้ valibot schema, Pinia store, composable, server route

### `migrate` — Bulk transformation across many files

เรียกเมื่อ:
- ผู้ใช้พูดถึง: migrate, ย้าย, แปลง, refactor ทั้งโปรเจกต์, เปลี่ยน X เป็น Y ทุกที่, cleanup ทุกจุด, codemod, replace all
- งานที่ pattern ซ้ำๆ กระจายหลายไฟล์ (เช่น native `<select>` → `USelect` ทั้งโปรเจกต์, inline schema → `shared/schemas/`, deprecated API → new API)
- **ห้ามใช้** สำหรับงานแก้ไฟล์เดียว (ใช้ `fe` แทน) หรือออกแบบ pattern ใหม่ (ใช้ `sa` ก่อน)

### `debug` — Bug diagnosis & fix

เรียกเมื่อ:
- ผู้ใช้พูดถึง: debug, bug, พัง, error, ไม่ทำงาน, แปลกๆ, ทำไม X, หา root cause, diagnose, วินิจฉัย, ปุ่มกดไม่ติด, page กระพริบ, loop infinite
- ผู้ใช้ส่ง error stack / log / screenshot ของ console error
- บังคับ trace ไป **root cause** ไม่ใช่แก้ symptom; scan ripple ของ pattern เดียวกันที่อื่น

---

## Pipeline: `sa → ux → fe → verify`

`sa` (spec) → `ux` (design) → `fe` (code) → `verify` — handoff checklist อยู่ใน SKILL.md ของแต่ละ skill

**กฎไหลลื่น:**
- ขั้นถัดไปเริ่มจาก artifact ของขั้นก่อน ไม่เริ่มจากศูนย์
- ux/fe เจอช่องว่างใน spec → yield กลับ sa ก่อน อย่าเดา
- fe เจอ design implement ไม่ได้ → yield กลับ ux ปรับ ไม่ hack
- ทุกขั้น echo สิ่งที่รับมา (1 บรรทัด) ก่อนต่อ

---

## Mid-task yield (สลับ skill กลางทาง)

ระหว่างทำงานในขั้นใดขั้นหนึ่ง ถ้าเจอประเด็นที่อยู่นอก scope ของ skill ปัจจุบัน — **หยุด, ระบุประเด็น, แล้ว yield ให้ skill ที่เหมาะสม** ไม่ทำต่อด้วย skill ผิด

ตัวอย่าง:
- กำลัง `fe` แล้วพบช่องโหว่ security → **yield ไป `sa` mode B audit** ก่อน fix
- กำลัง `ux` แล้วพบว่า requirement ไม่ครบ (ไม่รู้ว่า empty state ควร render อะไร) → **yield ไป `sa` mode A** เพื่อเก็บ spec ก่อน design
- กำลัง `sa` วิเคราะห์ bug แล้วเจอว่ารากปัญหาคือ reactivity → **yield ไป `fe` review mode** ลงรายละเอียดโค้ด

**กฎ yield:**
- บอกผู้ใช้ตรงๆ ว่ากำลัง yield ไปไหน เพราะอะไร (1 บรรทัด)
- ทำขั้นที่ yield ไปให้จบก่อนกลับมาที่ skill เดิม
- เมื่อกลับมา — apply ผลลัพธ์ของ yield (อย่าทำเหมือนไม่เคย yield)

---

## ความรอบคอบขั้นสูงสุด (cross-skill rule)

หลัก **"แก้จุดเดียว → bug อีกจุด"** ห้ามเกิดเด็ดขาด — บังคับใช้ทั้ง 3 skill

ก่อน **ตรวจ / เสนอแก้ / implement** สิ่งที่ touch โค้ดเดิม:

1. **trace caller / consumer** — `rg "symbol"` ทั้งโปรเจกต์ ดูว่ามีใครพึ่ง symbol/type/state นี้บ้าง
2. **trace shared invariant** — มี shared state, type, schema, route gate ที่ใช้ร่วมกันไหม?
3. **trace persistence** — ค่าเก่าใน localStorage / DB / cache จะ corrupt ไหมถ้า shape เปลี่ยน?
4. **trace cross-tab / cross-page sync** — `storage` event listener / WebSocket / SSE ที่ broadcast change ไหม?
5. **list ripple files** — ทุกไฟล์ที่ต้องแก้พร้อมกัน ระบุชัดก่อนเริ่มแก้

ดูรายละเอียดเต็มที่ skill `sa` section "หลักความรอบคอบขั้นสูงสุด" — `fe` กับ `ux` ก็ต้องทำตามหลักนี้เมื่อ touch โค้ดเดิม

---

## ข้อยกเว้นทั่วไป (ไม่เรียก skill)

- งาน config (Nuxt config, package.json, env, CI/CD)
- งาน docs / markdown ล้วน
- งาน backend ล้วนที่ไม่ใช่ frontend stack
- คำถามทั่วไปที่ตอบได้จากความรู้สากลโดยไม่ต้องอ่านโค้ด
- แก้ typo / comment / formatting เล็กน้อย

---

## Skill memory loop — ทำให้ skill ฉลาดขึ้นเรื่อยๆ

> Load/save logic หลักอยู่ที่ **Universal Phase 0** ด้านบนสุดของไฟล์นี้ — section นี้เก็บเฉพาะ skill-specific convention

### Memory hierarchy (3 ชั้น)

| ชั้น | Path | Scope | โหลดเมื่อ |
|---|---|---|---|
| **Global** | `~/.claude/memory/` | Cross-project, user preference, workflow rule | ทุก task (Universal Phase 0) |
| **Project** | `~/.claude/projects/<id>/memory/` | Project-specific finding/pattern/constraint | ทุก task (Universal Phase 0) |
| **Skill learnings** | `~/.claude/skills/<skill>/learnings.md` | Cross-project per-skill pitfall (Vue reactivity, Tailwind JIT, OWASP pattern) | เฉพาะเมื่อ skill ถูกเรียก (SKILL.md Phase 0.5) |

### Save triggers
ดู **Universal Phase 0 #4** ด้านบน (8 triggers + ตารางว่า save ไปที่ไหน)

### Load logic
ดู **Universal Phase 0 #1-2** ด้านบน (global → project → echo → conflict check)

### Skill tag convention ใน memory frontmatter

เมื่อ save memory ใหม่ → ใส่ field `skill:` ใน `metadata` เพื่อให้ Phase 0 ของ skill filter ได้:

```yaml
---
name: feedback-uselect-empty-value
description: ...
metadata:
  type: feedback
  skill: fe              # หรือ sa, ux, debug, migrate
  topic: nuxt-ui         # optional: เพิ่ม keyword สำหรับ filter
---
```

ค่าที่ใช้ได้ใน `skill:`
- `fe` — ผูกกับ frontend code logic / pattern
- `ux` — ผูกกับ visual / design / interaction
- `sa` — ผูกกับ requirement / spec / security
- `debug` — ผูกกับ bug pattern / root cause / runtime error
- `migrate` — ผูกกับ bulk migration / codemod
- `cross` — ใช้ได้หลาย skill (เช่น `feedback_verify_before_claiming_done`)

**กฎ:** ถ้าไม่ใส่ skill tag → default เป็น `cross` (ทุก skill เห็น) — แต่ควรใส่ให้ชัดเสมอเพื่อ filter ได้

### Graduation pipeline — promote ของซ้ำขึ้น tier

```
project memory (specific to one project)
    ↓ ถ้าเกิดซ้ำ ≥ 2 projects
global memory (~/.claude/memory/ — cross-project rule)
    ↓ ถ้าเกิดซ้ำ ≥ 3 projects กับ skill เดียวกัน
skill learnings (~/.claude/skills/<skill>/learnings.md — per-skill rule)
    ↓ ถ้า rule load-bearing พอจน skill ต้องบังคับใช้ทุกครั้ง
SKILL.md rule (เขียนลง skill เลย)
    ↓
ลบ tier ต้นทางเมื่อ promote — เพราะรวมไว้ใน tier บนแล้ว ไม่ duplicate
```

ผู้ใช้รัน `/distill-memory` (manual) เพื่อ review + promote — Claude ไม่ promote เองอัตโนมัติ (เสี่ยง drift)
