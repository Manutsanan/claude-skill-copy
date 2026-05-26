# Figma MCP integration — design source layer

> **Loaded on-demand by skills that consume Figma designs** (`ux` primarily + `sa` for requirement gathering from Figma comments). Referenced from CLAUDE.md skill orchestration.
>
> **MCP `figma` is the "design source" layer** — loads Figma design directly into context + views thumbnails of specific nodes + reads/writes design comments.

## Tool signatures (real — from schema)

| Tool | Required params | Returns |
|---|---|---|
| `mcp__figma__add_figma_file` | `url` (Figma file URL) | Design structure + file_key loaded into context |
| `mcp__figma__view_node` | `file_key`, `node_id` (`<n>:<n>`) | **Thumbnail image** of that node |
| `mcp__figma__read_comments` | `file_key` | All comments on the file |
| `mcp__figma__post_comment` | `file_key`, `message`, `x`, `y` (+ optional `node_id`) | Posts comment at coordinate |
| `mcp__figma__reply_to_comment` | `file_key`, `comment_id`, `message` | Reply to existing comment |

**Extract params from URL:**
- `file_key` — from `figma.com/file/<file_key>/...` or `figma.com/design/<file_key>/...`
- `node_id` — from URL param `?node-id=<n>-<n>` → convert `-` to `:` → `<n>:<n>`

## Trigger map (which tool to use, when)

| Trigger | Skill | Tool |
|---|---|---|
| User sends Figma URL (first time in session) | `ux` | `add_figma_file` — load full design structure first |
| Need visual of a specific component | `ux` | `view_node` (specify narrow node_id) |
| Read design comments / feedback | `sa` / `ux` | `read_comments` |
| Reply or post comment on Figma | `sa` | `reply_to_comment` / `post_comment` — **always notify user first** |

## Decision rule

| Situation | Action |
|---|---|
| User sends Figma URL | ✅ `add_figma_file` always — gets structured design data |
| Need visual confirmation of component after add | `view_node` with specific node_id only |
| Figma requires auth / incorrect URL | ❌ fallback → ask user for screenshot + description |
| Need live visual of Figma | `take_screenshot` via chrome-devtools on the Figma URL |

## Quality rules

- **Always `add_figma_file` first** when encountering a new Figma URL — never skip, even if "you think you know it"
- **`view_node` specifies a specific node** not the root node of the full page — cost grows with subtree size
- **Figma values are source of truth** — spacing/color/font from design → use directly, never estimate
- **Before post/reply comment** → notify user first every time, because it is visible to other designers

## Skill integration reference

- `ux/SKILL.md` — `add_figma_file` before designing from Figma + `view_node` to confirm specific components
- `sa/SKILL.md` — `read_comments` to gather requirements from design feedback
