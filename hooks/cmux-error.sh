#!/bin/sh
# Fires on StopFailure — notify + show "error" in cmux sidebar
[ -n "$CMUX_SOCKET_PATH" ] || exit 0
CMUX=/Applications/cmux.app/Contents/Resources/bin/cmux
"$CMUX" set-status claude "error" --color "#ff3b30" --priority 90
"$CMUX" notify --title "Claude" --body "Task failed"
"$CMUX" log --level error "Task failed"
