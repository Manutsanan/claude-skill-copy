# claude-skill-copy

> Skill system สำหรับ Claude Code — บังคับ discipline + pipeline + memory loop แบบ version-controlled

---

## ✨ ทำอะไรได้

- 🧠 **คิดก่อนเขียน** — pipeline `sa → ux → fe → verify` บังคับทุกครั้ง
- 🔍 **Debug มีระบบ** — mantra + hypotheses + falsify-first + breadcrumb ledger
- 🔄 **Memory สะสมเอง** — lesson ข้าม session, ข้าม project, promote ตาม tier
- 📋 **Phase checkpoint** — resume pipeline ข้าม session ได้ ไม่ start จากศูนย์
- 🌐 **MCP integrations** — browser, codegraph, live docs, Figma พร้อมใช้
- ⚡ **Token efficient** — RTK + deferred tools + quality gate compact

---

## ⚡ Quickstart

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy
cd ~/Project/claude-skill-copy
./scripts/setup.sh
```

→ ดู [QUICKSTART.md](QUICKSTART.md) สำหรับ test commands

---

## 🔧 How it works

### Phase 0 — ทำก่อนทุก task

```
1. โหลด global memory       ~/.claude/memory/MEMORY.md
2. โหลด project memory      ~/.claude/projects/<id>/memory/MEMORY.md
3. Scan phase checkpoint     → in_progress? ถามว่า resume / เริ่มใหม่
4. โหลด skill vocabulary     ~/.claude/memory/skill_trigger_vocabulary.md
5. Echo top 3-5 entries ที่ relevant
6. Conflict check           → ขัด memory? หยุดถามก่อน
7. Token efficiency gate    → rtk proxy / quality gate compact
8. Match intent → เลือก skill + echo: `→ invoking \`[skill]\` ([reason])`
```

---

### Decision matrix

| พูดว่า | Skill |
|---|---|
| วิเคราะห์ / spec / requirement | `sa` |
| ตรวจ security / audit / ช่องโหว่ | `sa` Mode B |
| ปรับ UI / responsive / animation / หน้าตา | `ux` |
| เขียน component / composable / refactor | `fe` |
| error / bug / X พัง / ไม่ทำงาน | `debug` |
| migrate / แปลง pattern หลายไฟล์ | `migrate` |
| audit project / health check | `audit` |
| verify / ทดสอบ / ดูว่าทำงานไหม | `verify` |
| เปิด app / run dev server | `run` |
| simplify / ลด code / หา duplication | `simplify` |
| review PR / code review | `review` |
| security review branch | `security-review` |
| ทำหน้าใหม่จาก mockup | `sa → ux → fe` |
| ตรวจ security แล้ว fix | `sa → fe` |
| debug แล้ว redesign data model | `debug → sa → fe` |
| ช่วยดู / ปรับ / ลอง / แก้ไข (ไม่มี object) | ❓ AskUserQuestion เสมอ — ไม่เดา |

> 💡 ไม่ต้องพิมพ์ `/skill` เอง — พิมพ์ภาษาไทยปกติ Claude detect เอง
> บรรทัดแรกจะขึ้น `→ invoking \`sa\` (reason)` เสมอ — ผิดแก้ได้ทันที

---

### Pipeline `sa → ux → fe → verify`

```
sa   →  spec (actor / flow / state machine / acceptance)
ux   →  design (component map / Tailwind / responsive / animation)
fe   →  code (Vue/Nuxt/TS / valibot / Nuxt UI)
verify → browser test + screenshot
```

**กฎ:**
- ❌ ห้ามสลับลำดับ
- ✅ ข้าม step ได้ถ้า input มีอยู่แล้ว
- ✅ ทุก step save phase checkpoint ก่อน handoff
- 🔄 เจอช่องว่าง yield กลับ skill ต้นน้ำ — ไม่เดา

---

### Memory loop

```
project memory  (~/.claude/projects/<id>/memory/)
    ↓ ซ้ำ ≥ 2 projects
global memory   (~/.claude/memory/)
    ↓ ซ้ำ ≥ 3 projects + skill เดียวกัน
skill learnings (skills/<skill>/learnings.md)
    ↓ load-bearing
SKILL.md rule
```

**10 save triggers** (save ทันที ไม่รอจบ session):

| # | เมื่อไหร่ |
|---|---|
| 1 | User แก้ทาง / บอกผิด |
| 2 | User confirm pattern ที่ไม่ obvious |
| 3 | เจอ error + root cause |
| 4 | งานสำเร็จด้วย approach ใหม่ |
| 5 | เจอ bug + ripple list |
| 6 | Constraint นอกโค้ด (API limit, deprecated) |
| 7 | Pattern ซ้ำ ≥ 2 ครั้งในงานเดียว |
| 8 | Session ยาว (> 20 turn) |
| 9 | Pipeline phase เสร็จ → save checkpoint |
| 10 | Skill invoke ถูกแก้ → save `feedback_skill_trigger_*` → distill เข้า vocabulary |

---

## 📦 Install

### Prerequisites

- Claude Code (CLI / desktop / VS Code)
- `git` + `bash` (macOS / Linux / WSL)
- **Auto-install:** `ripgrep`, `python3`, `jq`, chrome-devtools MCP
- **Optional:** [RTK CLI](https://github.com/skarekrow/rtk), [CodeGraph](https://github.com/colbymchenry/codegraph), Playwright MCP

### Bootstrap

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy
cd ~/Project/claude-skill-copy
./scripts/setup.sh
```

**setup.sh ทำ (idempotent):**

| Step | Action |
|---|---|
| 0 | ติดตั้ง system deps |
| 1 | Symlink 7 skills → `~/.claude/skills/` |
| 2 | ติดตั้ง `~/.claude/CLAUDE.md` + `RTK.md` |
| 3 | สร้าง `~/.claude/memory/` + `projects/` |
| 4 | ติดตั้ง lint hook (PostToolUse) |
| 5 | Register chrome-devtools MCP |

**Flags:** `--force` · `--skip-link` · `--skip-deps` · `--skip-mcp` · `--with-codegraph` · `--with-context7` · `--with-playwright`

### Verify

```bash
ls -la ~/.claude/skills/     # เห็น 7 symlinks
head ~/.claude/CLAUDE.md     # ขึ้น "@RTK.md" + "Universal Phase 0"
claude mcp list              # เห็น "chrome-devtools"
```

---

## 🌐 MCP Integrations

| MCP | ทำอะไร | Skill ที่ใช้ |
|---|---|---|
| **RTK** | กรอง shell output → ลด token 60-90% | ทุก skill (hook อัตโนมัติ) |
| **chrome-devtools** | Browser runtime — error / network / state / Lighthouse / perf trace / memory | `debug` / `ux` / `fe` / `audit` |
| **Playwright** | Cross-browser testing — Chromium + Firefox + WebKit (Safari) | `debug` / `ux` / `audit` / `fe` |
| **CodeGraph** | Semantic codebase graph — callers / impact / trace | ทุก skill ที่ ripple check |
| **Context7** | Live library docs ตามเวอร์ชัน | `fe` / `debug` / `migrate` / `sa` |
| **Figma** | Design structure + thumbnail + comments | `ux` / `sa` |

### Chrome-devtools vs Playwright

| ต้องการ | ใช้ MCP |
|---|---|
| Console errors / network / runtime state | `chrome-devtools` |
| Lighthouse score / perf trace / memory heap | `chrome-devtools` เท่านั้น |
| ทดสอบ Firefox engine | `playwright-firefox` |
| ทดสอบ Safari / WebKit | `playwright-webkit` |
| Dropdown select / navigate back / multi-tab | `playwright-*` |

### Playwright (opt-in)

```bash
./scripts/setup.sh --with-playwright
```

ติดตั้ง 3 MCP servers ใน `~/.claude.json`:
- `playwright-chromium` — Chromium engine
- `playwright-firefox` — Firefox engine
- `playwright-webkit` — WebKit/Safari engine

**Skills ที่ได้ประโยชน์:**
- `debug` — reproduce bug ใน Firefox/Safari; `browser_select_option` สำหรับ form bugs
- `ux` — cross-browser screenshot comparison หลัง chrome-devtools ผ่านแล้ว
- `audit` — cross-browser a11y: ARIA + keyboard nav ต่างกันระหว่าง engines
- `fe` — cross-browser hydration verify เมื่อ chrome-devtools pass แต่ user แจ้งว่า Firefox/Safari พัง

### CodeGraph (แนะนำ)

```bash
# 1. Install
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh

# 2. Register ใน ~/.claude.json → mcpServers
"codegraph": { "type": "stdio", "command": "~/.local/bin/codegraph", "args": ["serve", "--mcp"] }

# 3. Init ต่อ project (1 ครั้ง)
codegraph init -i
```

### Context7

```bash
./scripts/setup.sh --with-context7
# หรือเพิ่ม mcpServers: "context7": { "type":"stdio","command":"npx","args":["-y","@upstash/context7-mcp@latest"] }
```

### Figma

```json
"figma": { "type":"stdio","command":"npx","args":["-y","figma-developer-mcp","--figma-api-key=<KEY>","--stdio"] }
```

→ API key ที่ figma.com → Settings → Personal access tokens

---

## 💬 How to use

### Auto trigger — พิมพ์ตามธรรมชาติ

```
"วิเคราะห์ requirement หน้านี้"    → invoking `sa` (วิเคราะห์ requirement)
"ทำ UI ให้ responsive"             → invoking `ux` (UI + responsive)
"เขียน composable"                 → invoking `fe` (เขียน composable)
"ทำไม login ไม่ได้ — error 500"    → invoking `debug` (error + ไม่ได้)
"ทำหน้าใหม่ list สินค้า"           → invoking `sa` → ux → fe
"ช่วยดูหน่อย"                      → ❓ AskUserQuestion ก่อน
```

### Slash (บังคับ skill ตรง)

```
/sa วิเคราะห์ flow เก็บค่าจอง
/ux redesign หน้านี้
/fe refactor service layer
/debug หน้ากระพริบ — error stack: ...
/migrate inline schema → shared/schemas/
/audit
```

---

## 📋 Skills reference

| Skill | What | chrome-devtools | Playwright |
|---|---|---|---|
| [`sa`](skills/engineering/sa/SKILL.md) | System Analyst + Security Audit | — | — |
| [`ux`](skills/engineering/ux/SKILL.md) | Visual + interaction design | ✅ visual / lighthouse | ✅ cross-browser screenshot |
| [`fe`](skills/engineering/fe/SKILL.md) | Frontend code (Nuxt/Vue/React/TS) | 🟡 opt-in | 🟡 cross-browser hydration |
| [`debug`](skills/engineering/debug/SKILL.md) | Bug diagnosis | ✅ single-browser | ✅ cross-browser + select/back/tabs |
| [`migrate`](skills/engineering/migrate/SKILL.md) | Bulk transformation หลายไฟล์ | — | — |
| [`audit`](skills/engineering/audit/SKILL.md) | Project health sweep | ✅ lighthouse / perf / memory | ✅ cross-browser a11y |
| [`_template`](skills/misc/_template/SKILL.md) | Skeleton สำหรับ skill ใหม่ | — | — |

แต่ละ skill folder มี: `SKILL.md` · `learnings.md` · `REFERENCE.md` (fe เท่านั้น)

---

## 📁 Per-project CLAUDE.md

สร้างที่ root ของแต่ละ project:

```markdown
# <Project> — CLAUDE.md

## Stack
Nuxt 4 · TypeScript strict · Pinia · Tailwind 4 · valibot · Yarn

## Critical Rules
- API: ทุก call ผ่าน `useApiFetch` — ห้าม `$fetch` ตรงใน component
- Validation: valibot schema ใน `shared/schemas/<domain>.ts`
- Form: `<UForm>` + `<UFormField>` เท่านั้น
- Error: extract ผ่าน `getErrorMessage`

## File Naming
| Type | Convention |
|---|---|
| Components | PascalCase |
| Pages | kebab-case |
| Composables | `useCamelCase.ts` |
| Schemas | kebab-case |
```

---

## 🔄 Upgrade

```bash
cd ~/Project/claude-skill-copy
git pull                        # skills auto-update ผ่าน symlinks

# ถ้า CLAUDE.template.md เปลี่ยน
./scripts/setup.sh --force      # backup เก่าก่อน → แทนที่ใหม่
```

> Memory (`~/.claude/memory/`, `~/.claude/projects/`) ไม่ถูกแตะเลย

---

## ⚙️ Customize

```bash
# Fork + ใช้ของตัวเอง
git clone https://github.com/<you>/claude-skill-copy.git ~/Project/my-skills
./scripts/setup.sh

# เพิ่ม skill ใหม่
cp -R skills/misc/_template skills/in-progress/my-skill
# แก้ SKILL.md → ลองใช้ → พอพร้อม ย้ายไป skills/engineering/
```

**Buckets:**

| Bucket | Linked | Purpose |
|---|---|---|
| `skills/engineering/` | ✅ | daily use |
| `skills/misc/` | ✅ | meta/templates |
| `skills/in-progress/` | ❌ | drafts |
| `skills/deprecated/` | ❌ | retired |

---

## 🩺 Troubleshooting

**Skill ไม่ trigger**
```bash
ls -la ~/.claude/skills/   # ต้องเห็น symlinks → ถ้าเป็น real dir → setup.sh อีกครั้ง
```

**Claude ไม่ทำตาม discipline**
```bash
head ~/.claude/CLAUDE.md   # ต้องขึ้น "@RTK.md" + "Universal Phase 0"
# ถ้าไม่มี → ./scripts/setup.sh
```

**Memory ไม่ save**
```bash
grep "Universal save triggers" ~/.claude/CLAUDE.md   # ต้องเจอ
# ถ้าไม่เจอ → ./scripts/setup.sh --force
```

**CodeGraph return empty**
```bash
ls .codegraph/codegraph.db   # ถ้าไม่มี → codegraph init -i
which codegraph              # ถ้าไม่เจอ → เช็ค PATH + ~/.claude.json
# skill fallback rg อัตโนมัติ ไม่ crash
```

**Phase checkpoint ไม่ resume**
```bash
ls ~/.claude/projects/<id>/memory/project_phase_checkpoint_*
# status: complete / abandoned → Phase 0 ข้าม (ถูกแล้ว)
# status: in_progress แต่ไม่ echo → เช็ค project id (dir path → replace / ด้วย -)
```

**`rtk: command not found`**
→ ติดตั้ง [RTK](https://github.com/skarekrow/rtk) หรือ ignore (skill ทำงานได้ แค่ token saving น้อยลง)

**Windows symlink ไม่ทำงาน**
→ ใช้ WSL 2 + Ubuntu (recommended)

---

## 💡 Philosophy

**Discipline > playbook** — skill ไม่ได้บอก "ทำ 1, 2, 3" แต่บังคับว่า "ห้ามทำอะไร" — กัน anchoring bias, fix-by-coincidence, skip ripple check

**Memory > prompt engineering** — prompt บอก Claude ใน turn เดียว; memory บอก **ทุกครั้ง** ที่เจอ pattern คล้ายกัน และสะสมเองโดยไม่ต้อง edit SKILL.md

**Portability without uniformity** — repo ให้ discipline portable ข้ามเครื่อง; memory สะสม per-user ไม่ถูก overwrite

**Phase checkpoint > "จำ context"** — งานใหญ่บังคับ save artifact ทุก phase → resume ได้แม้ context หาย

---

## License · Credits · Contributing

MIT · Inspired by [9arm-skills](https://github.com/thananon/9arm-skills)

PR welcome — skill ใหม่ต้องใช้จริง ≥ 2 สัปดาห์ + พิสูจน์ว่า catch อะไรที่ skill เดิมไม่ catch ก่อน merge
