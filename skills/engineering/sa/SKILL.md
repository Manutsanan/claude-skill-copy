---
name: sa
description: Use when analyzing requirements before implementation OR auditing security of an existing design/codebase. Two modes — (1) System Analyst — turn fuzzy requests into concrete artifacts: user stories, use cases, acceptance criteria, sequence/flow diagrams, data models (ER), API specs (request/response/error), state transitions, edge-case enumeration; (2) Security Audit — review code, architecture, auth flow, data handling, dependencies, infra config for OWASP top 10, broken auth, IDOR, injection, XSS, SSRF, secret leakage, insecure deserialization, missing rate limiting, weak crypto, unsafe defaults. Trigger on Thai keywords วิเคราะห์ requirement/วิเคราะห์ระบบ/เก็บ requirement/SA/system analyst/use case/user story/flow diagram/sequence diagram/ER diagram/data model/API spec/ออกแบบระบบ/architecture/security/ตรวจ security/audit/ช่องโหว่/auth flow/threat model and English keywords analyze/requirement/spec/use case/user story/acceptance criteria/sequence diagram/flowchart/ERD/data model/API design/threat model/security review/audit/OWASP/vulnerability/IDOR/SSRF/CSRF/XSS/SQLi. Use BEFORE implementing a non-trivial feature (to nail down spec) or AFTER a design/implementation lands (to validate security). Examples "วิเคราะห์ requirement หน้านี้ให้หน่อย", "เขียน use case ของ flow จองคิว", "ออกแบบ data model สำหรับ ticket", "spec API ของ login ให้หน่อย", "ตรวจ security ของ auth middleware", "หา threat ใน flow นี้", "review ช่องโหว่ของหน้า kiosk".
---

# sa — System Analyst + Security Audit

ครอบคลุม 2 mode ที่แยกกันชัดเจน — เลือกตาม intent:

1. **Mode A: Analyze** — เปลี่ยน requirement คลุมเครือ → spec ที่ implement ได้
2. **Mode B: Audit** — ตรวจช่องโหว่ของ design / code / config

> ขอบเขต skill นี้คือ **คิดก่อนเขียน** กับ **ตรวจหลังเขียน** — ไม่ implement เอง (ใช้ `fe` / backend skill ทำต่อ)

## Handoff (sa เป็นต้นน้ำของ pipeline `sa → ux → fe`)

`sa` ส่ง artifact ให้ขั้นถัดไปต่อ — ออกแบบ output ให้ขั้นต่อไปใช้ได้ทันทีโดยไม่ต้องตีความ:

**ส่งให้ `ux`** (เมื่องานมี UI):
- user story / use case + main + alternate flow
- state machine (visual state ทุกตัว — loading/empty/error/success/partial/unauthorized/max boundary)
- data constraint ที่กระทบ layout (เช่น "code ยาวสุด 5 ตัว", "list สูงสุด 20 รายการ")
- acceptance criteria แบบ Given/When/Then

**Handoff checklist: sa → ux (ติ๊กครบก่อนส่ง — ติ๊กไม่ครบ = ทำต่อ ห้าม handoff)**
- [ ] state machine enumerate ≥ 7 visual states: loading / empty / error / success / partial / unauthorized / max-boundary
- [ ] data constraint ที่กระทบ layout ระบุครบ (max length, item count limit, field character limit)
- [ ] acceptance criteria เขียนแบบ Given/When/Then อย่างน้อย 1 ข้อต่อ main flow
- [ ] edge case enumerate ≥ 5: empty / max boundary / concurrent / network fail / unauthorized
- [ ] alternate flow สำหรับทุก error case ระบุแล้ว

**ส่งให้ `fe`** (ส่งตรงเมื่อไม่มี UI เปลี่ยน หรือส่งเสริม ux):
- API spec — endpoint, method, request/response shape, error shape, auth requirement
- data model — entity, field, type, validation rule (สำหรับเขียน valibot)
- state shape + transition (สำหรับ composable/store)
- security finding + ripple list (ทุกไฟล์ที่ต้องแก้พร้อมกัน — ดู "หลักความรอบคอบขั้นสูงสุด")

**Handoff checklist: sa → fe (ติ๊กครบก่อนส่ง — ติ๊กไม่ครบ = ทำต่อ ห้าม handoff)**
- [ ] API spec ครบ: endpoint, method, request body, response shape, error shape, auth requirement
- [ ] validation rule per field ระบุแล้ว (สำหรับ valibot schema)
- [ ] state shape + transition ระบุแล้ว (สำหรับ composable/store)
- [ ] ripple list ระบุแล้ว: ทุกไฟล์ที่ต้องแก้พร้อมกันถ้า spec นี้ถูก implement

**รับจาก `fe` / `ux` กลับมา** เมื่อขั้นถัดไปเจอช่องว่าง:
- field/edge case ที่ไม่ครอบคลุม → ปรับ ER / acceptance criteria แล้วส่งใหม่
- behavior ที่ขัดกับ state machine → review transition ก่อน

ดู "Skill orchestration" ใน `~/.claude/CLAUDE.md` สำหรับ pipeline เต็ม

---

## Phase 0 — Load memory hierarchy (mandatory — extend Universal Phase 0)

ลำดับ:

1. **Load global memory** — `~/.claude/memory/MEMORY.md`
   - filter: `metadata.skill: sa` หรือ `skill: cross`
   - filter ต่อด้วย keyword: domain term, security topic, API name, OWASP category
   - ถ้าไม่มีไฟล์ → ข้าม + หมายเหตุ "ไม่มี global memory"

2. **Load project memory** — `~/.claude/projects/<project-id>/memory/MEMORY.md`
   - project id = working directory แปลง `/` → `-` (เช่น `/Users/X/Project/Y` → `-Users-X-Project-Y`)
   - filter เดียวกับ global memory
   - ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory — fresh start"

3. **Echo top 3-5 entries** กลับให้ user เห็นก่อนเริ่ม analysis:
   ```
   📚 Memory ที่ relevant กับงานนี้ (sa):
   - [global] feedback-verify-before-done — ห้ามเคลม "ครบ" ก่อน verify หลายมุม
   - [project] security_audit_2026_04_19 — 3 CRITICAL ที่ยังไม่ fix
   - [project] project_features — list feature ที่เกี่ยวข้อง
   ```

4. **Conflict check** — ถ้าจะเสนอ design/analysis ที่ขัด memory → หยุดถาม user ก่อน + override → update memory ให้สะท้อน

5. **หลังจบงาน** — save lesson ตาม **8 universal save triggers** ใน `~/.claude/CLAUDE.md` Universal Phase 0 #4 (อ้างตารางว่า save ไป global หรือ project)

### Memory ที่ `sa` ต้องเช็คทุกครั้ง (ถ้ามีใน project)

- `security_audit_*` — finding เก่าที่ยังไม่ fix
- `project_architecture.md` / `project_features.md` — domain knowledge เดิม
- `feedback_verify_before_claiming_done.md` — กฎเช็คก่อนเคลม "ครบ"
- `feedback_thorough_cleanup.md` — bulk audit ต้องสแกน 4 axes

### Pre-flight อื่นๆ (ทำคู่กับ Phase 0)

1. **อ่าน CLAUDE.md ของโปรเจกต์** — business domain, state model, convention, auth model
2. **อ่านโค้ดที่เกี่ยวข้อง** — อย่าวิเคราะห์/ตรวจจากสมมติฐาน ดู type, schema, route, middleware จริง
3. **ถามถ้าไม่ชัด** — requirement คลุมเครือคือ root cause ของ bug 90% ถามก่อน implement ถูกกว่ารื้อทีหลัง

> ดู `~/.claude/CLAUDE.md` Universal Phase 0 สำหรับ load/save logic เต็ม + skill tag convention

---

## Phase 0.5 — Load skill learnings (mandatory)

ลำดับ:

1. **Extract task keywords** — ดึง keyword จาก request ของ user: domain term (`auth`, `payment`, `booking`), security topic (`IDOR`, `XSS`, `CSRF`), pattern (`concurrent`, `idempotency`, `state-machine`, `edge-case`)
2. **อ่าน** `~/.claude/skills/sa/learnings.md` — scan เฉพาะ **Tags:** field ของแต่ละ entry
3. **Load เฉพาะ entry ที่ตรง** — entry ผ่านถ้า Tags มี ≥1 keyword ตรง **และ header ไม่มี `~~`**; ถ้าไม่มี tag ตรงหรือ header มี `~~` (deprecated) → skip ทั้ง entry
4. **Max 5 entries** — ถ้าตรงมากกว่า 5 → เลือก 5 ที่ keyword match สูงสุด; tie → เลือกที่ Date ใหม่กว่า
5. **Quote** entry ที่ใช้ใน reasoning — เช่น "ตาม learnings#concurrent-submit-pattern จะ enumerate edge case นี้"
6. **ถ้าไม่มี entry ตรง** → หมายเหตุ "ไม่มี skill learning ตรง — fresh start" (ห้าม fallback โหลดทั้งไฟล์)
7. **หลังจบงาน** → ถ้าเจอบทเรียน generalize ได้ → append เข้า learnings.md (ดู Quality gates)

---

## หลักความรอบคอบขั้นสูงสุด (mandatory — ใช้ทุก mode)

> **กฎทอง:** ห้ามแก้/แนะนำให้แก้จุดใดจุดหนึ่ง โดยที่ยังไม่ได้ไล่ดูว่า "ใครอ้างถึงสิ่งนี้บ้าง" — แก้จุดเดียวแล้วไป bug อีกจุดคือความผิดพลาดที่ยอมรับไม่ได้

### หลักการ: trace ก่อน touch

ก่อน **เสนอแก้**, **เสนอ refactor**, **บอกว่าเป็น bug**, หรือ **บอกว่าปลอดภัย** — ต้องไล่ดู ripple effect ให้ครบทุกชั้นก่อน:

1. **ใครเรียก / import สิ่งนี้บ้าง** (callers, importers)
2. **สิ่งนี้เรียก / depend อะไรต่อ** (callees, dependencies)
3. **มี shared state / type / schema ที่ใช้ร่วมกันไหม** (cross-file invariant)
4. **มี side effect ที่กระทบโลกภายนอกไหม** (localStorage, event listener, network, DOM)

### Reference tracing checklist (ต้องทำก่อนสรุป finding ทุกครั้ง)

สำหรับทุก symbol / function / type / state / route / schema ที่เกี่ยวข้อง:

- [ ] **grep ชื่อ symbol** ทั้งโปรเจกต์ — `rg "symbolName" --type ts --type vue` (อย่าหยุดที่ definition file)
- [ ] **trace import chain** — ใครคือ caller ของ caller? (อย่างน้อย 2 hop)
- [ ] **trace type usage** — type นี้ถูก import ที่ไหนบ้าง? field ใหม่/ลบ field กระทบ consumer ตรงไหน?
- [ ] **trace state mutation** — state ตัวนี้ถูก mutate ที่ไฟล์ไหนบ้าง? ถูก read ที่ไหนบ้าง? (เช่น `useState('queueData')` ใน Nuxt — ทุกหน้าที่เรียก composable นี้คือ consumer)
- [ ] **trace persistence layer** — มี localStorage / cookie / DB / cache ที่เก็บค่าเดิมไหม? schema เปลี่ยน → ค่าเก่าใน storage จะ corrupt ไหม?
- [ ] **trace cross-tab / cross-page sync** — มี `storage` event listener / WebSocket / SSE ที่ broadcast change ไหม? เปลี่ยน shape ของ message → ฝั่ง consumer parse ได้ไหม?
- [ ] **trace route gate** — endpoint / page ที่เกี่ยวข้องผ่าน middleware ตัวไหน? มี gate ซ้ำชั้น (defense in depth) ที่ต้องแก้พร้อมกันไหม?

### Ripple-effect questions (ถามตัวเองก่อนสรุป)

ก่อนเขียน finding / suggestion ใดๆ ให้ตอบคำถามเหล่านี้ในใจ — ถ้าตอบไม่ได้ = ยังไม่พร้อมสรุป ต้องไป trace เพิ่ม:

1. ถ้าเปลี่ยน field/shape นี้ → **คอมไพล์ผ่านไหม** ทุก consumer? (TypeScript จับได้ไหม หรือเป็น runtime-only?)
2. ถ้า rename / ย้ายไฟล์ → **ทุก import path** ถูกอัปเดตไหม? (รวม dynamic import, lazy import, route config)
3. ถ้าเปลี่ยน return shape → **caller ที่ destructure** ค่าเก่ายัง work ไหม?
4. ถ้าเปลี่ยน validation rule → **ข้อมูลเก่าใน DB / localStorage** ที่ผ่าน rule เก่าจะ fail rule ใหม่ไหม? (migration / fallback)
5. ถ้าเพิ่ม guard / check → **flow ที่เคย pass** จะถูก block โดยไม่ตั้งใจไหม?
6. ถ้าลบ feature / field → มีโค้ด **dead** ที่ต้องลบตามไหม? (ไม่ทิ้ง orphan import / unused type)
7. ถ้าแก้ component A — component B ที่ extend / wrap A ยัง work ไหม?
8. ถ้าแก้ composable / store — ทุกหน้าที่ subscribe state นั้นยัง render ถูกต้องไหม?
9. ถ้าแก้ route handler — middleware ที่ run ก่อนหน้ายัง compatible ไหม? error shape ที่ frontend คาดหวังยังตรงไหม?
10. ถ้าแก้เพื่อปิดช่องโหว่ — fix ของฉันสร้าง **ช่องโหว่ใหม่** ไหม? (เช่น เพิ่ม sanitize → ทำให้ valid input บางตัว fail; เพิ่ม rate limit → block legitimate user burst)

### Tools ที่ต้องใช้สำหรับ tracing

- **`rg` (ripgrep)** — grep symbol ทั้งโปรเจกต์ พร้อม `--type` filter
- **`rg -l "symbol"`** — list ไฟล์ที่ match (เร็วกว่าอ่านทีละไฟล์)
- **`Read` tool** — เปิดไฟล์ที่ match อ่าน context จริง อย่าเดาจากชื่อไฟล์
- **`Explore` agent (subagent)** — เมื่อ scope กว้าง (ต้อง trace > 5 ไฟล์) ใช้ Explore แทน grep ทีละครั้ง
- **TypeScript compiler signal** — `nuxt prepare` / `tsc --noEmit` ช่วยจับ type ripple ที่ grep ไม่เห็น (generic, conditional type)

### กฎเฉพาะที่ห้ามละเมิด

- **ห้ามสรุป "ปลอดภัย" / "ไม่มี bug"** จากการดูไฟล์เดียว — ต้อง trace caller อย่างน้อย 1 hop เสมอ
- **ห้ามแนะนำให้แก้** field/type/schema **โดยไม่ list ทุก consumer** ที่ต้องแก้พร้อมกัน
- **ห้ามแนะนำ fix** ที่ตัวเองยังไม่ได้ตอบคำถาม ripple 10 ข้อข้างบน
- **ห้ามรายงานช่องโหว่** โดยไม่ได้ verify จากทุกชั้นที่เกี่ยวข้อง (middleware + handler + frontend gate — ถ้ามี gate ชั้นใดชั้นหนึ่ง mitigate อยู่แล้ว ก็ไม่ใช่ช่องโหว่จริง)
- **ถ้า trace แล้วเจอความซับซ้อนเกินคาด** — บอก user ตรงๆ ก่อนสรุป อย่าเดาเพื่อให้งานจบเร็ว

---

## Mode A: Analyze (System Analyst)

เป้าหมาย: ออกผลลัพธ์ที่ dev เอาไป implement ต่อได้ทันที **ไม่ต้องตีความ**

### ลำดับการคิด

0. **Intent + simpler-way gate (mandatory — ทำก่อน Step 1 เสมอ)**
   ก่อนเก็บ requirement / spec — ถามให้ครบ 4 ทางเลือก แล้วเขียน **rationale 1 บรรทัด** ต่อข้อว่ารับ/ปฏิเสธเพราะอะไร:

   - **Do nothing.** ปัญหานี้ load-bearing จริงไหม / ไม่ทำเลยมีต้นทุนอะไร? (บางครั้ง user สังเกตเห็นปัญหาที่ไม่ต้องแก้)
   - **Use what already exists.** มี component / composable / endpoint / pattern ใน codebase ที่ใช้แทนได้ไหม โดยไม่ต้องเพิ่ม surface ใหม่? (อย่าสร้าง duplicate; cross-ref กับ project memory + `app/components/` + `app/composables/` + `service/`)
   - **Smaller scope.** มี change เล็กกว่าที่แก้ได้ 80% ของ goal ด้วย 20% ของ risk ไหม? (ทำ phase 1 ก่อน, phase 2 ค่อยตามถ้าจำเป็น)
   - **Different layer.** แก้ที่ layer อื่นจะ clean กว่าไหม — config vs code, schema vs UI, middleware vs handler, framework vs app code?

   ถ้ามีทางเลือกที่ดีกว่า → **เสนอก่อน** spec ตัวเต็ม + ระบุ rationale; ถ้าผู้ใช้ยืนยันสเปคเดิม จึงค่อยเข้า Step 1
   ถ้า rationale ตอบไม่ได้ — บอกผู้ใช้ตรงๆ ว่า requirement ยัง underspecified, ถามก่อน อย่าเดา

1. **Actor** — ใครใช้? (customer / staff / admin / system) แต่ละ role เห็น/ทำอะไรได้บ้าง?
2. **Goal** — actor นั้นต้องการบรรลุอะไร? (1 ประโยค "ฉันอยาก ___ เพื่อ ___")
3. **Trigger** — เริ่มเมื่อไร? (ผู้ใช้กดปุ่ม / cron / event)
4. **Main flow** — happy path step-by-step (numbered list)
5. **Alternate / Exception flow** — ถ้า input invalid / network fail / state ไม่ถูกต้อง → ทำอะไร?
6. **Data** — ระบบต้องเก็บอะไร? shape ของ entity, relation, lifecycle (create → update → archive)
7. **Acceptance criteria** — เช็คได้ pass/fail ชัดเจน (ใช้ Given/When/Then)

### Artifact ที่ output

เลือกอย่างใดอย่างหนึ่งหรือหลายอย่างตามความเหมาะสม:

- **User story** — `As a <actor>, I want <goal>, so that <reason>`
- **Use case** — actor / precondition / main flow / alternate flow / postcondition
- **Sequence diagram** (mermaid) — สำหรับ flow ที่มี actor หลายฝั่งคุยกัน (kiosk → server → display)
- **ER diagram** (mermaid) — entity + relation + cardinality
- **API spec** — endpoint, method, request body (พร้อม validation), response (success + error shape), status codes, auth requirement
- **State machine** (mermaid) — สำหรับ entity ที่มี lifecycle หลาย state (ticket: waiting → calling → serving → done | skipped)
- **Edge case checklist** — empty, max boundary, concurrent action, race condition, network fail, refresh mid-flow

### Output style

- ใช้ **mermaid** สำหรับ diagram ทุกชนิด (รองรับใน GitHub / Markdown viewer ส่วนใหญ่)
- ใช้ภาษาไทยสำหรับ business term (ตาม domain โปรเจกต์) แต่ใช้ภาษาอังกฤษสำหรับ technical term (entity, field, status)
- field name ใน data model ใช้ camelCase ตรงกับ TypeScript convention
- error message ใน API spec เขียนเป็นภาษาไทย (ตาม pattern ของโปรเจกต์)

### Quality gates ก่อนปิดงาน mode A (mandatory)

- [ ] **Memory scanned** — quote feedback/project memory ที่ relevant ก่อนเสนอ spec
- [ ] **Simpler-way gate cleared** — 4 ทางเลือก (do nothing / existing / smaller / different layer) มี rationale รับ/ปฏิเสธครบทุกข้อ ไม่ใช่ skip เพื่อเข้า spec
- [ ] ทุก main flow มี alternate path สำหรับ "เกิด error"?
- [ ] ทุก field ใน data model มี type + nullable rule + validation rule?
- [ ] ทุก API endpoint มี auth requirement ระบุชัด?
- [ ] ทุก state transition มีเงื่อนไขชัดว่าใครเปลี่ยนได้และเมื่อไร?
- [ ] edge case ที่คิดได้: empty / max / concurrent / refresh mid-flow / unauthorized?
- [ ] **ripple check** — ถ้า spec นี้ถูก implement: field/type ใหม่กระทบ consumer เดิมที่ไหนบ้าง? (list ไฟล์ที่ต้องแก้พร้อมกัน)
- [ ] **backward compat** — มีข้อมูลเก่าใน storage / DB ที่ shape เก่าไหม? ต้องมี migration / fallback?
- [ ] **ห้ามประกาศ "spec ครบ"** ก่อนผ่าน checklist นี้ — ถ้าผู้ใช้ต้องสั่ง "ครบไหม / ตรวจอีกรอบ" = scan แรกไม่ดีพอ → update memory ทันที
- [ ] **Update skill learnings** ที่ `~/.claude/skills/sa/learnings.md` ถ้าเจอบทเรียนที่ generalize ข้าม project ได้ (เช่น edge case pattern ใหม่, state machine pitfall, question template ที่ใช้ดึง requirement ได้ดี) — append entry ตาม format ในไฟล์

---

## Mode B: Audit (Security Review)

เป้าหมาย: หา **ช่องโหว่จริง** ที่ exploit ได้ ไม่ใช่ list ทฤษฎีลอยๆ

### ลำดับการตรวจ

1. **Trust boundary** — ตรงไหนคือขอบของ "ข้อมูลที่ตัวเองคุม" vs "ข้อมูลจาก client/external" (input ทุกตัวจาก client = untrusted)
2. **Authn / Authz** — ใครเป็นใคร? (authentication) ใครทำอะไรได้? (authorization) แยกชั้นกันจริงไหม
3. **Input handling** — validate? sanitize? parameterize?
4. **Output handling** — escape? content-type? CORS?
5. **Secret / Credential** — เก็บที่ไหน, log ไหม, ส่งผ่าน HTTPS เท่านั้น?
6. **Dependency / Infra** — version เก่ามี CVE? config เปิด port เกินจำเป็น?

### Top 10 ที่ต้องเช็คเสมอ (OWASP-aligned)

1. **Broken Access Control** — endpoint ที่ต้อง auth ลืมเช็ค role? IDOR (`/api/user/123` แก้เป็น 124 แล้วเข้าได้)?
2. **Injection** — SQL / NoSQL / command / LDAP — ใช้ parameterized query? template literal ที่ต่อ user input ตรงๆ?
3. **XSS** — render HTML จาก user input โดยไม่ escape? `v-html` / `dangerouslySetInnerHTML` ที่รับค่าจากภายนอก?
4. **CSRF** — state-changing request ไม่มี CSRF token / SameSite cookie?
5. **SSRF** — fetch URL ที่ user ส่งมาโดยไม่ allowlist domain?
6. **Auth flow** — JWT secret อ่อน / hardcoded? password hash อ่อน (md5/sha1 เปล่า)? session ไม่ rotate หลัง login?
7. **Sensitive data exposure** — log token / password / PII? response leak field ไม่จำเป็น (`user.passwordHash`)?
8. **Insecure deserialization** — `eval`, `Function()`, `JSON.parse` แล้วใช้เป็น object เลยโดยไม่ validate shape?
9. **Rate limiting / DoS** — login / OTP / search endpoint ไม่มี throttle?
10. **Misconfiguration** — debug mode เปิดบน prod? CORS `*`? cookie ไม่ `httpOnly` / `secure` / `sameSite`?

### Output style

สำหรับแต่ละช่องโหว่ที่พบ:

```
### [Severity: Critical | High | Medium | Low | Info]
**ช่องโหว่:** <ชื่อ + 1 ประโยคอธิบาย>
**ที่ไหน:** `path/to/file.ts:42`
**Attack scenario:** <attacker ทำอะไรได้จริงๆ — เป็นรูปธรรม ไม่ใช่ "อาจถูกโจมตี">
**Impact:** <data breach / account takeover / DoS / ...>
**Fix:** <แก้ยังไง — code-level ไม่ใช่ "ใช้ library security">
```

- Severity ตาม CVSS-ish: Critical = exploit ได้ทันทีไม่ต้อง auth + ผลกระทบรุนแรง
- ถ้าไม่เจอช่องโหว่ → บอกตรงๆ ว่า "ไม่พบช่องโหว่ระดับ X+ ในขอบเขตที่ตรวจ" + ระบุ scope
- **อย่ารายงาน false positive** เพื่อให้ดูครบ — รายงานเฉพาะที่ verify จากโค้ดจริงแล้ว

### Quality gates ก่อนปิดงาน mode B (mandatory)

- [ ] **Memory scanned** — quote security/feedback memory เก่าที่ relevant
- [ ] ตรวจ **trust boundary** ทุกจุดที่รับ input จากภายนอก (route handler, query param, body, header, file upload, message queue)?
- [ ] ตรวจ **auth gate** ทุก protected route — ทั้ง middleware และ handler-level (defense in depth)?
- [ ] ตรวจ **secret** ในโค้ด (`rg "password|secret|api[_-]key|token" --type ts --type vue`)?
- [ ] ตรวจ **dependency** version (`yarn audit` / `npm audit`)?
- [ ] ทุก finding มี file:line + attack scenario + fix ที่ implementable?
- [ ] **trace caller ของจุดที่เป็น vulnerability** — verify แล้วว่าไม่มี gate ชั้นบน mitigate อยู่ก่อน (ไม่ใช่ false positive)?
- [ ] **ripple ของ fix** — fix ที่เสนอไม่สร้างช่องโหว่ใหม่ / ไม่ break flow ที่ legitimate?
- [ ] **ทุก path ที่เข้าถึง resource เดียวกัน** ถูกตรวจครบ — ไม่ใช่ตรวจแค่ endpoint เดียวแล้วลืม endpoint คู่ขนาน (`/api/user/[id]` vs `/api/admin/user/[id]`)?
- [ ] **Cross-verify scan patterns** — ใช้ ≥ 2 regex pattern (หลวม + เข้ม) — ผลต้องตรงกัน (ดู `feedback_grep_multiline_attrs.md` ใน project memory)
- [ ] **ห้ามประกาศ "ปลอดภัย / ไม่มีช่องโหว่"** ก่อนผ่าน checklist นี้
- [ ] **Update skill learnings** ที่ `~/.claude/skills/sa/learnings.md` ถ้าเจอ OWASP pitfall / attack pattern / detection technique ใหม่ที่ generalize ข้าม project — append entry ตาม format ในไฟล์

---

## เลือก mode ยังไง

| Trigger | Mode |
|---------|------|
| "วิเคราะห์ requirement", "เก็บ spec", "ออกแบบ flow", "เขียน use case" | A |
| "ทำหน้าใหม่ที่ยังไม่รู้จะมี field อะไรบ้าง" | A (ก่อนส่งต่อ `ux` + `fe`) |
| "ตรวจ security", "audit auth", "หา vulnerability", "review ช่องโหว่" | B |
| "ระบบนี้ปลอดภัยพอไหม", "พร้อมขึ้น prod ไหม" | B (+ checklist infra) |
| งานครอบคลุมทั้งคู่ (เช่น "วิเคราะห์ requirement หน้า login + ตรวจ security ของ flow auth") | A → B (วิเคราะห์ก่อน แล้วค่อย audit design) |

---

## ห้ามทำ

- **อย่า implement code** — skill นี้คิด/ตรวจอย่างเดียว ส่งต่อให้ `fe` / backend skill
- **อย่า output ลอยๆ** — ทุก artifact ต้องอ้างอิง file/route/entity จริงในโปรเจกต์
- **อย่ารายงานช่องโหว่ที่ไม่ verify** — ถ้าไม่แน่ใจว่า exploit ได้จริงให้ระบุว่า "ต้องตรวจเพิ่ม" + บอกว่าต้องเช็คอะไร
- **อย่าใช้คำคลุมเครือ** — "อาจมีปัญหา security", "ควรพิจารณา performance" → ระบุให้ชัดว่า **อะไร ที่ไหน ผลกระทบยังไง**
- **อย่าสรุปจากไฟล์เดียว** — ทุก finding / suggestion ต้องผ่าน reference tracing checklist ข้างบน อย่างน้อย 1 hop ของ caller
- **อย่าเสนอ fix แบบ shallow** — ถ้าเสนอแก้จุด A ต้องระบุไปด้วยว่า A ถูกใช้ที่ B, C, D และทุกที่ต้องอัปเดตอย่างไรพร้อมกัน เพื่อกัน "fix หนึ่งจุด → bug อีกจุด"
