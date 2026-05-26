#!/usr/bin/env python3
"""
PostCompact hook: after context compaction, scan for in-progress phase checkpoints
in the current project and inject them back as additionalContext so Claude knows
where it left off in a pipeline (sa/ux/fe checkpoint files).
Runs synchronously — output JSON is injected into the next model context.
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
        "systemMessage": "\n".join(lines),
    }
    print(json.dumps(output))


try:
    main()
except Exception:
    pass

sys.exit(0)
