---
name: audit
description: Use for whole-project health sweep across 4 dimensions — Performance/bundle, Code Quality/anti-pattern, Test Coverage/quality, Dependency/supply-chain. Read-only — produces inline report only, NEVER fixes (yield to fe/migrate/debug for that). Trigger on Thai keywords audit/ตรวจสุขภาพ project/สแกนทั้งโปรเจกต์/รีวิวทั้ง project/หา bloat/หา dead code/ตรวจ dependency/project health/หา anti-pattern ทั้งโปรเจกต์/ตรวจ test coverage and English keywords audit/project audit/health check/codebase sweep/find bloat/find dead code/check deps/outdated/CVE/coverage gap/code smell/anti-pattern scan. Examples "audit project นี้ให้หน่อย", "ตรวจสุขภาพ codebase", "หา dead code ทั้งโปรเจกต์", "ตรวจ dependency มี CVE ไหม", "test coverage เป็นยังไงบ้าง", "หา bundle bloat". DO NOT use for review pending changes (use /review), security audit alone (use sa or /security-review), single-bug diagnosis (use debug), or single-file refactor (use fe).
---

# audit — Project health sweep (4 dimensions, read-only)

**Report only, never fix.** Audit คือสายตา ไม่ใช่มือ — fix ต้อง yield ไป `fe` / `migrate` / `debug`

ทุก finding ต้องมี **file:line + evidence (ตัวเลข) + suggested action** — ไม่ใช่ความเห็น

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (ดู `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: audit | cross | fe | sa` + dimension keyword (perf, dead-code, coverage, cve, bloat)
- **Learnings filter:** `~/.claude/skills/audit/learnings.md` by Tags (max 5)
- **Critical:** ใช้ memory **กรอง false-positive** — finding ที่ user เคย accept ว่า "ตั้งใจ" → ไม่ขึ้น report (หรือ downgrade เป็น info)
- **Size check:** `find . -name '*.vue' -o -name '*.ts' | wc -l` > 1000 → บอก user + เสนอ scope ย่อย

---

## Phase 1 — Stack detection

ระบุ stack เพื่อเลือก tool ที่ใช้ได้จริง:

| signal | tool ที่จะใช้ |
|---|---|
| `package.json` มี `nuxt` | `nuxi`, `vue-tsc`, bundle analyzer |
| มี `vue` (no nuxt) | `vue-tsc`, vite analyzer |
| มี `react`/`next` | `tsc`, next bundle analyzer |
| มี `vitest`/`jest`/`playwright` config | coverage tool ที่ตรงกัน |
| `pnpm-lock.yaml` / `bun.lockb` / `yarn.lock` / `package-lock.json` | ใช้ pm ตรงกัน |

ระบุใน report ว่า audit ทำบน stack อะไร — detect ไม่ได้ → ถาม user

---

## Phase 2 — Dimension scans (ขนานได้)

### มิติ 1: Performance / bundle

| scan | command / signal | finding example |
|---|---|---|
| Full-module import | `rg "import \w+ from ['\"]lodash['\"]"` | `import _ from 'lodash'` → +71KB |
| Heavy lib in client | `rg "moment\|jquery\|chart.js"` | moment → ใช้ dayjs |
| ไม่ lazy-load route | page ไม่ใช้ `defineAsyncComponent` / dynamic import | route ใหญ่ใน initial bundle |
| Image ไม่ optimize | `rg "<img"` (ไม่ใช่ `<NuxtImg>`/`<NuxtPicture>`) | static img ไม่ผ่าน pipeline |
| N+1 fetch | `useFetch` ใน loop / map | `v-for` ห่อ `useFetch` |

**ห้ามเคลม "ช้า" ถ้าไม่มีตัวเลข** — bundle KB / render count / waterfall

### มิติ 2: Code Quality / anti-pattern

| scan | command / signal | finding example |
|---|---|---|
| Dead code (export) | `rg "export "` + trace caller `rg "from ['\"].*<file>['\"]"` | export ที่ 0 caller |
| Duplicate logic | function name คล้าย + body similar | `formatDate` 3 ที่ |
| God component | `wc -l app/components/*.vue` > 500 | `OrderForm.vue` 1200 บรรทัด |
| Deep nesting | `v-if` / `v-for` ซ้อน ≥ 4 ชั้น | template nesting hell |
| Magic number | `rg "\b[0-9]{3,}\b"` ใน logic | `setTimeout(fn, 3600000)` |
| Mutation of props | `rg "props\.\w+ ="` | direct mutate prop |

**ทุก "dead code" ต้อง trace caller ≥ 1 hop ก่อนเคลม** — กฎ Universal CLAUDE.md

### มิติ 3: Test Coverage / quality

| scan | command / signal | finding example |
|---|---|---|
| Coverage gap | `coverage/coverage-summary.json` | `useAuth.ts` 0% covered, ใช้ 12 ที่ |
| Critical path no test | high-fan-in file + ไม่มี test | high blast radius, no test |
| Weak assertion | `rg "expect.*\.toBe(true\|truthy\|defined)"` | assert without value |
| No error case | test มี `it()` แต่ไม่มี `toThrow` / `rejects` | happy path only |
| Brittle timing | `rg "setTimeout\|setInterval" test/` | flaky timing test |
| Skip / focus left | `rg "(it\|describe)\.(skip\|only)" test/` | committed `.only` / `.skip` |

**Flag "critical path ไม่มี test"** (high blast radius) — ไม่ flag "test น้อย" ทั่วไป

### มิติ 4: Dependency / supply chain

| scan | command | finding example |
|---|---|---|
| Outdated | `rtk proxy pnpm outdated` / `rtk proxy npm outdated` | vue@3.4 → 3.5 (major) |
| CVE | `rtk proxy pnpm audit --prod` / `rtk proxy npm audit --omit=dev` | `lodash@4.17.20` GHSA-xxx |
| Unused dep | `package.json` deps vs `rg "from ['\"]<dep>['\"]"` | `moment` ใน deps แต่ไม่ import |
| Duplicate transitive | `rtk proxy pnpm why <pkg>` | 3 version ของ `tslib` |

**ห้ามรัน `npm install <tool>` เพื่อ scan** — ใช้ tool ที่มีอยู่; ไม่มี → suggest user

---

## Phase 3 — Filter + dedupe

- Finding ซ้ำ (30 ไฟล์ import lodash) → รวมเป็น 1 entry + count
- Finding ใน `node_modules/` / `.nuxt/` / `dist/` / `coverage/` / `*.gen.ts` → ทิ้ง
- Finding ที่ memory บอก "ตั้งใจ" → ทิ้งหรือ downgrade info

---

## Phase 4 — Severity rank

| severity | criteria |
|---|---|
| 🔴 critical | security CVE, data loss, production พังได้ |
| 🟠 high | perf > 50KB, dead code ≥ 200 line, critical path 0 test |
| 🟡 medium | duplicate logic ≥ 3, weak assertion ≥ 5, outdated major |
| 🟢 low | code smell ไม่ block, outdated minor |
| ⚪ info | observation only |

Top 10 ต่อมิติ — ที่เหลือ aggregate count

---

## Phase 5 — Inline report

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

## <Dimension> — top 10
| sev | file:line | finding | evidence | suggest |
|---|---|---|---|---|
| 🔴 | app/components/Order.vue:12 | full lodash import | +71KB bundle | `import debounce from 'lodash-es/debounce'` |
```

---

## Post-report: Fix queue (mandatory)

หลัง report ต้อง output **prioritized fix queue** ให้ user พิมพ์ "fix #N" แล้วผมรู้ทันทีว่า invoke skill ไหน + context อะไร:

```markdown
| # | sev | finding | skill | pre-brief |
|---|---|---|---|---|
| 1 | 🔴 | CVE `lodash@4.17.20` | `debug` | patch → 4.18.0, verify ด้วย pnpm audit --prod |
| 2 | 🔴 | `useAuth.ts` 0% coverage, 12 caller | `sa` → `fe` | spec happy+error path ก่อน เขียน test |
| 3 | 🟠 | full lodash import 8 ไฟล์ | `migrate` | `import _ from 'lodash'` → named import ทั้ง 8 |
```

**กฎ:**
- เรียง severity สูง → ต่ำ
- pre-brief ต้องสั้นแต่ชัดพอให้ skill ถัดไปเริ่มได้ทันที
- pattern เดียวกันหลายไฟล์ → 1 แถว + count
- **Save fix queue ลง project memory** (`project_audit_fix_queue_YYYY-MM-DD.md`) เพื่อ track ข้าม session

---

## Handoff

- **ทำเองได้** เมื่อเป็น scan + report; ไม่ touch โค้ด
- **Yield `debug`** — runtime bug จริงระหว่าง scan / CVE exploitable
- **Yield `fe`** — user ขอ fix; single-file refactor
- **Yield `migrate`** — pattern เดียวกัน ≥ 10 ไฟล์
- **Yield `sa`** — test gap บอก requirement กำกวม

---

## Quality gates

- [ ] **ทุก "dead code" ผ่าน caller-trace ≥ 1 hop** — `rg "from ['\"].*<file>['\"]"` คืน 0
- [ ] **ทุก performance claim มีตัวเลข** — KB / count / time
- [ ] **ทุก CVE มี advisory ID** — GHSA-xxx / CVE-xxx
- [ ] **ทุก finding มี file:line** — ไม่มี "หลายไฟล์ทั่ว project"
- [ ] **Cross-verify 2 patterns** ของ dead code + manual spot-check 2–3 ไฟล์
- [ ] **ไม่ติดตั้ง tool ใหม่** — suggest แทน
- [ ] **เคารพ memory** — finding ที่ user เคย accept = ไม่ขึ้น report
- [ ] **Skill learnings updated** ถ้าเจอบทเรียน generalize ข้าม project ได้

ถ้า user ต้องสั่ง "ชัวไหม / ตรวจซ้ำ" = scan แรกไม่ละเอียดพอ → memo + ปรับทันที

---

## ห้ามทำ

- ❌ **fix** — audit คือสายตา (yield ไป fe/migrate/debug)
- ❌ **flag style/format ที่ subjective** — spacing, naming preference, comment style
- ❌ **flag TODO ทุกอันว่าเป็น smell** — TODO มี context, อ่านก่อน
- ❌ **ติดตั้ง tool ใหม่** — suggest แทน
- ❌ **ใช้ severity "critical"** ถ้าไม่มี security / data-loss / production-down
- ❌ **เคลม "ปลอดภัย / clean / ครบ"** ก่อนผ่าน quality gates
- ❌ **ทำงานนอก scope** — security review เต็ม → yield `sa` mode B หรือ `/security-review`
