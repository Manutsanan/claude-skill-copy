#!/bin/bash
# PostToolUse: remind to create .gitignore after `git init`.
# Logic lives here (not in `if:`) to avoid fallback false-positives on complex commands.
INPUT=$(cat)
CMD=$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
print(d.get('tool_input', {}).get('command', ''))
" 2>/dev/null || echo "")

case "$CMD" in
  "git init"*)
    [ ! -f .gitignore ] && printf '%s' \
      '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"git init just ran and .gitignore does not exist. REQUIRED: create a .gitignore appropriate for this project stack before doing anything else. This is a mandatory step per user preference."}}'
    ;;
esac
exit 0
