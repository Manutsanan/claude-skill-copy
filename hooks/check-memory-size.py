#!/usr/bin/env python3
"""SessionStart hook: warn when project memory approaches its 30–50/skill cap.
MEMORY.md truncates after 200 lines, so silently over-sized memory degrades
Phase 0 echoes. Emits a systemMessage Claude sees on session start; no Claude
tokens consumed unless the warn threshold is crossed.

Thresholds:
  WARN_THRESHOLD   project entries  → suggest review
  CRITICAL_THRESHOLD project entries → strongly urge /distill-memory
"""
import json
import os
import sys
from pathlib import Path

WARN_THRESHOLD = 30
CRITICAL_THRESHOLD = 45


def count_entries(memory_dir: Path) -> int:
    if not memory_dir.exists():
        return 0
    return sum(
        1
        for f in memory_dir.glob("*.md")
        if f.name != "MEMORY.md" and not f.name.startswith(".")
    )


def main():
    project_id = os.getcwd().replace("/", "-")
    project_mem = Path.home() / ".claude" / "projects" / project_id / "memory"
    global_mem = Path.home() / ".claude" / "memory"

    project_count = count_entries(project_mem)
    global_count = count_entries(global_mem)

    warnings: list[str] = []

    if project_count >= CRITICAL_THRESHOLD:
        warnings.append(
            f"🔴 Project memory has **{project_count} entries** (critical ≥ {CRITICAL_THRESHOLD}). "
            f"MEMORY.md truncates after 200 lines — echoed entries may be silently dropped. "
            f"Run `/distill-memory` before continuing."
        )
    elif project_count >= WARN_THRESHOLD:
        warnings.append(
            f"🟡 Project memory has **{project_count} entries** (warn ≥ {WARN_THRESHOLD}). "
            f"Consider `/distill-memory` to consolidate duplicates and promote cross-project lessons."
        )

    if global_count >= CRITICAL_THRESHOLD:
        warnings.append(
            f"🔴 Global memory has **{global_count} entries** — `/distill-memory` recommended."
        )

    if not warnings:
        return

    body = "## ⚠️ Memory size threshold reached\n\n" + "\n\n".join(warnings)
    print(json.dumps({"systemMessage": body}))


try:
    main()
except Exception:
    pass

sys.exit(0)
