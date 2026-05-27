---
name: run
description: Launch dev server and screenshot the current state. Use to visually confirm what the app looks like right now. Trigger on Thai: run app, เปิด app, รัน, ดูหน้าตา, เปิด dev server, screenshot หน้านี้. English: run, launch, open app, show me what it looks like, start dev server, screenshot. Do NOT use for verification after changes (use verify) or debugging (use debug).
user-invocable: false
---

# run — Dev Server + Screenshot

**Principle:** the fastest way to know if it looks right is to look at it

**Scope:** observation only — start server if needed, navigate, screenshot; does not write code

---

## Trigger เรียกเมื่อ

User mentions any of:
- **Thai**: run app, เปิด app, รัน, ดูหน้าตา, เปิด dev server, screenshot หน้านี้, ดู UI ปัจจุบัน
- **English**: run, launch, open app, show me, start dev server, screenshot, what does it look like

Or when:
- User wants a quick visual before deciding next step
- After pulling changes and wanting to see current state

**Do not invoke** when:
- Verifying a just-completed change (use `verify` — it checks console + edge cases)
- Debugging broken behavior (use `debug`)

---

## Pre-flight

1. Check `package.json` for dev command: `scripts.dev` / `scripts.start` / `scripts.serve`
2. Check if server already running: `curl -s -o /dev/null -w "%{http_code}" http://localhost:3000`

---

## Phase 1 — Server Check

```
200 → already up → go to Phase 2
fail → start server in background → wait (poll curl up to 30s, every 2s)
```

Dev command precedence: `scripts.dev` > `scripts.start` > `scripts.serve` > ask user

---

## Phase 2 — Navigate + Screenshot

1. `browser_navigate` to requested route (or `/` if not specified)
2. `browser_take_screenshot` — full viewport
3. If user asked for a specific route: navigate there + screenshot
4. If user asked for mobile: `browser_resize` to 390×844 + screenshot again

---

## Phase 3 — Hand Off

- Show screenshot
- Note any console errors found in `browser_console_messages` (1-line summary)
- Do not fix anything found — observe and report only
- Yield to `debug` if errors are critical; yield to `fe` if UI looks wrong

---

## Do not

- ❌ Kill or restart a running dev server without asking
- ❌ Fix problems found — observe and report only
- ❌ Start server if `curl` already returns 200
- ❌ Leave server running in background after session if user didn't ask for it
