#!/bin/sh
# Fires on Stop — notify + show "done" in cmux sidebar
[ -n "$CMUX_SOCKET_PATH" ] || exit 0
CMUX=/Applications/cmux.app/Contents/Resources/bin/cmux
"$CMUX" set-status claude "done" --color "#30d158" --priority 90
"$CMUX" notify --title "Claude" --body "Task complete"
"$CMUX" log --level success "Task complete"
