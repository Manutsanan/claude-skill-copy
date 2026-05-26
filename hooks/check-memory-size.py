#!/usr/bin/env python3
"""SessionStart hook: warn when project memory approaches its 30–50/skill cap,
and surface any hook errors logged in the past 24 hours.

MEMORY.md truncates after 200 lines, so silently over-sized memory degrades
Phase 0 echoes. Emits a systemMessage Claude sees on session start; no Claude
tokens consumed unless a threshold is crossed.

Thresholds:
  WARN_THRESHOLD   project entries  → suggest review
  CRITICAL_THRESHOLD project entries → strongly urge /distill-memory

Hook-error surfacing:
  Reads ~/.claude/logs/hook-errors.jsonl — emits warning if any error in last 24h.
  Errors come from log-skill-invoke.py and log-user-prompt.py (silent-fail policy
  swallows runtime errors but writes them here for forensic visibility).
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

WARN_THRESHOLD = 30
CRITICAL_THRESHOLD = 45
HOOK_ERROR_WINDOW_HOURS = 24
LOG_DIR = Path.home() / ".claude" / "logs"


def count_entries(memory_dir: Path) -> int:
    if not memory_dir.exists():
        return 0
    return sum(
        1
        for f in memory_dir.glob("*.md")
        if f.name != "MEMORY.md" and not f.name.startswith(".")
    )


def recent_hook_errors() -> dict[str, int]:
    """Return {hook_name: error_count} for errors in last HOOK_ERROR_WINDOW_HOURS."""
    err_file = LOG_DIR / "hook-errors.jsonl"
    if not err_file.exists():
        return {}
    cutoff = datetime.now(timezone.utc) - timedelta(hours=HOOK_ERROR_WINDOW_HOURS)
    counts: Counter = Counter()
    try:
        with err_file.open(encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    dt = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    if dt >= cutoff:
                        counts[rec.get("hook", "unknown")] += 1
                except Exception:
                    continue
    except Exception:
        return {}
    return dict(counts)


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

    hook_errors = recent_hook_errors()
    if hook_errors:
        total = sum(hook_errors.values())
        by_hook = ", ".join(f"{name}: {n}" for name, n in sorted(hook_errors.items()))
        warnings.append(
            f"🟠 **{total} hook error(s)** in last {HOOK_ERROR_WINDOW_HOURS}h ({by_hook}). "
            f"Inspect `~/.claude/logs/hook-errors.jsonl` or run `python3 ~/.claude/scripts/skill-report.py --errors`."
        )

    if not warnings:
        return

    body = "## ⚠️ SessionStart warnings\n\n" + "\n\n".join(warnings)
    print(json.dumps({"systemMessage": body}))


try:
    main()
except Exception:
    pass

sys.exit(0)
