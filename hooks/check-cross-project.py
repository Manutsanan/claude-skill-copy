#!/usr/bin/env python3
"""
Scans ~/.claude/projects/*/memory/*.md for entries whose `name:` slug appears
in ≥2 different projects (all types: feedback, project, user, reference).
Excludes MEMORY.md, phase checkpoint files, and hidden files.
Writes promotion candidates to ~/.claude/memory/.cross-project-candidates.md
so distill-memory can find them in the global memory audit (Step 1).
Runs as async SessionStart hook — no Claude tokens involved.
"""
import json, re, sys, urllib.request, urllib.error
from pathlib import Path
from collections import defaultdict
from datetime import date

PROJECTS_DIR = Path.home() / ".claude" / "projects"
OUTPUT = Path.home() / ".claude" / "memory" / ".cross-project-candidates.md"
MIN_PROJECTS = 2


def main():
    slug_to_projects: dict[str, list[str]] = defaultdict(list)

    SKIP_NAMES = {"MEMORY.md"}
    for mem_file in PROJECTS_DIR.glob("*/memory/*.md"):
        # Skip index, checkpoints, and hidden files
        if mem_file.name in SKIP_NAMES:
            continue
        if mem_file.name.startswith("project_phase_checkpoint"):
            continue
        if mem_file.name.startswith("."):
            continue
        project_id = mem_file.parts[-3]
        try:
            text = mem_file.read_text(encoding="utf-8", errors="ignore")
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

    # POST to n8n for cross-project digest notification
    try:
        items = [
            {"slug": slug, "count": len(projects),
             "projects": [p.rsplit("-", 1)[-1] for p in projects]}
            for slug, projects in sorted(candidates, key=lambda x: -len(x[1]))
        ]
        payload = json.dumps({"candidates": items, "count": len(candidates)}).encode()
        req = urllib.request.Request(
            "http://localhost:5678/webhook/claude-cross-project",
            data=payload, method="POST",
            headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=3)
    except Exception:
        pass


try:
    main()
except Exception:
    pass

sys.exit(0)
