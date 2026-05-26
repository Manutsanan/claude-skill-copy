#!/bin/bash
# SessionStart hook: verify tg-bridge daemon is running.
# Auto-restarts if dead; notifies Telegram on restart or failure.

source "$(dirname "$0")/tg-config.sh"

PID_FILE="$HOME/.claude/tools/tg-bridge/daemon.pid"
BRIDGE_BIN="$HOME/.claude/tools/tg-bridge/bin/tg-bridge"

tg_send() {
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        --data-urlencode "chat_id=${TELEGRAM_CHAT_ID}" \
        --data-urlencode "text=$1" \
        -o /dev/null 2>/dev/null || true
}

# Check if daemon is alive
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        exit 0  # healthy
    fi
fi

# Daemon is down — attempt restart
if [ -x "$BRIDGE_BIN" ]; then
    "$BRIDGE_BIN" start >/dev/null 2>&1
    sleep 3
    if [ -f "$PID_FILE" ]; then
        NEW_PID=$(cat "$PID_FILE")
        if kill -0 "$NEW_PID" 2>/dev/null; then
            tg_send "♻️ tg-bridge: daemon was down — restarted (PID ${NEW_PID})"
            exit 0
        fi
    fi
fi

tg_send "🔴 tg-bridge: daemon DOWN — auto-restart failed. Run: ~/.claude/tools/tg-bridge/bin/tg-bridge start"
exit 0
