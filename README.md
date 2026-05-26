<div align="center">

<br/>

# ⚡ Claude Skill System
## Built Exclusively for Frontend Developers

<br/>

[![Vue.js](https://img.shields.io/badge/Vue-3.x-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)](https://vuejs.org)
[![Nuxt](https://img.shields.io/badge/Nuxt-4.x-00DC82?style=for-the-badge&logo=nuxtdotjs&logoColor=white)](https://nuxt.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-strict-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)

<br/>

**A discipline-first skill system for Claude Code.**  
Enforces `think → design → code → verify` so you never skip steps,  
never break callers, and never guess at state.

<br/>

[Quickstart](#-quickstart) · [Skills](#-skills) · [How It Works](#-how-it-works) · [MCP Integrations](#-mcp-integrations)

<br/>

</div>

---

## 🎯 Who This Is For

**Frontend developers** who use Claude Code daily with:

- **Vue 3 / Nuxt 4** · React 18+ · TypeScript strict
- **Pinia** · Valibot · Nuxt UI · Tailwind CSS 4
- Composables, SSR/hydration, component libraries

> If you've ever had Claude "fix one thing and silently break another" — this is the system that stops that.

---

## 🔥 What Changes

| Without skills | With this system |
|---|---|
| Claude guesses your intent | Claude **names the skill** before acting — you correct it in 1 line |
| Fix breaks callers | **Ripple check** via CodeGraph runs before every edit |
| Session ends, context lost | **Phase checkpoint** resumes from last step across sessions |
| Prompt → code immediately | `sa → ux → fe → verify` **enforced** — no skipping |
| Claude makes up API syntax | **Context7** fetches live Nuxt/Vue/Valibot docs by version |
| Mistakes repeat across sessions | **Memory tier** promotes lessons from project → global → skill |

---

## ⚡ Quickstart

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git ~/Project/claude-skill-copy
cd ~/Project/claude-skill-copy
./scripts/setup.sh
```

### Optional install flags

Default `./scripts/setup.sh` ติดตั้งแค่ core (skills + memory + hooks + playwright-chromium). ส่วน MCP extras + automation ให้ opt-in:

| Flag | ทำอะไร | เมื่อไหร่ควรใช้ |
|---|---|---|
| `--with-codegraph` | ลง CodeGraph binary + register MCP | งาน ripple check ที่ใหญ่ — `sa`/`fe`/`debug`/`migrate` ใช้แทน `rg` |
| `--with-context7` | Register Context7 MCP | ดึง live docs ของ Nuxt UI / Valibot / library เวอร์ชันใหม่ |
| `--with-playwright` | Register playwright-firefox + playwright-webkit | ต้อง test cross-browser engine (Safari/Firefox) |
| `--with-chrome-devtools` | Register chrome-devtools MCP | ใช้ Lighthouse / perf trace / memory heap |
| `--with-weekly-distill` | ลง cron Mon 09:00 + Telegram digest | อยาก auto-detect promotion candidates รายสัปดาห์ (ต้องมี `~/.claude/.secrets/tg.env`) |

Flags ที่ใช้สลับ default:
- `--force` — overwrite `CLAUDE.md` / `RTK.md` ที่มีอยู่ (destructive)
- `--skip-mcp` — ข้าม playwright-chromium install
- `--skip-deps` — ข้าม auto-install ของ `rg` (ripgrep) ฯลฯ

```bash
# ติดตั้งครบเซ็ตที่ใช้บ่อยที่สุด
./scripts/setup.sh --with-codegraph --with-context7 --with-weekly-distill
```

Open Claude Code in any project. Type naturally:

```
ทำหน้า dashboard ใหม่ — แสดง order list + filter by status
```

Claude responds:

```
→ invoking `sa` (new page, unknown flow)

Phase 1 — Gather spec...
```

Then pipelines `sa → ux → fe → verify` automatically.

---

## 🛠 Skills

| Skill | Trigger words | What it does |
|---|---|---|
| [`sa`](skills/engineering/sa/SKILL.md) | วิเคราะห์ / spec / requirement / security | System spec · user flows · state machines · OWASP audit |
| [`ux`](skills/engineering/ux/SKILL.md) | ปรับ UI / responsive / animation / ทำให้สวย | Component map · Tailwind classes · responsive · a11y |
| [`fe`](skills/engineering/fe/SKILL.md) | เขียน / refactor / composable / store / schema | Vue/Nuxt/React/TS · Pinia · Valibot · Nuxt UI |
| [`debug`](skills/engineering/debug/SKILL.md) | error / พัง / ไม่ทำงาน / strange behavior | Mantra → hypotheses → falsify → root cause → ripple |
| [`migrate`](skills/engineering/migrate/SKILL.md) | migrate / แปลง / ทั้ง project | Pattern codemod across many files — never single-file |
| [`audit`](skills/engineering/audit/SKILL.md) | audit / health check / ตรวจ project | Lighthouse · dead code · bundle · dep security |
| [`verify`](skills/misc/verify/SKILL.md) | ทดสอบ / confirm / verify | Playwright golden-path + edge cases — not just `tsc` |
| [`run`](skills/misc/run/SKILL.md) | run / เปิด app / ดูหน้าตา / screenshot | Launch dev server + screenshot current state |
| [`security-review`](skills/misc/security-review/SKILL.md) | ตรวจ security / audit ก่อน merge / OWASP | OWASP Top 10 audit on branch diff — auth · IDOR · injection · secrets |
| [`pr`](skills/misc/pr/SKILL.md) | เขียน PR / สร้าง PR | Auto-draft PR description from git diff |
| [`review`](skills/misc/review/SKILL.md) | review / code review / ดู PR / ตรวจโค้ด | Code review — bugs · anti-patterns · type safety · logic errors |
| [`simplify`](skills/misc/simplify/SKILL.md) | simplify / ลด code / clean up / duplication | Dead code · duplication · over-complex logic — after fe/debug only |
| [`distill-memory`](skills/misc/distill-memory/SKILL.md) | distill-memory / จัดการ memory / clean up memory | Memory maintenance — prune stale · consolidate duplicates · promote lessons |

### The Frontend Pipeline

```
sa ──────► ux ──────► fe ──────► verify
 spec      design     code       browser
 flows     Tailwind   Vue/TS     Playwright
 states    a11y       Pinia      screenshot
```

**Enforced rules:**
- ❌ Code cannot be written before spec exists
- ❌ `ux` cannot be skipped if UI changes
- ✅ Skip only when the input artifact already exists
- 🔄 Spec gap mid-coding → yields back to `sa`, never guesses

---

## 🧠 How It Works

### Phase 0 — Runs before every task

```
1. Load global memory       ~/.claude/memory/MEMORY.md
2. Load project memory      ~/.claude/projects/<id>/memory/MEMORY.md
   └─ stale guard: any entry naming a file/function → verify still exists before applying
3. Scan phase checkpoint    → in_progress? ask resume / fresh start
4. Load skill vocabulary    Thai trigger phrases per skill
5. Echo top 3-5 relevant entries
6. Conflict check           → conflicts memory? stop + ask first
7. Token efficiency gate    → rtk proxy / quality gate
8. Match intent → pick skill → echo: `→ invoking [skill] (reason)`
   └─ multi-step pipeline (sa→ux→fe)? → create tasks before starting Phase 1
```

**Three enforced fixes that prevent the most common Claude mistakes:**

| Fix | Rule | Prevents |
|---|---|---|
| **Fix 1** — Pipeline task tracking | Multi-step pipelines create tasks before starting | Context compression losing pipeline state |
| **Fix 2** — Stale memory guard | Named file/function in memory → verify it still exists | Recommending deleted code |
| **Fix 5** — Checkpoint before yield | Before switching skill mid-task → write checkpoint | Context loss when skill yields to another |

### Memory that survives sessions

```
project memory  — per-project findings, patterns, constraints
    ↓ recurring ≥ 2 projects
global memory   — cross-project rules, user preferences
    ↓ recurring ≥ 3 projects + same skill
skill learnings — Vue reactivity quirks, Valibot pitfalls, OWASP patterns
```

**10 auto-save triggers** (no manual action needed):

| # | When |
|---|---|
| 1 | User corrects direction |
| 2 | Non-obvious pattern confirmed |
| 3 | Root cause found + ripple list |
| 4 | New approach succeeds |
| 5 | Pipeline phase complete → checkpoint saved |
| 6 | Constraint found outside the code |
| 7 | Pattern corrected ≥ 2× in one task |
| 8 | Session > 20 turns |
| 9 | Skill invocation corrected → saved to trigger vocab |
| 10 | Bug with traceable root cause → ripple files named |

---

## 🌐 MCP Integrations

| MCP | Purpose | Install |
|---|---|---|
| **playwright-chromium** | Default browser — navigate · click · screenshot · console · network | ✅ auto |
| **chrome-devtools** | Lighthouse · perf trace · memory heap only | opt-in |
| **playwright-firefox/webkit** | Real engine cross-browser tests | opt-in |
| **CodeGraph** | Semantic callers · impact · trace — ripple check before every edit; SessionStart hook auto-inits new projects | manual (first install) |
| **Context7** | Live Nuxt/Vue/Valibot/Pinia docs by version | opt-in |
| **Figma** | Design structure · node thumbnails · comments | manual |
| **RTK** | Shell output filter → 60–90% token savings | hook |

```bash
# Default (playwright-chromium auto-installed)
./scripts/setup.sh

# Cross-browser
./scripts/setup.sh --with-playwright

# Lighthouse + perf traces
./scripts/setup.sh --with-chrome-devtools

# Live library docs
./scripts/setup.sh --with-context7
```

---

## 📁 Per-project CLAUDE.md

Create `CLAUDE.md` at your project root — Claude reads it before every task:

```markdown
## Stack
Nuxt 4 · TypeScript strict · Pinia · Tailwind 4 · Valibot · Yarn

## Critical Rules
- API: all calls through `useApiFetch` — never raw `$fetch` in component
- Validation: valibot schema in `shared/schemas/<domain>.ts`
- Form: `<UForm>` + `<UFormField>` only
- Error: extract via `getErrorMessage`
```

No need to repeat your stack every prompt. Claude picks the right defaults.

---

## 📦 Repo Structure

```
skills/
├── engineering/
│   ├── sa/             # System Analyst + Security Audit
│   ├── ux/             # Visual + Interaction Design
│   ├── fe/             # Frontend Code (Vue / Nuxt / React / TS)
│   ├── debug/          # Bug Diagnosis — root cause, not symptom
│   ├── migrate/        # Bulk Pattern Transformation
│   └── audit/          # Project Health (Lighthouse · dead code · deps)
└── misc/
    ├── verify/          # Playwright Browser Verification — golden-path + edge cases
    ├── run/             # Dev Server + Screenshot — observe, don't fix
    ├── security-review/ # OWASP Branch Audit — diff-scoped, before merge
    ├── pr/              # PR Description Writer
    ├── review/          # Code Review — bugs · anti-patterns · type safety
    ├── simplify/        # Reduce Code Surface — dead code · duplication
    ├── distill-memory/  # Memory Distillation — prune · promote · audit
    └── _template/       # Skeleton for new skills
hooks/
    ├── lint-on-edit.sh          # PostToolUse → run linter after every edit
    ├── check-cross-project.py   # SessionStart (async) → flag memory slugs in ≥2 projects
    ├── check-memory-size.py     # SessionStart (async) → warn when project memory ≥ 30 entries
    ├── _checkpoint_lib.py       # Shared scan/render — imported by post-compact + inject-checkpoint
    ├── post-compact.py          # PostCompact → systemMessage + write sentinel
    ├── inject-checkpoint.py     # UserPromptSubmit → inject checkpoint as additionalContext (once per compaction)
    ├── tg-config.sh             # Telegram credential loader — sources ~/.claude/.secrets/tg.env (opt-in)
    ├── check-tg-bridge.sh       # SessionStart → auto-restart tg-bridge daemon (opt-in, not registered by setup.sh)
    ├── telegram-notify.sh       # Stop → push end-of-turn summary to Telegram (opt-in)
    └── rtk-rewrite.sh           # PreToolUse → rewrite shell commands via RTK for token savings
.secrets-template/
    └── tg.env.example           # Copy to ~/.claude/.secrets/tg.env (chmod 600) — never commit real values
scripts/
    ├── setup.sh                 # Bootstrap a fresh machine — see Quickstart flags
    ├── link-skills.sh           # Symlink skills/* → ~/.claude/skills/ (called by setup.sh)
    ├── list-skills.sh           # Print currently linked skills
    ├── lint-skills.py           # Validate frontmatter + link refs + size budgets (memory body, SKILL.md, CLAUDE.md)
    ├── distill-dry-run.py       # Memory tier scanner — emits markdown digest (read-only)
    └── distill-dry-run-notify.sh # Wraps the scanner → splits + sends to Telegram + archives last digest
mcp-guides/
    ├── browser.md               # Browser MCP (playwright-chromium default + chrome-devtools for Lighthouse/perf/memory)
    ├── codegraph.md             # CodeGraph MCP — semantic ripple/call-path/impact
    ├── context7.md              # Context7 MCP — live library docs
    └── figma.md                 # Figma MCP — design file load + node thumbnails + comments
```

> **Secrets convention** — credentials never live inside committable scripts. Hooks that need
> a token source `~/.claude/.secrets/<name>.env` (chmod 600, gitignored). The repo ships only
> `.env.example` templates; loaders no-op silently when the secrets file is absent.

---

## 🧹 Memory distillation rhythm

Memory grows automatically (8 save triggers in CLAUDE.md). Without pruning it becomes a graveyard — duplicate entries cost tokens every Phase 0 echo, stale entries actively mislead. **Detection is automated; application stays manual.**

### Auto-detection (no input from you)

| Mechanism | When | Output |
|---|---|---|
| `hooks/check-cross-project.py` | SessionStart (async) | Writes `~/.claude/memory/.cross-project-candidates.md` for slugs in ≥ 2 projects |
| `hooks/check-memory-size.py` | SessionStart (async) | `systemMessage` when current project ≥ 30 entries (critical at 45) |
| `scripts/distill-dry-run.py` | Mon 09:00 cron (`--with-weekly-distill`) | Telegram digest + archive at `~/.claude/memory/.last-distill-report.md` |

Sample weekly digest:

```
# 📚 Weekly memory distill — 2026-05-27

## 🟢 Cross-project promotion candidates
- **select-item-value-empty-string** — 3 projects: boonphone, mcop-web-manage, mcop-web-manage-v2

## ⚠️ Memory caps (≥ 30 entries)
- 🟡 warn **Project-mcop-web-manage** — 36 entries
- 🟡 warn **Project-mcop-web-manage-v2** — 30 entries

## 📊 Tier snapshot
- Global tier: 15 entries
- Projects scanned: 10
- Skill learnings files: 14

Next step: open a Claude session and run `/distill-memory` to review + apply.
```

### Manual application (you trigger)

Type `/distill-memory` in any session. The skill:

1. Scans all 3 tiers (global · project · skill learnings) — never trusts the index alone
2. Shows a proposal table — `PROMOTE` / `PRUNE` / `CROSS-LINK` candidates with sizes + reasons
3. **Waits for your confirmation before any write**
4. On apply: writes destination → deletes source (never duplicates) → updates `MEMORY.md` indexes
5. Returns a tier snapshot diff so you can see exactly what changed

Auto-promotion is intentionally **not** implemented. "Same slug in 2 projects" is a noisy signal — the model reading actual entry bodies catches false promotions that a heuristic script would push through. The cost of a wrong global promotion is paid by every Phase 0 echo until you notice.

---

## 🩺 Troubleshooting

**Skill not triggering**
```bash
ls -la ~/.claude/skills/   # should show symlinks → repo
```

**Claude ignoring discipline**
```bash
head ~/.claude/CLAUDE.md   # must start with "@RTK.md" + "Universal Phase 0"
# if missing → ./scripts/setup.sh
```

**CodeGraph returning empty**
```bash
ls .codegraph/codegraph.db   # if missing → codegraph init -i
# SessionStart hook auto-inits projects with one of:
#   package.json · pyproject.toml · go.mod · Cargo.toml · Gemfile · pom.xml · setup.py
# skill auto-falls back to rg — no crash
```

**`rtk: command not found`**
→ Install [RTK](https://github.com/skarekrow/rtk) or skip it — skills work without RTK, just with higher token usage.

---

## 💡 Philosophy

**Discipline > playbook** — skills don't say "do step 1, 2, 3."  
They enforce "you cannot proceed until this artifact exists."  
That eliminates anchoring bias, fix-by-coincidence, and skipped ripple checks.

**Memory > prompt engineering** — a prompt tells Claude once.  
Memory tells Claude every time it encounters the same pattern.  
And it gets smarter session after session without manual editing.

**Phase checkpoint > "remember context"** — large tasks save an artifact at every phase boundary. The `post-compact.py` hook surfaces any in-progress checkpoint as a systemMessage after compaction. Phase 0 then loads it and asks whether to resume or start fresh.

**Cross-project auto-flag** — `check-cross-project.py` runs at SessionStart (async, zero latency) and scans all project memories for `name:` slugs appearing in ≥ 2 projects. Pre-populates `/distill-memory` promotion candidates so no repeated lesson slips through.

**Memory-cap guardrail** — `check-memory-size.py` runs at SessionStart (async) and emits a `systemMessage` warning when the current project's memory crosses **30 entries** (critical at **45**). `MEMORY.md` truncates after 200 lines, so silently oversized memory degrades Phase 0 echoes — this catches it before quality drops.

**Weekly distill digest (opt-in)** — `scripts/distill-dry-run.py` scans all tiers and produces a markdown digest (cross-project promotion candidates + memory-cap status + tier counts). Install via `./scripts/setup.sh --with-weekly-distill` to register a Monday 09:00 cron that ships the digest to Telegram + archives to `~/.claude/memory/.last-distill-report.md`. **Detection is auto, application stays manual** — open a session and run `/distill-memory` to review + apply. Requires Telegram credentials at `~/.claude/.secrets/tg.env` (chmod 600).

**Lean every-turn payload** — CLAUDE.md is loaded on every prompt, so reference material moves out of it. The four MCP integration sections (Browser, CodeGraph, Context7, Figma) live in `mcp-guides/<name>.md` and are read on-demand by the skills that actually need them. CLAUDE.md keeps a 30-line consolidated stub (trigger map + decision shortcuts + pointers). Result: **CLAUDE.md ≈ 22 KB instead of 39 KB (−43%)**, which translates to roughly 3.5 K tokens saved per cold-start session — pipeline order, decision matrix, save triggers, and trigger keywords are all unchanged.

**Size-budget lints** — `lint-skills.py` warns when CLAUDE.md > 35 KB, any SKILL.md > 25 KB, or a memory entry body > 1.5 KB. The budgets are calibrated to the per-turn loading audit; warnings show up next to frontmatter/link checks so regrowth is caught at edit time instead of months later.

---

## License · Credits

MIT · Inspired by [9arm-skills](https://github.com/thananon/9arm-skills)  
PR welcome — new skills must be used ≥ 2 weeks in production + prove they catch something existing skills don't.
