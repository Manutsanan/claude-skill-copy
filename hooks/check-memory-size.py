#!/usr/bin/env python3
"""SessionStart hook: warn when project memory approaches its 30–50/skill cap,
and surface any hook errors logged in the past 24 hours.

Also:
  - Stale pipeline reminder: in-progress phase checkpoints from a prior session
  - Distill auto-inject: time-based suggestion when below count threshold but idle too long

Thresholds:
  WARN_THRESHOLD     project entries → suggest review
  CRITICAL_THRESHOLD project entries → strongly urge /distill-memory
  DISTILL_IDLE_DAYS  days since last distill → time-based suggestion (fires only below WARN)
  DISTILL_MIN_COUNT  minimum total entries before nagging about distill
"""
import json
import os
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from _checkpoint_lib import checkpoint_dir, scan_in_progress

WARN_THRESHOLD = 30
CRITICAL_THRESHOLD = 45
HOOK_ERROR_WINDOW_HOURS = 24
DISTILL_IDLE_DAYS = 14
DISTILL_MIN_COUNT = 10
LOG_DIR = Path.home() / ".claude" / "logs"


def count_entries(memory_dir: Path) -> int:
    if not memory_dir.exists():
        return 0
    return sum(
        1
        for f in memory_dir.glob("*.md")
        if f.name != "MEMORY.md" and not f.name.startswith(".")
    )


def recent_hook_errors() -> dict:
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


def last_distill_date() -> Optional[datetime]:
    """Scan skill invocation logs for most recent distill-memory run."""
    last: Optional[datetime] = None
    for log_file in sorted(LOG_DIR.glob("skill-invocations-*.jsonl"), reverse=True):
        try:
            lines = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()
            for line in reversed(lines):
                try:
                    rec = json.loads(line)
                    if rec.get("skill") == "distill-memory":
                        dt = datetime.strptime(rec["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(
                            tzinfo=timezone.utc
                        )
                        if last is None or dt > last:
                            last = dt
                        return last  # first (most recent) match in this file is the answer
                except Exception:
                    continue
        except Exception:
            continue
        if last is not None:
            break
    return last


def stale_pipeline_warning(directory: Path) -> Optional[str]:
    """Warn if any in-progress phase checkpoints exist (left over from a prior session)."""
    checkpoints = scan_in_progress(directory)
    if not checkpoints:
        return None
    phases = []
    for name, _ in checkpoints:
        # filename: project_phase_checkpoint_<phase>_YYYY-MM-DD.md
        parts = name.replace(".md", "").split("_")
        # find index of 'checkpoint' then next token is the phase
        try:
            idx = parts.index("checkpoint")
            phases.append(parts[idx + 1])
        except (ValueError, IndexError):
            phases.append("?")
    phase_str = " + ".join(phases)
    return (
        f"⏸️ **Stale pipeline detected** — `{phase_str}` checkpoint(s) are `in_progress` "
        f"from a prior session. Resume from the checkpoint or mark it as `abandoned` to start fresh."
    )


def distill_idle_warning(global_count: int, project_count: int) -> Optional[str]:
    """Time-based distill suggestion — only fires when below count-based thresholds."""
    total = global_count + project_count
    if total < DISTILL_MIN_COUNT:
        return None
    # Count-based logic already handles high counts — don't double-fire
    if project_count >= WARN_THRESHOLD or global_count >= CRITICAL_THRESHOLD:
        return None
    last = last_distill_date()
    if last is None:
        days_idle = 999
    else:
        days_idle = (datetime.now(timezone.utc) - last).days
    if days_idle < DISTILL_IDLE_DAYS:
        return None
    idle_str = f"{days_idle}d ago" if last is not None else "never"
    return (
        f"💡 Last `/distill-memory` was **{idle_str}** ({total} memory entries total). "
        f"Consider running it to promote cross-project patterns and prune stale entries."
    )


def main():
    project_id = os.getcwd().replace("/", "-")
    project_mem = Path.home() / ".claude" / "projects" / project_id / "memory"
    global_mem = Path.home() / ".claude" / "memory"

    project_count = count_entries(project_mem)
    global_count = count_entries(global_mem)

    warnings: list = []

    stale_warn = stale_pipeline_warning(project_mem)
    if stale_warn:
        warnings.append(stale_warn)

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

    distill_warn = distill_idle_warning(global_count, project_count)
    if distill_warn:
        warnings.append(distill_warn)

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
