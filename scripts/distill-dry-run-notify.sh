#!/bin/bash
# Weekly distill dry-run → Telegram digest.
# Designed to be invoked from cron; no-op silently if TG credentials are absent.
#
# Flow:
#   1. Load TG credentials via ~/.claude/hooks/tg-config.sh (sources ~/.claude/.secrets/tg.env)
#   2. Run distill-dry-run.py → markdown report on stdout
#   3. Send to Telegram. Long reports are split at 3500-char boundaries (TG limit 4096).
#   4. Also archive last report to ~/.claude/memory/.last-distill-report.md
#
# Exits 0 always — cron-friendly, never fails the schedule.

set -u

REPORT_SCRIPT="$HOME/.claude/scripts/distill-dry-run.py"
ARCHIVE="$HOME/.claude/memory/.last-distill-report.md"
TG_CONFIG="$HOME/.claude/hooks/tg-config.sh"

if [ ! -x "$REPORT_SCRIPT" ]; then
    echo "[distill-notify] missing or non-executable: $REPORT_SCRIPT" >&2
    exit 0
fi

REPORT=$(python3 "$REPORT_SCRIPT" 2>/dev/null) || REPORT=""
if [ -z "$REPORT" ]; then
    echo "[distill-notify] empty report — nothing to send" >&2
    exit 0
fi

# Archive (overwrites previous week)
mkdir -p "$(dirname "$ARCHIVE")"
printf '%s\n' "$REPORT" > "$ARCHIVE"

# Load TG credentials
if [ -f "$TG_CONFIG" ]; then
    # shellcheck disable=SC1090
    . "$TG_CONFIG"
fi

if [ -z "${TELEGRAM_BOT_TOKEN:-}" ] || [ -z "${TELEGRAM_CHAT_ID:-}" ]; then
    echo "[distill-notify] TG credentials not set — report archived to $ARCHIVE only" >&2
    exit 0
fi

# Send via Python (handles chunking + URL encoding cleanly; TG limit 4096 chars)
python3 - <<'PY' "$REPORT"
import os, sys, urllib.parse, urllib.request

report = sys.argv[1]
token = os.environ["TELEGRAM_BOT_TOKEN"]
chat_id = os.environ["TELEGRAM_CHAT_ID"]
url = f"https://api.telegram.org/bot{token}/sendMessage"

# Split on blank lines, accumulating up to MAX chars per message.
MAX = 3500
chunks = []
buf = []
size = 0
for para in report.split("\n\n"):
    add = (len(para) + 2)
    if size + add > MAX and buf:
        chunks.append("\n\n".join(buf))
        buf = [para]
        size = add
    else:
        buf.append(para)
        size += add
if buf:
    chunks.append("\n\n".join(buf))

for i, chunk in enumerate(chunks, 1):
    suffix = "" if len(chunks) == 1 else f"\n\n_(part {i}/{len(chunks)})_"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "parse_mode": "Markdown",
        "disable_web_page_preview": "true",
        "text": chunk + suffix,
    }).encode()
    try:
        urllib.request.urlopen(url, data=data, timeout=10)
    except Exception as e:
        sys.stderr.write(f"[distill-notify] TG send chunk {i} failed: {e}\n")
PY

exit 0
