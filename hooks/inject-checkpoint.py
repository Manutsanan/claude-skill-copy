#!/usr/bin/env python3
"""UserPromptSubmit hook: after compaction, inject in-progress checkpoints
as additionalContext so Phase 0 can resume the pipeline. Fires once per
compaction — the sentinel written by post-compact.py guards repeated injection.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _checkpoint_lib import checkpoint_dir, render_block, scan_in_progress


def main():
    directory = checkpoint_dir()
    sentinel = directory / ".pending-checkpoint-inject"
    if not sentinel.exists():
        return
    try:
        sentinel.unlink()
    except Exception:
        pass

    checkpoints = scan_in_progress(directory)
    if not checkpoints:
        return

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": render_block(checkpoints),
        }
    }
    print(json.dumps(output))


try:
    main()
except Exception:
    pass

sys.exit(0)
