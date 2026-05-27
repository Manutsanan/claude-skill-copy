#!/bin/bash
# Daily: read FOLLOWUPS.md, parse upcoming deadlines, POST to n8n
N8N_WEBHOOK="http://localhost:5678/webhook/claude-followups"
FOLLOWUPS_FILE="$HOME/Project/claude-skill-copy/FOLLOWUPS.md"

[ -f "$FOLLOWUPS_FILE" ] || exit 0

CONTENT=$(cat "$FOLLOWUPS_FILE")
TODAY=$(date +%Y-%m-%d)

PAYLOAD=$(jq -n --arg content "$CONTENT" --arg today "$TODAY" \
  '{content: $content, today: $today}')

curl -sf -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true
