#!/bin/bash
# Telegram credentials loader — sourced by hooks that send messages.
# Credentials live in ~/.claude/.secrets/tg.env (chmod 600, never committed).
# To bootstrap a new machine, copy tg-config.sh.example to that path and fill in real values.

SECRETS_FILE="$HOME/.claude/.secrets/tg.env"

if [ ! -f "$SECRETS_FILE" ]; then
    export TELEGRAM_BOT_TOKEN=""
    export TELEGRAM_CHAT_ID=""
    return 0 2>/dev/null || exit 0
fi

set -a
# shellcheck disable=SC1090
. "$SECRETS_FILE"
set +a
