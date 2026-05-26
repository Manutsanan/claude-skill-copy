# Context7 MCP integration — live library documentation layer

> **Loaded on-demand by skills that consume external library APIs** (`fe` + `debug` + `migrate` + `sa`). Referenced from CLAUDE.md skill orchestration.
>
> **MCP `context7` is the "live docs" layer** — fetches real documentation for external libraries by version, injecting it into the prompt instead of relying on stale training data.

## Trigger map (which tool to use, when)

| Trigger | Skill | Tool |
|---|---|---|
| Writing code using a new external library API (Nuxt UI, Valibot, Pinia, useFetch) | `fe` | `resolve-library-id` → `query-docs` |
| Error pointing to library behavior / breaking change | `debug` Step 4a | `query-docs <error pattern>` |
| Migrating between library versions | `migrate` Phase 0 | `resolve-library-id` → `query-docs "migration guide"` |
| Specifying API that depends on external library (opt-in) | `sa` mode A | `query-docs <API feature>` |

## Tool names

- `mcp__context7__resolve-library-id` — convert library name → Context7-compatible library ID
- `mcp__context7__query-docs` — fetch docs by library ID + query

## Decision rule (query vs skip)

| Situation | Action |
|---|---|
| Library is internal / custom package | ❌ skip — no index |
| Pattern already exists in `learnings.md` | ⚠️ skip — cached |
| Library in default stack + unfamiliar new API | ✅ query |
| Error may be caused by library version change | ✅ query always |
| Migrating library major/minor version | ✅ query always |

## Token cost reference

| Tool | Token cost | Note |
|---|---|---|
| `resolve-library-id` | ~100-200 🟢 | Run once per library per session |
| `query-docs` (narrow query) | ~500-2k 🟢 | Keep query specific — "UButton loading prop" not "all of Nuxt UI" |
| `query-docs` (broad query) | ~2-10k 🔴 | Forbidden — adds tokens unnecessarily |

## Quality rules

- **Always query narrow** — 1 specific feature per call; never query just the library name
- **1 library per call** — never combine queries for multiple libraries in one call
- Library not in index → fallback to official docs from training data + tell user
- Confirmed patterns → save to `~/.claude/skills/<skill>/learnings.md` to skip querying next time

## Skill integration reference

- `fe/SKILL.md` — query before implementing new library-specific API
- `debug/SKILL.md` — query in Step 4a when hypothesis involves library breaking change
- `migrate/SKILL.md` — query in Phase 0 Discover when migrating library version
- `sa/SKILL.md` — query opt-in when spec depends on external library API
