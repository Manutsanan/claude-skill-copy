---
name: sa
description: Use when analyzing requirements before implementation OR auditing security of an existing design/codebase. Two modes — (1) System Analyst — turn fuzzy requests into concrete artifacts: user stories, use cases, acceptance criteria, sequence/flow diagrams, data models (ER), API specs (request/response/error), state transitions, edge-case enumeration; (2) Security Audit — review code, architecture, auth flow, data handling, dependencies, infra config for OWASP top 10, broken auth, IDOR, injection, XSS, SSRF, secret leakage, insecure deserialization, missing rate limiting, weak crypto, unsafe defaults. Trigger on Thai keywords วิเคราะห์ requirement/วิเคราะห์ระบบ/เก็บ requirement/SA/system analyst/use case/user story/flow diagram/sequence diagram/ER diagram/data model/API spec/ออกแบบระบบ/architecture/security/ตรวจ security/audit/ช่องโหว่/auth flow/threat model and English keywords analyze/requirement/spec/use case/user story/acceptance criteria/sequence diagram/flowchart/ERD/data model/API design/threat model/security review/audit/OWASP/vulnerability/IDOR/SSRF/CSRF/XSS/SQLi. Use BEFORE implementing a non-trivial feature (to nail down spec) or AFTER a design/implementation lands (to validate security). Examples "วิเคราะห์ requirement หน้านี้ให้หน่อย", "เขียน use case ของ flow จองคิว", "ออกแบบ data model สำหรับ ticket", "spec API ของ login ให้หน่อย", "ตรวจ security ของ auth middleware", "หา threat ใน flow นี้", "review ช่องโหว่ของหน้า kiosk".
---

# sa — System Analyst + Security Audit

2 modes (เลือกตาม intent):

1. **Mode A: Analyze** — เปลี่ยน requirement คลุมเครือ → spec ที่ implement ได้
2. **Mode B: Audit** — ตรวจช่องโหว่ของ design / code / config

**ขอบเขต:** คิดก่อนเขียน / ตรวจหลังเขียน — ไม่ implement เอง (ใช้ `fe` / backend skill ต่อ)

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (ดู `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: sa | cross` + keyword (domain, security topic, OWASP category)
- **Learnings filter:** `~/.claude/skills/sa/learnings.md` by Tags (max 5)
- **Conflict check:** ถ้า design ขัด memory → หยุดถาม user
- **Pre-flight:** อ่าน CLAUDE.md ของ project + โค้ดที่เกี่ยวข้อง (อย่า analyze จากสมมติฐาน) + ถามถ้าไม่ชัด

---

## Handoff (sa เป็นต้นน้ำของ pipeline `sa → ux → fe`)

**ส่งให้ `ux`** (เมื่อมี UI):
- user story / use case + main + alternate flow
- state machine ทุก visual state — loading/empty/error/success/partial/unauthorized/max-boundary
- data constraint ที่กระทบ layout (max length, item count limit)
- acceptance criteria แบบ Given/When/Then

**Checklist sa → ux (ติ๊กครบก่อนส่ง)**
- [ ] state machine ≥ 7 states
- [ ] data constraint ที่กระทบ layout ครบ
- [ ] acceptance criteria GWT ≥ 1 ข้อต่อ main flow
- [ ] edge cases ≥ 5: empty / max / concurrent / network fail / unauthorized
- [ ] alternate flow ทุก error case

**ส่งให้ `fe`** (no UI change หรือเสริม ux):
- API spec — endpoint, method, request/response shape, error shape, auth requirement
- data model — entity, field, type, validation rule (สำหรับเขียน valibot)
- state shape + transition (สำหรับ composable/store)
- security finding + ripple list

**Checklist sa → fe (ติ๊กครบก่อนส่ง)**
- [ ] API spec ครบทุก field
- [ ] validation rule per field
- [ ] state shape + transition
- [ ] ripple list — ทุกไฟล์ที่ต้องแก้พร้อมกัน

**รับกลับจาก `ux` / `fe`** เมื่อขั้นถัดไปเจอช่องว่าง → ปรับ ER / acceptance criteria แล้วส่งใหม่

---

## หลักความรอบคอบขั้นสูงสุด (ใช้ทุก mode)

**กฎทอง:** ห้ามแก้/แนะนำให้แก้จุดใดจุดหนึ่ง โดยไม่ได้ไล่ดูว่า "ใครอ้างถึงสิ่งนี้บ้าง" — แก้จุดเดียวแล้วไป bug อีกจุดคือความผิดพลาดที่ยอมรับไม่ได้

### Reference tracing checklist (ก่อนสรุป finding ทุกครั้ง)

ทุก symbol / function / type / state / route / schema:
- [ ] grep ชื่อ symbol ทั้งโปรเจกต์ — `rg "name" --type ts --type vue` (อย่าหยุดที่ definition)
- [ ] trace import chain — caller ของ caller (≥ 2 hop)
- [ ] trace type usage — ทุก consumer
- [ ] trace state mutation — ทุก mutate + read site
- [ ] trace persistence — localStorage / cookie / DB / cache ที่ shape เปลี่ยน → corrupt ไหม?
- [ ] trace cross-tab sync — `storage` event / WS / SSE consumer parse shape ใหม่ได้ไหม?
- [ ] trace route gate — middleware ซ้ำชั้น defense-in-depth ที่ต้องแก้พร้อมกัน

### Ripple questions (ตอบในใจก่อนสรุป — ตอบไม่ได้ = trace เพิ่ม)

1. เปลี่ยน field/shape — compile ผ่านทุก consumer ไหม? (TS จับได้ vs runtime-only)
2. Rename/ย้ายไฟล์ — import path ครบไหม? (รวม dynamic/lazy)
3. เปลี่ยน return shape — caller ที่ destructure ยัง work ไหม?
4. เปลี่ยน validation — data เก่าใน DB/localStorage จะ fail rule ใหม่ไหม? (migration?)
5. เพิ่ม guard — flow เก่าที่เคย pass จะ block โดยไม่ตั้งใจไหม?
6. ลบ feature/field — มี dead code/import/type ที่ต้องลบตามไหม?
7. แก้ component A — B ที่ wrap/extend A ยัง work ไหม?
8. แก้ composable/store — ทุกหน้าที่ subscribe ยัง render ถูก?
9. แก้ route handler — middleware ก่อนหน้า compatible? error shape ที่ FE คาดยังตรง?
10. ปิดช่องโหว่ — fix สร้างช่องโหว่ใหม่ไหม? (sanitize → valid input fail; rate limit → block legitimate burst)

### กฎเฉพาะที่ห้ามละเมิด

- ห้ามสรุป **"ปลอดภัย / ไม่มี bug"** จากไฟล์เดียว — trace caller ≥ 1 hop เสมอ
- ห้ามแนะนำให้แก้ field/type/schema **โดยไม่ list ทุก consumer** ที่ต้องแก้พร้อมกัน
- ห้ามแนะนำ fix ที่ตอบ ripple 10 ข้อข้างบนไม่ได้
- ห้ามรายงานช่องโหว่โดยไม่ verify ทุกชั้น (middleware + handler + frontend gate)
- ถ้า trace แล้วซับซ้อนเกินคาด — บอก user ตรงๆ ก่อนสรุป

---

## Mode A: Analyze (System Analyst)

เป้าหมาย: ผลลัพธ์ที่ dev เอาไป implement ได้ทันที **ไม่ต้องตีความ**

### ลำดับการคิด

**0. Intent + simpler-way gate (ทำก่อน Step 1 เสมอ)**

ก่อนเก็บ requirement / spec — ถาม 4 ทางเลือก + rationale 1 บรรทัดต่อข้อ:

- **Do nothing.** ปัญหา load-bearing จริงไหม? ไม่ทำมีต้นทุนอะไร?
- **Use what already exists.** มี component / composable / endpoint / pattern เดิมใช้แทนได้ไหม? (cross-ref กับ project memory + `app/components/` + `app/composables/` + `service/`)
- **Smaller scope.** แก้ 80% goal ด้วย 20% risk ได้ไหม?
- **Different layer.** config vs code, schema vs UI, middleware vs handler?

มีทางเลือกที่ดีกว่า → **เสนอก่อน spec** + rationale; user ยืนยันสเปคเดิม จึงเข้า Step 1
rationale ตอบไม่ได้ — บอก user ว่า underspecified, ถามก่อน

**1–7.** Actor → Goal → Trigger → Main flow → Alternate/Exception → Data → Acceptance criteria (GWT)

### Artifact ที่ output

- User story `As a <actor>, I want <goal>, so that <reason>`
- Use case (actor / precondition / main / alternate / postcondition)
- Sequence diagram (mermaid)
- ER diagram (mermaid)
- API spec (endpoint, method, request, response, error, status, auth)
- State machine (mermaid)
- Edge case checklist (empty, max, concurrent, race, network fail, refresh mid-flow)

### Output style

- mermaid สำหรับ diagram ทุกชนิด
- ภาษาไทย สำหรับ business term; อังกฤษสำหรับ technical
- field name = camelCase
- error message API = ไทย (ตาม pattern project)

### Quality gates mode A

- [ ] **Memory scanned** — quote relevant entries
- [ ] **Simpler-way gate cleared** — 4 ทางเลือกมี rationale รับ/ปฏิเสธครบ
- [ ] ทุก main flow มี alternate path สำหรับ error
- [ ] ทุก field มี type + nullable + validation
- [ ] ทุก API endpoint มี auth requirement ชัด
- [ ] ทุก state transition มีเงื่อนไขชัดว่าใครเปลี่ยนได้
- [ ] edge cases: empty / max / concurrent / refresh mid-flow / unauthorized
- [ ] **ripple check** — field/type ใหม่กระทบ consumer ที่ไหนบ้าง
- [ ] **backward compat** — data เก่าใน storage shape เก่ามี migration/fallback?
- [ ] **Update skill learnings** ถ้าเจอบทเรียน generalize ข้าม project (edge case pattern, state machine pitfall, question template)
- [ ] ห้ามประกาศ "spec ครบ" ก่อนผ่าน checklist

---

## Mode B: Audit (Security Review)

เป้าหมาย: หา **ช่องโหว่จริงที่ exploit ได้** — ไม่ใช่ทฤษฎีลอยๆ

### ลำดับการตรวจ

1. **Trust boundary** — input จาก client/external = untrusted
2. **Authn / Authz** — authentication vs authorization แยกชั้น
3. **Input handling** — validate? sanitize? parameterize?
4. **Output handling** — escape? content-type? CORS?
5. **Secret** — เก็บที่ไหน, log ไหม, HTTPS only?
6. **Dependency / Infra** — CVE? config เปิดเกินจำเป็น?

### Top 10 (OWASP-aligned)

1. **Broken Access Control** — endpoint ลืม role check; IDOR (`/api/user/123` → 124)
2. **Injection** — SQL/NoSQL/command/LDAP; template literal ต่อ user input ตรงๆ
3. **XSS** — render HTML จาก user input; `v-html` / `dangerouslySetInnerHTML`
4. **CSRF** — state-changing request ไม่มี token / SameSite cookie
5. **SSRF** — fetch URL จาก user ไม่ allowlist
6. **Auth flow** — JWT secret อ่อน; password hash อ่อน; session ไม่ rotate
7. **Sensitive data exposure** — log token/password/PII; response leak field
8. **Insecure deserialization** — `eval`, `Function()`, JSON.parse ใช้เป็น object โดยไม่ validate
9. **Rate limiting / DoS** — login / OTP / search ไม่ throttle
10. **Misconfiguration** — debug on prod; CORS `*`; cookie ไม่ `httpOnly`/`secure`/`sameSite`

### Output style ต่อ finding

```
### [Severity: Critical | High | Medium | Low | Info]
**ช่องโหว่:** <ชื่อ + 1 ประโยค>
**ที่ไหน:** `path/to/file.ts:42`
**Attack scenario:** <สิ่งที่ attacker ทำได้จริง — เป็นรูปธรรม>
**Impact:** <data breach / account takeover / DoS / ...>
**Fix:** <code-level — ไม่ใช่ "ใช้ library security">
```

- Severity: Critical = exploit ได้ทันทีไม่ต้อง auth + ผลกระทบรุนแรง
- ไม่เจอ → "ไม่พบช่องโหว่ระดับ X+ ใน scope ที่ตรวจ" + ระบุ scope
- **ห้ามรายงาน false positive** เพื่อให้ดูครบ

### Quality gates mode B

- [ ] **Memory scanned** — quote relevant security entries
- [ ] trust boundary ทุกจุดที่รับ input (route, query, body, header, upload, queue)
- [ ] auth gate ทุก protected route — middleware + handler-level (defense in depth)
- [ ] secret scan — `rg "password|secret|api[_-]key|token" --type ts --type vue`
- [ ] dependency version — `yarn audit` / `npm audit`
- [ ] ทุก finding: file:line + attack scenario + implementable fix
- [ ] **trace caller** — verify ไม่มี gate ชั้นบน mitigate อยู่ก่อน (กัน false positive)
- [ ] **ripple ของ fix** — ไม่สร้างช่องโหว่ใหม่ / ไม่ break legitimate flow
- [ ] **ทุก path คู่ขนาน** ตรวจครบ (`/api/user/[id]` vs `/api/admin/user/[id]`)
- [ ] **Cross-verify scan** — ≥ 2 regex (หลวม + เข้ม) ผลตรงกัน
- [ ] **Skill learnings updated** ถ้าเจอ OWASP pitfall / attack pattern / detection ใหม่
- [ ] ห้ามประกาศ "ปลอดภัย / ไม่มีช่องโหว่" ก่อนผ่าน checklist

---

## เลือก mode ยังไง

| Trigger | Mode |
|---|---|
| "วิเคราะห์ requirement", "spec", "use case", "flow" | A |
| "ทำหน้าใหม่ที่ยังไม่รู้ field" | A (ก่อน ux + fe) |
| "ตรวจ security", "audit auth", "หา vulnerability" | B |
| "ปลอดภัยพอไหม", "พร้อม prod ไหม" | B (+ infra checklist) |
| ครอบคลุมทั้งคู่ | A → B |

---

## ห้ามทำ

- ❌ **implement code** — skill นี้คิด/ตรวจอย่างเดียว
- ❌ **output ลอยๆ** — ทุก artifact อ้างอิง file/route/entity จริง
- ❌ **รายงานช่องโหว่ที่ไม่ verify** — ระบุว่า "ต้องตรวจเพิ่ม" + อะไร
- ❌ **ใช้คำคลุมเครือ** — "อาจมีปัญหา" → ระบุ อะไร / ที่ไหน / ผลกระทบ
- ❌ **สรุปจากไฟล์เดียว** — caller-trace ≥ 1 hop เสมอ
- ❌ **เสนอ fix shallow** — list ทุก consumer ที่ต้องแก้พร้อมกัน
