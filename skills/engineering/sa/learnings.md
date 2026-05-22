# Learnings — sa

> **Per-skill, cross-project memory** — lessons for skill `sa` that apply across every project (System Analysis + Security Audit)
>
> **What to keep here:**
> - Edge cases that are commonly missed during enumeration (concurrent submit, network fail mid-flight, partial success, idempotency)
> - State machine patterns that pop up often (loading/empty/error/success/partial/unauthorized/max boundary)
> - OWASP / security pattern (IDOR check, auth boundary, secret leakage point, SSRF surface)
> - Question templates that pull requirements out of users effectively (e.g. "if X happens together with Y, what does the system do")
> - Diagram patterns that convey complex flow accurately (sequence vs state vs ER — when to use which)
>
> **What not to keep here:**
> - Domain-specific data models (e.g. Booking entity of one specific project → project memory)
> - Codebase-specific security findings (those go into project memory + fix in code)
> - Stakeholder names / project-specific business terms
>
> **When to read:** every time in the Pre-flight of skill `sa` (both Mode A Analyze and Mode B Audit)
> **When to append:** after a task if a lesson generalizes (see format in `_template/learnings.md`)

---

## Format per entry

```markdown
## <kebab-case-slug>

**Tags:** keyword1, keyword2, keyword3
**Mode:** analyze | audit | both
**Date:** YYYY-MM-DD

**Context:** what you were doing when the lesson emerged — **1 line only**
**Lesson:** rule + reason
**How to apply:** what to do next time
```

---

## Entries

<!-- newest on top -->

## enumerate-7-visual-states-checklist

**Tags:** state-machine, ui-state, edge-case, handoff-to-ux
**Mode:** analyze
**Date:** 2026-05-16

**Context:** handed spec to `ux` and the design was missing empty / unauthorized state — ux had to yield back to ask for more spec
**Lesson:** every spec with UI must enumerate at least **7 visual states** before handing off to ux: `loading`, `empty`, `error`, `success`, `partial`, `unauthorized`, `max-boundary` (e.g. list at limit, input at character cap) — if any are skipped → ux will guess → misinterpret → rework
**How to apply:**
- when writing a state machine for a new page/component → use the 7-state checklist as the minimum
- some states may be collapsible (e.g. `unauthorized` = redirect, no render) — but you must **state explicitly** that it's collapsed, not ignored
- write `state: <name>` into the Mermaid state diagram for every one — do not make ux guess


## concurrent-submit-race-condition

**Tags:** edge-case, race-condition, form, idempotency, concurrent
**Mode:** analyze
**Date:** 2026-05-16

**Context:** spec for form submit where rapid clicking sends 2 requests → DB gets duplicate row or payment is charged twice
**Lesson:** every mutating action must specify in spec:
1. **Optimistic disable** — disable button + lock form after click until response returns
2. **Idempotency key** — frontend generates UUID sent with request, backend rejects duplicates with same key within an N-minute window
3. **Server-side dedupe** — DB constraint or business rule that prevents double-write (e.g. `UNIQUE(user_id, order_id, action)`)
Missing any one = vulnerability
**How to apply:**
- whenever enumerating edge cases of a form/action → include "concurrent submit" as a default check
- hand off to fe with UUID generation pattern + hand to backend audit (mode B) to verify dedupe layer exists
- example high-risk flows: payment, OTP request, order create, booking confirm


## idor-test-pattern

**Tags:** owasp, idor, authz, audit, attack-scenario
**Mode:** audit
**Date:** 2026-05-16

**Context:** audited route `/api/order/[id]` and found it authenticates via middleware but does not check that the user owns the order
**Lesson:** Authentication (logged in) ≠ Authorization (owns this resource) — IDOR occurs every time you "check logged-in and then fetch a resource by id from URL/body without checking ownership"
**How to apply:**
- every route with `[id]` / `:id` in path or `id` in body → audit that:
  1. there is an ownership check at the DB-query level (`WHERE user_id = currentUser.id`), or
  2. there is a role check (`if user.role !== 'admin' && resource.owner !== user.id`)
- always report attack scenario: "Attacker logs in as user A → GET /api/order/<user B's order id> → sees user B's data"
- Fix: never trust `id` from URL — always scope query with session/JWT subject

