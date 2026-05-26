# Browser MCP integration — runtime observation layer

> **Loaded on-demand by skills that need browser observation.** Referenced from CLAUDE.md skill orchestration; read the relevant section here when verifying / debugging / running UI / auditing.
>
> **Default browser MCP is `playwright-chromium`** — use for all navigation, click, screenshot, console, network, and evaluate tasks. Reserve `chrome-devtools` **only** for Lighthouse scores, performance traces, and memory heap snapshots (tools unavailable in Playwright).

## When to open the browser (trigger map)

| Trigger | Skill | Primary tool |
|---|---|---|
| User requests verify / before declaring done when UI was touched | `verify` / all skills | playwright-chromium — `browser_navigate` → `browser_click` → `browser_snapshot` → `browser_console_messages` |
| Error stack / runtime crash / X broken / X not working | `debug` | playwright-chromium — `browser_navigate` → `browser_console_messages` + `browser_network_requests` + `browser_evaluate` |
| User requests to open app / "show me it running" | `run` | playwright-chromium — `browser_navigate` → `browser_take_screenshot` |
| After finishing a style batch / before claiming ux done | `ux` | playwright-chromium — `browser_take_screenshot` + `browser_resize`; chrome-devtools for `lighthouse_audit` only |
| User requests perf / a11y audit | `audit` | chrome-devtools only — `lighthouse_audit` + `performance_start_trace`/`stop`/`analyze_insight` + `take_memory_snapshot` |
| Reviewing code that touches auth / cookie / CSP / CORS | `security-review` | playwright-chromium — `browser_network_requests` + `browser_evaluate` + `browser_console_messages` |
| Verifying reactivity / hydration / memory leak | `fe` (opt-in) | playwright-chromium — `browser_evaluate` + `browser_console_messages`; chrome-devtools for memory heap only |
| Cross-browser bug / visual diff / a11y engine difference | `debug` / `ux` / `audit` | `playwright-firefox` / `playwright-webkit` — `browser_navigate` + `browser_take_screenshot` |
| Form interaction: dropdown / back button / drag-drop | `debug` | playwright-chromium — `browser_select_option` / `browser_navigate_back` / `browser_drop` |

**Do not open browser when:** spec/requirement (`sa` mode A), static codemod (`migrate`), backend-only logic, config/docs, typo, simplify, init

## Browser MCP decision rule

| Need | MCP to use | Reason |
|---|---|---|
| Lighthouse score (perf / a11y / best-practice) | `chrome-devtools` only | Playwright has no lighthouse |
| Performance trace (Web Vitals / long tasks) | `chrome-devtools` only | `performance_start_trace` not in Playwright |
| Memory heap snapshot | `chrome-devtools` only | `take_memory_snapshot` not in Playwright |
| Cross-browser engine test (Firefox / WebKit/Safari) | `playwright-firefox` / `playwright-webkit` | Real engine — emulation is not equivalent |
| Multi-tab (same user, same context) | `playwright-chromium` + `browser_tabs` | Tab management within same session |
| Multi-session isolation (different users / fresh state) | Separate terminal each with own Claude CLI | Each terminal = isolated context (`--isolated`); tabs alone do NOT isolate cookies |
| Everything else (navigate, click, screenshot, console, network, evaluate, interact) | `playwright-chromium` (default) | Default browser MCP |

**Rule:** playwright-chromium = default for all browser work; chrome-devtools = Lighthouse / perf trace / memory heap only; playwright-firefox/webkit = cross-browser engine tests

## Token cost reference (know the price before choosing a tool)

| Tool | Token cost | Use when |
|---|---|---|
| `take_snapshot` of large dashboard page | 15-20k 🔴 | Need uid of element to interact |
| `take_snapshot` of small page | 5-10k 🟡 | Need uid + a11y tree |
| `take_screenshot` (viewport) | 1-3k 🟢 | Need to see page / proof |
| `lighthouse_audit` (1 category) | 3-5k 🟡 | Check a11y/perf score |
| `lighthouse_audit` (all categories) | 10-15k 🔴 | Forbidden unless user asks for full audit |
| `performance_analyze_insight` (5s trace) | 5-10k 🟡 | Diagnose initial load |
| `performance_analyze_insight` (30s trace) | 15-30k 🔴 | Forbidden unless steady-state issue |
| `list_console_messages` | 500-2k 🟢 | Explore console |
| `list_network_requests` | 500-5k 🟢 | Explore network |
| `evaluate_script` | 100-2k 🟢 | Inspect specific value |
| `get_console_message <i>` / `get_network_request <id>` | 200-500 🟢 | Know index/id, narrow lookup |
| `take_memory_snapshot` | 2-5k 🟡 | Diagnose memory leak |

**Principle:** open browser only when necessary (verify / reproduce / proof) — never on every turn that touches UI

## Broad-vs-narrow decision rule (mandatory — apply before every browser tool call)

> **Core rule:** explore broad first, narrow later — never narrow from the start if you don't know what to ask

| Situation | Answer | Tool to use |
|---|---|---|
| Know exactly what to check (have hypothesis) | ✅ Yes — narrow | `evaluate_script` / `get_console_message` / `get_network_request` |
| Don't know, need to explore first (strange bug, first time on this page) | ❌ No — broad first | `take_snapshot` / `take_screenshot` / `list_console_messages` |
| Need proof to show user | ✅ Yes — but visual | `take_screenshot` |
| Check visual regression | ✅ Yes — but context | `take_screenshot` (full page) |

**Mandatory:** never use `evaluate_script` blindly on first debug — wrong query will miss the bug. Use a broad tool once to see the overall picture, then narrow.

## Token-saving toolkit (mandatory — apply on every browser tool call)

### 🟢 Safe-always (use anytime, no trade-off)

1. **Combine multiple checks in a single `evaluate_script`** — atomic state + ~80% savings
   ```js
   evaluate_script("JSON.stringify({
     state: <inspect 1>,
     errors: <inspect 2>,
     network: <inspect 3>
   })")
   ```

2. **Use `get_*` instead of `list_*` when index/id is known** — `get_console_message <i>`, `get_network_request <id>`

3. **`wait_for` a specific selector before observing** — prevents flake + reduces re-snapshots

4. **Specify Lighthouse category** — `category=performance` or `category=accessibility` separately (never run all 5 unless user asks for full audit)

5. **Performance trace 3-5 seconds + `reload: true`** — never exceed 10s unless diagnosing a steady-state issue

6. **Close page when task ends** — `close_page` before session ends

### 🟡 Context-dependent (use only in the stated context)

7. **Cache uid across calls** — OK for **static elements** (nav, header, app shell); **never** for list/dynamic/reactive components → re-snapshot whenever a component may remount

8. **Element-only screenshot (`uid=X`)** — use for component spec check; **never** for visual regression (needs full page)

9. **Batch actions before observing** — use for **success-path verify**; **never** during step-by-step debug (hides intermediate bugs)

10. **Same-page `navigate_page` instead of `new_page`** — use for continuous flow; **never** when isolation testing is required (auth, fresh state)

### 🔴 Avoid-by-default (forbidden unless truly necessary)

11. **`take_snapshot` on every step** — only when a fresh uid is needed; **never** as a replacement for screenshot
12. **`take_snapshot` on a large dashboard page** (> 50 components) — use a targeted `evaluate_script` query instead
13. **Lighthouse on every page** — pick 2-3 key pages (landing/dashboard/form) only
14. **Screenshot after every click** — observe only when you expect to have reached the target state

## Decision flow (mandatory — walk this flow before every tool call)

```
1. Do I know what to check?
   ├─ No → 1 broad tool call (snapshot/screenshot/list_*) → return to #1
   └─ Yes → go to #2

2. Which tool fits best?
   ├─ runtime value → evaluate_script (combine checks)
   ├─ console error → get_console_message <i> or list_console_messages
   ├─ network fail → get_network_request <id> or list_network_requests
   ├─ visual proof → take_screenshot
   └─ need to interact → take_snapshot (for uid) then cache

3. Is the tool on the 🔴 avoid list?
   ├─ Yes → return to #2, pick alternative
   └─ No → call

4. After call: did you get the data needed?
   ├─ Yes → continue
   └─ No → refine query (do NOT re-snapshot immediately)
```

## Quality preservation (prevent optimization from breaking quality)

Token-saving rules **do not reduce quality** when the decision rule above is followed. But forcing narrow from the start causes:

- **Missed bug** from wrong query direction → always broad first
- **Stale uid click** → re-snapshot whenever DOM may change
- **Layout regression invisible** → use full-page screenshot for visual regression
- **Intermediate bug hidden** → never batch during debug

If the user says "why didn't you see the bug" / "verify passed but it's broken in real run" / "why didn't you catch it" = optimization was too aggressive → return to broad scan + interrogate root cause

## Fallback when MCP is unavailable

If MCP `chrome-devtools` is offline / dev server isn't running / user disabled MCP — fall back in order:

1. Ask user to paste screenshot / console log instead (manual capture is more accurate for real-env visual state)
2. For verify → say plainly: "verify is code-level only (tsc + test) — not tested in a real browser". Never blanket-claim done
3. For debug → ask user for steps to reproduce + browser/version

## Manual paste vs MCP — use together, not either-or

- **Manual paste is more accurate for:** the user's real state (auth, cookie, prod data), env-specific bugs, user context (arrows, "this part")
- **MCP is more accurate for:** structural DOM (uid + a11y tree), runtime state (JS/network/console), reproduce + verify fix, responsive testing
- **Best workflow:** manual paste → start understanding the bug; MCP → dig out root cause + verify fix

## Skill integration reference

Custom skills with their own chrome-devtools + Playwright sections (read each skill's SKILL.md for specifics):
- `debug/SKILL.md` — playwright-chromium: default for all single-browser debugging (console/network/state/interactions); playwright-firefox/webkit: cross-browser engine bugs; chrome-devtools: perf trace + memory heap only
- `ux/SKILL.md` — chrome-devtools: visual + lighthouse + responsive; Playwright: cross-browser engine screenshot comparison
- `audit/SKILL.md` — chrome-devtools: lighthouse + perf trace + memory; Playwright: cross-browser a11y behavior (ARIA / keyboard nav)
- `fe/SKILL.md` — chrome-devtools: reactivity/hydration inspect; Playwright: cross-browser hydration verify

Built-in skills (verify / run / security-review) — use the trigger map + token discipline above as the guide, since these skills can't be edited directly
