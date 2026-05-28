---
name: verify
description: Browser-based verification after fe or debug completes. Navigate golden path, interact, screenshot, check console/network as proof. Trigger on Thai: ทดสอบ, confirm, verify, ตรวจสอบ, ดูผลลัพธ์, ลอง run ดู. English: verify, test it, check it works, confirm it runs. Do NOT use for writing code (use fe) or debugging (use debug).
user-invocable: false
---

# verify — Browser Verification

**Principle:** code-level pass (tsc + test) proves types compile — browser verify proves it actually works

**Scope:** observation only — does not write code; if bugs found, yield to `fe` or `debug`

---

## Trigger เรียกเมื่อ

User mentions any of:
- **Thai**: ทดสอบ, verify, confirm, ตรวจสอบ, ดูผลลัพธ์, ลอง run ดู, ลองเปิดดู
- **English**: verify, test it, confirm it works, check it, make sure it runs, prove it

Or when:
- `fe` or `debug` just completed and UI was changed
- User wants visual proof before merging

**Do not invoke** when:
- User wants to run the app just to see it (use `run`)
- User wants to write tests (use `fe`)
- Debugging a broken feature (use `debug`)

---

## Pre-flight (mandatory before every task)

1. **Scan project memory** — any prior verify failure patterns for this project?
2. **Scan skill learnings** at `~/.claude/skills/verify/learnings.md`
3. **Confirm dev server** — `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000` (or relevant port)
   - 200 → already up, proceed
   - fail → ask user to start server, or start via `run` skill first

---

## Phase 1 — Navigate + Initial State

1. `browser_navigate` to the target route
2. `browser_take_screenshot` — capture initial state
3. `browser_console_messages` — note any errors/warnings at page load
4. `browser_network_requests` — note any failed requests at load

---

## Phase 2 — Golden Path

Walk the primary user flow:
1. Fill inputs → `browser_fill`
2. Click actions → `browser_click`
3. Select options → `browser_select_option`
4. `browser_take_screenshot` at each key state transition
5. Check `browser_network_requests` after actions — look for failed API calls

---

## Phase 3 — Edge Cases

Test at minimum:
- **Empty state** — no data, empty list, zero results
- **Error state** — invalid input, required field empty, API error if simulatable
- **Loading state** — if async operations exist, check spinner/skeleton shows
- **Responsive** — `browser_resize` to 390×844 (mobile) + screenshot

---

## Phase 4 — Report

Output:
- Screenshot of each key state (initial, after action, error, mobile)
- Console summary: errors found / none
- Network summary: failed requests / none
- Table: `| Case | Expected | Actual | Pass/Fail |`

If anything fails → yield to `fe` (logic bug) or `debug` (runtime error) with:
- Exact screenshot showing the failure
- Console error text (if any)
- Reproduce steps (route → action → observe)

5. **Write result marker** — run after report so n8n can surface the outcome:
   ```bash
   CWD_HASH=$(python3 -c "import hashlib,os; print(hashlib.sha256(os.getcwd().encode()).hexdigest()[:16])")
   # Pass:
   echo "PASS" > "/tmp/.claude-verify-${CWD_HASH}"
   # Fail (replace with actual reason):
   echo "FAIL: <short reason>" > "/tmp/.claude-verify-${CWD_HASH}"
   ```

---

## Quality gates

- [ ] Browser actually opened — not just tsc/lint output
- [ ] Console checked — errors there are real bugs even if UI looks correct
- [ ] At least one error state tested — not just happy path
- [ ] Mobile resize checked if responsive was part of the change
- [ ] Screenshot attached as proof

---

## Do not

- ❌ Claim "verify passed" without opening the browser
- ❌ Skip console check — page may look correct but throw JS errors
- ❌ Only test happy path — always check at least one error/empty state
- ❌ Fix bugs found here directly — yield to `fe`/`debug` with exact finding
