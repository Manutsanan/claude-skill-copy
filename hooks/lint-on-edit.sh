#!/usr/bin/env bash
# PostToolUse hook: lint Claude Code skill/memory files after Edit/Write/NotebookEdit
# Warn-only — never blocks the edit (always exits 0).

set -e

if ! command -v jq &>/dev/null; then
  exit 0
fi

input=$(cat)
file_path=$(echo "$input" | jq -r '.tool_input.file_path // .tool_input.path // ""')

[ -z "$file_path" ] && exit 0

case "$file_path" in
  */.claude/skills/*|*/.claude/memory/*|*/.claude/projects/*/memory/*)
    output=$("$HOME/.claude/scripts/lint-skills.py" "$file_path" 2>&1 || true)
    if echo "$output" | grep -qE '^\[(FAIL|WARN)\]'; then
      echo "[lint-skills] $file_path" >&2
      echo "$output" >&2
    fi
    exit 0
    ;;
esac

exit 0
