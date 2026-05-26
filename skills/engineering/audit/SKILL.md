---
name: audit
description: Use for whole-project health sweep across 4 dimensions — Performance/bundle, Code Quality/anti-pattern, Test Coverage/quality, Dependency/supply-chain. Read-only — produces inline report only, NEVER fixes (yield to fe/migrate/debug for that). Trigger on Thai keywords audit/ตรวจสุขภาพ project/สแกนทั้งโปรเจกต์/รีวิวทั้ง project/หา bloat/หา dead code/ตรวจ dependency/project health/หา anti-pattern ทั้งโปรเจกต์/ตรวจ test coverage and English keywords audit/project audit/health check/codebase sweep/find bloat/find dead code/check deps/outdated/CVE/coverage gap/code smell/anti-pattern scan. Examples "audit project นี้ให้หน่อย", "ตรวจสุขภาพ codebase", "หา dead code ทั้งโปรเจกต์", "ตรวจ dependency มี CVE ไหม", "test coverage เป็นยังไงบ้าง", "หา bundle bloat". DO NOT use for review pending changes (use /review), security audit alone (use sa or /security-review), single-bug diagnosis (use debug), or single-file refactor (use fe).
---

# audit — Project health sweep (4 dimensions, read-only)

**Report only, never fix.** Audit is the eyes, not the hands — fixes must yield to `fe` / `migrate` / `debug`

Every finding must have **file:line + evidence (numbers) + suggested action** — not opinions

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (see `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: audit | cross | fe | sa` + dimension keyword (perf, dead-code, coverage, cve, bloat)
- **Learnings filter:** `~/.claude/skills/audit/learnings.md` by Tags (max 5)
- **Critical:** use memory to **filter false-positives** — findings the user previously accepted as "intentional" → omit from report (or downgrade to info)
- **Size check:** `find . -name '*.vue' -o -name '*.ts' | wc -l` > 1000 → notify user + propose narrower scope

---

## Progress tracker

Copy this block into your first response and tick boxes as each phase finishes. The fix queue and memory save are mandatory — do not stop at "report only".

```
Audit progress:
- [ ] Phase 1: Stack detected + stated in report
- [ ] Phase 2: Dimension 1 — Performance / bundle scanned
- [ ] Phase 2: Dimension 2 — Code Quality / anti-pattern scanned
- [ ] Phase 2: Dimension 3 — Test Coverage / quality scanned
- [ ] Phase 2: Dimension 4 — Dependency / supply chain scanned
- [ ] Phase 3: Filtered + deduped (node_modules / accepted findings)
- [ ] Phase 4: Severity ranked (criteria respected)
- [ ] Phase 5: Inline report written (file:line + evidence + suggest)
- [ ] Post-report: Fix queue produced + saved to project memory
- [ ] Quality gates passed
```

---

## Phase 1 — Stack detection

Identify stack to pick tools that actually work:

| signal | tool to use |
|---|---|
| `package.json` has `nuxt` | `nuxi`, `vue-tsc`, bundle analyzer |
| has `vue` (no nuxt) | `vue-tsc`, vite analyzer |
| has `react`/`next` | `tsc`, next bundle analyzer |
| has `vitest`/`jest`/`playwright` config | matching coverage tool |
| `pnpm-lock.yaml` / `bun.lockb` / `yarn.lock` / `package-lock.json` | use matching pm |

State in report which stack the audit ran on — can't detect → ask user

---

## Phase 2 — Dimension scans (parallelizable)

### Dimension 1: Performance / bundle

| scan | command / signal | finding example |
|---|---|---|
| Full-module import | `rg "import \w+ from ['\"]lodash['\"]"` | `import _ from 'lodash'` → +71KB |
| Heavy lib in client | `rg "moment\|jquery\|chart.js"` | moment → use dayjs |
| No lazy-load route | page doesn't use `defineAsyncComponent` / dynamic import | large route in initial bundle |
| Unoptimized image | `rg "<img"` (not `<NuxtImg>`/`<NuxtPicture>`) | static img bypasses pipeline |
| N+1 fetch | `useFetch` in loop / map | `v-for` wrapping `useFetch` |

**Never claim "slow" without numbers** — bundle KB / render count / waterfall

**Runtime perf (chrome-devtools MCP — supplements static scan):** open browser → `performance_start_trace` → run main flow (navigate / interact) 3-5 seconds → `performance_stop_trace` → `performance_analyze_insight` — yields FCP, LCP, TBT, CLS, blocking functions. Use paired with `lighthouse_audit` (category=performance) to confirm. See details in **Runtime audit playbook** below.

### Dimension 2: Code Quality / anti-pattern

| scan | command / signal | finding example |
|---|---|---|
| Dead code (export) | `rg "export "` + trace caller `rg "from ['\"].*<file>['\"]"` | export with 0 callers |
| Duplicate logic | similar function name + similar body | `formatDate` in 3 places |
| God component | `wc -l app/components/*.vue` > 500 | `OrderForm.vue` 1200 lines |
| Deep nesting | `v-if` / `v-for` nested ≥ 4 levels | template nesting hell |
| Magic number | `rg "\b[0-9]{3,}\b"` in logic | `setTimeout(fn, 3600000)` |
| Mutation of props | `rg "props\.\w+ ="` | direct mutate prop |

**Every "dead code" must trace caller ≥ 1 hop before claiming** — Universal CLAUDE.md rule

### Dimension 3: Test Coverage / quality

| scan | command / signal | finding example |
|---|---|---|
| Coverage gap | `coverage/coverage-summary.json` | `useAuth.ts` 0% covered, used in 12 places |
| Critical path no test | high-fan-in file + no test | high blast radius, no test |
| Weak assertion | `rg "expect.*\.toBe(true\|truthy\|defined)"` | assert without value |
| No error case | test has `it()` but no `toThrow` / `rejects` | happy path only |
| Brittle timing | `rg "setTimeout\|setInterval" test/` | flaky timing test |
| Skip / focus left | `rg "(it\|describe)\.(skip\|only)" test/` | committed `.only` / `.skip` |

**Flag "critical path has no test"** (high blast radius) — don't flag "few tests" in general

### Dimension 4: Dependency / supply chain

| scan | command | finding example |
|---|---|---|
| Outdated | `rtk proxy pnpm outdated` / `rtk proxy npm outdated` | vue@3.4 → 3.5 (major) |
| CVE | `rtk proxy pnpm audit --prod` / `rtk proxy npm audit --omit=dev` | `lodash@4.17.20` GHSA-xxx |
| Unused dep | `package.json` deps vs `rg "from ['\"]<dep>['\"]"` | `moment` in deps but not imported |
| Duplicate transitive | `rtk proxy pnpm why <pkg>` | 3 versions of `tslib` |

**Never run `npm install <tool>` to scan** — use existing tools; none → suggest to user

---

## Runtime audit playbook (chrome-devtools MCP — supplements Dimension 1 & a11y)

> Enable when MCP `chrome-devtools` is available + user requests perf / a11y audit requiring real numbers — static scan alone gives only "possibly slow/broken" while runtime audit gives "X ms slow / a11y score Y / function Z blocking"

### Performance trace recipe

```
1. navigate_page <localhost url>
2. performance_start_trace (reload: true to capture initial load)
3. wait 3-5 seconds + interact through main flow (login → main page → key action)
4. performance_stop_trace
5. performance_analyze_insight → read:
   - Core Web Vitals: FCP, LCP, TBT, CLS, INP
   - Long tasks (> 50ms) + call tree
   - Render-blocking resources
   - Layout shifts (CLS contributors)
6. Report in Dimension 1 table with actual numbers
```

### Lighthouse audit recipe (a11y + perf + best-practice in one pass)

```
1. navigate_page <localhost url>
2. lighthouse_audit categories=[performance, accessibility, best-practices, seo]
3. Read:
   - score per category (0-100)
   - opportunities (perf): list of fixes + estimated saving (KB / ms)
   - violations (a11y): rule + element + severity
4. Convert to finding row:
   - 🔴 a11y violation (contrast, missing label, focus trap)
   - 🟠 perf opportunity > 500ms saving
   - 🟡 best-practice fail (CSP, deprecated API)
```

### Memory leak recipe

```
1. navigate_page <localhost url>
2. take_memory_snapshot ← baseline
3. repeat suspected leak action 5-10 times (open/close modal, navigate back/forth)
4. take_memory_snapshot ← after
5. compare heap size — growth > 10MB / detached node count → flag as finding
```

### Tool selection (token-aware — runtime tools are more expensive than static)

| What numbers you need | Tool | Token cost | When to use |
|---|---|---|---|
| Web Vitals + long task | `performance_start/stop/analyze_insight` | 5-15k | Dimension 1 in every audit |
| A11y score + violations | `lighthouse_audit category=accessibility` | 3-10k | Project audit where user requests a11y |
| Bundle saving opportunity | `lighthouse_audit category=performance` | 3-10k | Confirm "lodash heavy" with Coverage tab |
| Memory leak | `take_memory_snapshot` × 2 | 4-10k | Suspected leak from code pattern |
| CSP / security header | `list_network_requests` | 500-5k | Dimension 4 supply chain audit |
| Cross-browser a11y behavior (ARIA / keyboard nav) | `playwright-firefox` + `playwright-webkit` | 1-3k/browser | Engine-specific ARIA differences beyond Lighthouse |

### Cross-browser a11y recipe (Playwright)

> Use when: user requests cross-browser a11y audit OR when ARIA behavior / keyboard navigation may differ between Chromium (Lighthouse) and real Firefox / Safari engines

```
1. Run chrome-devtools lighthouse_audit category=accessibility — Chromium baseline score
2. playwright-firefox: browser_navigate <url> → browser_press_key "Tab" (5x) → browser_take_screenshot → verify focus ring visible
3. playwright-firefox: browser_evaluate "() => document.activeElement.tagName" — verify Tab order / focus management
4. playwright-webkit: same Tab flow → browser_take_screenshot → compare focus ring vs Firefox
5. playwright-webkit: browser_evaluate "() => document.querySelectorAll('[role]').length" — verify ARIA roles loaded
6. Flag: missing focus ring in any engine / broken Tab order / ARIA not announced in Firefox or WebKit
```

### Anti-patterns (MCP-specific for audit — avoid)

- **Lighthouse on every page** — pick 2-3 key pages (landing, dashboard, form) only
- **Performance trace 30+ seconds** — 3-5 sec covers initial load + 1 flow; longer trace wastes tokens + is hard to analyze
- **No reload** before `performance_start_trace` — captures cached result, not cold load
- **`take_snapshot` on full page** — audit doesn't need the DOM tree; use targeted `evaluate_script` query instead

### Output integration (add to report table)

```markdown
| 🟠 | runtime | LCP 4.2s on /dashboard | LCP target 2.5s, function `loadAllOrders` 1.8s blocking | code-split + paginate |
| 🔴 | a11y    | login page contrast fail | 3 violations: button text 2.1:1 (need 4.5:1), missing aria-label on icon button | adjust theme tokens + add aria-label |
```

### Fallback when MCP is unavailable

- Ask user to send Lighthouse report PDF / screenshot from browser DevTools
- Do static scan only + state clearly in report: "perf/a11y dimension = static analysis only, no runtime numbers"

---

## Phase 3 — Filter + dedupe

- Duplicate findings (30 files import lodash) → collapse to 1 entry + count
- Findings in `node_modules/` / `.nuxt/` / `dist/` / `coverage/` / `*.gen.ts` → discard
- Findings memory marks as "intentional" → discard or downgrade to info

---

## Phase 4 — Severity rank

| severity | criteria |
|---|---|
| 🔴 critical | security CVE, data loss, can break production |
| 🟠 high | perf > 50KB, dead code ≥ 200 lines, critical path 0 test |
| 🟡 medium | duplicate logic ≥ 3, weak assertion ≥ 5, outdated major |
| 🟢 low | non-blocking code smell, outdated minor |
| ⚪ info | observation only |

Top 10 per dimension — aggregate count for the rest

---

## Phase 5 — Inline report

```markdown
# Audit — <project name>
**Stack:** Nuxt 4.x, Vue 3.5, Vitest, pnpm
**Scope:** 247 .vue + 138 .ts files

## Summary
| dimension | 🔴 | 🟠 | 🟡 | 🟢 | total |
|---|---|---|---|---|---|
| Performance   | 2 | 5 | 8 | 3 | 18 |
| Code Quality  | 0 | 3 | 12| 5 | 20 |
| Test Coverage | 4 | 6 | 4 | 0 | 14 |
| Dependency    | 1 | 4 | 2 | 1 | 8 |

## <Dimension> — top 10
| sev | file:line | finding | evidence | suggest |
|---|---|---|---|---|
| 🔴 | app/components/Order.vue:12 | full lodash import | +71KB bundle | `import debounce from 'lodash-es/debounce'` |
```

---

## Post-report: Fix queue (mandatory)

After the report, must output a **prioritized fix queue** so user can type "fix #N" and I know immediately which skill to invoke + what context:

```markdown
| # | sev | finding | skill | pre-brief |
|---|---|---|---|---|
| 1 | 🔴 | CVE `lodash@4.17.20` | `debug` | patch → 4.18.0, verify via pnpm audit --prod |
| 2 | 🔴 | `useAuth.ts` 0% coverage, 12 callers | `sa` → `fe` | spec happy+error path first, then write tests |
| 3 | 🟠 | full lodash import in 8 files | `migrate` | `import _ from 'lodash'` → named import across all 8 |
```

**Rules:**
- Order by severity high → low
- pre-brief must be brief but specific enough for the next skill to start immediately
- Same pattern across many files → 1 row + count
- **Save fix queue to project memory** (`project_audit_fix_queue_YYYY-MM-DD.md`) to track across sessions

---

## Handoff

- **Self-contained** when it's scan + report; no touching code
- **Yield `debug`** — real runtime bug found during scan / exploitable CVE
- **Yield `fe`** — user asks for fix; single-file refactor
- **Yield `migrate`** — same pattern in ≥ 10 files
- **Yield `sa`** — test gap reveals ambiguous requirement

---

## Quality gates

- [ ] **Every "dead code" passed caller-trace ≥ 1 hop** — `rg "from ['\"].*<file>['\"]"` returns 0
- [ ] **Every performance claim has numbers** — KB / count / time
- [ ] **Every CVE has advisory ID** — GHSA-xxx / CVE-xxx
- [ ] **Every finding has file:line** — no "across many files in project"
- [ ] **Cross-verify 2 patterns** for dead code + manual spot-check 2–3 files
- [ ] **No new tool installed** — suggest instead
- [ ] **Respect memory** — findings user previously accepted = not in report
- [ ] **Skill learnings updated** if a lesson generalizes across projects

If user has to say "are you sure / re-check" = first scan wasn't thorough enough → memo + fix immediately

---

## Never do

- ❌ **fix** — audit is the eyes (yield to fe/migrate/debug)
- ❌ **flag subjective style/format** — spacing, naming preference, comment style
- ❌ **flag every TODO as a smell** — TODOs have context, read first
- ❌ **install new tools** — suggest instead
- ❌ **use severity "critical"** without security / data-loss / production-down
- ❌ **claim "safe / clean / complete"** before passing quality gates
- ❌ **work out of scope** — full security review → yield `sa` mode B or `/security-review`
