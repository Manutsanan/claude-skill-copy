#!/usr/bin/env bash
# Stop hook (async): type-check Vue/Nuxt/TS projects when files changed this session.
# Routes results through n8n for trend tracking. Falls back to direct Telegram if n8n unavailable.

set -euo pipefail

source "$(dirname "$0")/tg-config.sh"
[ -z "${TELEGRAM_BOT_TOKEN:-}" ] && exit 0

INPUT=$(cat)
CWD=$(echo "$INPUT" | jq -r '.cwd // empty' 2>/dev/null)
[ -z "$CWD" ] || [ ! -d "$CWD" ] && exit 0

# Skip if no TypeScript project
[ -f "$CWD/tsconfig.json" ] || exit 0

# Skip if no .ts/.vue files modified in last 15 minutes
RECENT=$(find "$CWD" \( -name "*.ts" -o -name "*.vue" \) \
    ! -path "*/node_modules/*" ! -path "*/.nuxt/*" ! -path "*/dist/*" ! -path "*/.output/*" \
    -mmin -15 2>/dev/null | wc -l | tr -d ' ')
[ "$RECENT" -eq 0 ] && exit 0

PROJECT=$(basename "$CWD")

# Debounce: skip if no source file is newer than the last-run marker
DEBOUNCE_MARKER="/tmp/.claude-typecheck-${PROJECT}"
if [ -f "$DEBOUNCE_MARKER" ]; then
    NEWER=$(find "$CWD" \( -name "*.ts" -o -name "*.vue" \) \
        ! -path "*/node_modules/*" ! -path "*/.nuxt/*" ! -path "*/dist/*" ! -path "*/.output/*" \
        -newer "$DEBOUNCE_MARKER" 2>/dev/null | head -1)
    [ -z "$NEWER" ] && exit 0
fi

cd "$CWD"

# Resolve local binaries (prefer node_modules over global)
VUE_TSC="./node_modules/.bin/vue-tsc"
TSC="./node_modules/.bin/tsc"
[ ! -x "$VUE_TSC" ] && VUE_TSC="$(command -v vue-tsc 2>/dev/null || true)"
[ ! -x "$TSC" ]     && TSC="$(command -v tsc 2>/dev/null || true)"

# Pick command based on project type
if [ -f "nuxt.config.ts" ] || [ -f "nuxt.config.js" ]; then
    LABEL="Nuxt"
    CMD="${VUE_TSC:-$TSC} --noEmit"
elif grep -q '"vue"' package.json 2>/dev/null && [ -x "./node_modules/.bin/vue-tsc" ]; then
    LABEL="Vue"
    CMD="$VUE_TSC --noEmit"
else
    LABEL="TS"
    CMD="$TSC --noEmit"
fi

# Skip if no usable compiler found
[[ -z "${CMD%% *}" || ! -x "${CMD%% *}" ]] && exit 0

# Run type check — touch debounce marker so next Stop skips if nothing changed
touch "$DEBOUNCE_MARKER" 2>/dev/null || true
OUTPUT=$(bash -c "$CMD" 2>&1) && TS_EXIT=0 || TS_EXIT=$?

ERROR_COUNT=0
TOP_ERRORS=""
if [ "$TS_EXIT" -ne 0 ]; then
    ERROR_COUNT=$(echo "$OUTPUT" | grep -c "error TS" 2>/dev/null || echo "0")
    TOP_ERRORS=$(echo "$OUTPUT" | grep "error TS" | head -4 \
        | sed "s|$CWD/||g" \
        | awk '{print "• "$0}')
fi

# Route through n8n for trend tracking
N8N_WEBHOOK="http://localhost:5678/webhook/claude-typecheck"
N8N_PAYLOAD=$(jq -n \
    --arg project "$PROJECT" \
    --arg label "$LABEL" \
    --argjson exit_code "$TS_EXIT" \
    --argjson error_count "$ERROR_COUNT" \
    --arg top_errors "$TOP_ERRORS" \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    '{project:$project,label:$label,exit_code:$exit_code,error_count:$error_count,top_errors:$top_errors,timestamp:$ts}')

N8N_OK=$(curl -sf -X POST "$N8N_WEBHOOK" \
    -H "Content-Type: application/json" \
    -d "$N8N_PAYLOAD" \
    --max-time 5 2>/dev/null && echo "ok" || echo "")

# Fallback: direct Telegram if n8n unavailable
if [ -z "$N8N_OK" ]; then
    tg_send() {
        curl -sf -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -H "Content-Type: application/json" \
            -d "$(jq -n --arg chat "$TELEGRAM_CHAT_ID" --arg text "$1" \
                '{chat_id:$chat,text:$text,parse_mode:"HTML"}')" \
            --max-time 5 >/dev/null 2>&1 || true
    }
    if [ "$TS_EXIT" -eq 0 ]; then
        tg_send "✅ <b>Type check passed</b>
📁 <code>$PROJECT</code> ($LABEL) — 0 errors"
    else
        ESCAPED_ERRORS=$(echo "$TOP_ERRORS" | sed 's/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g')
        tg_send "❌ <b>Type check: $ERROR_COUNT error(s)</b>
📁 <code>$PROJECT</code> ($LABEL)

<code>$ESCAPED_ERRORS</code>"
    fi
fi
