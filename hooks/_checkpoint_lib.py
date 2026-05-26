"""Shared helpers for post-compact.py + inject-checkpoint.py.

Single source of truth for: locating the project checkpoint dir, scanning
for in-progress checkpoints, and rendering the resume block.
"""
import os
import re
from pathlib import Path


def checkpoint_dir() -> Path:
    project_id = os.getcwd().replace("/", "-")
    return Path.home() / ".claude" / "projects" / project_id / "memory"


def scan_in_progress(directory: Path) -> list[tuple[str, str]]:
    if not directory.exists():
        return []
    results: list[tuple[str, str]] = []
    for cp_file in sorted(directory.glob("project_phase_checkpoint_*.md")):
        try:
            text = cp_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"^\s*status:\s*in_progress", text, re.MULTILINE):
                results.append((cp_file.name, text.strip()))
        except Exception:
            pass
    return results


def render_block(checkpoints: list[tuple[str, str]]) -> str:
    lines = [
        "## ⚠️ Pipeline context restored after compaction\n",
        "The following phase checkpoints were in-progress before compaction:",
        "Resume from the checkpoint — do not restart from zero.\n",
    ]
    for name, text in checkpoints:
        lines.append(f"### {name}")
        lines.append(text)
        lines.append("")
    return "\n".join(lines)
