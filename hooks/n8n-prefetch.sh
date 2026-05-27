#!/bin/bash
# UserPromptSubmit hook: query n8n state store at session start, inject pre-computed context.
# Fires once per (project × reboot) via /tmp marker — silent fallback if n8n unavailable.

N8N_BASE="${N8N_WEBHOOK_URL:-http://localhost:5678}"

CWD_PATH="${PWD}"
CWD_HASH=$(echo -n "$CWD_PATH" | python3 -c \
  "import sys,hashlib; print(hashlib.sha256(sys.stdin.read().encode()).hexdigest()[:8])" 2>/dev/null)
[ -z "$CWD_HASH" ] && exit 0

# Fire once per (cwd × boot session)
MARKER="/tmp/.claude-prefetch-${CWD_HASH}"
[ -f "$MARKER" ] && exit 0
touch "$MARKER" 2>/dev/null

RESPONSE=$(curl -sf \
  "${N8N_BASE}/webhook/claude-prefetch?cwd_hash=${CWD_HASH}" \
  --max-time 1 2>/dev/null)
[ -z "$RESPONSE" ] && exit 0

HAS=$(echo "$RESPONSE" | python3 -c \
  "import json,sys; d=json.load(sys.stdin); print('1' if d.get('has_context') else '0')" 2>/dev/null)
[ "$HAS" != "1" ] && exit 0

CTX=$(echo "$RESPONSE" | python3 -c "
import json, sys
d = json.load(sys.stdin)
lines = d.get('items', [])
print('\n'.join(f'• {l}' for l in lines))
" 2>/dev/null)
[ -z "$CTX" ] && exit 0

python3 -c "
import json, sys
ctx = sys.argv[1]
out = {
    'hookSpecificOutput': {
        'hookEventName': 'UserPromptSubmit',
        'additionalContext': f'[n8n prefetch]\n{ctx}'
    }
}
print(json.dumps(out))
" "$CTX"
