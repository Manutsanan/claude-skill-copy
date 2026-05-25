# claude-skill-copy

> Skill system สำหรับ Claude Code ที่บังคับ discipline + pipeline orchestration + memory loop — version-controlled, portable ข้ามเครื่อง

**ทำอะไรได้:**
- Frontend development ที่บังคับคิดก่อนเขียน (`sa → ux → fe → verify`)
- Debug ที่บังคับ root cause + falsification + hypothesis ledger
- Bulk migration หลายไฟล์ที่บังคับ Discover → Plan → Execute → Verify
- Project health audit 4 dimensions (perf / code quality / coverage / dependency)
- Memory loop 3-tier ที่สะสม lessons ข้าม project + skill อัตโนมัติ
- Phase checkpoint ที่ resume pipeline งานใหญ่ข้าม session ได้
- **Semantic ripple check ผ่าน CodeGraph MCP** — รู้ทันทีว่า symbol ถูก call จากไหน + กระทบอะไร แทน grep ทั้ง project

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
  - [Phase 0 — runs before every task](#1-phase-0--runs-before-every-task)
  - [Decision matrix — pick the right skill](#2-decision-matrix--pick-the-right-skill)
  - [Pipeline `sa → ux → fe → verify`](#3-pipeline-sa--ux--fe--verify)
  - [Mid-task yield + ripple check](#4-mid-task-yield--ripple-check)
  - [Skill discipline — examples](#5-skill-discipline--examples)
  - [Memory loop — 3 tiers + graduation](#6-memory-loop--3-tiers--graduation)
- [Install](#install)
  - [Prerequisites](#prerequisites)
  - [One-time bootstrap](#one-time-bootstrap)
  - [Lint tooling](#lint-tooling-skill--memory-frontmatter-validator)
  - [Browser automation (chrome-devtools MCP)](#browser-automation-chrome-devtools-mcp)
  - [Codebase intelligence (CodeGraph MCP)](#codebase-intelligence-codegraph-mcp)
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

ระบบนี้แก้ด้วย 3 layer + 3 MCP:

| Layer | บังคับให้ Claude ทำอะไร |
|---|---|
| **Universal Phase 0** (`~/.claude/CLAUDE.md`) | โหลด memory + scan phase checkpoint + echo top entries + เลือก skill ตาม decision matrix **ก่อนทำงานทุกครั้ง** |
| **Skill discipline** (`~/.claude/skills/<skill>/SKILL.md`) | แต่ละ skill มี workflow บังคับ (เช่น debug ต้องท่อง mantra + ranked hypotheses + falsify-first + ledger) |
| **Memory loop** (3-tier hierarchy) | save lessons อัตโนมัติเมื่อเจอ trigger + promote เมื่อซ้ำข้าม project |

| MCP | ทำอะไร | Skill ที่ใช้ |
|---|---|---|
| **RTK** (Rust Token Killer) | กรอง shell output → ลด token 60-90% | ทุก skill (via hook อัตโนมัติ) |
| **chrome-devtools** | observe browser runtime — error, network, state, a11y | `debug` / `ux` / `fe` / `audit` |
| **CodeGraph** | semantic codebase graph — callers, impact, trace, context | ทุก skill ที่ทำ ripple check |
| **Context7** | live library docs ตามเวอร์ชัน — ป้องกัน hallucinated API | `fe` / `debug` / `migrate` / `sa` |

ผลคือ Claude ทำงานเหมือนมี checklist กำกับ — ไม่ค่อย hallucinate, ไม่ค่อยลืม edge case, ไม่ค่อยเคลม "เสร็จ" ก่อน verify

---

## How it works

### 1. Phase 0 — runs before every task

ทุกครั้งที่คุณส่ง prompt ใน Claude Code Claude จะ:

```
1. Load global memory       (~/.claude/memory/MEMORY.md)
2. Load project memory      (~/.claude/projects/<id>/memory/MEMORY.md)
3. Scan phase checkpoint    (project_phase_checkpoint_*.md)
   └─ status: in_progress → echo + ถามว่า resume หรือ เริ่มใหม่
4. Echo top 3-5 relevant entries ให้คุณเห็น
5. Conflict check — propose ขัด memory? → หยุดถามก่อน
6. Token efficiency gate    (quality gate compact + rtk proxy commands)
7. Match intent → decision matrix → เลือก skill
```

ทำให้ Claude **เห็นบทเรียนที่สะสมไว้ + งานค้างจาก session ก่อน** ทุกครั้งก่อนทำงาน

> **Phase checkpoint** — เมื่อ pipeline phase (sa/ux/fe) เสร็จ Claude save artifact เป็น `project_phase_checkpoint_<phase>_YYYY-MM-DD.md` ใน project memory โดยมี `status: in_progress` ถ้า session ใหม่เริ่มก่อน phase ถัดไปเริ่ม → echo ให้ resume ต่อได้ไม่หลุด context
>
> **Token efficiency rule** — Quality gate ของทุก skill ถ้าผ่านครบจะ output แค่ `✅ quality gates passed` 1 บรรทัด (ไม่ dump checklist เต็ม); `yarn`/`npm`/`pnpm` ใช้ผ่าน `rtk proxy yarn ...` เสมอ (ไม่ถูก RTK filter อัตโนมัติ)

### 2. Decision matrix — pick the right skill

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
| "ตรวจ security flow แล้ว fix" | `sa → fe` (ข้าม ux) |
| "debug แล้วต้อง redesign data model" | `debug → sa → fe` |
| "migrate ที่ต้องเปลี่ยน data shape" | `sa → migrate` |
| คำสั่งสั้น / กำกวม / intent ไม่ชัด | **ไม่เรียก skill** — ถาม 1 คำถามก่อน |

ไม่ต้องเรียก `/skill-name` เอง — พิมพ์ภาษาไทยปกติได้

### 3. Pipeline `sa → ux → fe → verify`

สำหรับงานใหญ่ (feature ใหม่ / redesign) Claude จะเข้า pipeline:

```
sa (spec — actor / flow / data / acceptance / state machine)
  ↓ handoff: state machine + acceptance criteria + ripple list
ux (design — component map + Tailwind plan + responsive + animation)
  ↓ handoff: Tailwind class literal + component map + visual state map
fe (code — Vue/Nuxt/TS + valibot + Nuxt UI)
  ↓ handoff: implementation summary
verify (run app + observe behavior + screenshot)
```

**กฎ:**
- ห้ามสลับลำดับ — spec ต้องเสร็จก่อน design, design ต้องเสร็จก่อน code
- ขั้นที่ skip ได้ คือขั้นที่ **input ของขั้นนั้นมีอยู่แล้ว** (เช่น มี spec ชัด → skip sa; ไม่มี UI เปลี่ยน → skip ux)
- ทุกขั้น **handoff artifact ที่ขั้นถัดไปใช้ได้จริง** + save เป็น phase checkpoint
- ถ้าเจอช่องว่างกลางทาง yield กลับ skill ต้นน้ำ ไม่เดา

### 4. Mid-task yield + ripple check

**Mid-task yield** — ระหว่างทำงานใน skill หนึ่ง ถ้าเจอประเด็นนอก scope → หยุด + yield ไป skill ที่เหมาะสม ไม่ทำต่อด้วย skill ผิด

ตัวอย่าง:
- กำลัง `fe` แล้วพบช่องโหว่ security → **yield ไป `sa` Mode B** ก่อน fix
- กำลัง `ux` แล้วพบว่า requirement ไม่ครบ (ไม่รู้ empty state ควร render อะไร) → **yield ไป `sa` Mode A**
- กำลัง `sa` วิเคราะห์ bug แล้วเจอว่ารากปัญหาคือ reactivity → **yield ไป `fe` review mode**

**Cross-skill ripple check** — ก่อน touch โค้ดเดิม ทุก skill ต้อง:

1. **trace caller / consumer** — prefer `mcp__codegraph__callers <symbol>` (semantic, instant); fallback `rg "symbol"` สำหรับ symbol ใหม่ใน session หรือ literal string pattern
2. **trace shared invariant** — shared state / type / schema / route gate?
3. **trace persistence** — localStorage / DB / cache จะ corrupt ไหมถ้า shape เปลี่ยน?
4. **trace cross-tab / cross-page sync** — `storage` event / WebSocket / SSE broadcast?
5. **list ripple files** — ทุกไฟล์ที่ต้องแก้พร้อมกัน ระบุชัดก่อนเริ่มแก้

หลัก **"แก้จุดเดียว → bug อีกจุด"** ห้ามเกิดเด็ดขาด

### 5. Skill discipline — examples

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

### 6. Memory loop — 3 tiers + graduation

```
project memory (~/.claude/projects/<id>/memory/)
    ↓ ซ้ำ ≥ 2 projects → promote
global memory (~/.claude/memory/ — cross-project rule)
    ↓ ซ้ำ ≥ 3 projects + skill เดียวกัน → promote
skill learnings (skills/<skill>/learnings.md ใน repo)
    ↓ load-bearing พอจน skill ต้องบังคับ → promote
SKILL.md rule
```

**9 save triggers** บังคับให้ save ระหว่างทำงาน (ไม่รอจบ session):
1. User แก้ทาง / บอกผิด
2. User confirm pattern ที่ไม่ obvious
3. เจอ error + root cause
4. งานสำเร็จด้วย approach ใหม่ที่ใช้ได้จริง
5. เจอ bug ที่หาที่มาได้ + ripple list
6. constraint นอกโค้ด (API limit, deprecated field)
7. pattern ซ้ำ ≥ 2 ครั้ง ในงานเดียว
8. session ยาว (> 20 turn)
9. **pipeline phase เสร็จ** — save phase checkpoint ก่อน handoff

→ memory จะสะสมเองโดยไม่ต้องสั่ง

---

## Install

### Prerequisites

- [Claude Code](https://claude.com/claude-code) — CLI / desktop / VS Code extension
- `git` + `bash` (zsh ใช้ได้)
- macOS / Linux / WSL (Windows native ไม่รองรับ symlink)
- **Auto-installed by setup.sh** (via brew/apt/dnf/yum/pacman): `ripgrep`, `python3`, `jq`, plus `chrome-devtools` MCP (via `claude mcp add`)
- **Soft prerequisites (warn-only if missing):** Node.js 18+ (สำหรับ MCP), Chrome/Chromium (สำหรับ browser automation)
- **Optional:** [RTK CLI](https://github.com/skarekrow/rtk) สำหรับ token saving บน shell commands
- **Optional:** [CodeGraph](https://github.com/colbymchenry/codegraph) สำหรับ semantic ripple check (แทน grep) — ดู [install section](#codebase-intelligence-codegraph-mcp)

### One-time bootstrap

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy
cd ~/Project/claude-skill-copy
./scripts/setup.sh
```

**setup.sh ทำให้ทุกอย่างที่จำเป็น (idempotent — รันซ้ำได้):**

| ขั้น | Action |
|---|---|
| 0 | ตรวจ + ติดตั้ง system deps (ripgrep + python3 + jq auto-install via package manager; curl/Node/Chrome detect + warn) |
| 1 | Symlink 7 skills → `~/.claude/skills/<name>/` (skip ถ้ามี real dir อยู่แล้ว) |
| 2 | ติดตั้ง `~/.claude/CLAUDE.md` จาก template (skip ถ้ามี — `--force` = backup เก่าก่อน) |
| 3 | ติดตั้ง `~/.claude/RTK.md` (เหมือนกัน) |
| 4 | สร้าง `~/.claude/memory/` + `~/.claude/projects/` (เปล่า) |
| 5 | ติดตั้ง lint tooling — venv + PyYAML + symlink scripts/hook + register PostToolUse hook (deps `python3` + `jq` ถูก auto-install ใน step 0 แล้ว) |
| 6 | Register `chrome-devtools` MCP at user scope via `claude mcp add` (idempotent; powers debug/ux/audit/fe browser playbooks) |
| 7 | Print summary + missing-soft-deps checklist |

**Flags:**
- `--force` — overwrite `CLAUDE.md` / `RTK.md` (backup เก่าเป็น `*.bak.YYYY-MM-DD`)
- `--skip-link` — ข้าม symlink (ถ้า link เองแล้ว)
- `--skip-deps` — ข้าม auto-install ของ system dependencies (ripgrep)
- `--skip-mcp` — ข้าม chrome-devtools MCP register (ถ้าไม่อยากได้ browser automation)

### Lint tooling (skill + memory frontmatter validator)

`setup.sh` ติดตั้ง lint script ที่ตรวจสุขภาพของ skill/memory files หลังทุก Edit/Write (warn-only — ไม่ block edit)

**ตรวจอะไร:**
- Frontmatter parse ได้ (strict YAML → lenient fallback สำหรับ prose ที่มี `: `)
- Required fields (`name`, `description`) ครบ
- `metadata.type` ∈ `{user, feedback, project, reference}`
- `metadata.skill` ∈ `{fe, ux, sa, debug, migrate, audit, cross}`
- `metadata.scope` ∈ `{global, project}`
- `name` เป็น kebab-case + ตรงกับ filename (normalize `_` ↔ `-`)
- Skill folder มี `SKILL.md` + symlink target มีอยู่จริง
- MEMORY.md index ตรงกับไฟล์บน disk
- ไม่มี orphan `[[link]]` ใน memory body

**Manual run:**
```bash
~/.claude/scripts/lint-skills.py              # full sweep (skills + global + project memories)
~/.claude/scripts/lint-skills.py PATH         # specific file or directory
```

**Hook behavior:** PostToolUse fire เฉพาะเมื่อ Edit/Write/NotebookEdit touch path ที่ขึ้นต้นด้วย `~/.claude/skills/`, `~/.claude/memory/`, หรือ `~/.claude/projects/*/memory/` — exit 0 เสมอ ถ้ามี warning/error จะ print ผ่าน stderr ให้ user เห็นใน Claude Code transcript

### Browser automation (chrome-devtools MCP)

`setup.sh` register `chrome-devtools` MCP at user scope ทันที — skill `debug` / `ux` / `audit` / `fe` มี playbook ในตัวสำหรับ browser automation (reproduce, snapshot, lighthouse, perf trace, memory leak detection)

**ROI โดยประมาณ** (เทียบกับไม่มี MCP):

| Skill | Quality lift | Token overhead |
|---|---|---|
| `verify` / `debug` | +50-80% | +30-60% |
| `ux` (visual + responsive + a11y) | +30-50% | +50-120% |
| `audit` (perf/a11y dimension) | +40-70% | +60-150% |
| `fe` (opt-in for reactivity/hydration) | +10-25% | +20-40% |

**Token discipline:** CLAUDE.md มี dedicated section "Chrome DevTools MCP integration" — Token cost reference + Broad-vs-narrow decision rule + Token-saving toolkit (3 tiers: Safe-always / Context-dependent / Avoid-by-default) + Decision flow ที่ Claude ต้องเดินก่อนเรียก browser tool ทุกครั้ง

**Graceful degradation:** ถ้า MCP ไม่พร้อม (Chrome ไม่ลง / dev server ไม่ขึ้น / user ปิด MCP) — ทุก skill มี **Fallback section** ที่ระบุชัดว่าจะ degrade ยังไง (ขอ user paste screenshot, verify ด้วย code-level เท่านั้น, etc.) ไม่ crash, ไม่ block

**Verify MCP install:**
```bash
claude mcp list                       # ต้องเห็น "chrome-devtools"
```

### Codebase intelligence (CodeGraph MCP)

CodeGraph เพิ่ม semantic graph traversal ให้ ripple check ทุก skill — แทนที่ `rg "symbol"` ด้วย graph traversal ที่รู้ callers จริง, call path, และ cascading impact

**1. Install binary:**
```bash
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

**2. Register MCP** — เพิ่มใน `~/.claude.json` ที่ key `mcpServers`:
```json
"codegraph": {
  "type": "stdio",
  "command": "/Users/<you>/.local/bin/codegraph",
  "args": ["serve", "--mcp"]
}
```

**3. Init index ต่อ project** (รัน 1 ครั้งต่อ project):
```bash
cd /path/to/project
codegraph init -i
```

สร้าง `.codegraph/codegraph.db` — index จะ auto-sync หลังจากนั้น (lag ~1-2s หลัง edit)

**Tools ที่ได้ (namespaced เป็น `mcp__codegraph__*`):**

| Tool | ใช้เมื่อ |
|---|---|
| `callers <symbol>` | Ripple check — ใครเรียก symbol นี้ (แทน grep) |
| `impact <symbol>` | ถ้าแก้ symbol นี้จะกระทบอะไรบ้าง |
| `trace <symbol>` | Call path จาก crash site → ต้นตอ (debug) |
| `context <file>` | เข้าใจ file นี้ทำอะไร + เชื่อมกับอะไร (sa) |
| `search <keyword>` | หา symbol ที่ไม่รู้ชื่อแน่ |
| `explore <s1> <s2>` | ดู source หลาย symbol พร้อมกัน (migrate) |
| `callees <symbol>` | symbol นี้ call อะไร (outgoing) |
| `node <symbol>` | Symbol details — type, location, signature |

**ROI ต่อ skill:**

| Skill | What improves | Token cost |
|---|---|---|
| `sa` / `fe` | Ripple list เชิง semantic — ไม่มี comment/string noise | ~200-500 🟢 |
| `debug` | Trace call chain จาก crash site ทันที | ~200-500 🟢 |
| `migrate` | Discover scope ด้วย callers graph ก่อน regex | ~200-500 🟢 |
| `sa` impact | วิเคราะห์ cascading effect ก่อน change | ~500-1k 🟡 |

**Graceful degradation:** ถ้า project ยังไม่ได้ init → CodeGraph return empty → skill fallback `rg` อัตโนมัติ + แจ้ง user

**Verify:**
```bash
codegraph --version                   # ต้องขึ้น version
```

### Live library documentation (Context7 MCP)

Context7 ดึง docs จริงของ external library ตามเวอร์ชัน มาใส่ใน prompt แทน training data เก่า — ป้องกัน hallucinated API และ breaking change ที่ไม่รู้ตัว

**Install:**
```bash
./scripts/setup.sh --with-context7
```

Or manually — เพิ่มใน `~/.claude.json` ที่ key `mcpServers`:
```json
"context7": {
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp@latest"]
}
```

**Tools ที่ได้ (namespaced เป็น `mcp__context7__*`):**

| Tool | ใช้เมื่อ |
|---|---|
| `resolve-library-id` | แปลง library name → Context7-compatible ID (e.g. `/nuxt/ui`) |
| `query-docs` | ดึง docs สำหรับ library + query ที่ระบุ (narrow เสมอ) |

**ROI ต่อ skill:**

| Skill | What improves | Token cost |
|---|---|---|
| `fe` | API verified ก่อน implement — ไม่ hallucinate method signature | ~500-2k 🟢 |
| `debug` | ตรวจ breaking change ก่อน test hypothesis — ลด wasted experiments | ~500-1k 🟢 |
| `migrate` | Migration guide จริงก่อน bulk transform | ~500-2k 🟢 |
| `sa` | Library API spec verified ก่อน commit (opt-in) | ~500-1k 🟢 |

**Query discipline — narrow เสมอ:**
```
# ✅ ~500 tokens
mcp__context7__query-docs libraryId="/nuxt/ui" query="UButton loading prop"

# ❌ ~5-10k tokens (ห้าม)
mcp__context7__query-docs libraryId="/nuxt/ui" query="Nuxt UI"
```

**Graceful degradation:** ถ้า library ไม่อยู่ใน index → แจ้ง user + fallback อ่าน official docs จาก training data

---

### Verify install

```bash
ls -la ~/.claude/skills/         # ควรเห็น symlinks 7 ตัว → repo
head ~/.claude/CLAUDE.md         # ต้องขึ้น "@RTK.md" + "Universal Phase 0"
claude mcp list                  # ต้องเห็น "chrome-devtools" (ถ้าไม่ใช้ --skip-mcp)
codegraph --version              # ถ้าติดตั้ง CodeGraph แล้ว
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
└── Handoff → ux + save project_phase_checkpoint_sa_YYYY-MM-DD.md

ux (Visual Design)
├── รับ state machine จาก sa
├── component map: UInput (search) + USelect (category) + UCard list + UPagination
├── Tailwind plan: grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4
├── visual state: loading = skeleton card / empty = icon + ข้อความ / error = retry button
├── animation: stagger fade-in items (30ms each, max 5)
├── responsive: filter bar collapse บน mobile → drawer
└── Handoff → fe + save project_phase_checkpoint_ux_YYYY-MM-DD.md

fe (Implementation)
├── รับ component map + Tailwind plan
├── valibot schema: ProductFilterSchema (category, search, page)
├── composable: useProducts({ category, search, page }) — useFetch wrapper
├── component: <ProductsListPage> — UInput + USelect + grid + UPagination
├── implement state machine ตาม sa
└── handoff → verify + save project_phase_checkpoint_fe_YYYY-MM-DD.md

verify
└── เปิด browser → ทดสอบ golden + edge case → screenshot
```

ถ้าหยุดกลาง pipeline แล้วเปิด session ใหม่ → Phase 0 scan checkpoint เจอ → ถามว่า resume ต่อหรือเริ่มใหม่

---

## Skills reference

| Skill | What | When to use | Browser MCP | Extras |
|---|---|---|---|---|
| [`sa`](skills/engineering/sa/SKILL.md) | System Analyst (Mode A) + Security Audit (Mode B) | วิเคราะห์ requirement / spec / OWASP / threat model | — | [`learnings.md`](skills/engineering/sa/learnings.md) |
| [`ux`](skills/engineering/ux/SKILL.md) | Visual + interaction design | layout / color / animation / responsive / a11y | ✅ visual + responsive + a11y | [`learnings.md`](skills/engineering/ux/learnings.md) |
| [`fe`](skills/engineering/fe/SKILL.md) | Frontend code (Nuxt/Vue/React/TS) | component / composable / state / reactivity / schema | 🟡 opt-in (reactivity/hydration) | [`learnings.md`](skills/engineering/fe/learnings.md) · [`REFERENCE.md`](skills/engineering/fe/REFERENCE.md) |
| [`debug`](skills/engineering/debug/SKILL.md) | Bug diagnosis | runtime error / X พัง / ไม่ทำงาน | ✅ reproduce + inspect | [`learnings.md`](skills/engineering/debug/learnings.md) |
| [`migrate`](skills/engineering/migrate/SKILL.md) | Bulk transformation | legacy pattern → new pattern หลายไฟล์ | — | [`learnings.md`](skills/engineering/migrate/learnings.md) |
| [`audit`](skills/engineering/audit/SKILL.md) | Project health sweep (read-only) | perf / dead code / coverage / dependency | ✅ lighthouse + perf trace | [`learnings.md`](skills/engineering/audit/learnings.md) |
| [`_template`](skills/misc/_template/SKILL.md) | Skeleton สำหรับสร้าง skill ใหม่ | copy แล้วแก้ตาม use case | — | — |

**ไฟล์ในแต่ละ skill folder:**
- `SKILL.md` — discipline + workflow + handoff checklist (Claude อ่านทุกครั้งที่ skill trigger)
- `learnings.md` — cross-project pitfalls ที่ graduate มาจาก project memory (Phase 0.5 load)
- `REFERENCE.md` — long-form reference (fe เท่านั้นตอนนี้ — Nuxt 4 / valibot / Nuxt UI cheatsheet)

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
│           ├── MEMORY.md                            ← project index
│           ├── project_*.md                         ← project-specific facts
│           ├── feedback_*.md                        ← project-specific patterns
│           ├── project_phase_checkpoint_sa_*.md     ← phase artifact (resume)
│           ├── project_phase_checkpoint_ux_*.md
│           ├── project_phase_checkpoint_fe_*.md
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
  skill: fe              # fe | ux | sa | debug | migrate | audit | cross
  topic: nuxt-ui
---

ห้ามใส่ `value: ""` ใน items ของ USelect — Reka UI throw runtime error

**Why:** Reka UI v2 enforces non-empty value
**How to apply:** ใช้ `null` หรือ string sentinel + convert ที่ API boundary
```

### Phase checkpoint format

```yaml
---
name: project-phase-checkpoint-sa-2026-05-22
description: SA spec สำหรับ feature list สินค้า — handoff ไป ux
metadata:
  type: project
  phase: sa              # sa | ux | fe
  status: in_progress    # → complete เมื่อ handoff สำเร็จ
---

<artifact ที่ phase ถัดไปต้องใช้ — state machine / API spec / acceptance>
```

ครั้งถัดที่เปิด Claude Code ใน project เดียวกัน → Phase 0 จะ scan เจอ + ถามว่า resume

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
# ลองใช้ — link-skills.sh จะข้าม in-progress/ (ปลอดภัย)
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

Memory save trigger อยู่ใน CLAUDE.md (9 triggers). ถ้า CLAUDE.md ไม่ถูก install ตรง path → Claude ไม่รู้ trigger. เช็ค:
```bash
grep -l "Universal save triggers" ~/.claude/CLAUDE.md
```

ถ้าไม่ขึ้น → re-install: `./scripts/setup.sh --force`

### CodeGraph tools ไม่ทำงาน / return empty

1. เช็คว่า project มี index: `ls .codegraph/codegraph.db` — ถ้าไม่มี → `codegraph init -i`
2. เช็ค binary อยู่ใน PATH: `which codegraph` — ถ้าไม่เจอ → ดู install path (`~/.local/bin/codegraph`) แล้วอัปเดต `~/.claude.json`
3. Restart Claude Code เพื่อ reload MCP server ใหม่
4. ถ้ายังไม่ทำงาน → skill จะ fallback `rg` ให้อัตโนมัติ — ไม่ crash

### Phase checkpoint ไม่ resume

Phase 0 step 3 จะ scan `project_phase_checkpoint_*.md` ใน `~/.claude/projects/<id>/memory/`. ถ้าไม่ resume:
1. เช็คว่ามีไฟล์จริง: `ls ~/.claude/projects/<your-project-id>/memory/project_phase_checkpoint_*`
2. เช็ค frontmatter `status:` — ถ้าเป็น `complete` หรือ `abandoned` → Phase 0 ข้าม (ถูกแล้ว)
3. ถ้า status เป็น `in_progress` แต่ Claude ไม่ echo → ตรวจ project id (working dir `/A/B/C` → id `-A-B-C`)

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

### Phase checkpoint > "remember context"

Session ใน Claude Code มีอายุจำกัด (context window + เวลา). งานใหญ่ (เช่น pipeline `sa → ux → fe` ที่ใช้เวลา 2-3 วัน) จะตกกลางทาง

แทนที่จะหวังว่า Claude "จำได้" — บังคับ save artifact ทุกครั้งที่ phase เสร็จ + scan เมื่อเปิด session ใหม่

→ resume ได้แม้ context window หาย
→ ไม่มี "เริ่มใหม่จากศูนย์" สำหรับงานใหญ่

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
