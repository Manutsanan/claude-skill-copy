#!/bin/bash
# Daily (08:58): read FOLLOWUPS.md, update Data Tables via state store.
# n8n Schedule Trigger fires at 09:00 and reads followups_text from Data Tables.
FOLLOWUPS_FILE="$HOME/Project/claude-skill-copy/FOLLOWUPS.md"

[ -f "$FOLLOWUPS_FILE" ] || exit 0

CONTENT=$(cat "$FOLLOWUPS_FILE")
TODAY=$(date +%Y-%m-%d)

PAYLOAD=$(jq -n --arg content "$CONTENT" --arg today "$TODAY" \
  '{content: $content, today: $today}')

# POST to state store — updates followups_text in Data Tables for the schedule trigger
curl -sf -X POST "http://localhost:5678/webhook/claude-state-store" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true
