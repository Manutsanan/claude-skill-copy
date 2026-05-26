#!/usr/bin/env python3
"""Distill memory — dry-run report (no writes).

Scans:
  - ~/.claude/memory/*.md                       (global tier)
  - ~/.claude/projects/*/memory/*.md            (project tier)
  - ~/.claude/skills/*/learnings.md             (skill tier)

Emits a markdown report covering:
  - Cross-project promotion candidates (slug or name in >= 2 projects)
  - Memory-cap status per project (warn >= 30, critical >= 45)
  - Global tier headcount
  - Action hint: invoke `/distill-memory` to apply

The report is printed to stdout; the caller decides how to deliver it
(TG, file, etc). No memory file is modified by this script.
"""
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import List, Optional, Tuple

HOME = Path.home()
GLOBAL_DIR = HOME / ".claude" / "memory"
PROJECTS_DIR = HOME / ".claude" / "projects"
SKILLS_DIR = HOME / ".claude" / "skills"

WARN_THRESHOLD = 30
CRITICAL_THRESHOLD = 45


def read_frontmatter_name(path: Path) -> Optional[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None
    match = re.search(r"^name:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


def project_entry_files(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    return [
        f
        for f in directory.glob("*.md")
        if f.name != "MEMORY.md" and not f.name.startswith(".")
    ]


def scan_promotion_candidates() -> List[Tuple[str, List[str]]]:
    slug_to_projects = defaultdict(list)  # type: ignore[var-annotated]
    for entry in PROJECTS_DIR.glob("*/memory/*.md"):
        if entry.name == "MEMORY.md" or entry.name.startswith("."):
            continue
        slug = read_frontmatter_name(entry)
        if not slug:
            continue
        project_id = entry.parts[-3]
        short = project_id.removeprefix("-Users-manutsanan-").lstrip("-")
        if short not in slug_to_projects[slug]:
            slug_to_projects[slug].append(short)

    candidates = [(s, p) for s, p in slug_to_projects.items() if len(p) >= 2]
    candidates.sort(key=lambda x: -len(x[1]))
    return candidates


def scan_memory_caps() -> List[Tuple[str, int, str]]:
    rows = []  # type: List[Tuple[str, int, str]]
    for memory_dir in sorted(PROJECTS_DIR.glob("*/memory")):
        project_id = memory_dir.parts[-2]
        short = project_id.removeprefix("-Users-manutsanan-").lstrip("-") or "(home)"
        count = len(project_entry_files(memory_dir))
        if count >= CRITICAL_THRESHOLD:
            label = "🔴 critical"
        elif count >= WARN_THRESHOLD:
            label = "🟡 warn"
        else:
            continue
        rows.append((short, count, label))
    rows.sort(key=lambda x: -x[1])
    return rows


def global_entry_count() -> int:
    if not GLOBAL_DIR.exists():
        return 0
    return sum(
        1
        for f in GLOBAL_DIR.glob("*.md")
        if f.name != "MEMORY.md" and not f.name.startswith(".")
    )


def render() -> str:
    today = date.today().isoformat()
    lines = [
        f"# 📚 Weekly memory distill — {today}",
        "",
        "_Auto-generated dry-run report. No memory was modified._",
        "",
    ]

    promotions = scan_promotion_candidates()
    if promotions:
        lines.append("## 🟢 Cross-project promotion candidates")
        lines.append(f"_{len(promotions)} slugs found in ≥ 2 projects — review for global tier_")
        lines.append("")
        for slug, projects in promotions[:15]:
            lines.append(f"- **{slug}** — {len(projects)} projects: {', '.join(projects)}")
        if len(promotions) > 15:
            lines.append(f"- _… +{len(promotions) - 15} more_")
        lines.append("")
    else:
        lines.append("## 🟢 Cross-project promotion candidates")
        lines.append("_None — no slug appears in ≥ 2 projects this week._")
        lines.append("")

    caps = scan_memory_caps()
    if caps:
        lines.append("## ⚠️ Memory caps (≥ 30 entries)")
        lines.append("")
        for short, count, label in caps:
            lines.append(f"- {label} **{short}** — {count} entries")
        lines.append("")
    else:
        lines.append("## ⚠️ Memory caps")
        lines.append(f"_All projects under {WARN_THRESHOLD} entries — nothing urgent._")
        lines.append("")

    g_count = global_entry_count()
    lines.append("## 📊 Tier snapshot")
    lines.append("")
    lines.append(f"- Global tier: **{g_count} entries**")
    lines.append(f"- Projects scanned: {len(list(PROJECTS_DIR.glob('*/memory')))}")
    skill_learnings = list(SKILLS_DIR.glob("*/learnings.md"))
    lines.append(f"- Skill learnings files: {len(skill_learnings)}")
    lines.append("")

    if promotions or caps:
        lines.append("---")
        lines.append("")
        lines.append("**Next step:** open a Claude session and run `/distill-memory` to review + apply.")
        lines.append("Skill walks you through promote / prune one at a time; nothing writes without your confirmation.")
    else:
        lines.append("---")
        lines.append("")
        lines.append("**Status:** memory is healthy — no action needed this week.")

    return "\n".join(lines) + "\n"


def main():
    sys.stdout.write(render())


if __name__ == "__main__":
    main()
