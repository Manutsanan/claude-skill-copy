---
name: audit
description: Use for whole-project health sweep across 4 dimensions — Performance/bundle, Code Quality/anti-pattern, Test Coverage/quality, Dependency/supply-chain. Read-only — produces inline report only, NEVER fixes (yield to fe/migrate/debug for that). Trigger on Thai keywords audit/ตรวจสุขภาพ project/สแกนทั้งโปรเจกต์/รีวิวทั้ง project/หา bloat/หา dead code/ตรวจ dependency/project health/หา anti-pattern ทั้งโปรเจกต์/ตรวจ test coverage and English keywords audit/project audit/health check/codebase sweep/find bloat/find dead code/check deps/outdated/CVE/coverage gap/code smell/anti-pattern scan. Examples "audit project นี้ให้หน่อย", "ตรวจสุขภาพ codebase", "หา dead code ทั้งโปรเจกต์", "ตรวจ dependency มี CVE ไหม", "test coverage เป็นยังไงบ้าง", "หา bundle bloat". DO NOT use for review pending changes (use /review), security audit alone (use sa or /security-review), single-bug diagnosis (use debug), or single-file refactor (use fe).
---

# audit — Project health sweep (4 dimensions, read-only)

> หลักการ: **report only, never fix** — audit คือสายตา ไม่ใช่มือ
> finding ทุกอันต้องมี **file:line + evidence + suggested action** (ไม่ใช่ความเห็น)
> งาน fix ต้อง yield ไป `fe` / `migrate` / `debug` — กันเปื้อน scope

---

## Phase 0 — Load memory hierarchy (mandatory — extend Universal Phase 0)

ลำดับ:

1. **Load global memory** — `~/.claude/memory/MEMORY.md`
   - filter: `metadata.skill: audit` / `cross` / `fe` / `sa`
   - filter ต่อด้วย keyword 4 มิติ (perf, dead code, test, dependency, bloat, lazy, lighthouse, CVE)
   - ถ้าไม่มีไฟล์ → ข้าม + หมายเหตุ "ไม่มี global memory"

2. **Load project memory** — `~/.claude/projects/<project-id>/memory/MEMORY.md`
   - project id = working directory แปลง `/` → `-`
   - filter เดียวกับ global memory
   - ถ้าไม่มี → ข้าม + หมายเหตุ "ไม่มี project memory — fresh sweep"

3. **Echo top 3-5 entries** ก่อน scan:
   ```
   📚 Memory ที่อาจ shape ผล audit:
   - [project] project_intentional_dead_code_X — keep ไว้สำหรับ migration window
   - [project] feedback_no_test_for_legacy_Y — accept ไว้แล้ว, ไม่ flag ซ้ำ
   ```

4. **ใช้กรอง false-positive** — finding ที่ตรงกับ memory ว่า "ตั้งใจ" → ไม่ขึ้น report (หรือลด severity เป็น info)

5. **หลังจบงาน** — save lesson ตาม **8 universal save triggers** ใน `~/.claude/CLAUDE.md` Universal Phase 0 #4

### Pre-flight อื่นๆ (ทำคู่กับ Phase 0)

1. **อ่าน CLAUDE.md ของโปรเจกต์** — เข้าใจ stack + business domain ก่อน scan
2. **ระบุขนาดโปรเจกต์** — `find . -name '*.vue' -o -name '*.ts' | wc -l` — ถ้า > 1000 ไฟล์ → บอก user ก่อนว่าจะใช้เวลานาน + เสนอ scope ย่อย

---

## Phase 0.5 — Load skill learnings (mandatory)

ลำดับ:

1. **Extract task keywords** — ดึง keyword จาก stack ที่ detect ใน Phase 1: framework (`nuxt`, `vue`, `react`), test tool (`vitest`, `jest`, `playwright`), package manager (`pnpm`, `bun`, `npm`), dimension (`perf`, `dead-code`, `coverage`, `cve`)
2. **อ่าน** `~/.claude/skills/audit/learnings.md` — scan เฉพาะ **Tags:** field ของแต่ละ entry
3. **Load เฉพาะ entry ที่ตรง** — entry ผ่านถ้า Tags มี ≥1 keyword ตรง **และ header ไม่มี `~~`**; ถ้าไม่มี tag ตรงหรือ header มี `~~` (deprecated) → skip ทั้ง entry
4. **Max 5 entries** — ถ้าตรงมากกว่า 5 → เลือก 5 ที่ keyword match สูงสุด; tie → เลือกที่ Date ใหม่กว่า
5. **Apply heuristic ทันที** — quote entry ที่ใช้ใน reasoning เช่น "ตาม learnings#nuxt-lodash-bloat จะ scan full import ก่อน"
6. **ถ้าไม่มี entry ตรง** → หมายเหตุ "ไม่มี skill learning ตรง — generic sweep" (ห้าม fallback โหลดทั้งไฟล์)
7. **หลังจบงาน** → ถ้าเจอ pattern ที่ generalize ข้าม project ได้ → append เข้า learnings.md (ดู Quality gates)

---

## Phase 1 — Stack detection

ก่อน scan ต้องระบุ stack เพื่อเลือก tool ที่ใช้ได้จริง:

| signal | tool ที่จะใช้ |
|---|---|
| `package.json` มี `nuxt` | `nuxi`, `vue-tsc`, bundle analyzer |
| `package.json` มี `vue` (ไม่มี nuxt) | `vue-tsc`, vite analyzer |
| `package.json` มี `react`/`next` | `tsc`, next bundle analyzer |
| มี `vitest`/`jest`/`playwright` config | coverage tool ที่ตรงกัน |
| package manager: `pnpm-lock.yaml` / `bun.lockb` / `yarn.lock` / `package-lock.json` | ใช้ package manager ตรงกัน |
| มี `.eslintrc*` | ใช้ eslint config ที่ project มีอยู่ |

ระบุใน report ตอนต้นว่า audit ทำบน stack อะไร — ถ้า detect ไม่ได้ ถาม user

---

## Phase 2 — Dimension scans (ทำขนาน 4 มิติ ได้)

### มิติ 1: Performance / bundle

| scan | command / signal | finding example |
|---|---|---|
| Full-module import | `rg "import \w+ from ['\"]lodash['\"]"` | `import _ from 'lodash'` → +71KB |
| Heavy lib in client bundle | `rg "moment\|jquery\|chart.js"` ใน client code | moment → ใช้ dayjs |
| ไม่ lazy-load route | Nuxt: page ไม่ใช้ `defineAsyncComponent` / dynamic import | route ใหญ่ใน initial bundle |
| Image ไม่ optimize | `rg "<img"` (ไม่ใช่ `<NuxtImg>`/`<NuxtPicture>`) | static img ไม่ผ่าน image pipeline |
| N+1 fetch pattern | `useFetch` ใน loop / map | `v-for` ห่อ `useFetch` |

**ห้ามเคลม "ช้า" ถ้าไม่มีตัวเลข** — bundle KB / render count / network waterfall

### มิติ 2: Code Quality / anti-pattern

| scan | command / signal | finding example |
|---|---|---|
| Dead code (export) | `rg "export (const\|function\|default)"` แล้ว trace caller ด้วย `rg "from ['\"].*<file>['\"]"` | export ที่ 0 caller |
| Duplicate logic | scan function ที่ name คล้ายกัน + body similar | `formatDate` 3 ที่ |
| God component | `wc -l app/components/*.vue` → > 500 = สงสัย | `OrderForm.vue` 1200 บรรทัด |
| Deep nesting | scan `v-if` / `v-for` ซ้อน ≥ 4 ชั้น | template nesting hell |
| Magic number | `rg "\b[0-9]{3,}\b"` ใน logic (ไม่นับ test/constant file) | `setTimeout(fn, 3600000)` |
| Mutation of props | `rg "props\.\w+ ="` | direct mutate prop |

**ทุก "dead code" ต้อง trace caller ≥ 1 hop** ก่อนเคลม — กฎ CLAUDE.md

### มิติ 3: Test Coverage / quality

| scan | command / signal | finding example |
|---|---|---|
| Coverage gap (ถ้ามี report) | อ่าน `coverage/coverage-summary.json` | `useAuth.ts` 0% covered, ใช้ 12 ที่ |
| Critical path no test | high-fan-in file (`rg "from ['\"].*useAuth['\"]"` → > 5 caller) + ไม่มี `useAuth.test.ts` | high blast radius, no test |
| Weak assertion | `rg "expect.*\.toBe(true\|truthy\|defined)"` | assert without value |
| No error case | test file มี `it(...)` แต่ไม่มี `toThrow` / `rejects` / `.catch` | happy path only |
| Brittle timing | `rg "setTimeout\|setInterval" test/` | flaky timing test |
| Skip / focus left in | `rg "(it\|describe)\.(skip\|only)"` test/ | committed `.only` / `.skip` |

**ไม่ flag "test น้อย" — flag "critical path ไม่มี test"** (high blast radius based)

### มิติ 4: Dependency / supply chain

| scan | command | finding example |
|---|---|---|
| Outdated | `rtk proxy pnpm outdated` / `rtk proxy npm outdated` / `rtk proxy bun outdated` | vue@3.4 → 3.5 (major) |
| CVE | `rtk proxy pnpm audit --prod` / `rtk proxy npm audit --omit=dev` | `lodash@4.17.20` GHSA-xxx high |
| Unused dep | grep `package.json` deps vs `rg "from ['\"]<dep>['\"]"` | `moment` ใน deps แต่ไม่ import ที่ไหน |
| Duplicate transitive | `rtk proxy pnpm why <pkg>` / `rtk proxy npm ls <pkg>` | 3 version ของ `tslib` |
| License risk | `package.json` ไม่มี `license` field / GPL ใน prod | (ถ้า relevant) |

**ห้ามรัน `npm install <tool>` เพื่อ scan** — ใช้ tool ที่มีอยู่เท่านั้น ถ้าไม่มี → suggest user ติดตั้ง

---

## Phase 3 — Filter + dedupe

- Finding ซ้ำ (เช่น 30 ไฟล์ import lodash) → รวมเป็น 1 entry + count
- Finding ที่อยู่ใน `node_modules/` / `.nuxt/` / `dist/` / `coverage/` → ทิ้ง
- Finding ที่ memory บอกว่า "ตั้งใจ" → ทิ้งหรือ downgrade เป็น info
- Finding ใน generated file (`.nuxt/`, `*.gen.ts`) → ทิ้ง

---

## Phase 4 — Severity rank

| severity | criteria |
|---|---|
| 🔴 **critical** | security CVE, data loss, ทำ production พังได้ |
| 🟠 **high** | perf > 50KB impact, dead code ≥ 200 line, critical path 0 test |
| 🟡 **medium** | duplicate logic ≥ 3, weak assertion ≥ 5, outdated major |
| 🟢 **low** | code smell ไม่ block, outdated minor |
| ⚪ **info** | observation only — เช่น stack version |

Top 10 ต่อมิติ — ที่เหลือ aggregate count

---

## Phase 5 — Inline report (output style)

```markdown
# Audit — <project name>

**Stack:** Nuxt 4.x, Vue 3.5, Vitest, pnpm
**Scope:** 247 .vue + 138 .ts files

## Summary
| มิติ | 🔴 | 🟠 | 🟡 | 🟢 | total |
|---|---|---|---|---|---|
| Performance   | 2 | 5 | 8 | 3 | 18 |
| Code Quality  | 0 | 3 | 12| 5 | 20 |
| Test Coverage | 4 | 6 | 4 | 0 | 14 |
| Dependency    | 1 | 4 | 2 | 1 | 8 |

## Performance — top 10
| sev | file:line | finding | evidence | suggest |
|---|---|---|---|---|
| 🔴 | app/components/Order.vue:12 | full lodash import | +71KB bundle | `import debounce from 'lodash-es/debounce'` |
| 🟠 | app/pages/dashboard.vue | route ไม่ lazy | 240KB initial | `defineAsyncComponent` |
...

## Code Quality — top 10
...

## Test Coverage — top 10
...

## Dependency — top 10
...

## Next steps
- Critical findings → yield ไป `debug` (CVE) / `fe` (refactor)
- Bulk pattern (≥10 ไฟล์ pattern เดียวกัน) → yield ไป `migrate`
- Missing requirement (เจอ test gap ที่ spec ไม่ชัด) → yield ไป `sa`
```

---

## Post-report: Fix queue (mandatory หลัง report เสร็จ)

หลัง report ต้อง output **prioritized fix queue** ทันที — ให้ user พิมพ์ "fix #N" แล้ว Claude รู้ทันทีว่าต้อง invoke skill อะไร + context อะไร โดยไม่ต้องอ่าน report ซ้ำ:

```markdown
## Fix queue (เรียงตาม severity)

| # | sev | finding | skill | pre-brief |
|---|---|---|---|---|
| 1 | 🔴 | CVE `lodash@4.17.20` GHSA-xxx | `debug` | patch lodash → 4.18.0, verify ด้วย pnpm audit --prod |
| 2 | 🔴 | `useAuth.ts` 0% coverage, 12 caller | `sa` → `fe` | spec test case happy+error path ก่อน แล้วเขียน test |
| 3 | 🟠 | full lodash import 8 ไฟล์ | `migrate` | แปลง `import _ from 'lodash'` → named import ทั้ง 8 ไฟล์ |
| 4 | 🟠 | `OrderForm.vue` 1200 บรรทัด | `fe` | แตก god component — extract OrderSummary, OrderItems |
```

**กฎของ fix queue:**
- เรียงจาก severity สูง → ต่ำ เสมอ
- `pre-brief` ต้องสั้นแต่ชัดพอที่ skill นั้นเริ่มทำงานได้ทันที
- finding ที่เป็น pattern เดียวกันหลายไฟล์ → รวมเป็น 1 แถว + บอก count
- **Save fix queue ลง project memory** (`project_audit_fix_queue_YYYY-MM-DD.md`) เพื่อ track progress ข้าม session — เมื่อ fix แต่ละ item เสร็จ ให้ mark ✅ ใน file

---

## Handoff

**audit ทำเองได้** เมื่อ:
- งานเป็น scan + report เฉย ๆ
- ไม่ touch โค้ดเดิม

**Yield ไป `debug`** เมื่อ:
- เจอ runtime bug จริงระหว่าง scan (ไม่ใช่ smell — ของจริง throw)
- เจอ CVE ที่ exploitable แล้ว user ต้องการ patch ทันที

**Yield ไป `fe`** เมื่อ:
- user ขอ "fix finding นี้" — audit ไม่ implement
- finding เป็น single-file refactor

**Yield ไป `migrate`** เมื่อ:
- finding เป็น pattern เดียวกัน ≥ 10 ไฟล์ (bulk transform)

**Yield ไป `sa`** เมื่อ:
- test gap บอกว่า requirement กำกวม — ต้อง spec ก่อนเขียน test

---

## Output style

- ใช้ **table** เป็นหลัก (file:line / evidence / suggest)
- ใช้ **mermaid** สำหรับ summary graph เมื่อ finding > 30
- finding ทุกอันต้องมี **file:line** + **evidence ตัวเลข** (KB / count / coverage %)
- ภาษาไทยสำหรับ business term, อังกฤษสำหรับ technical term

---

## Quality gates (mandatory ก่อนปิดงาน)

ห้ามรายงานก่อนทำครบ:

- [ ] **ทุก "dead code" ผ่าน caller-trace ≥ 1 hop** — `rg "from ['\"].*<file>['\"]"` ต้องคืน 0
- [ ] **ทุก performance claim มีตัวเลข** — KB / count / time, ไม่ใช่ "น่าจะช้า"
- [ ] **ทุก CVE มี advisory ID** — GHSA-xxx / CVE-xxx, ไม่ใช่ "อาจไม่ปลอดภัย"
- [ ] **ทุก finding มี file:line** — ไม่มี "หลายไฟล์ทั่ว project"
- [ ] **Cross-verify 2 patterns** ของ dead code — scan ด้วย `rg` + manual spot-check 2-3 ไฟล์
- [ ] **ไม่ติดตั้ง tool ใหม่** — ถ้าไม่มี ให้ suggest, ห้ามรัน `install`
- [ ] **เคารพ project memory** — finding ที่ user เคย accept = ไม่ขึ้น report
- [ ] **Update project memory** ถ้าเจอ pattern ที่กันเกิดซ้ำ
- [ ] **Update skill learnings** ที่ `~/.claude/skills/audit/learnings.md` ถ้าเจอบทเรียนที่ generalize ข้าม project ได้

ถ้า user ต้องสั่ง "ชัวไหม / ตรวจซ้ำ" = scan แรกไม่ละเอียดพอ → memo + ปรับวิธีทันที

---

## ห้ามทำ (anti-patterns)

- **ไม่ fix** — audit คือสายตา ไม่ใช่มือ (yield ไป fe/migrate/debug)
- **ไม่ flag style/format ที่ subjective** — spacing, naming preference, comment style
- **ไม่ flag ทุก TODO** ว่าเป็น code smell — TODO มี context, อ่านก่อน
- **ไม่ติดตั้ง tool ใหม่** โดยไม่ถาม — suggest แทน
- **ไม่ใช้ severity "critical"** ถ้าไม่มี security / data-loss / production-down impact
- **ไม่เคลม "ปลอดภัย / clean / ครบ"** ก่อนผ่าน quality gates
- **ไม่ทำงานนอก scope** — security review เต็มรูปแบบ ให้ yield ไป `sa` mode B หรือ /security-review
