---
name: pr
description: Use when writing, drafting, or publishing a GitHub PR description — concise, modern markdown with icons. Trigger on Thai: เขียน PR / สร้าง PR / draft PR / เปิด PR / ทำ PR / PR description / เขียน pull request and English: write PR / create PR / open PR / PR description / draft pull request / submit PR. Examples "เขียน PR ให้หน่อย", "สร้าง PR", "draft PR description", "open PR for this branch". DO NOT use for reviewing an existing PR (use `review`).
user-invocable: false
---

# pr — Write & publish GitHub PR descriptions

**Principle:** concise over complete — one scan should tell reviewers what changed and why

---

## Trigger เรียกเมื่อ

User mentions any of:
- **Thai**: เขียน PR, สร้าง PR, draft PR, เปิด PR, ทำ PR, PR description, เขียน pull request
- **English**: write PR, create PR, open PR, PR description, draft pull request, submit PR

Or working on a task that:
- Case A: branch has commits ready to merge and a PR needs to be opened
- Case B: existing PR body needs to be rewritten or improved

**Do not invoke** when:
- User wants to **review** an existing PR → yield to `review` skill
- No git repo or no commits on branch vs base

---

## Pre-flight (mandatory before every task)

1. **Load PR format** — read `~/.claude/memory/feedback_pr_description_style.md`; this is the authoritative template; do not deviate, do not duplicate inline
2. **Scan skill learnings** at `~/.claude/skills/pr/learnings.md` — grep tag matching current task
3. **Detect base branch** — in order:
   - `gh pr view --json baseRefName -q .baseRefName` (if PR already exists)
   - `git symbolic-ref refs/remotes/origin/HEAD | sed 's|refs/remotes/origin/||'`
   - Ask user if both fail
4. **Collect git data** — run all 3, store results before writing anything:
   - `git diff <base>...HEAD --stat` → file list + N files · +X / -Y
   - `git log <base>...HEAD --oneline` → commit messages for Overview context
   - `git diff <base>...HEAD --name-status` → change type per file (A/M/D/R)

---

## Thinking order

1. **Parse stats** — count files, extract real `+X / -Y` from `--stat` output, confirm base branch
2. **Classify each change** — map file path + name-status (A/M/D/R) → emoji per guide in format memory
3. **Group by scope** — cluster files by path prefix (e.g. `components/`, `server/`, `pages/`, `stores/`) for the collapsible block
4. **Write Overview** — 1 line; distill commit messages into the WHY not the WHAT; Thai OK
5. **Build Changes table** — each logical change = 1 row; merge trivial edits of the same type into 1 row
6. **Build Files Changed** — `<details>` collapsible block; grouped by scope with emoji prefix; summary line must include `N files · +X / -Y` (real numbers from `--stat`)
7. **Build Test Checklist** — ≤5 items; always end with "ไม่มี regression ใน console / network"
8. **Preview to user** — show full PR body as markdown before any `gh` command; never publish without explicit confirmation
9. **Execute** — based on user confirmation:
   - New PR: `gh pr create --title "..." --body "$(cat <<'EOF' ... EOF)"`
   - Edit existing: `gh pr edit --body "$(cat <<'EOF' ... EOF)"`
   - Output only: paste markdown text, user copies manually

---

## Handoff

**Input** — none; this skill is standalone
**Output** — PR URL (if published) or markdown body text (if output only)

**Mid-task yield** — if encountered mid-task:
- Branch has no commits vs base → stop; tell user "branch appears to have no new commits vs `<base>`"; ask to confirm base branch
- `gh` auth not configured → stop; ask user to run `gh auth login` first

---

## Output style

- Follow template exactly from `~/.claude/memory/feedback_pr_description_style.md`
- Emoji guide (also in that file): 🗑️ remove · 📦 restructure · ✨ feature · 🐛 bug fix · 🌐 i18n · ♻️ refactor · ✏️ update · 🔧 config · 🧪 test
- Files Changed section is **non-negotiable** — always present, always `<details>` collapsible
- Overview is **1 line max** — the WHY, not the WHAT
- No prose paragraphs anywhere
- No "Generated with Claude Code" footer

---

## Quality gates (mandatory before closing work)

- [ ] **`git diff --stat` actually ran** — `+X / -Y` are real numbers, not estimated
- [ ] **Files Changed section present** — `<details>` with grouped file list + `N files · +X / -Y` in summary
- [ ] **No prose walls** — every section is structured (table / list / code block)
- [ ] **Test checklist ≤ 5 items** — last item is always regression check
- [ ] **No "Generated with Claude Code" footer**
- [ ] **User confirmed publish step** — never run `gh pr create/edit` without showing preview first

---

## Do not do (anti-patterns)

- **do not estimate +X/-Y** — must come from real `git diff --stat`
- **do not skip Files Changed** — mandatory every time (user rule: "ต้องมีบอกว่ามีการแก้ไขไฟล์อะไรไปบ้างทุกครั้ง")
- **do not write Overview as a paragraph** — 1 line max, no bullet points inside Overview
- **do not add "Generated with Claude Code" footer** — explicitly forbidden
- **do not run `gh pr create` without preview** — always show markdown first, then ask
- **do not deviate from template** — format lives in `feedback_pr_description_style.md`; improvising = drift
- **do not invoke for PR review** — that is `review` skill's job
