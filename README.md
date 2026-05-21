# claude-skill-copy

Portable skill library for Claude Code — version-controlled mirror of `~/.claude/skills/` **plus** the global Phase 0 / orchestration rules that make the pipeline work.

After `./scripts/setup.sh`, another machine behaves the same as the source machine in every respect **except memory content** (which accumulates per-user as you work).

## What's portable vs not

| Layer | In repo | Per-user |
|---|---|---|
| Skill discipline (mantra, simpler-way gate, ripple checklists, OWASP, audit dimensions) | ✅ | |
| Pipeline orchestration (sa→ux→fe, decision matrix, mid-task yield) | ✅ via `CLAUDE.template.md` | |
| Save triggers + memory hierarchy logic | ✅ via `CLAUDE.template.md` | |
| RTK CLI integration (optional) | ✅ via `RTK.template.md` (commands) — | binary install separately |
| Global memory entries (user preferences, cross-project lessons) | | ✅ accumulates in `~/.claude/memory/` |
| Project memory entries (per-project finding/pattern) | | ✅ accumulates in `~/.claude/projects/<id>/memory/` |

## Install

```bash
git clone https://github.com/Manutsanan/claude-skill-copy.git
cd claude-skill-copy
./scripts/setup.sh
```

`setup.sh` is idempotent and non-destructive by default. It will:

1. Symlink every shippable `SKILL.md` into `~/.claude/skills/<name>`
2. Install `~/.claude/CLAUDE.md` from `CLAUDE.template.md` (skipped if you already have one — use `--force` to overwrite with backup)
3. Install `~/.claude/RTK.md` from `RTK.template.md` (same skip-if-exists logic)
4. Create empty `~/.claude/memory/` + `~/.claude/projects/` if missing

### Flags

- `--force` — overwrite existing `CLAUDE.md` / `RTK.md` (backs them up as `*.bak.YYYY-MM-DD` first)
- `--skip-link` — skip symlink step (if you already linked manually)

### Optional dependency

`RTK.md` documents the [RTK Rust Token Killer](https://github.com/skarekrow/rtk) CLI for token-savings on shell commands. Without RTK installed, skills still work — they just won't use the `rtk proxy ...` prefix.

## Layout

```
.
├── CLAUDE.template.md        ← installed to ~/.claude/CLAUDE.md (Universal Phase 0 + orchestration)
├── RTK.template.md           ← installed to ~/.claude/RTK.md (optional RTK reference)
├── FOLLOWUPS.md              ← scheduled reviews (mantra usefulness, distillation)
├── .claude-plugin/
│   └── plugin.json           ← skill registry (promotion gate)
├── scripts/
│   ├── setup.sh              ← full bootstrap (this file)
│   ├── link-skills.sh        ← symlink-only step
│   └── list-skills.sh        ← list every SKILL.md
└── skills/
    ├── engineering/          ← daily code work (linked into ~/.claude/skills/)
    ├── misc/                 ← meta utilities (linked)
    ├── in-progress/          ← drafts (NOT linked)
    └── deprecated/           ← retired (NOT linked)
```

## Skills (engineering bucket)

- [audit](skills/engineering/audit/SKILL.md) — whole-project health sweep (perf, code quality, coverage, deps). Read-only.
- [debug](skills/engineering/debug/SKILL.md) — runtime error diagnosis. Mantra recital, ranked hypotheses, falsify-first, breadcrumb ledger.
- [fe](skills/engineering/fe/SKILL.md) — frontend code (Nuxt/Vue/React/TS): components, composables, schemas, state, reactivity. Reference details in [REFERENCE.md](skills/engineering/fe/REFERENCE.md).
- [migrate](skills/engineering/migrate/SKILL.md) — bulk transformations across many files (Discover → Plan → Execute → Cross-verify).
- [sa](skills/engineering/sa/SKILL.md) — system analyst (Mode A: spec, starts with simpler-way gate) + security audit (Mode B: OWASP-aligned).
- [ux](skills/engineering/ux/SKILL.md) — visual / interaction design: layout, animation, responsive, a11y, modern aesthetic.

## Misc

- [_template](skills/misc/_template/SKILL.md) — skeleton for creating new skills (copy and adapt).

## Promotion gate

Skills in `engineering/` or `misc/` must:

1. Have an entry above (with skill name linked to its `SKILL.md`).
2. Have an entry in `.claude-plugin/plugin.json`.

Half-finished work lives in `in-progress/` (skipped by `link-skills.sh`) until it earns a row.

## How memory accumulates

Memory starts empty per machine. It grows as you work via the **8 save triggers** documented in `CLAUDE.template.md` (Universal Phase 0 #4):

- User correction / confirmation
- Errors with root cause
- New approach that worked
- Cross-project repetition

Three tiers (lowest → highest scope):

```
project memory (~/.claude/projects/<id>/memory/)
    ↓ (recurs in 2+ projects)
global memory (~/.claude/memory/)
    ↓ (recurs in 3+ projects, same skill)
skill learnings (~/.claude/skills/<skill>/learnings.md — in this repo)
    ↓ (load-bearing universally)
SKILL.md rule (in this repo)
```

Run `/distill-memory` periodically to promote stale entries up the chain. Quarterly review recommended — see `FOLLOWUPS.md`.

## Upgrade path

When the upstream repo updates (e.g. new SKILL.md content):

```bash
cd ~/Project/claude-skill-copy
git pull
# Skills auto-update via symlinks — no further action needed.
# If CLAUDE.template.md changed:
./scripts/setup.sh --force   # backs up your CLAUDE.md first
```

Your memory (`~/.claude/memory/`, `~/.claude/projects/`) is untouched.
