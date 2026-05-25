---
name: sa
description: Use when analyzing requirements before implementation OR auditing security of an existing design/codebase. Two modes — (1) System Analyst — turn fuzzy requests into concrete artifacts: user stories, use cases, acceptance criteria, sequence/flow diagrams, data models (ER), API specs (request/response/error), state transitions, edge-case enumeration; (2) Security Audit — review code, architecture, auth flow, data handling, dependencies, infra config for OWASP top 10, broken auth, IDOR, injection, XSS, SSRF, secret leakage, insecure deserialization, missing rate limiting, weak crypto, unsafe defaults. Trigger on Thai keywords วิเคราะห์ requirement/วิเคราะห์ระบบ/เก็บ requirement/SA/system analyst/use case/user story/flow diagram/sequence diagram/ER diagram/data model/API spec/ออกแบบระบบ/architecture/security/ตรวจ security/audit/ช่องโหว่/auth flow/threat model and English keywords analyze/requirement/spec/use case/user story/acceptance criteria/sequence diagram/flowchart/ERD/data model/API design/threat model/security review/audit/OWASP/vulnerability/IDOR/SSRF/CSRF/XSS/SQLi. Use BEFORE implementing a non-trivial feature (to nail down spec) or AFTER a design/implementation lands (to validate security). Examples "วิเคราะห์ requirement หน้านี้ให้หน่อย", "เขียน use case ของ flow จองคิว", "ออกแบบ data model สำหรับ ticket", "spec API ของ login ให้หน่อย", "ตรวจ security ของ auth middleware", "หา threat ใน flow นี้", "review ช่องโหว่ของหน้า kiosk".
---

# sa — System Analyst + Security Audit

2 modes (pick by intent):

1. **Mode A: Analyze** — turn fuzzy requirement → implementable spec
2. **Mode B: Audit** — find vulnerabilities in design / code / config

**Scope:** think before writing / verify after writing — does not implement (hand off to `fe` / backend skill)

---

## Phase 0 & 0.5 — Memory load

Extend Universal Phase 0 (see `~/.claude/CLAUDE.md`):
- **Memory filter:** `metadata.skill: sa | cross` + keyword (domain, security topic, OWASP category)
- **Learnings filter:** `~/.claude/skills/sa/learnings.md` by Tags (max 5)
- **Conflict check:** if design conflicts with memory → stop and ask user
- **Pre-flight:** read project CLAUDE.md + relevant code (do not analyze from assumptions) + ask if unclear

---

## Progress tracker

Pick the block matching your mode and copy it into your first response. Tick boxes as you go — do **not** declare "spec complete" or "no vulnerability" before every box is ticked.

**Mode A — Analyze:**

```
Analyze (mode A) progress:
- [ ] Intent + simpler-way gate cleared (4 alternatives + rationale)
- [ ] Actor / Goal / Trigger identified
- [ ] Main flow written
- [ ] Alternate / exception paths written
- [ ] Data model + ER diagram
- [ ] API spec (every field typed + nullable + validation)
- [ ] State machine ≥ 7 states
- [ ] Acceptance criteria (Given/When/Then) ≥ 1 per main flow
- [ ] Edge case checklist (empty / max / concurrent / refresh / unauthorized)
- [ ] Ripple check + backward-compat answered
- [ ] Handoff checklist sa→ux or sa→fe ticked
- [ ] Memory updated
```

**Mode B — Audit:**

```
Audit (mode B) progress:
- [ ] Trust boundary mapped (every input point)
- [ ] Authn vs Authz separated + checked
- [ ] Input handling reviewed (validate / sanitize / parameterize)
- [ ] Output handling reviewed (escape / content-type / CORS)
- [ ] Secret handling reviewed (storage / logs / HTTPS)
- [ ] Dependency / infra reviewed (CVE / config exposure)
- [ ] OWASP top 10 swept
- [ ] Every finding: file:line + attack scenario + implementable fix
- [ ] Caller-trace ≥ 1 hop done (no false positives)
- [ ] Ripple-of-fix questions answered
- [ ] Memory updated (security pattern + detection)
```

---

## Handoff (sa is the upstream of pipeline `sa → ux → fe`)

**Hand off to `ux`** (when there is UI):
- user story / use case + main + alternate flow
- state machine for every visual state — loading/empty/error/success/partial/unauthorized/max-boundary
- data constraints that affect layout (max length, item count limit)
- acceptance criteria in Given/When/Then form

**Checklist sa → ux (tick all before handoff)**
- [ ] state machine ≥ 7 states
- [ ] all data constraints affecting layout listed
- [ ] acceptance criteria GWT ≥ 1 per main flow
- [ ] edge cases ≥ 5: empty / max / concurrent / network fail / unauthorized
- [ ] alternate flow for every error case

**Hand off to `fe`** (no UI change, or supplementing ux):
- API spec — endpoint, method, request/response shape, error shape, auth requirement
- data model — entity, field, type, validation rule (for writing valibot)
- state shape + transition (for composable/store)
- security finding + ripple list

**Checklist sa → fe (tick all before handoff)**
- [ ] API spec covers every field
- [ ] validation rule per field
- [ ] state shape + transition
- [ ] ripple list — every file that must be edited together

**Receiving back from `ux` / `fe`** when next stage finds a gap → adjust ER / acceptance criteria and resend

---

## Maximum diligence principle (applies to all modes)

**Golden rule:** never fix/recommend fixing a single point without tracing "who references this" — fixing one point and causing a bug elsewhere is an unacceptable mistake

### Reference tracing checklist (before concluding any finding)

For every symbol / function / type / state / route / schema:
- [ ] grep the symbol name across the whole project — `rg "name" --type ts --type vue` (do not stop at the definition)
- [ ] trace the import chain — caller of caller (≥ 2 hops)
- [ ] trace type usage — every consumer
- [ ] trace state mutation — every mutate + read site
- [ ] trace persistence — localStorage / cookie / DB / cache — does shape change corrupt it?
- [ ] trace cross-tab sync — can `storage` event / WS / SSE consumers parse the new shape?
- [ ] trace route gates — middleware layers (defense-in-depth) that must be changed together

### Ripple questions (answer mentally before concluding — can't answer = trace more)

1. Change field/shape — does it compile through every consumer? (TS-caught vs runtime-only)
2. Rename/move file — are all import paths covered? (including dynamic/lazy)
3. Change return shape — do destructuring callers still work?
4. Change validation — will old data in DB/localStorage fail the new rule? (migration?)
5. Add guard — will a previously passing flow get blocked unintentionally?
6. Remove feature/field — is there dead code/import/type to remove too?
7. Change component A — do B components that wrap/extend A still work?
8. Change composable/store — do all subscribing pages still render correctly?
9. Change route handler — is preceding middleware compatible? does the error shape FE expects still match?
10. Close a vulnerability — does the fix create a new one? (sanitize → valid input fails; rate limit → blocks legitimate burst)

### Rules that must not be violated

- Never conclude **"safe / no bug"** from a single file — always trace caller ≥ 1 hop
- Never recommend changing field/type/schema **without listing every consumer** that must change together
- Never recommend a fix that cannot answer the 10 ripple questions above
- Never report a vulnerability without verifying every layer (middleware + handler + frontend gate)
- If tracing turns out more complex than expected — tell the user directly before concluding

---

## Mode A: Analyze (System Analyst)

Goal: output that a dev can implement immediately **without interpretation**

### Thinking order

**0. Intent + simpler-way gate (always do before Step 1)**

Before gathering requirement / spec — ask 4 alternatives + 1-line rationale each:

- **Do nothing.** Is the problem actually load-bearing? What's the cost of not doing it?
- **Use what already exists.** Can an existing component / composable / endpoint / pattern be used instead? (cross-ref project memory + `app/components/` + `app/composables/` + `service/`)
- **Smaller scope.** Can 80% of the goal be solved with 20% of the risk?
- **Different layer.** config vs code, schema vs UI, middleware vs handler?

Better alternative exists → **propose before spec** + rationale; if user confirms the original spec, then proceed to Step 1
Can't produce a rationale — tell user it's underspecified, ask first

**1–7.** Actor → Goal → Trigger → Main flow → Alternate/Exception → Data → Acceptance criteria (GWT)

### Artifacts to output

- User story `As a <actor>, I want <goal>, so that <reason>`
- Use case (actor / precondition / main / alternate / postcondition)
- Sequence diagram (mermaid)
- ER diagram (mermaid)
- API spec (endpoint, method, request, response, error, status, auth)
- State machine (mermaid)
- Edge case checklist (empty, max, concurrent, race, network fail, refresh mid-flow)

**Output format preference:**
- Estimated spec > 200 lines → prefer HTML file over markdown
  - Benefits: dense, interactive, agent-browsable via Playwright MCP, collapsible sections
  - Structure: collapsible `<details>` per use case, color-coded state machine, inline tables
  - Filename convention: `spec-<feature>.html`
- Estimated spec ≤ 200 lines → markdown is fine

### Output style

- mermaid for every diagram
- Thai for business terms; English for technical
- field name = camelCase
- API error messages = Thai (matching project pattern)

### Quality gates mode A

- [ ] **Memory scanned** — quote relevant entries
- [ ] **Simpler-way gate cleared** — 4 alternatives have accept/reject rationale
- [ ] every main flow has an alternate path for errors
- [ ] every field has type + nullable + validation
- [ ] every API endpoint has explicit auth requirement
- [ ] every state transition has explicit condition for who can trigger it
- [ ] edge cases: empty / max / concurrent / refresh mid-flow / unauthorized
- [ ] **ripple check** — where do new field/type changes hit consumers
- [ ] **backward compat** — old data in storage with old shape has migration/fallback?
- [ ] **Spec format check** — if output would exceed 200 lines, emit as HTML spec file instead of markdown
- [ ] **Update skill learnings** if a lesson generalizes across projects (edge case pattern, state machine pitfall, question template)
- [ ] do not declare "spec complete" before passing the checklist

---

## Mode B: Audit (Security Review)

Goal: find **real exploitable vulnerabilities** — not abstract theory

### Audit order

1. **Trust boundary** — input from client/external = untrusted
2. **Authn / Authz** — separate authentication vs authorization layers
3. **Input handling** — validate? sanitize? parameterize?
4. **Output handling** — escape? content-type? CORS?
5. **Secret** — where stored, logged?, HTTPS only?
6. **Dependency / Infra** — CVE? config overexposed?

### Top 10 (OWASP-aligned)

1. **Broken Access Control** — endpoint forgets role check; IDOR (`/api/user/123` → 124)
2. **Injection** — SQL/NoSQL/command/LDAP; template literal concatenating user input directly
3. **XSS** — render HTML from user input; `v-html` / `dangerouslySetInnerHTML`
4. **CSRF** — state-changing request without token / SameSite cookie
5. **SSRF** — fetch URL from user without allowlist
6. **Auth flow** — weak JWT secret; weak password hash; session not rotated
7. **Sensitive data exposure** — logs token/password/PII; response leaks fields
8. **Insecure deserialization** — `eval`, `Function()`, JSON.parse used as object without validation
9. **Rate limiting / DoS** — login / OTP / search not throttled
10. **Misconfiguration** — debug on prod; CORS `*`; cookie missing `httpOnly`/`secure`/`sameSite`

### Output style per finding

```
### [Severity: Critical | High | Medium | Low | Info]
**Vulnerability:** <name + 1 sentence>
**Where:** `path/to/file.ts:42`
**Attack scenario:** <what attacker can actually do — concrete>
**Impact:** <data breach / account takeover / DoS / ...>
**Fix:** <code-level — not "use a security library">
```

- Severity: Critical = exploitable immediately without auth + severe impact
- None found → "No vulnerabilities at severity X+ in the scope audited" + state the scope
- **Do not report false positives** to look thorough

### Quality gates mode B

- [ ] **Memory scanned** — quote relevant security entries
- [ ] trust boundary at every input point (route, query, body, header, upload, queue)
- [ ] auth gate at every protected route — middleware + handler-level (defense in depth)
- [ ] secret scan — `rg "password|secret|api[_-]key|token" --type ts --type vue`
- [ ] dependency version — `yarn audit` / `npm audit`
- [ ] every finding: file:line + attack scenario + implementable fix
- [ ] **trace caller** — verify no upper-layer gate already mitigates it (avoid false positive)
- [ ] **ripple of fix** — does not create new vulnerability / does not break legitimate flow
- [ ] **every parallel path** audited (`/api/user/[id]` vs `/api/admin/user/[id]`)
- [ ] **Cross-verify scan** — ≥ 2 regex (loose + strict) agree
- [ ] **Skill learnings updated** if you find a new OWASP pitfall / attack pattern / detection
- [ ] do not declare "safe / no vulnerability" before passing the checklist

---

## How to pick a mode

| Trigger | Mode |
|---|---|
| "วิเคราะห์ requirement", "spec", "use case", "flow" | A |
| "ทำหน้าใหม่ที่ยังไม่รู้ field" | A (before ux + fe) |
| "ตรวจ security", "audit auth", "หา vulnerability" | B |
| "ปลอดภัยพอไหม", "พร้อม prod ไหม" | B (+ infra checklist) |
| Covers both | A → B |

---

## Do not

- ❌ **implement code** — this skill only thinks/audits
- ❌ **abstract output** — every artifact must reference a real file/route/entity
- ❌ **report unverified vulnerability** — say "needs further check" + what
- ❌ **use vague wording** — "may have a problem" → state what / where / impact
- ❌ **conclude from a single file** — always caller-trace ≥ 1 hop
- ❌ **propose shallow fix** — list every consumer that must change together
