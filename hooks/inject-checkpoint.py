#!/usr/bin/env python3
"""
UserPromptSubmit hook: after context compaction, inject in-progress phase
checkpoints as additionalContext so Claude's Phase 0 can resume the pipeline.
Fires only once per compaction (sentinel file guards repeated injection).
post-compact.py writes the sentinel; this hook reads + deletes it.
"""
import json, sys, os, re
from pathlib import Path


def main():
    cwd = os.getcwd()
    project_id = cwd.replace("/", "-")
    checkpoint_dir = Path.home() / ".claude" / "projects" / project_id / "memory"
    sentinel = checkpoint_dir / ".pending-checkpoint-inject"

    if not sentinel.exists():
        return

    try:
        sentinel.unlink()
    except Exception:
        pass

    if not checkpoint_dir.exists():
        return

    checkpoints = []
    for cp_file in sorted(checkpoint_dir.glob("project_phase_checkpoint_*.md")):
        try:
            text = cp_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^status:\s*in_progress", text, re.MULTILINE):
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
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(output))


try:
    main()
except Exception:
    pass

sys.exit(0)
