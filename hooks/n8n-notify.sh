#!/bin/bash
# Send Claude stop event to n8n webhook with enriched payload
N8N_WEBHOOK="${N8N_WEBHOOK_URL:-http://localhost:5678/webhook/claude-stop}"
INPUT=$(cat)

# Enrich: last skill invoked
LOG_DIR="$HOME/.claude/logs"
LAST_SKILL=$(find "$LOG_DIR" -name "skill-invocations-*.jsonl" -newer "$LOG_DIR/.last-skill-marker" 2>/dev/null \
  | xargs tail -1 2>/dev/null | jq -r '.skill // ""' 2>/dev/null || echo "")
# Fallback: most recent entry from this month
if [ -z "$LAST_SKILL" ]; then
  MONTH=$(date +%Y-%m)
  LAST_SKILL=$(tail -1 "$LOG_DIR/skill-invocations-${MONTH}.jsonl" 2>/dev/null | jq -r '.skill // ""' 2>/dev/null || echo "")
fi
LAST_SKILL=$(echo "$LAST_SKILL" | tr '[:lower:]' '[:upper:]')

# Enrich: completed checkpoint phases (sa/ux/fe) for current project
CWD_PATH=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
[ -z "$CWD_PATH" ] && CWD_PATH="$(pwd)"
CWD_HASH=$(echo -n "$CWD_PATH" | python3 -c "import sys,hashlib; print(hashlib.sha256(sys.stdin.read().encode()).hexdigest()[:16])" 2>/dev/null || echo "")

# Debounce: prevent double-send from concurrent sessions (multi-terminal)
DEBOUNCE="/tmp/.claude-notify-${CWD_HASH}"
if [ -f "$DEBOUNCE" ]; then exit 0; fi
touch "$DEBOUNCE" 2>/dev/null
(sleep 10 && rm -f "$DEBOUNCE") &

PROJECT_MEM="$HOME/.claude/projects/-$(echo "$CWD_PATH" | tr '/' '-' | sed 's/^-//')/memory"
CHECKPOINT_PHASES="[]"
if [ -d "$PROJECT_MEM" ]; then
  PHASES=$(ls "$PROJECT_MEM"/project_phase_checkpoint_*.md 2>/dev/null \
    | xargs -I{} basename {} 2>/dev/null \
    | grep -oE 'checkpoint_(sa|ux|fe)' \
    | sed 's/checkpoint_//' \
    | tr '[:lower:]' '[:upper:]' \
    | sort -u \
    | jq -R . | jq -s . 2>/dev/null || echo "[]")
  CHECKPOINT_PHASES="${PHASES:-[]}"
fi

# Enrich: memory file count
MEM_FILES=$(find "$HOME/.claude/memory" "$HOME/.claude/projects" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
MEM_BYTES=$(find "$HOME/.claude/memory" "$HOME/.claude/projects" -name "*.md" 2>/dev/null \
  | xargs wc -c 2>/dev/null | tail -1 | awk '{print $1}' || echo "0")

PAYLOAD=$(echo "$INPUT" | jq \
  --arg cwd "$CWD_PATH" \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg last_skill "$LAST_SKILL" \
  --arg cwd_hash "$CWD_HASH" \
  --argjson checkpoint_phases "$CHECKPOINT_PHASES" \
  --argjson mem_files "${MEM_FILES:-0}" \
  --argjson mem_bytes "${MEM_BYTES:-0}" \
  '. + {
    cwd: $cwd,
    timestamp: $ts,
    last_skill: $last_skill,
    cwd_hash: $cwd_hash,
    checkpoint_phases: $checkpoint_phases,
    mem_files: $mem_files,
    mem_bytes: $mem_bytes
  }' 2>/dev/null || \
  printf '{"cwd":"%s","timestamp":"%s","last_skill":"%s","cwd_hash":"%s","checkpoint_phases":[],"mem_files":0,"mem_bytes":0}' \
    "$CWD_PATH" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$LAST_SKILL" "$CWD_HASH")

# POST to pipeline tracker
curl -sf -X POST "$N8N_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true

# POST same payload to memory health monitor (separate workflow)
curl -sf -X POST "http://localhost:5678/webhook/claude-memory" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true

# POST to state store — feeds pre-fetch cache for next session
curl -sf -X POST "http://localhost:5678/webhook/claude-state-store" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" \
  --max-time 5 2>/dev/null || true
