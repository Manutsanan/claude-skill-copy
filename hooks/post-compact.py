#!/usr/bin/env python3
"""PostCompact hook: surface in-progress phase checkpoints + arm sentinel
so inject-checkpoint.py can inject them as additionalContext on the next prompt.
PostCompact only supports systemMessage; UserPromptSubmit is the only path
that reaches Claude's context after compaction.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _checkpoint_lib import checkpoint_dir, render_block, scan_in_progress


def main():
    directory = checkpoint_dir()
    checkpoints = scan_in_progress(directory)
    if not checkpoints:
        return

    print(json.dumps({"systemMessage": render_block(checkpoints)}))

    sentinel = directory / ".pending-checkpoint-inject"
    try:
        sentinel.touch()
    except Exception:
        pass


try:
    main()
except Exception:
    pass

sys.exit(0)
