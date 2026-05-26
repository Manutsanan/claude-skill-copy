#!/usr/bin/env python3
"""
Scans ~/.claude/projects/*/memory/feedback_*.md for entries whose
`name:` slug appears in ≥2 different projects.
Writes promotion candidates to ~/.claude/memory/.cross-project-candidates.md
so distill-memory can find them in the global memory audit (Step 1).
Runs as async SessionStart hook — no Claude tokens involved.
"""
import re, sys
from pathlib import Path
from collections import defaultdict
from datetime import date

PROJECTS_DIR = Path.home() / ".claude" / "projects"
OUTPUT = Path.home() / ".claude" / "memory" / ".cross-project-candidates.md"
MIN_PROJECTS = 2


def main():
    slug_to_projects: dict[str, list[str]] = defaultdict(list)

    for feedback_file in PROJECTS_DIR.glob("*/memory/feedback_*.md"):
        project_id = feedback_file.parts[-3]
        try:
            text = feedback_file.read_text(encoding="utf-8", errors="ignore")
            m = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
            if not m:
                continue
            slug = m.group(1).strip()
            if project_id not in slug_to_projects[slug]:
                slug_to_projects[slug].append(project_id)
        except Exception:
            pass

    candidates = [(s, p) for s, p in slug_to_projects.items() if len(p) >= MIN_PROJECTS]

    if not candidates:
        try:
            OUTPUT.unlink()
        except FileNotFoundError:
            pass
        return

    lines = [
        "# Cross-project promotion candidates",
        f"# Generated: {date.today()}",
        "# Each entry: same `name:` slug found in ≥2 project memories → candidate for global memory",
        "",
    ]
    for slug, projects in sorted(candidates, key=lambda x: -len(x[1])):
        short_names = [p.rsplit("-", 1)[-1] for p in projects]
        lines.append(f"- **{slug}** — {len(projects)} projects: {', '.join(short_names)}")

    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


try:
    main()
except Exception:
    pass

sys.exit(0)
