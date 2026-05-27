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
| Forgotten in-progress pipeline | **Stale pipeline reminder** fires at every session start when a prior checkpoint is `in_progress` |
| Repeated type-check on every turn | **Quality-gate debounce** skips `vue-tsc` unless a source file actually changed since last run |

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
| `--with-n8n` | ติดตั้ง Docker (ถ้าไม่มี) + start n8n container + deploy hooks + load launchd agents + สร้าง account/API key + activate 9 workflows อัตโนมัติ | ต้องการ n8n automation layer — ใส่ `N8N_EMAIL` + `N8N_PASSWORD` ใน `~/.claude/.secrets/n8n.env` ก่อนรัน (setup.sh จะรอถ้าค่ายัง placeholder) |

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
    ├── check-memory-size.py     # SessionStart (async) → warn when project memory ≥ 30 entries + surface hook errors (last 24h) + stale pipeline reminder + distill idle reminder (time-based, when below WARN threshold but ≥ 14d since last run)
    ├── _checkpoint_lib.py       # Shared scan/render — imported by post-compact + inject-checkpoint
    ├── post-compact.py          # PostCompact → systemMessage + write sentinel
    ├── inject-checkpoint.py     # UserPromptSubmit → inject checkpoint as additionalContext (once per compaction)
    ├── log-skill-invoke.py      # PreToolUse (matcher=Skill) → append JSONL to ~/.claude/logs/ (errors → hook-errors.jsonl)
    ├── log-user-prompt.py       # UserPromptSubmit → truncated prompt JSONL (redacts emails/tokens, 200 chars; errors → hook-errors.jsonl)
    ├── tg-config.sh             # Telegram credential loader — sources ~/.claude/.secrets/tg.env (opt-in)
    ├── check-tg-bridge.sh       # SessionStart → auto-restart tg-bridge daemon (opt-in, not registered by setup.sh)
    ├── telegram-notify.sh       # Stop → push end-of-turn summary to Telegram (opt-in)
    ├── n8n-notify.sh            # Stop (async) → enriched payload (last_skill, checkpoint_phases, mem_files/bytes) → /webhook/claude-stop + /webhook/claude-memory + /webhook/claude-state-store
    ├── n8n-prefetch.sh          # UserPromptSubmit → query n8n state store once per (project × reboot); inject pipeline state / memory alerts / followups as additionalContext
    ├── git-init-check.sh        # PostToolUse (matcher=Bash) → reads stdin JSON to detect actual `git init`; emits .gitignore reminder only when needed (no false positives on complex commands)
    ├── skill-vocab-sync.py      # PostToolUse (async, matcher=Write|Edit) → detects feedback_skill_trigger_* saves; parses phrase/correct/wrong; appends to skill_trigger_vocabulary.md immediately; POSTs to n8n /webhook/claude-vocab-correction for tracking + recurring-mismatch alerts
    ├── quality-gate.sh          # Stop (async) → type-check Vue/Nuxt/TS with debounce (skips if no .ts/.vue newer than last-run marker); routes through n8n /webhook/claude-typecheck for trend tracking (direct Telegram fallback)
    ├── n8n-followups-check.sh   # [launchd daily 09:00] reads FOLLOWUPS.md → POST /webhook/claude-followups
    ├── n8n-weekly-report.sh     # [launchd Mon 09:00] aggregates skill JSONL logs → POST /webhook/claude-weekly
    ├── n8n-drift-check.sh       # [launchd daily 10:00] compares hook checksums local vs repo → POST /webhook/claude-drift
    └── rtk-rewrite.sh           # PreToolUse → rewrite shell commands via RTK for token savings
.secrets-template/
    ├── tg.env.example           # Copy to ~/.claude/.secrets/tg.env (chmod 600) — never commit real values
    └── n8n.env.example          # Copy to ~/.claude/.secrets/n8n.env (chmod 600) — API key + credentials
launchd/
    ├── com.claude.followups-check.plist  # daily 09:00 → n8n-followups-check.sh
    ├── com.claude.weekly-report.plist    # Mon 09:00 → n8n-weekly-report.sh
    └── com.claude.drift-check.plist      # daily 10:00 → n8n-drift-check.sh
scripts/
    ├── setup.sh                 # Bootstrap a fresh machine — see Quickstart flags
    ├── link-skills.sh           # Symlink skills/* → ~/.claude/skills/ (called by setup.sh)
    ├── list-skills.sh           # Print currently linked skills
    ├── lint-skills.py           # Validate frontmatter + link refs + size budgets (memory body, SKILL.md, CLAUDE.md)
    ├── distill-dry-run.py       # Memory tier scanner — emits markdown digest (read-only)
    ├── distill-dry-run-notify.sh # Wraps the scanner → splits + sends to Telegram + archives last digest
    ├── skill-report.py          # Analytics over ~/.claude/logs/ — invokes per skill, top phrases, silent skills
    ├── n8n-setup-account.py     # Playwright headless: create n8n owner account + API key → writes N8N_API_KEY to n8n.env (auto-called by setup.sh --with-n8n)
    └── create-n8n-workflows.py  # Create + activate all 9 n8n webhook workflows via API (auto-called by setup.sh --with-n8n)
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
| `hooks/check-memory-size.py` | SessionStart (async) | `systemMessage` when current project ≥ 30 entries (critical at 45); stale pipeline reminder when any `in_progress` checkpoint exists; distill idle suggestion when ≥ 14d since last `/distill-memory` and count is below WARN threshold |
| `hooks/n8n-prefetch.sh` | UserPromptSubmit (once per session) | Injects pipeline state · memory alerts · pending followups from n8n state store as `additionalContext` |
| `scripts/distill-dry-run.py` | Mon 09:00 cron (`--with-weekly-distill`) | Telegram digest + archive at `~/.claude/memory/.last-distill-report.md` |

Sample weekly digest:

```
# 📚 Weekly memory distill — 2026-05-27

## 🟢 Cross-project promotion candidates
- **select-item-value-empty-string** — 3 projects: shop-a, shop-b, shop-admin

## ⚠️ Memory caps (≥ 30 entries)
- 🟡 warn **Project-shop-b** — 36 entries
- 🟡 warn **Project-shop-admin** — 30 entries

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

## 📊 Skill invocation observability

Every `Skill` tool call and every user prompt is appended to `~/.claude/logs/*.jsonl` so you can answer questions like *"which Thai phrase keeps triggering the wrong skill?"* or *"which skill never gets used?"* with data, not gut feel.

### What gets logged

| File | When | Content | Privacy |
|---|---|---|---|
| `skill-invocations-YYYY-MM.jsonl` | PreToolUse (matcher=Skill) | ts, session prefix, cwd hash, skill, args (120 chars) | cwd hashed |
| `prompts-YYYY-MM.jsonl` | UserPromptSubmit | ts, session prefix, cwd hash, prompt (200 chars), length | emails/tokens redacted, slash-only prompts skipped |
| `hook-errors.jsonl` | hook runtime error | ts, hook name, error class, last 2KB of traceback | no payload data |

Files rotate monthly. Nothing ever leaves the machine — logs are not synced to the repo or any external service.

### Query

```bash
python3 ~/.claude/scripts/skill-report.py                # overview, last 30 days
python3 ~/.claude/scripts/skill-report.py --days 7
python3 ~/.claude/scripts/skill-report.py --skill sa     # top phrases that triggered sa
python3 ~/.claude/scripts/skill-report.py --silent       # skills with zero invokes
python3 ~/.claude/scripts/skill-report.py --errors       # recent hook errors + traceback
```

### Hook errors are surfaced, not silent

The logging hooks exit 0 on failure (so they never block your workflow), but the error trace is written to `hook-errors.jsonl`. The existing `check-memory-size.py` SessionStart hook scans the last 24h of errors and adds them to its `systemMessage` warning. If a hook silently broke between sessions, you'll see it on the next session start — not weeks later.

### Honest limits

- **Vocab auto-sync** closes the correction loop partially — `skill-vocab-sync.py` applies the phrase immediately; n8n tracks recurring mismatches. Full auto-promotion (moving corrected phrases from project memory to CLAUDE.md) still requires `/distill-memory`
- **Prompt→invoke correlation** uses a 10-second window in the same session; noisy on multi-turn tasks
- **First weeks are sparse** — meaningful signal after ~50+ invocations per skill
- **No realtime alerts** — hook errors surface on *next* SessionStart, not mid-session

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

**Logging hooks misbehaving**
```bash
python3 ~/.claude/scripts/skill-report.py --errors --days 7   # recent traces
tail -f ~/.claude/logs/hook-errors.jsonl                       # watch live
ls ~/.claude/logs/                                             # files write-perms OK?
```
If `hook-errors.jsonl` is missing entirely after a known-bad payload, the hook itself isn't being invoked — check `~/.claude/settings.json` for the `Skill` matcher under `PreToolUse` and `log-user-prompt.py` under `UserPromptSubmit`.

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

**Memory-cap guardrail + proactive reminders** — `check-memory-size.py` runs at SessionStart (async) and emits `systemMessage` warnings in three cases: (1) current project memory crosses **30 entries** (critical at **45**) — MEMORY.md truncates after 200 lines so oversized memory degrades Phase 0 echoes silently; (2) any `in_progress` phase checkpoint exists from a prior session — surfaces the stale pipeline so you resume instead of restarting; (3) `/distill-memory` hasn't been run in **14 days** and total memory count is above 10 but below the count-based threshold — a time-based nudge that fires before things get noisy, not after.

**Weekly distill digest (opt-in)** — `scripts/distill-dry-run.py` scans all tiers and produces a markdown digest (cross-project promotion candidates + memory-cap status + tier counts). Install via `./scripts/setup.sh --with-weekly-distill` to register a Monday 09:00 cron that ships the digest to Telegram + archives to `~/.claude/memory/.last-distill-report.md`. **Detection is auto, application stays manual** — open a session and run `/distill-memory` to review + apply. Requires Telegram credentials at `~/.claude/.secrets/tg.env` (chmod 600).

**n8n automation layer** — hooks are stateless (fire-and-forget); n8n is the stateful middleware. 9 webhook-based workflows extend the skill system without touching Claude's context: pipeline phase tracking (sa→ux→fe completion across sessions), type-check trend history (regression detection), memory growth monitoring, FOLLOWUPS.md deadline alerts, weekly skill analytics, repo sync drift detection, cross-project pattern promotion reminders, a **state store** (GET + POST webhooks sharing `staticData`) that caches pipeline state and memory alerts between sessions — queried by `n8n-prefetch.sh` at session start to inject context before Phase 0 even runs — and a **vocab tracker** that accumulates skill-trigger corrections and fires a Telegram alert when the same phrase is corrected ≥ 2 times (recurring mismatch signal). n8n runs in Docker (`~/.n8n` mounted only) — host scripts do all file reads and push pre-processed payloads via HTTP POST. Telegram remains notification-only and can be removed without affecting skill flow. **Setup is fully automated via `--with-n8n`:** Docker is installed if missing, n8n container is started, and a Playwright headless script (`n8n-setup-account.py`) creates the owner account, generates an API key, and writes it back to `n8n.env` — then `create-n8n-workflows.py` creates and activates all 7 workflows. The only manual step is setting `N8N_EMAIL` + `N8N_PASSWORD` in `~/.claude/.secrets/n8n.env`; setup.sh pauses and waits if they're still at placeholder values.

**Lean every-turn payload** — CLAUDE.md is loaded on every prompt, so reference material moves out of it. The four MCP integration sections (Browser, CodeGraph, Context7, Figma) live in `mcp-guides/<name>.md` and are read on-demand by the skills that actually need them. CLAUDE.md keeps a 30-line consolidated stub (trigger map + decision shortcuts + pointers). Result: **CLAUDE.md ≈ 22 KB instead of 39 KB (−43%)**, which translates to roughly 3.5 K tokens saved per cold-start session — pipeline order, decision matrix, save triggers, and trigger keywords are all unchanged.

**Size-budget lints** — `lint-skills.py` warns when CLAUDE.md > 35 KB, any SKILL.md > 25 KB, or a memory entry body > 1.5 KB. The budgets are calibrated to the per-turn loading audit; warnings show up next to frontmatter/link checks so regrowth is caught at edit time instead of months later.

---

## License · Credits

MIT · Inspired by [9arm-skills](https://github.com/thananon/9arm-skills)  
PR welcome — new skills must be used ≥ 2 weeks in production + prove they catch something existing skills don't.

