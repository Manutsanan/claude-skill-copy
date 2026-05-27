#!/bin/bash
# Weekly (Monday): aggregate skill invocation logs, POST to n8n
N8N_WEBHOOK="http://localhost:5678/webhook/claude-weekly"
LOG_DIR="$HOME/.claude/logs"

# Collect last 7 days of skill invocation logs
COMBINED=""
for f in "$LOG_DIR"/skill-invocations-*.jsonl; do
  [ -f "$f" ] || continue
  COMBINED="$COMBINED$(cat "$f")"$'\n'
done

[ -z "$(echo "$COMBINED" | tr -d '\n ')" ] && exit 0

# Aggregate in shell: count per skill
COUNTS=$(echo "$COMBINED" | grep -o '"skill":"[^"]*"' \
  | sort | uniq -c | sort -rn \
  | awk '{gsub(/"skill":"/, ""); gsub(/"/, ""); printf "%d %s\n", $1, $2}')

TOTAL=$(echo "$COMBINED" | grep -c '"skill"' 2>/dev/null || echo 0)
TODAY=$(date +%Y-%m-%d)
WEEK_START=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d "7 days ago" +%Y-%m-%d 2>/dev/null || echo "")

PAYLOAD=$(jq -n \
  --arg counts "$COUNTS" \
  --argjson total "$TOTAL" \
  --arg today "$TODAY" \
  --arg week_start "$WEEK_START" \
  '{counts: $counts, total: $total, today: $today, week_start: $week_start}')

curl -sf -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true
