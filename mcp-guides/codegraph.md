# CodeGraph MCP integration — codebase intelligence layer

> **Loaded on-demand by skills that need ripple analysis** (sa / fe / debug / migrate). Referenced from CLAUDE.md skill orchestration.
>
> **MCP `codegraph` is the "semantic map" of the codebase** — transforms ripple checks from line-by-line grep → semantic graph traversal that knows call paths, impact, and callers instantly.

## Trigger map (which tool to use, when)

| Trigger | Skill | Tool |
|---|---|---|
| Ripple check before editing an existing symbol | all skills | `mcp__codegraph__callers <symbol>` |
| View call path / trace A calls B calls C | `debug` Step 2 | `mcp__codegraph__trace <symbol>` |
| Understand what this file/component does + connects to | `sa` mode A | `mcp__codegraph__context <file>` |
| Find a symbol whose name is uncertain | all skills | `mcp__codegraph__search <keyword>` |
| Analyze impact if this symbol changes | `sa` / `fe` | `mcp__codegraph__impact <symbol>` |
| View symbol details (type, location, signature) | all skills | `mcp__codegraph__node <symbol>` |
| View source of multiple symbols at once | `sa` / `migrate` | `mcp__codegraph__explore <sym1> <sym2>` |
| View what this symbol calls (outgoing) | `fe` / `debug` | `mcp__codegraph__callees <symbol>` |

## Decision rule (rg vs codegraph)

| Situation | Tool |
|---|---|
| Symbol created in this session (index lag ~1-2s) | `rg` always |
| Literal string / comment / non-code text | `rg` always |
| Existing symbol + need semantic callers | `mcp__codegraph__callers` first |
| Critical + high-risk change | cross-verify both: `mcp__codegraph__impact` + `rg` |

## Project index (must init before use in each project)

```bash
codegraph init -i   # run once in the project root dir
```

If not yet initialized → tools will error or return empty → fallback to `rg` immediately + tell user to run init

## Token cost reference

| Tool | Token cost | Use when |
|---|---|---|
| `codegraph__callers` | ~200-500 🟢 | Ripple check before every symbol change |
| `codegraph__trace` | ~200-500 🟢 | Call path from crash site |
| `codegraph__search` | ~100-300 🟢 | Symbol discovery |
| `codegraph__impact` | ~500-1k 🟡 | High-risk or cascading change |
| `codegraph__context` | ~1-3k 🟡 | Understanding a file's role |
| `codegraph__explore` | ~1-5k 🟡 | Multi-symbol source dump |

## Quality rules

- Never declare "no ripple" from `codegraph__callers` alone if the change is critical (type contract / auth gate) — cross-verify with `rg` too
- If `codegraph__callers` returns empty + the symbol should have callers → suspect stale index → run `rg` then tell user to run `codegraph init -i` again
- If project has no `.codegraph/codegraph.db` → do not reference codegraph — fallback to `rg` + tell user to init first

## Skill integration reference

Skills with their own CodeGraph section:
- `sa/SKILL.md` — context loading + impact analysis in reference tracing checklist
- `fe/SKILL.md` — callers check before touching existing code
- `debug/SKILL.md` — trace call path in Step 2 + callers in Step 6
- `migrate/SKILL.md` — callers discovery in Phase 0 Discover
