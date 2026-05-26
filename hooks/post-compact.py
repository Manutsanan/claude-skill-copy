#!/usr/bin/env python3
"""
PostCompact hook: after context compaction, scan for in-progress phase checkpoints.
Shows them as systemMessage (visible in UI immediately) and writes a sentinel file
so inject-checkpoint.py (UserPromptSubmit hook) can inject them as additionalContext
on the user's next message — the only way to reach Claude's context post-compaction.
"""
import json, sys, os, re
from pathlib import Path


def main():
    cwd = os.getcwd()
    project_id = cwd.replace("/", "-")
    checkpoint_dir = Path.home() / ".claude" / "projects" / project_id / "memory"

    if not checkpoint_dir.exists():
        return

    checkpoints = []
    for cp_file in sorted(checkpoint_dir.glob("project_phase_checkpoint_*.md")):
        try:
            text = cp_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^\s*status:\s*in_progress", text, re.MULTILINE):
                checkpoints.append((cp_file.name, text.strip()))
        except Exception:
            pass

    if not checkpoints:
        return

    lines = ["## ⚠️ Pipeline context restored after compaction\n"]
    lines.append("The following phase checkpoints were in-progress before compaction:")
    lines.append("Resume from the checkpoint — do not restart from zero.\n")
    for name, text in checkpoints:
        lines.append(f"### {name}")
        lines.append(text)
        lines.append("")

    output = {
        "systemMessage": "\n".join(lines),
    }
    print(json.dumps(output))

    # Write sentinel so inject-checkpoint.py injects checkpoint as additionalContext
    # on the user's next message (UserPromptSubmit supports additionalContext; PostCompact does not).
    sentinel = checkpoint_dir / ".pending-checkpoint-inject"
    try:
        sentinel.touch()
    except Exception:
        pass


try:
    main()
except Exception:
    pass

sys.exit(0)
