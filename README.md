# claude-skill-copy

Personal skill library for Claude Code — version-controlled copy of `~/.claude/skills/`.

## Layout

Skills live under `skills/`, grouped into buckets:

- `engineering/` — daily code work (sa → ux → fe pipeline + debug / migrate / audit)
- `misc/` — meta utilities (templates, kept around)
- `in-progress/` — drafts not yet ready to ship (skipped by `link-skills.sh`)
- `deprecated/` — retired skills (skipped by `link-skills.sh`)

Each skill = one directory containing `SKILL.md` (with YAML frontmatter — `name`, `description`) plus any bundled `learnings.md` / reference files.

## Install

Symlink every shippable skill into `~/.claude/skills/`:

```bash
./scripts/link-skills.sh
```

List every `SKILL.md`:

```bash
./scripts/list-skills.sh
```

The link script skips `in-progress/`, `deprecated/`, and `personal/` — use those buckets to experiment without shipping.

## Promotion gate

Skills in `engineering/` or `misc/` must:

1. Have an entry below (with skill name linked to its `SKILL.md`).
2. Have an entry in `.claude-plugin/plugin.json`.

This keeps half-finished work out of the live `~/.claude/skills/` until it earns a row in the index.

## Skills

### engineering/

- [audit](skills/engineering/audit/SKILL.md) — whole-project health sweep (performance, code quality, test coverage, dependencies). Read-only.
- [debug](skills/engineering/debug/SKILL.md) — diagnose runtime errors. Recite the debug mantra, build a hypothesis ledger, falsify before fixing.
- [fe](skills/engineering/fe/SKILL.md) — frontend code work (Nuxt/Vue/React/TypeScript): components, composables, schemas, state, reactivity.
- [migrate](skills/engineering/migrate/SKILL.md) — bulk transformations across many files (legacy → new pattern, codemod style).
- [sa](skills/engineering/sa/SKILL.md) — system analyst (Mode A: spec) + security audit (Mode B: OWASP). Mode A starts with the simpler-way gate.
- [ux](skills/engineering/ux/SKILL.md) — visual / interaction design: layouts, components, animation, responsive, accessibility.

### misc/

- [_template](skills/misc/_template/SKILL.md) — skeleton for creating new skills (copy and edit).
