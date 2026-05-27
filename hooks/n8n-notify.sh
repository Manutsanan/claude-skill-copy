#!/bin/bash
# Send Claude stop/phase event to n8n webhook
N8N_WEBHOOK="${N8N_WEBHOOK_URL:-http://localhost:5678/webhook/claude-skill}"
INPUT=$(cat)
PAYLOAD=$(echo "$INPUT" | jq --arg cwd "$(pwd)" --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  '. + {cwd: $cwd, timestamp: $ts}' 2>/dev/null || \
  printf '{"cwd":"%s","timestamp":"%s"}' "$(pwd)" "$(date -u +%Y-%m-%dT%H:%M:%SZ)")
curl -sf -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 3 2>/dev/null || true
