#!/bin/bash
# Daily: compare hook file checksums between local and repo, POST drifts to n8n
N8N_WEBHOOK="http://localhost:5678/webhook/claude-drift"
HOOKS_LOCAL="$HOME/.claude/hooks"
HOOKS_REPO="$HOME/Project/claude-skill-copy/hooks"

DRIFTS="[]"
DRIFT_COUNT=0

for LOCAL in "$HOOKS_LOCAL"/*.sh "$HOOKS_LOCAL"/*.py; do
  [ -f "$LOCAL" ] || continue
  # Skip symlinks that point to repo (already in sync by definition)
  [ -L "$LOCAL" ] && continue
  BASE=$(basename "$LOCAL")
  REPO="$HOOKS_REPO/$BASE"
  [ -f "$REPO" ] || continue
  L=$(md5 -q "$LOCAL" 2>/dev/null || md5sum "$LOCAL" 2>/dev/null | cut -d' ' -f1)
  R=$(md5 -q "$REPO"  2>/dev/null || md5sum "$REPO"  2>/dev/null | cut -d' ' -f1)
  if [ "$L" != "$R" ]; then
    DRIFTS=$(echo "$DRIFTS" | jq --arg f "$BASE" '. += [$f]')
    DRIFT_COUNT=$((DRIFT_COUNT + 1))
  fi
done

PAYLOAD=$(jq -n \
  --argjson drifts "$DRIFTS" \
  --argjson drift_count "$DRIFT_COUNT" \
  '{drifts: $drifts, drift_count: $drift_count}')

curl -sf -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true
