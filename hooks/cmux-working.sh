#!/bin/sh
# Fires on UserPromptSubmit — show "working" status in cmux sidebar
[ -n "$CMUX_SOCKET_PATH" ] || exit 0
CMUX=/Applications/cmux.app/Contents/Resources/bin/cmux
"$CMUX" set-status claude "working…" --color "#007aff" --priority 90
