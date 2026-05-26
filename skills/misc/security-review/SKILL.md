---
name: security-review
description: Security audit of the current branch before merging. OWASP Top 10 check on changed files — auth gates, input validation, output encoding, IDOR, secrets, cookies, CORS/CSP. Trigger on Thai: ตรวจ security, security review, audit ก่อน merge, ดู security. English: security review, security audit, OWASP check, audit before merge, check for vulnerabilities. Do NOT use for general code review (use review) or system spec (use sa Mode B).
---

# security-review — Branch Security Audit

**Principle:** audit what changed in this branch — not the whole codebase; every finding must have file:line + exploitability + fix

**Scope:** read-only analysis of diff + optional runtime checks; does not write fixes (yield to `fe`)

---

## Trigger เรียกเมื่อ

User mentions any of:
- **Thai**: ตรวจ security, security review, audit ก่อน merge, ดู security, ช่องโหว่, vulnerability
- **English**: security review, security audit, OWASP, pentest, audit before merge, check for vulns, XSS, CSRF, IDOR

Or when:
- Branch is ready to merge and user wants security sign-off
- `sa` (Mode B audit) yields a security concern to investigate further

**Do not invoke** when:
- General code review (use `review`)
- Designing security architecture from scratch (use `sa` Mode B)

---

## Pre-flight (mandatory before every task)

1. **Scan project memory** — any prior security findings for this project?
2. **Scan skill learnings** at `~/.claude/skills/security-review/learnings.md`
3. **Confirm scope** — which branch? `git diff main...HEAD --name-only`

---

## Phase 1 — Diff Scope

```bash
git diff main...HEAD --name-only   # files changed in this branch
git diff main...HEAD --stat        # lines changed per file
```

Categorize changed files:
- **Auth** — middleware, guards, JWT/session handling
- **API routes** — server endpoints, request handlers
- **Forms** — input fields, validation schemas
- **Config** — env vars, CORS settings, CSP headers
- **DB** — queries, ORM calls, migrations

---

## Phase 2 — Static Analysis

Walk each changed file in scope. Check per category:

| Category | What to check |
|---|---|
| **Auth gates** | Route guard present? Middleware applied to all routes that need it? Token validated server-side (not just client)? |
| **Input validation** | All user input validated before use? Schema-based (Valibot/Zod/Joi)? Client-side only = not secure |
| **Output encoding** | User data escaped before render? `v-html` / `dangerouslySetInnerHTML` with user content = XSS |
| **IDOR** | Can user A access user B's resource? Ownership checked on server per request? |
| **SQL / NoSQL injection** | Parameterized queries? No string interpolation in DB calls? ORM used correctly? |
| **Secrets in code** | API keys, tokens, passwords hardcoded? `.env` committed? |
| **File upload** | Type + size restricted? Stored outside webroot? Filename sanitized? |
| **Mass assignment** | Are request body fields explicitly whitelisted before DB insert? |
| **Rate limiting** | Auth endpoints (login, reset) rate-limited? |
| **Dependency** | New packages added? Known CVE? (`npm audit` / `yarn audit`) |

---

## Phase 3 — Runtime Checks (if dev server available)

Optional — run if server is accessible:

1. `browser_network_requests` — auth headers sent on protected routes?
2. `browser_evaluate("document.cookie")` — HttpOnly cookies not visible (expected); if visible = misconfigured
3. Navigate to protected route without auth — expect 401/redirect, not data

---

## Phase 4 — Report

```
## Security Review — <branch> vs main

### Summary
- Files reviewed: N
- Critical: N | High: N | Medium: N | Low: N

### Findings

| # | Severity | Category | File:line | Finding | Fix |
|---|---|---|---|---|---|
| 1 | Critical | Auth | server/api/orders.ts:42 | No ownership check — any user can access any order | Add `if (order.userId !== session.userId) throw createError({statusCode: 403})` |
```

**Severity:**
- **Critical** — direct data breach / account takeover → block merge
- **High** — exploitable with low effort → block merge
- **Medium** — specific conditions required → fix in follow-up PR
- **Low** — defence-in-depth / hardening → note only

Yield to `fe` for Critical/High fixes with exact finding + recommended fix.

---

## Quality gates

- [ ] Every changed auth/API/form file reviewed — not just spot-checked
- [ ] All Phase 2 categories checked — no category skipped
- [ ] Each finding has file:line (not just "there's an issue")
- [ ] Severity correctly assigned — Critical/High must be evidenced
- [ ] `npm audit` / `yarn audit` run if new dependencies added

---

## Do not

- ❌ Audit the whole codebase — only the diff (`git diff main...HEAD`)
- ❌ Write code fixes directly — yield to `fe` with exact finding
- ❌ Claim "no issues" without checking all Phase 2 categories
- ❌ Mark Medium/Low as Critical without actual exploitability evidence
