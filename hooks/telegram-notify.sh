#!/bin/bash
# Stop hook: notify Telegram with an overview + per-file heuristic summary
# (size category / affected Vue section / +/- identifiers) when Claude
# finishes a turn that involved file modifications. No external API calls.

source "$(dirname "$0")/tg-config.sh"

python3 /Users/manutsanan/.claude/hooks/telegram-notify.py
exit 0
