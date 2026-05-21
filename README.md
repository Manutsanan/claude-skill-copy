# claude-skill-copy

> Skill system สำหรับ Claude Code ที่บังคับ discipline + pipeline orchestration + memory loop — version-controlled, portable ข้ามเครื่อง

**ทำอะไรได้:**
- Frontend development ที่บังคับคิดก่อนเขียน (`sa → ux → fe`)
- Debug ที่บังคับ root cause + falsification + hypothesis ledger
- Bulk migration หลายไฟล์ที่บังคับ Discover → Plan → Execute → Verify
- Project health audit 4 dimensions (perf / code quality / coverage / dependency)
- Memory loop ที่สะสม lessons ข้าม project + skill อัตโนมัติ

**Target audience:** developer ที่ใช้ Claude Code กับ frontend project (Nuxt / Vue / React / TypeScript) และอยากให้ Claude ทำงาน **สม่ำเสมอ ไม่ตามใจตัวเอง**

---

## Quickstart (impatient version)

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy
cd ~/Project/claude-skill-copy
./scripts/setup.sh
```

ดู [QUICKSTART.md](QUICKSTART.md) สำหรับ test commands

---

## Table of contents

- [Why this exists](#why-this-exists)
- [How it works](#how-it-works)
- [Install](#install)
- [How to use](#how-to-use)
- [Skills reference](#skills-reference)
- [Per-project CLAUDE.md](#per-project-claudemd)
- [Memory system](#memory-system)
- [Customize](#customize)
- [Upgrade](#upgrade)
- [Troubleshooting](#troubleshooting)
- [Philosophy](#philosophy)

---

## Why this exists

Claude Code โดยตัวเองทำงานเก่ง แต่ **ไม่สม่ำเสมอ** — บางครั้งคิดก่อนเขียน บางครั้ง implement เลย; บางครั้ง verify หลายมุม บางครั้งเชื่อ scan รอบเดียว

ระบบนี้แก้ด้วย 3 layer:

| Layer | บังคับให้ Claude ทำอะไร |
|---|---|
| **Universal Phase 0** (`~/.claude/CLAUDE.md`) | โหลด memory + echo top entries + เลือก skill ตาม decision matrix **ก่อนทำงานทุกครั้ง** |
| **Skill discipline** (`~/.claude/skills/<skill>/SKILL.md`) | แต่ละ skill มี workflow บังคับ (เช่น debug ต้องท่อง mantra + ranked hypotheses + falsify-first + ledger) |
| **Memory loop** (3-tier hierarchy) | save lessons อัตโนมัติเมื่อเจอ trigger + promote เมื่อซ้ำข้าม project |

ผลคือ Claude ทำงานเหมือนมี checklist กำกับ — ไม่ค่อย hallucinate, ไม่ค่อยลืม edge case, ไม่ค่อยเคลม "เสร็จ" ก่อน verify

---

## How it works

### 1. Phase 0 — runs before every task

ทุกครั้งที่คุณส่ง prompt ใน Claude Code Claude จะ:

```
1. Load global memory  (~/.claude/memory/MEMORY.md)
2. Load project memory (~/.claude/projects/<id>/memory/MEMORY.md)
3. Echo top 3-5 relevant entries ให้คุณเห็น
4. Check conflict — propose ขัด memory? → หยุดถามก่อน
5. Match intent → decision matrix → เลือก skill
```

ทำให้ Claude **เห็นบทเรียนที่สะสมไว้** ทุกครั้งก่อนทำงาน

### 2. Decision matrix — pick the right skill automatically

| User บอก | Skill ที่ trigger |
|---|---|
| "วิเคราะห์ / spec / requirement" | `sa` (System Analyst) |
| "ตรวจ security / audit / ช่องโหว่" | `sa` Mode B (Security Audit) |
| "ปรับ UI / responsive / animation" | `ux` |
| "เขียน component / refactor / composable" | `fe` |
| "debug / error / X พัง / ไม่ทำงาน" | `debug` |
| "migrate / แปลง pattern หลายไฟล์" | `migrate` |
| "audit project / health check" | `audit` |
| "ทำหน้าใหม่จาก mockup" | pipeline: `sa → ux → fe` |

ไม่ต้องเรียก `/skill-name` เอง — พิมพ์ภาษาไทยปกติได้

### 3. Pipeline — `sa → ux → fe → verify`

สำหรับงานใหญ่ (feature ใหม่ / redesign) Claude จะเข้า pipeline:

```
sa (spec — actor/flow/data/acceptance)
  ↓ handoff: state machine + acceptance criteria + ripple list
ux (design — component map + Tailwind plan + responsive + animation)
  ↓ handoff: Tailwind class literal + component map + visual state map
fe (code — Vue/Nuxt/TS + valibot + Nuxt UI)
  ↓
verify (run app + observe behavior)
```

**กฎ:** ห้ามสลับลำดับ — spec ต้องเสร็จก่อน design, design ต้องเสร็จก่อน code; ถ้าเจอช่องว่างกลางทาง yield กลับ skill ต้นน้ำ ไม่เดา

### 4. Skill discipline — examples

แต่ละ skill มี discipline บังคับ ตัวอย่าง:

**`debug` mantra** (ท่อง verbatim ทุก session):
> 1. First is reproducibility.
> 2. Know the fail path.
> 3. Question your hypothesis. Run disproof before proof.
> 4. Every run is a breadcrumb. Maintain the ledger.

แล้วบังคับ:
- เขียน **3-5 ranked hypotheses** ก่อน adopt
- **Run disproof first** ก่อน proof
- **Breadcrumb ledger** บันทึกทุก experiment
- ทุก hypothesis ใหม่ต้อง cross-check ทั้ง ledger

**`sa` Mode A simpler-way gate** (ก่อนเก็บ spec):
- Do nothing? — load-bearing จริงไหม
- Use existing? — มี component/composable เดิมใช้แทนได้ไหม
- Smaller scope? — แก้ 80% goal ด้วย 20% risk ได้ไหม
- Different layer? — config/schema/middleware แทน?

ตอบ rationale 1 บรรทัดต่อข้อ ก่อนเข้า spec ตัวเต็ม

### 5. Memory loop — 3 tiers + graduation

```
project memory (~/.claude/projects/<id>/memory/)
    ↓ ซ้ำ ≥ 2 projects → promote
global memory (~/.claude/memory/ — cross-project rule)
    ↓ ซ้ำ ≥ 3 projects + skill เดียวกัน → promote
skill learnings (skills/<skill>/learnings.md ใน repo)
    ↓ load-bearing พอจน skill ต้องบังคับ → promote
SKILL.md rule
```

**8 save triggers** บังคับให้ save ระหว่างทำงาน (ไม่รอจบ session):
- User แก้ทาง / confirm pattern
- เจอ error + root cause
- approach ใหม่ใช้ได้
- เจอ bug + ripple
- constraint นอกโค้ด (API limit, deprecated field)
- pattern ซ้ำ ≥ 2 ครั้ง
- session ยาว (> 20 turn)
- pipeline phase เสร็จ

→ memory จะสะสมเองโดยไม่ต้องสั่ง

---

## Install

### Prerequisites

- [Claude Code](https://claude.com/claude-code) — CLI / desktop / VS Code extension
- `git` + `bash` (zsh ใช้ได้)
- macOS / Linux / WSL (Windows native ไม่รองรับ symlink)
- **Optional:** [RTK CLI](https://github.com/skarekrow/rtk) สำหรับ token saving บน shell commands

### One-time bootstrap

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy
cd ~/Project/claude-skill-copy
./scripts/setup.sh
```

**setup.sh ทำให้ทุกอย่างที่จำเป็น (idempotent — รันซ้ำได้):**

| ขั้น | Action |
|---|---|
| 1 | Symlink 7 skills → `~/.claude/skills/<name>/` (skip ถ้ามี real dir อยู่แล้ว) |
| 2 | ติดตั้ง `~/.claude/CLAUDE.md` จาก template (skip ถ้ามี — `--force` = backup เก่าก่อน) |
| 3 | ติดตั้ง `~/.claude/RTK.md` (เหมือนกัน) |
| 4 | สร้าง `~/.claude/memory/` + `~/.claude/projects/` (เปล่า) |
| 5 | Print next steps |

**Flags:**
- `--force` — overwrite `CLAUDE.md` / `RTK.md` (backup เก่าเป็น `*.bak.YYYY-MM-DD`)
- `--skip-link` — ข้าม symlink (ถ้า link เองแล้ว)

### Verify install

```bash
ls -la ~/.claude/skills/         # ควรเห็น symlinks 7 ตัว → repo
head ~/.claude/CLAUDE.md         # ต้องขึ้น "@RTK.md" + "Universal Phase 0"
```

เปิด Claude Code ใน project ใดก็ได้ ลอง:
```
ใช้ skill debug ตรวจอะไรก่อนเริ่ม
```

ต้องเห็น Claude **ท่อง mantra 4 ข้อ verbatim**

---

## How to use

### Trigger skill — ไม่ต้องเรียกเอง

พิมพ์ภาษาไทยปกติ Claude detect intent จาก decision matrix:

```
"วิเคราะห์ requirement หน้านี้ให้หน่อย"          → sa Mode A
"ตรวจ security ของ auth flow"                  → sa Mode B
"ทำ UI ให้สวยขึ้น + responsive"                 → ux
"เขียน composable นี้ให้หน่อย"                  → fe
"ทำไม login ไม่ได้ — เจอ error 500"             → debug
"migrate native select เป็น USelect ทั้ง project" → migrate
"audit project นี้ — perf + dependency"        → audit
"ทำหน้าใหม่ list สินค้า มี filter + sort"        → sa → ux → fe pipeline
```

### Trigger skill ตรง — ใช้ slash

ถ้าอยากบังคับ skill ใดเฉพาะ:

```
/sa วิเคราะห์ flow เก็บค่าจอง
/debug หน้ากระพริบ — มี error stack มาด้วย: ...
/ux redesign หน้านี้
/fe refactor service layer
/migrate inline schema → shared/schemas/
/audit
```

### ขั้นที่ Claude จะทำในแต่ละ skill

ตัวอย่าง `/debug`:

1. **Recite mantra** verbatim (reproduce → fail path → falsify → breadcrumb)
2. **Load memory** filter by error keyword (เช่น "SelectItem", "Hydration mismatch")
3. **Read error literally** + **bottom-up stack trace**
4. **Reproduce locally** ถ้าทำได้
5. **Generate 3-5 hypotheses** เรียงตาม likelihood
6. **Run disproof first** สำหรับ hypothesis #1
7. **Maintain breadcrumb ledger** ทุก experiment
8. **Fix root cause** (ไม่ใช่ symptom)
9. **Trace ripple** — scan pattern เดียวกันที่อื่น
10. **Verify** — error หาย + ไม่มี regression
11. **Update memory** ถ้าเป็น pattern ใหม่

### Pipeline ตัวอย่าง — feature ใหม่

User: *"ทำหน้า list สินค้าใหม่ มี filter ตาม category + search + pagination"*

```
sa Mode A (System Analyst)
├── Step 0: simpler-way gate
│   - Do nothing? — ไม่ได้ user ต้องการเห็นสินค้า
│   - Use existing? — มี ProductList component เดิมแต่ไม่มี filter
│   - Smaller scope? — phase 1 = filter category ก่อน, search/pagination = phase 2
│   - Different layer? — N/A
├── Actor: customer
├── Goal: หาสินค้าตาม category + keyword
├── State machine: idle → loading → empty | results | error
├── API spec: GET /api/products?category=X&search=Y&page=N
├── Acceptance: filter category → show only matched / empty state → ข้อความ + ปุ่ม reset
└── Handoff → ux

ux (Visual Design)
├── รับ state machine จาก sa
├── component map: UInput (search) + USelect (category) + UCard list + UPagination
├── Tailwind plan: grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4
├── visual state: loading = skeleton card / empty = icon + ข้อความ / error = retry button
├── animation: stagger fade-in items (30ms each, max 5)
├── responsive: filter bar collapse บน mobile → drawer
└── Handoff → fe

fe (Implementation)
├── รับ component map + Tailwind plan
├── valibot schema: ProductFilterSchema (category, search, page)
├── composable: useProducts({ category, search, page }) — useFetch wrapper
├── component: <ProductsListPage> — UInput + USelect + grid + UPagination
├── implement state machine ตาม sa
└── handoff → verify

verify
└── เปิด browser → ทดสอบ golden + edge case → screenshot
```

---

## Skills reference

| Skill | What | When to use |
|---|---|---|
| [`sa`](skills/engineering/sa/SKILL.md) | System Analyst (Mode A) + Security Audit (Mode B) | วิเคราะห์ requirement / spec / OWASP / threat model |
| [`ux`](skills/engineering/ux/SKILL.md) | Visual + interaction design | layout / sí / animation / responsive / a11y |
| [`fe`](skills/engineering/fe/SKILL.md) | Frontend code (Nuxt/Vue/React/TS) | component / composable / state / reactivity / schema |
| [`debug`](skills/engineering/debug/SKILL.md) | Bug diagnosis | runtime error / X พัง / ไม่ทำงาน |
| [`migrate`](skills/engineering/migrate/SKILL.md) | Bulk transformation | legacy pattern → new pattern หลายไฟล์ |
| [`audit`](skills/engineering/audit/SKILL.md) | Project health sweep | perf / dead code / coverage / dependency |

ดู `SKILL.md` ของแต่ละตัวสำหรับรายละเอียดเต็ม (handoff checklist, quality gates, anti-patterns)

---

## Per-project CLAUDE.md

หลัง bootstrap แล้ว **แต่ละ project ที่คุณทำงาน ควรมี `CLAUDE.md` ของตัวเองที่ root** เพื่อบอก Claude ว่า project นี้:

- Stack อะไร (Nuxt 4 / 3 / React / Vue 3 / Svelte)
- Convention ที่ต้องตาม (naming, file structure, import alias)
- Critical rules (ห้ามทำอะไร / ต้องผ่าน wrapper ตัวไหน)
- File naming pattern

### Template

```markdown
# <Project name> — CLAUDE.md

## Stack
Nuxt 4 · TypeScript strict · Pinia · Tailwind 4 · valibot · Vitest · Yarn

## Critical Rules
- **API**: ทุก call ผ่าน `useApiFetch` — ห้าม `$fetch` ตรงใน component
- **Validation**: valibot schema ใน `shared/schemas/<domain>.ts`
- **Form**: `<UForm>` + `<UFormField>` เท่านั้น — ห้าม native `<input>` ใน form ใหม่
- **Error**: extract ผ่าน `getErrorMessage` จาก `app/utils/errorMessage.ts`
- **i18n**: ทุก string แสดงผลผ่าน `i18n/locales/`

## File Naming
| Type | Convention |
|---|---|
| Components | PascalCase (`DialogChangePassword.vue`) |
| Pages | kebab-case (`loan-contracts.vue`) |
| Services | `*.service.ts` |
| Composables | `useCamelCase.ts` |
| Schemas | kebab-case (`installment-rate.ts`) |

## Out of Scope
ห้ามแนะนำ: SSR patterns, Vuex, Options API, CSS-in-JS, native `<input>` ใน form ใหม่
```

Skill จะอ่านไฟล์นี้ใน Pre-flight ทุกครั้ง → suggest pattern ตาม convention ของคุณ

---

## Memory system

### เริ่มต้นเปล่า — สะสมเอง

หลัง bootstrap `~/.claude/memory/` ว่าง — เป็นเรื่องปกติ Phase 0 echo จะหมายเหตุ "ไม่มี memory ตรง — fresh start"

ระหว่างทำงาน Claude จะ save ลง 3 tier อัตโนมัติ:

```
~/.claude/
├── memory/                       ← Global (cross-project)
│   ├── MEMORY.md                 ← index
│   ├── user_role.md              ← user profile
│   ├── feedback_*.md             ← cross-project rules
│   └── ...
├── projects/
│   └── -Users-X-Project-Y/
│       └── memory/
│           ├── MEMORY.md         ← project index
│           ├── project_*.md      ← project-specific facts
│           ├── feedback_*.md     ← project-specific patterns
│           └── ...
└── skills/<skill>/learnings.md   ← per-skill pitfalls (ใน repo, version-controlled)
```

### Save format

```yaml
---
name: feedback-uselect-empty-value
description: Reka UI throws if SelectItem has empty string value
metadata:
  type: feedback
  skill: fe              # fe | ux | sa | debug | migrate | cross
  topic: nuxt-ui
---

ห้ามใส่ `value: ""` ใน items ของ USelect — Reka UI throw runtime error

**Why:** Reka UI v2 enforces non-empty value
**How to apply:** ใช้ `null` หรือ string sentinel + convert ที่ API boundary
```

### Distillation — กัน memory เน่า

หลังใช้ ~3 เดือน memory จะเริ่มมี entries ที่ stale (code reference ไม่ตรงแล้ว). รัน:

```
/distill-memory
```

(ถ้ามี skill นี้ available) หรือ manual review:

1. เปิด MEMORY.md แต่ละ tier
2. ทุก entry ถาม: "ยังจริงไหม? code ที่อ้างยังมีไหม?"
3. ไม่จริง → ลบ; ซ้ำ ≥ 2 projects → promote ขึ้น tier บน

ดู [FOLLOWUPS.md](FOLLOWUPS.md) สำหรับ schedule

---

## Customize

### Fork + แก้

```bash
# fork ผ่าน GitHub UI แล้ว clone ของตัวเอง
git clone https://github.com/<your-username>/claude-skill-copy.git ~/Project/my-skills
cd ~/Project/my-skills
./scripts/setup.sh
```

แก้ SKILL.md / CLAUDE.template.md ใน fork ของตัวเอง — commit + push → ครั้งหน้า `git pull` ได้ของตัวเอง

### เพิ่ม skill ใหม่

```bash
cd ~/Project/claude-skill-copy
cp -R skills/misc/_template skills/in-progress/my-new-skill
# แก้ skills/in-progress/my-new-skill/SKILL.md (name + description + content)
# ลองใช้ — รัน link-skills.sh จะข้าม in-progress/ (ปลอดภัย)
```

พอ skill พร้อม ship:
1. ย้ายไป `skills/engineering/` หรือ `skills/misc/`
2. เพิ่ม entry ใน README ([Skills reference](#skills-reference))
3. เพิ่มใน `.claude-plugin/plugin.json`
4. รัน `./scripts/link-skills.sh` อีกครั้ง

### Buckets

| Bucket | Linked? | Purpose |
|---|---|---|
| `skills/engineering/` | ✅ | daily code work |
| `skills/misc/` | ✅ | meta utilities (templates, etc.) |
| `skills/in-progress/` | ❌ | drafts ที่ยังไม่พร้อม |
| `skills/deprecated/` | ❌ | retired (ไม่ลบ — เก็บ history) |

`link-skills.sh` ข้าม `in-progress/` + `deprecated/` + `personal/` → ลอง skill ใหม่โดยไม่ pollute live

---

## Upgrade

### Pull update จาก upstream

```bash
cd ~/Project/claude-skill-copy
git pull
# Skills auto-update ผ่าน symlinks — ไม่ต้องทำอะไรเพิ่ม
```

### ถ้า CLAUDE.template.md เปลี่ยน

```bash
./scripts/setup.sh --force
# Backup ของเก่า → ~/.claude/CLAUDE.md.bak.YYYY-MM-DD
# แทนที่ด้วย version ใหม่
```

Memory ของคุณ (`~/.claude/memory/`, `~/.claude/projects/`) **ไม่ถูกแตะ** — repo ไม่มี logic ลบ memory

---

## Troubleshooting

### setup.sh บอกว่า `~/.claude/skills/` เป็น real dir ไม่ overwrite

```bash
# Backup ก่อน เผื่อมีของสำคัญ
mv ~/.claude/skills ~/.claude/skills.backup-$(date +%Y-%m-%d)
mkdir ~/.claude/skills
./scripts/setup.sh
```

### Symlinks ไม่ทำงานบน Windows

Windows native filesystem (NTFS ไม่ผ่าน WSL) symlink ต้อง admin. ใช้:
- WSL 2 + Ubuntu — recommended
- หรือ Git Bash with admin (slower)

### `rtk: command not found`

RTK CLI optional — skill ใช้ได้แต่บาง command ใน skill อ้าง `rtk proxy yarn` / `rtk proxy pnpm`. ทางแก้:
1. Install RTK ([github.com/skarekrow/rtk](https://github.com/skarekrow/rtk)) — recommended ถ้าต้องการ token saving
2. หรือ ignore — skill ส่วนใหญ่ยังทำงาน, แค่ shell commands บางตัว fail

### Skill ไม่ trigger เลย

เช็ค:
```bash
ls -la ~/.claude/skills/
# ต้องเห็น symlinks (`-> /Users/.../Project/claude-skill-copy/...`)
```

ถ้าเป็น real dir → setup.sh ไม่ได้ link สำเร็จ → ดู step ข้างบน

### Claude ไม่ทำตาม discipline ใน SKILL.md

เช็คว่า `~/.claude/CLAUDE.md` มีจริงไหม:
```bash
cat ~/.claude/CLAUDE.md | head -5
# ต้องเห็น "@RTK.md" + "Universal Phase 0"
```

ถ้าไม่มี → `./scripts/setup.sh` (ไม่ใช้ `--force` ก็พอ — จะ install ให้)

### Memory ไม่ save อัตโนมัติ

Memory save trigger อยู่ใน CLAUDE.md (8 triggers). ถ้า CLAUDE.md ไม่ถูก install ตรง path → Claude ไม่รู้ trigger. เช็ค:
```bash
grep -l "Universal save triggers" ~/.claude/CLAUDE.md
```

ถ้าไม่ขึ้น → re-install: `./scripts/setup.sh --force`

---

## Philosophy

### Discipline > playbook

Skill ทุกตัวเขียนเป็น **discipline + workflow** ไม่ใช่ "ทำตามขั้นตอน 1, 2, 3 แล้วเสร็จ" — เพราะ playbook strict เกินไป handle edge case ไม่ได้

ตัวอย่าง `debug` ไม่ได้บอก "หา bug ตามลำดับ" — แต่บังคับ:
- ท่อง mantra (กัน drift)
- เขียน 3-5 hypotheses (กัน anchoring bias)
- Run disproof ก่อน proof (กัน fix-by-coincidence)
- Cross-check ledger ทุก hypothesis ใหม่ (กัน ลืม contradicting evidence)

Discipline ไม่ใช่ "ทำอะไรต่อไป" แต่เป็น "ห้ามทำอะไร"

### Memory > prompt engineering

Prompt engineering = บอก Claude ใน turn เดียว
Memory = บอก Claude **ทุกครั้ง** ที่เกิด pattern คล้ายๆ เดิม

ระบบนี้สะสม lesson เอง — ครั้งแรก user แก้ทาง → save; ครั้งที่ 2 Claude echo ก่อนทำซ้ำ; ครั้งที่ 5 ใน project อื่น → promote ขึ้น global; ครั้งที่ 10 ในข้าม project → promote ขึ้น skill learnings (ใน repo)

ผลคือ skill ฉลาดขึ้นเอง โดยไม่ต้อง edit SKILL.md ทุกครั้ง

### Portability without uniformity

Repo ทำ **discipline + pipeline** ให้ portable — memory ให้ accumulate per-user

→ ทุกเครื่องมี skill behavior เหมือนกัน
→ แต่ละเครื่องมี lesson ของตัวเอง

นี่คือเหตุผลที่ repo มี `CLAUDE.template.md` (รูปแบบ) แต่ไม่มี `memory.template/` (เนื้อหา)

---

## License

MIT (ใช้ฟรี, fork ได้, แก้ได้)

## Credits

Inspired by [9arm-skills](https://github.com/thananon/9arm-skills) — discipline-based skill structure (debug-mantra, scrutinize, post-mortem pattern)

## Contributing

Pull request welcome — แต่ skill ใหม่ต้องผ่าน promotion gate:
1. Draft ใน `skills/in-progress/`
2. ใช้จริง ≥ 2 สัปดาห์ + พิสูจน์ว่า catch อะไรที่ skill เดิมไม่ catch
3. ย้ายไป `engineering/` หรือ `misc/` + เพิ่ม entry ใน README + plugin.json

Skill ที่ "ดูดีในกระดาษ" แต่ไม่ catch อะไรจริง = ceremony เปล่ากิน token → ไม่ accept
